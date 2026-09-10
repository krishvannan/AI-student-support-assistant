"""
System Verification and Smoke Test for CampusAI.
Tests database operations, document loading, text chunking, and vector search.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.sqlite_db import (
    init_db,
    get_student_profile,
    save_or_update_profile,
    save_study_plan,
    get_recent_study_plans,
    add_chat_message,
    get_chat_history,
    save_quiz_record,
    get_recent_quizzes,
)
from database.models import StudentProfile, StudyPlan, ChatMessage, QuizRecord
from memory.student_memory import StudentMemory
from rag.loader import PDFDocumentLoader
from rag.splitter import DocumentSplitter
from rag.vectorstore import get_vector_store
from utils.config import DOCUMENTS_DIR


def run_all_tests():
    print("=" * 60)
    print("   CampusAI System Verification Test Suite")
    print("=" * 60)

    # 1. Test SQLite Database
    print("\n[1/5] Testing SQLite Database Initialization & CRUD...")
    init_db()
    profile = get_student_profile()
    assert profile is not None, "Profile should not be None"
    print(f"  [OK] Retrieved active student profile: {profile.name} ({profile.department}, Sem {profile.semester})")

    # Update profile test
    profile.name = "Alex Johnson"
    profile.roll_number = "2024CS089"
    save_or_update_profile(profile)
    updated = get_student_profile()
    assert updated.name == "Alex Johnson", f"Expected Alex Johnson, got {updated.name}"
    print(f"  [OK] Profile update test passed: {updated.name} - {updated.roll_number}")

    # Chat history test
    msg = ChatMessage(session_id="test_session", sender="user", message="Hello CampusAI!")
    add_chat_message(msg)
    history = get_chat_history("test_session")
    assert len(history) > 0, "Chat history should contain at least 1 message"
    print(f"  [OK] Chat history persistence passed ({len(history)} messages)")

    # 2. Test Student Memory Context
    print("\n[2/5] Testing Student Memory Prompt Generation...")
    context_prompt = StudentMemory.get_context_prompt()
    assert "Alex Johnson" in context_prompt
    assert "Computer Science" in context_prompt
    print("  [OK] Context prompt contains student identity & subjects:")
    print("    " + context_prompt.replace("\n", "\n    ")[:200] + "...")

    # 3. Test PDF Document Loading
    print("\n[3/5] Testing PDF Document Loader on Sample Documents...")
    docs = PDFDocumentLoader.load_directory(str(DOCUMENTS_DIR))
    print(f"  [OK] Loaded {len(docs)} document pages from {DOCUMENTS_DIR}")
    assert len(docs) > 0, "Should have loaded at least 1 document page"
    sample_doc = docs[0]
    print(f"  [OK] Sample page extracted from: {sample_doc.metadata.get('source')} (Page {sample_doc.metadata.get('page')})")
    print(f"  [OK] Sample text snippet: {sample_doc.page_content[:120].strip()}...")

    # 4. Test Semantic Text Splitter
    print("\n[4/5] Testing Document Chunk Splitter...")
    splitter = DocumentSplitter(chunk_size=750, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    print(f"  [OK] Split {len(docs)} pages into {len(chunks)} semantic chunks")
    assert len(chunks) >= len(docs), "Chunks should be >= number of pages"

    # 5. Test Vector Store & Similarity Search
    print("\n[5/5] Testing Vector Store Storage & Retrieval...")
    vstore = get_vector_store()
    added_count = vstore.add_documents(chunks)
    print(f"  [OK] Indexed {added_count} chunks into ChromaDB / Vector Store")

    total_in_store = vstore.get_document_count()
    print(f"  [OK] Total vector count in store: {total_in_store}")

    # Query test
    query = "What is the minimum attendance required according to regulations?"
    search_results = vstore.similarity_search(query, k=3)
    print(f"  [OK] Executed query: '{query}' -> Retrieved {len(search_results)} relevant chunks")
    if search_results:
        top_match = search_results[0]
        print(f"    Top Match Document: {top_match.metadata.get('source')}")
        print(f"    Content Excerpt: {top_match.page_content[:150].strip()}...")

    print("\n" + "=" * 60)
    print("   ALL TESTS PASSED SUCCESSFULLY! (5/5)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
