# Pramaan frontend feature guide

## Scope and status

This project is a frontend prototype with a document-analysis API integration.
The analyzer submits PDFs and UTF-8 TXT files to the configured backend; other
records and interactions remain illustrative fixtures or browser-session state
and must not be treated as production data or verified financial conclusions.

## Entry points and navigation

| Route | Status | Notes |
| --- | --- | --- |
| `/` | Implemented | Original full-screen Pramaan landing page and hero CTA are preserved. |
| `/app` | Implemented | Command Center workspace. |
| `/analyze` | Implemented | Validates PDF/TXT files and submits each file as multipart `file` to `/api/documents/analyze`; displays backend results and request errors. |
| `/documents` | Implemented | Search, category/status/demo risk filters, sortable columns, and pagination over illustrative fixtures. |
| `/documents/:documentId` | Implemented | Detail tabs for overview, fields, preview, evidence, consistency, dependencies, and history. Unknown IDs show a recovery state. |
| `/evidence` | Implemented | Illustrative source references, pages, confidence, and missing/ambiguous states. |
| `/consistency` | Implemented | Scenario-selectable checks, expected/observed values, differences, and unresolved dependencies. |
| `/trust-graph` | Implemented | Selectable fixture nodes and relationships with a legend and detail panel. |
| `/review` | Implemented | Local correction fields and simulated request/approve/reject actions with confirmation. |
| `/audit` | Implemented | Fixture and session-local events with filters and expandable details. |
| `/health` | Implemented | Shows API configuration separately from live service health, which this page does not probe. |
| `/settings` | Implemented | Theme state, in-memory Demo Mode control, supported-file guidance, and document-analysis API configuration. |
| `/dashboard` | Preserved | The earlier dashboard remains available separately. Its processing UI is labeled as simulated Demo Mode. |

The shared workspace shell provides route navigation, breadcrumbs, theme
controls, browser Back/Forward buttons, Recent Pages, and a Ctrl+K command
palette with route and action search. Browser Back/Forward and Alt+Left/Right
operate on browser navigation history. The keyboard shortcut is ignored while
focus is in an editor.

The document library includes an explicitly illustrative risk-severity
category; it is a demo label and is not a risk assessment or financial
conclusion. The trust graph supports selecting sample nodes and edges, review
actions require a reason and confirmation, and the audit trail supports
filtering and expanding event details.

## Demo scenarios

Four selectable illustrative fixtures cover a valid invoice, a discrepancy,
missing tax information, and an ambiguous/unsupported document. Scenario
selection is shared across the evidence, consistency, graph, and review
workspaces. Fixtures are maintained in `src/demoFixtures.ts`.

## Limitations and future work

- The backend accepts PDF and UTF-8 TXT uploads up to its configured size limit
  (10 MiB by default). Each selected file is submitted separately.
- Backend availability is not checked by the health/settings pages; an analysis
  request reports connection and server errors on the selected file.
- The sample document preview is a generated visual placeholder, not a
  rendering of the selected file.
- Review actions, audit events, and Demo Mode preferences other than the
  application theme are in-memory and can be lost on refresh.
- Authentication and notifications remain unimplemented. The backend service
  may be unavailable independently of frontend API configuration.
- Browser-level interaction, accessibility, and responsive checks should be
  rerun in the intended demo environment before presenting a release as
  verified.
