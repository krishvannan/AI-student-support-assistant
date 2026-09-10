"""CampusAI UI Pages package."""
from pages.home import render_home_page
from pages.chatbot import render_chatbot_page
from pages.study_planner import render_study_planner_page
from pages.quiz_generator import render_quiz_page
from pages.summarizer import render_summarizer_page
from pages.profile import render_profile_page
from pages.about import render_about_page

__all__ = [
    "render_home_page",
    "render_chatbot_page",
    "render_study_planner_page",
    "render_quiz_page",
    "render_summarizer_page",
    "render_profile_page",
    "render_about_page",
]
