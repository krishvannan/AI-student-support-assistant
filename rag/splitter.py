"""
Document Splitter Module for CampusAI.
Splits extracted document text into semantic chunks with context overlap.
"""

from typing import List
from langchain_core.documents import Document

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        RecursiveCharacterTextSplitter = None


class DocumentSplitter:
    """Splits documents into overlapping chunks for vector embedding and retrieval."""

    def __init__(self, chunk_size: int = 750, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        if RecursiveCharacterTextSplitter:
            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", "; ", " ", ""]
            )
        else:
            self._splitter = None

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of Documents into chunks and attach chunk indexing metadata.
        """
        if not documents:
            return []

        if self._splitter:
            chunks = self._splitter.split_documents(documents)
        else:
            # Fallback pure-Python splitter
            chunks = []
            for doc in documents:
                text = doc.page_content
                start = 0
                while start < len(text):
                    end = min(start + self.chunk_size, len(text))
                    chunk_text = text[start:end].strip()
                    if chunk_text:
                        chunks.append(Document(page_content=chunk_text, metadata=dict(doc.metadata)))
                    start += self.chunk_size - self.chunk_overlap

        # Add unique chunk indices
        for idx, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = idx

        return chunks
