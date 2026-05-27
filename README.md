# GovPrepAI - Smart Government Exam Prep Agent

GovPrepAI is an AI-powered exam preparation system for Indian competitive exam students. It uses a FastAPI backend, a Streamlit frontend, LangGraph-based multi-agent orchestration, Groq-hosted LLMs, DuckDuckGo web search, ChromaDB vector storage, HuggingFace embeddings, and PDF note ingestion to create preparation plans, syllabus maps, mock tests, weak-topic revision material, and current-affairs guidance.

The project is built as a practical prototype for an exam-preparation startup product. It is designed to help users ask preparation questions, upload their own notes, get source-grounded guidance, and receive structured study outputs instead of one generic LLM response.

## Supported Exams

This project intentionally supports only these exam tracks:

| Exam track | Scope |
| --- | --- |
| `SSC` | SSC CGL and related SSC-style preparation workflows. |
| `Banking` | IBPS, SBI, RBI, and banking awareness style workflows. |
| `GATE CS/IT` | GATE Computer Science / Information Technology paper only. |
| `GATE DA` | GATE Data Science and Artificial Intelligence paper only. |
| `RRB` | Railway Recruitment Board preparation workflows. |

Generic GATE support is not enabled. The application accepts only `GATE CS/IT` and `GATE DA` so it does not accidentally answer for unsupported GATE papers.

## What This Project Does

GovPrepAI provides five main preparation capabilities:

1. Full plan-and-execute preparation workflow.
2. Official-syllabus and topic-weightage guidance.
3. Mock-test generation.
4. Target-date study-plan generation.
5. Uploaded-notes retrieval using RAG.

The full workflow takes a user goal such as:

```text
Create a 6-month SSC preparation plan with syllabus, topic weightage, resources, and mock schedule.
```

Then it:

1. Retrieves relevant uploaded notes for the user.
2. Sends the goal and exam type to a LangGraph pipeline.
3. Uses an LLM planner to decide which specialist agents should run.
4. Executes the selected specialist agents.
5. Passes earlier agent results into later agent calls.
6. Optionally replans once if early results suggest a better path.
7. Synthesizes everything into one final markdown study plan.

## Main Features

- FastAPI backend with Swagger docs at `/docs`.
- Streamlit frontend for non-technical users.
- LangGraph planner, executor, replanner, and synthesizer workflow.
- Six specialist preparation agents:
  - `syllabus_navigator`
  - `question_bank_agent`
  - `current_affairs_agent`
  - `mock_test_agent`
  - `weak_topic_agent`
  - `study_plan_agent`
- Source-grounded web search with titles, URLs, and snippets.
- India-region search defaults through DuckDuckGo.
- Accuracy rules that tell the model to cite URLs and avoid unsupported claims.
- SSC and Banking curated knowledge pack.
- PDF notes upload and retrieval through ChromaDB.
- HuggingFace sentence-transformer embeddings.
- Docker support for backend deployment.
- `.gitignore` and `.dockerignore` configured for safe GitHub publishing.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend API | FastAPI |
| ASGI server | Uvicorn |
| Frontend | Streamlit |
| Workflow engine | LangGraph |
| LLM orchestration | LangChain |
| LLM provider | Groq through `langchain-groq` |
| Search | `duckduckgo-search` |
| Vector database | ChromaDB |
| Embeddings | HuggingFace sentence-transformer embeddings |
| PDF parsing | PyMuPDF |
| Config | `python-dotenv` |
| Dependency management | `requirements.txt`, `uv.lock`, `pyproject.toml` |
| Containerization | Docker |

## Architecture

