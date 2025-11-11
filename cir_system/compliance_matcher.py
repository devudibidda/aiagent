"""
Advanced Compliance Matcher
Matches CIR evidence against CIM requirements with Met/Not Met/Partial status
"""

import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceStatus(str, Enum):
    """Compliance assessment status"""
    MET = "Met"
    NOT_MET = "Not Met"
    PARTIAL = "Partial"
    UNABLE_TO_VERIFY = "Unable to Verify"


@dataclass
class ComplianceEvidence:
    """Evidence for a compliance assessment"""
    requirement_id: str
    requirement_title: str
    status: ComplianceStatus
    evidence_found: List[str]  # What evidence was found in CIR
    expected_evidence: List[str]  # What should be there per CIM
    comments: str
    supporting_cir_text: str  # Relevant excerpt from CIR
    visual_evidence: List[str]  # Images, photos, etc.
    confidence_score: float  # 0-100


class ComplianceMatcher:
    """Match CIR documents against CIM requirements"""
    
    def __init__(self):
        self.evidence_list: List[ComplianceEvidence] = []
    
    def assess_compliance(
        self,
        cir_text: str,
        cir_metadata: Dict[str, Any],
        cim_requirements: List[Any],
        cim_metadata: Dict[str, Any]
    ) -> Tuple[List[ComplianceEvidence], Dict[str, Any]]:
        """
        Assess CIR compliance against CIM requirements
        
        Returns:
            (evidence_list, summary)
        """
        self.evidence_list = []
        
        logger.info(f"Assessing compliance: {len(cim_requirements)} requirements")
        
        # Check component applicability
        applicable_requirements = self._filter_applicable_requirements(
            cim_requirements,
            cir_metadata,
            cim_metadata
        )
        
        # Assess each requirement
        for requirement in applicable_requirements:
            evidence = self._assess_requirement(
                requirement,
                cir_text,
                cir_metadata
            )
            self.evidence_list.append(evidence)
        
        # Generate summary
        summary = self._generate_summary()
        
        logger.info(f"Compliance assessment complete: {summary['go_nogo']}")
        
        return self.evidence_list, summary
    
    def _filter_applicable_requirements(
        self,
        requirements: List[Any],
        cir_metadata: Dict[str, Any],
        cim_metadata: Dict[str, Any]
    ) -> List[Any]:
        """Filter requirements applicable to this CIR"""
        applicable = []
        
        cir_component = str(cir_metadata.get("Component Type", "")).lower()
        cim_components = [c.lower() for c in cim_metadata.get("affected_components", [])]
        
        for req in requirements:
            # Check component match
            if not cim_components or any(comp in cir_component for comp in cim_components):
                applicable.append(req)
        
        return applicable
    
    def _assess_requirement(
        self,
        requirement: Any,
        cir_text: str,
        cir_metadata: Dict[str, Any]
    ) -> ComplianceEvidence:
        """Assess a single requirement against CIR"""
        
        req_id = requirement.requirement_id
        req_title = requirement.title
        req_type = requirement.requirement_type
        req_description = requirement.description
        expected_evidence = requirement.evidence_needed
        
        # Search for evidence in CIR
        evidence_found = self._search_evidence(req_description, cir_text)
        cir_excerpt = self._extract_relevant_text(req_description, cir_text)
        
        # Assess status
        status, confidence = self._determine_status(
            req_type,
            evidence_found,
            expected_evidence,
            cir_text
        )
        
        # Generate comments
        comments = self._generate_assessment_comment(
            status,
            evidence_found,
            expected_evidence
        )
        
        evidence = ComplianceEvidence(
            requirement_id=req_id,
            requirement_title=req_title,
            status=status,
            evidence_found=evidence_found,
            expected_evidence=expected_evidence,
            comments=comments,
            supporting_cir_text=cir_excerpt,
            visual_evidence=self._find_visual_evidence(cir_text),
            confidence_score=confidence
        )
        
        return evidence
    
    def _search_evidence(self, requirement_desc: str, cir_text: str) -> List[str]:
        """Search for evidence matching requirement"""
        evidence = []
        
        # Break requirement into keywords
        keywords = [word.lower() for word in requirement_desc.split() if len(word) > 3]
        
        # Search for keywords in CIR
        for keyword in keywords:
            if keyword in cir_text.lower():
                evidence.append(f"Found: {keyword}")
        
        # Look for specific evidence types
        if "test" in requirement_desc.lower():
            if any(t in cir_text.lower() for t in ["test report", "test results", "test data"]):
                evidence.append("Test documentation found")
        
        if "document" in requirement_desc.lower():
            if any(d in cir_text.lower() for d in ["document", "record", "report", "log"]):
                evidence.append("Documentation found")
        
        if "photo" in requirement_desc.lower() or "image" in requirement_desc.lower():
            if "photo" in cir_text.lower() or "image" in cir_text.lower() or "[PHOTO]" in cir_text:
                evidence.append("Photo/Image reference found")
        
        return evidence
    
    def _extract_relevant_text(self, requirement: str, cir_text: str, max_length: int = 300) -> str:
        """Extract relevant text from CIR"""
        # Simple heuristic: find sentences containing requirement keywords
        import re
        
        keywords = requirement.split()[:3]  # First 3 words
        
        sentences = re.split(r'(?<=[.!?])\s+', cir_text)
        
        relevant = []
        for sentence in sentences:
            if any(kw.lower() in sentence.lower() for kw in keywords):
                relevant.append(sentence)
                if len(' '.join(relevant)) > max_length:
                    break
        
        return ' '.join(relevant)[:max_length]
    
    def _determine_status(
        self,
        req_type: str,
        evidence_found: List[str],
        expected_evidence: List[str],
        cir_text: str
    ) -> Tuple[ComplianceStatus, float]:
        """Determine compliance status"""
        
        confidence = 0.0
        
        if not evidence_found:
            return ComplianceStatus.UNABLE_TO_VERIFY, 30.0
        
        # Calculate score based on evidence found vs. expected
        evidence_ratio = len(evidence_found) / max(1, len(expected_evidence))
        
        if evidence_ratio >= 0.9:
            status = ComplianceStatus.MET
            confidence = 90.0 + min(10, len(evidence_found) * 5)
        elif evidence_ratio >= 0.5:
            status = ComplianceStatus.PARTIAL
            confidence = 60.0 + (evidence_ratio * 30)
        else:
            status = ComplianceStatus.NOT_MET
            confidence = min(50, 10 + len(evidence_found) * 10)
        
        return status, confidence
    
    def _generate_assessment_comment(
        self,
        status: ComplianceStatus,
        evidence_found: List[str],
        expected_evidence: List[str]
    ) -> str:
        """Generate assessment comment"""
        
        if status == ComplianceStatus.MET:
            return f"All required evidence found ({len(evidence_found)} items verified)"
        
        elif status == ComplianceStatus.PARTIAL:
            missing = len(expected_evidence) - len(evidence_found)
            return f"Partial compliance: {len(evidence_found)} of {len(expected_evidence)} requirements met. {missing} items missing."
        
        elif status == ComplianceStatus.NOT_MET:
            return f"Non-compliant: {len(expected_evidence)} requirements expected, {len(evidence_found)} found"
        
        else:
            return f"Unable to verify requirement: insufficient evidence in CIR"
    
    def _find_visual_evidence(self, cir_text: str) -> List[str]:
        """Find references to visual evidence"""
        import re
        
        visual_evidence = []
        
        # Look for photo/image references
        photo_patterns = [
            r"\[PHOTO[^\]]*\]",
            r"\[IMAGE[^\]]*\]",
            r"photo.*?(?:attached|included|see)",
            r"(?:see|refer to)\s+(?:photo|image|figure|fig\.?|picture)"
        ]
        
        for pattern in photo_patterns:
            matches = re.finditer(pattern, cir_text, re.IGNORECASE)
            for match in matches:
                visual_evidence.append(match.group(0))
        
        return visual_evidence
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate compliance summary"""
        
        total = len(self.evidence_list)
        met = sum(1 for e in self.evidence_list if e.status == ComplianceStatus.MET)
        partial = sum(1 for e in self.evidence_list if e.status == ComplianceStatus.PARTIAL)
        not_met = sum(1 for e in self.evidence_list if e.status == ComplianceStatus.NOT_MET)
        unable = sum(1 for e in self.evidence_list if e.status == ComplianceStatus.UNABLE_TO_VERIFY)
        
        # Calculate overall compliance score
        compliance_score = (met + partial * 0.5) / max(1, total) * 100 if total > 0 else 0
        
        # Determine GO/NO-GO
        # GO if: ≥85% compliance and no critical NOT_MET
        go_nogo = "GO" if compliance_score >= 85 and not_met == 0 else "NO-GO"
        
        return {
            "total_requirements": total,
            "met": met,
            "partial": partial,
            "not_met": not_met,
            "unable_to_verify": unable,
            "compliance_score": compliance_score,
            "go_nogo": go_nogo,
            "summary": (
                f"Compliance Assessment: {go_nogo}\n"
                f"Score: {compliance_score:.1f}%\n"
                f"Met: {met}/{total}, Partial: {partial}, Not Met: {not_met}"
            )
        }
    
    def get_evidence_table_data(self) -> List[Dict[str, Any]]:
        """Get evidence formatted for table"""
        return [
            {
                "Requirement ID": e.requirement_id,
                "Requirement": e.requirement_title,
                "Status": e.status.value,
                "Evidence Found": ", ".join(e.evidence_found) if e.evidence_found else "None",
                "Comments": e.comments,
                "Confidence": f"{e.confidence_score:.0f}%",
                "Visual Evidence": ", ".join(e.visual_evidence) if e.visual_evidence else "None"
            }
            for e in self.evidence_list
        ]
