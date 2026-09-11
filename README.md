# 🏛️ CampusAI – Intelligent Student Support Assistant

> **A production-grade, university-themed AI assistant for higher education students, featuring Retrieval-Augmented Generation (RAG), Persistent Conversational Memory, and AI Tool Calling.**

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://www.langchain.com/)
[![Google Gemini](https://img.shields.io/badge/LLM-Google%20Gemini%201.5-orange.svg)](https://aistudio.google.com/)
[![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)

---

## 📌 Project Overview

In large academic institutions, students frequently struggle to navigate complex academic regulations, keep track of scattered circular deadlines, obtain personalized study schedules, and test their conceptual understanding.

**CampusAI** solves these problems by providing an intelligent, personalized academic companion. Built with **LangChain**, **Google Gemini**, **ChromaDB**, **SQLite**, and **Streamlit**, CampusAI understands university policies, remembers individual student profiles, synthesizes bureaucratic circulars into clear action items, and generates science-backed revision roadmaps.

---

## 🚀 Key Features

### 1. 💬 AI College Assistant (Retrieval-Augmented Generation)
- **PDF Document Ingestion**: Ingests university regulations, course syllabus handbooks, exam circulars, and FAQs.
- **Semantic Chunking & Embedding**: Chunks PDF content via `RecursiveCharacterTextSplitter` and embeds them using Google `text-embedding-004`.
- **Persistent ChromaDB Vector Store**: Performs cosine similarity search to retrieve relevant context.
- **Source Attribution**: Every response includes expandable citations displaying the document name, page number, and exact text excerpt.
- **Dynamic Personalization**: Automatically tailors answers to the active student's department, semester, and enrolled subjects.

### 2. 🧠 Student Memory (SQLite Context Persistence)
- **Student Profile Management**: Stores Student Name, Roll Number, Department, Semester, Enrolled Subjects, Target GPA, and Preferred Language in a local SQLite database.
- **Dynamic System Augmentation**: Injects student identity into LLM system prompts across all tools without repetitive prompting.
- **Multi-Turn Chat History**: Preserves conversation history across sessions in SQLite.

### 3. 📅 AI Study Planner
- **Intelligent Timetabling**: Generates day-by-day revision schedules based on exam dates, available daily hours, and subject difficulties.
- **Cognitive Science Strategies**: Incorporates spaced repetition, Pomodoro intervals, and interleaved practice.
- **Export & Storage**: Save generated study plans in SQLite and download as Markdown.

### 4. 📄 College Notice & Circular Summarizer
- **Executive Summaries**: Distills multi-page circulars into a concise 2-sentence brief.
- **Critical Deadlines & Timelines**: Highlights fee deadlines, hall ticket release dates, and exam dates.
- **Actionable Student Checklist**: Provides step-by-step required actions for students.

### 5. 📝 Practice Quiz & Assessment Generator
- **Rigorously Formatted MCQs**: Generates test-standard multiple-choice questions from lecture notes, syllabus chapters, or topics.
- **Interactive Quiz Taking Mode**: Students take tests interactively directly inside the Streamlit UI.
- **Automated Grading & Explanations**: Instant score computation, celebration animations for high scores, and thorough academic explanations for every question.
- **Performance History**: Tracks past quiz scores in SQLite.

---

## 🏗️ System Architecture

```
CampusAI Architecture
├── Presentation Layer (Streamlit Multi-page Interface)
│   ├── 🏠 Home: Snapshot, quick stats, active student card, quick action tiles
│   ├── 💬 College Assistant: RAG document search, source citations, conversational memory
│   ├── 📅 Study Planner: AI schedule generation, priority matrix, downloadable timetable
│   ├── 📝 Quiz Generator: Dynamic MCQ generator from notes/syllabus with interactive test mode
│   ├── 📄 Notice Summarizer: Key highlights, deadline extractor, actionable checklist
│   └── 👤 Student Profile: SQLite-backed profile (dept, semester, subjects, target GPA)
│
├── Intelligence & Tool Layer (LangChain + Google Gemini)
│   ├── RAG Engine: PDF Document Loader -> Recursive Splitter -> Gemini Embeddings -> ChromaDB
│   ├── Memory Layer: SQLite Student Profile Context + Conversational Buffer Window
│   └── Specialized AI Tools: Study Planner Tool, Quiz Generator Tool, Notice Summarizer Tool
│
└── Persistence Layer
    ├── Vector Store: ChromaDB (persistent local collection with cosine space)
    ├── Relational Store: SQLite (campus_ai.db for student profile, chat history, and plans)
    └── Storage: documents/ for official university regulations, syllabus, and notices
```

---

## 📂 Project Structure

```
CampusAI/
│── app.py                   # Streamlit main entrypoint & navigation router
│── requirements.txt         # Python project dependencies
│── .env                     # Local environment variables (API keys & paths)
│── .env.example             # Example environment configuration
│── README.md                # Comprehensive project documentation
│
├── pages/                   # Streamlit Official Multipage Views
│   ├── 1_Home.py            # Dashboard & overview
│   ├── 2_College_Assistant.py # RAG College Assistant chat
│   ├── 3_Study_Planner.py   # AI Timetable generator
│   ├── 4_Quiz_Generator.py  # Interactive MCQ test generator
│   ├── 5_Notice_Summarizer.py # Circular & Notice summarizer
│   └── 6_Student_Profile.py # Student profile SQLite manager
│
├── rag/                     # Retrieval-Augmented Generation Engine
│   ├── __init__.py
│   ├── loader.py            # PDF text & metadata extractor (PyPDF2/pypdf)
│   ├── splitter.py          # Semantic text chunker
│   ├── embeddings.py        # Google Gemini embeddings wrapper
│   ├── vectorstore.py       # ChromaDB persistent vector database manager
│   └── retriever.py         # Multi-turn RAG QA pipeline
│
├── memory/                  # Memory & Persona Layer
│   ├── __init__.py
│   ├── student_memory.py    # SQLite student profile prompt injection
│   └── chat_memory.py       # Conversational buffer & message logs
│
├── tools/                   # AI Tools & Agents
│   ├── __init__.py
│   ├── study_planner.py     # Study plan generation tool
│   ├── summarizer.py        # Notice summarizer tool
│   └── quiz_generator.py    # Multiple choice question generator & parser
│
├── database/                # SQLite Relational Persistence
│   ├── __init__.py
│   ├── models.py            # Dataclass models (Profile, Plan, Chat, Quiz)
│   └── sqlite_db.py         # SQLite connection manager & CRUD queries
│
├── documents/               # University Knowledge Base (Included Sample PDFs)
│   ├── academic_regulations_2024.pdf
│   ├── cse_curriculum_and_syllabus.pdf
│   ├── campus_placement_circular_2024.pdf
│   ├── end_semester_examination_notice.pdf
│   └── campus_hostel_and_facility_guide.pdf
│
├── assets/                  # Styling & Brand Assets
│   └── style.css            # University-themed modern stylesheet
│
└── utils/                   # Utilities & Setup Helpers
    ├── __init__.py
    ├── config.py            # Centralized settings & path configuration
    ├── helpers.py           # UI components, badges & sidebar widgets
    └── sample_docs_generator.py # Automated sample PDF generator
```

---

## ⚙️ Installation & Setup

### 1. Clone or Open the Repository
```bash
cd CampusAI-studsupport
```

### 2. Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Google Gemini API Key
Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).

You can set it in two ways:
1. **Option A (Recommended)**: Create a `.env` file (or edit the existing one):
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   EMBEDDING_MODEL=models/text-embedding-004
   ```
2. **Option B**: Enter your API key directly in the application's sidebar under **AI Configuration** at runtime.

### 5. Generate Sample University PDFs (Pre-built)
The project includes a generator script that builds 5 realistic university PDFs:
```bash
python utils/sample_docs_generator.py
```

### 6. Run the Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser!

---

## 🧪 Sample Testing Queries

Try these sample questions in the **Ask College Assistant** page to test RAG retrieval:

1. **Attendance Regulations**:
   > *"What is the minimum attendance required to appear for end semester examinations, and what is the condonation rule?"*
   - **Expected response**: 75% minimum aggregate attendance required. Medical condonation available between 65% and 74.9% with Rs. 1,000 fee. Below 65% is detained. Source: `academic_regulations_2024.pdf` (Page 1).

2. **Placement Drive**:
   > *"What is the eligibility criteria and registration deadline for the Mega Placement Drive?"*
   - **Expected response**: B.E./B.Tech (CSE, IT, ECE, AI&DS) with CGPA >= 7.50, no arrears. Deadline: October 25, 2024, at 5:00 PM. Source: `campus_placement_circular_2024.pdf`.

3. **Student Profile Personalization**:
   > *"What core subjects should I focus on for my upcoming exams?"*
   - **Expected response**: Uses active student profile (Semester 6 Computer Science) to give tailored advice on CS8601 (AI & ML), CS8603 (Compiler Design), and CS8602 (Cloud Computing).

4. **Exam Notice Deadlines**:
   > *"When is the last date to pay semester exam fees with and without late fine?"*
   - **Expected response**: Without late fine: October 24, 2024. With late fine (Rs. 500): October 25 to October 29, 2024. Source: `end_semester_examination_notice.pdf`.

---

## 🎓 Viva & College Examiner Q&A

| Question | Explanation |
|---|---|
| **Why RAG instead of Fine-Tuning?** | University documents (exam dates, fee circulars, regulations) change every semester. RAG allows updating the knowledge base instantly by uploading a PDF without expensive retraining. It also provides verifiable source citations. |
| **How does Student Memory work?** | Profile details (Department, Semester, Subjects, Target GPA) are stored in SQLite. The `StudentMemory` module dynamically constructs a personalized system prompt on each LLM call so the assistant always knows the student's background. |
| **Why ChromaDB?** | ChromaDB is an open-source, embeddable vector database that runs locally without external server infrastructure, offering fast cosine similarity search and persistent on-disk storage. |
| **How are Hallucinations prevented?** | By grounding answers strictly within retrieved document chunks, enforcing source citation metadata, and configuring low model temperature (0.2–0.3). |

---

## 📄 License
This project is developed for educational and academic demonstration purposes.
Licensed under the [MIT License](LICENSE).
