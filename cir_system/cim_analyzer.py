"""
Advanced CIM Document Analyzer
Extracts compliance requirements from CIM (Condition Impact Management) documents
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ComplianceRequirement:
    """A single compliance requirement extracted from CIM"""
    requirement_id: str
    title: str
    description: str
    requirement_type: str  # e.g., "Test Method", "Documentation", "Visual Inspection"
    applicable_components: List[str]
    acceptance_criteria: str
    evidence_needed: List[str]
    source_document: str
    severity: str = "HIGH"  # HIGH, MEDIUM, LOW


@dataclass
class CIMAnalysis:
    """Complete analysis of CIM documents"""
    cim_case_id: str
    cim_title: str
    affected_components: List[str]
    failure_types: List[str]
    requirements: List[ComplianceRequirement] = field(default_factory=list)
    work_instructions: Dict[str, str] = field(default_factory=dict)
    test_procedures: Dict[str, str] = field(default_factory=dict)
    acceptance_standards: Dict[str, str] = field(default_factory=dict)
    visual_inspection_criteria: List[str] = field(default_factory=list)
    documentation_requirements: List[str] = field(default_factory=list)


class CIMDocumentAnalyzer:
    """Analyze CIM documents to extract compliance requirements"""
    
    def __init__(self):
        self.analysis: Optional[CIMAnalysis] = None
        self.requirement_counter = 0
    
    def analyze_cim_document(self, text: str, doc_name: str = "CIM Document") -> CIMAnalysis:
        """
        Analyze CIM document text and extract all compliance requirements
        
        Args:
            text: Full text of CIM document
            doc_name: Name/identifier of document
            
        Returns:
            CIMAnalysis with extracted requirements
        """
        logger.info(f"Analyzing CIM document: {doc_name}")
        
        # Extract CIM case information
        cim_case_id = self._extract_case_id(text)
        cim_title = self._extract_title(text)
        
        # Extract component information
        affected_components = self._extract_affected_components(text)
        failure_types = self._extract_failure_types(text)
        
        # Create analysis object
        analysis = CIMAnalysis(
            cim_case_id=cim_case_id,
            cim_title=cim_title,
            affected_components=affected_components,
            failure_types=failure_types
        )
        
        # Extract different types of requirements
        analysis.requirements.extend(self._extract_test_methods(text, doc_name))
        analysis.requirements.extend(self._extract_documentation_requirements(text, doc_name))
        analysis.requirements.extend(self._extract_visual_inspection_criteria(text, doc_name))
        analysis.requirements.extend(self._extract_procedural_requirements(text, doc_name))
        
        # Extract work instructions
        analysis.work_instructions = self._extract_work_instructions(text)
        
        # Extract test procedures
        analysis.test_procedures = self._extract_test_procedures(text)
        
        # Extract acceptance standards
        analysis.acceptance_standards = self._extract_acceptance_standards(text)
        
        # Extract visual inspection criteria
        analysis.visual_inspection_criteria = self._extract_visual_criteria_list(text)
        
        # Extract documentation requirements
        analysis.documentation_requirements = self._extract_documentation_list(text)
        
        self.analysis = analysis
        logger.info(f"Extracted {len(analysis.requirements)} compliance requirements")
        
        return analysis
    
    def _extract_case_id(self, text: str) -> str:
        """Extract CIM case ID"""
        patterns = [
            r'CIM\s*[-:]?\s*(\d+)',
            r'Case\s*(?:ID|Number)\s*[-:]?\s*([A-Z0-9\-]+)',
            r'(\w+[-]\d+[-]\d+)'  # Format: XXX-001-002
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if '1' in str(match.groups()) else match.group(0)
        
        return "CIM-UNKNOWN"
    
    def _extract_title(self, text: str) -> str:
        """Extract CIM title"""
        lines = text.split('\n')
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                return line
        return "CIM Case Summary"
    
    def _extract_affected_components(self, text: str) -> List[str]:
        """Extract affected component types"""
        components = []
        
        component_keywords = [
            'blade', 'rotor', 'nacelle', 'tower', 'foundation',
            'gearbox', 'generator', 'transformer', 'bearing',
            'pitch', 'yaw', 'brake', 'hub', 'shaft', 'bolt',
            'weld', 'connector', 'cable', 'sensor', 'controller'
        ]
        
        text_lower = text.lower()
        for component in component_keywords:
            if component in text_lower:
                # Try to extract with context
                pattern = rf'(?:the\s+)?({component}[s]?)\s+(?:component|part|assembly|system)'
                match = re.search(pattern, text_lower)
                if match:
                    components.append(match.group(1).title())
        
        return list(set(components))  # Remove duplicates
    
    def _extract_failure_types(self, text: str) -> List[str]:
        """Extract failure types mentioned"""
        failure_types = []
        
        failure_keywords = [
            'fatigue', 'corrosion', 'fracture', 'delamination', 'erosion',
            'cracking', 'wear', 'bearing failure', 'misalignment', 'vibration',
            'overheating', 'electrical failure', 'mechanical failure'
        ]
        
        text_lower = text.lower()
        for failure in failure_keywords:
            if failure in text_lower:
                failure_types.append(failure.title())
        
        return list(set(failure_types))
    
    def _extract_test_methods(self, text: str, source: str) -> List[ComplianceRequirement]:
        """Extract test method requirements"""
        requirements = []
        
        # Look for test method descriptions
        test_patterns = [
            r'(?:test|examination|inspection)\s+(?:method|procedure|step)[s]?:?\s*([^\n]+)',
            r'(?:perform|conduct|carry out)\s+(?:the\s+)?([^:]+?)\s+test',
            r'test.*?(?:per|according to|as per|following)\s+([A-Z\d\-\.]+)',
        ]
        
        for pattern in test_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                req = ComplianceRequirement(
                    requirement_id=f"TEST-{self._next_id()}",
                    title=f"Test Method",
                    description=match.group(1),
                    requirement_type="Test Method",
                    applicable_components=[],
                    acceptance_criteria="Test performed per specification",
                    evidence_needed=["Test report", "Test data", "Technician signature"],
                    source_document=source
                )
                requirements.append(req)
        
        return requirements
    
    def _extract_documentation_requirements(self, text: str, source: str) -> List[ComplianceRequirement]:
        """Extract documentation requirements"""
        requirements = []
        
        doc_patterns = [
            r'(?:document|record|report)\s+(?:the|all)\s+([^\n.]+)',
            r'(?:required documents?|must include)\s*:?\s*([^\n]+)',
            r'(?:submit|provide)\s+(?:the\s+)?([^\n.]+)'
        ]
        
        for pattern in doc_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                desc = match.group(1).strip()
                if len(desc) > 10:
                    req = ComplianceRequirement(
                        requirement_id=f"DOC-{self._next_id()}",
                        title="Documentation",
                        description=desc,
                        requirement_type="Documentation",
                        applicable_components=[],
                        acceptance_criteria="Documentation complete and accurate",
                        evidence_needed=["Document", "Report", "Record"],
                        source_document=source
                    )
                    requirements.append(req)
        
        return requirements
    
    def _extract_visual_inspection_criteria(self, text: str, source: str) -> List[ComplianceRequirement]:
        """Extract visual inspection requirements"""
        requirements = []
        
        inspection_patterns = [
            r'(?:visual inspection|inspect visually|look for)\s*:?\s*([^\n.]+)',
            r'(?:check|observe)\s+(?:for|the)\s+([^\n.]+)',
            r'(?:appearance|condition|surface)\s+(?:should|must)\s+([^\n.]+)'
        ]
        
        for pattern in inspection_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                req = ComplianceRequirement(
                    requirement_id=f"VIS-{self._next_id()}",
                    title="Visual Inspection",
                    description=match.group(1),
                    requirement_type="Visual Inspection",
                    applicable_components=[],
                    acceptance_criteria="Visual inspection passed",
                    evidence_needed=["Photo", "Screenshot", "Visual evidence"],
                    source_document=source,
                    severity="MEDIUM"
                )
                requirements.append(req)
        
        return requirements
    
    def _extract_procedural_requirements(self, text: str, source: str) -> List[ComplianceRequirement]:
        """Extract procedural/step requirements"""
        requirements = []
        
        # Look for numbered steps
        step_pattern = r'(?:step|procedure)\s+(\d+)[:\-\.]?\s*([^\n]+)'
        matches = re.finditer(step_pattern, text, re.IGNORECASE)
        
        for match in matches:
            step_num = match.group(1)
            step_desc = match.group(2).strip()
            if len(step_desc) > 10:
                req = ComplianceRequirement(
                    requirement_id=f"PROC-{self._next_id()}",
                    title=f"Procedure Step {step_num}",
                    description=step_desc,
                    requirement_type="Procedure",
                    applicable_components=[],
                    acceptance_criteria="Step completed as specified",
                    evidence_needed=["Completion log", "Signature", "Timestamp"],
                    source_document=source,
                    severity="HIGH"
                )
                requirements.append(req)
        
        return requirements
    
    def _extract_work_instructions(self, text: str) -> Dict[str, str]:
        """Extract work instructions sections"""
        instructions = {}
        
        # Look for work instruction sections
        sections = re.split(r'(?:Work Instructions?|Procedure|Steps?)[:\-]?\s*\n', text, flags=re.IGNORECASE)
        
        for i, section in enumerate(sections[1:], 1):
            if len(section.strip()) > 50:
                instructions[f"Instruction {i}"] = section[:500]  # First 500 chars
        
        return instructions
    
    def _extract_test_procedures(self, text: str) -> Dict[str, str]:
        """Extract test procedure sections"""
        procedures = {}
        
        sections = re.split(r'(?:Test Procedure|Testing Procedure)[:\-]?\s*\n', text, flags=re.IGNORECASE)
        
        for i, section in enumerate(sections[1:], 1):
            if len(section.strip()) > 50:
                procedures[f"Test Procedure {i}"] = section[:500]
        
        return procedures
    
    def _extract_acceptance_standards(self, text: str) -> Dict[str, str]:
        """Extract acceptance standards"""
        standards = {}
        
        # Look for acceptance criteria
        patterns = [
            r'(?:Acceptance Criteria?|Pass Criteria?|Success Criteria?)[:\-]?\s*([^\n]+(?:\n[^\n]*?){0,5})',
            r'(?:Shall|Must|Should)\s+([^\n.]+\.)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, flags=re.IGNORECASE)
            for i, match in enumerate(matches, 1):
                standards[f"Standard {i}"] = match.group(1)[:300]
        
        return standards
    
    def _extract_visual_criteria_list(self, text: str) -> List[str]:
        """Extract list of visual criteria"""
        criteria = []
        
        visual_keywords = [
            'crack', 'corrosion', 'rust', 'discoloration', 'deformation',
            'wear', 'damage', 'contamination', 'alignment', 'gap',
            'surface finish', 'color', 'label', 'marking', 'seal'
        ]
        
        text_lower = text.lower()
        for keyword in visual_keywords:
            if keyword in text_lower:
                # Try to extract context
                pattern = rf'(?:(?:no|check for|look for|observe)\s+)?({keyword}[s]?)[^\n.]*(?:\.|;|,)'
                match = re.search(pattern, text_lower)
                if match:
                    criteria.append(match.group(0).capitalize())
        
        return list(set(criteria))
    
    def _extract_documentation_list(self, text: str) -> List[str]:
        """Extract list of required documentation"""
        docs = []
        
        doc_keywords = [
            'test report', 'certificate', 'record', 'log', 'work order',
            'photo', 'image', 'drawing', 'specification', 'standard',
            'invoice', 'shipping document', 'inspection record', 'signature'
        ]
        
        text_lower = text.lower()
        for keyword in doc_keywords:
            if keyword in text_lower:
                docs.append(keyword.title())
        
        return list(set(docs))
    
    def _next_id(self) -> str:
        """Get next requirement ID"""
        self.requirement_counter += 1
        return f"{self.requirement_counter:03d}"
    
    def get_requirements_summary(self) -> Dict[str, Any]:
        """Get summary of all requirements"""
        if not self.analysis:
            return {}
        
        return {
            "case_id": self.analysis.cim_case_id,
            "title": self.analysis.cim_title,
            "total_requirements": len(self.analysis.requirements),
            "by_type": self._count_by_type(),
            "affected_components": self.analysis.affected_components,
            "failure_types": self.analysis.failure_types,
            "requirements": [
                {
                    "id": r.requirement_id,
                    "title": r.title,
                    "type": r.requirement_type,
                    "description": r.description,
                    "severity": r.severity
                }
                for r in self.analysis.requirements
            ]
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count requirements by type"""
        counts = {}
        for req in self.analysis.requirements:
            counts[req.requirement_type] = counts.get(req.requirement_type, 0) + 1
        return counts
