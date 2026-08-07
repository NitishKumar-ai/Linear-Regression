# AgentMesh Operator Recovery — Engineering Test Plan

## Release Gate

The milestone is releasable only when the real SQLite-backed server and browser complete this sequence:

```text
start with idempotency key
  -> observe canonical SSE
  -> protected side effect succeeds once
  -> later task fails deterministically
  -> inspect workflow and task evidence
  -> retry failed step
  -> completed side effect is reused, not repeated
  -> final artifact matches assertion
  -> engage cooperative halt
  -> new start is rejected
  -> release halt
  -> new start succeeds
  -> clean shutdown with zero post-close polling
```

## Unit Coverage

| Surface | Branches |
|---|---|
| Request schema | missing, blank, trimmed, oversized goal/context, invalid idempotency key, valid body |
| Error mapping | typed 400, 404, 409, 503, 500 sanitization, request ID |
| Start authority | new start, duplicate reuse, conflicting payload, halt blocked, persistence failure |
| Lifecycle state machine | every allowed and forbidden pause/resume/retry/terminate transition |
| Local mutex | acquisition, release on success, release on throw, independent workflow keys |
| Event adapter | canonical event, malformed JSON, invalid shape, unknown type, bounded diagnostic |
| Evidence redaction | secret keys, nested values, truncation, explicit reveal metadata |
| Shutdown coordinator | ordering and idempotent repeated close |

## Integration Coverage

| Test | Real components | Assertions |
|---|---|---|
| Route composition | Nest/Express app factory + random port | `/api/agents/:id/run` exists and validates |
| Idempotent start race | HTTP + SQLite + executor + mutex | N concurrent requests create one workflow |
| Halt/start barrier | HTTP + halt store + start authority | Halt between validation and persistence prevents creation |
| Lifecycle race | SQLite + executor + queues | Concurrent stale commands produce one valid transition and typed conflicts |
| Recovery workload | HTTP + worker pool + SQLite + deterministic tool/LLM | Failure, retry, artifact, exactly-once side effect |
| SSE recovery | Real event bus + HTTP stream | Heartbeat, bounded queue policy, reconnect refetch |
| Restart recovery | Persisted SQLite file + process restart | Durable workflow/task/idempotency receipt recovered |
| Shutdown | Active pollers + HTTP + SQLite | Pollers stop before DB destroy; no unhandled errors |
| Network posture | app factory configuration | Loopback default; wildcard/non-loopback rejected |

## UI Component Coverage

| Component | Required states |
|---|---|
| Agents/start | loading, empty, error, validation, pending, duplicate receipt, halt 503 |
| Active recovery workspace | running, failed, retrying, completed, stale/reconnecting |
| Workflow evidence | paginated tasks, redacted output, truncated output, reveal |
| Cooperative halt | disengaged, engaging, engaged with reason, releasing, failure |
| Responsive inspector/dialog | desktop dock, tablet overlay, mobile full-screen, focus/Escape/restore |
| Mutation receipts | success, typed conflict, request ID, retry action |

## Browser E2E

Use Playwright against the real `server-lite` application factory and Vite UI:

1. Verify persistent local-only mode label.
2. Launch the seeded deterministic recovery workload.
3. Confirm the URL contains the active workflow ID.
4. Observe running evidence and SSE connection state.
5. Observe the injected failure and inspect the failed task.
6. Retry safely with an operator reason.
7. Confirm the protected side effect count remains exactly one.
8. Confirm the final artifact.
9. Refresh and reopen the same run by URL.
10. Simulate SSE disconnect; confirm stale marker and reconciliation.
11. Engage halt; confirm copy states cooperative semantics.
12. Confirm a new run returns the stable 503 error.
13. Release halt and start a new run.
14. Repeat the inspector flow at a narrow viewport with keyboard-only navigation.

## Non-Functional Gates

- No fixed ports in tests.
- No mocks for persistence, HTTP routing, worker queues, or lifecycle transitions in integration tests.
- No test may pass while logging unhandled rejections, database-after-close access, or failed background loops.
- Event and task payload limits have explicit fixtures at boundary-1, boundary, and boundary+1.
- Concurrent tests use barriers, not timing-only sleeps.
- CI stores the failed workflow/task/event transcript as an artifact.

## Required Test Files

- `agent-runtime/test/agent-routes.test.ts`
- `core/test/WorkflowExecutorOps.test.ts`
- `server-lite/test/operator-loop.integration.test.ts`
- `server-lite/test/operator-start-race.integration.test.ts`
- `server-lite/test/shutdown.integration.test.ts`
- `ui/src/lib/serverLiteApi.test.ts`
- `ui/src/lib/events.test.ts`
- `ui/src/pages/AgentsPage.test.tsx`
- `ui/src/components/WorkflowInspector.test.tsx`
- `ui/e2e/operator-recovery.spec.ts`
