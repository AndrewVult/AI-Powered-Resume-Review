```python
import streamlit as st
import pdfplumber
from openai import OpenAI, OpenAIError

# Initialize OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------------------
# Function to extract text from PDF
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    # Trim text to prevent token overload
    return text[:6000]

# -------------------------------
# Function to analyze resume
# -------------------------------
def analyze_resume(resume_text, job_description):
    prompt = f"""
    You are an HR assistant helping to evaluate resumes.

    Job description:
    {job_description}

    Candidate resume:
    {resume_text}

    Please analyze whether this candidate is a strong match for the role.
    Respond with strengths, weaknesses, and an overall recommendation.
    """

    models_to_try = ["gpt-4o-mini", "gpt-3.5-turbo"]

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            st.warning(f"⚠️ Model {model} failed: {str(e)}. Trying fallback...")

    return "❌ Sorry, all models failed. Please try again later."

# -------------------------------
# Streamlit App
# -------------------------------
st.title("AI-Powered Resume Review")

job_description = st.text_area("Paste the job description here:")

uploaded_files = st.file_uploader(
    "Upload candidate resumes (PDF only)", type="pdf", accept_multiple_files=True
)

if st.button("Analyze Resumes"):
    if not job_description.strip():
        st.error("Please paste a job description first.")
    elif not uploaded_files:
        st.error("Please upload at least one resume.")
    else:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Analyzing {uploaded_file.name}..."):
                resume_text = extract_text_from_pdf(uploaded_file)
                analysis = analyze_resume(resume_text, job_description)
                st.subheader(f"Results for {uploaded_file.name}")
                st.write(analysis)
```

