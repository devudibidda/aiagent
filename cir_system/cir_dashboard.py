"""
Gradio UI for CIR Batch Analysis Dashboard
"""

import logging
import json
from pathlib import Path
import gradio as gr
from typing import Dict, Any

from .cir_batch_processor import CIRBatchProcessor
from .cir_ocr_extractor import extract_cir_pdf

logger = logging.getLogger(__name__)


class CIRDashboard:
    """Gradio dashboard for CIR analysis"""
    
    def __init__(self, output_dir: str = "./cir_output"):
        self.processor = CIRBatchProcessor(output_dir=output_dir)
        self.last_summary = None
    
    def process_batch(self, pdf_folder: str) -> tuple:
        """Process all PDFs in folder"""
        try:
            if not Path(pdf_folder).exists():
                return "Error: Folder not found", "", "", ""
            
            # Process batch
            def progress_callback(current, total, message):
                pass  # Gradio handles progress
            
            summary = self.processor.process_directory(
                pdf_folder,
                progress_callback=progress_callback
            )
            
            self.last_summary = summary
            
            # Generate report
            report = self._generate_summary_report(summary)
            go_nogo_report = self._generate_go_nogo_report(summary)
            
            return (
                f"✅ Processing complete: {summary['successfully_processed']}/{summary['total_files']} successful",
                report,
                go_nogo_report,
                self._generate_detailed_table()
            )
        
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            return f"Error: {e}", "", "", ""
    
    def process_single(self, pdf_path: str) -> tuple:
        """Process single PDF"""
        try:
            if not Path(pdf_path).exists():
                return "Error: File not found", "", "", ""
            
            result = self.processor.process_single_pdf(pdf_path)
            
            if result["status"] == "success":
                doc = result["document"]
                
                # Create detailed display
                details = f"""
FILE INFORMATION:
• Filename: {result['filename']}
• CIR Number: {result['cir_number']}
• File Size: {result['file_size_mb']:.2f} MB
• Pages: {result['page_count']}
• OCR Confidence: {result['ocr_confidence']:.1f}%

COMPLIANCE STATUS:
• Status: {'✅ GO' if result['compliance']['status'] == 'GO' else '❌ NO-GO'}
• Score: {result['compliance']['score']:.1f}%
• Passed Checks: {result['compliance']['passed_checks']}
• Failed Checks: {result['compliance']['failed_checks']}
• Critical Issues: {result['compliance']['critical_issues']}

TECHNICAL DATA:
• Component: {doc['technical_data'].get('component_name', 'N/A')}
• Part Number: {doc['technical_data'].get('part_number', 'N/A')}
• Drawing Number: {doc['technical_data'].get('drawing_number', 'N/A')}
• Revision: {doc['technical_data'].get('revision', 'N/A')}

CHANGE DETAILS:
• Change Type: {doc['change_details'].get('change_type', 'N/A')}
• Owner: {doc['change_details'].get('change_owner', 'N/A')}
• Implementation: {doc['change_details'].get('implementation_date', 'N/A')}
"""
                
                text_preview = doc['full_text_content'][:2000] + "..." if len(doc['full_text_content']) > 2000 else doc['full_text_content']
                
                return (
                    f"✅ File processed successfully",
                    details,
                    json.dumps(result, indent=2),
                    text_preview
                )
            else:
                return f"❌ Error: {result.get('error', 'Unknown error')}", "", "", ""
        
        except Exception as e:
            logger.error(f"Single PDF processing error: {e}")
            return f"Error: {e}", "", "", ""
    
    def _generate_summary_report(self, summary: Dict) -> str:
        """Generate summary report"""
        report = f"""
BATCH PROCESSING SUMMARY
{'='*60}

Total Files: {summary['total_files']}
Successfully Processed: {summary['successfully_processed']}
Failed: {summary['failed']}

GO Status: {summary['go_count']} ({summary['go_count']/max(1, summary['successfully_processed'])*100:.1f}%)
NO-GO Status: {summary['nogo_count']} ({summary['nogo_count']/max(1, summary['successfully_processed'])*100:.1f}%)

Processing Period:
• Started: {summary['start_time']}
• Completed: {summary['end_time']}

{'='*60}
"""
        return report
    
    def _generate_go_nogo_report(self, summary: Dict) -> str:
        """Generate detailed GO/NO-GO report"""
        go_nogo = self.processor.get_go_nogo_report()
        
        report = f"""
GO/NO-GO DETAILED REPORT
{'='*60}

SUMMARY:
• Total Documents: {go_nogo['total']}
• GO (Compliant): {go_nogo['go']} ({go_nogo['go_percentage']:.1f}%)
• NO-GO (Non-compliant): {go_nogo['nogo']}

GO DOCUMENTS ({go_nogo['go']}):
"""
        for f in go_nogo['go_files']:
            report += f"✅ {f['filename']} (CIR: {f['cir_number']}, Score: {f['score']:.1f}%)\n"
        
        report += f"\nNO-GO DOCUMENTS ({go_nogo['nogo']}):\n"
        for f in go_nogo['nogo_files']:
            report += f"❌ {f['filename']} (CIR: {f['cir_number']}, Score: {f['score']:.1f}%)\n"
        
        report += f"\n{'='*60}"
        return report
    
    def _generate_detailed_table(self) -> str:
        """Generate detailed table of all results"""
        if not self.processor.results:
            return "No results available"
        
        table = "FILENAME | CIR# | STATUS | SCORE | CRITICAL ISSUES\n"
        table += "-" * 80 + "\n"
        
        for result in self.processor.results:
            if result["status"] == "success":
                status = "GO" if result["compliance"]["status"] == "GO" else "NO-GO"
                table += f"{result['filename'][:20]} | {result['cir_number'][:10]} | {status} | {result['compliance']['score']:.1f}% | {result['compliance']['critical_issues']}\n"
        
        return table


