# Test Plan: Animated Step Card Onboarding

## Test Diagram & Coverage Map

| Code Path / Flow | Type of Test Needed | Existing Coverage | Action |
| --- | --- | --- | --- |
| **UX: Screen Transitions** | Manual / Playwright | None | Defer to manual QA (P3) |
| **UX: LocalStorage Resume** | Unit / Component | None | Write React Testing Library test for `useLocalStorage` state initialization |
| **API: Single Payload Submission** | Integration | None | Write integration test for `POST /api/onboarding/complete` with valid full payload |
| **API: Validation (Security)** | Unit | None | Write Zod schema tests ensuring payloads > 5KB or excessive array items are rejected |
| **API: Role Escalation Protection** | Integration | None | Test that a user with existing workspace invite cannot change role to `principal` via onboarding |
| **DB: Orphaned Data** | N/A | N/A | Mitigated entirely by client-side accumulation |
| **Guard Hook (`use-onboarding-guard`)** | Unit | None | Test redirect logic (onboarding_complete true/false, role skips) |

## Evals
- No LLM/Prompt changes in this feature. Evals not required.

## 2am Friday Breaks
- The primary risk is a DB constraint violation during the single-payload submit. The single-transaction submission must either fully succeed or fully rollback to prevent corrupted workspace states.
