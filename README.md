# GovPrepAI: Smart Government Exam Prep Agent

GovPrepAI is a Python AI application for Indian government exam preparation. It combines:

- FastAPI backend APIs
- Streamlit browser UI
- LangGraph plan-and-execute workflow
- Groq-hosted chat LLM through LangChain
- DuckDuckGo web search evidence
- ChromaDB vector storage for uploaded PDF notes
- HuggingFace sentence-transformer embeddings
- A curated SSC and Banking preparation knowledge pack

The project is built to answer preparation goals such as syllabus planning, topic weightage, practice generation, current-affairs guidance, mock tests, weak-topic revision, and study schedules.

## What I Checked

Project-authored files and folders checked:

- `README.md`
- `pyproject.toml`
- `requirements.txt`
- `uv.lock`
- `Dockerfile`
- `.env.example`
- `.env` key names only, without exposing secret values
- `.gitignore`
- `.dockerignore`
- `app/__init__.py`
- `app/main.py`
- `app/schemas.py`
- `app/api/__init__.py`
- `app/api/routes.py`
- `app/agents/__init__.py`
- `app/agents/agent_runners.py`
- `app/agents/llm.py`
- `app/agents/prompts.py`
- `app/agents/runners.py`
- `app/core/__init__.py`
- `app/core/config.py`
- `app/core/exam_types.py`
- `app/core/exam_knowledge.py`
- `app/services/__init__.py`
- `app/services/rag.py`
- `app/stategraph/__init__.py`
- `app/stategraph/json_parser.py`
- `app/stategraph/nodes.py`
- `app/stategraph/pipeline.py`
- `app/stategraph/schemas.py`
- `app/ui/__init__.py`
- `app/ui/streamlit_app.py`

Runtime/generated folders also present:

- `.git/` stores repository metadata.
- `.venv/` stores installed Python packages and command-line scripts.
- `__pycache__/` folders store compiled Python bytecode.
- `.pytest_cache/` stores pytest cache data.
- `chroma_db/` stores local ChromaDB vector database files.

These generated folders are not where project behavior is implemented. They are ignored or treated as runtime artifacts.

## High-Level Purpose

The application accepts a user's exam preparation request and returns structured study guidance. Depending on the endpoint used, it can:

- Run a full multi-agent preparation workflow.
- Return syllabus, topic, subtopic, weightage, and priority guidance.
- Generate a mock test.
- Build a target-date study plan.
- Upload and index PDF notes.
- Retrieve uploaded notes during a future preparation request.

The main target exams are:

- `SSC`
- `Banking`
- `GATE CS/IT`
- `GATE DA`
- `RRB`

Generic `GATE` is intentionally not a supported canonical exam type. It must resolve to either `GATE CS/IT` or `GATE DA`.

## Main Runtime Flow

The full workflow is available at `POST /api/prepare`.

Flow:

1. User sends a goal, exam type, and user ID.
2. API normalizes and may resolve the exam type from the goal text.
3. API retrieves relevant uploaded-note chunks for that user from ChromaDB.
4. If note context exists, the API appends it to the user goal.
5. `GovPrepPipeline` starts the LangGraph workflow.
6. Planner creates a JSON execution plan of up to 4 steps.
7. Executor runs the selected specialist agent for each step.
8. After 2 successful steps, replanner can run once if steps remain.
9. Executor continues on the revised or original plan.
10. Synthesizer combines all agent outputs into final markdown.
11. API returns the full workflow state and metadata.

## Application Entry Point

File: `app/main.py`

This file creates the FastAPI app.

It configures:

- App title: `GovPrepAI`
- Description: `Smart Government Exam Preparation Multi-Agent System`
- Version: `1.0.0`
- CORS with all origins and methods allowed
- Routes from `GovPrepApi`

When run directly with `python app/main.py`, it starts Uvicorn on:

- Host: `0.0.0.0`
- Port: `8000`

Reload is disabled by default. It is enabled only when `APP_RELOAD` is set to `1`, `true`, or `yes`. If enabled, reload watches only the `app` directory.

## Backend API Routes

File: `app/api/routes.py`

The `GovPrepApi` class registers all HTTP routes.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Health check |
| `POST` | `/api/upload-notes` | Upload and index PDF notes for a user |
| `POST` | `/api/prepare` | Run the full plan-execute-replan-synthesize workflow |
| `POST` | `/api/syllabus` | Run only the syllabus navigator agent |
| `POST` | `/api/mock-test` | Run only the mock-test agent |
| `POST` | `/api/study-plan` | Run only the study-plan agent |

