"""
CIR Batch Processor
Process thousands of CIR PDFs in batch with progress tracking
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime
import uuid

from .cir_schema import CIRDocument, cir_to_dict, create_empty_cir_document
from .cir_ocr_extractor import extract_cir_pdf
from .cir_validator import CIRComplianceValidator

logger = logging.getLogger(__name__)


class CIRBatchProcessor:
    """Process multiple CIR PDFs in batch"""
    
    def __init__(self, output_dir: str = "./cir_output"):
        """Initialize batch processor"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.validator = CIRComplianceValidator()
        self.results: List[Dict] = []
        self.summary: Dict = {
            "total_files": 0,
            "successfully_processed": 0,
            "failed": 0,
            "go_count": 0,
            "nogo_count": 0,
            "start_time": None,
            "end_time": None,
            "files": []
        }
    
    def process_directory(
        self,
        pdf_directory: str,
        progress_callback: Optional[Callable] = None,
        pattern: str = "*.pdf"
    ) -> Dict:
        """
        Process all PDFs in a directory
        
        Args:
            pdf_directory: Path to folder containing PDFs
            progress_callback: Optional callback for progress (current, total)
            pattern: File pattern to match (default: *.pdf)
        
        Returns:
            Summary dictionary with results
        """
        pdf_dir = Path(pdf_directory)
        
        if not pdf_dir.exists():
            logger.error(f"Directory not found: {pdf_directory}")
            return self.summary
        
        # Find all PDFs
        pdf_files = list(pdf_dir.glob(pattern))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        self.summary["total_files"] = len(pdf_files)
        self.summary["start_time"] = datetime.now().isoformat()
        
        # Process each PDF
        for idx, pdf_file in enumerate(pdf_files, 1):
            if progress_callback:
                progress_callback(idx, len(pdf_files), f"Processing: {pdf_file.name}")
            
            try:
                logger.info(f"[{idx}/{len(pdf_files)}] Processing: {pdf_file.name}")
                result = self.process_single_pdf(str(pdf_file))
                self.results.append(result)
                
                # Update summary
                if result["status"] == "success":
                    self.summary["successfully_processed"] += 1
                    
                    if result["compliance"]["status"] == "GO":
                        self.summary["go_count"] += 1
                    else:
                        self.summary["nogo_count"] += 1
                    
                    self.summary["files"].append({
                        "filename": result["filename"],
                        "cir_number": result["cir_number"],
                        "status": result["compliance"]["status"],
                        "score": result["compliance"]["score"]
                    })
                else:
                    self.summary["failed"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
                self.summary["failed"] += 1
        
        self.summary["end_time"] = datetime.now().isoformat()
        
        # Save results
        self._save_results()
        
        logger.info(f"Batch processing complete: {self.summary['successfully_processed']}/{len(pdf_files)} successful")
        
        return self.summary
    
    def process_single_pdf(self, pdf_path: str) -> Dict:
        """
        Process single PDF and return structured result
        
        Returns:
            Dictionary with extraction and compliance data
        """
        try:
            pdf_file = Path(pdf_path)
            
            if not pdf_file.exists():
                return {
                    "status": "error",
                    "filename": pdf_file.name,
                    "error": "File not found"
                }
            
            # Extract metadata
            file_size_mb = pdf_file.stat().st_size / (1024 * 1024)
            
            # Generate IDs
            document_id = str(uuid.uuid4())
            cir_number = self._extract_cir_number(pdf_file.name)
            
            # Extract text and images
            logger.info(f"Extracting text from {pdf_file.name}")
            full_text, pages, ocr_confidence = extract_cir_pdf(str(pdf_file))
            
            # Create CIR document
            cir_doc = create_empty_cir_document(
                document_id=document_id,
                cir_number=cir_number,
                filename=pdf_file.name,
                file_size_mb=file_size_mb,
                page_count=len(pages)
            )
            
            # Update with extracted content
            cir_doc.full_text_content = full_text
            cir_doc.extracted_pages = pages
            cir_doc.metadata.ocr_confidence = ocr_confidence
            
            # Extract and populate technical data
            self._populate_technical_data(cir_doc)
            
            # Extract and populate change details
            self._populate_change_details(cir_doc)
            
            # Validate compliance
            logger.info(f"Validating compliance for {pdf_file.name}")
            cir_doc.compliance = self.validator.validate(cir_doc)
            
            # Convert to dictionary
            result = {
                "status": "success",
                "filename": pdf_file.name,
                "document_id": document_id,
                "cir_number": cir_number,
                "extraction_timestamp": datetime.now().isoformat(),
                "file_size_mb": file_size_mb,
                "page_count": len(pages),
                "ocr_confidence": ocr_confidence,
                "text_length": len(full_text),
                "compliance": {
                    "status": cir_doc.compliance.status.value,
                    "score": cir_doc.compliance.score,
                    "passed_checks": cir_doc.compliance.passed_checks,
                    "failed_checks": cir_doc.compliance.failed_checks,
                    "critical_issues": len(cir_doc.compliance.critical_issues),
                    "warnings": len(cir_doc.compliance.warnings)
                },
                "document": cir_to_dict(cir_doc)
            }
            
            # Save individual JSON
            self._save_single_result(pdf_file.stem, result)
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}", exc_info=True)
            return {
                "status": "error",
                "filename": Path(pdf_path).name,
                "error": str(e)
            }
    
    def _extract_cir_number(self, filename: str) -> str:
        """Extract CIR number from filename"""
        import re
        
        # Look for patterns like CIR-1234 or CIR_1234
        match = re.search(r'CIR[_-]?(\d+)', filename, re.IGNORECASE)
        if match:
            return f"CIR-{match.group(1)}"
        
        # Default to filename without extension
        return Path(filename).stem
    
    def _populate_technical_data(self, cir_doc: CIRDocument):
        """Extract and populate technical data from text"""
        text = cir_doc.full_text_content.lower()
        
        # Try to extract component name (usually in title or first lines)
        lines = cir_doc.full_text_content.split('\n')
        for line in lines[:20]:
            if line.strip() and len(line) > 5:
                if not cir_doc.technical_data.component_name:
                    cir_doc.technical_data.component_name = line.strip()[:100]
                break
        
        # Look for part number
        import re
        part_match = re.search(r'part\s*(?:number|#|no\.?)[:\s]*([A-Z0-9\-\.]+)', text)
        if part_match:
            cir_doc.technical_data.part_number = part_match.group(1)
        
        # Look for drawing number
        draw_match = re.search(r'drawing\s*(?:number|#|no\.?)[:\s]*([A-Z0-9\-\.]+)', text)
        if draw_match:
            cir_doc.technical_data.drawing_number = draw_match.group(1)
        
        # Look for revision
        rev_match = re.search(r'revision\s*(?:number|#|rev\.?|:)?\s*([A-Z0-9]+)', text)
        if rev_match:
            cir_doc.technical_data.revision = rev_match.group(1)
    
    def _populate_change_details(self, cir_doc: CIRDocument):
        """Extract and populate change details from text"""
        text = cir_doc.full_text_content.lower()
        
        # Look for change type
        if "design" in text:
            cir_doc.change_details.change_type = "Design Change"
        elif "material" in text:
            cir_doc.change_details.change_type = "Material Change"
        elif "process" in text:
            cir_doc.change_details.change_type = "Process Change"
        
        # Extract first substantial paragraph as reason/description
        paragraphs = [p.strip() for p in cir_doc.full_text_content.split('\n\n') if p.strip()]
        if paragraphs:
            for p in paragraphs:
                if len(p) > 50:
                    if not cir_doc.change_details.reason_for_change:
                        cir_doc.change_details.reason_for_change = p[:200]
                    if not cir_doc.change_details.technical_justification:
                        cir_doc.change_details.technical_justification = p[:500]
                    break
    
    def _save_single_result(self, stem: str, result: Dict):
        """Save individual PDF result to JSON"""
        try:
            output_file = self.output_dir / f"{stem}_result.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Saved result: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save result: {e}")
    
    def _save_results(self):
        """Save all results and summary"""
        try:
            # Save summary
            summary_file = self.output_dir / "batch_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(self.summary, f, indent=2)
            logger.info(f"Saved summary: {summary_file}")
            
            # Save detailed results
            results_file = self.output_dir / "all_results.json"
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Saved results: {results_file}")
            
            # Save CSV summary
            self._save_csv_summary()
        
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def _save_csv_summary(self):
        """Save summary as CSV for easy analysis"""
        try:
            import csv
            
            csv_file = self.output_dir / "batch_summary.csv"
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "filename", "cir_number", "compliance_status", "score",
                    "passed_checks", "failed_checks", "critical_issues"
                ])
                writer.writeheader()
                
                for result in self.results:
                    if result["status"] == "success":
                        writer.writerow({
                            "filename": result["filename"],
                            "cir_number": result["cir_number"],
                            "compliance_status": result["compliance"]["status"],
                            "score": f"{result['compliance']['score']:.1f}",
                            "passed_checks": result["compliance"]["passed_checks"],
                            "failed_checks": result["compliance"]["failed_checks"],
                            "critical_issues": result["compliance"]["critical_issues"]
                        })
            
            logger.info(f"Saved CSV summary: {csv_file}")
        
        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")
    
    def get_summary(self) -> Dict:
        """Get processing summary"""
        return self.summary
    
    def get_go_nogo_report(self) -> Dict:
        """Get GO/NO-GO report"""
        go_files = [f for f in self.summary["files"] if f["status"] == "GO"]
        nogo_files = [f for f in self.summary["files"] if f["status"] == "NO-GO"]
        
        return {
            "total": len(self.summary["files"]),
            "go": len(go_files),
            "nogo": len(nogo_files),
            "go_percentage": (len(go_files) / len(self.summary["files"]) * 100) if self.summary["files"] else 0,
            "go_files": go_files,
            "nogo_files": nogo_files
        }
