# GovPrepAI - Smart Government Exam Prep Agent

GovPrepAI is a multi-agent exam preparation assistant for government and competitive exams. It combines FastAPI, LangGraph, Groq LLMs, DuckDuckGo search, ChromaDB, HuggingFace embeddings, PDF note ingestion, and a Streamlit UI to generate exam-specific study plans, syllabus maps, mock tests, current-affairs guidance, and revision support.

Supported exam tracks:

- SSC
- Banking
- GATE
- RRB

## Features

- Multi-agent plan-and-execute workflow powered by LangGraph.
- Source-grounded responses with URL-based search evidence.
- India-region search defaults for exam preparation queries.
- Syllabus navigator for exam topics, subtopics, priority, and weightage.
- Question bank agent for previous-year-style practice questions.
- Current affairs agent for exam-relevant recent topics.
- Mock test generator with options, answers, explanations, and topic tags.
- Weak-topic revision agent for targeted notes and common traps.
- Study plan agent for realistic schedules, revision cycles, and mock-test cadence.
- PDF notes upload with ChromaDB-backed retrieval augmented generation.
- FastAPI backend with interactive Swagger docs.
- Streamlit frontend for non-technical users.
- Docker support for backend deployment.

## Tech Stack

| Layer | Tools |
| --- | --- |
| Backend API | FastAPI, Uvicorn |
| Agent workflow | LangGraph, LangChain |
| LLM provider | Groq via `langchain-groq` |
| Search | DuckDuckGo Search |
| RAG | ChromaDB, HuggingFace sentence-transformer embeddings |
| PDF parsing | PyMuPDF |
| Frontend | Streamlit |
| Config | `python-dotenv` |
| Packaging | `requirements.txt`, `pyproject.toml`, `uv.lock` |
| Container | Docker |

## Architecture

```text
User
  |
  | FastAPI / Streamlit
  v
GovPrepPipeline
  |
  v
Planner LLM
  |
  v
Executor
  |
  +--> syllabus_navigator
  +--> question_bank_agent
  +--> current_affairs_agent
  +--> mock_test_agent
  +--> weak_topic_agent
  +--> study_plan_agent
  |
  v
Optional Replanner
  |
  v
Synthesizer
  |
  v
Final markdown preparation plan
```

The planner creates up to four execution steps. The executor runs the selected specialist agent for each step and passes prior results forward as context. After two successful steps, the replanner can revise the remaining steps once. The synthesizer turns all completed agent outputs into one final markdown action plan.

## Project Structure

```text
.
|-- app/
|   |-- main.py                 FastAPI app factory and local server entrypoint
|   |-- schemas.py              API request and response schemas
|   |-- api/
|   |   |-- routes.py           Backend HTTP endpoints
|   |-- agents/
|   |   |-- llm.py              Groq ChatGroq client factory
|   |   |-- prompts.py          Planner, replanner, synthesizer, and agent prompts
|   |   |-- runners.py          Specialist agent implementations
|   |   |-- agent_runners.py    Compatibility exports
|   |-- core/
|   |   |-- config.py           Environment-backed settings
|   |-- services/
|   |   |-- rag.py              PDF extraction, chunking, embeddings, and ChromaDB retrieval
|   |-- stategraph/
|   |   |-- json_parser.py      Safe parser for LLM JSON output
|   |   |-- nodes.py            LangGraph planner/executor/replanner/synthesizer nodes
|   |   |-- pipeline.py         LangGraph workflow builder
|   |   |-- schemas.py          Workflow TypedDict state definitions
|   |-- ui/
|       |-- streamlit_app.py    Streamlit frontend
|-- Dockerfile
|-- requirements.txt
|-- pyproject.toml
|-- uv.lock
|-- .env.example
|-- .gitignore
|-- .dockerignore
```

## Prerequisites

- Python 3.11 or newer.
- A Groq API key.
- `uv` is recommended for local setup.
- Docker is optional.

Install `uv` on Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Environment Variables

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Required:

| Variable | Description |
| --- | --- |
| `GROQ_API_KEY` | Your Groq API key. Required for LLM-powered endpoints. |

Optional:

| Variable | Default | Description |
| --- | --- | --- |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name used by the agents. |
| `APP_ENV` | `development` | Application environment label. |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Local ChromaDB persistence directory. |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace embedding model. |
| `LLM_TEMPERATURE` | `0.2` | LLM temperature. |
| `SEARCH_REGION` | `in-en` | DuckDuckGo region used for web evidence. |
| `SEARCH_MAX_RESULTS` | `5` | Search results requested per query. |
| `APP_RELOAD` | unset | Set to `true` only when running `python app/main.py` with autoreload. |

Example `.env`:

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

Do not commit `.env`. It is ignored by `.gitignore`.

## Local Setup

Create and activate a virtual environment:

```powershell
uv venv .venv --python 3.11
.venv\Scripts\activate
```

Install dependencies:

```powershell
uv pip install -r requirements.txt
```

Verify the app imports:

