"""High-level pipeline orchestration for compliance analysis."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.prompts import PromptTemplate

try:  # Prefer the dedicated langchain-ollama integration when available.
    from langchain_ollama import ChatOllama  # type: ignore[import]
except ImportError:  # Fallback to the legacy community implementation.
    from langchain_community.chat_models.ollama import ChatOllama

from .api_client import APIClient, OAuthConfig
from .config import Settings, get_settings
from .pdf_processor import PDFProcessor
from .vector_store import VectorStoreManager

logger = logging.getLogger(__name__)


class ComplianceAgent:
    """Coordinates document retrieval, embedding, and RAG analysis."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.api_client: Optional[APIClient] = None
        if self.settings.api_base_url:
            oauth_config = OAuthConfig.from_env()
            self.api_client = APIClient(
                base_url=self.settings.api_base_url,
                auth_config=oauth_config,
            )
        self.pdf_processor = PDFProcessor()
        self.vector_manager = VectorStoreManager()
        self.llm = ChatOllama(model=self.settings.ollama_model, temperature=0)
        self.compliance_query = "Analyse this document for compliance gaps against the provided standards."

    def download_pdf(self, pdf_id: str) -> Path:
        pdf_id_path = Path(pdf_id)
        filename = (
            pdf_id_path.name
            if pdf_id_path.suffix.lower() == ".pdf"
            else f"{pdf_id}.pdf"
        )
        output_path = self.settings.download_dir / filename
        if self.api_client is not None:
            return self.api_client.fetch_pdf(pdf_id, output_path)

        # Local/offline mode: copy from provided path or local PDF directory.
        candidate_path = Path(pdf_id).expanduser()
        if candidate_path.is_file():
            source_path = candidate_path.resolve()
        else:
            if not self.settings.local_pdf_dir:
                raise ValueError(
                    "LOCAL_PDF_DIR must be configured in offline mode or provide a full path."
                )
            source_path = (self.settings.local_pdf_dir / f"{pdf_id}.pdf").resolve()
            if not source_path.exists():
                raise FileNotFoundError(f"Local PDF not found at {source_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, output_path)
        logger.info("Copied local PDF %s to %s", source_path, output_path)
        return output_path

    def _summarise_chunks(self, chunks: List[str], context_label: str) -> str:
        if not chunks:
            return "No textual content detected."
        limited_chunks = "\n\n".join(chunks[:5])
        summary_prompt = (
            "You are a compliance analyst. Summarise the following content with a focus on"
            f" {context_label}. Provide exactly four concise bullet points highlighting key"
            " themes, risks, or requirements.\n\nCONTENT:\n"
            f"{limited_chunks}"
        )
        response = self.llm.invoke(summary_prompt)
        return getattr(response, "content", None) or str(response)

    def _load_knowledge_base(
        self, knowledge_base_dir: Path
    ) -> tuple[Optional[object], Optional[str]]:
        """Load or build knowledge base artifacts.

        Returns a tuple of (vector_store, summary_text).
        """
        embeddings_dir = knowledge_base_dir / "embeddings"

        kb_langchain_docs: List = []
        kb_chunks: List[str] = []

        for pdf_file in sorted(knowledge_base_dir.glob("*.pdf")):
            try:
                result = self.pdf_processor.extract(pdf_file)
            except Exception as exc:  # pragma: no cover - defensive.
                logger.warning("Skipping knowledge base file %s: %s", pdf_file, exc)
                continue
            kb_langchain_docs.extend(result.langchain_documents)
            kb_chunks.extend(result.chunks)

        store = self.vector_manager.try_load_store(embeddings_dir)
        if store is not None:
            logger.info("Loaded cached knowledge-base embeddings from %s", embeddings_dir)
        elif kb_langchain_docs:
            store = self.vector_manager.build_store(kb_langchain_docs)
            try:
                self.vector_manager.save_store(store, embeddings_dir)
            except Exception as exc:  # pragma: no cover - disk issues
                logger.warning("Failed to persist knowledge base embeddings: %s", exc)

        kb_summary = None
        if kb_chunks:
            kb_summary = self._summarise_chunks(kb_chunks, "the knowledge base standards")

        return store, kb_summary

    def analyse(self, pdf_id: str, knowledge_base_path: Path | str) -> Dict[str, object]:
        knowledge_base_dir = Path(knowledge_base_path).expanduser().resolve()
        if not knowledge_base_dir.exists():
            raise FileNotFoundError(f"Knowledge base path not found: {knowledge_base_dir}")

        pdf_path = self.download_pdf(pdf_id)
        pdf_result = self.pdf_processor.extract(pdf_path)
        pdf_summary = self._summarise_chunks(pdf_result.chunks, "the document under review")

        doc_store = None
        if pdf_result.langchain_documents:
            doc_store = self.vector_manager.build_store(pdf_result.langchain_documents)

        kb_store, kb_summary = self._load_knowledge_base(knowledge_base_dir)

        retrievers = []
        weights = []
        if kb_store is not None:
            retrievers.append(kb_store.as_retriever(search_kwargs={"k": 4}))
            weights.append(0.6)
        if doc_store is not None:
            retrievers.append(doc_store.as_retriever(search_kwargs={"k": 4}))
            weights.append(0.4)

        if not retrievers:
            raise RuntimeError("No document content available for retrieval")

        if len(retrievers) == 1:
            retriever = retrievers[0]
        else:
            retriever = self.vector_manager.build_ensemble_retriever(retrievers, weights=weights)

        base_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are a compliance analyst. Use the provided context to compare the"
                " document against the relevant standards and provide: \n"
                "1. Key areas where the document aligns with the standards.\n"
                "2. Gaps or missing requirements.\n"
                "3. Recommended remediation steps.\n\n"
                "Knowledge base overview:\n{knowledge_base_summary}\n\n"
                "Document summary:\n{document_summary}\n\n"
                "Context:\n{context}\n\n"
                "Question: {question}"
            ),
        )

        prompt = base_prompt.partial(
            knowledge_base_summary=kb_summary or "No knowledge base summary available.",
            document_summary=pdf_summary,
        )

        source_documents = retriever.get_relevant_documents(self.compliance_query)
        context_text = "\n\n".join(doc.page_content for doc in source_documents)
        prompt_text = prompt.format(
            context=context_text,
            question=self.compliance_query,
        )

        llm_response = self.llm.invoke(prompt_text)
        answer = getattr(llm_response, "content", None) or str(llm_response)

        sources = [
            {
                "source": doc.metadata.get("source"),
                "chunk": doc.metadata.get("chunk"),
                "snippet": doc.page_content[:300],
            }
            for doc in source_documents
        ]

        return {
            "analysis": answer,
            "sources": sources,
            "document_summary": pdf_summary,
            "knowledge_base_summary": kb_summary,
        }
