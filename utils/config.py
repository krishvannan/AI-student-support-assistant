"""
Configuration module for CampusAI.
Handles environment variables, API key loading, model names, and system paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of Project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Path Configurations
DEFAULT_SQLITE_PATH = BASE_DIR / "database" / "campus_ai.db"
DEFAULT_CHROMA_DIR = BASE_DIR / "chroma_db"
DEFAULT_DOCS_DIR = BASE_DIR / "documents"
ASSETS_DIR = BASE_DIR / "assets"

SQLITE_DB_PATH = Path(os.getenv("SQLITE_DB_PATH", str(DEFAULT_SQLITE_PATH)))
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(DEFAULT_CHROMA_DIR)))
DOCUMENTS_DIR = Path(os.getenv("DOCUMENTS_DIR", str(DEFAULT_DOCS_DIR)))

# AI Models
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

# In-memory API key override (for when user inputs key in Streamlit UI)
_runtime_api_key = None


def get_api_key() -> str:
    """
    Retrieve Google Gemini API Key from runtime override, environment variable, or return empty string.
    """
    global _runtime_api_key
    if _runtime_api_key:
        return _runtime_api_key.strip()
    return os.getenv("GEMINI_API_KEY", "").strip()


def set_api_key(key: str) -> None:
    """
    Set runtime API key override and update os.environ.
    """
    global _runtime_api_key
    if key:
        clean_key = key.strip()
        _runtime_api_key = clean_key
        os.environ["GEMINI_API_KEY"] = clean_key


def is_api_key_set() -> bool:
    """Check whether a non-empty API key is available."""
    key = get_api_key()
    return bool(key and key != "your_gemini_api_key_here")


def ensure_directories() -> None:
    """Ensure critical project directories exist."""
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
