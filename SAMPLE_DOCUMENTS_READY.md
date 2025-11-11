# 🎯 QUICK START - Sample Documents Ready!

## ✅ What Was Done

Sample compliance standard documents have been **automatically created** and are ready to use:

```
📁 ai_compliance_agent/knowledge_base/
   ├── ISO_27001_Standard.pdf      (3.9 KB)
   ├── GDPR_Standard.pdf           (4.2 KB)
   └── SOC2_Standard.pdf           (4.3 KB)
```

These are generic compliance standards that you can use immediately for testing.

---

## 🚀 Start Application in 60 Seconds

### Step 1: Start Ollama (Terminal 1)
```bash
ollama serve
```
Wait for: `Listening on 127.0.0.1:11434`

### Step 2: Run Web Interface (Terminal 2)
```bash
cd /workspaces/aiagent
python -m ai_compliance_agent.ui_gradio
```

### Step 3: Open Browser (Terminal 3)
```bash
http://127.0.0.1:7860
```

---

## 📋 How to Use

### Scenario 1: Analyze a Local PDF
1. In the web UI, enter PDF path:
   ```
   ./ai_compliance_agent/local_pdfs/your_document.pdf
   ```
2. Or copy your PDF to that folder first:
   ```bash
   cp /path/to/your/document.pdf ai_compliance_agent/local_pdfs/
   ```
3. Click "Analyse Document"

### Scenario 2: Test with Sample Data
The knowledge base already has 3 sample standards. Just:
1. Provide any PDF path (or use a sample from `local_pdfs/`)
2. Click "Analyse Document"
3. Review the compliance analysis against the standards

---

## 🔄 Bypass vs. Real Knowledge Base

### Option A: Use Fallback Mode (No PDFs needed)
If `knowledge_base/` is empty, the agent automatically uses **generic compliance standards**:
- ISO 27001
- GDPR
- SOC 2

### Option B: Use Real Documents (Recommended for Production)
Replace the sample PDFs with your actual compliance standards:
```bash
# Remove samples
rm ai_compliance_agent/knowledge_base/*.pdf

# Add your PDFs
cp /path/to/your/standards/*.pdf ai_compliance_agent/knowledge_base/

# On first run, embeddings will be generated and cached
```

---

## 📊 Sample Document Contents

### ISO 27001
- Information Security Management System
- 8 core requirements: asset management, access control, cryptography, physical security, operations, incidents, business continuity, compliance
- 14 control objectives
- Implementation timeline

### GDPR
- Data Protection Regulation (EU 2016/679)
- 7 key principles: lawfulness, purpose limitation, data minimization, accuracy, storage limitation, integrity/confidentiality, accountability
- 7 individual rights: right to access, erasure, rectification, etc.
- Key organizational requirements
- Penalties for non-compliance

### SOC 2
- Service Organization Control Type II
- 5 Trust Service Criteria: Common Criteria, Availability, Confidentiality, Integrity, Privacy
- Common control activities (CC1-CC9)
- Security, operational, and documentation requirements

---

## ⚙️ Configuration (Optional)

The system is pre-configured to work. Optional customizations:

```bash
# Edit .env (if needed)
nano .env

# Change default model (if you have more RAM)
OLLAMA_MODEL=mistral  # Larger, better quality
OLLAMA_MODEL=neural-chat  # Smaller, faster (default)
```

---

## 🧪 Validate Everything Works

```bash
python tests/validate_setup.py
```

Should show: ✓ All 7 tests PASSED

---

## 🎓 Example Workflow

1. **Prepare PDF**
   ```bash
   cp my_document.pdf ai_compliance_agent/local_pdfs/
   ```

2. **Start services**
   ```bash
   # Terminal 1
   ollama serve
   
   # Terminal 2
   python -m ai_compliance_agent.ui_gradio
   ```

3. **Analyze document**
   - Open http://127.0.0.1:7860
   - Enter: `./ai_compliance_agent/local_pdfs/my_document.pdf`
   - Click "Analyse Document"

