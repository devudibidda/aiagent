#!/usr/bin/env python3
"""
Knowledge Base Fallback Utility

Provides fallback compliance standards when knowledge base is empty.
This allows the agent to work without requiring pre-populated PDFs.
"""

from pathlib import Path
from typing import List, Dict, Optional
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)


# Generic compliance standards as text
COMPLIANCE_STANDARDS = {
    "iso27001": {
        "title": "ISO 27001:2022 - Information Security Management System",
        "description": "International standard for Information Security Management Systems.",
        "content": """
ISO 27001:2022 REQUIREMENTS:

1. INFORMATION ASSET MANAGEMENT
   - All information assets must be identified and classified
   - Data inventory must be maintained
   - Asset ownership and custody established
   - Asset handling and disposal procedures documented

2. ACCESS CONTROL
   - Access based on business requirements and least privilege principle
   - Authentication mechanisms (passwords, MFA) required
   - Role-based access control (RBAC) implementation
   - Periodic access reviews and revocation procedures

3. CRYPTOGRAPHY AND ENCRYPTION
   - Encryption required for data at rest and in transit
   - Encryption keys must be securely managed
   - Strong cryptographic algorithms must be used
   - Regular encryption key rotation

4. PHYSICAL AND ENVIRONMENTAL SECURITY
   - Secure facility with access controls and monitoring
   - Environmental protections (temperature, humidity, fire suppression)
   - Visitor management and escort procedures
   - Equipment security and protection from damage

5. OPERATIONS SECURITY
   - Change management procedures for system modifications
   - System monitoring and event logging
   - Capacity planning and performance management
   - Problem and incident management processes

6. INCIDENT MANAGEMENT
   - Incident detection and reporting procedures
   - Incident classification and severity determination
   - Incident investigation and response
   - Incident documentation and follow-up

7. BUSINESS CONTINUITY
   - Backup procedures with regular testing
   - Disaster recovery plans
   - Business continuity planning for critical services
   - Crisis management and communication procedures

8. COMPLIANCE
   - Identification of applicable laws and regulations
   - Compliance with contractual obligations
   - Regular compliance assessments and audits
   - Protection of intellectual property and confidential information
"""
    },
    "gdpr": {
        "title": "GDPR - General Data Protection Regulation (EU 2016/679)",
        "description": "EU regulation governing data protection and privacy.",
        "content": """
GDPR REQUIREMENTS:

1. DATA PROTECTION PRINCIPLES
   - Lawfulness, fairness, and transparency in processing
   - Purpose limitation - data used only for specified purposes
   - Data minimization - collect only necessary data
   - Accuracy of personal data
   - Storage limitation - retain only as long as necessary
   - Integrity and confidentiality through security measures
   - Accountability - demonstrate compliance

2. LEGAL BASIS FOR PROCESSING
   - Consent must be freely given, specific, informed, and unambiguous
   - Contract performance
   - Legal obligation compliance
   - Protection of vital interests
   - Public task performance
   - Legitimate interests (with balance test)

3. INDIVIDUALS' RIGHTS
   - Right to be informed about data processing
   - Right of access to personal data
   - Right to rectification of inaccurate data
   - Right to erasure (Right to be Forgotten)
   - Right to restrict processing
   - Right to data portability
   - Right to object to processing
   - Rights related to automated decision-making

4. DATA PROTECTION BY DESIGN AND DEFAULT
   - Implement privacy considerations from project initiation
   - Data protection impact assessments (DPIA) for high-risk processing
   - Pseudonymization and encryption of personal data
   - Ability to demonstrate compliance (accountability)

5. DATA BREACH NOTIFICATION
   - Breach to authority within 72 hours (if high risk)
   - Breach notification to individuals without undue delay
   - Breach documentation and investigation
   - Demonstration of no special risk to individuals

6. DATA PROTECTION OFFICER (DPO)
   - Designation required for public authorities and sensitive processing
   - Independence in role and reporting to highest management
   - Tasks include monitoring compliance, handling data subject requests
   - Acting as point of contact for authorities

7. INTERNATIONAL DATA TRANSFERS
   - Adequacy decisions for transfers to non-EU countries
   - Standard contractual clauses or binding corporate rules
   - Supplementary measures to ensure adequate protection
   - Lawful transfers mechanism in place

8. ORGANIZATIONAL REQUIREMENTS
   - Data processing agreements with processors and third parties
   - Record of processing activities documentation
   - Vendor management and processor accountability
   - Staff training and awareness programs
   - Incident response and crisis procedures
"""
    },
    "soc2": {
        "title": "SOC 2 Type II - Service Organization Control",
        "description": "Framework for service organizations' controls over security, availability, and confidentiality.",
        "content": """
SOC 2 TYPE II REQUIREMENTS:

1. COMMON CRITERIA (CC) - FOUNDATIONAL CONTROLS
   CC1: The organization demonstrates a commitment to competence and responsibility
   CC2: Board of directors and management maintain independence
   CC3: Individuals demonstrate competence to fulfill responsibilities
   CC4: Accountability is assigned and communicated
   CC5: Organization obtains and communicates information about objectives
   CC6: Confidentiality of information is restricted appropriately
   CC7: Planned and controlled information system changes
   CC8: Ongoing and periodic monitoring of internal controls
   CC9: Organization identifies, analyzes, and manages risks

2. AVAILABILITY PRINCIPLE
   Systems are available for operation and use to support objectives
   - Infrastructure supports system availability requirements
   - Availability targets documented (SLAs)
   - Monitoring of system availability and performance
   - Incident response for availability issues
   - Backup systems and recovery procedures
   - Disaster recovery testing

3. CONFIDENTIALITY PRINCIPLE
   Confidential information is protected from unauthorized disclosure
   - Encryption of sensitive data at rest and in transit
   - Access controls limiting data exposure
   - User authentication and authorization
   - Monitoring and logging of access attempts
   - Encryption key management procedures
   - Data classification and handling procedures

4. INTEGRITY PRINCIPLE
   System inputs, processing, and outputs are complete, accurate, and timely
   - System monitoring and error detection
   - Preventive and detective controls over transactions
   - Data validation and completeness checks
   - System reconciliation procedures
   - Access logging and audit trails
   - Change management controls

5. PRIVACY PRINCIPLE
   Personal information collected, used, and retained according to privacy objectives
   - Privacy policies and procedures documented
   - Consent mechanisms for data collection
   - Data minimization in collection and use
   - Individual rights honored (access, correction, deletion)
   - Vendor agreements include privacy requirements
   - Data retention policies and secure disposal

6. SECURITY CONTROLS REQUIRED
   - Multi-factor authentication for system access
   - Network segmentation and perimeter security
   - Vulnerability management and patch procedures
   - Antivirus/malware protection
   - Intrusion detection and prevention systems
   - Configuration management and baselines
   - Security awareness training
   - Physical security access controls

7. OPERATIONAL REQUIREMENTS
   - Change management with testing and approval
   - Segregation of duties in critical processes
   - Third-party/vendor management and monitoring
   - Service level agreements with defined metrics
   - Incident management and response procedures
   - Data backup and recovery testing
   - Audit logging covering entire assessment period

8. AUDIT TRAIL AND DOCUMENTATION
   - System audit logs retained and protected
   - Monitoring for suspicious activities
   - Log analysis and review procedures
   - Evidence of control operation over assessment period
   - Management's statements and representations
   - Auditor's findings and management responses
"""
    },
}


