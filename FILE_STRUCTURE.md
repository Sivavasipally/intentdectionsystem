# Complete File Structure

## Project Root Files

| File | Purpose | Lines |
|------|---------|-------|
| `.env.example` | Environment variables template | ~30 |
| `.gitignore` | Git ignore rules | ~190 |
| `requirements.txt` | Python dependencies | ~40 |
| `pyproject.toml` | Python project config (mypy, pytest, black, ruff) | ~30 |
| `Dockerfile` | Docker image definition | ~40 |
| `docker-compose.yml` | Docker Compose configuration | ~30 |
| `Makefile` | Build automation and commands | ~95 |
| `README.md` | Complete documentation | ~500 |
| `QUICKSTART.md` | 5-minute setup guide | ~200 |
| `ARCHITECTURE.md` | System architecture docs | ~400 |
| `PROJECT_SUMMARY.md` | Project overview | ~600 |
| `FILE_STRUCTURE.md` | This file | ~150 |

## Application Code (`app/`)

### Core (`app/`)
- `__init__.py` - Package initialization
- `main.py` - FastAPI application entry point (200 lines)

### API Layer (`app/api/`)
- `__init__.py` - API package exports
- `intent.py` - Intent detection endpoints (160 lines)
- `channels.py` - Channel management endpoints (80 lines)
- `ingest.py` - Document ingestion endpoint (100 lines)

### Agent Layer (`app/agents/`)
- `__init__.py` - Agent exports
- `graph.py` - LangGraph workflow definition (200 lines)
- `tools.py` - Agent tools (retriever, validator, writer) (180 lines)

### Configuration (`app/config/`)
- `__init__.py` - Config exports
- `settings.py` - Pydantic settings (80 lines)

### Database (`app/db/`)
- `__init__.py` - Database exports
- `database.py` - SQLAlchemy setup and session management (50 lines)

### Data Models (`app/models/`)
- `__init__.py` - Model exports
- `database.py` - SQLAlchemy ORM models (120 lines)
- `schemas.py` - Pydantic request/response schemas (200 lines)

### RAG Components (`app/rag/`)
- `__init__.py` - RAG exports
- `embeddings.py` - Gemini embeddings service (40 lines)
- `chunking.py` - Text chunking service (60 lines)
- `vector_store.py` - FAISS vector store (180 lines)

### Business Services (`app/services/`)
- `__init__.py` - Services exports
- `intent.py` - Intent detection logic (120 lines)
- `retrieval.py` - RAG retrieval service (140 lines)
- `ingestion.py` - Document processing (150 lines)
- `llm.py` - Gemini LLM service (80 lines)
- `policy.py` - Policy routing (80 lines)
- `prompts.py` - Prompt management (50 lines)

### Utilities (`app/utils/`)
- `__init__.py` - Utils exports
- `tracing.py` - Request tracing (30 lines)

## Prompts (`prompts/`)

| File | Purpose | Lines |
|------|---------|-------|
| `router.yaml` | Intent classification with few-shot examples | ~60 |
| `entities.yaml` | Entity extraction rules | ~40 |
| `rag_answer.yaml` | RAG Q&A template | ~20 |
| `validate_kb.yaml` | KB validation template | ~25 |

## Policies (`policies/`)

| File | Purpose | Lines |
|------|---------|-------|
| `router.yaml` | Intent routing rules and policies | ~40 |

## Tests (`tests/`)

| File | Purpose | Lines |
|------|---------|-------|
| `__init__.py` | Tests package | 1 |
| `conftest.py` | Pytest fixtures | ~50 |
| `test_intent.py` | Intent detection tests | ~150 |
| `test_rag.py` | RAG component tests | ~100 |

## Evaluation (`eval/`)

| File | Purpose | Lines |
|------|---------|-------|
| `offline.jsonl` | 20 labeled test samples | 20 |
| `evaluate.py` | Evaluation script with metrics | ~150 |

## Scripts (`scripts/`)

| File | Purpose | Lines |
|------|---------|-------|
| `__init__.py` | Scripts package | 1 |
| `init_db.py` | Database initialization | ~25 |
| `ingest_cli.py` | CLI document ingestion | ~80 |
| `verify_setup.py` | Setup verification checks | ~250 |
| `test_system.py` | Interactive testing CLI | ~400 |

## Schemas (`schemas/`)

| File | Purpose | Lines |
|------|---------|-------|
| `intent_result.json` | Intent result JSON schema | ~50 |
| `understand_and_open_response.json` | Response JSON schema | ~60 |

## Knowledge Base (`kb/`)

| File | Purpose | Lines |
|------|---------|-------|
| `sample_channels.md` | Sample KB document | ~200 |
| *(user-added .pdf/.docx files)* | Knowledge base documents | - |

## Runtime Data (`data/` - not in git)

```
data/
├── indexes/              # FAISS vector indexes
│   └── {tenant}/        # Per-tenant indexes
│       ├── faiss.index  # FAISS binary
│       └── metadata.pkl # Metadata pickle
├── uploads/             # Temporary uploads
└── app.db              # SQLite database (dev)
```

