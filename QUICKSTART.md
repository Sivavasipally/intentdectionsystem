# Quick Start Guide

## 5-Minute Setup

### 1. Install & Configure

```bash
# Clone and setup
cd intentdectionsystem
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 2. Initialize

```bash
# Create database
python scripts/init_db.py

# Start server
python -m uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

### 3. Ingest Sample Knowledge Base

```bash
# Ingest sample document
python scripts/ingest_cli.py --tenant bank-asia --doc-type channels kb/sample_channels.md
```

### 4. Test the System

**Detect Intent:**
```bash
curl -X POST http://localhost:8000/intent/v1/detect \
  -H "Content-Type: application/json" \
  -d '{
    "utterance": "What are NEFT charges?",
    "channel": "web",
    "locale": "en-IN",
    "tenant": "bank-asia"
  }'
```

**Open Channel (Full Flow):**
```bash
curl -X POST http://localhost:8000/intent/v1/understand-and-open \
  -H "Content-Type: application/json" \
  -d '{
    "utterance": "Open WhatsApp channel for Retail Banking and enable card block",
    "tenant": "bank-asia"
  }'
```

## Key Endpoints

| Endpoint | Purpose | Method |
|----------|---------|--------|
| `/intent/v1/detect` | Detect intent | POST |
| `/intent/v1/understand-and-open` | Full workflow | POST |
| `/intent/v1/simulate` | Test multiple | POST |
| `/channels/{id}` | Get channel | GET |
| `/ingest` | Upload docs | POST |
| `/health` | Health check | GET |
| `/docs` | Swagger UI | GET |

## Common Commands

```bash
# Run server
make run

# Ingest documents
make ingest DOCS="./kb/*.pdf"

# Run tests
make test

# Run evaluation
make eval

# Docker
make docker-build
make docker-run
```

## Example Utterances

### Open Channel
- "Open WhatsApp channel for Retail Banking"
- "Register for mobile banking"
- "Activate Telegram channel for card services"

### FAQs
- "What are NEFT transfer charges?"
- "How to block my credit card?"
- "What are loan interest rates?"

### Transactions
- "Transfer 5000 rupees to savings account"
- "Check my account balance"
- "Show last 5 transactions"

### Out-of-Domain
- "What's the weather?"
- "Who won the match?"
- "Tell me a joke"

## Architecture Overview

```
User Input → FastAPI → LangGraph Agent → [
  1. Detect Intent (Gemini)
  2. Retrieve KB (FAISS)
  3. Extract Entities (Gemini + KB)
  4. Validate (KB)
  5. Route (Policy)
  6. Execute (Channel Writer)
] → Response
```

## Troubleshooting

**Issue**: Module not found
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Issue**: Database error
```bash
rm data/app.db
python scripts/init_db.py
```

**Issue**: Gemini API error
- Check GOOGLE_API_KEY in .env
- Verify API is enabled at https://ai.google.dev/

**Issue**: No KB results
```bash
# Ensure documents are ingested
python scripts/ingest_cli.py --tenant bank-asia kb/sample_channels.md
```

## Next Steps

1. Add your own knowledge base documents (.pdf/.docx)
2. Customize prompts in `prompts/` directory
3. Adjust policies in `policies/router.yaml`
4. Extend intents in prompt templates
5. Add more channels and operations

## Resources

- Full Documentation: [README.md](README.md)
- API Docs: http://localhost:8000/docs
- Sample Data: [kb/sample_channels.md](kb/sample_channels.md)
- Tests: [tests/](tests/)
- Evaluation: [eval/](eval/)