```powershell
python -c "from app.main import app; print(app.title)"
```

Expected output:

```text
GovPrepAI
```

## Run the Backend

Use this command for normal local development:

```powershell
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open the API docs:

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

### Autoreload

On Windows, avoid plain `--reload` because it can watch `.venv` and cause noisy reload traces. If you need autoreload, scope it to the app directory:

```powershell
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

If running through `python app/main.py`, autoreload is disabled by default. To enable it explicitly:

```powershell
$env:APP_RELOAD="true"
python app/main.py
```

## Run the Streamlit Frontend

Start the FastAPI backend first, then run:

```powershell
uv run streamlit run app/ui/streamlit_app.py
```

The frontend expects the API at:

```text
http://localhost:8000
```

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Health check |
| `POST` | `/api/prepare` | Full plan-and-execute agent workflow |
| `POST` | `/api/syllabus` | Syllabus map and topic priority |
| `POST` | `/api/mock-test` | Generate an exam-style mock test |
| `POST` | `/api/study-plan` | Generate a target-date study plan |
| `POST` | `/api/upload-notes?user_id=default` | Upload and index PDF notes |

### Full Preparation Workflow

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/prepare `
  -H "Content-Type: application/json" `
  -d "{\"goal\":\"Create a 6-month SSC preparation plan with syllabus, topic weightage, resources, and mock schedule.\",\"exam_type\":\"SSC\",\"user_id\":\"default\"}"
```

Request body:

```json
{
  "goal": "Create a 6-month SSC preparation plan with syllabus, topic weightage, resources, and mock schedule.",
  "exam_type": "SSC",
  "user_id": "default"
}
```

### Syllabus

```json
{
  "exam_type": "RRB"
}
```

### Mock Test

```json
{
  "exam_type": "GATE",
  "topic": "Operating Systems"
}
```

### Study Plan

```json
{
  "exam_type": "Banking",
  "target_date": "2026-12-31",
  "weak_topics": ["Percentage", "Current Affairs"]
}
```

### Upload Notes

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/upload-notes?user_id=default" `
  -F "file=@notes.pdf"
```

Uploaded notes are parsed, chunked, embedded, and persisted in `CHROMA_PERSIST_DIR`. Later `/api/prepare` calls retrieve relevant note context for the same `user_id`.

## Docker

Build the backend image:

```powershell
docker build -t govprepai .
```

Run the backend container:

```powershell
docker run --rm -p 8000:8000 --env-file .env govprepai
```

Open:

```text
http://localhost:8000/docs
```

## Accuracy and Production Notes

This project is designed to reduce hallucinations by grounding answers in search evidence and uploaded notes. It still cannot guarantee perfect answers, especially for live exam notifications, cutoffs, eligibility rules, dates, or official changes. For production use, always display source links and encourage users to verify final decisions from the official exam body.

For better answer quality:

- Keep `LLM_TEMPERATURE` low, such as `0.1` to `0.3`.
- Prefer official PDFs, notifications, and exam-body pages in uploaded notes.
- Ask users for their exact exam, year, category, language, and target date.
- Use source URLs in final answers.
- Mark uncertain or inferred content clearly.
- Add monitoring for failed searches, empty results, slow LLM calls, and repeated user questions.

### Search Provider

The default search implementation uses `duckduckgo-search` because it is free and works for prototyping. It is not the same as ChatGPT's built-in web search and it does not provide paid production guarantees. For a startup-scale product, consider adding a provider abstraction and using a dedicated search API such as Brave Search API, Tavily, Google Programmable Search, or OpenAI's Responses API web search when budget allows.

### Free Deployment Reality

Free hosting and free LLM/search tiers are useful for demos, early testing, and small pilots. They are not enough for "all users in India" because free tiers usually have limits on requests, bandwidth, uptime, CPU/RAM, storage, abuse protection, and support. A realistic path is:

1. Launch a free pilot for a small user group.
2. Collect high-value exam questions and improve prompts/RAG.
3. Add analytics, rate limits, caching, and source verification.
4. Move to paid infrastructure only after usage proves demand.

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

Stop the running server and restart without reload:

```powershell
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

If you need reload, use:

```powershell
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

### ChromaDB or embedding data should not be pushed

Local vector data is stored in `chroma_db/` by default. This directory is ignored by Git.

### Search returns `Search unavailable`

DuckDuckGo search failures are caught so the app can continue. Retry later or check network access.

## GitHub Push Guide

Initialize Git if needed:

```powershell
git init
```

Check files:

```powershell
git status
```

Stage the project:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Initial commit: add GovPrepAI exam prep agent"
```

Add your GitHub remote:

```powershell
git remote add origin https://github.com/<your-username>/<your-repo>.git
```

Push:

```powershell
git branch -M main
git push -u origin main
```

## Recommended Commit Message

```text
Initial commit: add GovPrepAI exam prep agent
```

## License

This project is configured as MIT in `pyproject.toml`. Add a `LICENSE` file before publishing if you want GitHub to display the license clearly.
