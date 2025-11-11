#!/usr/bin/env python3
"""
Quick Start Guide - CIR-CIM Compliance Analysis System

This script demonstrates how to use the integrated system.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def example_1_module_imports():
    """Example 1: Import and verify all modules"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Module Imports")
    print("="*60)
    
    try:
        from cir_system.cim_analyzer import CIMDocumentAnalyzer
        from cir_system.cir_advanced_extractor import AdvancedCIRExtractor
        from cir_system.compliance_matcher import ComplianceMatcher
        from cir_system.cir_cim_pipeline import CIRCIMAnalysisPipeline
        from cir_system.table_generator import DynamicTableGenerator
        from cir_system.report_generator import ComplianceReportGenerator
        
        print("\n✓ All modules imported successfully")
        print("✓ System is ready for use")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def example_2_cim_extraction():
    """Example 2: Extract requirements from CIM document"""
    print("\n" + "="*60)
    print("EXAMPLE 2: CIM Requirement Extraction")
    print("="*60)
    
    from cir_system.cim_analyzer import CIMDocumentAnalyzer
    
    # Sample CIM text (in real use, read from PDF)
    sample_cim = """
    CIM Case ID: CIM-2024-STD-001
    
    AFFECTED COMPONENTS:
    - Gearbox Drive Train
    - Bearing Housing
    - Main Shaft
    
    FAILURE MODE: Unusual vibration and noise
    
    COMPLIANCE REQUIREMENTS:
    
    1. VISUAL INSPECTION:
       All bearing surfaces must be visually inspected for
       cracks, discoloration, or deformation.
       Evidence Required: High-resolution photos
       Test Method: Visual inspection with documentation
    
    2. VIBRATION ANALYSIS:
       Vibration measurements required at multiple points.
       Acceptance Standard: < 3mm/s RMS at all locations
       Test Method: Accelerometer with FFT
    
    3. OIL ANALYSIS:
       Gearbox oil must be laboratory tested for
       metallic particles indicating wear.
       Evidence Required: Laboratory certificate
       Acceptance: Particle count within limits
    """
    
    analyzer = CIMDocumentAnalyzer()
    analysis = analyzer.analyze_cim_document(sample_cim)
    
    print(f"\n✓ Case ID: {analysis.cim_case_id}")
    print(f"✓ Components affected: {', '.join(analysis.affected_components)}")
    print(f"✓ Failure modes: {', '.join(analysis.failure_types)}")
    print(f"✓ Requirements extracted: {len(analysis.requirements)}")
    
    for req in analysis.requirements:
        print(f"\n  [{req.requirement_type.upper()}] {req.title}")
        print(f"    Severity: {req.severity}")
        print(f"    Components: {', '.join(req.applicable_components)}")


def example_3_cir_extraction():
    """Example 3: Extract metadata from CIR document"""
    print("\n" + "="*60)
    print("EXAMPLE 3: CIR Metadata Extraction")
    print("="*60)
    
    from cir_system.cir_advanced_extractor import AdvancedCIRExtractor
    
    # Sample CIR text (in real use, read from PDF)
    sample_cir = """
    SERVICE REPORT
    
    CIR ID: CIR-2024-STD-001
    Report Type: Service Visit Report
    Service Report Number: SR-2024-0001
    
    TURBINE INFORMATION
    Turbine ID: V136-001
    WTG ID: WTG-42
    Turbine Type: V136-4.2MW
    MK Version: 5.0
    Country: Germany
    Site: Vestas Green Park
    
    COMPONENT: Gearbox Drive Train
    Manufacturer: Vestas
    Serial Number: GB-20240001
    
    SERVICE DETAILS
    Service Date: 2024-01-15
    Technician: John Smith
    
    INSPECTION FINDINGS:
    - Visual: No cracks or deformation detected
    - Photos: inspection_01.jpg, inspection_02.jpg
    - Oil Analysis: Laboratory cert OIL-001
    - Vibration Point A: 2.1 mm/s RMS
    - Vibration Point B: 1.9 mm/s RMS
    - Vibration Point C: 2.3 mm/s RMS
    
    STATUS: All checks passed - Ready for operation
    """
    
    extractor = AdvancedCIRExtractor()
    metadata = extractor.extract_metadata(sample_cir)
    
    print(f"\n✓ Extracted {len(metadata.all_fields)} metadata fields:")
    
    priority_fields = ["CIR ID", "Turbine ID", "Component", 
                       "Service Date", "Technician"]
    
    for field in priority_fields:
        if field in metadata.all_fields:
            value = metadata.all_fields[field]
            print(f"  {field}: {value}")


