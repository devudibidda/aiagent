# Troubleshooting & Best Practices Guide

## 🔴 Error: "llama runner process has terminated: signal: terminated"

### **Root Causes**
1. **Insufficient memory**: Ollama model consumes 4-8GB RAM; prompt is too large
2. **Multiple sequential LLM calls**: Each invocation keeps context in memory
3. **Timeout**: Network connectivity to Ollama service interrupted
4. **Model not loaded**: Ollama process crashed or model failed to load

### **Solutions** ✅

#### **1. Check Ollama is Running**
```bash
# Terminal 1: Start Ollama (required!)
ollama serve

# Terminal 2: Verify it's accessible
curl http://localhost:11434/api/tags
```

#### **2. Monitor Memory During Runs**
```bash
# Terminal 3: Watch system memory
watch -n 1 'free -h && echo "---" && ps aux | grep ollama'
```

#### **3. Use Lightweight Model**
```bash
# In .env, set a smaller model
OLLAMA_MODEL=neural-chat  # ~4GB instead of mistral's 7GB

# Or download it first
ollama pull neural-chat
```

#### **4. Optimize Prompt Size**
✅ **What we fixed in the code:**
- Reduced chunks from 5 to 3 (saves ~40% memory)
- Limited chunk size to 1500 chars (was unlimited)
- Capped context to 3000 chars max
- Added error handling with graceful fallbacks

#### **5. Run on Machine with More RAM**
- **Minimum**: 16GB RAM recommended
- **Optimal**: 32GB+ for 7B models like Mistral

---

## 📋 Best Practices for Production Use

### **1. Environment Configuration**
```bash
# .env file
API_BASE_URL=https://api.example.com
TOKEN_URL=https://auth.example.com/oauth/token
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
OLLAMA_MODEL=neural-chat
DOWNLOAD_DIR=./tmp_downloads
KNOWLEDGE_BASE_DIR=./knowledge_base
LOCAL_PDF_DIR=./local_pdfs
```

### **2. Pre-load Models at Startup**
```bash
# Before running the app, pre-load the model
ollama pull neural-chat
ollama pull mistral

# Or create a startup script
cat > start_app.sh << 'EOF'
#!/bin/bash
ollama serve &
OLLAMA_PID=$!
sleep 5
ollama pull neural-chat
python -m ai_compliance_agent.ui_gradio
kill $OLLAMA_PID
EOF
chmod +x start_app.sh
./start_app.sh
```

### **3. Implement Request Timeouts**
```python
# In agent_pipeline.py, add timeout handling:
from langchain_ollama import ChatOllama

self.llm = ChatOllama(
    model=self.settings.ollama_model,
    temperature=0,
    timeout=120,  # 2-minute timeout
    num_ctx=2048,  # Context window limit
)
```

### **4. Cache Embeddings Aggressively**
```python
# Already implemented in vector_store.py
# Knowledge base embeddings are cached to avoid recomputation
# First run: ~30 seconds (generates embeddings)
# Subsequent runs: <1 second (loads from disk)
```

### **5. Batch Mode for Multiple PDFs**
```python
# Future enhancement: Process queue of PDFs
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

def analyse_batch(pdf_ids: List[str], kb_path: Path, max_workers=2):
    """Process multiple PDFs concurrently with memory awareness."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(self.analyse, pdf_id, kb_path)
            for pdf_id in pdf_ids
        ]
        results = [f.result() for f in futures]
    return results
```

### **6. Structured Logging**
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)

