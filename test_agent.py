#!/usr/bin/env python3
"""Quick test of the compliance agent"""

from pathlib import Path
from ai_compliance_agent.agent_pipeline import ComplianceAgent
from ai_compliance_agent.config import get_settings

print("=" * 60)
print("🧪 Testing AI Compliance Agent")
print("=" * 60)
print()

try:
    # Initialize
    print("1️⃣ Initializing agent...")
    settings = get_settings()
    agent = ComplianceAgent(settings)
    print("✓ Agent initialized")
    print()
    
    # Test with sample PDF
    kb_path = Path("./ai_compliance_agent/knowledge_base")
    
    if not kb_path.exists():
        print(f"❌ Knowledge base not found: {kb_path}")
        exit(1)
    
    print(f"2️⃣ Knowledge base: {kb_path}")
    pdfs = list(kb_path.glob("*.pdf"))
    print(f"✓ Found {len(pdfs)} standard PDFs")
    for pdf in pdfs:
        print(f"  - {pdf.name}")
    print()
    
    # Create a simple test document
    print("3️⃣ Creating test document...")
    test_doc_path = Path("./test_document.pdf")
    
    if not test_doc_path.exists():
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        doc = SimpleDocTemplate(str(test_doc_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph("<b>Test Document - System Security</b>", styles['Heading1']))
        story.append(Spacer(1, 0.2))
        story.append(Paragraph(
            "Our organization has implemented basic security measures:<br/>"
            "• User authentication is enabled<br/>"
            "• Data is stored on servers<br/>"
            "• Backups are performed monthly<br/>"
            "• Staff training is conducted annually<br/>",
            styles['Normal']
        ))
        
        doc.build(story)
        print(f"✓ Created test PDF: {test_doc_path}")
    print()
    
    # Run analysis
    print("4️⃣ Running compliance analysis...")
    print("   (This may take 10-30 seconds...)")
    print()
    
    result = agent.analyse(
        pdf_id=str(test_doc_path),
        knowledge_base_path=kb_path
    )
    
    print("=" * 60)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 60)
    print()
    
    print("📊 COMPLIANCE ANALYSIS:")
    print("-" * 60)
    print(result.get("analysis", "No analysis"))
    print()
    
    print("📄 DOCUMENT SUMMARY:")
    print("-" * 60)
    print(result.get("document_summary", "No summary"))
    print()
    
    print("📋 KNOWLEDGE BASE SUMMARY:")
    print("-" * 60)
    print(result.get("knowledge_base_summary", "No KB summary")[:500] + "...")
    print()
    
    print("🔗 SOURCES RETRIEVED:")
    print("-" * 60)
    sources = result.get("sources", [])
    if sources:
        for i, source in enumerate(sources[:3], 1):
            print(f"{i}. {source.get('source')} - Chunk {source.get('chunk')}")
    else:
        print("No sources retrieved")
    print()
    
    print("=" * 60)
    print("✅ TEST SUCCESSFUL!")
    print("=" * 60)
    print()
    print("🌐 Web UI available at: http://127.0.0.1:7860")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
