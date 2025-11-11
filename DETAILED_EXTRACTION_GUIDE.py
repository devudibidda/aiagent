#!/usr/bin/env python3
"""
USAGE GUIDE - Extract All PDF Details & Get Comprehensive Summary
"""

examples = """
╔════════════════════════════════════════════════════════════╗
║          📖 HOW TO EXTRACT ALL PDF DETAILS                ║
╚════════════════════════════════════════════════════════════╝

🎯 WHAT YOU GET WHEN YOU UPLOAD A PDF:

  1. FULL DOCUMENT TEXT
     └─ Every word from every page

  2. METADATA
     ├─ Filename
     ├─ File size in KB
     ├─ Number of pages
     ├─ Author
     └─ Title

  3. STATISTICS
     ├─ Total word count
     ├─ Character count
     └─ Page breakdown

  4. STRUCTURE
     ├─ All sections identified
     ├─ Headers extracted
     └─ Content hierarchy

  5. KEY INFORMATION
     ├─ Bullet points
     ├─ Numbered items
     └─ Important statements

  6. COMPLIANCE ANALYSIS
     ├─ Gaps identified
     ├─ Alignment areas
     └─ Relevant standards

════════════════════════════════════════════════════════════

🚀 3 WAYS TO USE:

METHOD 1: WEB INTERFACE (Easiest)
═══════════════════════════════════

  Start the app:
  $ python -m ai_compliance_agent.ui_gradio

  Then:
  1. Open: http://127.0.0.1:7860
  2. Click "Analyse Document"
  3. Enter PDF path or upload
  4. Click "Analyse Document"
  5. View results in tabs:
     - Analysis: Compliance gaps
     - Document Summary: Full extraction
     - Knowledge Base Summary: Standards overview
     - Sources: Retrieved references

  → You see comprehensive summary with all details


METHOD 2: PYTHON SCRIPT
═══════════════════════

  from ai_compliance_agent.pdf_extractor import extract_and_summarize_pdf
  
  # Extract everything
  details, summary = extract_and_summarize_pdf("your_document.pdf")
  
  # Get formatted summary
  print(summary)
  
  # Or access individual parts:
  print("Full Text:")
  print(details["full_text"])
  
  print("\nMetadata:")
  print(details["metadata"])
  
  print("\nSections:")
  for section in details["sections"]:
      print(f"- {section['title']}")
  
  print("\nKey Points:")
  for point in details["key_points"]:
      print(f"• {point}")


METHOD 3: COMMAND LINE
═════════════════════

  python ai_compliance_agent/pdf_extractor.py your_document.pdf
  
  Outputs formatted summary to console
  Also saves to: your_document.summary.txt


METHOD 4: VIA AGENT
═══════════════════

  from ai_compliance_agent.agent_pipeline import ComplianceAgent
  from pathlib import Path
  
  agent = ComplianceAgent()
  result = agent.analyse(
      pdf_id="your_document.pdf",
      knowledge_base_path=Path("./ai_compliance_agent/knowledge_base")
  )
  
  # Get everything:
  print(result["document_summary"])  # Full extraction
  print(result["full_text"])         # Raw text
  print(result["analysis"])          # Compliance analysis
  print(result["pdf_details"])       # All details dict

════════════════════════════════════════════════════════════

📊 SAMPLE EXTRACTION OUTPUT:

  ┌─ METADATA ────────────────────────────┐
  │ Filename: contract.pdf                │
  │ File Size: 245.3 KB                   │
  │ Pages: 12                             │
  │ Author: John Smith                    │
  │ Title: Service Agreement 2024         │
  └───────────────────────────────────────┘

  ┌─ STATISTICS ──────────────────────────┐
  │ Total Words: 8,342                    │
  │ Avg per Page: 695 words               │
  │ Avg per Page: 5,234 characters        │
  └───────────────────────────────────────┘

  ┌─ SECTIONS (Sample) ───────────────────┐
  │ 1. Service Agreement                  │
  │ 2. Definitions and Interpretation     │
  │ 3. Services to be Provided            │
  │ 4. Payment Terms                      │
  │ 5. Confidentiality                    │
  │ 6. Liability                          │
  │ 7. Term and Termination               │
  │ 8. General Provisions                 │
  └───────────────────────────────────────┘

  ┌─ KEY POINTS (Sample) ─────────────────┐
  │ • Service commencement date: Jan 1    │
  │ • Confidentiality period: 5 years     │
  │ • Liability cap: $100,000             │
  │ • Termination notice: 30 days         │
  │ • Payment terms: Net 30               │
  └───────────────────────────────────────┘

════════════════════════════════════════════════════════════

💡 REAL-WORLD EXAMPLES:

Example 1: Extract contract details
──────────────────────────────────

  from ai_compliance_agent.pdf_extractor import extract_and_summarize_pdf
  
  contract = extract_and_summarize_pdf("contract.pdf")[0]
  
  print(f"Contract: {contract['metadata']['title']}")
  print(f"Author: {contract['metadata']['author']}")
  print(f"Pages: {contract['metadata']['page_count']}")
  print(f"Words: {contract['word_count']}")
  
  for section in contract['sections']:
      print(f"\\n{section['title']}")
      print(section['content'][:200] + "...")


Example 2: Find all clauses (key points)
─────────────────────────────────────────

  _, summary = extract_and_summarize_pdf("agreement.pdf")
  
  # Get all bullet points / numbered items
  details, _ = extract_and_summarize_pdf("agreement.pdf")
  
  print("All clauses and provisions:")
  for i, point in enumerate(details['key_points'], 1):
      print(f"{i}. {point}")


Example 3: Analyze compliance
──────────────────────────────

  from ai_compliance_agent.agent_pipeline import ComplianceAgent
  from pathlib import Path
  
  agent = ComplianceAgent()
  result = agent.analyse(
      pdf_id="policy.pdf",
      knowledge_base_path=Path("./ai_compliance_agent/knowledge_base")
  )
  
  print("DOCUMENT CONTENT:")
  print(result["document_summary"])
  
  print("\\nCOMPLIANCE ANALYSIS:")
  print(result["analysis"])
  
  print("\\nRELEVANT STANDARDS:")
  for source in result["sources"]:
      print(f"- {source['source']}")

════════════════════════════════════════════════════════════

✅ DATA STRUCTURE RETURNED:

  {
      "metadata": {
          "filename": str,
          "file_size_kb": float,
          "page_count": int,
          "author": str,
          "title": str,
          "created": datetime,
          "modified": datetime,
      },
      "full_text": str,  # Complete document text
      "pages": [
          {
              "page_number": int,
              "text": str,
              "char_count": int,
              "word_count": int,
          },
          ...
      ],
      "word_count": int,
      "sections": [
          {
              "title": str,
              "content": str,
          },
          ...
      ],
      "key_points": [str, str, ...],  # Extracted bullet points
  }

════════════════════════════════════════════════════════════

🎯 YOUR USE CASES SOLVED:

  ✓ Extract ALL text from PDF
    → details["full_text"]

  ✓ Get document metadata
    → details["metadata"]

  ✓ Find all sections
    → details["sections"]

  ✓ Get key points
    → details["key_points"]

  ✓ Page breakdown
    → details["pages"]

  ✓ Get statistics
    → word_count, character counts

  ✓ Compliance analysis
    → result["analysis"]

  ✓ Formatted summary
    → result["document_summary"]

════════════════════════════════════════════════════════════

🚀 START NOW:

  Quick Test:
  $ python test_extraction.py

  Full Test:
  $ python test_agent.py

  Web UI:
  $ python -m ai_compliance_agent.ui_gradio
  → Open: http://127.0.0.1:7860

════════════════════════════════════════════════════════════

📝 NOTES:

  • All PDFs are extracted completely
  • No data is lost
  • Sections automatically identified
  • Key points extracted
  • All available in structured format
  • Fast and reliable
  • No external API calls
  • Everything local

════════════════════════════════════════════════════════════

✅ YOU'RE ALL SET!

Your system now:
  ✓ Extracts complete PDF text
  ✓ Identifies all sections
  ✓ Extracts all key points
  ✓ Provides document metadata
  ✓ Analyzes for compliance
  ✓ Shows everything you need
  ✓ Works via UI or code
"""

print(examples)
