#!/usr/bin/env python3
"""
Test comprehensive PDF extraction and detailed summarization
"""

from pathlib import Path
from ai_compliance_agent.pdf_extractor import extract_and_summarize_pdf

print("=" * 80)
print("🧪 COMPREHENSIVE PDF EXTRACTION TEST")
print("=" * 80)
print()

# Test with one of the sample PDFs
test_pdf = Path("./ai_compliance_agent/knowledge_base/ISO_27001_Standard.pdf")

if not test_pdf.exists():
    print(f"❌ Test PDF not found: {test_pdf}")
    exit(1)

print(f"📄 Extracting from: {test_pdf.name}")
print()

try:
    # Extract all details
    details, summary = extract_and_summarize_pdf(test_pdf)
    
    # Print summary
    print(summary)
    
    # Also show the full text
    print("\n" + "=" * 80)
    print("📖 FULL EXTRACTED TEXT")
    print("=" * 80)
    print()
    print(details["full_text"][:3000])
    if len(details["full_text"]) > 3000:
        print(f"\n... ({len(details['full_text']) - 3000} more characters)")
    
    # Save to file
    output_file = test_pdf.with_stem(test_pdf.stem + "_EXTRACTED_SUMMARY")
    with open(output_file, "w") as f:
        f.write(summary)
        f.write("\n\n")
        f.write("=" * 80)
        f.write("\nFULL TEXT:\n")
        f.write("=" * 80)
        f.write("\n\n")
        f.write(details["full_text"])
    
    print(f"\n\n💾 Full extraction saved to: {output_file}")
    print()
    print("✅ Extraction complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
