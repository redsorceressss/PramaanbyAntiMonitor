"""Runtime configuration (environment-driven, documented in .env.example)."""
import os
from pathlib import Path

APP_NAME = "ANTIMONITOR - Pramaan AI Trust Engine"
APP_VERSION = "0.2.0"
API_PREFIX = "/api/v1"

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "50"))
MIN_TEXT_CHARS = int(os.getenv("MIN_TEXT_CHARS", "30"))

# Below this blended score a prediction is demoted to "unknown".
CLASSIFICATION_THRESHOLD = float(os.getenv("CLASSIFICATION_THRESHOLD", "0.35"))
# Top-two scores closer than this => the document may belong to two categories.
CLASSIFICATION_MARGIN = float(os.getenv("CLASSIFICATION_MARGIN", "0.08"))
# Below this score a (non-unknown) prediction is still sent to a human reviewer.
REVIEW_CONFIDENCE_THRESHOLD = float(os.getenv("REVIEW_CONFIDENCE_THRESHOLD", "0.55"))

# Financial Consistency Sentinel: |total - (subtotal + tax)| <= tolerance passes.
# 0.02 = two independent half-unit roundings (e.g. rounded subtotal and rounded tax).
ARITHMETIC_TOLERANCE = float(os.getenv("ARITHMETIC_TOLERANCE", "0.02"))

# Share of extracted characters that must look like normal text before we trust it.
MIN_TEXT_QUALITY = float(os.getenv("MIN_TEXT_QUALITY", "0.60"))

_default_db = Path(__file__).resolve().parents[2] / "data" / "audit.sqlite3"
AUDIT_DB_PATH = os.getenv("AUDIT_DB_PATH", str(_default_db))

CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",") if x.strip()]
