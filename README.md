# Pramaan — integrated frontend

React + Vite frontend for the deployed FastAPI service (`https://pramaan-backend-lb3p.onrender.com`).

## Do not open `index.html` by double-clicking it
This is a React + Vite app; `index.html` only loads `/src/main.tsx`, which a browser cannot run from disk.
Run it through the dev server (Node.js 20.19+ required):

```bash
npm install
npm run dev
```
Open the **http://localhost:…** address Vite prints (Windows: double-click `START-WINDOWS.bat`).

## Analysis mode
By default **no backend is used**. The Analyze page reads the PDF/TXT in your browser (`src/localAnalyzer.ts`),
classifies it, extracts document number/date/subtotal/tax/total, runs arithmetic consistency checks and shows the
result in the existing UI. Files never leave your machine. Limits: PDFs need a text layer (scanned PDFs need OCR),
and the results are rule-based heuristics, not the Pramaan AI engine.

To switch back to the deployed API, set `VITE_USE_BACKEND=true` in `.env.local` and restart. In that mode the route is
`POST /api/documents/analyze` (multipart field `file`), it needs an access token (Settings → Backend access token, or
`VITE_API_TOKEN`), and a deployed build needs CORS enabled on the backend.

## Production build
```bash
npm run build && npm run preview
```
In local mode a deployed build needs no backend. Static hosts also need a "serve index.html for unknown paths" rewrite for deep links like `/analyze`.

## Scope
Only the Analyze page performs real analysis. Dashboard, library, evidence, consistency,
trust-graph, review and audit screens still use labelled demo fixtures — wire them only after confirming
their schemas in `/docs`.
