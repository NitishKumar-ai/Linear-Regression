# Test Plan — w29-build-merge ship (delta audit 2026-07-18)

Scope: changes since the 2026-07-17 audit of f0a0b59..0884788 (scored 75%, 3 accepted gaps).
Delta = commits 8ec3374, 6d84c94, 013439d + uncommitted working-tree changes
(onboarding.ts helper, 3 new test files, whatsapp mock fix).

## Affected Pages/Routes

| Surface | Change | Automated coverage |
|---|---|---|
| Sidebar (principal, school_admin) | New "Absentees" nav item → /absentees (8ec3374) | None (no e2e; carried gap) |
| /absentees page | Unchanged this delta; now reachable via nav | None (carried, accepted 07-17) |
| POST /api/attendance (upsert via pgMarkAttendance) | note = COALESCE(EXCLUDED.note, attendance.note) (6d84c94) | attendance_note_preserve.regression.test.ts — real SQL exercised |
| POST /api/onboarding/invite/teacher | Now resolves school via resolveInvitingAdminSchool() | invite_teacher_non_creator_school.test.ts |
| GET /api/onboarding/invite/teacher/list | Same helper | invite_teacher_non_creator_school.test.ts |
| GET /api/gdpr/export | Unchanged; newly tested | gdpr.test.ts (scoping/auth/404; zip stream NOT covered) |
| DELETE /api/gdpr/delete | Unchanged; newly tested | gdpr.test.ts (happy/auth/error) |
| POST /api/upload | Unchanged; newly tested | upload.test.ts (rejections + diskPathToUrl; no accept path) |
| WhatsApp automation suite | BULLMQ_PREFIX mock fix re-enables previously import-failing suite | whatsapp-automation.test.ts passing again |

## Key Interactions to Verify

1. **/absentees via nav**: log in as principal and as school_admin → "Absentees" (PhoneCall icon) appears under Attendance in the sidebar → click → call list loads for today. Verify platform admin does NOT see the link (page would 400 without schoolCode).
2. **Attendance note preservation**: mark a student absent with a note (mobile path / API with note) → re-save the same class from the web marking page (status only) → note still present on /absentees and in DB. Then save with a new note → note updates.
3. **Teacher invite by non-creator admin**: as a principal who joined via /invite/staff (users.school_code set, no schools.created_by_uid match) → POST /invite/teacher returns 201 and the invite is attached to the joined school; GET /invite/teacher/list returns that school's invites. Also verify the original creator can still invite (created_by_uid path — NOT unit-tested, verify manually).
4. **GDPR export**: authenticated GET /api/gdpr/export returns a zip containing only the caller's own data (archiver/createRequire path is untestable in vitest — verify against a running server).
5. **GDPR delete**: DELETE /api/gdpr/delete removes the caller's account; failure returns 500, not silent success.
6. **Upload rejection**: .html, .exe, and image-MIME/.svg-extension spoof are all rejected with no url returned and nothing written to public/uploads; a legitimate .png upload still succeeds (accept path NOT unit-tested).

## Edge Cases

- Status-only re-save with an OLDER updated_at than the stored row → upsert WHERE clause skips the update entirely (note and status both retained).
- Save that explicitly carries a note still overwrites (COALESCE takes EXCLUDED.note when non-null). Clearing a note from the web is unsupported by design — document, don't "fix".
- Admin linked by schoolId but not schoolCode (invite-accept variance) → helper's pgFindSchoolById branch (unit-tested).
- Admin with neither created school nor linked school → 404 "Complete school setup first" (unit-tested for POST; list route 404 untested).
- pgFindUserById returns null (deleted user with live token) → helper returns null → 404 (outcome-equivalent to the both-null test, not directly exercised).
- GDPR export when the user row vanished mid-session → 404 before archiver loads (unit-tested).
- Upload with no file field → 400 (unit-tested).

## Critical Paths

1. **/absentees call list** — pilot-offer deliverable (#331): nav → page → today's absentees with notes → CSV download. No automated e2e; manual QA before ship (carried accepted gap).
2. **Attendance note preservation (ISSUE-002)** — data-loss regression guarded by attendance_note_preserve.regression.test.ts, which drives the real pgMarkAttendance SQL; reverting to EXCLUDED.note fails the test.
3. **Teacher invite by non-creator admin** — unlocks invited principals/school_admins to build out their staff; schoolCode and schoolId fallback branches unit-tested at both call sites. Creator (created_by_uid) branch has no test anywhere — regression here would lock out original workspace creators; verify manually.
4. **GDPR export/delete** — compliance-critical; scoping (own-id-only) and delete error propagation unit-tested. Zip-stream happy path has NO automated coverage (the in-file claim of e2e coverage is inaccurate) — verify export manually against a live server.
5. **Upload rejection (stored-XSS boundary)** — html/exe/svg-spoof rejection unit-tested; files are rejected before storage.

## Known gaps (accepted or carried)

- No Playwright spec for /absentees or the new nav link (carried from 07-17 audit).
- POST /api/usage unthrottled (carried, accepted).
- pg-queries helpers mostly exercised via mocks (carried; narrowed — pgMarkAttendance upsert SQL now exercised for real).
- resolveInvitingAdminSchool creator branch (B1) untested (new).
- GDPR export zip-stream happy path untested anywhere (new; in-test comment overstates e2e coverage).
- Upload accept happy path (200 + url) untested (new).