```text
User
  |
  +--> Streamlit frontend
  |       |
  |       v
  +--> FastAPI backend
          |
          +--> /api/upload-notes
          |       |
          |       v
          |   PyMuPDF -> text chunks -> embeddings -> ChromaDB
          |
          +--> /api/prepare
          |       |
          |       v
          |   retrieve user notes context
          |       |
          |       v
          |   GovPrepPipeline
          |       |
          |       +--> planner
          |       +--> executor
          |       +--> optional replanner
          |       +--> synthesizer
          |       |
          |       v
          |   final markdown answer
          |
          +--> /api/syllabus
          +--> /api/mock-test
          +--> /api/study-plan
```

## LangGraph Workflow

The workflow lives in `app/stategraph/`.

| File | Responsibility |
| --- | --- |
| `pipeline.py` | Builds and compiles the LangGraph state graph. |
| `nodes.py` | Implements planner, executor, replanner, synthesizer, and routing logic. |
| `schemas.py` | Defines workflow state and step structures with `TypedDict`. |
| `json_parser.py` | Safely parses JSON arrays from LLM output. |

### Workflow State

The workflow state contains:

| Field | Meaning |
| --- | --- |
| `user_goal` | User's preparation request or doubt. |
| `user_id` | User identifier used for note retrieval. |
| `exam_type` | One of `SSC`, `Banking`, `GATE CS/IT`, `GATE DA`, `RRB`. |
| `plan` | List of planned agent steps. |
| `current_step_index` | Which plan step is being executed. |
| `completed_results` | Results already produced by specialist agents. |
| `final_output` | Final synthesized markdown answer. |
| `replan_count` | Number of replanning cycles used. |
| `error` | Last recoverable workflow error, if any. |
| `notes_context` | Optional retrieved note context. |

### Planner

The planner reads the user goal and exam type, then asks the LLM to return a JSON array of steps. Each step contains:

```json
{
  "step_id": 1,
  "agent": "syllabus_navigator",
  "instruction": "Map the syllabus, topic weightage, and priorities."
}
```

The planner is limited to a maximum of four steps.

### Executor

The executor runs the selected specialist agent. It also passes a compact summary of previous step results into the next agent, so later agents can build on earlier outputs.

### Replanner

After two successful agent steps, the replanner can run once. It can keep, remove, or modify the remaining steps based on what has already been learned.

### Synthesizer

The synthesizer combines all agent results into one final markdown answer. It is instructed to include exactly five next steps for today.

## Specialist Agents

Specialist agents live in `app/agents/runners.py`.

| Agent | What it does |
| --- | --- |
| `syllabus_navigator` | Finds and structures syllabus, topics, subtopics, weightage, priority, and official-source caveats. |
| `question_bank_agent` | Studies previous-year patterns and creates practice questions. |
| `current_affairs_agent` | Searches and filters current affairs relevant to the selected exam. |
| `mock_test_agent` | Creates a 20-question mock test with options, answers, explanations, and topic tags. |
| `weak_topic_agent` | Creates focused revision notes for weak or low-coverage topics. |
| `study_plan_agent` | Creates realistic study schedules with revision cycles, PYQ practice, and mock-test planning. |

All LLM calls use async `ainvoke`.

## Accuracy Design

GovPrepAI is designed to reduce hallucination, but it cannot guarantee perfect answers. Accuracy is improved through four layers:

1. Curated SSC and Banking knowledge.
2. URL-based web search evidence.
3. Uploaded-notes retrieval.
4. Strict system prompts.

The prompt-level accuracy rules tell the model to:

- Treat search evidence and uploaded notes as grounding context.
- Prefer official sources, exam bodies, government domains, notifications, and PDFs.
- Cite URLs when using search evidence.
- Avoid inventing dates, cutoffs, notification numbers, eligibility rules, or official claims.
- Say when evidence is weak or unavailable.
- Separate confirmed facts from recommendations.

## Search Behavior

Search runs through `duckduckgo-search`.

The system uses structured search results:

```text
[1] Result title
URL: https://example.com
Snippet: Result snippet
```

For official exam searches, the app searches multiple query forms:

- official notification / syllabus / PDF query
- `site:gov.in` query
- `site:nic.in` query
- latest pattern and weightage query

