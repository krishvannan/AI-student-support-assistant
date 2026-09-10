"""
Embeddings Module for CampusAI.
Integrates Google Gemini text embeddings using LangChain with fallback capabilities.
"""

from typing import List, Optional
import numpy as np
from utils.config import get_api_key, EMBEDDING_MODEL

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    GoogleGenerativeAIEmbeddings = None


class FallbackEmbeddings:
    """
    Deterministic pseudo-embeddings for offline testing or pre-API key startup.
    Ensures vectorstore methods do not crash before API key configuration.
    """
    def __init__(self, dimension: int = 768):
        self.dimension = dimension

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            embeddings.append(self._hash_text(text))
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        return self._hash_text(text)

    def _hash_text(self, text: str) -> List[float]:
        np.random.seed(abs(hash(text)) % (2**32))
        vec = np.random.randn(self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


def get_embedding_function(api_key: Optional[str] = None):
    """
    Get configured embedding model.
    Uses GoogleGenerativeAIEmbeddings if API key is present; otherwise returns FallbackEmbeddings.
    """
    key = api_key or get_api_key()

    if key and GoogleGenerativeAIEmbeddings:
        try:
            return GoogleGenerativeAIEmbeddings(
                model=EMBEDDING_MODEL,
                google_api_key=key
            )
        except Exception as e:
            print(f"Warning: Failed initializing GoogleGenerativeAIEmbeddings ({e}). Using fallback.")
            return FallbackEmbeddings()

    return FallbackEmbeddings()