### Health Check

Input: none.

Output:

```json
{
  "status": "ok",
  "service": "GovPrepAI"
}
```

### Upload Notes

Endpoint:

```text
POST /api/upload-notes?user_id=default
```

Input:

- Multipart file field named `file`
- Expected file type is PDF
- Optional query parameter `user_id`, default `default`

Internal behavior:

1. Reads uploaded PDF bytes.
2. Runs ingestion in a worker thread with `asyncio.to_thread`.
3. Extracts text with PyMuPDF.
4. Splits text into chunks.
5. Stores embeddings in ChromaDB under a per-user collection.

Output:

```json
{
  "user_id": "default",
  "chunk_count": 42
}
```

### Prepare

Endpoint:

```text
POST /api/prepare
```

Input:

```json
{
  "goal": "Create a 6-month SSC preparation plan with syllabus, resources, topic weightage, and mock schedule.",
  "exam_type": "SSC",
  "user_id": "default"
}
```

Input rules:

- `goal` must be at least 3 characters.
- `exam_type` must normalize to one supported exam.
- `user_id` defaults to `default`.

Internal behavior:

1. Calls `resolve_exam_type(request.exam_type, request.goal)`.
2. Retrieves notes with `retrieve_notes_context(goal, user_id, 6)`.
3. Appends retrieved notes to the goal if found.
4. Runs `GovPrepPipeline.run(goal, exam_type, user_id)`.
5. Adds response metadata:
   - `requested_exam_type`
   - `resolved_exam_type`
   - `exam_type_overridden`

Output:

The response is the LangGraph state plus exam-resolution metadata. It includes:

- `user_goal`
- `user_id`
- `exam_type`
- `plan`
- `current_step_index`
- `completed_results`
- `final_output`
- `replan_count`
- `error`
- `requested_exam_type`
- `resolved_exam_type`
- `exam_type_overridden`

### Syllabus

Endpoint:

```text
POST /api/syllabus
```

Input:

```json
{
  "exam_type": "RRB"
}
```

Internal instruction sent to the agent:

```text
Find the latest official syllabus, all topics, topic weightage, and priority ranking.
```

Output:

```json
{
  "exam_type": "RRB",
  "result": "markdown/text result from syllabus_navigator"
}
```

### Mock Test

Endpoint:

```text
POST /api/mock-test
```

Input:

```json
{
  "exam_type": "GATE CS/IT",
  "topic": "Operating Systems"
}
```

Internal instruction:

```text
Create a mock test focused on topic: Operating Systems
```

Output:

```json
{
  "exam_type": "GATE CS/IT",
  "topic": "Operating Systems",
  "result": "markdown/text mock test"
}
```

### Study Plan

Endpoint:

```text
POST /api/study-plan
```

Input:

```json
{
  "exam_type": "Banking",
  "target_date": "2026-12-31",
  "weak_topics": ["Percentage", "Current Affairs"]
}
```

Internal instruction:

```text
Create a study plan up to target date 2026-12-31. Weak topics: Percentage, Current Affairs. Include 10-month, 8-month, and 6-month options.
```

Output:

```json
{
  "exam_type": "Banking",
  "target_date": "2026-12-31",
  "result": "markdown/text study plan"
}
```

## API Schemas

File: `app/schemas.py`

Pydantic models:

- `ExamTypeModel`
- `GovPrepRequest`
- `ExamTypeRequest`
- `MockTestRequest`
- `StudyPlanRequest`
- `UploadNotesResponse`

All request models with `exam_type` use a validator that calls `normalize_exam_type`.

Validation details:

- `GovPrepRequest.goal`: required, minimum length 3.
- `GovPrepRequest.user_id`: default `default`.
- `MockTestRequest.topic`: required, minimum length 1.
- `StudyPlanRequest.target_date`: required, minimum length 4.
- `StudyPlanRequest.weak_topics`: defaults to empty list.

## Exam Type Handling

File: `app/core/exam_types.py`

Canonical supported exam values:

```python
("SSC", "Banking", "GATE CS/IT", "GATE DA", "RRB")
```

Alias examples:

