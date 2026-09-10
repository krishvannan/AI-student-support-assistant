"""
ChromaDB Persistent Vector Store Module for CampusAI.
Handles persistent vector indexing, semantic search, and document cataloging using ChromaDB.
"""

from pathlib import Path
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain_core.documents import Document

from utils.config import CHROMA_PERSIST_DIR, is_api_key_set
from rag.embeddings import get_embedding_function


class ChromaVectorStore:
    """Manages persistent ChromaDB vector store for college documents."""

    COLLECTION_NAME = "campus_ai_docs"

    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = Path(persist_directory or CHROMA_PERSIST_DIR)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[Document], batch_size: int = 50) -> int:
        """
        Embed and persist documents into ChromaDB.
        Returns total number of chunks successfully stored.
        """
        if not documents:
            return 0

        if not is_api_key_set():
            raise ValueError(
                "Gemini API key is required to embed documents. "
                "Please configure GEMINI_API_KEY in .env or the sidebar."
            )

        embedder = get_embedding_function()
        total_added = 0

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            texts = [doc.page_content for doc in batch]
            metadatas = [doc.metadata for doc in batch]
            ids = [
                f"{doc.metadata.get('source', 'doc')}_{doc.metadata.get('page', 1)}_{i + idx}"
                for idx, doc in enumerate(batch)
            ]

            # Generate real Gemini vector embeddings
            embeddings = embedder.embed_documents(texts)

            # Sanitize metadata to Chroma-compliant types (str, int, float, bool)
            sanitized_metadatas = []
            for m in metadatas:
                clean_m = {}
                for k, v in m.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean_m[k] = v
                    else:
                        clean_m[k] = str(v)
                sanitized_metadatas.append(clean_m)

            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=sanitized_metadatas
            )
            total_added += len(batch)

        return total_added

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Execute semantic cosine similarity search in ChromaDB.
        Returns top-k matching Document chunks.
        """
        if not query or not query.strip():
            return []

        if self._collection.count() == 0:
            return []

        if not is_api_key_set():
            raise ValueError("Gemini API key is required to perform vector similarity search.")

        embedder = get_embedding_function()
        query_embedding = embedder.embed_query(query)

        actual_k = min(k, self._collection.count())
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_k
        )

        documents: List[Document] = []
        if results and results.get("documents") and results["documents"][0]:
            docs_text = results["documents"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs_text)

            for text, meta in zip(docs_text, metadatas):
                documents.append(Document(page_content=text, metadata=meta))

        return documents

    def get_document_count(self) -> int:
        """Return total number of vector chunks stored in ChromaDB."""
        try:
            return self._collection.count()
        except Exception:
            return 0

    def get_indexed_files(self) -> List[str]:
        """Return distinct source document filenames stored in ChromaDB."""
        try:
            data = self._collection.get(include=["metadatas"])
            if data and data.get("metadatas"):
                files = set()
                for m in data["metadatas"]:
                    if m and "source" in m:
                        files.add(m["source"])
                return sorted(list(files))
        except Exception:
            pass
        return []

    def clear(self) -> None:
        """Delete and recreate the ChromaDB collection."""
        try:
            self._client.delete_collection(name=self.COLLECTION_NAME)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )


# Singleton instance
_vector_store_instance = None


def get_vector_store() -> ChromaVectorStore:
    """Get or create singleton instance of ChromaVectorStore."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = ChromaVectorStore()
    return _vector_store_instance
