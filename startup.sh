#!/bin/bash

# AI Compliance Agent - Complete Startup Guide
# This script ensures all prerequisites are met before running the agent

set -e  # Exit on error

echo "🚀 AI Compliance Agent - Startup Initialization"
echo "================================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Python installation
echo ""
echo "📋 Checking prerequisites..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Python installed: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if .env exists
echo ""
if [ -f .env ]; then
    print_status ".env file found"
else
    print_warning ".env file not found. Creating template..."
    cat > .env << 'EOF'
# API Configuration (for OAuth2 PDF fetching)
API_BASE_URL=
TOKEN_URL=
CLIENT_ID=
CLIENT_SECRET=

# Local paths
DOWNLOAD_DIR=./tmp_downloads
KNOWLEDGE_BASE_DIR=./knowledge_base
LOCAL_PDF_DIR=./local_pdfs

# Ollama Configuration
OLLAMA_MODEL=neural-chat
# Alternative models: mistral, llama2, dolphin-mixtral
EOF
    print_warning "Template .env created. Please configure credentials if needed."
fi

# Check Ollama installation
echo ""
if command -v ollama &> /dev/null; then
    print_status "Ollama CLI installed"
else
    print_warning "Ollama not installed. Install from https://ollama.ai"
    echo "Then run: ollama serve"
fi

# Check if Ollama service is running
echo ""
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_status "Ollama service is running ✓"
    
    # Get model information
    OLLAMA_MODEL=$(grep OLLAMA_MODEL .env 2>/dev/null | cut -d'=' -f2 || echo "neural-chat")
    OLLAMA_MODEL=${OLLAMA_MODEL:-neural-chat}
    
    echo ""
    echo "Available models:"
    curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f'  - {m[\"name\"]}') for m in data.get('models', [])]" 2>/dev/null || echo "  (Could not fetch models)"
    
else
    print_error "Ollama service not running!"
    echo ""
    echo "📌 To start Ollama in another terminal, run:"
    echo "   ollama serve"
    echo ""
    read -p "Proceed anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
echo ""
echo "📁 Creating required directories..."
mkdir -p tmp_downloads
mkdir -p knowledge_base
mkdir -p local_pdfs
print_status "Directories ready"

# Check for knowledge base PDFs
echo ""
KB_COUNT=$(find knowledge_base -name "*.pdf" 2>/dev/null | wc -l)
if [ "$KB_COUNT" -gt 0 ]; then
    print_status "Found $KB_COUNT PDF(s) in knowledge_base/"
else
    print_warning "No PDFs found in knowledge_base/. Add compliance standard PDFs there."
fi

# Install Python dependencies
echo ""
echo "📦 Checking Python dependencies..."
if [ -f requirements.txt ]; then
    # Check if all packages are installed
    python3 -m pip list 2>/dev/null | grep -q "langchain" && print_status "Dependencies appear installed" || {
        print_warning "Installing dependencies..."
        python3 -m pip install --quiet -r requirements.txt
        print_status "Dependencies installed"
    }
else
    print_error "requirements.txt not found"
    exit 1
fi

# Test imports
echo ""
echo "🧪 Testing Python imports..."
python3 << 'EOF'
import sys
try:
    from ai_compliance_agent.config import get_settings
    print("✓ Config module loaded")
    
    from ai_compliance_agent.pdf_processor import PDFProcessor
    print("✓ PDF processor loaded")
    
    from ai_compliance_agent.vector_store import VectorStoreManager
    print("✓ Vector store loaded")
    
    from langchain_ollama import ChatOllama
    print("✓ Ollama integration loaded")
    
    import gradio as gr
    print("✓ Gradio loaded")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_status "All imports successful"
else
    print_error "Import test failed"
    exit 1
fi

# System resource check
echo ""
echo "💾 Checking system resources..."
python3 << 'EOF'
import psutil
import os

# RAM check
total_ram = psutil.virtual_memory().total / (1024**3)
available_ram = psutil.virtual_memory().available / (1024**3)
print(f"Available RAM: {available_ram:.1f} GB / {total_ram:.1f} GB")

if available_ram < 4:
    print("⚠ Warning: Less than 4GB RAM available. Consider closing other applications.")
elif available_ram < 8:
    print("⚠ Warning: Less than 8GB RAM available. Use neural-chat model instead of mistral.")
else:
    print("✓ Sufficient RAM for Mistral model")

# Disk space check
disk = psutil.disk_usage('/')
free_disk = disk.free / (1024**3)
print(f"Free disk space: {free_disk:.1f} GB")

if free_disk < 1:
    print("⚠ Warning: Less than 1GB disk space")
EOF

# Final status
echo ""
echo "================================================"
echo -e "${GREEN}✓ Startup check complete!${NC}"
echo ""
echo "🎯 Next steps:"
echo ""
echo "1. If Ollama is not running, start it in another terminal:"
echo "   ollama serve"
echo ""
echo "2. Download a model (if not already downloaded):"
echo "   ollama pull neural-chat"
echo ""
echo "3. Start the web interface:"
echo "   python -m ai_compliance_agent.ui_gradio"
echo ""
echo "4. Open your browser:"
echo "   http://127.0.0.1:7860"
echo ""
echo "================================================"
