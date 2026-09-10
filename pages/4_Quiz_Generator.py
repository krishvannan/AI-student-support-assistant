"""
AI Quiz Generator Page for CampusAI.
Generates test-standard MCQs with an interactive test-taking mode, automated grading, and explanations.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from memory.student_memory import StudentMemory
from tools.quiz_generator import QuizGeneratorTool
from rag.loader import PDFDocumentLoader
from database.sqlite_db import get_recent_quizzes
from utils.helpers import setup_page


def main():
    setup_page(
        title="AI Quiz & Assessment Generator",
        subtitle="Generate rigorous multiple choice practice exams with instant grading and explanations",
        icon="📝"
    )

    profile = StudentMemory.get_profile()

    tab_test, tab_history = st.tabs(["🎯 Take Practice Quiz", "📊 Performance History"])

    with tab_test:
        with st.expander("⚙️ Quiz Configuration & Material", expanded="quiz_data" not in st.session_state):
            source_mode = st.radio(
                "Source Material Option",
                options=["Pre-filled Subject Topic", "Upload Lecture Notes (PDF)", "Paste Study Material / Notes"],
                horizontal=True
            )

            study_text = ""
            topic_name = "General Assessment"

            if source_mode == "Pre-filled Subject Topic":
                selected_subject = st.selectbox("Select Subject", profile.subjects)
                sub_topics = {
                    "Artificial Intelligence": "Heuristic Search, A* Algorithm, and Alpha-Beta Pruning",
                    "Cloud Computing": "Virtualization, Docker Containerization, and Kubernetes Architecture",
                    "Compiler Design": "Lexical Analysis, LL(1) and LR Parsers, and Intermediate Code Generation",
                    "Web Technologies": "React Component Lifecycle, Node.js REST APIs, and Authentication",
                    "Database Management Systems": "Normalization (1NF-BCNF), ACID Properties, and B+ Trees"
                }
                default_topic = sub_topics.get(selected_subject, f"{selected_subject} Core Concepts")
                topic_input = st.text_input("Specific Topic / Chapter", value=default_topic)
                topic_name = f"{selected_subject} - {topic_input}"
                study_text = f"University syllabus and exam topics for {selected_subject}: {topic_input}. Core academic concepts, algorithms, and practical problems."

            elif source_mode == "Upload Lecture Notes (PDF)":
                uploaded_pdf = st.file_uploader("Upload Notes or Syllabus PDF", type=["pdf"], key="quiz_pdf")
                topic_name = uploaded_pdf.name if uploaded_pdf else "Uploaded Material"
                if uploaded_pdf:
                    docs = PDFDocumentLoader.load_from_bytes(uploaded_pdf.read(), uploaded_pdf.name)
                    study_text = "\n".join([d.page_content for d in docs])
                    st.info(f"Loaded {len(docs)} pages from `{uploaded_pdf.name}`.")

            else:
                topic_name = st.text_input("Topic Title", value="Software Engineering Principles")
                study_text = st.text_area("Paste Lecture Notes / Article Text", height=160)

            c1, c2 = st.columns(2)
            with c1:
                num_q = st.slider("Number of Questions", min_value=3, max_value=10, value=5)
            with c2:
                diff = st.select_slider("Difficulty Level", options=["Easy", "Medium", "Hard"], value="Medium")

            if st.button("🚀 Generate Quiz", key="btn_create_quiz", use_container_width=True):
                if not study_text:
                    st.error("Please provide study text or choose a valid subject topic.")
                else:
                    with st.spinner("AI Professor is generating questions and distractors..."):
                        res = QuizGeneratorTool.generate_quiz(
                            study_material=study_text,
                            topic=topic_name,
                            num_questions=num_q,
                            difficulty=diff
                        )

                        if res["success"]:
                            st.session_state["quiz_data"] = res["questions"]
                            st.session_state["quiz_topic"] = topic_name
                            st.session_state["quiz_submitted"] = False
                            st.session_state["student_answers"] = {}
                            st.success(f"Generated {len(res['questions'])} questions on '{topic_name}'!")
                            st.rerun()
                        else:
                            st.error(f"Quiz Generation Error: {res.get('error')}")

        # Interactive Test Taking Interface
        if "quiz_data" in st.session_state and st.session_state["quiz_data"]:
            questions = st.session_state["quiz_data"]
            topic = st.session_state.get("quiz_topic", "Practice Quiz")

            st.markdown(f"### 📋 Assessment: **{topic}**")
            st.caption("Select the best answer for each question and submit when finished.")

            # Form for answering questions
            with st.form("quiz_taking_form"):
                user_selections = {}

                for i, q in enumerate(questions):
                    st.markdown(f"#### Q{i+1}: {q.get('question')}")
                    options = q.get("options", [])

                    # Radio button for choices
                    selected = st.radio(
                        f"Choose your answer for Q{i+1}:",
                        options=options,
                        index=None,
                        key=f"q_choice_{i}"
                    )
                    user_selections[i] = selected
                    st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)

                submit_test = st.form_submit_button("🏁 Submit Test & Grade Answers", use_container_width=True)

            if submit_test:
                st.session_state["quiz_submitted"] = True
                st.session_state["user_selections"] = user_selections

            # Display Results & Explanations if Submitted
            if st.session_state.get("quiz_submitted", False):
                user_selections = st.session_state.get("user_selections", {})
                correct_count = 0

                st.markdown("---")
                st.markdown("## 📊 Assessment Results & Detailed Feedback")

                for i, q in enumerate(questions):
                    user_ans = user_selections.get(i)
                    correct_ans = q.get("correct_answer")
                    correct_idx = q.get("correct_option_index")
                    options = q.get("options", [])

                    # Identify correct option string
                    if correct_idx is not None and 0 <= correct_idx < len(options):
                        expected_ans = options[correct_idx]
                    else:
                        expected_ans = str(correct_ans)

                    is_correct = (user_ans == expected_ans) or (user_ans and correct_ans and str(user_ans).strip().lower() == str(correct_ans).strip().lower())

                    if is_correct:
                        correct_count += 1
                        st.markdown(f"✅ **Question {i+1}: Correct!**")
                        st.markdown(f"**Your Answer:** `{user_ans}`")
                    else:
                        st.markdown(f"❌ **Question {i+1}: Incorrect**")
                        st.markdown(f"- Your Answer: `{user_ans or 'No Answer Selected'}`")
                        st.markdown(f"- **Correct Answer:** `{expected_ans}`")

                    # Explanation block
                    st.markdown(
                        f"""
                        <div class="quiz-explanation-box">
                            <b>💡 Academic Explanation:</b><br/>{q.get('explanation', 'No explanation provided.')}
                        </div>
                        <br>
                        """,
                        unsafe_allow_html=True
                    )

                score_pct = (correct_count / len(questions)) * 100
                st.markdown(f"### 🏆 Final Score: **{correct_count} / {len(questions)} ({score_pct:.1f}%)**")

                if score_pct >= 80:
                    st.balloons()
                    st.success("🌟 Outstanding performance! You have mastered this topic.")
                elif score_pct >= 60:
                    st.info("👍 Good effort! Review the explanations above to solidify concepts.")
                else:
                    st.warning("⚠️ Consider revising this subject using the AI Study Planner before retaking the quiz.")

                # Save score to SQLite
                QuizGeneratorTool.record_quiz_score(
                    topic=topic,
                    score=correct_count,
                    total=len(questions),
                    questions_data=questions
                )

    with tab_history:
        st.markdown("### 📈 Recent Assessment History")
        history = get_recent_quizzes(limit=10)

        if not history:
            st.info("No quiz attempts recorded in SQLite yet. Take a quiz to view your score progression.")
        else:
            for q in history:
                pct = (q.score / q.total_questions) * 100 if q.total_questions > 0 else 0
                badge_color = "#10b981" if pct >= 70 else "#f59e0b" if pct >= 50 else "#ef4444"

                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:0.9rem 1.2rem; margin-bottom:0.8rem; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-weight:700; color:#1e293b;">{q.topic}</div>
                            <div style="font-size:0.8rem; color:#64748b;">Completed: {q.completed_at[:16].replace('T', ' ')}</div>
                        </div>
                        <div style="background:{badge_color}; color:#ffffff; font-weight:700; padding:0.3rem 0.8rem; border-radius:15px; font-size:0.9rem;">
                            {q.score} / {q.total_questions} ({pct:.0f}%)
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


if __name__ == "__main__" or True:
    main()
