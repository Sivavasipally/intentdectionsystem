# Troubleshooting Guide

## Common Issues and Solutions

### Database Initialization

#### Issue: "Attribute name 'metadata' is reserved"
**Solution**: Already fixed in the code. The column has been renamed to `chunk_metadata`.

If you still see this error:
1. Delete any existing database: `del data\app.db` (Windows) or `rm data/app.db` (Mac/Linux)
2. Run: `python scripts\init_db.py`

---

### Import Errors

#### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution**: Set PYTHONPATH

**Windows:**
```bash
set PYTHONPATH=%PYTHONPATH%;%CD%
```

**Mac/Linux:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

Or add to your virtual environment activation:
```bash
# Edit venv\Scripts\activate.bat (Windows)
# Add near the top:
set PYTHONPATH=%VIRTUAL_ENV%\..

# Or edit venv/bin/activate (Mac/Linux)
# Add:
export PYTHONPATH="$VIRTUAL_ENV/.."
```

#### Issue: "No module named 'langchain_google_genai'"
**Solution**: Reinstall dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### API Key Issues

#### Issue: "GOOGLE_API_KEY not configured" or "Invalid API key"
**Solutions**:

1. **Check .env file exists**:
   ```bash
   dir .env    # Windows
   ls .env     # Mac/Linux
   ```

2. **Verify API key format** (no quotes, no spaces):
   ```env
   # CORRECT:
   GOOGLE_API_KEY=AIzaSyD...actual_key_here

   # INCORRECT:
   GOOGLE_API_KEY="AIzaSyD..."
   GOOGLE_API_KEY = AIzaSyD...
   ```

3. **Get a new API key**:
   - Visit https://ai.google.dev/
   - Sign in with Google account
   - Create new API key
   - Enable Gemini API

4. **Restart the server** after changing .env

---

### Server Won't Start

#### Issue: "Address already in use" or Port 8000 in use
**Solutions**:

1. **Change port** in `.env`:
   ```env
   API_PORT=8001
   ```

2. **Or specify port when running**:
   ```bash
   uvicorn app.main:app --port 8001
   ```

