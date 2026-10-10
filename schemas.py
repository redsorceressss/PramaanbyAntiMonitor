"""Response/request contract of the AI/ML service.

All additions over v0.1 are OPTIONAL fields with defaults, so existing consumers keep working.
"""
from typing import Literal

from pydantic import BaseModel, Field

DocumentType = Literal["invoice", "receipt", "bank_statement", "tax_document", "purchase_order", "unknown"]
FieldStatus = Literal["supported", "missing", "invalid", "uncertain", "not_applicable"]


class HealthResponse(BaseModel):
    status: str
    components: dict[str, bool]
    version: str | None = None


class Evidence(BaseModel):
    source_text: str | None = None
    page: int | None = None
    start_offset: int | None = None          # offsets into the concatenated document text
    end_offset: int | None = None
    page_start_offset: int | None = None     # same span, relative to its page
    page_end_offset: int | None = None
    value_start_offset: int | None = None    # span of just the value inside the snippet
    value_end_offset: int | None = None
    available: bool = False
    verified: bool | None = None             # EvidenceTrace self-audit: snippet really sits at these offsets
    redacted: bool = False                   # sensitive identifiers are masked in value and snippet


class ExtractedField(BaseModel):
    name: str
    value: str | None = None
    normalized_value: str | None = None
    status: FieldStatus
    confidence: float | None = None          # always null: no calibrated extraction confidence exists
    evidence: Evidence = Field(default_factory=Evidence)
    reason: str | None = None
    required: bool = True
    candidates: list[str] = Field(default_factory=list)  # other distinct values found (conflicts)


class ConsistencyCheck(BaseModel):
    check_id: str
    status: Literal["passed", "discrepancy", "unresolved", "not_applicable"]
    expected_value: float | None = None
    observed_value: float | None = None
    difference: float | None = None
    explanation: str
    input_fields: list[str] = Field(default_factory=list)
    unresolved_dependencies: list[str] = Field(default_factory=list)
    dependency_status: dict[str, str] = Field(default_factory=dict)  # field -> status of each input


class DependencyInfo(BaseModel):
    nodes: list[str] = Field(default_factory=list)
    edges: list[dict[str, str]] = Field(default_factory=list)
    node_states: dict[str, str] = Field(default_factory=dict)
    unresolved_chains: list[str] = Field(default_factory=list)  # human-readable propagation paths


class Alternative(BaseModel):
    type: str
    score: float


class Classification(BaseModel):
    predicted_type: DocumentType
    confidence: float | None = None
    interpretation: str
    alternatives: list[Alternative] = Field(default_factory=list)
    ambiguous: bool = False                  # top-two categories too close to call
    matched_cues: list[str] = Field(default_factory=list)
    method: str | None = None


class ReviewItem(BaseModel):
    code: str
    severity: Literal["high", "medium", "low"]
    message: str
    fields: list[str] = Field(default_factory=list)


class ReviewDecision(BaseModel):
    required: bool
    reasons: list[str] = Field(default_factory=list)
    items: list[ReviewItem] = Field(default_factory=list)


class DocumentInfo(BaseModel):
    file_kind: str
    page_count: int
    character_count: int
    ocr_required: bool = False
    scanned_pages: list[int] = Field(default_factory=list)
    text_quality: float | None = None


class TrustSummary(BaseModel):
    """Plain counts only - deliberately NOT a composite 'trust score' (it could not be calibrated)."""
    fields_total: int
    fields_supported: int
    fields_with_verified_evidence: int
    checks_passed: int
    checks_discrepancy: int
    checks_unresolved: int
    accept_eligible: bool
    disclaimer: str


class Routing(BaseModel):
    simulated: bool = True
    queue: str
    after_review: str | None = None


class AnalyzeResponse(BaseModel):
    document_id: str
    processing_status: Literal["completed", "review_required", "failed"]
    classification: Classification
    extracted_fields: list[ExtractedField]
    consistency_checks: list[ConsistencyCheck]
    trust_dependencies: DependencyInfo
    human_review: ReviewDecision
    warnings: list[str] = Field(default_factory=list)
    processing_duration_ms: float | None = None
    document_info: DocumentInfo | None = None
    trust_summary: TrustSummary | None = None
    routing: Routing | None = None


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


# ---- reviewer corrections (PROVISIONAL contract: no tech-lead contract was supplied) ----
class CorrectionRequest(BaseModel):
    field_name: str = Field(min_length=1, max_length=64)
    corrected_value: str = Field(min_length=1, max_length=500)
    original_value: str | None = Field(default=None, max_length=500)
    original_status: str | None = Field(default=None, max_length=32)
    reviewer: str = Field(min_length=1, max_length=100)
    reason: str | None = Field(default=None, max_length=500)


class CorrectionRecord(BaseModel):
    correction_id: str
    document_id: str
    field_name: str
    original_value: str | None = None
    corrected_value: str
    normalized_corrected_value: str | None = None
    original_status: str | None = None
    reviewer: str
    reason: str | None = None
    created_at: str
    prev_hash: str
    record_hash: str


class AuditVerification(BaseModel):
    valid: bool
    records_checked: int
    first_broken_record: int | None = None


class RevalidateField(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    value: str = Field(max_length=500)


class RevalidateRequest(BaseModel):
    category: DocumentType
    fields: list[RevalidateField]


class RevalidateResponse(BaseModel):
    category: DocumentType
    extracted_fields: list[ExtractedField]
    consistency_checks: list[ConsistencyCheck]
    trust_dependencies: DependencyInfo
    human_review: ReviewDecision
    trust_summary: TrustSummary