Default search config:

| Variable | Default |
| --- | --- |
| `SEARCH_REGION` | `in-en` |
| `SEARCH_MAX_RESULTS` | `5` |

DuckDuckGo is suitable for a free prototype. It is not a guaranteed production search API. For a serious production system, add a search-provider abstraction and consider Brave Search API, Tavily, Google Programmable Search, or OpenAI web search when budget is available.

## Curated Knowledge Pack

The curated knowledge pack lives in:

```text
app/core/exam_knowledge.py
```

It currently provides offline grounding for SSC and Banking. It includes:

- SSC CGL and Banking topic weightages.
- Quantitative Aptitude topics.
- Reasoning topics.
- English Language topics.
- General Awareness topics.
- Subtopic examples for Number System, Data Interpretation, and Banking Awareness.
- A 26-week preparation roadmap.
- Exam-level weightage maps for SSC CGL, IBPS PO, SBI PO, and RBI Grade B style patterns.
- Resource URLs for official sites, mocks, PYQ resources, notes, YouTube channels, and topic practice.

When the selected exam is `SSC` or `Banking`, this pack is inserted into the agent prompt. For `GATE CS/IT`, `GATE DA`, and `RRB`, the app relies on live search evidence, uploaded notes, and official-source caveats unless you add more curated knowledge.

## RAG and Uploaded Notes

The RAG service lives in:

```text
app/services/rag.py
```

It works like this:

1. User uploads a PDF through `/api/upload-notes`.
2. PyMuPDF extracts page text.
3. Text is split into chunks using `RecursiveCharacterTextSplitter`.
4. HuggingFace embeddings are generated.
5. Chunks are stored in ChromaDB under a per-user collection.
6. Later `/api/prepare` calls retrieve relevant chunks using similarity search.
7. Retrieved note context is appended to the user goal before the LangGraph workflow runs.

Default chunk settings:

| Setting | Value |
| --- | --- |
| `chunk_size` | `500` |
| `chunk_overlap` | `100` |
| retrieval `k` | `6` |

Default ChromaDB directory:

```text
./chroma_db
```

This directory is ignored by Git.

## Backend API

The API routes are registered in:

```text
app/api/routes.py
```

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Health check. |
| `POST` | `/api/upload-notes?user_id=default` | Upload and index PDF notes for a user. |
| `POST` | `/api/prepare` | Run the full LangGraph plan-and-execute workflow. |
| `POST` | `/api/syllabus` | Run only the syllabus navigator. |
| `POST` | `/api/mock-test` | Run only the mock-test generator. |
| `POST` | `/api/study-plan` | Run only the study-plan generator. |

## API Request Schemas

Schemas live in:

```text
app/schemas.py
```

Allowed exam types:

```python
Literal["SSC", "Banking", "GATE CS/IT", "GATE DA", "RRB"]
```

### `/api/prepare`

```json
{
  "goal": "Create a 6-month SSC preparation plan with syllabus, resources, topic weightage, and mock schedule.",
  "exam_type": "SSC",
  "user_id": "default"
}
```

Response includes the full workflow state, including `plan`, `completed_results`, `final_output`, and `error`.

### `/api/syllabus`

```json
{
  "exam_type": "RRB"
}
```

### `/api/mock-test`

```json
{
  "exam_type": "GATE CS/IT",
  "topic": "Operating Systems"
}
```

### `/api/study-plan`

```json
{
  "exam_type": "Banking",
  "target_date": "2026-12-31",
  "weak_topics": ["Percentage", "Current Affairs"]
}
```

### `/api/upload-notes`

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/upload-notes?user_id=default" `
  -F "file=@notes.pdf"
