"""PDF note ingestion and retrieval with ChromaDB."""

from __future__ import annotations

import logging
import re
import warnings
from io import BytesIO
from typing import TYPE_CHECKING

from chromadb.config import Settings as ChromaClientSettings
from chromadb.telemetry.product import ProductTelemetryClient, ProductTelemetryEvent
import fitz
from langchain_core.documents import Document
from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain_text_splitters import RecursiveCharacterTextSplitter
from overrides import override

from app.core.config import get_settings

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
        from langchain_community.vectorstores import Chroma


logger = logging.getLogger(__name__)


class NoOpChromaTelemetry(ProductTelemetryClient):
    """Chroma telemetry client that intentionally drops local telemetry events."""

    @override
    def capture(self, event: ProductTelemetryEvent) -> None:
        return None


class NotesRagService:
    """Ingests user PDF notes and retrieves relevant context from ChromaDB."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def collection_name(self, user_id: str) -> str:
        """Create a Chroma-safe per-user collection name."""

        safe_user_id = re.sub(r"[^A-Za-z0-9_-]+", "_", user_id).strip("_") or "default"
        name = f"notes_{safe_user_id}"[:63].strip("_-")
        return name if len(name) >= 3 else "notes_default"

    def chroma_client_settings(self) -> ChromaClientSettings:
        """Disable Chroma anonymized telemetry for cleaner local logs."""

        return ChromaClientSettings(
            anonymized_telemetry=False,
            chroma_product_telemetry_impl="app.services.rag.NoOpChromaTelemetry",
            chroma_telemetry_impl="app.services.rag.NoOpChromaTelemetry",
        )

    def embeddings(self) -> Embeddings:
        settings = get_settings()
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r'Field "model_name" has conflict with protected namespace "model_"\.',
                category=UserWarning,
                module=r"pydantic\._internal\._fields",
            )
            warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
            except ImportError:
                from langchain_community.embeddings import HuggingFaceEmbeddings

            return HuggingFaceEmbeddings(model_name=settings.embedding_model)

    def extract_pdf_text(self, pdf_bytes: bytes) -> list[Document]:
        """Extract text from PDF bytes with PyMuPDF."""

        documents: list[Document] = []
        with fitz.open(stream=BytesIO(pdf_bytes), filetype="pdf") as pdf:
            for page_index, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()
                if text:
                    documents.append(Document(page_content=text, metadata={"page": page_index}))
        return documents

    def ingest_notes(self, pdf_bytes: bytes, user_id: str) -> int:
        """Extract, chunk, and persist user PDF notes in a per-user collection."""

        settings = get_settings()
        collection = self.collection_name(user_id)
        raw_documents = self.extract_pdf_text(pdf_bytes)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        chunks = splitter.split_documents(raw_documents)

        vectorstore = Chroma(
            collection_name=collection,
            embedding_function=self.embeddings(),
            persist_directory=settings.chroma_persist_dir,
            client_settings=self.chroma_client_settings(),
        )
        try:
            vectorstore.delete_collection()
        except Exception as exc:
            logger.debug("Skipping Chroma collection deletion failure: %s", exc)

        if not chunks:
            return 0

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings(),
            collection_name=collection,
            persist_directory=settings.chroma_persist_dir,
            client_settings=self.chroma_client_settings(),
        )
        if hasattr(vectorstore, "persist"):
            vectorstore.persist()
        return len(chunks)

    def retrieve_notes_context(self, query: str, user_id: str, k: int = 6) -> str:
        """Retrieve relevant user-note chunks joined by newlines."""

        settings = get_settings()
        vectorstore = Chroma(
            collection_name=self.collection_name(user_id),
            embedding_function=self.embeddings(),
            persist_directory=settings.chroma_persist_dir,
            client_settings=self.chroma_client_settings(),
        )
        try:
            documents = vectorstore.similarity_search(query, k=k)
        except Exception:
            return ""
        return "\n".join(document.page_content for document in documents)


_default_rag_service = NotesRagService()


def ingest_notes(pdf_bytes: bytes, user_id: str) -> int:
    return _default_rag_service.ingest_notes(pdf_bytes, user_id)


def retrieve_notes_context(query: str, user_id: str, k: int = 6) -> str:
    return _default_rag_service.retrieve_notes_context(query, user_id, k)
