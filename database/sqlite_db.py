"""
SQLite database management for CampusAI.
Handles table initialization, thread-safe connections, and CRUD operations.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from database.models import StudentProfile, StudyPlan, ChatMessage, QuizRecord
from utils.config import SQLITE_DB_PATH


def get_connection() -> sqlite3.Connection:
    """Create and return a database connection with row factory enabled."""
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize all required SQLite tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Student Profile Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT,
            department TEXT NOT NULL,
            semester INTEGER NOT NULL,
            subjects TEXT NOT NULL,
            target_gpa REAL,
            preferred_language TEXT DEFAULT 'English',
            interests TEXT,
            updated_at TEXT NOT NULL
        )
    """)

    # 2. Study Plans Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            exam_date TEXT NOT NULL,
            daily_hours REAL NOT NULL,
            subjects TEXT NOT NULL,
            plan_content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES student_profile(id)
        )
    """)

    # 3. Chat History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            sources TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    # 4. Quiz Records Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            questions_data TEXT,
            completed_at TEXT NOT NULL
        )
    """)

    conn.commit()

    # Seed default profile if none exists
    cursor.execute("SELECT COUNT(*) FROM student_profile")
    if cursor.fetchone()[0] == 0:
        default_profile = StudentProfile()
        save_or_update_profile(default_profile)

    conn.close()


def get_student_profile() -> StudentProfile:
    """Retrieve the primary active student profile."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_profile ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if not row:
        return StudentProfile()

    # Parse subjects list
    subjects_raw = row["subjects"]
    try:
        subjects = json.loads(subjects_raw) if subjects_raw.startswith("[") else [s.strip() for s in subjects_raw.split(",") if s.strip()]
    except Exception:
        subjects = [s.strip() for s in subjects_raw.split(",") if s.strip()]

    return StudentProfile(
        id=row["id"],
        name=row["name"],
        roll_number=row["roll_number"] or "",
        department=row["department"],
        semester=row["semester"],
        subjects=subjects,
        target_gpa=row["target_gpa"] or 8.5,
        preferred_language=row["preferred_language"] or "English",
        interests=row["interests"] or "",
        updated_at=row["updated_at"]
    )


def save_or_update_profile(profile: StudentProfile) -> int:
    """Save or update the student profile."""
    conn = get_connection()
    cursor = conn.cursor()

    subjects_json = json.dumps(profile.subjects if isinstance(profile.subjects, list) else [s.strip() for s in profile.subjects.split(",")])
    now = datetime.now().isoformat()

    cursor.execute("SELECT id FROM student_profile ORDER BY id DESC LIMIT 1")
    existing = cursor.fetchone()

    if existing:
        profile_id = existing["id"]
        cursor.execute("""
            UPDATE student_profile
            SET name=?, roll_number=?, department=?, semester=?, subjects=?, target_gpa=?, preferred_language=?, interests=?, updated_at=?
            WHERE id=?
        """, (
            profile.name,
            profile.roll_number,
            profile.department,
            profile.semester,
            subjects_json,
            profile.target_gpa,
            profile.preferred_language,
            profile.interests,
            now,
            profile_id
        ))
    else:
        cursor.execute("""
            INSERT INTO student_profile (name, roll_number, department, semester, subjects, target_gpa, preferred_language, interests, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.name,
            profile.roll_number,
            profile.department,
            profile.semester,
            subjects_json,
            profile.target_gpa,
            profile.preferred_language,
            profile.interests,
            now
        ))
        profile_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return profile_id


def save_study_plan(plan: StudyPlan) -> int:
    """Save a study plan."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO study_plans (student_id, exam_date, daily_hours, subjects, plan_content, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        plan.student_id,
        plan.exam_date,
        plan.daily_hours,
        plan.subjects,
        plan.plan_content,
        plan.created_at or datetime.now().isoformat()
    ))
    conn.commit()
    plan_id = cursor.lastrowid
    conn.close()
    return plan_id


def get_recent_study_plans(limit: int = 5) -> List[StudyPlan]:
    """Retrieve recent study plans."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM study_plans ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    plans = []
    for r in rows:
        plans.append(StudyPlan(
            id=r["id"],
            student_id=r["student_id"],
            exam_date=r["exam_date"],
            daily_hours=r["daily_hours"],
            subjects=r["subjects"],
            plan_content=r["plan_content"],
            created_at=r["created_at"]
        ))
    return plans


def add_chat_message(msg: ChatMessage) -> int:
    """Insert a chat message record."""
    conn = get_connection()
    cursor = conn.cursor()
    sources_text = json.dumps(msg.sources) if msg.sources else ""
    cursor.execute("""
        INSERT INTO chat_history (session_id, sender, message, sources, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        msg.session_id,
        msg.sender,
        msg.message,
        sources_text,
        msg.timestamp or datetime.now().isoformat()
    ))
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id


def get_chat_history(session_id: str = "default_session", limit: int = 50) -> List[ChatMessage]:
    """Retrieve chat history for a session in chronological order."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM chat_history
        WHERE session_id = ?
        ORDER BY id ASC
        LIMIT ?
    """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()

    messages = []
    for r in rows:
        sources = None
        if r["sources"]:
            try:
                sources = json.loads(r["sources"])
            except Exception:
                sources = []
        messages.append(ChatMessage(
            id=r["id"],
            session_id=r["session_id"],
            sender=r["sender"],
            message=r["message"],
            sources=sources,
            timestamp=r["timestamp"]
        ))
    return messages


def clear_chat_history(session_id: str = "default_session") -> None:
    """Clear chat messages for a session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


def save_quiz_record(quiz: QuizRecord) -> int:
    """Record a completed quiz attempt."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quiz_records (topic, score, total_questions, questions_data, completed_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        quiz.topic,
        quiz.score,
        quiz.total_questions,
        quiz.questions_data,
        quiz.completed_at or datetime.now().isoformat()
    ))
    conn.commit()
    qid = cursor.lastrowid
    conn.close()
    return qid


def get_recent_quizzes(limit: int = 5) -> List[QuizRecord]:
    """Retrieve recent quiz attempts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_records ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    quizzes = []
    for r in rows:
        quizzes.append(QuizRecord(
            id=r["id"],
            topic=r["topic"],
            score=r["score"],
            total_questions=r["total_questions"],
            questions_data=r["questions_data"] or "",
            completed_at=r["completed_at"]
        ))
    return quizzes
