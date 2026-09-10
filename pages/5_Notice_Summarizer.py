"""
Notice Summarizer Page for CampusAI.
Summarizes administrative circulars, extracts deadlines, important dates, and action items.
"""

import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.summarizer import NoticeSummarizerTool
from rag.loader import PDFDocumentLoader
from utils.config import DOCUMENTS_DIR
from utils.helpers import setup_page


def main():
    setup_page(
        title="College Notice & Circular Summarizer",
        subtitle="Extract key highlights, critical deadlines, and actionable student checklists from circulars",
        icon="📄"
    )

    col_input, col_output = st.columns([1, 1])

    with col_input:
        st.markdown("### 📥 Select or Upload Notice")

        mode = st.radio(
            "Input Mode",
            options=["Select Sample Campus Circular", "Upload Notice (PDF)", "Paste Notice Text"],
            horizontal=True
        )

        notice_text = ""
        notice_title = "University Circular"

        if mode == "Select Sample Campus Circular":
            sample_notices = {
                "Mega Placement Drive 2024 (TCS, Google, Microsoft)": "campus_placement_circular_2024.pdf",
                "End Semester Examination Schedule & Fees (Nov/Dec 2024)": "end_semester_examination_notice.pdf",
                "Hostel Guidelines & Campus Facilities Guide": "campus_hostel_and_facility_guide.pdf"
            }
            selected_sample = st.selectbox("Choose Sample Circular", list(sample_notices.keys()))
            notice_title = selected_sample

            doc_path = DOCUMENTS_DIR / sample_notices[selected_sample]
            if doc_path.exists():
                docs = PDFDocumentLoader.load_pdf(str(doc_path))
                notice_text = "\n\n".join([d.page_content for d in docs])
                st.info(f"Loaded `{doc_path.name}` ({len(docs)} pages).")

        elif mode == "Upload Notice (PDF)":
            up_pdf = st.file_uploader("Upload Official Notice (PDF)", type=["pdf"])
            if up_pdf:
                notice_title = up_pdf.name
                docs = PDFDocumentLoader.load_from_bytes(up_pdf.read(), up_pdf.name)
                notice_text = "\n\n".join([d.page_content for d in docs])
                st.info(f"Extracted {len(docs)} pages from uploaded PDF.")

        else:
            notice_title = st.text_input("Notice Title", value="Circular from Dean of Student Affairs")
            notice_text = st.text_area("Paste Full Notice Text", height=250, placeholder="Paste bureaucratic announcement text here...")

        if st.button("⚡ Summarize Notice", key="btn_run_summarize", use_container_width=True):
            if not notice_text.strip():
                st.error("Please provide or select notice content.")
            else:
                with st.spinner("AI Administrator is analyzing notice dates and deadlines..."):
                    res = NoticeSummarizerTool.summarize_notice(
                        notice_text=notice_text,
                        notice_title=notice_title
                    )

                    if res["success"]:
                        st.session_state["active_notice_summary"] = res["summary_markdown"]
                        st.session_state["active_notice_title"] = notice_title
                        st.success("Analysis complete!")
                    else:
                        st.error(f"Error: {res.get('error')}")

    with col_output:
        st.markdown("### 📋 Executive Summary & Action Items")

        if "active_notice_summary" in st.session_state:
            st.markdown(f"#### 📢 {st.session_state.get('active_notice_title', 'Circular Summary')}")
            st.markdown(st.session_state["active_notice_summary"])

            st.download_button(
                label="📥 Download Notice Summary",
                data=st.session_state["active_notice_summary"],
                file_name=f"Summary_{st.session_state.get('active_notice_title', 'Notice')[:20]}.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.markdown(
                """
                <div style="background:#f8fafc; border:2px dashed #cbd5e1; border-radius:12px; padding:2.5rem; text-align:center; color:#64748b;">
                    <div style="font-size:2.5rem; margin-bottom:0.5rem;">📄</div>
                    <div style="font-weight:600;">No Notice Summarized Yet</div>
                    <div style="font-size:0.85rem; margin-top:0.3rem;">Select a sample circular or upload a PDF on the left to extract key deadlines and action items.</div>
                </div>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__" or True:
    main()
