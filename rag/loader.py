"""
Document Loader Module for CampusAI.
Extracts text and page metadata from PDF documents using PyPDF2 and pypdf.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pypdf
except ImportError:
    pypdf = None


class PDFDocumentLoader:
    """Extracts text and structured metadata from PDF files."""

    @staticmethod
    def load_pdf(file_path: str) -> List[Document]:
        """
        Load a single PDF and return a list of LangChain Document objects,
        one Document per non-empty page.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file not found: {file_path}")

        documents: List[Document] = []
        filename = path.name

        # Attempt extraction using pypdf or PyPDF2
        if pypdf:
            try:
                reader = pypdf.PdfReader(str(path))
                for page_idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    clean_text = text.strip()
                    if clean_text:
                        metadata = {
                            "source": filename,
                            "file_path": str(path),
                            "page": page_idx + 1,
                            "total_pages": len(reader.pages),
                            "doc_name": path.stem.replace("_", " ").title()
                        }
                        documents.append(Document(page_content=clean_text, metadata=metadata))
                if documents:
                    return documents
            except Exception as e:
                pass  # Fallback to PyPDF2

        if PyPDF2:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page_idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    clean_text = text.strip()
                    if clean_text:
                        metadata = {
                            "source": filename,
                            "file_path": str(path),
                            "page": page_idx + 1,
                            "total_pages": len(reader.pages),
                            "doc_name": path.stem.replace("_", " ").title()
                        }
                        documents.append(Document(page_content=clean_text, metadata=metadata))

        return documents

    @classmethod
    def load_directory(cls, directory_path: str) -> List[Document]:
        """
        Load all PDF files in a directory recursively.
        """
        dir_path = Path(directory_path)
        if not dir_path.exists():
            return []

        all_docs: List[Document] = []
        for pdf_file in dir_path.glob("**/*.pdf"):
            try:
                docs = cls.load_pdf(str(pdf_file))
                all_docs.extend(docs)
            except Exception as e:
                print(f"Error loading {pdf_file}: {e}")

        return all_docs

    @classmethod
    def load_from_bytes(cls, file_bytes: bytes, filename: str) -> List[Document]:
        """
        Load PDF from in-memory bytes (e.g., Streamlit file uploader).
        """
        import io
        documents: List[Document] = []
        stream = io.BytesIO(file_bytes)

        if pypdf:
            try:
                reader = pypdf.PdfReader(stream)
                for page_idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    clean_text = text.strip()
                    if clean_text:
                        metadata = {
                            "source": filename,
                            "page": page_idx + 1,
                            "total_pages": len(reader.pages),
                            "doc_name": Path(filename).stem.replace("_", " ").title()
                        }
                        documents.append(Document(page_content=clean_text, metadata=metadata))
                return documents
            except Exception:
                stream.seek(0)

        if PyPDF2:
            reader = PyPDF2.PdfReader(stream)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                clean_text = text.strip()
                if clean_text:
                    metadata = {
                        "source": filename,
                        "page": page_idx + 1,
                        "total_pages": len(reader.pages),
                        "doc_name": Path(filename).stem.replace("_", " ").title()
                    }
                    documents.append(Document(page_content=clean_text, metadata=metadata))

        return documents
