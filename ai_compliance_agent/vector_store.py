"""Vector store utilities backed by FAISS."""
from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Iterable, List, Optional

from langchain_classic.schema import Document as LCDocument

try:  # Prefer the newer langchain-huggingface package when available.
    from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore[import]
except ImportError:  # Fallback kept for compatibility with older environments.
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class VectorStoreManager:
    """Builds, loads, and combines FAISS indexes."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        self.model_name = model_name
        self._embedding = HuggingFaceEmbeddings(model_name=model_name)

    @property
    def embedding(self) -> HuggingFaceEmbeddings:
        return self._embedding

    def build_store(self, documents: Iterable[LCDocument]) -> FAISS:
        docs = list(documents)
        if not docs:
            raise ValueError("Cannot build FAISS store with no documents")
        logger.debug("Building FAISS index with %d documents", len(docs))
        return FAISS.from_documents(docs, self._embedding)

    def save_store(self, store: FAISS, directory: Path | str) -> None:
        target = Path(directory).expanduser().resolve()
        target.mkdir(parents=True, exist_ok=True)
        logger.debug("Persisting FAISS index to %s", target)
        store.save_local(folder_path=str(target))

    def load_store(self, directory: Path | str) -> FAISS:
        source = Path(directory).expanduser().resolve()
        index_file = source / "index.faiss"
        if not index_file.exists():
            raise FileNotFoundError(f"FAISS index not found at {index_file}")
        logger.debug("Loading FAISS index from %s", source)
        return FAISS.load_local(
            folder_path=str(source),
            embeddings=self._embedding,
            allow_dangerous_deserialization=True,
        )

    def try_load_store(self, directory: Path | str) -> Optional[FAISS]:
        try:
            return self.load_store(directory)
        except FileNotFoundError:
            return None

    def clone_store(self, store: FAISS) -> FAISS:
        """Deep copy a FAISS store so the original remains untouched."""
        return pickle.loads(pickle.dumps(store))

    def build_ensemble_retriever(self, retrievers, weights: Optional[List[float]] = None):
        """Return a weighted ensemble retriever from pre-built retrievers."""
        from langchain_classic.retrievers.ensemble import EnsembleRetriever

        return EnsembleRetriever(retrievers=retrievers, weights=weights)
