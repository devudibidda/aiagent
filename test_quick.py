#!/usr/bin/env python3
"""
Quick test to verify the AI Compliance Agent works end-to-end.
Creates a minimal test PDF and analyzes it.
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_test_pdf():
    """Create a minimal test PDF for quick testing."""
    test_pdf = Path("ai_compliance_agent/local_pdfs/test_document.pdf")
    test_pdf.parent.mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(str(test_pdf), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Minimal content to avoid memory issues
    story.append(Paragraph("Test Document for Compliance Analysis", styles['Heading1']))
    story.append(Spacer(1, 0.3))
    story.append(Paragraph("This document contains user data and needs encryption.", styles['Normal']))
    story.append(Spacer(1, 0.2))
    story.append(Paragraph("Current state: No encryption implemented. Data stored in plain text.", styles['Normal']))
    story.append(Spacer(1, 0.2))
    story.append(Paragraph("We have admin access controls but no MFA.", styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created test PDF: {test_pdf}")
    return test_pdf

def test_agent():
    """Test the agent with minimal prompts."""
    print("\n" + "="*60)
    print("Testing AI Compliance Agent")
    print("="*60 + "\n")
    
    # Create test PDF
    test_pdf = create_test_pdf()
    
    # Import agent
    print("Importing agent...")
    try:
        from ai_compliance_agent.agent_pipeline import ComplianceAgent
        from ai_compliance_agent.config import get_settings
        print("✓ Imports successful")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    # Initialize
    print("\nInitializing agent...")
    try:
        settings = get_settings()
        agent = ComplianceAgent(settings)
        print("✓ Agent initialized")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False
    
    # Run analysis
    print("\nRunning compliance analysis...")
    print("(This will use Ollama - ensure 'ollama serve' is running)")
    print("-" * 60)
    
    try:
        result = agent.analyse(
            pdf_id=str(test_pdf),
            knowledge_base_path=Path("ai_compliance_agent/knowledge_base")
        )
        print("✓ Analysis completed!\n")
        
        # Print results
        print("RESULTS:")
        print("-" * 60)
        print(f"\nDocument Summary:\n{result['document_summary']}\n")
        print(f"Knowledge Base:\n{result['knowledge_base_summary']}\n")
        print(f"Analysis:\n{result['analysis']}\n")
        
        if result['sources']:
            print(f"Sources used: {len(result['sources'])} documents")
            for i, source in enumerate(result['sources'][:3], 1):
                print(f"  {i}. {source.get('source', 'unknown')}")
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Agent is working!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)
