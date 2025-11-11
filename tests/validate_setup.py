#!/usr/bin/env python3
"""
Diagnostic test script to validate the AI Compliance Agent setup.

This script tests all components independently to identify issues.
Run this before reporting bugs!

Usage:
    python tests/validate_setup.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_config():
    """Test configuration loading."""
    print("=" * 60)
    print("🔧 TEST 1: Configuration Loading")
    print("=" * 60)
    
    try:
        from ai_compliance_agent.config import get_settings
        settings = get_settings()
        
        print(f"✓ API Base URL: {settings.api_base_url or '(None - local mode)'}")
        print(f"✓ Download Dir: {settings.download_dir}")
        print(f"✓ Knowledge Base Dir: {settings.knowledge_base_dir}")
        print(f"✓ Ollama Model: {settings.ollama_model}")
        
        # Check directories exist
        if not settings.download_dir.exists():
            print(f"  Creating {settings.download_dir}")
            settings.download_dir.mkdir(parents=True, exist_ok=True)
        if not settings.knowledge_base_dir.exists():
            print(f"  Creating {settings.knowledge_base_dir}")
            settings.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
            
        print("✓ Configuration test PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Configuration test FAILED: {e}\n")
        return False


def test_pdf_processor():
    """Test PDF processing capabilities."""
    print("=" * 60)
    print("🔧 TEST 2: PDF Processor")
    print("=" * 60)
    
    try:
        from ai_compliance_agent.pdf_processor import PDFProcessor
        from pathlib import Path
        
        processor = PDFProcessor()
        print(f"✓ PDF Processor initialized")
        
        # Check if there's a test PDF
        kb_path = Path("./ai_compliance_agent/knowledge_base")
        local_path = Path("./ai_compliance_agent/local_pdfs")
        
        test_pdf = None
        for p in [kb_path, local_path]:
            pdfs = list(p.glob("*.pdf"))
            if pdfs:
                test_pdf = pdfs[0]
                break
        
        if test_pdf:
            print(f"  Testing with: {test_pdf.name}")
            result = processor.extract(test_pdf)
            print(f"✓ Extracted {len(result.chunks)} chunks from PDF")
            print(f"✓ Generated {len(result.langchain_documents)} LangChain documents")
            print("✓ PDF Processor test PASSED\n")
            return True
        else:
            print("⚠ No test PDF found. Skipping extraction test.")
            print("✓ PDF Processor loaded successfully\n")
            return True
            
    except Exception as e:
        print(f"✗ PDF Processor test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store():
    """Test vector store capabilities."""
    print("=" * 60)
    print("🔧 TEST 3: Vector Store & Embeddings")
    print("=" * 60)
    
    try:
        from ai_compliance_agent.vector_store import VectorStoreManager
        from langchain_core.documents import Document
        
        manager = VectorStoreManager()
        print(f"✓ VectorStoreManager initialized")
        
        # Create test documents
        test_docs = [
            Document(page_content="Compliance requirement: All systems must have authentication"),
            Document(page_content="Security standard: Data must be encrypted at rest"),
        ]
        
        print("  Building test vector store...")
        store = manager.build_store(test_docs)
        print(f"✓ Vector store built with {len(test_docs)} documents")
        
        # Test retrieval
        results = store.similarity_search("authentication requirement", k=1)
        print(f"✓ Retrieved {len(results)} relevant documents")
        
        print("✓ Vector Store test PASSED\n")
        return True
        
    except Exception as e:
        print(f"✗ Vector Store test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_ollama_connection():
    """Test Ollama service connectivity."""
    print("=" * 60)
    print("🔧 TEST 4: Ollama Service Connection")
    print("=" * 60)
    
    try:
        import requests
        
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            import json
            models = json.loads(response.text)
            print(f"✓ Ollama service is running")
            print(f"✓ Available models: {len(models.get('models', []))}")
            for model in models.get('models', [])[:5]:  # Show first 5
                print(f"  - {model.get('name')}")
            return True
        else:
            print(f"✗ Unexpected response from Ollama: {response.status_code}\n")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama at localhost:11434")
        print("  Make sure to run: ollama serve\n")
        return False
    except Exception as e:
        print(f"✗ Ollama connection test FAILED: {e}\n")
        return False


def test_llm_inference():
    """Test LLM inference capability."""
    print("=" * 60)
    print("🔧 TEST 5: LLM Inference")
    print("=" * 60)
    
    try:
        from ai_compliance_agent.config import get_settings
        from langchain_ollama import ChatOllama
        
        settings = get_settings()
        
        print(f"  Initializing {settings.ollama_model}...")
        llm = ChatOllama(
            model=settings.ollama_model,
            temperature=0,
            timeout=30,
        )
        
        print("  Running test inference...")
        response = llm.invoke("What is compliance?")
        
        answer = getattr(response, "content", None) or str(response)
        print(f"✓ LLM Response: {answer[:100]}...")
        print("✓ LLM Inference test PASSED\n")
        return True
        
    except Exception as e:
        print(f"✗ LLM Inference test FAILED: {e}")
        print("  Make sure Ollama is running and the model is downloaded.\n")
        return False


def test_system_resources():
    """Test system resource availability."""
    print("=" * 60)
    print("🔧 TEST 6: System Resources")
    print("=" * 60)
    
    try:
        import psutil
        
        # RAM check
        total_ram = psutil.virtual_memory().total / (1024**3)
        available_ram = psutil.virtual_memory().available / (1024**3)
        
        print(f"✓ Total RAM: {total_ram:.1f} GB")
        print(f"✓ Available RAM: {available_ram:.1f} GB")
        
        if available_ram < 4:
            print("  ⚠ Warning: Less than 4GB RAM. Consider using 'neural-chat' model.")
        elif available_ram >= 8:
            print("  ✓ Sufficient RAM for all models")
        
        # Disk space check
        disk = psutil.disk_usage('/')
        free_disk = disk.free / (1024**3)
        print(f"✓ Free disk space: {free_disk:.1f} GB")
        
        if free_disk < 1:
            print("  ⚠ Warning: Low disk space (<1GB)")
        
        print("✓ System Resources test PASSED\n")
        return True
        
    except Exception as e:
        print(f"✗ System Resources test FAILED: {e}\n")
        return False


def test_imports():
    """Test all required imports."""
    print("=" * 60)
    print("🔧 TEST 7: Python Dependencies")
    print("=" * 60)
    
    imports = {
        "gradio": "gr",
        "langchain": None,
        "langchain_community": None,
        "langchain_core": None,
        "langchain_huggingface": None,
        "langchain_ollama": "ChatOllama",
        "requests": None,
        "dotenv": "load_dotenv",
        "pypdf": None,
        "faiss": None,
        "sentence_transformers": None,
    }
    
    failed = []
    for module, item in imports.items():
        try:
            if item:
                exec(f"from {module} import {item}")
            else:
                __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n✗ Missing imports: {', '.join(failed)}")
        print("  Run: pip install -r requirements.txt\n")
        return False
    else:
        print("\n✓ Python Dependencies test PASSED\n")
        return True


def main():
    """Run all diagnostic tests."""
    print("\n" + "=" * 60)
    print("🔍 AI Compliance Agent - Setup Validation")
    print("=" * 60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("System Resources", test_system_resources),
        ("PDF Processor", test_pdf_processor),
        ("Vector Store", test_vector_store),
        ("Ollama Service", test_ollama_connection),
        ("LLM Inference", test_llm_inference),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except KeyboardInterrupt:
            print("\n\n⚠ Tests interrupted by user\n")
            sys.exit(1)
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run the agent.\n")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above for details.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
