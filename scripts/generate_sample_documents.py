#!/usr/bin/env python3
"""
Generate sample compliance standard PDFs for testing.

Creates generic compliance documents based on:
- ISO 27001 (Information Security Management)
- GDPR (General Data Protection Regulation)
- SOC 2 (Service Organization Control)

Usage:
    python scripts/generate_sample_documents.py
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime


def create_iso_27001_pdf(output_path: Path) -> None:
    """Generate ISO 27001 Information Security Management standard."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1,  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        spaceBefore=12,
    )
    
    # Title
    story.append(Paragraph("ISO 27001:2022 - Information Security Management System", title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Introduction
    intro_text = """
    <b>Overview:</b> ISO 27001 is the international standard for Information Security Management Systems (ISMS).
    It provides requirements for establishing, implementing, maintaining, and continually improving an ISMS.
    Organizations use ISO 27001 to protect sensitive information and manage security risks.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Core Requirements
    story.append(Paragraph("Core Requirements:", heading_style))
    
    requirements = [
        ("1. Asset Management", "Organizations must identify and protect all information assets. This includes hardware, software, personnel, documentation, and services."),
        ("2. Access Control", "Restrict access to information and systems based on business requirements and the principle of least privilege."),
        ("3. Cryptography", "Implement cryptographic measures to protect information from unauthorized access, including encryption at rest and in transit."),
        ("4. Physical and Environmental Security", "Establish secure perimeters and entry controls. Protect facilities, equipment, and utilities from environmental hazards."),
        ("5. Operations Security", "Manage system operations including change management, capacity planning, and system monitoring."),
        ("6. Incident Management", "Establish procedures for detecting, assessing, and responding to security incidents."),
        ("7. Business Continuity", "Implement measures to ensure continuity of critical business functions during and after incidents."),
        ("8. Compliance", "Ensure compliance with applicable laws, regulations, and contractual obligations."),
    ]
    
    for req_title, req_desc in requirements:
        story.append(Paragraph(f"<b>{req_title}</b>", styles['Normal']))
        story.append(Paragraph(req_desc, styles['Normal']))
        story.append(Spacer(1, 0.15 * inch))
    
    story.append(PageBreak())
    
    # Control Objectives
    story.append(Paragraph("Control Objectives:", heading_style))
    
    control_text = """
    ISO 27001 requires implementation of controls across 14 control objectives:
    <br/><br/>
    • <b>A.5:</b> Organizational Controls - Policies, roles, responsibilities<br/>
    • <b>A.6:</b> People Controls - Training, awareness, competence<br/>
    • <b>A.7:</b> Governance Controls - Information security strategy<br/>
    • <b>A.8:</b> Asset Management - Asset inventory and protection<br/>
    • <b>A.9:</b> Access Control - User access and authentication<br/>
    • <b>A.10:</b> Cryptography - Encryption and key management<br/>
    • <b>A.11:</b> Physical Security - Premises and facility protection<br/>
    • <b>A.12:</b> Operations Security - Change and incident management<br/>
    • <b>A.13:</b> Communications Security - Network security and monitoring<br/>
    • <b>A.14:</b> System Acquisition - Secure development and procurement<br/>
    """
    story.append(Paragraph(control_text, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Implementation Timeline
    story.append(Paragraph("Typical Implementation Timeline:", heading_style))
    timeline_text = """
    Phase 1 (Months 1-2): Gap analysis, awareness training, establish governance<br/>
    Phase 2 (Months 3-4): Implement technical controls, access management<br/>
    Phase 3 (Months 5-6): Implement operational controls, incident procedures<br/>
    Phase 4 (Months 7-8): Internal audit, management review, certification readiness<br/>
    """
    story.append(Paragraph(timeline_text, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {output_path}")


def create_gdpr_pdf(output_path: Path) -> None:
    """Generate GDPR (General Data Protection Regulation) standard."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#003d7a'),
        spaceAfter=30,
        alignment=1,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#003d7a'),
        spaceAfter=12,
        spaceBefore=12,
    )
    
    story.append(Paragraph("GDPR - General Data Protection Regulation (EU 2016/679)", title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    intro_text = """
    <b>Overview:</b> GDPR is the European Union's data protection regulation that governs the processing of personal data.
    It applies to organizations worldwide that process data of EU residents. GDPR establishes principles for lawful,
    fair, and transparent data handling with individuals having rights over their personal information.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Key Principles
    story.append(Paragraph("Key Principles:", heading_style))
    principles = [
        ("Lawfulness, Fairness & Transparency", "Data processing must be lawful and fair. Individuals must be informed about how their data is used."),
        ("Purpose Limitation", "Personal data must be collected for specified, explicit, and legitimate purposes only."),
        ("Data Minimization", "Collect and process only the minimum necessary personal data required for the specified purpose."),
        ("Accuracy", "Keep personal data accurate and up-to-date. Implement procedures to rectify or erase inaccurate data."),
        ("Storage Limitation", "Retain personal data only as long as necessary for the original purpose."),
        ("Integrity and Confidentiality", "Process data securely using appropriate technical and organizational measures to prevent unauthorized access."),
        ("Accountability", "Demonstrate compliance through documentation, audits, and impact assessments."),
    ]
    
    for principle, description in principles:
        story.append(Paragraph(f"<b>{principle}:</b> {description}", styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
    
    story.append(PageBreak())
    
    # Rights of Data Subjects
    story.append(Paragraph("Rights of Data Subjects:", heading_style))
    rights_text = """
    <b>Right to be Informed:</b> Individuals must be informed when their data is collected and how it will be used.<br/><br/>
    <b>Right of Access:</b> Individuals can request a copy of their personal data within 30 days.<br/><br/>
    <b>Right to Rectification:</b> Individuals can correct inaccurate or incomplete personal data.<br/><br/>
    <b>Right to Erasure:</b> Individuals can request deletion of their data (Right to be Forgotten).<br/><br/>
    <b>Right to Restrict Processing:</b> Individuals can request limitation of how their data is processed.<br/><br/>
    <b>Right to Data Portability:</b> Individuals can receive their data in a structured, commonly-used format.<br/><br/>
    <b>Right to Object:</b> Individuals can object to processing for direct marketing and other purposes.<br/><br/>
    <b>Rights Related to Automated Processing:</b> Protection against automated decision-making and profiling.<br/>
    """
    story.append(Paragraph(rights_text, styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Key Requirements
    story.append(Paragraph("Key Requirements for Organizations:", heading_style))
    requirements_text = """
    • Obtain explicit consent before processing personal data (except in specific cases)<br/>
    • Conduct Data Protection Impact Assessments (DPIA) for high-risk processing<br/>
    • Document all processing activities (Record of Processing Activities - ROPA)<br/>
    • Implement Data Protection by Design and Default<br/>
    • Report data breaches to authorities within 72 hours<br/>
    • Designate a Data Protection Officer (DPO) if required<br/>
    • Establish Data Processing Agreements with third parties<br/>
    • Implement technical safeguards: encryption, access controls, monitoring<br/>
    • Retain audit logs and maintain documentation for accountability<br/>
    • Train employees on GDPR compliance and data handling<br/>
    """
    story.append(Paragraph(requirements_text, styles['Normal']))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # Penalties
    story.append(Paragraph("Penalties for Non-Compliance:", heading_style))
    penalties_text = """
    <b>Category 1 Violations:</b> Up to €10,000,000 or 2% of global annual turnover<br/>
    <b>Category 2 Violations:</b> Up to €20,000,000 or 4% of global annual turnover<br/>
    """
    story.append(Paragraph(penalties_text, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {output_path}")


def create_soc2_pdf(output_path: Path) -> None:
    """Generate SOC 2 (Service Organization Control) standard."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        spaceBefore=12,
    )
    
    story.append(Paragraph("SOC 2 - Service Organization Control Type II Compliance", title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    intro_text = """
    <b>Overview:</b> SOC 2 is a compliance framework for service organizations that deliver services affecting
    client data security, availability, processing integrity, confidentiality, and privacy. SOC 2 Type II reports
    provide evidence of effective controls over extended periods (typically 6+ months).
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Trust Service Criteria
    story.append(Paragraph("Five Trust Service Criteria (TSC):", heading_style))
    
    criteria = [
        ("CC - Common Criteria", "Foundation controls applicable to all service organizations. Includes governance, risk management, and information systems monitoring."),
        ("A - Availability", "Systems and services are available for operation and use to support objectives. Addresses uptime, disaster recovery, and business continuity."),
        ("C - Confidentiality", "Information designated as confidential is protected from unauthorized disclosure. Includes encryption, access controls, and monitoring."),
        ("I - Integrity", "System inputs, processing, and outputs are complete, accurate, and timely. Ensures data is protected and transactions are valid."),
        ("P - Privacy", "Personal information is collected, used, retained, and disclosed in accordance with privacy objectives. Covers data minimization and consent."),
    ]
    
    for criterion, description in criteria:
        story.append(Paragraph(f"<b>{criterion}:</b> {description}", styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
    
    story.append(PageBreak())
    
    # Common Control Activities
    story.append(Paragraph("Common Control Activities (CC):", heading_style))
    
    cc_controls = [
        "CC1: Governance - Organization demonstrates commitment to competence and responsibility",
        "CC2: Independence - Board of directors and management maintain independence",
        "CC3: Competence - Individuals demonstrate competence to fulfill responsibilities",
        "CC4: Accountability - Assignment and accountability for performance of duties",
        "CC5: Rights and Responsibilities - Information about objectives and responsibilities communicated",
        "CC6: Confidentiality - Confidentiality of information restricted appropriately",
        "CC7: Change Management - Planned and controlled information system changes",
        "CC8: Monitoring - Ongoing and periodic monitoring to assess effectiveness of controls",
        "CC9: Risk Assessment - Management evaluates organization's objectives and risks",
    ]
    
    for control in cc_controls:
        story.append(Paragraph(f"• {control}", styles['Normal']))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # Implementation Requirements
    story.append(Paragraph("Key Implementation Requirements:", heading_style))
    
    requirements_text = """
    <b>Security Controls:</b><br/>
    • Network security and segmentation<br/>
    • Access controls and authentication (MFA required)<br/>
    • Encryption of data at rest and in transit<br/>
    • System monitoring and logging<br/>
    • Incident response procedures<br/>
    <br/>
    <b>Operational Controls:</b><br/>
    • Change management procedures<br/>
    • Backup and recovery testing<br/>
    • Disaster recovery and business continuity plans<br/>
    • Personnel security and training<br/>
    • Vendor management and contracts<br/>
    <br/>
    <b>Evidence & Documentation:</b><br/>
    • System design and architecture documentation<br/>
    • Security policies and procedures<br/>
    • Audit logs covering entire audit period<br/>
    • Management assertions and certifications<br/>
    • External audit findings and management responses<br/>
    """
    story.append(Paragraph(requirements_text, styles['Normal']))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # SOC 2 Type II vs Type I
    story.append(Paragraph("SOC 2 Type II vs Type I:", heading_style))
    comparison_text = """
    <b>Type I:</b> Point-in-time assessment of control design and implementation effectiveness.<br/>
    Suitable for: Initial compliance, new services<br/>
    <br/>
    <b>Type II:</b> Assessment of control effectiveness over a period (typically 6-12 months).<br/>
    More rigorous than Type I. Demonstrates sustained compliance and operational effectiveness.<br/>
    Suitable for: Mature organizations, customer-facing services<br/>
    """
    story.append(Paragraph(comparison_text, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {output_path}")


def main():
    """Generate all sample PDF documents."""
    kb_dir = Path(__file__).parent.parent / "ai_compliance_agent" / "knowledge_base"
    kb_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("📄 Generating Sample Compliance Standard Documents")
    print("=" * 60)
    print()
    
    try:
        create_iso_27001_pdf(kb_dir / "ISO_27001_Standard.pdf")
        create_gdpr_pdf(kb_dir / "GDPR_Standard.pdf")
        create_soc2_pdf(kb_dir / "SOC2_Standard.pdf")
        
        print()
        print("=" * 60)
        print("✅ Successfully created sample documents!")
        print("=" * 60)
        print()
        print(f"📁 Location: {kb_dir}")
        print()
        print("Files created:")
        for pdf in sorted(kb_dir.glob("*.pdf")):
            size_mb = pdf.stat().st_size / (1024 * 1024)
            print(f"  ✓ {pdf.name} ({size_mb:.2f} MB)")
        
        print()
        print("📌 These documents are ready for analysis!")
        print("   Start the app: python -m ai_compliance_agent.ui_gradio")
        print()
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print()
        print("Install reportlab to generate PDFs:")
        print("  pip install reportlab")
        print()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generating PDFs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
