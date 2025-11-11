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
        logger.info("Triggering analysis for %s using KB %s", pdf_id, knowledge_base_path)
        result = agent.analyse(pdf_id=pdf_id.strip(), knowledge_base_path=Path(knowledge_base_path))
        return {
            "Analysis": result.get("analysis", ""),
            "Document Summary": result.get("document_summary", ""),
            "Knowledge Base Summary": result.get("knowledge_base_summary", ""),
            "Sources": _format_sources(result.get("sources", [])),
        }

    with gr.Blocks(title="AI Compliance Agent") as demo:
        gr.Markdown("# AI Compliance Agent\nFetch, analyse, and compare PDFs against your standards.")

        with gr.Row():
            pdf_id = gr.Textbox(label="PDF ID", placeholder="12345")
            kb_path = gr.Textbox(
                label="Knowledge Base Path",
                value=str(get_settings().knowledge_base_dir),
            )

        analyse_button = gr.Button("Analyse Document")

        output = gr.JSON(label="Results")

        analyse_button.click(
            analyse,
            inputs=[pdf_id, kb_path],
            outputs=[output],
        )

    return demo


def launch() -> None:
    settings = get_settings()
    agent = ComplianceAgent(settings=settings)
    interface = build_interface(agent)
    interface.launch(server_port=7860)


if __name__ == "__main__":
    launch()