class KnowledgeBaseFallback:
    """Provides fallback compliance standards when KB is empty."""
    
    @staticmethod
    def get_fallback_documents() -> List[Document]:
        """Generate fallback compliance standard documents."""
        documents = []
        
        for standard_id, standard_info in COMPLIANCE_STANDARDS.items():
            doc = Document(
                page_content=standard_info["content"],
                metadata={
                    "source": f"fallback_{standard_id}",
                    "title": standard_info["title"],
                    "type": "compliance_standard",
                    "description": standard_info["description"],
                    "chunk": 0,
                }
            )
            documents.append(doc)
            logger.info(f"Generated fallback document: {standard_info['title']}")
        
        return documents
    
    @staticmethod
    def is_knowledge_base_empty(kb_path: Path) -> bool:
        """Check if knowledge base directory has PDF files."""
        if not kb_path.exists():
            return True
        
        pdf_files = list(kb_path.glob("*.pdf"))
        return len(pdf_files) == 0
    
    @staticmethod
    def get_fallback_summary() -> str:
        """Return summary of available fallback standards."""
        standards_list = "\n".join([
            f"• {info['title']}: {info['description']}"
            for info in COMPLIANCE_STANDARDS.values()
        ])
        
        return f"""
COMPLIANCE STANDARDS (Fallback Mode):

{standards_list}

Note: These are generic standards. For production use, add organization-specific 
compliance documents to the knowledge_base/ directory.
"""


