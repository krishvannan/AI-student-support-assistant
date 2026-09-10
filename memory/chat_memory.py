"""
Chat Memory Module for CampusAI.
Handles conversation buffers, session-based storage, and SQLite history persistence.
"""

from typing import List, Dict, Any, Optional
from database.sqlite_db import add_chat_message, get_chat_history, clear_chat_history
from database.models import ChatMessage


class ChatMemoryManager:
    """Manages conversational history across UI sessions and SQLite persistence."""

    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id

    def add_user_message(self, message: str) -> None:
        """Store a user message in database."""
        chat_msg = ChatMessage(
            session_id=self.session_id,
            sender="user",
            message=message
        )
        add_chat_message(chat_msg)

    def add_ai_message(self, message: str, sources: Optional[List[dict]] = None) -> None:
        """Store an assistant message with optional source citations in database."""
        chat_msg = ChatMessage(
            session_id=self.session_id,
            sender="assistant",
            message=message,
            sources=sources
        )
        add_chat_message(chat_msg)

    def get_messages(self, limit: int = 30) -> List[ChatMessage]:
        """Fetch chronological messages for this session."""
        return get_chat_history(session_id=self.session_id, limit=limit)

    def clear(self) -> None:
        """Clear all messages for this session."""
        clear_chat_history(session_id=self.session_id)

    def format_history_for_prompt(self, max_turns: int = 6) -> str:
        """
        Format recent conversation history as dialogue text for LLM context.
        """
        recent = self.get_messages(limit=max_turns * 2)
        if not recent:
            return ""

        formatted_turns = []
        for msg in recent:
            prefix = "Student" if msg.sender == "user" else "Assistant"
            formatted_turns.append(f"{prefix}: {msg.message}")

        return "\n".join(formatted_turns)
