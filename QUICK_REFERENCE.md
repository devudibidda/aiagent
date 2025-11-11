# 🚀 AI COMPLIANCE AGENT - QUICK REFERENCE CARD

## ⚡ START IN 30 SECONDS

```powershell
# Terminal 1
ollama serve mistral

# Terminal 2
cd C:\Users\Nandan\agent
python -m ai_compliance_agent.ui_gradio

# Browser
http://localhost:7860
```

---

## 📋 MODES OF OPERATION

### 1. Web UI (Recommended)
```bash
python -m ai_compliance_agent.ui_gradio
# → http://localhost:7860
```

### 2. CLI
```bash
python -m ai_compliance_agent.app <pdf_id> <kb_path> [--pretty]
```

### 3. Python API
```python
from ai_compliance_agent.agent_pipeline import ComplianceAgent
agent = ComplianceAgent()
result = agent.analyse("doc.pdf", "knowledge_base")
```

---

## 🔧 CONFIGURATION

### Environment Variables (.env)
```bash
OLLAMA_MODEL=mistral
API_BASE_URL=http://api-url
TOKEN_URL=http://token-url
CLIENT_ID=id
CLIENT_SECRET=secret
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
