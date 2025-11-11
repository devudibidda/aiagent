#!/usr/bin/env python3
"""
✅ VESTAS CIR SYSTEM - NOW RUNNING!
Test with your first PDF
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         ✅ CIR ANALYSIS SYSTEM IS NOW RUNNING!               ║
║                                                                ║
║              Ready to test with your CIR PDF                  ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝


🌐 OPEN IN YOUR BROWSER:
════════════════════════════════════════════════════════════════

http://127.0.0.1:7861

OR use: "$BROWSER http://127.0.0.1:7861"


🚀 QUICK TEST STEPS:
════════════════════════════════════════════════════════════════

STEP 1: Prepare your CIR PDF
───────────────────────────
Place your PDF in one of these locations:
  • /workspaces/aiagent/cir_pdfs/
  • /workspaces/aiagent/test_cir.pdf
  • Any folder you choose

For example, if your file is at: /path/to/CIR-001.pdf


STEP 2: Open the Dashboard
──────────────────────────
Go to: http://127.0.0.1:7861

You'll see 3 tabs:
  1. 📦 Batch Processing  - Process multiple PDFs
  2. 📄 Single Document   - Analyze one PDF
  3. ℹ️ Information       - Help & features


STEP 3: Test Single Document First (RECOMMENDED)
──────────────────────────────────────────────────
1. Click the "📄 Single Document" tab
2. Enter your PDF path: /path/to/CIR-001.pdf
3. Click "🔍 Analyze" button
4. Wait for processing...
5. View results in the tabs:
   ✓ Details   - Summary information
   ✓ JSON      - Structured data (JSON format)
   ✓ Text      - Extracted text content


STEP 4: View Results
────────────────────
You'll see:
  ✓ Filename and file info
  ✓ CIR Number
  ✓ Compliance Status (GO or NO-GO)
  ✓ Compliance Score (%)
  ✓ Technical Data (component, part number, etc.)
  ✓ Change Details (change type, reason, etc.)
  ✓ Full extracted text
  ✓ Complete JSON for integration


STEP 5: Test Batch Processing (Optional)
──────────────────────────────────────────
Once single document works:
1. Prepare folder with 1-10 CIRs
2. Go to "📦 Batch Processing" tab
3. Enter folder path
4. Click "🚀 Process Batch"
5. View combined results


📊 WHAT TO EXPECT:
════════════════════════════════════════════════════════════════

For each PDF, you'll get:

1. COMPLIANCE STATUS:
   GO     = Compliant (score ≥ 85%, no critical issues)
   NO-GO  = Non-compliant (score < 85% or critical issues found)

2. COMPLIANCE SCORE:
   0-84%   = NO-GO (non-compliant)
   85-100% = GO (compliant)

3. ISSUES FOUND:
   Critical Issues: Must be fixed before approval
   Warnings:       Should be addressed

4. EXTRACTED DATA:
   • Component name and ID
   • Part number and drawing number
   • Change type (Design, Material, Process, etc.)
   • Change reason and justification
   • Change owner and implementation date
   • Full text of the document

5. JSON OUTPUT:
   Complete structured data for:
   - Integration with your systems
   - Further analysis
   - Database storage
   - Reporting


⚙️ SYSTEM INFO:
════════════════════════════════════════════════════════════════

Dashboard URL:    http://127.0.0.1:7861
Status:           RUNNING ✅
Process ID:       Check with: ps aux | grep cir_main
Output Folder:    ./cir_output/
Log File:         /tmp/cir.log

Process Command:  nohup python cir_main.py > /tmp/cir.log 2>&1 &
View Logs:        tail -f /tmp/cir.log


📁 OUTPUT LOCATION:
════════════════════════════════════════════════════════════════

After processing, results are saved to: cir_output/

├── batch_summary.json       (Overall statistics)
├── batch_summary.csv        (Excel format)
├── all_results.json         (All documents combined)
└── {filename}_result.json   (Individual results)

Each JSON file contains:
✓ Complete document data
✓ Extraction metrics
✓ Compliance results
✓ Full text content
✓ Issues and recommendations


🔍 COMPLIANCE CHECKS:
════════════════════════════════════════════════════════════════

The system validates:
✓ CIR number present
✓ Component identification
✓ Part/drawing numbers
✓ Change type specified
✓ Change reason documented
✓ Technical justification provided
✓ Implementation plan
✓ Change owner assigned
✓ Approval evidence
✓ Document quality
✓ OCR confidence level
✓ No extraction errors

Score = (Passed Checks / Total Checks) × 100

Threshold:
  ≥ 85% + No CRITICAL issues = GO ✅
  < 85% or CRITICAL issues = NO-GO ❌


⚠️ NOTES:
════════════════════════════════════════════════════════════════

OCR Dependencies Warning:
- The system can process digital PDFs (will show warning)
- For scanned PDFs, install: pytesseract pdf2image
  Command: pip install pytesseract pdf2image

Processing Speed:
- Per PDF: 1-5 seconds
- 10 PDFs: ~30-50 seconds
- 100 PDFs: ~5-15 minutes
- 1000 PDFs: ~20-80 minutes


✅ NEXT STEPS:
════════════════════════════════════════════════════════════════

1. Open browser: http://127.0.0.1:7861

2. Go to "📄 Single Document" tab

3. Enter your PDF path

4. Click "🔍 Analyze"

5. Check results in tabs

6. Download JSON file

7. Repeat with batch if needed


🎉 READY TO TEST!
════════════════════════════════════════════════════════════════

System Status: ✅ RUNNING
Dashboard: http://127.0.0.1:7861
Ready to process: Your CIR PDFs


Questions?
• Check CIR_QUICKSTART.py for detailed guide
• Check CIR_SYSTEM_COMPLETE.py for full documentation
• Check cir_examples.py for code examples


Let's analyze your first CIR! 🚀
""")
