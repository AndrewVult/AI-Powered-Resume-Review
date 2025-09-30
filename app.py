import streamlit as st
import pdfplumber
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Function to extract text from uploaded PDF resumes
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# Function to analyze resume against job description
def analyze_resume(resume_text, job_description):
    prompt = f"""
    You are an HR assistant. Evaluate the following resume against the job description. 
    Highlight strengths, weaknesses, and whether this candidate is a strong fit.

    Job Description:
    {job_description}

    Resume:
    {resume_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",   # can also use "gpt-4.1-mini" or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a professional HR assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content

# Streamlit UI
st.title("AI-Powered Resume Reviewer")

job_description = st.text_area("Paste the Job Description:", height=200)

uploaded_files = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

if st.button("Analyze Resumes"):
    if job_description and uploaded_files:
        for uploaded_file in uploaded_files:
            st.subheader(f"Results for: {uploaded_file.name}")
            resume_text = extract_text_from_pdf(uploaded_file)

            if resume_text.strip():
                analysis = analyze_resume(resume_text, job_description)
                st.write(analysis)
            else:
                st.error(f"No text could be extracted from {uploaded_file.name}")
    else:
        st.warning("Please provide a job description and upload at least one resume.")
