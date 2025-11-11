# 🎯 Quick Reference Card - AI Compliance Agent

## 🚨 ERROR: "llama runner process has terminated"

**INSTANT FIX (3 steps):**
```bash
# Terminal 1 - Start Ollama
ollama serve

# Terminal 2 - Check status
curl http://localhost:11434/api/tags

# Terminal 3 - Run app
OLLAMA_MODEL=neural-chat python -m ai_compliance_agent.ui_gradio
```

**If still failing:**
- ✅ Ensure 8GB+ free RAM: `free -h`
- ✅ Use lighter model: `OLLAMA_MODEL=neural-chat` in `.env`
- ✅ Monitor memory: `watch -n 1 free -h`

---

## ⚡ START IN 30 SECONDS

```bash
# Terminal 1
ollama serve

# Terminal 2 (wait 3 seconds)
OLLAMA_MODEL=neural-chat python -m ai_compliance_agent.ui_gradio

# Browser
http://127.0.0.1:7860
```

---

## 📋 MODES OF OPERATION

### 1. Web UI (Recommended) ⭐
```bash
python -m ai_compliance_agent.ui_gradio
# → http://127.0.0.1:7860
# Best for: Interactive analysis, non-technical users
```

### 2. Python API
```python
from ai_compliance_agent.agent_pipeline import ComplianceAgent
from pathlib import Path

agent = ComplianceAgent()
result = agent.analyse(
    pdf_id="./local_pdfs/document.pdf",
    knowledge_base_path=Path("./ai_compliance_agent/knowledge_base")
)
print(result["analysis"])
```

### 3. Batch Processing
```python
from concurrent.futures import ThreadPoolExecutor

pdfs = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
with ThreadPoolExecutor(max_workers=2) as executor:
    results = [
        executor.submit(agent.analyse, pdf, kb_path)
        for pdf in pdfs
    ]
```

---

## 🔧 CONFIGURATION

### Environment Variables (.env)
```bash
# ✅ REQUIRED
OLLAMA_MODEL=neural-chat

# ❓ Optional (OAuth2 PDF API)
API_BASE_URL=https://api.example.com
TOKEN_URL=https://auth.example.com/oauth/token
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret

# Optional (paths)
DOWNLOAD_DIR=./ai_compliance_agent/tmp_downloads
KNOWLEDGE_BASE_DIR=./ai_compliance_agent/knowledge_base
LOCAL_PDF_DIR=./ai_compliance_agent/local_pdfs
```

### Directories
```
knowledge_base/    → Standard PDFs
local_pdfs/        → Local test files
tmp_downloads/     → Downloaded PDFs
```

---

## ✅ QUICK CHECKLIST

- [ ] Python 3.11.9+
- [ ] Virtual env active
- [ ] 65+ packages installed
- [ ] Ollama ready
- [ ] Port 7860 free
- [ ] Knowledge base setup

---

## 🆘 QUICK FIXES

| Problem | Fix |
|---------|-----|
| "Module not found" | ✅ Already fixed |
| Ollama error | Run: `ollama serve mistral` |
| Port 7860 in use | `taskkill /PID <ID> /F` |
| Slow | Use: `OLLAMA_MODEL=neural-chat` |
| Memory error | Process one file at a time |

---

## 📚 DOCUMENTATION

- **QUICK_START_GUIDE.md** - Complete setup
- **ADVANCED_GUIDE.md** - Production deployment
- **RUN_COMMANDS.md** - All commands
- **SCRIPT_ANALYSIS.md** - Technical details

---

## 🎯 TYPICAL USAGE

```python
from ai_compliance_agent.agent_pipeline import ComplianceAgent
from pathlib import Path

# Initialize
agent = ComplianceAgent()

# Analyze
result = agent.analyse(
    pdf_id="document.pdf",
    knowledge_base_path=Path("knowledge_base")
)

# Results contain:
# - analysis (main report)
# - document_summary
# - knowledge_base_summary
# - sources (retrieved context)
```

---

## 🚀 STATUS: ✅ READY

**All issues fixed. Ready to execute now!**

---

## 📱 FILES CREATED FOR YOU

```
✅ FINAL_SUMMARY.md         → Start here
✅ RUN_COMMANDS.md          → Copy-paste commands
✅ QUICK_START_GUIDE.md     → Step-by-step setup
✅ ADVANCED_GUIDE.md        → Production guide
✅ SCRIPT_ANALYSIS.md       → Technical details
```

---

**Let's go! 🎉**

Run these commands now:
```
ollama serve mistral &
python -m ai_compliance_agent.ui_gradio
```
