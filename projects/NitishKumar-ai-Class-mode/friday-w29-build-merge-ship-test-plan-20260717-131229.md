# Ship Test Plan — w29-build-merge (2026-07-17)

Diff: main...HEAD, 16 files, ~979 insertions. Issues: #335 (honest toast copy), #336 (admin attendance school_code fail-closed), #337 (view-event instrumentation), offer commitments (absentee call list + CSV export).

## Affected Pages/Routes

| Surface | Path | Change |
|---|---|---|
| Attendance page | `/attendance` | Toast no longer claims WhatsApp notification (#335); subtitle/tooltip reworded; fires `attendance_view` on mount (#337) |
| Analytics page | `/analytics` | Fires `report_view` on mount (#337) |
| Absentees page (NEW) | `/absentees` | Date picker, per-class grouping, `tel:` links, print, CSV download buttons; protected to principal/school_admin/admin |
| Attendance API | `POST /api/attendance` | Platform-admin writes derive school_code from marked students; 400 fail-closed when unresolvable (#336) |
| Absentees API (NEW) | `GET /api/attendance/absentees?date=` | Day's absentee list; principal/school_admin/admin only; admin needs `?schoolCode=`; 500 fail-loud |
| Usage API (NEW) | `POST /api/usage` | `attendance_view`/`report_view` allowlist; tenant scope from session, never body; 202 |
| Export API (NEW) | `GET /api/export/attendance.csv`, `GET /api/export/fees.csv` | UTF-8 BOM CSV, school-scoped, optional from/to bounds, 500 fail-loud |

## Key Interactions to Verify

1. Teacher marks a student absent → toast says only "N students marked." — no "notified on WhatsApp" line (pinned by `e2e/web/attendance.spec.ts`).
2. Platform admin (no school of own) marks attendance → row persisted with the STUDENTS' school_code, never NULL (`attendance_school_code.regression.test.ts`).
3. Principal opens `/absentees` → today's absent students grouped by class with parent phone `tel:` links; date change refetches.
4. Principal clicks "Attendance CSV"/"Fees CSV" → file downloads with BOM, opens vernacular names correctly in Excel.
5. Visiting `/attendance` or `/analytics` fires exactly one POST `/api/usage` per visit; failure never breaks the page (fire-and-forget).

## Edge Cases

- Admin marks students spanning two schools with the same class name → 400, no write (tenant-mix guard).
- Students with NULL school_code (orphans) → 400, no write.
- School-scoped user with no school posts a view event → 403 fail-closed (never NULL school_code row).
- Client-supplied `schoolCode` in `/api/usage` body is ignored — scope comes from session.
- Feature name outside `{attendance_view, report_view}` allowlist → 400.
- Malformed dates: absentees `?date=17-07-2026` → 400; export `from`/`to` non-ISO → 400.
- Platform admin hits absentees/export without `?schoolCode=` → 400 fail-closed.
- CSV escaping: names containing quotes/commas (`Ravi "RJ"`) → RFC-4180 doubled quotes; null fields → empty.
- Fee amounts render as currency units (400.00), not cents (40000).
- DB outage during absentees/export → 500, never a silently empty list/file (spec E5).
- Absentee with no parent phone → "no phone on file", no broken `tel:` link.

## Critical Paths

1. **Tenant isolation (P1)**: attendance rows and feature_usage rows must never persist with NULL school_code for school-bound actors; admin writes derive scope from targets, all reads/exports require an explicit school. Covered: `attendance_school_code.regression.test.ts` (4), `usage.test.ts` (8), `absentees_export.test.ts` (11), `export_edge_cases.test.ts` (5, new).
2. **Honesty invariant (#335)**: no fabricated "parents notified" claim anywhere; pinned by e2e exact-text toast assertion.
3. **Fail-loud exports (E5)**: query failure = 500 error, never an empty CSV a principal would mistake for "no data".
4. **Offer commitments**: absentee call list and no-cost data export are the pilot's paid promises — `/absentees` page flow needs an e2e pass before demo (currently server-tested only).

## Remaining E2E/Integration Gaps

- `/absentees` page flow (load, grouping, empty state, error state, CSV/print buttons) — no Playwright spec.
- `attendance_view`/`report_view` POST not asserted in e2e (effect exists, unverified in a real browser).
- `pgGetAbsenteesByDate` / `pgExportAttendanceRows` / `pgExportFeeRows` SQL never executed in tests (mocked at route boundary) — needs live-PG integration or e2e.
