"""
RAG Retriever and Question Answering Engine for CampusAI.
Coordinates vector retrieval, student profile memory, conversation context, and Gemini LLM.
"""

from typing import List, Dict, Any, Tuple, Optional
from utils.config import get_api_key, GEMINI_MODEL, is_api_key_set
from rag.vectorstore import get_vector_store
from memory.student_memory import StudentMemory
from memory.chat_memory import ChatMemoryManager

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class CollegeAssistantRAG:
    """RAG pipeline integrating retrieval with Gemini LLM generation."""

    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self.vector_store = get_vector_store()
        self.memory_manager = ChatMemoryManager(session_id=session_id)

    def _get_llm(self):
        """Initialize Google Gemini chat model."""
        api_key = get_api_key()
        if not api_key:
            return None

        if ChatGoogleGenerativeAI:
            return ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=api_key,
                temperature=0.3,
                max_output_tokens=1500
            )
        return None

    def query(
        self,
        user_question: str,
        k: int = 4,
        use_memory: bool = True,
        use_student_profile: bool = True
    ) -> Dict[str, Any]:
        """
        Execute full RAG retrieval and answer generation.
        Returns:
            {
                "answer": str,
                "sources": List[Dict[str, Any]],
                "num_sources": int
            }
        """
        api_key = get_api_key()
        if not is_api_key_set():
            return {
                "answer": "⚠️ **Google Gemini API Key is not configured.**\n\n"
                          "Please add your Gemini API key in the **Settings** sidebar or in the `.env` file to enable AI answers.",
                "sources": [],
                "num_sources": 0
            }

        # 1. Retrieve relevant document chunks from ChromaDB
        relevant_docs = self.vector_store.similarity_search(user_question, k=k)

        # 2. Extract sources metadata
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

        context_text = "\n\n".join(context_chunks) if context_chunks else "No specific college documents found for this query in the database."

        # 3. Assemble Student Profile Memory
        student_context = StudentMemory.get_context_prompt() if use_student_profile else "No student profile context provided."

        # 4. Assemble Chat History Buffer
        history_text = self.memory_manager.format_history_for_prompt(max_turns=4) if use_memory else ""

        # 5. Build system prompt
        system_instruction = (
            "You are 'CampusAI', an intelligent, empathetic, and knowledgeable university student support assistant.\n"
            "Your role is to guide college students with academic regulations, syllabus, exam timetables, notices, and study advice.\n\n"
            f"{student_context}\n\n"
            "GUIDELINES:\n"
            "- Always prioritize facts provided in the College Documents Context.\n"
            "- If the student profile information (e.g. semester, department, subjects) is relevant, personalize the answer accordingly.\n"
            "- If documents provide an exact answer, quote or reference the policy or regulation clearly.\n"
            "- If the documents do not contain the answer, politely say so and provide helpful general guidance based on university standards.\n"
            "- Format answers with clear bullet points, bold key terms, and professional formatting.\n"
        )

        prompt_content = (
            f"=== COLLEGE DOCUMENTS CONTEXT ===\n"
            f"{context_text}\n\n"
            f"=== RECENT CONVERSATION ===\n"
            f"{history_text if history_text else 'First message in conversation.'}\n\n"
            f"=== STUDENT QUESTION ===\n"
            f"{user_question}\n\n"
            f"Please provide an accurate, helpful, and well-structured response for the student."
        )

        # 6. Call LLM
        answer = ""
        try:
            llm = self._get_llm()
            if llm:
                response = llm.invoke([
                    SystemMessage(content=system_instruction),
                    HumanMessage(content=prompt_content)
                ])
                answer = response.content
            elif genai:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=GEMINI_MODEL,
                    system_instruction=system_instruction
                )
                res = model.generate_content(prompt_content)
                answer = res.text
            else:
                answer = "Error: LangChain or Google Generative AI client not installed properly."
        except Exception as e:
            answer = f"⚠️ An error occurred while communicating with Gemini API: {str(e)}"

        # 7. Record to memory and database
        if use_memory:
            self.memory_manager.add_user_message(user_question)
            self.memory_manager.add_ai_message(answer, sources=sources_list)

        return {
            "answer": answer,
            "sources": sources_list,
            "num_sources": len(sources_list)
        }
