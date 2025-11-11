"""PDF ingestion utilities for the AI compliance agent."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

try:  # Prefer pypdf when available for better maintenance.
    from pypdf import PdfReader
except ImportError:  # Fall back to PyPDF2 if pypdf is missing.
    from PyPDF2 import PdfReader  # type: ignore

from langchain_classic.schema import Document as LCDocument
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


@dataclass
class PDFExtractionResult:
    """Container describing the outputs of PDF processing."""

    source_path: Path
    raw_text: str
    langchain_documents: List[LCDocument]
    chunks: List[str]


class PDFProcessor:
    """Extracts text from PDFs and prepares downstream artifacts."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def extract(self, pdf_path: Path | str) -> PDFExtractionResult:
        """Read a PDF file and return extracted text and chunked representations."""
        path = Path(pdf_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        logger.debug("Extracting text from %s", path)
        reader = PdfReader(str(path))
        pages_text: List[str] = []
        for page_number, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
            except Exception as exc:  # pragma: no cover - PyPDF internals vary.
                logger.warning("Failed to extract text from page %s (%s): %s", path, page_number, exc)
                page_text = ""
            pages_text.append(page_text.strip())

        raw_text = "\n\n".join(filter(None, pages_text))
        if not raw_text:
            logger.warning("No text extracted from %s", path)

        chunks = self.splitter.split_text(raw_text) if raw_text else []
        langchain_documents = [
            LCDocument(page_content=chunk, metadata={"source": str(path), "chunk": idx})
            for idx, chunk in enumerate(chunks)
        ]
        return PDFExtractionResult(
            source_path=path,
            raw_text=raw_text,
            langchain_documents=langchain_documents,
            chunks=chunks,
        )