def build_cir_dashboard() -> gr.Blocks:
    """Build Gradio dashboard"""
    
    dashboard = CIRDashboard()
    
    with gr.Blocks(title="Vestas CIR Analysis Dashboard") as demo:
        gr.Markdown(
            """
# 🏭 Vestas CIR Analysis System
## Change Impact Report - Batch Processing & Compliance Validation
            """
        )
        
        with gr.Tabs():
            # Batch Processing Tab
            with gr.Tab("📦 Batch Processing"):
                gr.Markdown("### Process hundreds or thousands of CIR PDFs")
                
                with gr.Row():
                    batch_folder = gr.Textbox(
                        label="PDF Folder Path",
                        placeholder="/path/to/cir_pdfs",
                        info="Path containing CIR PDF files"
                    )
                
                batch_button = gr.Button("🚀 Process Batch", variant="primary", scale=1)
                batch_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Tabs():
                    with gr.Tab("Summary"):
                        batch_summary = gr.Textbox(
                            label="Processing Summary",
                            lines=15,
                            interactive=False
                        )
                    
                    with gr.Tab("GO/NO-GO Report"):
                        go_nogo_report = gr.Textbox(
                            label="Compliance Report",
                            lines=20,
                            interactive=False
                        )
                    
                    with gr.Tab("Detailed Results"):
                        detailed_table = gr.Textbox(
                            label="All Documents",
                            lines=25,
                            interactive=False
                        )
                
                batch_button.click(
                    dashboard.process_batch,
                    inputs=[batch_folder],
                    outputs=[batch_status, batch_summary, go_nogo_report, detailed_table]
                )
            
            # Single File Tab
            with gr.Tab("📄 Single Document"):
                gr.Markdown("### Analyze a single CIR PDF")
                
                with gr.Row():
                    single_file = gr.Textbox(
                        label="PDF File Path",
                        placeholder="/path/to/document.pdf",
                        info="Path to CIR PDF file"
                    )
                
                single_button = gr.Button("🔍 Analyze", variant="primary")
                single_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Tabs():
                    with gr.Tab("Details"):
                        single_details = gr.Textbox(
                            label="Document Details",
                            lines=20,
                            interactive=False
                        )
                    
                    with gr.Tab("JSON"):
                        single_json = gr.Textbox(
                            label="Structured Data (JSON)",
                            lines=20,
                            interactive=False
                        )
                    
                    with gr.Tab("Text"):
                        single_text = gr.Textbox(
                            label="Extracted Text",
                            lines=25,
                            interactive=False
                        )
                
                single_button.click(
                    dashboard.process_single,
                    inputs=[single_file],
                    outputs=[single_status, single_details, single_json, single_text]
                )
            
            # Info Tab
            with gr.Tab("ℹ️ Information"):
                gr.Markdown("""
### Vestas CIR Analysis System

This system processes Vestas Change Impact Report (CIR) documents to:

1. **Extract Content**: Uses OCR to extract text and images from PDFs
2. **Validate Compliance**: Checks against Vestas CIR standards
3. **Generate Reports**: GO/NO-GO compliance status for each document
4. **Batch Processing**: Handle thousands of PDFs efficiently

#### Features:
- ✅ OCR text extraction with confidence scoring
- ✅ Automatic data extraction (component, change type, etc.)
- ✅ Comprehensive compliance validation
- ✅ GO/NO-GO status determination
- ✅ JSON output for easy integration
- ✅ Batch processing with progress tracking
- ✅ Summary reports and analytics

#### Compliance Checks:
- Document metadata and identifiers
- Technical data completeness
- Change documentation
- Approval evidence
- Quality metrics
- OCR confidence levels

#### Output Format:
All results are saved as JSON files in the output folder with:
- Document metadata
- Extracted technical data
- Change details
- Compliance validation results
- Critical issues and warnings
- Extracted text and images

""")
    
    return demo


def launch() -> None:
    """Launch the CIR analysis dashboard"""
    interface = build_cir_dashboard()
    interface.launch(server_name="127.0.0.1", server_port=7860, show_error=True)


if __name__ == "__main__":
    launch()
