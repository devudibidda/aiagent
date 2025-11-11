"""Configuration helpers for the AI compliance agent.

This module centralizes environment and runtime configuration to keep the rest of
the codebase clean. It relies on `.env` overrides for sensitive values while
providing reasonable defaults for local development.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables as soon as the module is imported.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Typed configuration values used across the project."""

    api_base_url: Optional[str]
    download_dir: Path
    knowledge_base_dir: Path
    local_pdf_dir: Optional[Path] = None
    ollama_model: str = "mistral"
    faiss_index_dir: Optional[Path] = None

    def ensure_directories(self) -> None:
        """Create local directories that the pipeline expects to exist."""
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        if self.faiss_index_dir is not None:
            self.faiss_index_dir.mkdir(parents=True, exist_ok=True)
        if self.local_pdf_dir is not None:
            self.local_pdf_dir.mkdir(parents=True, exist_ok=True)


def _path_from_env(name: str, default: str) -> Path:
    value = os.getenv(name, default)
    return Path(value).expanduser().resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return memoized settings constructed from environment variables."""

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

    settings = Settings(
        api_base_url=api_base_url.rstrip("/") if api_base_url else None,
        download_dir=download_dir,
        knowledge_base_dir=knowledge_base_dir,
        local_pdf_dir=local_pdf_dir,
        ollama_model=os.getenv("OLLAMA_MODEL", "mistral"),
        faiss_index_dir=faiss_index_dir,
    )
    settings.ensure_directories()
    return settings
