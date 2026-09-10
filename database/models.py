"""
Data models and schemas for CampusAI SQLite database.
Defines entity dataclasses for StudentProfile, StudyPlan, ChatMessage, and QuizRecord.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import json


@dataclass
class StudentProfile:
    """Represents a student's personal and academic profile."""
    id: Optional[int] = None
    name: str = "Student"
    roll_number: str = ""
    department: str = "Computer Science and Engineering"
    semester: int = 6
    subjects: List[str] = field(default_factory=lambda: [
        "Artificial Intelligence",
        "Cloud Computing",
        "Compiler Design",
        "Web Technologies",
        "Database Management Systems"
    ])
    target_gpa: float = 8.5
    preferred_language: str = "English"
    interests: str = "AI/ML, Software Engineering, Placements"
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def subjects_as_string(self) -> str:
        """Return subjects formatted as comma-separated string."""
        return ", ".join(self.subjects) if isinstance(self.subjects, list) else str(self.subjects)

    def to_dict(self) -> dict:
        """Convert profile to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "roll_number": self.roll_number,
            "department": self.department,
            "semester": self.semester,
            "subjects": self.subjects,
            "target_gpa": self.target_gpa,
            "preferred_language": self.preferred_language,
            "interests": self.interests,
            "updated_at": self.updated_at
        }


@dataclass
class StudyPlan:
    """Represents a generated study plan saved for a student."""
    id: Optional[int] = None
    student_id: Optional[int] = None
    exam_date: str = ""
    daily_hours: float = 4.0
    subjects: str = ""
    plan_content: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ChatMessage:
    """Represents a single message in the conversational history."""
    id: Optional[int] = None
    session_id: str = "default_session"
    sender: str = "user"  # "user" or "assistant"
    message: str = ""
    sources: Optional[List[dict]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def sources_json(self) -> str:
        return json.dumps(self.sources) if self.sources else ""


@dataclass
class QuizRecord:
    """Represents a quiz history and performance attempt."""
    id: Optional[int] = None
    topic: str = ""
    score: int = 0
    total_questions: int = 5
    questions_data: str = ""  # JSON-encoded question details
    completed_at: str = field(default_factory=lambda: datetime.now().isoformat())
