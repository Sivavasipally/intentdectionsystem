# Quick Setup Guide - OpenAI Version

## ✅ Complete Migration to OpenAI

Your Intent Detection System now uses **OpenAI** instead of Gemini.

---

## 🚀 Quick Start (5 Steps)

### Step 1: Install Dependencies

```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Install OpenAI packages
pip install -r requirements.txt
```

This installs:
- `openai==1.12.0`
- `langchain-openai==0.0.5`
- `tiktoken==0.5.2`

---

### Step 2: Get OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Click on **API Keys** in the left sidebar
4. Click **"Create new secret key"**
5. Copy the key (starts with `sk-`)

⚠️ **Important**: Save the key immediately - you won't be able to see it again!

---

### Step 3: Configure Environment

```bash
# Update your .env file
notepad .env
```

Add/update these lines:
```env
# OpenAI API
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Remove old Gemini key (if present)
# GOOGLE_API_KEY=...
```

**Save the file!**

---

### Step 4: Re-Ingest Documents (IMPORTANT!)

⚠️ **You MUST re-ingest** because embedding dimensions changed from 768 → 1536

```bash
# Delete old FAISS indexes
rmdir /S data\indexes

# Re-ingest sample document
python scripts\ingest_cli.py --tenant bank-asia --doc-type channels kb\sample_channels.md
```

You should see:
```
Found 1 file(s) to ingest
============================================================
INGESTION COMPLETE
============================================================
Documents processed: 1
Chunks created: ~15-20
Index path: .\data\indexes\bank-asia
============================================================
```

---

### Step 5: Start & Test

```bash
# Start the server
python -m uvicorn app.main:app --reload
```

**Test it:**

Open http://localhost:8000/docs and try the `/intent/v1/detect` endpoint with:
```json
{
  "utterance": "What are NEFT transfer charges?",
  "channel": "web",
  "locale": "en-IN",
  "tenant": "bank-asia"
}
```

Or use the command line:
```bash
# In a new terminal
python scripts\test_system.py smoke
```

---

## 📊 What Changed?

| Component | Before (Gemini) | After (OpenAI) |
|-----------|----------------|----------------|
| **LLM** | gemini-1.5-flash | gpt-4o-mini |
| **Embeddings** | embedding-001 (768d) | text-embedding-3-small (1536d) |
| **API Key Env** | GOOGLE_API_KEY | OPENAI_API_KEY |
| **Cost** | ~$0 (free tier) | ~$0.0001 per request |
| **Quality** | Good | Better (more consistent) |

---

## 💰 Pricing (Don't Worry, It's Cheap!)

### Per Request Costs
- **Simple intent detection**: ~$0.0001 (1/100th of a cent)
- **Full workflow (open channel)**: ~$0.001 (1/10th of a cent)
- **Document ingestion** (1000 chunks): ~$0.02 (2 cents)

### Example Monthly Usage
- 10,000 requests/month: **~$1-2**
- 100,000 requests/month: **~$10-20**

**Free tier**: $5 credit for new accounts (lasts a long time with this usage!)

---

## 🎯 Model Options

### Recommended Settings (Default)
```env
OPENAI_MODEL=gpt-4o-mini           # Fast, cheap, good quality
OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # Best value
```

### Alternative Models

**For better quality:**
```env
OPENAI_MODEL=gpt-4o                # Higher quality, 2-3x cost
```

**For lower cost:**
```env
OPENAI_MODEL=gpt-3.5-turbo         # Faster, cheaper, lower quality
```

**For better embeddings:**
```env
OPENAI_EMBEDDING_MODEL=text-embedding-3-large  # 3072 dimensions, higher cost
```

---

## ✅ Verify Setup

Run the verification script:

```bash
python scripts\verify_setup.py
```

You should see:
```
✓ Python 3.11+
✓ Dependencies installed
✓ OPENAI_API_KEY is set
✓ API key is valid and accessible
✓ Database initialized
✓ Knowledge base has documents
✓ Vector store indexes exist
```

---

## 🔧 Troubleshooting

### "OPENAI_API_KEY not configured"
1. Check `.env` file exists in project root
2. Make sure the key is on one line: `OPENAI_API_KEY=sk-...`
3. No quotes needed around the key
4. Restart the server after changing `.env`

### "Incorrect dimensions for IndexFlatL2"
Old FAISS indexes are incompatible. Delete and re-ingest:
```bash
rmdir /S data\indexes
python scripts\ingest_cli.py --tenant bank-asia kb\sample_channels.md
```

### "Rate limit exceeded"
You're making requests too fast:
- Free tier: 3 requests/minute, 200/day
- Paid tier: 3,500 requests/minute
- Solution: Add payment method or slow down requests

### "Insufficient quota"
Add credits to your OpenAI account:
1. Visit https://platform.openai.com/account/billing
2. Add payment method
3. Purchase credits (starts at $5)

---

## 📖 Additional Resources

- **OpenAI Platform**: https://platform.openai.com/
- **API Documentation**: https://platform.openai.com/docs/api-reference
- **Pricing**: https://openai.com/pricing
- **Usage Dashboard**: https://platform.openai.com/usage
- **Migration Guide**: [OPENAI_MIGRATION.md](OPENAI_MIGRATION.md)

---

## 🎉 You're All Set!

The system is now running on OpenAI with:
- ✅ Better response quality
- ✅ More consistent JSON parsing
- ✅ Higher quality embeddings
- ✅ Proven scalability

Cost: ~$0.0001 per request (very affordable!)

**Next Steps:**
1. Test with your own utterances
2. Add your own documents to `kb/`
3. Customize prompts in `prompts/`
4. Deploy to production!

For full documentation, see [README.md](README.md)
