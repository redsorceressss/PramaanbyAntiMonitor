# ANTIMONITOR (CBC103) - AI/ML service: Pramaan AI Trust Engine

AI-powered financial document classifier and trust layer for **Code Breaker Challenge 2.0, Problem Statement 36**.
Classify -> extract -> prove where each value came from -> check it -> flag uncertainty -> let a human correct it, with an auditable trail.

> Development status: synthetic-data prototype. Not a validated real-world model, fraud detector or compliance tool.

## What is implemented (v0.2)

| Area | Behaviour |
|---|---|
| Ingestion | PDF (PyMuPDF) and UTF-8 TXT. Size, extension and `%PDF-` signature checks. Rejects empty, malformed, **password-protected**, binary and over-long (>`MAX_PDF_PAGES`) files with stable `error_code`s. Detects scanned/image-only pages and garbled text layers. **OCR is not implemented**; such documents are reported as `ocr_required` and sent to review. |
| Classification | invoice, receipt, bank_statement, tax_document, purchase_order, **unknown**. TF-IDF + Logistic Regression blended with a transparent whole-word cue lexicon and an explicit "unknown" class. Returns confidence, top-3 `alternatives`, `matched_cues`, and an `ambiguous` flag when two categories are too close to call. |
| Extraction | Per-category field specs with **required vs optional** fields. Nothing is inferred: absent text means `missing`. Conflicting candidates (e.g. `Amount Due` vs `Total`) and ambiguous dates (`03/04/2026`) become `uncertain`, not a silent guess. Account / taxpayer IDs are masked. |
| EvidenceTrace | Every value carries the real source snippet, page, document offsets, page-relative offsets and value offsets. A self-audit re-slices the document text; any span that does not match is downgraded to `uncertain` (`evidence.verified`). |
| Financial Consistency Sentinel | `subtotal + tax = total` using `Decimal` arithmetic and a documented tolerance (`ARITHMETIC_TOLERANCE`, default 0.02 = two half-unit roundings), plus `currency_consistency`. A discrepancy is a **reason for review, never a fraud finding**. |
| Trust Dependency Graph | Nodes carry state (`supported/missing/invalid/uncertain/passed/unresolved/...`). Problems propagate field -> check -> `final_decision`, with readable `unresolved_chains` such as `tax_amount (missing) -> subtotal_plus_tax (unresolved) -> final_decision (review)`. |
| Human review | `human_review.reasons` (strings) plus structured `items` (`code`, `severity`, `fields`) for ambiguous/low-confidence classification, missing/invalid/uncertain fields, discrepancies, unresolved checks, OCR needs and low text quality. |
| Corrections | **Provisional** endpoints (no contract was supplied): old and new values, reviewer, reason and timestamp are stored in a **hash-chained SQLite audit log** (`/api/v1/audit/verify` detects edits or deletions). `revalidate` re-runs the Sentinel/graph/review after a reviewer edits values. |
| Routing (stretch) | **Simulated** queue suggestion per type; uncertain documents go to `human_review_queue`. Nothing is dispatched. |

"Accept eligible" (`trust_summary.accept_eligible`) means only that every configured check passed. It does not establish authenticity.

## Setup

Python 3.10+.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env      # optional; defaults are fine
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` (interactive API) and `/health`. The service reads real environment variables; `.env` is documentation (export the values or use your process manager).

Tests (run the full suite on your machine; see "Verification status"):

```powershell
python -m pytest -q
```

## API summary

| Method & path | Purpose |
|---|---|
| `GET /health` | Truthful component status: api, classifier, `pdf_text_extraction` (PyMuPDF importable), `audit_store` |
| `POST /api/v1/documents/analyze` | Multipart field **`file`** (`.pdf`/`.txt`, <=10 MiB). Returns the analysis (see `docs/examples/`) |
| `POST /api/v1/documents/revalidate` | What-if: `{category, fields:[{name,value}]}` -> Sentinel, graph, review |
| `POST /api/v1/documents/{document_id}/corrections` | **Provisional.** Record a reviewer correction (201) |
| `GET /api/v1/documents/{document_id}/corrections` | List corrections for a document |
| `GET /api/v1/audit/verify` | Verify the audit hash chain |

Errors are `{ "detail": "...", "error_code": "..." }` with 400 (invalid/empty/malformed/encrypted/too many pages), 413 (too large), 415 (unsupported extension), 422 (invalid request/correction), 500 (generic message, no stack trace).
Full details, field semantics and the integration checklist: `docs/api-integration.md`, `docs/compatibility-checklist.md`.

## Demo data, evaluation and honesty

* `data/samples/*.pdf` - **synthetic** demo documents covering every behaviour (clean invoice, the deck's Rs 3,200 gap, unreadable tax, ambiguous invoice/receipt, unsupported memo, scanned image-only PDF, ...). Regenerate with `python scripts/make_samples.py` (needs `reportlab`, dev-only).
* The classifier trains at startup on **synthetic** text from `app/ml/synthetic.py`. `python scripts/evaluate_synthetic.py` runs a held-out *synthetic* wording check. It scores 100% because the task is trivially easy for same-author data; **that is not real-world accuracy** and must not be quoted as such.
* Confidence values are blended heuristic scores, **not calibrated probabilities**. No production accuracy is claimed. Real claims need a labelled set of real documents and a held-out split.
* Regex extraction proves "this text was found", not that the value is semantically right. Known limits: CGST+SGST splits are not summed; multi-currency/`$` ambiguity is flagged, not resolved; table-heavy layouts may separate labels from values.

## Security and privacy

No document content is logged; only the error type is logged for unexpected failures. Uploads are validated and never executed or written to disk by the service; Starlette may spool large multipart bodies to a temp file, so enforce size limits at your gateway too. Account and taxpayer identifiers are masked in values and evidence. The audit log stores reviewer values only (never document text). No third-party service receives documents. Before any deployment beyond a local demo add HTTPS, authentication, rate limiting, access control and a retention policy.

## Verification status

See "Verification status" in `docs/compatibility-checklist.md` for exactly what was executed in the build sandbox and what still needs a run on a machine with the dependencies installed.
