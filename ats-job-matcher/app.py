import streamlit as st
from matcher import match_resume
import PyPDF2

st.set_page_config(page_title="ATS Job Matcher", page_icon="🎯")

st.title("🎯 ATS Job Match Analyzer")
st.markdown("Paste your resume and job description to see your match score!")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    uploaded = st.file_uploader("Upload PDF (optional)", type="pdf")
    resume_text = ""
    if uploaded:
        pdf = PyPDF2.PdfReader(uploaded)
        for page in pdf.pages:
            resume_text += page.extract_text()
        st.success("PDF loaded!")
    resume_text = st.text_area("Or paste resume here", value=resume_text, height=300)

with col2:
    st.subheader("💼 Job Description")
    jd_text = st.text_area("Paste job description here", height=300)

if st.button("🔍 Analyze Match", use_container_width=True):
    if resume_text and jd_text:
        with st.spinner("Analyzing..."):
            result = match_resume(resume_text, jd_text)

        score = result["score"]
        
        # Score color
        if score >= 70:
            color = "green"
            emoji = "🟢"
            msg = "Strong Match!"
        elif score >= 40:
            color = "orange"
            emoji = "🟡"
            msg = "Moderate Match"
        else:
            color = "red"
            emoji = "🔴"
            msg = "Weak Match"

        st.markdown(f"## {emoji} ATS Score: **:{color}[{score}%]** — {msg}")
        st.progress(int(score))

        col3, col4 = st.columns(2)
        with col3:
            st.success(f"✅ Matched Keywords ({len(result['matched'])})")
            for k in result["matched"]:
                st.markdown(f"• {k}")

        with col4:
            st.error(f"❌ Missing Keywords ({len(result['missing'])})")
            for k in result["missing"]:
                st.markdown(f"• {k}")
    else:
        st.warning("Please fill both resume and job description!")