"""Minimal Streamlit client for GovPrepAI."""

from __future__ import annotations

import httpx
import streamlit as st


API_BASE_URL = "http://localhost:8000"
EXAMS = ["UPSC", "SSC", "GATE", "Banking", "State PSC", "Railway"]


st.set_page_config(page_title="GovPrepAI", page_icon="GP", layout="wide")
st.title("GovPrepAI")
st.caption("Smart Government Exam Preparation Multi-Agent System")

with st.sidebar:
    st.header("Exam Setup")
    user_id = st.text_input("User ID", value="default")
    exam_type = st.selectbox("Exam Type", EXAMS)

tabs = st.tabs(["Plan Agent", "Syllabus", "Mock Test", "Study Plan", "Notes"])

with tabs[0]:
    goal = st.text_area(
        "Preparation goal or doubt",
        value="Create a complete preparation roadmap with syllabus, resources, weightage, and practice plan.",
        height=120,
    )
    if st.button("Run Plan-and-Execute Agent", type="primary"):
        with st.spinner("GovPrepAI agents are planning and executing..."):
            response = httpx.post(
                f"{API_BASE_URL}/api/prepare",
                json={"goal": goal, "exam_type": exam_type, "user_id": user_id},
                timeout=180,
            )
        response.raise_for_status()
        data = response.json()
        st.markdown(data.get("final_output") or "No final output returned.")
        with st.expander("Execution Trace"):
            st.json(data)

with tabs[1]:
    if st.button("Load Syllabus"):
        with st.spinner("Finding and structuring syllabus..."):
            response = httpx.post(
                f"{API_BASE_URL}/api/syllabus",
                json={"exam_type": exam_type},
                timeout=120,
            )
        response.raise_for_status()
        st.markdown(response.json()["result"])

with tabs[2]:
    topic = st.text_input("Topic", value="Quantitative Aptitude")
    if st.button("Generate Mock Test"):
        with st.spinner("Generating mock test..."):
            response = httpx.post(
                f"{API_BASE_URL}/api/mock-test",
                json={"exam_type": exam_type, "topic": topic},
                timeout=120,
            )
        response.raise_for_status()
        st.markdown(response.json()["result"])

with tabs[3]:
    target_date = st.text_input("Target Date", value="2026-12-31")
    weak_topics_text = st.text_input("Weak Topics", value="Percentage, Current Affairs")
    if st.button("Generate Study Plan"):
        weak_topics = [topic.strip() for topic in weak_topics_text.split(",") if topic.strip()]
        with st.spinner("Building timetable..."):
            response = httpx.post(
                f"{API_BASE_URL}/api/study-plan",
                json={
                    "exam_type": exam_type,
                    "target_date": target_date,
                    "weak_topics": weak_topics,
                },
                timeout=120,
            )
        response.raise_for_status()
        st.markdown(response.json()["result"])

with tabs[4]:
    uploaded = st.file_uploader("Upload PDF notes", type=["pdf"])
    if uploaded and st.button("Index Notes"):
        files = {"file": (uploaded.name, uploaded.getvalue(), "application/pdf")}
        with st.spinner("Indexing notes in ChromaDB..."):
            response = httpx.post(
                f"{API_BASE_URL}/api/upload-notes",
                params={"user_id": user_id},
                files=files,
                timeout=180,
            )
        response.raise_for_status()
        st.success(f"Indexed {response.json()['chunk_count']} chunks.")

