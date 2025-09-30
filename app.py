import streamlit as st
import openai
import PyPDF2
import pandas as pd
import io

# --- SETUP ---
st.set_page_config(page_title="AI Resume Screener", layout="wide")
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- HELPERS ---
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def analyze_resume(resume_text, job_description):
    prompt = f"""
    You are an HR assistant. Compare this resume to the job description and provide:
    - Match Score (0-100)
    - Key Strengths
    - Red Flags / Concerns
    - Recommendation (e.g., Interview, Maybe, Reject)

    Job Description:
    {job_description}

    Resume:
    {resume_text}

    Return the answer in JSON with keys: score, strengths, red_flags, recommendation.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    try:
        content = response.choices[0].message["content"]
        result = eval(content) if content.strip().startswith("{") else {}
        return result
    except Exception:
        return {"score": None, "strengths": "Parsing error", "red_flags": "Parsing error", "recommendation": "Check manually"}

# --- UI ---
st.title("📄 AI Resume Screener")
st.write("Upload resumes (PDF) and paste a job description to get AI-powered evaluations.")

job_description = st.text_area("Paste Job Description", height=200)
uploaded_files = st.file_uploader("Upload one or more resumes (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files and job_description:
    results = []
    for file in uploaded_files:
        resume_text = extract_text_from_pdf(file)
        analysis = analyze_resume(resume_text, job_description)
        results.append({
            "Candidate": file.name,
            "Score": analysis.get("score"),
            "Strengths": analysis.get("strengths"),
            "Red Flags": analysis.get("red_flags"),
            "Recommendation": analysis.get("recommendation"),
        })

    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

    # CSV Download
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("⬇️ Download Results as CSV", data=csv_buffer.getvalue(),
                       file_name="resume_screening_results.csv", mime="text/csv")
