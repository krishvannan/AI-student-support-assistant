"""
RAG Retriever and Question Answering Engine for CampusAI.
Coordinates ChromaDB vector retrieval, student profile memory, conversation context, and LangChain Google Gemini LLM.
"""

from typing import List, Dict, Any, Optional
from utils.config import get_api_key, GEMINI_MODEL, is_api_key_set
from rag.vectorstore import get_vector_store
from memory.student_memory import StudentMemory
from memory.chat_memory import ChatMemoryManager
from utils.helpers import extract_text_from_response

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage


class CollegeAssistantRAG:
    """Production RAG pipeline integrating LangChain, ChromaDB, and Google Gemini."""

    def __init__(self, session_id: str = "student_session"):
        self.session_id = session_id
        self.vector_store = get_vector_store()
        self.memory_manager = ChatMemoryManager(session_id=session_id)

    def _get_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize Google Gemini chat model via LangChain."""
        api_key = get_api_key()
        if not api_key:
            raise ValueError("Google Gemini API Key is missing. Configure it in .env or the sidebar.")

        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=api_key,
            temperature=0.3,
            max_output_tokens=1500
        )

    def query(
        self,
        user_question: str,
        k: int = 4,
        use_memory: bool = True,
        use_student_profile: bool = True
    ) -> Dict[str, Any]:
        """
        Execute full Retrieval-Augmented Generation:
        1. Retrieve relevant chunks from ChromaDB
        2. Attach source citations
        3. Augment with Student Memory and Chat History
        4. Generate grounded response using Google Gemini
        5. Persist to SQLite chat history
        """
        if not is_api_key_set():
            return {
                "answer": (
                    "⚠️ **Google Gemini API Key is not configured.**\n\n"
                    "To enable AI answers, please enter your Gemini API key in the **🔑 AI Configuration** "
                    "section in the sidebar or add `GEMINI_API_KEY=your_key` to your `.env` file."
                ),
                "sources": [],
                "num_sources": 0
            }

        if not user_question or not user_question.strip():
            return {
                "answer": "Please enter a valid question.",
                "sources": [],
                "num_sources": 0
            }

        # 1. Retrieve relevant document chunks from ChromaDB
        relevant_docs = []
        try:
            if self.vector_store.get_document_count() > 0:
                relevant_docs = self.vector_store.similarity_search(user_question, k=k)
        except Exception as e:
            print(f"Warning: Vector search exception: {e}")

        # 2. Extract source citations
        sources_list = []
        context_chunks = []
        for doc in relevant_docs:
            source_name = doc.metadata.get("source", "College Document")
            page_num = doc.metadata.get("page", 1)
            content_snippet = doc.page_content[:250].strip() + ("..." if len(doc.page_content) > 250 else "")

            sources_list.append({
                "source": source_name,
                "page": page_num,
                "snippet": content_snippet
            })
            context_chunks.append(f"--- Document: {source_name} (Page {page_num}) ---\n{doc.page_content}")

        if context_chunks:
            context_text = "\n\n".join(context_chunks)
        else:
            context_text = (
                "Notice: No specific college documents are indexed in ChromaDB yet, or no direct matches were found. "
                "Answer using standard university academic best practices."
            )

        # 3. Assemble Student Profile Memory Context
        student_context = StudentMemory.get_context_prompt() if use_student_profile else "No profile provided."

        # 4. Assemble Multi-turn Chat History Buffer
        history_text = self.memory_manager.format_history_for_prompt(max_turns=4) if use_memory else ""

        # 5. Formulate System Prompt
        system_instruction = (
            "You are 'CampusAI', an intelligent, authoritative, and helpful university student support assistant.\n"
            "You assist students with academic regulations, examination schedules, syllabus details, and circulars.\n\n"
            f"{student_context}\n\n"
            "INSTRUCTIONS:\n"
            "1. Ground your answer in the provided College Documents Context whenever possible.\n"
            "2. If document context directly answers the question, cite the policy and provide exact details.\n"
            "3. If personalizing for the student, use their enrolled department, semester, and subjects.\n"
            "4. Structure your response with bold headings, bullet points, and clean formatting.\n"
            "5. If information is not in the documents, state that clearly and offer general guidance.\n"
        )

        user_content = (
            f"=== RETRIEVED COLLEGE DOCUMENTS (CHROMADB) ===\n"
            f"{context_text}\n\n"
            f"=== PREVIOUS CHAT TURNS ===\n"
            f"{history_text if history_text else 'New conversation session.'}\n\n"
            f"=== STUDENT QUESTION ===\n"
            f"{user_question}\n"
        )

        # 6. Invoke Gemini LLM via LangChain
        try:
            llm = self._get_llm()
            response = llm.invoke([
                SystemMessage(content=system_instruction),
                HumanMessage(content=user_content)
            ])
            answer = extract_text_from_response(response.content)
        except Exception as e:
            answer = (
                f"⚠️ **Error communicating with Google Gemini API**: {str(e)}\n\n"
                "Please verify that your Gemini API key is valid and has access to `gemini-1.5-flash`."
            )

        # 7. Persist to SQLite Memory
        if use_memory:
            self.memory_manager.add_user_message(user_question)
            self.memory_manager.add_ai_message(answer, sources=sources_list)

        return {
            "answer": answer,
            "sources": sources_list,
            "num_sources": len(sources_list)
        }
