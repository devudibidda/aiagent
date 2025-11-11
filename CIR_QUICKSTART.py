#!/usr/bin/env python3
"""
VESTAS CIR ANALYSIS SYSTEM - QUICK START GUIDE

This system is designed to:
✓ Process 1000s of CIR PDFs
✓ Extract text and image data using OCR
✓ Validate compliance against Vestas standards
✓ Generate GO/NO-GO status for each document
✓ Output structured JSON format for analysis
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         VESTAS CIR ANALYSIS SYSTEM - QUICK START              ║
║                                                                ║
║  Process Change Impact Reports with OCR & Compliance Check   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝


📋 SYSTEM CAPABILITIES:
═════════════════════════════════════════════════════════════════

1. OCR TEXT EXTRACTION
   • Extract text from digital PDFs (fast)
   • Extract text from scanned PDFs (OCR with confidence)
   • Page-by-page extraction
   • Image extraction from PDFs

2. DATA EXTRACTION
   • Component identification
   • Part numbers and drawing numbers
   • Change type classification
   • Technical specifications
   • Change justification and reasoning

3. COMPLIANCE VALIDATION
   • Check required fields presence
   • Validate technical data completeness
   • Verify change documentation
   • Check approval evidence
   • Quality metrics and OCR confidence

4. COMPLIANCE STATUS
   • GO: Fully compliant (85%+ score, no critical issues)
   • NO-GO: Non-compliant (issues found)
   • Detailed scoring and issue tracking

5. BATCH PROCESSING
   • Process hundreds or thousands of PDFs
   • Progress tracking
   • Automatic result aggregation
   • JSON output for each document
   • CSV summary report
   • GO/NO-GO statistics


🚀 GETTING STARTED:
═════════════════════════════════════════════════════════════════

STEP 1: Install Dependencies
────────────────────────────
pip install gradio pypdf pdf2image pytesseract pillow

For OCR to work, also install:
sudo apt-get install tesseract-ocr poppler-utils


STEP 2: Prepare Your PDFs
────────────────────────
Place your Vestas CIR PDFs in a folder:
  mkdir cir_pdfs
  # Copy your PDF files here


STEP 3: Choose Your Method

METHOD A: Web Dashboard (Recommended for non-technical users)
─────────────────────────────────────────────────────────────
python cir_main.py

Then open: http://127.0.0.1:7860

Features:
✓ Upload folder of PDFs
✓ View processing progress
✓ See GO/NO-GO results
✓ Download JSON reports
✓ Analyze single documents
✓ View compliance scores


METHOD B: Python Script (For developers)
────────────────────────────────────────
from cir_system import CIRBatchProcessor

processor = CIRBatchProcessor(output_dir="./cir_results")
summary = processor.process_directory("./cir_pdfs")

print(f"GO: {summary['go_count']}")
print(f"NO-GO: {summary['nogo_count']}")


METHOD C: Command Line (For automation)
──────────────────────────────────────
python cir_examples.py


📊 OUTPUT FORMAT:
═════════════════════════════════════════════════════════════════

Each PDF generates JSON with:

{
  "document_id": "uuid",
  "cir_number": "CIR-12345",
  "filename": "document.pdf",
  "compliance": {
    "status": "GO",           ← GO or NO-GO
    "score": 92.5,            ← Compliance percentage
    "critical_issues": 0,
    "warnings": 2
  },
  "technical_data": {
    "component_name": "...",
    "part_number": "...",
    "drawing_number": "...",
    "revision": "..."
  },
  "change_details": {
    "change_type": "Design Change",
    "reason_for_change": "...",
    "technical_justification": "...",
    "change_owner": "..."
  },
  "full_text_content": "...",      ← Complete extracted text
  "extracted_pages": {...},         ← Page-by-page text
  "extraction_errors": [],
  "processing_notes": []
}


🔍 VALIDATION RULES:
═════════════════════════════════════════════════════════════════

GO Status Requires:
✓ CIR Number present
✓ Component identified
✓ Change type specified
✓ Technical justification provided
✓ Compliance score ≥ 85%
✓ No CRITICAL issues
✓ OCR confidence ≥ 80%

NO-GO Status Assigned For:
✗ Any CRITICAL issue found
✗ Compliance score < 85%
✗ Required fields missing
✗ Insufficient documentation


📈 BATCH PROCESSING EXAMPLE:
═════════════════════════════════════════════════════════════════

Input:  1000 CIR PDFs in ./cir_pdfs/
Output: cir_output/
        ├── batch_summary.json          (Overall statistics)
        ├── batch_summary.csv            (Excel-compatible)
        ├── all_results.json             (All documents)
        └── document_name_result.json    (Individual results)

Summary shows:
• Total processed: 1000
• Successfully: 998
• Failed: 2
• GO: 847 (84.7%)
• NO-GO: 153 (15.3%)


💻 USAGE EXAMPLES:
═════════════════════════════════════════════════════════════════

# Example 1: Single PDF
──────────────────────
from cir_system import extract_cir_pdf, CIRComplianceValidator

text, pages, confidence = extract_cir_pdf("document.pdf")
print(f"Extracted {len(pages)} pages")
print(f"Confidence: {confidence:.1f}%")


# Example 2: Batch Process
──────────────────────────
from cir_system import CIRBatchProcessor

processor = CIRBatchProcessor()
summary = processor.process_directory("./cir_pdfs")

for file in summary['files']:
    print(f"{file['filename']}: {file['status']}")


# Example 3: Custom Validation
──────────────────────────────
from cir_system import CIRComplianceValidator, CIRDocument

validator = CIRComplianceValidator()
validation = validator.validate(cir_document)

if validation.status.value == "GO":
    print("✅ Document is compliant")
else:
    print("❌ Document has issues:")
    for issue in validation.critical_issues:
        print(f"  - {issue.description}")


🔧 CONFIGURATION:
═════════════════════════════════════════════════════════════════

You can customize:

1. OCR Settings (in cir_ocr_extractor.py)
   - Use OCR for scanned PDFs: True/False
   - Tesseract path: custom path if needed

2. Compliance Rules (in cir_schema.py)
   - Minimum GO score: 85%
   - Allow warnings: True/False
   - Custom check rules

3. Output Format
   - JSON structure
   - CSV fields
   - Report format


⚠️ TROUBLESHOOTING:
═════════════════════════════════════════════════════════════════

Problem: "OCR dependencies not available"
Solution: pip install pytesseract pdf2image
          sudo apt-get install tesseract-ocr

Problem: "Very Low OCR Confidence"
Solution: Your PDF is scanned image-based
          Check if original is clear
          Consider document preprocessing

Problem: "No text extracted"
Solution: PDF may be image-based (scanned)
          Install OCR dependencies above
          Try with sample PDF first

Problem: "Processing is slow"
Solution: Normal for 1000s of PDFs
          Each PDF takes 1-5 seconds
          1000 PDFs = 15-80 minutes
          Run in background


📝 NEXT STEPS:
═════════════════════════════════════════════════════════════════

1. Test with sample PDF:
   python cir_examples.py

2. Launch dashboard:
   python cir_main.py

3. Process your PDFs:
   Point to folder containing CIRs
   Click "Process Batch"
   View results

4. Analyze JSON output:
   Open cir_output/batch_summary.json
   Review compliance scores
   Identify NO-GO documents
   Take corrective actions


✅ YOU'RE READY!
═════════════════════════════════════════════════════════════════

The system is ready to:
✓ Handle 1000s of PDFs
✓ Extract ALL text and data using OCR
✓ Validate against Vestas standards
✓ Generate GO/NO-GO compliance status
✓ Output structured JSON format

Start with: python cir_main.py

Then open: http://127.0.0.1:7860

Questions? Check cir_examples.py for code examples.
""")

# Optional: auto-launch
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--launch":
        from cir_system import launch
        launch()