- `ssc` -> `SSC`
- `bank`, `banking` -> `Banking`
- `gate cs`, `gate cse`, `gate computer science`, `gate it` -> `GATE CS/IT`
- `gate da`, `gate data science`, `gate ai`, `gate artificial intelligence` -> `GATE DA`
- `railway`, `railways`, `rrb` -> `RRB`

The application can infer exam type from the user goal. If the selected exam conflicts with an explicitly mentioned exam in the goal, the goal text wins.

Example:

```json
{
  "exam_type": "SSC",
  "goal": "Create a plan for SBI PO"
}
```

Resolved exam:

```text
Banking
```

The response marks this with:

```json
{
  "exam_type_overridden": true
}
```

## LangGraph Pipeline

Files:

- `app/stategraph/pipeline.py`
- `app/stategraph/nodes.py`
- `app/stategraph/schemas.py`
- `app/stategraph/json_parser.py`

The pipeline is implemented by `GovPrepPipeline`.

Graph nodes:

- `planner`
- `executor`
- `replanner`
- `synthesizer`

Graph edges:

```text
planner -> executor
executor -> executor
executor -> replanner
executor -> synthesizer
replanner -> executor
synthesizer -> END
```

The executor uses conditional routing through `should_continue_executing`.

## Workflow State

File: `app/stategraph/schemas.py`

`GovPrepState` contains:

| Field | Meaning |
| --- | --- |
| `user_goal` | The user request, possibly with appended uploaded-note context |
| `user_id` | User identity for note retrieval |
| `exam_type` | Canonical exam type |
| `plan` | List of executable planner steps |
| `current_step_index` | Index of the next step to execute |
| `completed_results` | Result objects from finished steps |
| `final_output` | Final synthesized answer |
| `replan_count` | Number of replanning cycles used |
| `error` | Last recoverable workflow error |
| `notes_context` | Optional field in schema, but current API appends notes into `user_goal` instead |

Each `Step` contains:

| Field | Meaning |
| --- | --- |
| `step_id` | Planner step number |
| `agent` | Agent name |
| `instruction` | Agent instruction |
| `status` | `pending`, `done`, or `failed` |
| `result` | Agent output or failure text |

## Planner

File: `app/stategraph/nodes.py`

Prompt source: `PLANNER_SYSTEM_PROMPT` in `app/agents/prompts.py`.

Planner behavior:

1. Receives `user_goal` and `exam_type`.
2. Calls the Groq LLM.
3. Expects a JSON array.
4. Parses the array using `LlmJsonParser`.
5. Normalizes and validates each step.
6. Keeps at most 4 steps.
7. Falls back to one `syllabus_navigator` step if parsing or LLM call fails.

Allowed planner agents:

- `syllabus_navigator`
- `question_bank_agent`
- `current_affairs_agent`
- `mock_test_agent`
- `weak_topic_agent`
- `study_plan_agent`

Planner rules:

- Maximum 4 steps.
- Use the exact exam type supplied by workflow state.
- Steps must be logically ordered.
- Put syllabus before question-bank if both are needed.
- Put current-affairs before mock-test if both are needed.
- Use study-plan for roadmap, timetable, resource allocation, and mock schedule requests.
- Use mock-test only when actual mock questions are requested.
- Return only JSON.

Example planner output:

```json
[
  {
    "step_id": 1,
    "agent": "syllabus_navigator",
    "instruction": "Map the syllabus, topic weightage, and priority order."
  },
  {
    "step_id": 2,
    "agent": "study_plan_agent",
    "instruction": "Create a 6-month roadmap with weekly revision and mocks."
  }
]
```

## Executor

File: `app/stategraph/nodes.py`

Executor behavior:

1. Reads the current step from `plan[current_step_index]`.
2. Looks up the agent function in `agent_registry`.
3. Adds prior execution context to the instruction.
4. Runs the selected async agent.
5. Marks the step `done` or `failed`.
6. Appends a result object to `completed_results`.
7. Increments `current_step_index`.

Prior context format:

```text
Step 1 (syllabus_navigator): first 400 characters of result
```

If there are no prior results:

```text
No prior results yet.
```

If an unknown agent appears, the step fails with:

```text
Unknown agent: agent_name
```

If the agent raises an exception, the result becomes:

```text
ExceptionType: exception message
```

## Replanner

File: `app/stategraph/nodes.py`

Prompt source: `REPLANNER_SYSTEM_PROMPT` in `app/agents/prompts.py`.

Replanner behavior:

