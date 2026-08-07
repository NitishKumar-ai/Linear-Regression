# Architectural Design Plan: Integrating the AI Module in Agent Mesh Using Multi-Agent Orchestration

This document details the architectural design and implementation plan for integrating the [@agentmesh/ai](file:///Users/friday/Downloads/Agent_mesh/ai) module into the Agent Mesh ecosystem, specifically detailing registration, execution workflows, and orchestrations inside [server-lite](file:///Users/friday/Downloads/Agent_mesh/server-lite/src/index.ts) and [agent-runtime](file:///Users/friday/Downloads/Agent_mesh/agent-runtime).

---

## 1. System Overview and Component Breakdown

Agent Mesh employs a distributed, asynchronous task-processing design. The coordination of LLM resources and agent behaviors spans three primary modules:
1. **`@agentmesh/ai`**: Encapsulates LLM providers, embedding generators, token budget enforcement, and system task wrappers.
2. **`@agentmesh/agent-runtime`**: Runs worker loops polling task queues, evaluating agent behaviors, running custom tools, and monitoring agent budgets.
3. **`server-lite` / Core**: Orchestrates workflows, schedules tasks, evaluates routing logic (deciders), and maintains persistent queues.

### Component Relationship Diagram

```
+--------------------------------------------------------------------------------------------------------+
|                                              SERVER-LITE                                               |
|                                                                                                        |
|  +--------------------+      +--------------------+      +--------------------+      +--------------+  |
|  |  WorkflowService   |      |    TaskService     |      |   DeciderService   |      |  SyncEngine  |  |
|  +---------+----------+      +---------+----------+      +---------+----------+      +-------+------+  |
|            |                           |                           |                         |         |
|            v                           v                           v                         v         |
|  +---------+---------------------------+---------------------------+-------------------------+------+  |
|  |                                     WorkflowExecutorOps (Engine)                                 |  |
|  +-------------------------------------+------------------------------------------------------------+  |
|                                        |                                                               |
|                                        | registers                                                     |
|                                        v                                                               |
|                        +---------------+---------------+                                               |
|                        |      SystemTaskRegistry       |                                               |
|                        |  - LLM_CHAT_COMPLETE          |                                               |
|                        |  - SUB_WORKFLOW, FORK, JOIN   |                                               |
|                        +-------------------------------+                                               |
+----------------------------------------|---------------------------------------------------------------+
                                         | polls queues / updates tasks
                                         v
+----------------------------------------|---------------------------------------------------------------+
|                                 AGENT-RUNTIME (Worker Pool)                                            |
|                                                                                                        |
|  +--------------------------------------------------------------------------------------------------+  |
|  |                                        AgentWorkerPool                                           |  |
|  |  Polls queues in loop. For each task, checks BudgetManager and triggers the appropriate task     |  |
|  |  handler, passing execution state to AgentWorkflowExecutor.                                      |  |
|  +----+----------------------+-----------------------+---------------------+--------------------+----+  |
|       |                      |                       |                     |                    |      |
|       v                      v                       v                     v                    v      |
|  +----+----+           +-----+------+          +-----+------+        +-----+------+       +-----+----+ |
|  |AgentPlan|           |AgentExecute|          |AgentReview |        |ChatComplete|       |Embeddings| |
|  +----+----+           +-----+------+          +-----+------+        +-----+------+       +-----+----+ |
|       |                      |                       |                     |                    |      |
|       | calls                | invokes               | evaluates           | routes via         |      |
|       v                      v                       v                     v                    v      |
|  +----+----------------------+-----------------------+---------------------+--------------------+----+  |
|  |                                          @agentmesh/ai                                           |  |
|  |                                                                                                  |  |
|  |  +--------------------+      +--------------------+      +--------------------+                  |  |
|  |  |       LLMs         |      |    ModelClient     |      |  AIModelProvider   |                  |  |
|  |  +--------------------+      +--------------------+      +--------------------+                  |  |
|  |  |   DocumentLoader   |      |JsonSchemaValidator |      |   BudgetManager    |                  |  |
|  |  +--------------------+      +--------------------+      +--------------------+                  |  |
|  +--------------------------------------------------------------------------------------------------+  |
+--------------------------------------------------------------------------------------------------------+
```

### Module Roles and Code References

*   **[LLMs](file:///Users/friday/Downloads/Agent_mesh/ai/src/main/typescript/LLMs.ts)**: Configures and manages calls to various LLMs. It coordinates inputs, handles prompts, parses JSON schemas with [JsonSchemaValidator](file:///Users/friday/Downloads/Agent_mesh/ai/src/main/typescript/index.ts), and feeds content fragments using [DocumentLoader](file:///Users/friday/Downloads/Agent_mesh/ai/src/main/typescript/index.ts).
*   **[ModelClient](file:///Users/friday/Downloads/Agent_mesh/ai/src/main/typescript/routing/ModelClient.ts)**: Acts as a semantic router, selecting the underlying target provider based on task routing properties or client inputs.
*   **[AIModelProvider](file:///Users/friday/Downloads/Agent_mesh/ai/src/main/typescript/AIModelProvider.ts)**: Hosts provider adaptors like [AnthropicProvider](file:///Users/friday/Downloads/Agent_mesh/ai/src/main/typescript/providers/AnthropicProvider.ts) and [GeminiProvider](file:///Users/friday/Downloads/Agent_mesh/ai/src/main/typescript/providers/GeminiProvider.ts).
*   **[AgentWorkerPool](file:///Users/friday/Downloads/Agent_mesh/agent-runtime/src/agent/AgentWorkerPool.ts)**: Spawns independent threads executing long-polling queries on the queue backend via [TaskService](file:///Users/friday/Downloads/Agent_mesh/rest/src/controllers/TaskService.ts).
*   **[AgentPlan](file:///Users/friday/Downloads/Agent_mesh/agent-runtime/src/tasks/AgentPlan.ts)**: High-level planning module that instructs the LLM to generate sequential tasks towards a designated goal.
*   **[AgentExecute](file:///Users/friday/Downloads/Agent_mesh/agent-runtime/src/tasks/AgentExecute.ts)**: Drives the iterative loop (Action -> Observation -> Parse) via [AgentLoop](file:///Users/friday/Downloads/Agent_mesh/agent-runtime/src/tools/AgentLoop.ts) until the task is complete.
*   **[AgentReview](file:///Users/friday/Downloads/Agent_mesh/agent-runtime/src/tasks/AgentReview.ts)**: Critic module that checks outputs and determines if the task criteria were successfully achieved.

---

## 2. Multi-Agent Orchestration Workflows

The Agent Mesh core supports complex structures like sequential pipelines, conditional loops, child sub-workflows, and parallel execution. These structures route execution data across multiple worker processes.

### 2.1 Sub-Workflow Execution Routes (`SUB_WORKFLOW`)

A workflow can split off dedicated, self-contained sub-tasks to child agents by triggering a `SUB_WORKFLOW` system task.

```
[Parent Workflow]
       |
       v
+--------------+
| SUB_WORKFLOW | ------> Creates Idempotent Sub-Workflow ID
+-------+------+         Starts Sub-Workflow definition in DB
        |
        +-- (Sub-workflow in RUNNING state)
        |
        v
    [Engine Polls] <---------------------------------------------+
        |                                                        |
        v                                                        |
   Is Terminal?                                                  |
     /      \                                                    |
   (Yes)    (No) ------------------------------------------------+
     |
     v
Update Parent Task
- status = COMPLETED/FAILED
- outputData = Sub-Workflow Output
```

1.  **Instantiation**: When the [SubWorkflow](file:///Users/friday/Downloads/Agent_mesh/core/src/execution/tasks/SubWorkflow.ts) task starts, it generates a unique, idempotent ID: `${parentWorkflowId}_${taskId}_${retryCount}`.
2.  **Registration**: It invokes `workflowExecutor.startWorkflowIdempotent()`. This populates the database and registers the child workflow without executing it immediately on the caller thread.
3.  **State Management**: The parent `SUB_WORKFLOW` task transitions to `IN_PROGRESS` in the DB.
4.  **Completion Polling**: In every evaluation sweep, the `SubWorkflow` system task checks if the sub-workflow status is terminal. Once terminal, it copies the child output variables to the parent task's `outputData` and marks the task as `COMPLETED`.

### 2.2 Parallel Orchestration (`FORK_JOIN`)

For tasks requiring concurrent processes (e.g., parallel code reviews, simultaneous market research, or multi-agent consultations), `FORK` and `JOIN` coordinate execution.

```
           +--------------+
           |  FORK Task   |
           +---+------+-+-+
               |      | |
       +-------+      | +-------+
       |              v         |
       v          [Agent 2]     v
   [Agent 1]      (Parallel)  [Agent 3]
   (Parallel)                 (Parallel)
       |              |         |
       +-------+      | +-------+
               v      v v
           +--------------+
           |  JOIN Task   |
           +--------------+
```

1.  **Fork Execution**: The [Fork](file:///Users/friday/Downloads/Agent_mesh/core/src/execution/tasks/Fork.ts) task mapper spawns concurrent paths defined in the workflow definition. These are pushed to the task queue.
2.  **Worker Pick-up**: Distinct worker pools poll and run these tasks concurrently (e.g. `AgentWorkerPool` instances handling `agent_execute`).
3.  **Join Synchronization**: The [Join](file:///Users/friday/Downloads/Agent_mesh/core/src/execution/tasks/Join.ts) task acts as a barrier. It blocks downstream execution until all tasks listed in its fork definition reach a terminal status.

---

## 3. Concrete Data Flows and APIs

This section outlines data flows and JSON payload transformations during multi-agent task execution.

### 3.1 LLM Task Request / Response

When [LlmChatComplete](file:///Users/friday/Downloads/Agent_mesh/ai/src/main/typescript/tasks/LlmChatComplete.ts) is triggered, it invokes `llms.chatComplete()` using the routed provider.

#### Input Data Flow (`task.inputData`)
```json
{
  "agentId": "commit_guard",
  "model": "claude-3-7-sonnet-20250219",
  "messages": [
    {
      "role": "user",
      "content": "Perform a security scan on git repo 'https://github.com/example/repo'."
    }
  ],
  "temperature": 0.2
}
```

#### Output Data Flow (`task.outputData` after completion)
```json
{
  "content": "{\"thought\": \"Scanning code...\", \"tool\": \"security_scan\", \"args\": {\"path\": \"./src\"}}",
  "tokenUsed": 350,
  "promptTokens": 200,
  "completionTokens": 150,
  "costUsd": 0.0007
}
```

---

## 4. Concrete Test Strategies and Edge Cases

A resilient agent framework must handle errors, budget constraints, and network instability.

### 4.1 Test Strategies

*   **Cooperative Killswitch Tests**: Verify that triggering the [Killswitch](file:///Users/friday/Downloads/Agent_mesh/agent-runtime/src/killswitch/Killswitch.ts) halts active agent loops immediately. Tasks must update to `CANCELED` status rather than hanging indefinitely.
*   **Budget Depletion Integration Tests**: Execute a multi-stage workflow with the [BudgetManager](file:///Users/friday/Downloads/Agent_mesh/agent-runtime/src/agent/BudgetManager.ts) configured to a low limit. Verify that the agent halts when the limit is hit, updates the active task to `FAILED` status, and logs `BUDGET_EXCEEDED` in `reasonForIncompletion`.
*   **Sub-Workflow Cancellation Test**: Terminate a parent workflow while a child sub-workflow is running. Verify that `SubWorkflow.cancel()` triggers, marking the child sub-workflow as `TERMINATED`.
*   **Orchestration Parity Unit Tests**: Validate that the [DeciderService](file:///Users/friday/Downloads/Agent_mesh/core/src/execution/DeciderService.ts) correctly processes sequential outputs, branch evaluations, and dynamic fork joins.

### 4.2 Handling Failures and Edge Cases

| Edge Case | Detection Mechanism | Mitigation Strategy |
| :--- | :--- | :--- |
| **Model Rate Limiting** | Catching HTTP `429` / `503` exceptions. | Apply exponential backoff and jitter in [ModelClient](file:///Users/friday/Downloads/Agent_mesh/ai/src/main/typescript/routing/ModelClient.ts). |
| **Budget Exceeded** | `BudgetManager.checkBudget()` returning `allowed: false`. | Transition task to `FAILED` and cancel downstream workflows. |
| **Worker Crash mid-Loop** | Unreported task statuses exceeding `heartbeatTimeout`. | The [WorkflowSweeper](file:///Users/friday/Downloads/Agent_mesh/core/src/execution/WorkflowSweeper.ts) re-queues orphaned tasks. |
| **Malformed LLM Output** | JSON parse failures in critic results. | Standardize formatting prompts and fallback to an agent repair loop. |

---

## ## GSTACK REVIEW REPORT

### 1. Decisions Logged
*   **D1 (Architecture)**: Implement cascade termination in the core [WorkflowExecutor](file:///Users/friday/Downloads/Agent_mesh/core/src/execution/tasks/SubWorkflow.ts) so child sub-workflows are terminated automatically when parent workflows are cancelled.
*   **D2 (Code Quality)**: Centralize LLM token pricing inside [ModelClient](file:///Users/friday/Downloads/Agent_mesh/ai/src/main/typescript/routing/ModelClient.ts) or a dedicated pricing registry instead of using hardcoded estimations inside the task.
*   **D3 (Performance)**: Configure [server-lite](file:///Users/friday/Downloads/Agent_mesh/server-lite/src/index.ts) SQLite connection to enable Write-Ahead Logging (WAL) mode and a 5000ms `busy_timeout` to eliminate database concurrency lockouts.

### 2. Test Coverage Mapping
```
CODE PATHS                                            USER FLOWS
[+] core/src/execution/tasks                          [+] Multi-Agent Execution
  ├── SubWorkflow.ts                                    ├── [★★★ TESTED] Sub-workflow completion — execution.test.ts:89
  │   ├── [★★★ TESTED] happy path + failure             ├── [★★★ TESTED] Failure propagation — execution.test.ts:121
  │   └── [GAP]         Cascade cancellation on parent  └── [GAP]        Nested dynamic fork-join depth/deadlock check
  ├── Fork.ts / Join.ts                               [+] Budget and Limits
  │   └── [★★★ TESTED] Parallel forks — decider-parity  ├── [GAP] [→E2E] Budget depletion execution halt
  └── LlmChatComplete.ts                                └── [GAP] [→EVAL] Model output schema check
      ├── [★★★ TESTED] Routed completion happy path
      └── [GAP]         Tracing span emission
```
*Legend: ★★★ behavior + edge + error | ★★ happy path | ★ smoke check | [→E2E] = integration test | [→EVAL] = LLM eval*

