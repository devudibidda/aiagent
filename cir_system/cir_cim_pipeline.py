"""
CIR-CIM Analysis Pipeline
Orchestrates end-to-end compliance analysis workflow
"""

import logging
import json
from typing import List, Dict, Any, Tuple
from pathlib import Path

from .cim_analyzer import CIMDocumentAnalyzer
from .cir_advanced_extractor import AdvancedCIRExtractor
from .compliance_matcher import ComplianceMatcher

logger = logging.getLogger(__name__)


class CIRCIMAnalysisPipeline:
    """
    End-to-end pipeline for analyzing CIR documents against CIM requirements
    
    Workflow:
    1. Analyze CIM document to extract compliance requirements
    2. Extract metadata and evidence from CIR document
    3. Match CIR evidence against CIM requirements
    4. Generate compliance report
    """
    
    def __init__(self):
        self.cim_analyzer = CIMDocumentAnalyzer()
        self.cir_extractor = AdvancedCIRExtractor()
        self.compliance_matcher = ComplianceMatcher()
    
    def analyze_pair(
        self,
        cir_pdf_path: str,
        cim_pdf_path: str,
        output_json: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a CIR document against a CIM document
        
        Args:
            cir_pdf_path: Path to CIR PDF
            cim_pdf_path: Path to CIM PDF
            output_json: Save results to JSON file
        
        Returns:
            Comprehensive analysis results
        """
        
        logger.info(f"Starting analysis: CIR={cir_pdf_path}, CIM={cim_pdf_path}")
        
        try:
            # Step 1: Extract CIM requirements
            logger.info("Extracting CIM requirements...")
            cim_text = self._extract_pdf_text(cim_pdf_path)
            cim_analysis = self.cim_analyzer.analyze_cim_document(cim_text)
            
            cim_requirements = [
                {
                    "id": req.id,
                    "title": req.title,
                    "type": req.requirement_type,
                    "description": req.description,
                    "severity": req.severity,
                    "components": req.applicable_components,
                    "expected_evidence": req.expected_evidence
                }
                for req in cim_analysis.requirements
            ]
            
            logger.info(f"Extracted {len(cim_requirements)} CIM requirements")
            
            # Step 2: Extract CIR metadata and content
            logger.info("Extracting CIR metadata and content...")
            cir_text = self._extract_pdf_text(cir_pdf_path)
            cir_metadata = self.cir_extractor.extract_metadata(cir_text)
            
            logger.info(f"Extracted {len(cir_metadata.all_fields)} CIR metadata fields")
            
            # Step 3: Assess compliance
            logger.info("Assessing compliance...")
            evidence_list, summary = self.compliance_matcher.assess_compliance(
                cir_text=cir_text,
                cir_metadata=cir_metadata.all_fields,
                cim_requirements=cim_requirements,
                cim_metadata=cim_analysis.__dict__
            )
            
            # Step 4: Generate comprehensive results
            results = {
                "cir_path": str(cir_pdf_path),
                "cim_path": str(cim_pdf_path),
                "analysis_timestamp": str(Path(__file__).parent),
                "cir_metadata": cir_metadata.all_fields,
                "cir_metadata_sources": cir_metadata.field_sources,
                "cim_case_id": cim_analysis.case_id,
                "cim_affected_components": cim_analysis.affected_components,
                "cim_failure_modes": cim_analysis.failure_modes,
                "cim_requirements": cim_requirements,
                "compliance_evidence": [
                    {
                        "requirement_id": e.requirement_id,
                        "requirement_title": e.requirement_title,
                        "status": e.status.value,
                        "evidence_found": e.evidence_found,
                        "expected_evidence": e.expected_evidence,
                        "comments": e.comments,
                        "confidence_score": e.confidence_score,
                        "visual_evidence": e.visual_evidence
                    }
                    for e in evidence_list
                ],
                "compliance_summary": summary,
                "go_nogo": summary.get("go_nogo", "NO-GO"),
                "compliance_score": summary.get("compliance_score", 0.0)
            }
            
            # Save JSON if requested
            if output_json:
                output_dir = Path(cir_pdf_path).parent / "analysis"
                output_dir.mkdir(exist_ok=True)
                
                cir_name = Path(cir_pdf_path).stem
                output_file = output_dir / f"{cir_name}_analysis.json"
                
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
                
                results["output_file"] = str(output_file)
                logger.info(f"Results saved to {output_file}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error in pipeline analysis: {e}", exc_info=True)
            return {
                "error": str(e),
                "cir_path": str(cir_pdf_path),
                "cim_path": str(cim_pdf_path)
            }
    
    def analyze_batch(
        self,
        cir_pdf_dir: str,
        cim_pdf_path: str,
        output_json: bool = True,
        max_files: int = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple CIR documents against a single CIM document
        
        Args:
            cir_pdf_dir: Directory containing CIR PDFs
            cim_pdf_path: Path to single CIM PDF
            output_json: Save results to JSON
            max_files: Maximum number of files to process (None = all)
        
        Returns:
            List of analysis results
        """
        
        logger.info(f"Starting batch analysis: CIR_DIR={cir_pdf_dir}, CIM={cim_pdf_path}")
        
        # Extract CIM once for all CIRs
        logger.info("Analyzing CIM document...")
        cim_text = self._extract_pdf_text(cim_pdf_path)
        cim_analysis = self.cim_analyzer.analyze_cim_document(cim_text)
        
        cim_requirements = [
            {
                "id": req.id,
                "title": req.title,
                "type": req.requirement_type,
                "description": req.description,
                "severity": req.severity,
                "components": req.applicable_components,
                "expected_evidence": req.expected_evidence
            }
            for req in cim_analysis.requirements
        ]
        
        logger.info(f"Extracted {len(cim_requirements)} CIM requirements")
        
        # Process CIR files
        cir_dir = Path(cir_pdf_dir)
        cir_files = list(cir_dir.glob("*.pdf"))
        
        if max_files:
            cir_files = cir_files[:max_files]
        
        logger.info(f"Found {len(cir_files)} CIR files to analyze")
        
        results = []
        for idx, cir_file in enumerate(cir_files, 1):
            logger.info(f"Processing {idx}/{len(cir_files)}: {cir_file.name}")
            
            try:
                # Extract CIR content
                cir_text = self._extract_pdf_text(str(cir_file))
                cir_metadata = self.cir_extractor.extract_metadata(cir_text)
                
                # Assess compliance
                evidence_list, summary = self.compliance_matcher.assess_compliance(
                    cir_text=cir_text,
                    cir_metadata=cir_metadata.all_fields,
                    cim_requirements=cim_requirements,
                    cim_metadata=cim_analysis.__dict__
                )
                
                # Create result entry
                result = {
                    "cir_file": str(cir_file),
                    "cir_name": cir_file.stem,
                    "cir_metadata": cir_metadata.all_fields,
                    "go_nogo": summary.get("go_nogo", "NO-GO"),
                    "compliance_score": summary.get("compliance_score", 0.0),
                    "met_requirements": summary.get("met", 0),
                    "partial_requirements": summary.get("partial", 0),
                    "not_met_requirements": summary.get("not_met", 0),
                    "total_requirements": summary.get("total_requirements", 0),
                    "compliance_evidence": [
                        {
                            "requirement_id": e.requirement_id,
                            "status": e.status.value,
                            "confidence_score": e.confidence_score
                        }
                        for e in evidence_list
                    ]
                }
                
                results.append(result)
            
            except Exception as e:
                logger.error(f"Error processing {cir_file.name}: {e}")
                results.append({
                    "cir_file": str(cir_file),
                    "error": str(e)
                })
        
        # Save batch results
        if output_json:
            output_dir = Path(cir_pdf_dir).parent / "batch_analysis"
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / "batch_results.json"
            with open(output_file, 'w') as f:
                json.dump({
                    "total_files": len(cir_files),
                    "results": results,
                    "cim_reference": str(cim_pdf_path)
                }, f, indent=2)
            
            logger.info(f"Batch results saved to {output_file}")
        
        return results
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF
        
        Uses PyPDF for basic extraction
        """
        try:
            from PyPDF2 import PdfReader
            
            text = []
            with open(pdf_path, 'rb') as f:
                pdf = PdfReader(f)
                for page in pdf.pages:
                    text.append(page.extract_text())
            
            return "\n".join(text)
        
        except ImportError:
            logger.error("PyPDF2 not available. Install: pip install PyPDF2")
            return ""
        except Exception as e:
            logger.error(f"Error extracting PDF {pdf_path}: {e}")
            return ""
    
    def get_summary_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from batch analysis"""
        
        valid_results = [r for r in results if "error" not in r]
        
        if not valid_results:
            return {"error": "No valid results"}
        
        go_count = sum(1 for r in valid_results if r.get("go_nogo") == "GO")
        nogo_count = sum(1 for r in valid_results if r.get("go_nogo") == "NO-GO")
        
        avg_score = sum(r.get("compliance_score", 0) for r in valid_results) / len(valid_results)
        
        return {
            "total_analyzed": len(valid_results),
            "go_count": go_count,
            "nogo_count": nogo_count,
            "go_percentage": (go_count / len(valid_results) * 100) if valid_results else 0,
            "average_compliance_score": avg_score,
            "total_met_requirements": sum(r.get("met_requirements", 0) for r in valid_results),
            "total_partial_requirements": sum(r.get("partial_requirements", 0) for r in valid_results),
            "total_not_met_requirements": sum(r.get("not_met_requirements", 0) for r in valid_results)
        }