1. Runs only after at least 2 successful completed steps.
2. Runs only if `replan_count == 0`.
3. Runs only if there are remaining plan steps.
4. Sends original goal, exam type, completed results, and remaining steps to the LLM.
5. Expects a JSON array of revised remaining steps.
6. Can keep, remove, or modify remaining steps.
7. Allows an empty revised plan.
8. Increments `replan_count`.

If replanning fails, the original remaining steps are kept and `error` is set to:

```text
Replanner kept original remaining steps: ...
```

Important: this project has bounded replanning. It does not replan repeatedly. Maximum replanning cycles: 1.

## Synthesizer

File: `app/stategraph/nodes.py`

Prompt source: `SYNTHESIZER_SYSTEM_PROMPT` in `app/agents/prompts.py`.

Synthesizer behavior:

1. Receives original goal, exam type, and all completed results.
2. Serializes them into a structured JSON summary.
3. Calls the Groq LLM.
4. Produces final markdown.
5. Must include exactly 5 next steps for today.

If synthesis fails, the project returns a fallback markdown answer with:

- A note that synthesis failed.
- Completed agent results in JSON.
- Exactly 5 default next steps.

## Conditional Routing

File: `app/stategraph/nodes.py`

After every executor call, `should_continue_executing` decides the next graph node.

Routing logic:

- If all plan steps have run, route to `synthesize`.
- If at least 2 successful steps are done, replanning has not happened, and steps remain, route to `replan`.
- Otherwise route back to `execute`.

This means a typical 4-step plan can look like:

```text
planner
executor step 1
executor step 2
replanner
executor remaining step 3
executor remaining step 4
synthesizer
END
```

## JSON Parsing for Plans

File: `app/stategraph/json_parser.py`

`LlmJsonParser` exists because LLMs may return JSON wrapped in markdown fences or with extra text.

It can handle:

