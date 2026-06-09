import os
import json
import streamlit as st

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from utils import extract_text

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📊",
    layout="wide"
)

# ==========================
# LOAD ENV
# ==========================

load_dotenv()

# ==========================
# CUSTOM CSS
# ==========================

st.markdown("""
<style>

.hero {
    padding: 25px;
    border-radius: 15px;
    background: linear-gradient(90deg,#2563EB,#7C3AED);
    color: white;
    text-align: center;
    margin-bottom: 25px;
}

.hero h1 {
    margin-bottom: 10px;
}

.hero h4 {
    margin-bottom: 10px;
    opacity: 0.95;
}

.hero p {
    opacity: 0.85;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# HERO SECTION
# ==========================

st.markdown("""
<div class='hero'>
    <h1>📊 ATS Resume Analyzer</h1>
    <h4>AI-Powered Resume Screening & Skill Gap Analysis</h4>
    <p>Resume Analysis • ATS Scoring • Skill Matching • Career Recommendations</p>
</div>
""", unsafe_allow_html=True)

# ==========================
# INPUT SECTION
# ==========================

col1, col2 = st.columns([1, 2])

with col1:
    resume_file = st.file_uploader(
        "📄 Upload Resume",
        type=["pdf", "docx", "txt"]
    )

with col2:
    job_description = st.text_area(
        "💼 Paste Job Description",
        height=300
    )

# ==========================
# ANALYZE BUTTON
# ==========================

if st.button("🚀 Analyze Resume"):

    if resume_file is None:
        st.warning("Please upload a resume.")
        st.stop()

    if not job_description.strip():
        st.warning("Please paste a Job Description.")
        st.stop()

    resume_text = extract_text(resume_file)

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = f"""
You are an expert ATS Resume Analyzer and Career Coach.

Compare the Resume and Job Description.

Evaluate:
1. Job Role Match
2. Skills Match
3. Missing Skills
4. Candidate Strengths
5. Career Recommendations

Return ONLY valid JSON.

Format:

{{
    "job_role": "",
    "match_score": "",
    "matched_skills": [],
    "missing_skills": [],
    "candidate_strengths": [],
    "recommendations": [],
    "overall_feedback": ""
}}

Resume:
{resume_text}

Job Description:
{job_description}
"""

    with st.spinner("🔍 Analyzing Resume..."):
        response = llm.invoke(prompt)

    try:

        content = response.content
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        result = json.loads(content)

        score_text = str(
            result.get(
                "match_score",
                "0"
            )
        )

        try:
            score = int(
                ''.join(
                    filter(
                        str.isdigit,
                        score_text
                    )
                )
            )
        except:
            score = 0

        st.success("✅ Analysis Completed Successfully")

        # ==========================
        # METRICS
        # ==========================

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "🎯 ATS Score",
                f"{score}%"
            )

        with col2:
            st.metric(
                "💼 Job Role",
                result.get(
                    "job_role",
                    "N/A"
                )
            )

        with col3:
            st.metric(
                "✅ Matched Skills",
                len(
                    result.get(
                        "matched_skills",
                        []
                    )
                )
            )

        st.progress(score / 100)

        if score >= 80:
            st.success("🟢 Strong Match")
        elif score >= 60:
            st.warning("🟡 Moderate Match")
        else:
            st.error("🔴 Low Match")

        # ==========================
        # TABS
        # ==========================

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📊 Dashboard",
                "🎯 Skills Match",
                "💪 Strengths & Tips",
                "📄 Report"
            ]
        )

        # ==========================
        # DASHBOARD
        # ==========================

        with tab1:

            st.subheader("🎯 Match Summary")

            st.write(
                result.get(
                    "overall_feedback",
                    "No feedback available."
                )
            )

        # ==========================
        # SKILLS
        # ==========================

        with tab2:

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    "✅ Matched Skills"
                )

                for skill in result.get(
                    "matched_skills",
                    []
                ):
                    st.success(
                        f"✓ {skill}"
                    )

            with col2:

                st.subheader(
                    "❌ Missing Skills"
                )

                for skill in result.get(
                    "missing_skills",
                    []
                ):
                    st.error(
                        f"✗ {skill}"
                    )

        # ==========================
        # STRENGTHS
        # ==========================

        with tab3:

            st.subheader(
                "💪 Candidate Strengths"
            )

            for strength in result.get(
                "candidate_strengths",
                []
            ):
                st.info(
                    strength
                )

            st.subheader(
                "📚 Recommendations"
            )

            for rec in result.get(
                "recommendations",
                []
            ):
                st.warning(
                    rec
                )

        # ==========================
        # REPORT
        # ==========================

        with tab4:

            st.subheader(
                "📄 Full Analysis Report"
            )

            st.json(result)

            report_json = json.dumps(
                result,
                indent=4
            )

            st.download_button(
                label="⬇ Download Report",
                data=report_json,
                file_name="ATS_Resume_Report.json",
                mime="application/json"
            )

    except Exception as e:

        st.error(
            "Could not parse model response."
        )

        st.write(
            response.content
        )

        st.exception(e)

# ==========================
# FOOTER
# ==========================

st.markdown("---")

st.caption(
    "📊 ATS Resume Analyzer | Powered by Groq GPT-OSS-120B"
)