logging.getLogger().handlers[0].setFormatter(JSONFormatter())
```

### **7. Health Check Endpoint** (Optional)
```python
# Add to ui_gradio.py for monitoring
@app.get("/health")
def health_check():
    try:
        response = self.llm.invoke("Hello")
        return {"status": "healthy", "ollama": "ready"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503
```

---

## 🔧 Debugging Tips

### **Enable Verbose Logging**
```bash
# Set debug environment variables
export LANGCHAIN_DEBUG=true
export LANGCHAIN_VERBOSE=true

python -m ai_compliance_agent.ui_gradio
```

### **Test Components Independently**
```python
# test_components.py
from ai_compliance_agent.pdf_processor import PDFProcessor
from ai_compliance_agent.vector_store import VectorStoreManager
from langchain_ollama import ChatOllama

# Test 1: PDF extraction
pdf = PDFProcessor()
result = pdf.extract(Path("test.pdf"))
print(f"Extracted {len(result.chunks)} chunks")

# Test 2: Vectorization
store_mgr = VectorStoreManager()
store = store_mgr.build_store(result.langchain_documents)
print("Vectorization successful")

# Test 3: LLM connectivity
llm = ChatOllama(model="neural-chat")
response = llm.invoke("What is compliance?")
print(f"LLM response: {response.content}")
```

### **Profile Memory Usage**
```python
# In agent_pipeline.py
import tracemalloc

def analyse_with_profiling(self, pdf_id: str, kb_path: Path):
    tracemalloc.start()
    result = self.analyse(pdf_id, kb_path)
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current: {current / 1024 / 1024:.1f} MB; Peak: {peak / 1024 / 1024:.1f} MB")
    tracemalloc.stop()
    return result
```

---

## 📊 Model Recommendations

| Model | VRAM | Speed | Quality | Recommended For |
|-------|------|-------|---------|-----------------|
| **neural-chat** | 4GB | Fast | Good | Default (memory-constrained) |
| **mistral** | 7GB | Medium | Excellent | Standard (16GB RAM) |
| **llama2** | 7GB | Medium | Excellent | Alternative |
| **dolphin-mixtral** | 45GB | Slow | Outstanding | High-end servers only |

### **Quick Start (Recommended)**
```bash
# Fastest setup
ollama pull neural-chat

# In .env
OLLAMA_MODEL=neural-chat

# Run app
python -m ai_compliance_agent.ui_gradio
```

---

## ✅ Pre-Flight Checklist

Before running the agent:

- [ ] Ollama installed and `ollama serve` running in background
- [ ] Model downloaded: `ollama pull <model>`
- [ ] `.env` file configured with API credentials
- [ ] `knowledge_base/` directory has at least one standard PDF
- [ ] At least 8GB free RAM available
- [ ] Python dependencies installed: `pip install -r requirements.txt`
- [ ] Test PDF available in `local_pdfs/` or API accessible

### **Minimal Test**
```bash
# Verify all components
python -c "
from ai_compliance_agent.config import get_settings
from langchain_ollama import ChatOllama

settings = get_settings()
print(f'✓ Settings loaded: {settings.ollama_model}')

llm = ChatOllama(model=settings.ollama_model, timeout=30)
response = llm.invoke('Hello')
print('✓ Ollama responding')

print('✓ Ready to run app!')
"
```

---

## 🚀 Performance Optimization Checklist

### **For Faster Analysis**
1. Use `neural-chat` instead of `mistral` (-30% latency)
2. Pre-cache embeddings (first run only)
3. Reduce `search_kwargs={"k": 4}` to `{"k": 2}` (trade-off: accuracy)
4. Batch documents in knowledge base (avoid 100s of PDFs)

### **For Better Accuracy**
1. Use `mistral` model instead of `neural-chat`
2. Increase context: `search_kwargs={"k": 8}`
3. Add domain-specific fine-tuning (advanced)
4. Use ensemble of multiple models (not implemented yet)

---

## 📞 Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `Connection refused: localhost:11434` | Ollama not running | `ollama serve` |
| `llama runner process terminated` | Out of memory | Use smaller model or more RAM |
| `FileNotFoundError: knowledge_base/` | KB path missing | Create directory + add PDFs |
| `ResponseError: llama2: not found` | Model not downloaded | `ollama pull llama2` |
| `Timeout waiting for response` | Prompt too large | Reduce chunk size (already done) |

---

## 📖 Additional Resources

- [Ollama Documentation](https://ollama.ai)
- [LangChain Documentation](https://python.langchain.com)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Gradio Documentation](https://gradio.app)