def example_4_compliance_assessment():
    """Example 4: Assess compliance"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Compliance Assessment")
    print("="*60)
    
    from cir_system.cim_analyzer import CIMDocumentAnalyzer
    from cir_system.cir_advanced_extractor import AdvancedCIRExtractor
    from cir_system.compliance_matcher import ComplianceMatcher
    
    # Extract CIM requirements
    sample_cim = """
    CIM Case: CIM-001
    
    REQUIREMENT 1: VISUAL INSPECTION
    Description: Bearing surfaces must be inspected for defects
    Evidence Required: Photos, Documentation
    
    REQUIREMENT 2: VIBRATION ANALYSIS
    Description: Vibration must be measured at multiple points
    Acceptance: < 3mm/s RMS
    
    REQUIREMENT 3: OIL ANALYSIS
    Description: Oil must be laboratory tested
    Evidence Required: Certificate
    """
    
    analyzer = CIMDocumentAnalyzer()
    cim_analysis = analyzer.analyze_cim_document(sample_cim)
    
    # Extract CIR metadata
    sample_cir = """
    CIR-2024-001
    Status: Service completed
    
    Visual inspection completed - no defects found
    Photos attached: IMG_001.jpg, IMG_002.jpg
    
    Vibration measurements:
    Point A: 2.1 mm/s RMS
    Point B: 1.9 mm/s RMS
    Point C: 2.3 mm/s RMS
    All within acceptable limits
    
    Oil analysis: Laboratory certificate OIL-2024-001
    Result: Normal condition
    """
    
    extractor = AdvancedCIRExtractor()
    cir_metadata = extractor.extract_metadata(sample_cir)
    
    # Assess compliance
    matcher = ComplianceMatcher()
    evidence_list, summary = matcher.assess_compliance(
        cir_text=sample_cir,
        cir_metadata=cir_metadata.all_fields,
        cim_requirements=cim_analysis.requirements,
        cim_metadata={}
    )
    
    print(f"\n✓ Compliance Score: {summary.get('compliance_score', 0):.1f}%")
    print(f"✓ Status: {summary.get('go_nogo', 'N/A')}")
    print(f"✓ Met: {summary.get('met', 0)} / Partial: {summary.get('partial', 0)} / Not Met: {summary.get('not_met', 0)}")


def example_5_generate_table():
    """Example 5: Generate compliance table"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Generate Tables")
    print("="*60)
    
    from cir_system.table_generator import DynamicTableGenerator
    
    table_gen = DynamicTableGenerator()
    
    # Sample compliance summary
    summary = {
        "compliance_score": 92.5,
        "go_nogo": "GO",
        "met": 8,
        "partial": 1,
        "not_met": 0,
        "total_requirements": 9
    }
    
    print("\n" + table_gen.generate_summary_statistics(summary))


def example_6_pipeline():
    """Example 6: Use integrated pipeline"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Integrated Pipeline")
    print("="*60)
    
    from cir_system.cir_cim_pipeline import CIRCIMAnalysisPipeline
    
    print("\nPipeline Architecture:")
    print("  1. CIM Analysis - Extract compliance requirements")
    print("  2. CIR Extraction - Extract metadata and evidence")
    print("  3. Compliance Matching - Assess evidence against requirements")
    print("  4. Report Generation - Create Excel files")
    print("  5. Table Generation - Format for display")
    
    print("\nUsage:")
    print("  pipeline = CIRCIMAnalysisPipeline()")
    print("  results = pipeline.analyze_pair('cir.pdf', 'cim.pdf')")
    print("  batch = pipeline.analyze_batch('cir_dir/', 'cim.pdf')")
    print("  stats = pipeline.get_summary_statistics(batch)")


def main():
    """Run all examples"""
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " QUICK START GUIDE - CIR-CIM ANALYSIS SYSTEM ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    # Run examples
    if not example_1_module_imports():
        print("\n✗ System not ready. Please install dependencies:")
        print("  pip install -r cir_system/requirements.txt")
        return
    
    example_2_cim_extraction()
    example_3_cir_extraction()
    example_4_compliance_assessment()
    example_5_generate_table()
    example_6_pipeline()
    
    # Summary
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    
    print("""
1. PREPARE DOCUMENTS:
   - Place CIM documents in: cir_system/knowledge_base/
   - Place CIR PDFs in: ai_compliance_agent/local_pdfs/

2. RUN ANALYSIS:
   from cir_system.cir_cim_pipeline import CIRCIMAnalysisPipeline
   
   pipeline = CIRCIMAnalysisPipeline()
   results = pipeline.analyze_pair('cir.pdf', 'cim.pdf')

3. GENERATE REPORTS:
   from cir_system.report_generator import ComplianceReportGenerator
   
   gen = ComplianceReportGenerator()
   excel_file = gen.generate_report(
       report_name="Analysis_2024",
       cir_metadata_list=[results["cir_metadata"]],
       compliance_evidence_list=[results["compliance_evidence"]],
       cim_requirements=results["cim_requirements"]
   )

4. BATCH PROCESSING:
   batch = pipeline.analyze_batch(
       cir_pdf_dir="./documents/cirs/",
       cim_pdf_path="./documents/cim_reference.pdf",
       max_files=1000
   )
   
   stats = pipeline.get_summary_statistics(batch)
   print(f"GO: {stats['go_percentage']:.1f}%")
   print(f"Average Score: {stats['average_compliance_score']:.1f}%")

5. DOCUMENTATION:
   - See: CIR_SYSTEM_COMPLETE_INTEGRATION.md
   - System Architecture & Configuration Details
""")
    
    print("="*60)
    print("✓ System is ready for production use!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