4. **Review results**
   - Check "Analysis" tab for compliance gaps
   - Check "Document Summary" for key points
   - Check "Sources" for referenced standards

---

## 📁 Project Structure (Ready to Go)

```
/workspaces/aiagent/
├── ai_compliance_agent/
│   ├── knowledge_base/           ← 3 sample PDFs here!
│   │   ├── ISO_27001_Standard.pdf
│   │   ├── GDPR_Standard.pdf
│   │   ├── SOC2_Standard.pdf
│   │   └── embeddings/           ← Auto-generated cache
│   ├── local_pdfs/              ← Add your PDFs here
│   ├── tmp_downloads/           ← Downloaded PDFs stored here
│   ├── agent_pipeline.py        ← Main logic (with fallback)
│   ├── ui_gradio.py             ← Web interface
│   └── kb_fallback.py           ← ✨ NEW: Fallback mode
├── tests/
│   └── validate_setup.py        ← Run to validate
├── scripts/
│   └── generate_sample_documents.py  ← ✨ NEW: PDF generator
├── QUICK_REFERENCE.md           ← Quick lookup
├── TROUBLESHOOTING_AND_BEST_PRACTICES.md  ← Detailed guide
└── setup_with_samples.sh        ← ✨ NEW: Automated setup
```

---

## 🔧 If Something Goes Wrong

### "Knowledge base is empty"
✅ **FIXED** - Now uses fallback standards automatically

### "Can't find PDF"
```bash
# Copy your PDF to local_pdfs
cp your_file.pdf ai_compliance_agent/local_pdfs/

# Then reference it in the app
./ai_compliance_agent/local_pdfs/your_file.pdf
```

### "Ollama process terminated"
```bash
# Use smaller model in .env
OLLAMA_MODEL=neural-chat

# Ensure 8GB+ RAM is free
free -h
```

---

## 💡 Pro Tips

1. **First run is slow** - Embeddings are computed and cached
   - Subsequent runs: <1 second for KB retrieval

2. **Multiple PDFs in KB** - Retrieves most relevant parts
   - Works best with 2-5 documents per domain

3. **Add your own standards** - Replace sample PDFs
   - Place them in `knowledge_base/` folder

4. **Monitor memory** - Watch LLM during analysis
   ```bash
   watch -n 1 'free -h && echo "---" && ps aux | grep ollama'
   ```

5. **Batch processing** - Coming soon!
   - Process multiple documents programmatically

---

## 📊 Next Steps

### Immediate (Test)
```bash
# 1. Start Ollama
ollama serve

# 2. Run app
python -m ai_compliance_agent.ui_gradio

# 3. Open browser and test!
http://127.0.0.1:7860
```

### Short Term (Production-Ready)
1. Replace sample PDFs with real standards
2. Run `python tests/validate_setup.py`
3. Review `TROUBLESHOOTING_AND_BEST_PRACTICES.md`
4. Configure API credentials (if using OAuth2)

### Long Term (Advanced)
- Implement batch processing
- Add custom compliance scoring
- Generate detailed reports
- Integrate with ITSM systems

---

## 🎯 What This Means for You

| Before | After |
|--------|-------|
| ❌ Error: Knowledge base empty | ✅ Auto-uses fallback standards |
| ❌ Must create PDFs manually | ✅ Sample PDFs provided |
| ❌ Confusing error messages | ✅ Graceful fallback mode |
| ❌ Hard to test without docs | ✅ Ready to test immediately! |

---

## 🚀 Ready to Go!

Everything is set up. You can now:

1. ✅ Run the web interface
2. ✅ Upload any PDF
3. ✅ Get compliance analysis
4. ✅ Replace samples when ready

**Start here**: `python -m ai_compliance_agent.ui_gradio`

Then open: `http://127.0.0.1:7860`

---

**Need help?** Check `QUICK_REFERENCE.md` or `TROUBLESHOOTING_AND_BEST_PRACTICES.md`