3. **Find and kill process** using port 8000:

   **Windows:**
   ```bash
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

   **Mac/Linux:**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

#### Issue: Server starts but immediately crashes
**Check logs for**:
1. Missing GOOGLE_API_KEY
2. Database connection errors
3. Import errors

**Solution**: Run with verbose logging:
```bash
uvicorn app.main:app --log-level debug
```

---

### Ingestion Issues

#### Issue: "Unsupported file type"
**Supported formats**: .pdf, .docx, .doc, .md (markdown)

**Solution**: Convert your files to supported format

#### Issue: "No files found" when using glob pattern
**Windows issue**: Windows doesn't expand `*.pdf` automatically

**Solution**: Use full paths or quote the pattern:
```bash
# Instead of:
make ingest DOCS=./kb/*.pdf

# Use:
python scripts\ingest_cli.py --tenant bank-asia kb\file1.pdf kb\file2.pdf

# Or PowerShell:
Get-ChildItem kb\*.pdf | ForEach-Object { python scripts\ingest_cli.py --tenant bank-asia $_.FullName }
```

#### Issue: "Memory error" during ingestion
**Large files**: Break into smaller chunks or increase Python memory

**Solution**:
```bash
# For large files, ingest one at a time
python scripts\ingest_cli.py --tenant bank-asia kb\large_file.pdf
```

---

### FAISS / Vector Store Issues

#### Issue: "FAISS index not found"
**Solution**: Documents haven't been ingested yet
```bash
python scripts\ingest_cli.py --tenant bank-asia kb\sample_channels.md
```

#### Issue: "No results from retrieval"
**Solutions**:
1. **Check tenant name matches**:
   - Ingestion tenant: `--tenant bank-asia`
   - Query tenant: `"tenant": "bank-asia"`

2. **Verify index exists**:
   ```bash
   dir data\indexes\bank-asia    # Windows
   ls data/indexes/bank-asia     # Mac/Linux
   ```
   Should see: `faiss.index` and `metadata.pkl`

3. **Re-ingest documents**:
   ```bash
   # Delete old indexes
   rmdir /S data\indexes\bank-asia  # Windows
   rm -rf data/indexes/bank-asia    # Mac/Linux

   # Re-ingest
   python scripts\ingest_cli.py --tenant bank-asia kb\*.md
   ```

---

### Database Issues

#### Issue: "Database is locked"
**SQLite limitation**: Only one writer at a time

**Solutions**:
1. **Stop all running processes** accessing the database
2. **Delete database lock file**:
   ```bash
   del data\app.db-journal   # Windows
   rm data/app.db-journal    # Mac/Linux
   ```
3. **Use PostgreSQL** for production (concurrent access)

#### Issue: "No such table: channels"
**Solution**: Database not initialized
```bash
python scripts\init_db.py
```

#### Issue: Want to reset database
**Solution**:
```bash
# Windows:
del data\app.db
python scripts\init_db.py

# Mac/Linux:
rm data/app.db
python scripts/init_db.py
```

---

### Gemini API Issues

#### Issue: "API quota exceeded"
**Solutions**:
1. Check quota at https://console.cloud.google.com/
2. Wait for quota reset (usually daily)
3. Upgrade API plan
4. Use rate limiting in production

#### Issue: "API timeout"
**Solutions**:
1. Check internet connection
2. Increase timeout in `app/services/llm.py`
3. Try again (temporary issue)

#### Issue: "Model not found"
**Solution**: Update model name in `app/services/llm.py`:
```python
# Try different model:
model="gemini-1.5-pro"  # or "gemini-pro"
```

---

### Testing Issues

#### Issue: Tests fail with "fixture not found"
**Solution**: Install test dependencies
```bash
pip install pytest pytest-asyncio pytest-cov
```

#### Issue: Tests pass but no coverage report
**Solution**: Install coverage
```bash
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html
```

#### Issue: Smoke tests fail - "Connection refused"
**Solution**: Make sure server is running
```bash
# Terminal 1: Start server
uvicorn app.main:app --reload

# Terminal 2: Run tests
python scripts\test_system.py smoke
```

---

### Docker Issues

#### Issue: "Docker daemon not running"
**Solution**: Start Docker Desktop

#### Issue: "Cannot find .env"
**Solution**: Create .env before building
```bash
copy .env.example .env
# Add GOOGLE_API_KEY
docker-compose up --build
```

#### Issue: Container starts but API not accessible
**Solutions**:
1. **Check port mapping**: Should be `8000:8000`
2. **Check logs**: `docker-compose logs -f`
3. **Verify container running**: `docker ps`

---

### Performance Issues

#### Issue: Slow response times
**Optimizations**:

1. **Use faster Gemini model**:
   ```python
   # In app/services/llm.py
   model="gemini-1.5-flash"  # Faster
   ```

2. **Reduce retrieval count**:
   ```env
   RETRIEVAL_TOP_K=3  # Instead of 6
   ```

3. **Enable Redis caching** (optional):
   ```bash
   # Install Redis
   pip install redis

   # In .env:
   REDIS_URL=redis://localhost:6379/0
   ```

4. **Use multiple workers** (production):
   ```bash
   uvicorn app.main:app --workers 4
   ```

---

### Windows-Specific Issues

#### Issue: Makefile commands don't work
**Solution**: Use Python directly or install Make for Windows

**Alternative**:
```bash
# Instead of: make run
python -m uvicorn app.main:app --reload

# Instead of: make test
pytest tests/ -v

# Instead of: make ingest DOCS=./kb/*.pdf
python scripts\ingest_cli.py --tenant bank-asia kb\*.pdf
```

#### Issue: Path issues with backslashes
**Solution**: Use forward slashes in paths:
```python
# Works on both Windows and Linux:
path = "kb/sample_channels.md"
```

---

### Common Questions

#### Q: How do I add a new intent?
**A**: Edit `prompts/router.yaml`:
```yaml
few_shot:
  - user: "Your example utterance"
    assistant: |
      {
        "intent": "your_new_intent",
        "confidence": 0.9,
        "entities": {}
      }
```

Then add to `policies/router.yaml`:
```yaml
intent_routes:
  your_new_intent:
    tool: YourTool
    require_kb_validation: false
```

#### Q: How do I change confidence threshold?
**A**: Edit `.env`:
```env
MIN_CONFIDENCE=0.8  # Higher = more strict
OOD_THRESHOLD=0.5   # Lower = more OOD detection
```

#### Q: How do I use PostgreSQL instead of SQLite?
**A**:
1. Install: `pip install psycopg2-binary`
2. Create database: `createdb intent_db`
3. Update `.env`:
   ```env
   DB_URL=postgresql://user:password@localhost:5432/intent_db
   ```
4. Initialize: `python scripts/init_db.py`

#### Q: How do I deploy to production?
**A**: See deployment checklist:
1. Use PostgreSQL (not SQLite)
2. Set `ENV=production` in `.env`
3. Use multiple workers: `--workers 4`
4. Enable HTTPS (nginx/reverse proxy)
5. Set proper `LOG_LEVEL=WARNING`
6. Use Redis for caching
7. Set up monitoring (health checks)

---

## Getting More Help

1. **Check logs**: Server console output
2. **Run verification**: `python scripts/verify_setup.py`
3. **Check setup**: Review [QUICKSTART.md](QUICKSTART.md)
4. **Read docs**: [README.md](README.md)
5. **Test API**: http://localhost:8000/docs

---

## Quick Reset (Nuclear Option)

If everything is broken and you want to start fresh:

```bash
# Windows:
rmdir /S /Q venv data
del .env
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with GOOGLE_API_KEY
python scripts\init_db.py
python scripts\ingest_cli.py --tenant bank-asia kb\sample_channels.md
uvicorn app.main:app --reload

# Mac/Linux:
rm -rf venv data .env
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with GOOGLE_API_KEY
python scripts/init_db.py
python scripts/ingest_cli.py --tenant bank-asia kb/sample_channels.md
uvicorn app.main:app --reload
```

This gives you a completely fresh start!