```

Response:

```json
{
  "user_id": "default",
  "chunk_count": 42
}
```

## Streamlit Frontend

The frontend lives in:

```text
app/ui/streamlit_app.py
```

It provides five tabs:

| Tab | Purpose |
| --- | --- |
| Plan Agent | Runs `/api/prepare`. |
| Syllabus | Runs `/api/syllabus`. |
| Mock Test | Runs `/api/mock-test`. |
| Study Plan | Runs `/api/study-plan`. |
| Notes | Uploads PDFs through `/api/upload-notes`. |

The sidebar lets the user choose:

- `user_id`
- `exam_type`

The frontend expects the backend at:

```text
http://localhost:8000
```

## Configuration

Settings are loaded in:

```text
app/core/config.py
```

Create `.env` from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Required:

| Variable | Description |
| --- | --- |
| `GROQ_API_KEY` | Groq API key used by LLM endpoints. |

Optional:

| Variable | Default | Description |
| --- | --- | --- |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq chat model. |
| `APP_ENV` | `development` | Environment label. |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB persistence path. |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model. |
| `LLM_TEMPERATURE` | `0.2` | LLM creativity level. Lower is more deterministic. |
| `SEARCH_REGION` | `in-en` | DuckDuckGo search region. |
| `SEARCH_MAX_RESULTS` | `5` | Search results requested per query. |
| `APP_RELOAD` | unset | Enables reload only when running `python app/main.py`. |

Example:

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

Never commit `.env`.

## Local Setup

Install `uv` on Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Create and activate a virtual environment:

```powershell
uv venv .venv --python 3.11
.venv\Scripts\activate
```

Install dependencies:

```powershell
uv pip install -r requirements.txt
```

Verify the backend imports:

```powershell
python -c "from app.main import app; print(app.title)"
```

Expected output:

```text
GovPrepAI
```

## Run the Backend

Normal run:

```powershell
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open docs:

```text
http://localhost:8000/docs
```

Health check:

```powershell
curl.exe http://127.0.0.1:8000/
```

Expected response:

```json
{"status":"ok","service":"GovPrepAI"}
```

### Autoreload on Windows

Avoid plain `--reload` because it can watch `.venv` and trigger noisy reload traces. If needed, scope reload to the app directory:

