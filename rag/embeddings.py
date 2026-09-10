"""
Google Gemini Embeddings Module for CampusAI.
Integrates LangChain GoogleGenerativeAIEmbeddings using official models.
"""

from typing import Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.config import get_api_key, EMBEDDING_MODEL, is_api_key_set


def get_embedding_function(api_key: Optional[str] = None) -> GoogleGenerativeAIEmbeddings:
    """
    Get configured Google Gemini embedding model.
    Raises ValueError if API key is not configured.
    """
    key = api_key or get_api_key()
    if not key or key == "your_gemini_api_key_here":
        raise ValueError(
            "Google Gemini API Key is not configured. "
            "Please provide your API key in the .env file or via the sidebar 'AI Configuration'."
        )

    # Use GoogleGenerativeAIEmbeddings from langchain-google-genai
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=key
    )
