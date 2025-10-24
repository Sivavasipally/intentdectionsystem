# Installation Guide - OpenAI Version

Complete installation guide for the Intent Detection System with OpenAI.

---

## Prerequisites

- **Python 3.11 or higher** (Check: `python --version`)
- **pip** package manager
- **OpenAI API Key** (Get it from https://platform.openai.com/)
- **Windows/Mac/Linux** - Works on all platforms

---

## Step-by-Step Installation

### Step 1: Clone or Download the Project

If you already have the project:
```bash
cd D:\GenAi\intentdectionsystem
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Mac/Linux:
# source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 3: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI & Uvicorn (Web server)
- LangChain & OpenAI (AI framework)
- FAISS (Vector search)
- SQLAlchemy (Database)
- LangGraph (Agent orchestration)
- And 30+ other dependencies

**Installation time**: 2-5 minutes

### Step 5: Configure Environment

```bash
# Copy the example environment file
copy .env.example .env

# Edit the .env file
notepad .env
```

**Minimum required configuration:**

```env
# OpenAI API (REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Database (default is fine)
DB_URL=sqlite:///./data/app.db

# Vector Store (default is fine)
VECTOR_DIR=./data/indexes

# Default Settings (optional - these are defaults)
TENANT=bank-asia
LANGUAGE=en-IN
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
MIN_CONFIDENCE=0.7
LOG_LEVEL=INFO
```

**Save the file!**

### Step 6: Get OpenAI API Key

1. Go to https://platform.openai.com/
2. Create an account or sign in
3. Click **API Keys** in the left sidebar
4. Click **"Create new secret key"**
5. Name it (e.g., "Intent Detection System")
6. **Copy the key** (starts with `sk-`)
7. Paste it into your `.env` file

⚠️ **Important**:
- Save the key immediately - you can't see it again
- Never commit `.env` to git
- Free tier includes $5 credit

### Step 7: Initialize Database

```bash
python scripts\init_db.py
```

You should see:
```
Initializing database...
Created data directory: D:\GenAi\intentdectionsystem\data
Created indexes directory: D:\GenAi\intentdectionsystem\data\indexes
Created uploads directory: D:\GenAi\intentdectionsystem\data\uploads

✓ Database initialized successfully!
✓ Database location: D:\GenAi\intentdectionsystem\data\app.db
```

### Step 8: Ingest Sample Knowledge Base

```bash
python scripts\ingest_cli.py --tenant bank-asia --doc-type channels kb\sample_channels.md
```

You should see:
```
Found 1 file(s) to ingest

============================================================
INGESTION COMPLETE
============================================================
Documents processed: 1
Chunks created: 15-20
Index path: .\data\indexes\bank-asia
============================================================
```

This creates the FAISS vector index for RAG retrieval.

### Step 9: Verify Installation

```bash
python scripts\verify_setup.py
```

You should see all checkmarks:
```
✓ Python version 3.11+
✓ Dependencies installed
✓ Environment configured
✓ OPENAI_API_KEY is set
✓ API key is valid and accessible
✓ Database initialized
✓ Knowledge base has documents
✓ Vector store indexes exist
```

### Step 10: Start the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Starting Intent Detection System...
INFO:     Environment: development
INFO:     Tenant: bank-asia
INFO:     Database initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

🎉 **Success! The server is running!**

---

## Testing Your Installation

### Option 1: Open Swagger UI

Open your browser to:
```
http://localhost:8000/docs
```

Try the `/intent/v1/detect` endpoint with:
```json
{
  "utterance": "What are NEFT transfer charges?",
  "channel": "web",
  "locale": "en-IN",
  "tenant": "bank-asia"
}
```

### Option 2: Run Smoke Tests

Open a **new terminal** (keep server running):

```bash
cd D:\GenAi\intentdectionsystem
venv\Scripts\activate
python scripts\test_system.py smoke
```

### Option 3: Use cURL

```bash
curl -X POST http://localhost:8000/intent/v1/detect ^
  -H "Content-Type: application/json" ^
  -d "{\"utterance\":\"What are NEFT charges?\",\"channel\":\"web\",\"locale\":\"en-IN\",\"tenant\":\"bank-asia\"}"
```

### Option 4: Interactive Testing

```bash
python scripts\test_system.py

# Type commands:
> detect What are NEFT charges?
> open Open WhatsApp channel for Retail Banking
> list
> quit
```

---

## Installed Packages Summary

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.109.2 | Web framework |
| uvicorn | 0.27.1 | ASGI server |
| openai | 1.12.0 | OpenAI API client |
| langchain | 0.1.9 | LLM framework |
| langchain-openai | 0.0.5 | OpenAI integration |
| langgraph | 0.0.26 | Agent orchestration |
| faiss-cpu | 1.7.4 | Vector search |
| sqlalchemy | 2.0.27 | Database ORM |
| pydantic | 2.6.1 | Data validation |
| pypdf | 4.0.1 | PDF processing |
| pytest | 8.0.0 | Testing |

Total packages: ~40

---

## Directory Structure After Installation

```
intentdectionsystem/
├── venv/                    # Virtual environment (created)
├── data/                    # Runtime data (created)
│   ├── app.db              # SQLite database
│   ├── indexes/            # FAISS indexes
│   │   └── bank-asia/      # Tenant-specific index
│   │       ├── faiss.index
│   │       └── metadata.pkl
│   └── uploads/            # Temp uploads
├── app/                     # Application code
├── prompts/                 # Prompt templates
├── policies/                # Policy config
├── kb/                      # Knowledge base
│   └── sample_channels.md  # Sample document
├── .env                     # Your config (created)
└── requirements.txt         # Dependencies
```

---

## Common Installation Issues

### Issue: Python version too old
```bash
python --version
# If < 3.11, download from https://www.python.org/downloads/
```

### Issue: pip install fails
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try again
pip install -r requirements.txt
```

### Issue: Virtual environment activation fails

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

### Issue: OpenAI API key invalid
1. Check you copied the full key (starts with `sk-`)
2. No quotes around the key in `.env`
3. No spaces before or after the `=`
4. Key should be on one line

### Issue: Database initialization fails
```bash
# Delete data folder and try again
rmdir /S data
python scripts\init_db.py
```

### Issue: Port 8000 already in use
```bash
# Use different port
python -m uvicorn app.main:app --port 8001
```

---

## Next Steps

After successful installation:

1. **Add Your Documents**:
   - Copy PDF/DOCX files to `kb/` folder
   - Run: `python scripts\ingest_cli.py --tenant bank-asia kb\yourfile.pdf`

2. **Customize Prompts**:
   - Edit files in `prompts/` directory
   - Adjust intent classification, entity extraction

3. **Configure Policies**:
   - Edit `policies/router.yaml`
   - Set confidence thresholds, routing rules

4. **Run Tests**:
   - `pytest tests/ -v`
   - `python eval/evaluate.py`

5. **Deploy to Production**:
   - See deployment guide in README.md
   - Use PostgreSQL instead of SQLite
   - Run with multiple workers

---

## Useful Commands

```bash
# Start development server
python -m uvicorn app.main:app --reload

# Or use Makefile (if you have make):
make run

# Run tests
pytest tests/ -v

# Run evaluation
python eval/evaluate.py

# Verify setup
python scripts\verify_setup.py

# Ingest documents
python scripts\ingest_cli.py --tenant bank-asia kb\*.pdf

# Interactive testing
python scripts\test_system.py
```

---

## Getting Help

- **Documentation**: [README.md](README.md)
- **Quick Start**: [SETUP_OPENAI.md](SETUP_OPENAI.md)
- **Migration Guide**: [OPENAI_MIGRATION.md](OPENAI_MIGRATION.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **API Docs**: http://localhost:8000/docs (when server is running)

---

## Uninstallation

To completely remove:

```bash
# Deactivate virtual environment
deactivate

# Delete virtual environment
rmdir /S venv

# Delete data
rmdir /S data

# Delete .env
del .env
```

---

**Installation complete! You're ready to start building with the Intent Detection System! 🚀**
