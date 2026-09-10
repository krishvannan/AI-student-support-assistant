"""
Vector Database Store for CampusAI.
Manages ChromaDB persistent vector database with document indexing and similarity search.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document

from utils.config import CHROMA_PERSIST_DIR, get_api_key
from rag.embeddings import get_embedding_function

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None


class ChromaVectorStore:
    """Manages document vector embeddings and ChromaDB persistent storage."""

    COLLECTION_NAME = "campus_ai_docs"

    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = Path(persist_directory or CHROMA_PERSIST_DIR)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collection = None
        self._memory_docs: List[Document] = []
        self._init_client()

    def _init_client(self) -> None:
        """Initialize Chroma persistent client and collection."""
        if chromadb:
            try:
                self._client = chromadb.PersistentClient(
                    path=str(self.persist_directory),
                    settings=Settings(anonymized_telemetry=False)
                )
                self._collection = self._client.get_or_create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"Warning: Could not initialize ChromaDB client ({e}). Running in-memory mode.")
                self._client = None
                self._collection = None

    def add_documents(self, documents: List[Document], batch_size: int = 50) -> int:
        """
        Embed and add documents to vector collection.
        Returns total number of chunks added.
        """
        if not documents:
            return 0

        embedder = get_embedding_function()

        if self._collection is not None:
            total_added = 0
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                texts = [doc.page_content for doc in batch]
                metadatas = [doc.metadata for doc in batch]
                ids = [f"{doc.metadata.get('source', 'doc')}_{doc.metadata.get('page', 1)}_{i + idx}" for idx, doc in enumerate(batch)]

                embeddings = embedder.embed_documents(texts)

                # Ensure all metadata values are str, int, float, or bool
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
        else:
            # In-memory storage fallback
            self._memory_docs.extend(documents)
            return len(documents)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Retrieve the top-k most relevant Document chunks for a query.
        """
        if not query or not query.strip():
            return []

        embedder = get_embedding_function()
        query_embedding = embedder.embed_query(query)

        if self._collection is not None:
            try:
                count = self._collection.count()
                if count == 0:
                    return []

                actual_k = min(k, count)
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
            except Exception as e:
                print(f"Error executing Chroma query: {e}")
                return []
        else:
            # Simple substring/cosine heuristic for in-memory fallback
            matches = []
            keywords = query.lower().split()
            for doc in self._memory_docs:
                text_lower = doc.page_content.lower()
                score = sum(1 for kw in keywords if kw in text_lower)
                if score > 0:
                    matches.append((score, doc))
            matches.sort(key=lambda x: x[0], reverse=True)
            return [doc for _, doc in matches[:k]]

    def get_document_count(self) -> int:
        """Return total number of chunks stored in vector store."""
        if self._collection is not None:
            try:
                return self._collection.count()
            except Exception:
                return 0
        return len(self._memory_docs)

    def get_indexed_files(self) -> List[str]:
        """Return unique source file names stored in vector store."""
        if self._collection is not None:
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
        return sorted(list({doc.metadata.get("source", "unknown") for doc in self._memory_docs}))

    def clear(self) -> None:
        """Clear all stored vectors from collection."""
        if self._collection is not None:
            try:
                self._client.delete_collection(name=self.COLLECTION_NAME)
                self._collection = self._client.create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"Error resetting collection: {e}")
        self._memory_docs = []


# Singleton instance
_vector_store_instance = None


def get_vector_store() -> ChromaVectorStore:
    """Get or create singleton instance of ChromaVectorStore."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = ChromaVectorStore()
    return _vector_store_instance