- Plain JSON arrays.
- JSON arrays wrapped in ```json fences.
- Text that contains a JSON array somewhere inside.

It rejects non-array JSON.

It returns only dictionary items from the parsed array.

## Agents Used

File: `app/agents/runners.py`

All specialist agents are methods of `GovPrepAgentRunners`.

There are 6 agents:

| Agent | Function | Purpose |
| --- | --- | --- |
| `syllabus_navigator` | `run_syllabus_navigator` | Syllabus, topics, subtopics, weightage, priority, source caveats |
| `question_bank_agent` | `run_question_bank_agent` | Previous-year pattern analysis and practice questions |
| `current_affairs_agent` | `run_current_affairs_agent` | Exam-relevant current affairs with source URLs |
| `mock_test_agent` | `run_mock_test_agent` | 20-question mock test with options, answers, explanations, topic tags |
| `weak_topic_agent` | `run_weak_topic_agent` | Weak-topic revision notes, traps, mnemonics |
| `study_plan_agent` | `run_study_plan_agent` | Timetable, roadmap, subject rotation, revision, PYQs, mock schedule |

All LLM agent calls use async `ainvoke`.

## Agent Prompting

File: `app/agents/prompts.py`

Every specialist agent call includes:

- A role-specific system prompt.
- Shared accuracy grounding rules.
- User instruction.
- Exam type.
- Curated knowledge when available.
- Search evidence when that agent uses search.
- Prior execution context when run inside the LangGraph workflow.

Shared accuracy rules require the model to:

- Treat search evidence and uploaded notes as grounding context.
- Prefer official sources, exam bodies, government domains, notifications, and PDFs.
- Cite source URLs when using search evidence.
- Avoid inventing dates, cutoffs, notification numbers, eligibility rules, or official claims.
- Say what needs official verification if evidence is weak.
- Separate confirmed facts from recommendations.

## LLM Configuration

File: `app/agents/llm.py`

LLM client:

- Class: `ChatGroq`
- Provider package: `langchain-groq`
- Model comes from `GROQ_MODEL`.
- API key comes from `GROQ_API_KEY`.
- Temperature comes from `LLM_TEMPERATURE`, unless overridden.

If `GROQ_API_KEY` is missing, LLM endpoints raise:

```text
GROQ_API_KEY is not configured. Add it to .env before calling LLM endpoints.
```

Default model:

```text
llama-3.3-70b-versatile
```

Default temperature:

```text
0.2
```

## Search Behavior

File: `app/agents/runners.py`

Search provider:

- `duckduckgo-search`
- `DDGS`

The project sets:

```python
DDGS._impersonates = ("chrome_131",)
```

Search settings:

- Region from `SEARCH_REGION`, default `in-en`.
- Max results from `SEARCH_MAX_RESULTS`, default `5`.
- Safesearch: `moderate`.

Search result format passed to agents:

```text
[1] Result title
URL: https://example.com
Snippet: Search snippet
```

Duplicate URLs are removed.

At most 12 evidence results are formatted for the prompt.

If search fails:

```text
Search unavailable. Use general knowledge only with clear uncertainty.
```

If search returns no evidence:

```text
No search evidence found. Use general knowledge only with clear uncertainty.
```

### Official Exam Search

For syllabus and question-bank workflows, `official_exam_search` runs these query shapes:

- `{exam_type} {topic} official notification syllabus pdf`
- `{exam_type} {topic} site:gov.in`
- `{exam_type} {topic} site:nic.in`
- `{exam_type} {topic} latest exam pattern weightage`

This biases results toward official or higher-confidence sources, but it does not guarantee official-only evidence.

## Curated Knowledge Pack

File: `app/core/exam_knowledge.py`

Curated offline knowledge exists for:

- SSC-style preparation
- Banking, IBPS, SBI, RBI-style preparation

For unsupported curated exams such as `GATE CS/IT`, `GATE DA`, and `RRB`, the function returns:

```text
No curated offline syllabus pack is available for this exam type. Use live search evidence, uploaded notes, and official-source caveats.
```

The curated pack contains:

- Topic weightages for Quantitative Aptitude.
- Topic weightages for Reasoning.
- Topic weightages for English Language.
- Topic weightages for General Awareness.
- Subtopic examples for Number System.
- Subtopic examples for Data Interpretation.
- Subtopic examples for Banking Awareness.
- A 26-week roadmap.
- Exam-level weightage maps.
- Official, mock, PYQ, notes, YouTube, and topic resource URLs.

Exam-level weightage examples included:

- SSC CGL Tier-1
- SSC CGL Tier-2
- IBPS PO Prelims
- IBPS PO Mains
- SBI PO Prelims
- SBI PO Mains
- RBI Grade B Phase-1

Important caveat from the code: current official notification dates, vacancies, eligibility, fees, and final syllabus PDFs should be verified against official exam-body websites.

## RAG and Uploaded Notes

File: `app/services/rag.py`

The RAG service is `NotesRagService`.

Default chunking:

- `chunk_size = 500`
- `chunk_overlap = 100`

Default retrieval:

- `k = 6` chunks

Storage:

- ChromaDB
- Persist directory from `CHROMA_PERSIST_DIR`
- Default `./chroma_db`

Embeddings:

- Default model: `sentence-transformers/all-MiniLM-L6-v2`
- Loaded through `langchain_huggingface.HuggingFaceEmbeddings` when available.
- Falls back to `langchain_community.embeddings.HuggingFaceEmbeddings`.

PDF extraction:

- Uses PyMuPDF `fitz`.
- Opens PDF bytes from memory.
- Extracts text page by page.
- Skips blank pages.
- Stores page number in document metadata.

Collection naming:

- User-specific collection name is `notes_{safe_user_id}`.
- Unsafe characters are replaced with `_`.
- Collection name is trimmed to 63 characters.
- Minimum name fallback is `notes_default`.

Ingestion behavior:

1. Extract PDF text.
2. Split into chunks.
3. Create/open Chroma collection.
4. Attempt to delete the existing collection for the user.
5. If no chunks exist, return `0`.
6. Store new chunks with embeddings.
7. Persist if the vectorstore supports `persist`.
8. Return chunk count.

Important: uploading notes for the same user replaces that user's previous collection because `delete_collection()` is attempted before storing new chunks.

Retrieval behavior:

1. Opens Chroma collection for the user.
2. Runs similarity search.
3. Returns joined page contents.
4. If retrieval fails, returns an empty string.

Telemetry:

- Defines `NoOpChromaTelemetry`.
- Sets Chroma telemetry implementations to the no-op class.
- Sets `anonymized_telemetry=False`.

## How Notes Affect Answers

Uploaded notes are used only in `/api/prepare`.

They are not currently used by:

- `/api/syllabus`
- `/api/mock-test`
- `/api/study-plan`

For `/api/prepare`, the API retrieves notes before running the graph. If notes are found, it modifies the goal like this:

```text
Original user goal