## Total Line Count by Component

| Component | Files | Approx Lines |
|-----------|-------|--------------|
| Application Code | 25 | ~2,500 |
| Tests | 3 | ~300 |
| Scripts | 4 | ~750 |
| Prompts | 4 | ~145 |
| Policies | 1 | ~40 |
| Docs | 7 | ~2,400 |
| Config | 5 | ~250 |
| **TOTAL** | **49** | **~6,385** |

## File Type Breakdown

| Extension | Count | Purpose |
|-----------|-------|---------|
| `.py` | 29 | Python code |
| `.yaml` | 5 | Prompts & policies |
| `.md` | 7 | Documentation |
| `.json` | 2 | JSON schemas |
| `.jsonl` | 1 | Test dataset |
| `.txt` | 1 | Dependencies |
| `.toml` | 1 | Project config |
| `.yml` | 1 | Docker Compose |
| `Dockerfile` | 1 | Docker |
| `Makefile` | 1 | Build automation |
| `.example` | 1 | Env template |
| `.gitignore` | 1 | Git ignore |

## Key File Dependencies

### Import Chain
```
main.py
  ├── api/* (routers)
  │   ├── models/schemas.py
  │   ├── agents/graph.py
  │   │   └── agents/tools.py
  │   │       ├── services/intent.py
  │   │       ├── services/retrieval.py
  │   │       └── services/policy.py
  │   └── services/ingestion.py
  ├── config/settings.py
  └── db/database.py
      └── models/database.py
```

### Service Dependencies
```
services/intent.py
  ├── services/llm.py
  │   └── config/settings.py
  └── services/prompts.py

services/retrieval.py
  ├── rag/vector_store.py
  │   └── rag/embeddings.py
  └── services/llm.py

services/ingestion.py
  ├── rag/chunking.py
  ├── rag/embeddings.py
  └── rag/vector_store.py
```

## External Dependencies

### Python Packages (requirements.txt)
- **Web**: fastapi, uvicorn
- **AI/ML**: langchain, langchain-google-genai, langgraph, google-generativeai
- **Vector**: faiss-cpu, sentence-transformers
- **DB**: sqlalchemy, alembic, psycopg2-binary
- **Docs**: pypdf, python-docx, docx2txt, unstructured
- **Data**: pydantic, pydantic-settings, numpy, scikit-learn
- **Utils**: pyyaml, python-dotenv, httpx, redis, tenacity
- **Dev**: pytest, pytest-asyncio, pytest-cov, mypy, black, ruff

### System Dependencies
- Python 3.11+
- Google Gemini API access
- (Optional) PostgreSQL
- (Optional) Redis

## Generated/Runtime Files (not in git)

```
data/
  ├── app.db              # SQLite database
  ├── indexes/{tenant}/   # FAISS indexes
  └── uploads/            # Temp uploads

*.pyc                     # Bytecode
__pycache__/             # Python cache
.pytest_cache/           # Pytest cache
.mypy_cache/             # Mypy cache
.ruff_cache/             # Ruff cache
htmlcov/                 # Coverage reports
.coverage                # Coverage data
*.log                    # Log files
.env                     # Environment (secret)
```

## File Permissions

### Executable Scripts
- `scripts/*.py` - Should be executable
- Can run with: `python scripts/<script>.py`

### Configuration Files
- `.env` - Read-only for app, write for admin
- `prompts/*.yaml` - Editable by users
- `policies/*.yaml` - Editable by users

### Data Directories
- `data/` - Read/write for app
- `kb/` - Read for app, write for users
- `uploads/` - Read/write for app (temp)

## Quick Navigation

### To add a new feature:
1. **Model**: `app/models/schemas.py` (API) + `app/models/database.py` (DB)
2. **Business Logic**: `app/services/<new>.py`
3. **API**: `app/api/<new>.py`
4. **Tests**: `tests/test_<new>.py`

### To modify behavior:
1. **Intents**: `prompts/router.yaml`
2. **Entities**: `prompts/entities.yaml` + `app/models/schemas.py`
3. **Routing**: `policies/router.yaml`
4. **Agent Flow**: `app/agents/graph.py`

### To troubleshoot:
1. **Logs**: Check console output or log files
2. **DB**: `data/app.db` (SQLite browser)
3. **Indexes**: `data/indexes/{tenant}/`
4. **Tests**: Run `make test` or `make smoke`
5. **Verify**: Run `make verify`

## Documentation Map

| Document | Audience | Purpose |
|----------|----------|---------|
| `README.md` | All users | Complete documentation |
| `QUICKSTART.md` | New users | Fast setup |
| `ARCHITECTURE.md` | Developers | System design |
| `PROJECT_SUMMARY.md` | Technical managers | Overview |
| `FILE_STRUCTURE.md` | Developers | This file |
| `/docs` (API) | API users | Endpoint docs |
