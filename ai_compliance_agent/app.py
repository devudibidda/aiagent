"""Command-line entry point for the AI compliance agent pipeline."""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .agent_pipeline import ComplianceAgent
from .config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyse PDFs for compliance gaps")
    parser.add_argument("pdf_id", help="Identifier of the PDF to fetch via the external API")
    parser.add_argument(
        "knowledge_base_path",
        help="Path to the knowledge base directory (expects PDF files and optional embeddings/)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    agent = ComplianceAgent(settings=settings)

    logger.info("Starting compliance analysis for PDF '%s'", args.pdf_id)
    result = agent.analyse(pdf_id=args.pdf_id, knowledge_base_path=Path(args.knowledge_base_path))

    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
