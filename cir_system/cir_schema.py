"""
Vestas CIR (Change Impact Report) Document Schema and Structure
Defines the JSON format for extracted and validated CIR data
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ComplianceStatus(str, Enum):
    """GO/NO-GO compliance status"""
    GO = "GO"
    NO_GO = "NO-GO"
    PENDING_REVIEW = "PENDING_REVIEW"


class SeverityLevel(str, Enum):
    """Issue severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class DocumentMetadata:
    """PDF document metadata"""
    filename: str
    file_size_mb: float
    page_count: int
    extraction_timestamp: str
    ocr_confidence: float = 0.0  # 0-100 OCR accuracy
    extraction_method: str = "pytesseract"  # OCR method used


@dataclass
class TechnicalData:
    """Extracted technical information"""
    component_name: Optional[str] = None
    component_id: Optional[str] = None
    part_number: Optional[str] = None
    drawing_number: Optional[str] = None
    revision: Optional[str] = None
    description: Optional[str] = None
    specifications: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChangeDetails:
    """Change information"""
    change_type: Optional[str] = None  # e.g., "Design Change", "Material Change"
    reason_for_change: Optional[str] = None
    affected_areas: List[str] = field(default_factory=list)
    implementation_date: Optional[str] = None
    change_owner: Optional[str] = None
    technical_justification: Optional[str] = None


@dataclass
class ComplianceIssue:
    """Identified compliance issue"""
    issue_id: str
    severity: SeverityLevel
    category: str  # e.g., "Technical", "Documentation", "Quality"
    description: str
    affected_section: str
    recommended_action: str
    resolution_status: str = "OPEN"


@dataclass
class ComplianceValidation:
    """Compliance validation results"""
    status: ComplianceStatus
    score: float  # 0-100
    total_checks: int
    passed_checks: int
    failed_checks: int
    critical_issues: List[ComplianceIssue] = field(default_factory=list)
    warnings: List[ComplianceIssue] = field(default_factory=list)
    validation_rules_applied: List[str] = field(default_factory=list)
    validation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExtractedImage:
    """Extracted image information"""
    image_id: str
    page_number: int
    image_type: str  # e.g., "diagram", "schematic", "photo"
    description: Optional[str] = None
    location_in_page: str = "unknown"  # approximate location
    size_pixels: Optional[tuple] = None


@dataclass
class CIRDocument:
    """Complete CIR document structure"""
    # Identifiers
    document_id: str  # Unique ID
    cir_number: str  # CIR reference number
    
    # Metadata
    metadata: DocumentMetadata
    
    # Content
    technical_data: TechnicalData
    change_details: ChangeDetails
    
    # Extracted text (full content)
    full_text_content: str
    extracted_pages: Dict[int, str]  # page_number -> page_text
    
    # Images
    extracted_images: List[ExtractedImage] = field(default_factory=list)
    
    # Compliance
    compliance: ComplianceValidation = field(default_factory=lambda: ComplianceValidation(
        status=ComplianceStatus.PENDING_REVIEW,
        score=0.0,
        total_checks=0,
        passed_checks=0,
        failed_checks=0
    ))
    
    # Additional
    processing_notes: List[str] = field(default_factory=list)
    extraction_errors: List[str] = field(default_factory=list)


def create_empty_cir_document(
    document_id: str,
    cir_number: str,
    filename: str,
    file_size_mb: float,
    page_count: int
) -> CIRDocument:
    """Create an empty CIR document template"""
    return CIRDocument(
        document_id=document_id,
        cir_number=cir_number,
        metadata=DocumentMetadata(
            filename=filename,
            file_size_mb=file_size_mb,
            page_count=page_count,
            extraction_timestamp=datetime.now().isoformat()
        ),
        technical_data=TechnicalData(),
        change_details=ChangeDetails(),
        full_text_content="",
        extracted_pages={}
    )


def cir_to_dict(cir_doc: CIRDocument) -> Dict[str, Any]:
    """Convert CIR document to dictionary (JSON serializable)"""
    doc_dict = asdict(cir_doc)
    
    # Convert enums to strings
    doc_dict["compliance"]["status"] = cir_doc.compliance.status.value
    
    for issue in doc_dict["compliance"]["critical_issues"]:
        issue["severity"] = issue["severity"]
    
    for issue in doc_dict["compliance"]["warnings"]:
        issue["severity"] = issue["severity"]
    
    return doc_dict


# Compliance Rules for Vestas CIR
VESTAS_CIR_RULES = {
    "required_fields": [
        "cir_number",
        "component_name",
        "change_type",
        "reason_for_change",
        "technical_justification"
    ],
    "mandatory_checks": [
        "Has CIR number",
        "Has component identification",
        "Has change justification",
        "Has implementation plan",
        "Has quality approval",
        "Has technical review",
        "Has change owner"
    ],
    "compliance_thresholds": {
        "go_score_minimum": 85,  # 85% compliance score = GO
        "no_go_issues": ["CRITICAL"],  # Any CRITICAL issue = NO-GO
        "allow_warnings": True
    }
}
