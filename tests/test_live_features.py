"""
End-to-end Live Feature Verification for CampusAI.
Validates RAG, ChromaDB persistence, Gemini embeddings, Study Planner, Notice Summarizer, and Quiz Generator.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure Windows terminal doesn't crash on emoji characters
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from utils.config import DOCUMENTS_DIR, is_api_key_set
from rag.loader import PDFDocumentLoader
from rag.splitter import DocumentSplitter
from rag.vectorstore import get_vector_store
from rag.retriever import CollegeAssistantRAG
from tools.study_planner import StudyPlannerTool
from tools.summarizer import NoticeSummarizerTool
from tools.quiz_generator import QuizGeneratorTool
from memory.student_memory import StudentMemory


def test_live_features():
    print("=" * 65)
    print("   CampusAI Live End-to-End Feature Verification")
    print("=" * 65)

    assert is_api_key_set(), "API Key must be set in .env"
    print(" [1/5] API Key Verified & Active")

    # 1. RAG & ChromaDB Real Ingestion
    print("\n [2/5] Testing RAG Pipeline (PDF -> Chunks -> Embeddings -> ChromaDB)...")
    docs = PDFDocumentLoader.load_directory(str(DOCUMENTS_DIR))
    print(f"       Loaded {len(docs)} pages from sample PDFs")
    splitter = DocumentSplitter(chunk_size=750, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    print(f"       Created {len(chunks)} text chunks")

    vstore = get_vector_store()
    vstore.clear()
    added = vstore.add_documents(chunks[:5])  # Index first 5 chunks for fast verification
    print(f"       Successfully generated Gemini embeddings and stored {added} chunks in ChromaDB!")

    rag = CollegeAssistantRAG()
    rag_result = rag.query(
        user_question="What is the minimum attendance required according to regulations?",
        k=2
    )
    print(f"       RAG Answer Generated ({len(rag_result['answer'])} chars):")
    print(f"       '{rag_result['answer'][:160]}...'")
    print(f"       Sources cited: {len(rag_result['sources'])} documents")
    assert len(rag_result['answer']) > 20, "RAG answer should not be empty"

    # 2. Notice Summarizer
    print("\n [3/5] Testing Notice Summarizer Tool...")
    sample_notice = (
        "OFFICE OF THE CONTROLLER OF EXAMINATIONS\n"
        "Notification No. COE/2024/ES-02\n"
        "All students are notified that End Semester Exam Fee payment portal closes on October 24, 2024 without late fee.\n"
        "Fee with fine of Rs. 500 will be accepted up to October 29, 2024. Practical exams commence November 11, 2024."
    )
    summary_result = NoticeSummarizerTool.summarize_notice(sample_notice, "End Semester Notice")
    assert summary_result["success"], f"Summarizer failed: {summary_result.get('error')}"
    print(f"       Summary Generated ({len(summary_result['summary_markdown'])} chars):")
    print(f"       '{summary_result['summary_markdown'][:160]}...'")

    # 3. AI Study Planner
    print("\n [4/5] Testing AI Study Planner Tool...")
    plan_result = StudyPlannerTool.generate_plan(
        exam_date="2026-10-15",
        subjects=["Artificial Intelligence", "Compiler Design"],
        daily_hours=4.0
    )
    assert plan_result["success"], f"Study planner failed: {plan_result.get('error')}"
    print(f"       Study Plan Generated ({len(plan_result['plan_markdown'])} chars):")
    print(f"       '{plan_result['plan_markdown'][:160]}...'")

    # 4. AI Quiz Generator
    print("\n [5/5] Testing AI Quiz Generator Tool...")
    quiz_result = QuizGeneratorTool.generate_quiz(
        study_material="The A* search algorithm uses a heuristic function h(n) and cost function g(n) to find the shortest path. f(n) = g(n) + h(n).",
        topic="A* Search Algorithm",
        num_questions=3,
        difficulty="Medium"
    )
    assert quiz_result["success"], f"Quiz generator failed: {quiz_result.get('error')}"
    print(f"       Generated {len(quiz_result['questions'])} MCQs successfully!")
    q1 = quiz_result['questions'][0]
    print(f"       Q1: {q1.get('question')}")
    print(f"       Options: {q1.get('options')}")
    print(f"       Correct: {q1.get('correct_answer')}")

    print("\n" + "=" * 65)
    print("   ALL 5 LIVE GEMINI AI FEATURES PASSED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    test_live_features()
