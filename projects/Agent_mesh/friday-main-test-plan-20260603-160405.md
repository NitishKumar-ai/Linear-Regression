# Test Diagram & Coverage Plan

## Execution Paths
1. `plan(context) -> Plan`
   - Flow: Receive goal -> call Flash-Lite -> return structured JSON steps
   - Coverage: Mock LLM tests, Prompt evaluations (Missing)
2. `execute(plan) -> Result`
   - Flow: Iterate steps -> execute code in E2B -> return result
   - Coverage: E2B sandbox mock, egress timeout tests (Missing)
3. `review(result) -> Verdict`
   - Flow: Compare result vs criteria -> loop or succeed
   - Coverage: Infinite loop terminator tests (Missing)

## Required Test Suites (2am Friday Protection)
- System-level token/cost caps tests
- Prompt-eval testing in CI (Promptfoo)
- Chaos testing for DBOS resume (killing worker mid-step)
