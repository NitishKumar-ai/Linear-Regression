# Test Plan: Phase A (Proving the Ingestion Moat)

## Test Diagram: Codepaths & Coverage

### 1. Ingestion Endpoint (`api/main.py`)
- **Happy Path:** Valid messy data (text/audio) -> Returns B-schema extraction
- **Validation Path:** Over-sized file -> Returns 413 Payload Too Large
- **Auth Path:** Unauthenticated user -> Returns 401 Unauthorized
- **Missing Audio Path:** Pure static or empty file -> Returns 200 with Empty Schema

### 2. ML Extraction Pipeline (`workers/vision_tasks.py`)
- **LLM Prompt Regression:** 5-10 messy data cases run against LLM-as-a-judge (Automated Eval Suite)
- **JSON Validation:** LLM hallucinated JSON -> Pydantic Validation Error -> Dead Letter Queue
- **Injection Attack:** Payload says "Ignore all previous instructions" -> Empty Schema or Sanitized output

### 3. Entity Resolution
- **Semantic Match:** "Jon Doe" and "John Doe" match probabilistically -> Same entity linked

## Required Eval Suites
- **Messy Data Ground Truth Eval:** 10 real-world examples with a known B-schema set. Run on every LLM prompt change.
- **LLM-as-a-judge:** To rate entity resolution confidence.
