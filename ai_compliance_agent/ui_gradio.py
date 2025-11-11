"""Gradio UI wiring for the AI compliance agent."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import gradio as gr

from .agent_pipeline import ComplianceAgent
from .config import get_settings

logger = logging.getLogger(__name__)


def _format_sources(sources: list[Dict[str, Any]]) -> str:
    if not sources:
        return "No source documents were retrieved."
    lines = []
    for source in sources:
        lines.append(
            f"- {source.get('source', 'unknown')} | chunk {source.get('chunk', '?')}\n  {source.get('snippet', '')}"
        )
    return "\n".join(lines)


def build_interface(agent: ComplianceAgent) -> gr.Blocks:
    def analyse(pdf_id: str, knowledge_base_path: str) -> Dict[str, Any]:
        """Run compliance analysis with error handling and progress updates."""
        try:
            if not pdf_id.strip():
                return {
                    "status": "error",
                    "Analysis": "PDF ID is required",
                    "Document Summary": "",
                    "Knowledge Base Summary": "",
                    "Sources": "",
                }
            
            logger.info("Triggering analysis for %s using KB %s", pdf_id, knowledge_base_path)
            result = agent.analyse(
                pdf_id=pdf_id.strip(),
                knowledge_base_path=Path(knowledge_base_path)
            )
            
            return {
                "status": "success",
                "Analysis": result.get("analysis", ""),
                "Document Summary": result.get("document_summary", ""),
                "Knowledge Base Summary": result.get("knowledge_base_summary", ""),
                "Sources": _format_sources(result.get("sources", [])),
            }
        except FileNotFoundError as exc:
            logger.error("File not found: %s", exc)
            return {
                "status": "error",
                "Analysis": f"Error: {exc}",
                "Document Summary": "",
                "Knowledge Base Summary": "",
                "Sources": "",
            }
        except Exception as exc:
            logger.error("Analysis failed: %s", exc, exc_info=True)
            return {
                "status": "error",
                "Analysis": f"Analysis failed: {exc}",
                "Document Summary": "",
                "Knowledge Base Summary": "",
                "Sources": "",
            }

    with gr.Blocks(title="AI Compliance Agent") as demo:
        gr.Markdown(
            "# AI Compliance Agent\n"
            "Fetch, analyse, and compare PDFs against your standards.\n\n"
            "**Note:** Ensure Ollama is running (`ollama serve`) before analyzing documents."
        )

        with gr.Row():
            pdf_id = gr.Textbox(
                label="PDF ID",
                placeholder="12345 or /path/to/file.pdf",
                info="Local PDF path or API ID"
            )
            kb_path = gr.Textbox(
                label="Knowledge Base Path",
                value=str(get_settings().knowledge_base_dir),
                info="Folder containing standard PDFs",
            )

        analyse_button = gr.Button("Analyse Document", variant="primary")
        status_text = gr.Textbox(label="Status", interactive=False)

        with gr.Tabs():
            with gr.Tab("Results"):
                analysis_output = gr.Textbox(
                    label="Compliance Analysis",
                    lines=20,
                    max_lines=None,
                    interactive=False,
                    scale=1
                )
            with gr.Tab("Document Summary"):
                doc_summary = gr.Textbox(
                    label="Document Summary",
                    lines=25,
                    max_lines=None,
                    interactive=False,
                    scale=1
                )
            with gr.Tab("Knowledge Base Summary"):
                kb_summary = gr.Textbox(
                    label="Standards Summary",
                    lines=20,
                    max_lines=None,
                    interactive=False,
                    scale=1
                )
            with gr.Tab("Source Documents"):
                sources = gr.Textbox(
                    label="Retrieved Sources",
                    lines=20,
                    max_lines=None,
                    interactive=False,
                    scale=1
                )

        def run_analysis(pdf_id_val, kb_path_val):
            """Wrapper to extract fields from result dict."""
            result = analyse(pdf_id_val, kb_path_val)
            status = "✅ Success" if result.get("status") == "success" else "❌ Error"
            return (
                status,
                result.get("Analysis", ""),
                result.get("Document Summary", ""),
                result.get("Knowledge Base Summary", ""),
                result.get("Sources", ""),
            )

        analyse_button.click(
            run_analysis,
            inputs=[pdf_id, kb_path],
            outputs=[status_text, analysis_output, doc_summary, kb_summary, sources],
        )

    return demo


def launch() -> None:
    settings = get_settings()
    settings.ensure_directories()
    agent = ComplianceAgent(settings=settings)
    interface = build_interface(agent)
    interface.launch(server_name="127.0.0.1", server_port=7860, show_error=True)


if __name__ == "__main__":
    launch()

