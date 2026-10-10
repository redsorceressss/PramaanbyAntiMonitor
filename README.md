# Anti Monitor — Hackathon Backend

FastAPI backend starter for an AI financial-document classifier. Includes registration/login, JWT bearer authentication, per-user document access, PDF/image upload, text extraction, a transparent keyword baseline classifier, metadata storage, manual review, history, and CSV export.

> Important: The included classifier is a **rule-based baseline**, not a trained AI model. Replace `app/classifier.py` with the AIML teammate's model while preserving the dictionary return format. Confidence is a heuristic score and must not be represented as calibrated model probability.

## 1. Windows PowerShell setup

Open PowerShell in this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `SECRET_KEY` to a long random value before use. Example to generate one:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the printed value into `.env` as `SECRET_KEY=...`.

## 2. Start the backend

```powershell
uvicorn app.main:app --reload --port 8000
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

SQLite database and `uploads/` are created locally.

## 3. Scanned documents / OCR

Digital PDFs with selectable text work without a separate OCR install. For scanned PDFs and image files, install the Tesseract OCR application for Windows and ensure `tesseract.exe` is available on PATH. If OCR is not installed, scanned files may fail with a processing error.

## 4. Frontend integration

Set the frontend API base URL to `http://127.0.0.1:8000`.

### Register
`POST /api/auth/register`
```json
{"full_name":"Demo User","email":"demo@example.com","password":"StrongPass123"}
```

### Login
`POST /api/auth/login`
```json
{"email":"demo@example.com","password":"StrongPass123"}
```

Both return:
```json
{"access_token":"...","token_type":"bearer","user":{"id":1,"full_name":"Demo User","email":"demo@example.com","created_at":"..."}}
```

Store the token only as needed for the prototype and send it on protected calls:
`Authorization: Bearer <access_token>`

For a production deployment, prefer secure HttpOnly cookies or a carefully designed OAuth flow and add rate limiting, HTTPS, email verification, password reset, session revocation, and security review.

### Upload and analyze
`POST /api/documents/analyze` as `multipart/form-data` with field name `file`.

### Other endpoints
- `GET /api/auth/me`
- `GET /api/documents`
- `GET /api/documents/{id}`
- `PATCH /api/documents/{id}/review`
- `GET /api/documents/{id}/history`
- `GET /api/documents/export`
- `DELETE /api/documents/{id}`

Example review body:
```json
{
  "document_type": "invoice",
  "metadata": {
    "vendor": "ABC Technologies",
    "invoice_number": "INV-1042",
    "date": "2026-10-08",
    "total_amount": 12500
  },
  "mark_reviewed": true
}
```

## 5. Frontend login example

```js
const API_BASE = "http://127.0.0.1:8000";

export async function login(email, password) {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Login failed");
  return data; // keep access_token and attach it to protected requests
}

export async function analyzeFile(file, token) {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_BASE}/api/documents/analyze`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Analysis failed");
  return data;
}
```

## 6. Integration notes for the team

- The UI/UX developer should map its login, signup, upload, result, review, history, and export screens to these endpoints.
- The AIML developer should implement `analyze_text(text)` in `app/classifier.py`, returning `document_type`, `classification_confidence`, `metadata`, `missing_fields`, `warnings`, and `review_required`.
- The tech lead should set the correct `FRONTEND_ORIGINS` in `.env`, review secrets and file limits, and run the end-to-end test.
- Use synthetic/redacted financial files for the hackathon. Do not upload real bank statements or credentials to a demo system.

## Limitations before production
This is a hackathon starter, not a production financial system. It does not include rate limiting, email verification, password reset, malware scanning, refresh-token/session revocation, migrations, or a full security audit. Uploaded documents are stored locally until deleted. Add a retention policy and HTTPS before handling real financial information.