```powershell
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

If running with `python app/main.py`, reload is disabled by default. To enable it:

```powershell
$env:APP_RELOAD="true"
python app/main.py
```

## Run the Frontend

Start the backend first, then run:

```powershell
uv run streamlit run app/ui/streamlit_app.py
```

## Docker

Build:

```powershell
docker build -t govprepai .
```

Run:

```powershell
docker run --rm -p 8000:8000 --env-file .env govprepai
```

Open:

```text
http://localhost:8000/docs
```

## Project Files Explained

| File | Explanation |
| --- | --- |
| `app/main.py` | Creates the FastAPI app, adds CORS, registers API routes, and optionally runs Uvicorn. |
| `app/schemas.py` | Defines API request and response models with Pydantic. |
| `app/api/routes.py` | Maps HTTP endpoints to pipeline, direct agents, and RAG service calls. |
| `app/agents/llm.py` | Creates the Groq `ChatGroq` client and validates `GROQ_API_KEY`. |
| `app/agents/prompts.py` | Stores system prompts and accuracy grounding rules. |
| `app/agents/runners.py` | Runs DuckDuckGo search, formats evidence, and calls specialist agents. |
| `app/agents/agent_runners.py` | Compatibility exports for standalone runner functions. |
| `app/core/config.py` | Loads `.env` settings and caches them. |
| `app/core/exam_knowledge.py` | Stores curated SSC and Banking knowledge, resources, roadmaps, and weightages. |
| `app/services/rag.py` | Handles PDF text extraction, chunking, embeddings, ChromaDB storage, and retrieval. |
| `app/stategraph/pipeline.py` | Builds the LangGraph graph. |
| `app/stategraph/nodes.py` | Implements planner, executor, replanner, synthesizer, and conditional routing. |
| `app/stategraph/json_parser.py` | Parses LLM JSON arrays and tolerates markdown fences. |
| `app/stategraph/schemas.py` | Defines graph state and step types. |
| `app/ui/streamlit_app.py` | Provides the browser UI. |
| `requirements.txt` | Python dependency pins. |
| `pyproject.toml` | Project metadata and tool settings. |
| `uv.lock` | Lockfile generated by `uv`. |
| `Dockerfile` | Container instructions for backend deployment. |
| `.env.example` | Safe template for local environment variables. |
| `.gitignore` | Prevents committing secrets, virtualenvs, caches, vector DB data, and local artifacts. |
| `.dockerignore` | Keeps unnecessary files out of Docker images. |

## Data and Storage

Local generated data:

| Path | Purpose | Git behavior |
| --- | --- | --- |
| `.env` | Local secrets and config | Ignored |
| `.venv/` | Python virtual environment | Ignored |
| `chroma_db/` | Local vector database | Ignored |
| `__pycache__/` | Python bytecode cache | Ignored |
| `.pytest_cache/` | Pytest cache | Ignored |
| `.ruff_cache/` | Ruff cache | Ignored |
| `logs/` | Local logs | Ignored |

## Production Notes

This project can be deployed for a demo or pilot, but production at large scale needs more work.

Recommended before production:

- Add authentication.
- Add per-user rate limits.
- Add request logging and monitoring.
- Add answer-quality evaluation.
- Add source-ranking and official-source preference.
- Add persistent hosted ChromaDB or another managed vector database.
- Add database-backed user accounts and note metadata.
- Add background jobs for long PDF ingestion.
- Add retry and timeout policies around LLM and search calls.
- Add tests for routes, parser behavior, RAG collection naming, and workflow routing.
- Add a paid or reliable search API if the product becomes public.

## Free Deployment Reality

Free hosting and free LLM/search tiers are useful for demos and small pilots. They are not enough for all users in India because free tiers usually limit:

- request count
- bandwidth
- uptime
- CPU and memory
- storage
- model usage
- search calls
- abuse protection

Use free infrastructure to validate demand. Move to paid infrastructure when real users depend on the product.

## Development Checks

Compile all Python files:

```powershell
python -m compileall app
```

Run tests if tests are added:

```powershell
python -m pytest
```

Run Ruff if installed:

```powershell
python -m ruff check app
```

## Troubleshooting

### `GROQ_API_KEY is not configured`

Create `.env` from `.env.example` and set `GROQ_API_KEY`.

### Uvicorn reload watches `.venv`

Stop the server and restart without reload:

```powershell
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

If reload is required:

```powershell
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

### Search returns `Search unavailable`

The app catches DuckDuckGo failures and continues with uncertainty. Check network access or retry later.

### Notes are not affecting answers

Confirm that:

- The PDF contains extractable text, not only scanned images.
- `/api/upload-notes` returned a non-zero `chunk_count`.
- The same `user_id` is used in `/api/upload-notes` and `/api/prepare`.
- `CHROMA_PERSIST_DIR` points to the same local directory across runs.

### ChromaDB data should not be pushed

`chroma_db/` is ignored by Git because it is local generated vector data.

## GitHub Push Guide

Check current status:

```powershell
git status
```

Stage changes:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Update README with complete project documentation"
```

Push:

```powershell
git push origin main
```

## Recommended Future Improvements

- Add curated knowledge for `GATE CS/IT`, `GATE DA`, and `RRB`.
- Add official syllabus PDF ingestion for each supported exam.
- Add a dedicated search provider interface.
- Add answer citation post-processing.
- Add unit tests and integration tests.
- Add user authentication.
- Add cloud storage for uploaded notes.
- Add admin dashboard for monitoring.
- Add multilingual output for Indian language users.
- Add exam-date-aware planning.

## License

This project is configured as MIT in `pyproject.toml`. Add a `LICENSE` file before publishing if you want GitHub to display the license clearly.
