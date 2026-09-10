"""
Notice Summarizer Tool for CampusAI.
Extracts summaries, critical deadlines, dates, and actionable checklists from campus notices and circulars.
"""

from typing import Dict, Any
from utils.config import get_api_key, GEMINI_MODEL, is_api_key_set
from memory.student_memory import StudentMemory

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class NoticeSummarizerTool:
    """Processes university circulars and extracts structured executive summaries."""

    @staticmethod
    def summarize_notice(notice_text: str, notice_title: str = "University Circular") -> Dict[str, Any]:
        """
        Summarize a college circular or administrative notice.
        Returns parsed summary sections.
        """
        if not is_api_key_set():
            return {
                "success": False,
                "error": "Google Gemini API Key is not set. Please add it in Settings.",
                "summary_markdown": ""
            }

        if not notice_text or len(notice_text.strip()) < 20:
            return {
                "success": False,
                "error": "Notice content is too short to summarize.",
                "summary_markdown": ""
            }

        api_key = get_api_key()
        student_profile = StudentMemory.get_profile()

        system_prompt = (
            "You are an AI Campus Administrator and Notice Analyst for university students.\n"
            "Your job is to read complex, bureaucratic university circulars and convert them into crystal-clear, "
            "actionable insights that students won't miss.\n"
            f"Active Student Profile:\n- Dept: {student_profile.department}\n- Semester: {student_profile.semester}\n"
        )

        user_prompt = (
            f"Document Title: {notice_title}\n\n"
            f"=== NOTICE TEXT ===\n"
            f"{notice_text}\n"
            f"===================\n\n"
            "Please analyze this circular and produce a comprehensive markdown report with exactly these sections:\n"
            "1. 📌 **Executive Summary**: 2 to 3 sentences summarizing the main announcement.\n"
            "2. 🗓️ **Important Dates & Timings**: A markdown table or bulleted list of all mentioned dates, times, and events.\n"
            "3. ⚠️ **Critical Deadlines**: Any final cut-off dates or consequences of missing them.\n"
            "4. ✅ **Action Items Checklist for Students**: Step-by-step checklist of what students must do right now.\n"
            "5. 👥 **Applicability & Target Audience**: Specify which departments, years, or batches are affected.\n"
            "6. 📞 **Contact & Escalation Desk**: Office, emails, or helpline numbers mentioned.\n"
        )

        try:
            if ChatGoogleGenerativeAI:
                llm = ChatGoogleGenerativeAI(
                    model=GEMINI_MODEL,
                    google_api_key=api_key,
                    temperature=0.2
                )
                response = llm.invoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ])
                summary_content = response.content
            elif genai:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=GEMINI_MODEL,
                    system_instruction=system_prompt
                )
                res = model.generate_content(user_prompt)
                summary_content = res.text
            else:
                summary_content = "Error: Generative AI SDK not initialized."

            return {
                "success": True,
                "summary_markdown": summary_content
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed summarizing notice: {str(e)}",
                "summary_markdown": ""
            }
