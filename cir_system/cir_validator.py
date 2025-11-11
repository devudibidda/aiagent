"""
CIR Compliance Validator
Validates extracted CIR documents against Vestas standards
"""

import logging
import re
from typing import List, Dict, Tuple, Optional
from .cir_schema import (
    CIRDocument,
    ComplianceStatus,
    ComplianceIssue,
    SeverityLevel,
    ComplianceValidation,
    VESTAS_CIR_RULES
)

logger = logging.getLogger(__name__)


class CIRComplianceValidator:
    """Validates CIR documents for compliance"""
    
    def __init__(self, rules: Dict = None):
        """Initialize validator with rules"""
        self.rules = rules or VESTAS_CIR_RULES
        self.validation_results: List[ComplianceIssue] = []
    
    def validate(self, cir_doc: CIRDocument) -> ComplianceValidation:
        """
        Perform comprehensive compliance validation
        
        Returns:
            ComplianceValidation with status (GO/NO-GO) and details
        """
        self.validation_results = []
        checks_performed = []
        
        # Run all validation checks
        checks_performed.extend(self._check_required_fields(cir_doc))
        checks_performed.extend(self._check_technical_data(cir_doc))
        checks_performed.extend(self._check_change_details(cir_doc))
        checks_performed.extend(self._check_documentation(cir_doc))
        checks_performed.extend(self._check_approvals(cir_doc))
        checks_performed.extend(self._check_quality(cir_doc))
        
        # Calculate compliance score
        passed = sum(1 for check in checks_performed if check["status"] == "PASS")
        failed = len(checks_performed) - passed
        score = (passed / len(checks_performed) * 100) if checks_performed else 0
        
        # Separate critical issues and warnings
        critical_issues = [issue for issue in self.validation_results 
                          if issue.severity == SeverityLevel.CRITICAL]
        warnings = [issue for issue in self.validation_results 
                   if issue.severity != SeverityLevel.CRITICAL]
        
        # Determine GO/NO-GO status
        status = self._determine_status(score, critical_issues)
        
        validation = ComplianceValidation(
            status=status,
            score=score,
            total_checks=len(checks_performed),
            passed_checks=passed,
            failed_checks=failed,
            critical_issues=critical_issues,
            warnings=warnings,
            validation_rules_applied=checks_performed
        )
        
        logger.info(f"Validation complete: {status.value} (Score: {score:.1f}%)")
        
        return validation
    
    def _determine_status(self, score: float, critical_issues: List[ComplianceIssue]) -> ComplianceStatus:
        """Determine GO/NO-GO status"""
        threshold = self.rules["compliance_thresholds"]["go_score_minimum"]
        
        # NO-GO if critical issues
        if critical_issues:
            return ComplianceStatus.NO_GO
        
        # NO-GO if score below threshold
        if score < threshold:
            return ComplianceStatus.NO_GO
        
        # GO if all checks pass
        return ComplianceStatus.GO
    
    def _check_required_fields(self, cir_doc: CIRDocument) -> List[Dict]:
        """Check if all required fields are present"""
        checks = []
        
        required = self.rules["required_fields"]
        
        # Check document level
        if not cir_doc.cir_number:
            self._add_issue("Missing CIR Number", SeverityLevel.CRITICAL, 
                           "Document", "CIR document must have unique CIR number")
            checks.append({"check": "CIR Number Present", "status": "FAIL"})
        else:
            checks.append({"check": "CIR Number Present", "status": "PASS"})
        
        # Check technical data
        tech = cir_doc.technical_data
        if not tech.component_name:
            self._add_issue("Missing Component Name", SeverityLevel.CRITICAL,
                           "Technical Data", "Component must be identified")
            checks.append({"check": "Component Identified", "status": "FAIL"})
        else:
            checks.append({"check": "Component Identified", "status": "PASS"})
        
        if not tech.part_number and not tech.drawing_number:
            self._add_issue("Missing Part/Drawing Number", SeverityLevel.HIGH,
                           "Technical Data", "Must have part number or drawing number")
            checks.append({"check": "Part Number Available", "status": "FAIL"})
        else:
            checks.append({"check": "Part Number Available", "status": "PASS"})
        
        # Check change details
        change = cir_doc.change_details
        if not change.change_type:
            self._add_issue("Missing Change Type", SeverityLevel.HIGH,
                           "Change Details", "Change type must be specified")
            checks.append({"check": "Change Type Specified", "status": "FAIL"})
        else:
            checks.append({"check": "Change Type Specified", "status": "PASS"})
        
        if not change.reason_for_change:
            self._add_issue("Missing Change Reason", SeverityLevel.HIGH,
                           "Change Details", "Reason for change must be documented")
            checks.append({"check": "Change Reason Documented", "status": "FAIL"})
        else:
            checks.append({"check": "Change Reason Documented", "status": "PASS"})
        
        if not change.technical_justification:
            self._add_issue("Missing Technical Justification", SeverityLevel.CRITICAL,
                           "Change Details", "Technical justification is mandatory")
            checks.append({"check": "Technical Justification", "status": "FAIL"})
        else:
            checks.append({"check": "Technical Justification", "status": "PASS"})
        
        return checks
    
    def _check_technical_data(self, cir_doc: CIRDocument) -> List[Dict]:
        """Check technical data completeness"""
        checks = []
        
        tech = cir_doc.technical_data
        
        if tech.description and len(tech.description.strip()) > 10:
            checks.append({"check": "Component Description", "status": "PASS"})
        else:
            self._add_issue("Insufficient Description", SeverityLevel.MEDIUM,
                           "Technical Data", "Component description should be more detailed")
            checks.append({"check": "Component Description", "status": "FAIL"})
        
        if tech.specifications:
            checks.append({"check": "Specifications Provided", "status": "PASS"})
        else:
            self._add_issue("Missing Specifications", SeverityLevel.MEDIUM,
                           "Technical Data", "Technical specifications should be included")
            checks.append({"check": "Specifications Provided", "status": "FAIL"})
        
        return checks
    
    def _check_change_details(self, cir_doc: CIRDocument) -> List[Dict]:
        """Check change details"""
        checks = []
        
        change = cir_doc.change_details
        
        if change.implementation_date:
            checks.append({"check": "Implementation Date Set", "status": "PASS"})
        else:
            self._add_issue("Missing Implementation Date", SeverityLevel.HIGH,
                           "Change Details", "Implementation date must be specified")
            checks.append({"check": "Implementation Date Set", "status": "FAIL"})
        
        if change.change_owner:
            checks.append({"check": "Change Owner Assigned", "status": "PASS"})
        else:
            self._add_issue("Missing Change Owner", SeverityLevel.HIGH,
                           "Change Details", "Change owner must be assigned")
            checks.append({"check": "Change Owner Assigned", "status": "FAIL"})
        
        if change.affected_areas:
            checks.append({"check": "Affected Areas Documented", "status": "PASS"})
        else:
            self._add_issue("No Affected Areas Listed", SeverityLevel.MEDIUM,
                           "Change Details", "Should document areas affected by change")
            checks.append({"check": "Affected Areas Documented", "status": "FAIL"})
        
        return checks
    
    def _check_documentation(self, cir_doc: CIRDocument) -> List[Dict]:
        """Check documentation quality"""
        checks = []
        
        text_length = len(cir_doc.full_text_content.strip())
        
        if text_length > 500:
            checks.append({"check": "Documentation Complete", "status": "PASS"})
        else:
            self._add_issue("Insufficient Documentation", SeverityLevel.MEDIUM,
                           "Documentation", "Document seems incomplete or truncated")
            checks.append({"check": "Documentation Complete", "status": "FAIL"})
        
        # Check for key terms
        key_terms = ["change", "impact", "risk", "verification", "approval"]
        found_terms = sum(1 for term in key_terms if term.lower() in cir_doc.full_text_content.lower())
        
        if found_terms >= 3:
            checks.append({"check": "Key Documentation Elements", "status": "PASS"})
        else:
            self._add_issue("Missing Key Documentation", SeverityLevel.MEDIUM,
                           "Documentation", f"Found {found_terms}/5 expected documentation elements")
            checks.append({"check": "Key Documentation Elements", "status": "FAIL"})
        
        return checks
    
    def _check_approvals(self, cir_doc: CIRDocument) -> List[Dict]:
        """Check approval signatures/marks"""
        checks = []
        
        # Look for approval keywords in text
        approval_keywords = ["approved", "signed", "authorized", "reviewed", "confirmed"]
        has_approval = any(keyword in cir_doc.full_text_content.lower() 
                          for keyword in approval_keywords)
        
        if has_approval:
            checks.append({"check": "Approval Evidence", "status": "PASS"})
        else:
            self._add_issue("No Approval Evidence Found", SeverityLevel.HIGH,
                           "Approvals", "Document should show approval signatures or evidence")
            checks.append({"check": "Approval Evidence", "status": "FAIL"})
        
        return checks
    
    def _check_quality(self, cir_doc: CIRDocument) -> List[Dict]:
        """Check quality and extraction metrics"""
        checks = []
        
        # OCR confidence
        if cir_doc.metadata.ocr_confidence >= 80:
            checks.append({"check": "Text Extraction Quality", "status": "PASS"})
        elif cir_doc.metadata.ocr_confidence >= 60:
            self._add_issue("Low OCR Confidence", SeverityLevel.MEDIUM,
                           "Quality", f"OCR confidence {cir_doc.metadata.ocr_confidence:.1f}% - manual review recommended")
            checks.append({"check": "Text Extraction Quality", "status": "WARN"})
        else:
            self._add_issue("Very Low OCR Confidence", SeverityLevel.HIGH,
                           "Quality", f"OCR confidence {cir_doc.metadata.ocr_confidence:.1f}% - document may be unreadable")
            checks.append({"check": "Text Extraction Quality", "status": "FAIL"})
        
        # Extraction errors
        if not cir_doc.extraction_errors:
            checks.append({"check": "No Extraction Errors", "status": "PASS"})
        else:
            self._add_issue(f"{len(cir_doc.extraction_errors)} Extraction Errors", SeverityLevel.MEDIUM,
                           "Quality", "Some content may not have been extracted correctly")
            checks.append({"check": "No Extraction Errors", "status": "FAIL"})
        
        return checks
    
    def _add_issue(self, title: str, severity: SeverityLevel, category: str, description: str):
        """Add a compliance issue"""
        issue = ComplianceIssue(
            issue_id=f"ISSUE_{len(self.validation_results) + 1:04d}",
            severity=severity,
            category=category,
            description=description,
            affected_section=title,
            recommended_action=self._get_recommended_action(severity, category)
        )
        self.validation_results.append(issue)
    
    def _get_recommended_action(self, severity: SeverityLevel, category: str) -> str:
        """Get recommended action for issue"""
        if severity == SeverityLevel.CRITICAL:
            return "MUST be resolved before CIR approval"
        elif severity == SeverityLevel.HIGH:
            return "Should be resolved before CIR approval"
        elif severity == SeverityLevel.MEDIUM:
            return "Should be addressed in next revision"
        else:
            return "Consider for future improvements"
