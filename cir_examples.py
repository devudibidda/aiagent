#!/usr/bin/env python3
"""
Example usage of the Vestas CIR Analysis System
"""

import logging
from pathlib import Path
from cir_system import CIRBatchProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_process_single_pdf():
    """Example 1: Process a single CIR PDF"""
    logger.info("\n=== EXAMPLE 1: Process Single PDF ===\n")
    
    processor = CIRBatchProcessor(output_dir="./cir_output_example1")
    
    # Process a single PDF
    pdf_path = "./sample_cir.pdf"  # Replace with actual path
    
    if not Path(pdf_path).exists():
        logger.warning(f"Sample PDF not found at {pdf_path}")
        logger.info("To test, place a CIR PDF at ./sample_cir.pdf")
        return
    
    result = processor.process_single_pdf(pdf_path)
    
    print("\n" + "="*60)
    print("PROCESSING RESULT")
    print("="*60)
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"CIR Number: {result['cir_number']}")
        print(f"Compliance: {result['compliance']['status']} ({result['compliance']['score']:.1f}%)")
        print(f"Text extracted: {result['text_length']} characters")
        print(f"Pages: {result['page_count']}")
        print(f"OCR Confidence: {result['ocr_confidence']:.1f}%")


def example_2_batch_process():
    """Example 2: Process all PDFs in a directory"""
    logger.info("\n=== EXAMPLE 2: Batch Process Multiple PDFs ===\n")
    
    processor = CIRBatchProcessor(output_dir="./cir_output_batch")
    
    pdf_folder = "./cir_pdfs"  # Replace with actual folder
    
    if not Path(pdf_folder).exists():
        logger.warning(f"PDF folder not found at {pdf_folder}")
        logger.info("To test, create a folder './cir_pdfs' with CIR PDFs")
        return
    
    # Define progress callback
    def progress(current, total, message):
        logger.info(f"[{current}/{total}] {message}")
    
    # Process batch
    summary = processor.process_directory(
        pdf_folder,
        progress_callback=progress
    )
    
    print("\n" + "="*60)
    print("BATCH PROCESSING SUMMARY")
    print("="*60)
    print(f"Total: {summary['total_files']}")
    print(f"Success: {summary['successfully_processed']}")
    print(f"Failed: {summary['failed']}")
    print(f"GO: {summary['go_count']}")
    print(f"NO-GO: {summary['nogo_count']}")
    
    # Get detailed report
    go_nogo = processor.get_go_nogo_report()
    print(f"\nGO Percentage: {go_nogo['go_percentage']:.1f}%")
    
    print("\nResults saved to: ./cir_output_batch/")


def example_3_programmatic_usage():
    """Example 3: Use in your own code"""
    logger.info("\n=== EXAMPLE 3: Programmatic Usage ===\n")
    
    from cir_system import extract_cir_pdf, CIRComplianceValidator
    from cir_system import create_empty_cir_document
    
    pdf_path = "./sample_cir.pdf"
    
    if not Path(pdf_path).exists():
        logger.warning(f"Sample PDF not found at {pdf_path}")
        return
    
    # Step 1: Extract text and pages
    logger.info("Step 1: Extracting text from PDF...")
    full_text, pages, ocr_confidence = extract_cir_pdf(pdf_path)
    
    print(f"\nExtracted {len(pages)} pages")
    print(f"Total text: {len(full_text)} characters")
    print(f"OCR Confidence: {ocr_confidence:.1f}%")
    
    # Step 2: Create document structure
    logger.info("Step 2: Creating document structure...")
    cir_doc = create_empty_cir_document(
        document_id="DOC-001",
        cir_number="CIR-12345",
        filename=Path(pdf_path).name,
        file_size_mb=1.0,
        page_count=len(pages)
    )
    cir_doc.full_text_content = full_text
    cir_doc.extracted_pages = pages
    cir_doc.metadata.ocr_confidence = ocr_confidence
    
    # Step 3: Validate compliance
    logger.info("Step 3: Validating compliance...")
    validator = CIRComplianceValidator()
    cir_doc.compliance = validator.validate(cir_doc)
    
    print(f"\nCompliance Status: {cir_doc.compliance.status.value}")
    print(f"Score: {cir_doc.compliance.score:.1f}%")
    print(f"Critical Issues: {len(cir_doc.compliance.critical_issues)}")
    print(f"Warnings: {len(cir_doc.compliance.warnings)}")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║    Vestas CIR Analysis System - Usage Examples            ║
║                                                            ║
║    Process thousands of CIR PDFs with OCR and            ║
║    compliance validation                                  ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("\n📝 AVAILABLE EXAMPLES:")
    print("1. Process single PDF")
    print("2. Batch process multiple PDFs")
    print("3. Programmatic usage in your code")
    
    try:
        example_1_process_single_pdf()
        # example_2_batch_process()
        # example_3_programmatic_usage()
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
