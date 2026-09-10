"""
Notice Summarizer Tool for CampusAI.
Extracts executive summaries, critical deadlines, dates, and actionable checklists from campus notices and circulars.
"""

from typing import Dict, Any
from utils.config import get_api_key, GEMINI_MODEL, is_api_key_set
from memory.student_memory import StudentMemory

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage


class NoticeSummarizerTool:
    """Processes university circulars and extracts structured executive summaries."""

    @staticmethod
    def summarize_notice(notice_text: str, notice_title: str = "University Circular") -> Dict[str, Any]:
        """
        Summarize a college circular or administrative notice using LangChain and Google Gemini.
        Returns parsed summary sections.
        """
        if not is_api_key_set():
            return {
                "success": False,
                "error": "Google Gemini API Key is not set. Please configure it in .env or the sidebar.",
                "summary_markdown": ""
            }

        if not notice_text or len(notice_text.strip()) < 20:
            return {
                "success": False,
                "error": "Notice content is too short to analyze. Please provide a valid document or text.",
                "summary_markdown": ""
            }

        api_key = get_api_key()
        student_profile = StudentMemory.get_profile()

        system_prompt = (
            "You are an AI Campus Administrator and Notice Analyst for university students.\n"
            "Your job is to read complex, bureaucratic university circulars and convert them into crystal-clear, "
            "actionable insights that students cannot afford to miss.\n"
            f"Active Student Profile:\n- Dept: {student_profile.department}\n- Semester: {student_profile.semester}\n"
        )

        user_prompt = (
            f"Document Title: {notice_title}\n\n"
            f"=== NOTICE TEXT ===\n"
            f"{notice_text}\n"
            f"===================\n\n"
            "Please analyze this circular and produce a comprehensive markdown report with exactly these sections:\n\n"
            "1. 📌 **Executive Summary**\n"
            "A concise 2 to 3-sentence summary of the main announcement.\n\n"
            "2. 🗓️ **Important Dates & Timings (Table)**\n"
            "A markdown table listing each event, its date, and its time/venue.\n"
            "| Event / Milestone | Date | Time & Venue |\n\n"
            "3. ⚠️ **Critical Deadlines & Consequences**\n"
            "List all cut-off dates, late penalty fees, and consequences of missing them.\n\n"
            "4. ✅ **Action Items Checklist for Students**\n"
            "Step-by-step checklist of what the student must do immediately (e.g. portal registration, document submission, fee payment).\n\n"
            "5. 👥 **Target Audience & Affected Batches**\n"
            "Specify the exact departments, semesters, or batches affected.\n\n"
            "6. 📞 **Contact Information & Helpdesk**\n"
            "Office room numbers, helplines, or email addresses mentioned in the circular.\n"
        )

        try:
            llm = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=api_key,
                temperature=0.2
            )
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            return {
                "success": True,
                "summary_markdown": response.content
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed summarizing notice: {str(e)}",
                "summary_markdown": ""
            }