def create_fallback_aware_retriever(kb_path: Path) -> Optional[List[Document]]:
    """Create retriever that falls back to generic standards if KB is empty.
    
    Args:
        kb_path: Path to knowledge base directory
        
    Returns:
        List of Document objects from KB or fallback standards
    """
    if KnowledgeBaseFallback.is_knowledge_base_empty(kb_path):
        logger.warning(f"Knowledge base empty at {kb_path}. Using fallback standards.")
        return KnowledgeBaseFallback.get_fallback_documents()
    
    return None  # Use normal KB loading


def inject_fallback_mode(agent_class):
    """Decorator to inject fallback mode into ComplianceAgent.
    
    Usage:
        @inject_fallback_mode
        class ComplianceAgent:
            ...
    """
    original_load_kb = agent_class._load_knowledge_base
    
    def _load_knowledge_base_with_fallback(self, knowledge_base_dir: Path):
        """Wrapped version with fallback support."""
        # Try normal loading
        try:
            return original_load_kb(self, knowledge_base_dir)
        except Exception as e:
            logger.warning(f"Failed to load KB: {e}. Using fallback standards.")
            # Use fallback
            fallback_docs = KnowledgeBaseFallback.get_fallback_documents()
            store = self.vector_manager.build_store(fallback_docs)
            summary = KnowledgeBaseFallback.get_fallback_summary()
            return store, summary
    
    agent_class._load_knowledge_base = _load_knowledge_base_with_fallback
    return agent_class


# Quick reference strings for common compliance gaps
COMMON_COMPLIANCE_GAPS = {
    "authentication": "Multi-factor authentication not implemented for critical systems",
    "encryption": "Data encryption at rest not implemented for sensitive information",
    "access_control": "User access reviews not performed regularly",
    "incident_response": "No documented incident response procedures",
    "backup_recovery": "Backup and recovery procedures not tested",
    "training": "Security awareness training not provided to staff",
    "documentation": "Security policies not documented or outdated",
    "monitoring": "System monitoring and logging not implemented",
    "vendor_management": "Third-party vendors not assessed for security controls",
    "change_management": "Changes to systems not tracked or approved",
}


if __name__ == "__main__":
    # Test fallback mode
    print("=" * 60)
    print("🧪 Testing Knowledge Base Fallback")
    print("=" * 60)
    print()
    
    # Check KB
    kb_path = Path("./ai_compliance_agent/knowledge_base")
    is_empty = KnowledgeBaseFallback.is_knowledge_base_empty(kb_path)
    
    print(f"Knowledge Base Path: {kb_path}")
    print(f"KB Status: {'EMPTY ⚠️' if is_empty else 'HAS FILES ✓'}")
    print()
    
    # Generate fallback docs
    print("Available fallback standards:")
    for standard_id, info in COMPLIANCE_STANDARDS.items():
        print(f"  ✓ {info['title']}")
    
    print()
    print("Fallback summary:")
    print(KnowledgeBaseFallback.get_fallback_summary())
