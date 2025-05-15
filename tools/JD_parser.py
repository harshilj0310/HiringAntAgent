import json
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Define prompt
jd_parsing_prompt = PromptTemplate(
    input_variables=["jd_text"],
    template="""
    Extract structured information from the following Job Description (JD).
    Return a JSON object with the following fields:
    - "job_title": (string)
    - "required_skills": (list of strings)
    - "preferred_skills": (list of strings)
    - "experience_required": (string, years required)
    - "location": (string)
    - "job_type": (Full-time, Part-time, Contract, etc.)
    - "education_required": (string)
    - "responsibilities": (list of key responsibilities)

    Job Description:
    {jd_text}

    JSON Output:
    """
)

llm = ChatOpenAI(model="gpt-4", temperature=0)
jd_parsing_chain = jd_parsing_prompt | llm


def parse_job_description(jd_input):
    # Check if it's a valid file path
    if isinstance(jd_input, str) and os.path.exists(jd_input):
        if jd_input.endswith(".pdf"):
            reader = PdfReader(jd_input)
            jd_text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
        else:  # assume .txt
            with open(jd_input, "r", encoding="utf-8", errors="ignore") as f:
                jd_text = f.read()
    else:
        # assume it's raw text, not a path
        jd_text = jd_input

    response = jd_parsing_chain.invoke({"jd_text": jd_text})

    try:
        parsed_data = json.loads(response.content.strip())
    except json.JSONDecodeError:
        parsed_data = {"error": "Invalid JSON returned from model"}

    return parsed_data



if __name__ == "__main__":
    sample_jd = """
    We are hiring a Data Scientist with 3+ years of experience in Python, NLP, and Machine Learning.
    Responsibilities include building predictive models and analyzing large datasets.
    Preferred skills: Experience with cloud platforms like AWS, Azure, or GCP.
    Location: Mumbai, India.
    Job Type: Full-time
    Education: B.Tech or higher in CS or related field
    """
    result = parse_job_description(sample_jd)
    print(json.dumps(result, indent=2, ensure_ascii=False))
