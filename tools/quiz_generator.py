"""
AI Quiz Generator Tool for CampusAI.
Generates rigorous Multiple Choice Questions (MCQs) with options, answer keys, and academic explanations using Google Gemini.
"""

import json
import re
from typing import List, Dict, Any, Optional
from utils.config import get_api_key, GEMINI_MODEL, is_api_key_set
from memory.student_memory import StudentMemory
from database.sqlite_db import save_quiz_record
from database.models import QuizRecord
from utils.helpers import extract_text_from_response

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage


class QuizGeneratorTool:
    """Generates MCQs and practice exams based on syllabus, lecture notes, or study topics."""

    @staticmethod
    def _clean_json_output(raw_text: str) -> str:
        """Strip markdown code backticks and extract pure JSON string."""
        cleaned = raw_text.strip()
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if match:
            cleaned = match.group(1).strip()
        return cleaned

    @classmethod
    def generate_quiz(
        cls,
        study_material: str,
        topic: str = "Academic Assessment",
        num_questions: int = 5,
        difficulty: str = "Medium"
    ) -> Dict[str, Any]:
        """
        Generate multiple choice questions based on study material or topic.
        Returns:
            {
                "success": bool,
                "questions": List[Dict],
                "error": str
            }
        """
        if not is_api_key_set():
            return {
                "success": False,
                "questions": [],
                "error": "Google Gemini API Key is not configured. Please configure it in .env or the sidebar."
            }

        api_key = get_api_key()
        student = StudentMemory.get_profile()

        system_prompt = (
            "You are an expert University Professor and Examination Board Member.\n"
            "Your job is to generate rigorous, high-quality Multiple Choice Questions (MCQs) for engineering exams.\n"
            "Requirements:\n"
            "1. Each question must test conceptual understanding or problem solving, NOT superficial recall.\n"
            "2. Provide exactly 4 plausible choices for each question.\n"
            "3. Clearly specify the exact correct answer string and the 0-based index (0, 1, 2, or 3).\n"
            "4. Provide a thorough, pedagogically sound explanation for why that answer is correct.\n"
            "5. OUTPUT FORMAT MUST BE STRICTLY VALID JSON ONLY. Do not write introductory or concluding text.\n"
            f"Target student department: {student.department}, Semester: {student.semester}.\n"
        )

        user_prompt = (
            f"Generate a {num_questions}-question quiz on the topic: '{topic}'.\n"
            f"Difficulty Level: {difficulty}\n\n"
            f"=== STUDY MATERIAL / REFERENCE CONTENT ===\n"
            f"{study_material[:4000]}\n"
            f"===========================================\n\n"
            "Return a JSON array of objects with the exact schema below:\n"
            "[\n"
            "  {\n"
            "    \"id\": 1,\n"
            "    \"question\": \"Question text here?\",\n"
            "    \"options\": [\"Option 1\", \"Option 2\", \"Option 3\", \"Option 4\"],\n"
            "    \"correct_answer\": \"Option 2\",\n"
            "    \"correct_option_index\": 1,\n"
            "    \"explanation\": \"Detailed explanation of why this option is correct and why others are incorrect.\"\n"
            "  }\n"
            "]\n"
        )

        try:
            llm = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=api_key,
                temperature=0.3
            )
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            raw_output = extract_text_from_response(response.content)

            # Parse JSON
            cleaned_json = cls._clean_json_output(raw_output)
            questions = json.loads(cleaned_json)

            if not isinstance(questions, list) or len(questions) == 0:
                return {"success": False, "questions": [], "error": "AI returned empty question list."}

            return {
                "success": True,
                "topic": topic,
                "difficulty": difficulty,
                "questions": questions,
                "error": ""
            }

        except json.JSONDecodeError as jde:
            return {
                "success": False,
                "questions": [],
                "error": f"JSON parsing failed: {jde}. Raw output: {raw_output[:200]}"
            }
        except Exception as e:
            return {
                "success": False,
                "questions": [],
                "error": f"Error generating quiz: {str(e)}"
            }

    @staticmethod
    def record_quiz_score(topic: str, score: int, total: int, questions_data: List[Dict]) -> None:
        """Save student quiz attempt to SQLite."""
        try:
            record = QuizRecord(
                topic=topic,
                score=score,
                total_questions=total,
                questions_data=json.dumps(questions_data)
            )
            save_quiz_record(record)
        except Exception as e:
            print(f"Failed to record quiz score: {e}")
