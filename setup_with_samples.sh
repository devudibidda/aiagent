#!/bin/bash

# AI Compliance Agent - Complete Setup & Sample Data Generator
# Creates sample PDFs and prepares the environment for testing

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║    AI Compliance Agent - Setup & Sample Data Generator     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Python
print_step "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
print_success "Python ready: $PYTHON_VERSION"
echo ""

# Check if reportlab is installed
print_step "Checking dependencies for PDF generation..."
python3 << 'PYTHONEOF'
try:
    import reportlab
    print("reportlab available")
except ImportError:
    print("reportlab missing")
PYTHONEOF

if python3 -c "import reportlab" 2>/dev/null; then
    print_success "reportlab available"
else
    print_warning "reportlab not found. Installing..."
    pip install -q reportlab 2>/dev/null || {
        print_error "Failed to install reportlab"
        echo "Run: pip install reportlab"
        exit 1
    }
    print_success "reportlab installed"
fi
echo ""

# Create knowledge base directory
print_step "Creating knowledge_base directory..."
mkdir -p ai_compliance_agent/knowledge_base
print_success "Directory ready"
echo ""

# Generate sample PDFs
print_step "Generating sample compliance standard PDFs..."
python3 << 'PYTHONEOF'
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from scripts.generate_sample_documents import (
        create_iso_27001_pdf,
        create_gdpr_pdf,
        create_soc2_pdf,
    )
    
    kb_dir = Path("ai_compliance_agent/knowledge_base")
    
    print("\n  Generating ISO 27001...")
    create_iso_27001_pdf(kb_dir / "ISO_27001_Standard.pdf")
    
    print("  Generating GDPR...")
    create_gdpr_pdf(kb_dir / "GDPR_Standard.pdf")
    
    print("  Generating SOC 2...")
    create_soc2_pdf(kb_dir / "SOC2_Standard.pdf")
    
    # List generated files
    pdfs = list(kb_dir.glob("*.pdf"))
    print(f"\n✓ Generated {len(pdfs)} sample PDFs:")
    for pdf in sorted(pdfs):
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"    • {pdf.name} ({size_mb:.1f} MB)")
        
except Exception as e:
    print(f"✗ Error generating PDFs: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHONEOF

if [ $? -eq 0 ]; then
    print_success "Sample PDFs generated"
else
    print_error "Failed to generate PDFs"
    exit 1
fi
echo ""

# Create/update .env if missing
print_step "Checking environment configuration..."
if [ ! -f .env ]; then
    print_warning ".env not found. Creating template..."
    cat > .env << 'EOF'
# API Configuration (optional - for OAuth2 PDF fetching)
API_BASE_URL=
TOKEN_URL=
CLIENT_ID=
CLIENT_SECRET=

# Local Paths
DOWNLOAD_DIR=./ai_compliance_agent/tmp_downloads
KNOWLEDGE_BASE_DIR=./ai_compliance_agent/knowledge_base
LOCAL_PDF_DIR=./ai_compliance_agent/local_pdfs

# Ollama Model Selection
OLLAMA_MODEL=neural-chat
# Alternative models: mistral, llama2, neural-chat (default - most memory efficient)
EOF
    print_success ".env template created"
else
    print_success ".env already exists"
fi
echo ""

# Create directories
print_step "Creating required directories..."
mkdir -p ai_compliance_agent/tmp_downloads
mkdir -p ai_compliance_agent/local_pdfs
print_success "All directories ready"
echo ""

# Install Python dependencies
print_step "Checking Python dependencies..."
pip_quiet=$(pip install --quiet -q 2>/dev/null && echo "yes" || echo "no")

if python3 -c "from ai_compliance_agent import *" 2>/dev/null; then
    print_success "Dependencies already installed"
else
    print_warning "Installing dependencies..."
    pip install -q -r ai_compliance_agent/requirements.txt 2>/dev/null || {
        print_error "Failed to install dependencies"
        echo "Run: pip install -r ai_compliance_agent/requirements.txt"
        exit 1
    }
    print_success "Dependencies installed"
fi
echo ""

# Final status
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   ✅ SETUP COMPLETE!                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "📊 Status Summary:"
echo "  ✓ Python environment ready"
echo "  ✓ Dependencies installed"
echo "  ✓ Directories created"
echo "  ✓ Sample PDFs generated (ISO 27001, GDPR, SOC 2)"
echo "  ✓ Configuration ready"
echo ""

echo "🚀 Next Steps:"
echo ""
echo "  1. Start Ollama (in a new terminal):"
echo "     ${BLUE}ollama serve${NC}"
echo ""
echo "  2. Download a model (optional, auto-pulled on first run):"
echo "     ${BLUE}ollama pull neural-chat${NC}"
echo ""
echo "  3. Validate setup:"
echo "     ${BLUE}python tests/validate_setup.py${NC}"
echo ""
echo "  4. Start the web interface:"
echo "     ${BLUE}python -m ai_compliance_agent.ui_gradio${NC}"
echo ""
echo "  5. Open browser:"
echo "     ${BLUE}http://127.0.0.1:7860${NC}"
echo ""

echo "📁 Knowledge Base Contents:"
ls -lh ai_compliance_agent/knowledge_base/*.pdf 2>/dev/null | awk '{print "     " $9 " (" $5 ")"}'
echo ""

echo "💡 Tips:"
echo "  • Sample PDFs are ready in: ai_compliance_agent/knowledge_base/"
echo "  • To use your own PDFs, add them to the knowledge_base directory"
echo "  • Run: python tests/validate_setup.py to verify everything"
echo "  • Check QUICK_REFERENCE.md for troubleshooting"
echo ""

print_success "Setup complete! Ready to analyze documents."
echo ""