Relevant uploaded notes context:
retrieved chunks...
```

The graph state has an optional `notes_context` field in the schema, but the current implementation does not set it separately. The notes are appended into `user_goal`.

## Scheduling and Study Planning

There is no background job scheduler, calendar scheduler, cron worker, or persistent schedule database in this project.

Scheduling means LLM-generated study schedules produced by `study_plan_agent`.

The study-plan prompt asks for:

- Daily hours.
- Subject rotation.
- Revision cycles.
- PYQ practice.
- Mock-test schedule.
- 10-month, 8-month, and 6-month roadmap options when relevant.
- For 6-month plans:
  - Month-wise phases.
  - Weekly topic allocation.
  - Revision slots.
  - Resource URLs from curated knowledge.
  - Topic weightage priorities.
  - Mock-analysis routine.

The direct `/api/study-plan` endpoint always asks the agent to include 10-month, 8-month, and 6-month options.

## Streamlit Frontend

File: `app/ui/streamlit_app.py`

The Streamlit UI talks to:

```text
http://localhost:8000
```

It defines:

- Page title: `GovPrepAI`
- Page icon: `GP`
- Layout: `wide`

Sidebar inputs:

- `User ID`, default `default`
- `Exam Type`, one of `SSC`, `Banking`, `GATE CS/IT`, `GATE DA`, `RRB`

Tabs:

| Tab | API Used | Purpose |
| --- | --- | --- |
| `Plan Agent` | `/api/prepare` | Full multi-agent workflow |
| `Syllabus` | `/api/syllabus` | Syllabus guidance |
| `Mock Test` | `/api/mock-test` | Topic-focused mock test |
| `Study Plan` | `/api/study-plan` | Target-date timetable |
| `Notes` | `/api/upload-notes` | Upload and index PDF notes |

Frontend error behavior:

- If API cannot be reached, it shows a Streamlit error and stops.
- If API returns non-2xx, it shows status code and response detail.
- Successful full workflow shows `final_output` and an expandable execution trace.

## Inputs and Outputs by User Workflow

### Full Plan Agent

User inputs:

- `user_id`
- `exam_type`
- free-text preparation goal

Output:

- Final markdown answer.
- Full execution trace in UI expander.
- API returns plan, completed results, final output, error status, and exam resolution metadata.

### Syllabus

User input:

- `exam_type`

Output:

- Markdown/text syllabus map with topics, subtopics, weights, priorities, URLs, and caveats.

### Mock Test

User inputs:

- `exam_type`
- `topic`

Output:

- 20-question mock test with:
  - question
  - 4 options
  - correct answer
  - explanation
  - topic tag

### Study Plan

User inputs:

- `exam_type`
- `target_date`
- comma-separated weak topics

Output:

- Study timetable and roadmap.
- Revision cycles.
- PYQ and mock-test planning.
- Weak-topic handling.

### Notes

User inputs:

- `user_id`
- PDF file

Output:

- Number of chunks indexed.

Later impact:

- Relevant chunks can be retrieved for `/api/prepare` requests with the same `user_id`.

## Configuration

File: `app/core/config.py`

Environment variables are loaded with `python-dotenv`.

Settings:

| Variable | Default | Required | Purpose |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | empty | Yes for LLM endpoints | Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | No | Chat model |
| `APP_ENV` | `development` | No | Environment label |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | No | Vector DB directory |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | No | Embedding model |
| `LLM_TEMPERATURE` | `0.2` | No | Chat model temperature |
| `SEARCH_REGION` | `in-en` | No | DuckDuckGo region |
| `SEARCH_MAX_RESULTS` | `5` | No | Results per search query |
| `APP_RELOAD` | unset | No | Enables direct-run Uvicorn reload |

`.env.example` includes:

```env
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
APP_ENV=development
CHROMA_PERSIST_DIR=./chroma_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_TEMPERATURE=0.2
SEARCH_REGION=in-en
SEARCH_MAX_RESULTS=5
```

The local `.env` file in this workspace contains these keys:

- `GROQ_API_KEY`
- `APP_ENV`
- `CHROMA_PERSIST_DIR`

Secret values are intentionally not documented here.

## Dependencies

File: `requirements.txt`

Pinned dependencies:

- `fastapi==0.115.0`
- `uvicorn==0.30.6`
- `python-multipart==0.0.9`
- `httpx==0.27.2`
- `pydantic==2.8.2`
- `langchain==0.3.0`
- `langchain-chroma==0.1.4`
- `langchain-community==0.3.0`
- `langchain-groq==0.2.0`
- `langchain-huggingface==0.1.0`
- `langchain-text-splitters==0.3.0`
- `langgraph==0.2.28`
- `chromadb==0.5.3`
- `sentence-transformers==3.0.1`
- `PyMuPDF==1.24.9`
- `duckduckgo-search==7.2.1`
- `streamlit==1.38.0`
- `python-dotenv==1.0.1`

## Project Metadata

File: `pyproject.toml`

Project:

- Name: `govprepai`
- Version: `1.0.0`
- Description: `Smart Government Exam Preparation Multi-Agent System`
- Python: `>=3.11`
- License: MIT text

Tool config:

- Pytest python path includes `.`
- Pytest asyncio mode is `auto`
- Ruff line length is `100`
- Ruff target version is `py311`
- Ruff lint rules: `E`, `F`, `I`, `UP`
- Mypy Python version is `3.11`
- Mypy warns on `Any` returns and unused config
- Mypy ignores missing imports

File: `uv.lock`

This lock file is minimal and declares:

- Lock version `1`
- Revision `1`
- Python `>=3.11`
- Virtual package `govprepai` version `1.0.0`

## Docker Behavior

File: `Dockerfile`

Docker image behavior:

1. Starts from `python:3.11-slim`.
2. Sets workdir to `/app`.
3. Installs `build-essential`.
4. Copies `requirements.txt`.
5. Installs Python dependencies with `pip`.
6. Copies project files.
7. Creates `chroma_db`.
8. Exposes port `8000`.
9. Runs:

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Build:

```powershell
docker build -t govprepai .
```

Run:

```powershell
docker run --rm -p 8000:8000 --env-file .env govprepai
```

## Ignore Files

`.gitignore` prevents committing:

- `.env` and secret files
- Virtual environments
- Python bytecode
- Build artifacts
- Tool caches
- Chroma/vector DB data
- SQLite and DB files
- Upload/temp folders
- Logs
- Streamlit secrets
- Jupyter checkpoints
- IDE and OS files
- Node artifacts if added later

`.dockerignore` keeps Docker context smaller and excludes:

- Git metadata
- Python caches
- Virtual environments
- Env files
- Tool caches
- Chroma DB
- Logs
- Upload/temp folders
- Streamlit secrets

## Runtime Data and Generated Files

Generated runtime paths:

| Path | Purpose |
| --- | --- |
| `.venv/` | Local Python virtual environment |
| `chroma_db/` | Local persisted ChromaDB data |
| `__pycache__/` | Python bytecode |
| `.pytest_cache/` | Test cache |
| `.git/` | Git repository internals |

These are not application source files.

## How to Run Locally

Create environment:

```powershell
uv venv .venv --python 3.11
.venv\Scripts\activate
```

Install dependencies:

```powershell
uv pip install -r requirements.txt
```

Create `.env`:

```powershell
Copy-Item .env.example .env
```

Set at least:

```env
GROQ_API_KEY=your_groq_key_here
```

Start backend:

```powershell
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open API docs:

```text
http://localhost:8000/docs
```

Start frontend:

```powershell
uv run streamlit run app/ui/streamlit_app.py
```

## Important Failure and Fallback Behavior

### Missing Groq Key

LLM calls fail with a clear runtime error.

Affected endpoints:

- `/api/prepare`
- `/api/syllabus`
- `/api/mock-test`
- `/api/study-plan`

### Planner Failure

The workflow falls back to one syllabus step.

### Replanner Failure

The original remaining plan is kept.

### Synthesizer Failure

The workflow returns fallback markdown with completed results and 5 default next steps.

### Search Failure

Agents continue, but prompt text says search is unavailable and general knowledge must be used with uncertainty.

### Empty or Scanned PDF

If PyMuPDF extracts no text, ingestion returns:

```json
{
  "chunk_count": 0
}
```

Scanned image PDFs need OCR support, which is not currently implemented.

## Accuracy Model

The project tries to reduce hallucination through:

- Curated SSC/Banking preparation knowledge.
- Live web search evidence.
- Uploaded-note retrieval.
- Strong prompt rules about official verification.
- Source URL requirements.
- Explicit uncertainty when evidence is weak.

However, the system still depends on LLM output and DuckDuckGo search quality. Official dates, vacancies, eligibility, fees, notification numbers, and final syllabus PDFs must be verified from official sources before serious use.

