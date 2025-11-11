"""Configuration helpers for the AI compliance agent.

This module centralizes environment and runtime configuration to keep the rest of
the codebase clean. It relies on `.env` overrides for sensitive values while
providing reasonable defaults for local development.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables as soon as the module is imported.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Typed configuration values used across the project.
    
    Attributes:
        api_base_url: Base URL for OAuth2 PDF API (None for local mode)
        download_dir: Where to store downloaded PDFs
        knowledge_base_dir: Directory containing compliance standard PDFs
        local_pdf_dir: Optional directory for local PDF files
        ollama_model: Ollama model name (default: neural-chat for memory efficiency)
        faiss_index_dir: Optional directory for cached FAISS embeddings
    """

    api_base_url: Optional[str]
    download_dir: Path
    knowledge_base_dir: Path
    local_pdf_dir: Optional[Path] = None
    ollama_model: str = "neural-chat"  # Changed default from mistral to neural-chat
    faiss_index_dir: Optional[Path] = None

    def ensure_directories(self) -> None:
        """Create local directories that the pipeline expects to exist."""
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        if self.faiss_index_dir is not None:
            self.faiss_index_dir.mkdir(parents=True, exist_ok=True)
        if self.local_pdf_dir is not None:
            self.local_pdf_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Directories ready: %s", self.download_dir)


def _path_from_env(name: str, default: str) -> Path:
    """Resolve a path from environment variable or default."""
    value = os.getenv(name, default)
    return Path(value).expanduser().resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return memoized settings constructed from environment variables.
    
    Returns:
        Settings object with all configuration values.
        
    Raises:
        ValueError: If required paths are not accessible.
    """

    api_base_url = os.getenv("API_BASE_URL")

    download_dir = _path_from_env("DOWNLOAD_DIR", "./ai_compliance_agent/tmp_downloads")
    knowledge_base_dir = _path_from_env(
        "KNOWLEDGE_BASE_DIR", "./ai_compliance_agent/knowledge_base"
    )
    local_pdf_dir_env = os.getenv("LOCAL_PDF_DIR", "./ai_compliance_agent/local_pdfs")
    local_pdf_dir = Path(local_pdf_dir_env).expanduser().resolve() if local_pdf_dir_env else None
    
    faiss_index_dir_env = os.getenv("FAISS_INDEX_DIR")
    faiss_index_dir = None
    if faiss_index_dir_env:
        faiss_index_dir = Path(faiss_index_dir_env).expanduser().resolve()

    # Get model name with better default
    ollama_model = os.getenv("OLLAMA_MODEL", "neural-chat")
    logger.info("Using Ollama model: %s", ollama_model)

    settings = Settings(
        api_base_url=api_base_url.rstrip("/") if api_base_url else None,
        download_dir=download_dir,
        knowledge_base_dir=knowledge_base_dir,
        local_pdf_dir=local_pdf_dir,
        ollama_model=ollama_model,
        faiss_index_dir=faiss_index_dir,
    )
    settings.ensure_directories()
    return settings
