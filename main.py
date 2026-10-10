import logging

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core import config
from app.core.config import API_PREFIX, APP_NAME, APP_VERSION, CORS_ORIGINS, MAX_UPLOAD_BYTES
from app.ml.classifier import classifier_ready
from app.schemas import (AnalyzeResponse, AuditVerification, CorrectionRecord, CorrectionRequest, ErrorResponse,
                         HealthResponse, RevalidateRequest, RevalidateResponse)
from app.services import pipeline
from app.services.ingestion import IngestionError, pdf_engine_available
from app.trust import audit

log = logging.getLogger("antimonitor.aiml")

app = FastAPI(title=APP_NAME, version=APP_VERSION,
              description="Explainable financial document classification with an evidence-linked trust layer (Pramaan AI Trust Engine).")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])

ERRORS = {400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}, 415: {"model": ErrorResponse}}


@app.exception_handler(IngestionError)
async def _ingestion_error(_: Request, exc: IngestionError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc), "error_code": exc.code})


@app.exception_handler(audit.CorrectionError)
async def _correction_error(_: Request, exc: audit.CorrectionError):
    return JSONResponse(status_code=422, content={"detail": str(exc), "error_code": "INVALID_CORRECTION"})


@app.exception_handler(Exception)
async def _unexpected(_: Request, exc: Exception):
    log.error("Unhandled error of type %s", type(exc).__name__)  # type only: never log document content or stack traces to clients
    return JSONResponse(status_code=500, content={"detail": "Internal processing error.", "error_code": "INTERNAL_ERROR"})


@app.get("/health", response_model=HealthResponse)
def health():
    components = {"api": True, "classifier": classifier_ready(), "pdf_text_extraction": pdf_engine_available(),
                  "audit_store": audit.audit_store_writable()}
    return HealthResponse(status="ok" if all(components.values()) else "degraded", components=components, version=APP_VERSION)


@app.post(f"{API_PREFIX}/documents/analyze", response_model=AnalyzeResponse, responses=ERRORS)
def analyze_document(file: UploadFile = File(...)):
    """Multipart field `file`. Type is decided by extension (.pdf/.txt) plus content signature, not by the client's Content-Type."""
    try:
        filename = file.filename or "upload"
        suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if suffix not in ("pdf", "txt"):
            raise IngestionError("Unsupported file type. Upload a PDF or UTF-8 TXT file.", "UNSUPPORTED_TYPE", 415)
        content = file.file.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise IngestionError(f"File exceeds the {MAX_UPLOAD_BYTES}-byte upload limit.", "FILE_TOO_LARGE", 413)
        return pipeline.analyze_document(filename, content)
    finally:
        file.file.close()


@app.post(f"{API_PREFIX}/documents/revalidate", response_model=RevalidateResponse)
def revalidate(request: RevalidateRequest):
    """What-if: re-run the Sentinel, dependency graph and review rules after a reviewer edits values."""
    return pipeline.revalidate(request.category, [(f.name, f.value) for f in request.fields])


@app.post(f"{API_PREFIX}/documents/{{document_id}}/corrections", response_model=CorrectionRecord, status_code=201)
def create_correction(document_id: str, request: CorrectionRequest):
    """PROVISIONAL contract (none was supplied). Stores old and new values in a hash-chained audit log."""
    record = audit.record_correction(document_id, request.field_name, request.corrected_value, request.reviewer,
                                     request.original_value, request.original_status, request.reason)
    return CorrectionRecord(**record)


@app.get(f"{API_PREFIX}/documents/{{document_id}}/corrections", response_model=list[CorrectionRecord])
def get_corrections(document_id: str):
    return [CorrectionRecord(**r) for r in audit.list_corrections(document_id)]


@app.get(f"{API_PREFIX}/audit/verify", response_model=AuditVerification)
def verify_audit():
    return AuditVerification(**audit.verify_chain())