## What This Project Does Not Yet Have

Current missing production features:

- Authentication.
- User account database.
- Persistent metadata for uploaded notes.
- OCR for scanned PDFs.
- Background queue for long ingestion.
- Real calendar integration.
- Cron or reminder scheduler.
- Rate limits.
- Observability and tracing.
- Automated answer evaluation.
- Unit or integration tests in the repository.
- Hosted vector database setup.
- Search-provider abstraction.
- Official PDF ingestion pipeline per exam.
- Curated packs for `GATE CS/IT`, `GATE DA`, and `RRB`.

## File-by-File Summary

| File | Role |
| --- | --- |
| `app/main.py` | FastAPI app factory, CORS, route registration, direct Uvicorn entry |
| `app/schemas.py` | Pydantic API request and response models |
| `app/api/routes.py` | Backend endpoints for health, notes, workflow, syllabus, mock test, study plan |
| `app/agents/llm.py` | Groq `ChatGroq` client factory |
| `app/agents/prompts.py` | Planner, replanner, synthesizer, agent, and accuracy prompts |
| `app/agents/runners.py` | Specialist agents, search, curated-knowledge insertion, LLM calls |
| `app/agents/agent_runners.py` | Backward-compatible exports |
| `app/core/config.py` | Environment settings loader and cache |
| `app/core/exam_types.py` | Supported exam aliases, normalization, inference, conflict resolution |
| `app/core/exam_knowledge.py` | Curated SSC/Banking weights, roadmap, resources |
| `app/services/rag.py` | PDF extraction, chunking, embeddings, Chroma storage and retrieval |
| `app/stategraph/schemas.py` | TypedDict graph state and step schema |
| `app/stategraph/json_parser.py` | Tolerant parser for LLM JSON arrays |
| `app/stategraph/nodes.py` | Planner, executor, replanner, synthesizer, router |
| `app/stategraph/pipeline.py` | LangGraph construction and async run entry |
| `app/ui/streamlit_app.py` | Streamlit UI client |
| `requirements.txt` | Python dependency pins |
| `pyproject.toml` | Project metadata and tool configuration |
| `uv.lock` | Minimal uv lock data |
| `Dockerfile` | Backend container build and run definition |
| `.env.example` | Safe environment template |
| `.gitignore` | Git ignore rules |
| `.dockerignore` | Docker build context ignore rules |

## End-to-End Example

1. User uploads PDF notes in the Streamlit `Notes` tab.
2. Backend indexes notes into `chroma_db` under `notes_default`.
3. User opens `Plan Agent`.
4. User selects `SSC`.
5. User asks:

```text
Create a complete 6-month SSC CGL roadmap with syllabus, topic weightage, resources, PYQ practice, weak-topic revision, and mock schedule.
```

6. API retrieves notes for `default`.
7. Planner might choose:

```json
[
  {
    "step_id": 1,
    "agent": "syllabus_navigator",
    "instruction": "Map SSC CGL syllabus, topic weightage, and priority order."
  },
  {
    "step_id": 2,
    "agent": "question_bank_agent",
    "instruction": "Analyze PYQ patterns and generate practice questions."
  },
  {
    "step_id": 3,
    "agent": "weak_topic_agent",
    "instruction": "Identify weak or low-coverage topics from context and create revision material."
  },
  {
    "step_id": 4,
    "agent": "study_plan_agent",
    "instruction": "Create a 6-month timetable with resources, revision, PYQs, and mock schedule."
  }
]
```

8. Executor runs step 1.
9. Executor runs step 2.
10. Replanner may revise remaining steps.
11. Executor runs remaining steps.
12. Synthesizer returns one final markdown answer with exactly 5 next steps for today.

## Bottom Line

This project is a working prototype of a multi-agent government exam preparation assistant. The core product behavior is concentrated in:

- `app/api/routes.py`
- `app/stategraph/nodes.py`
- `app/stategraph/pipeline.py`
- `app/agents/runners.py`
- `app/services/rag.py`
- `app/core/exam_knowledge.py`
- `app/ui/streamlit_app.py`

The system plans with an LLM, executes specialist exam-prep agents, optionally replans once, and synthesizes a final markdown study answer. Uploaded PDF notes can ground full workflow answers through ChromaDB retrieval. Study schedules are generated as text plans by the study-plan agent; there is no separate calendar or background scheduling engine.
