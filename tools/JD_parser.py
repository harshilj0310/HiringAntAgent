import json
import os
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

# Define the prompt
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

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create parsing chain (Prompt -> LLM)
jd_parsing_chain = jd_parsing_prompt | llm  


# Function to parse the resume using the chain
def parse_job_description(jd_text):
    response = jd_parsing_chain.invoke({"jd_text": jd_text})

    # Extract structured JSON response safely
    try:
        parsed_data = json.loads(response.content.strip())  # Extracts response properly
    except json.JSONDecodeError:
        parsed_data = {"error": "Invalid JSON returned from model"}

    return parsed_data


if __name__ == "__main__":
    jd_text = """
    We are hiring a Data Scientist with 3+ years of experience in Python, NLP, and Machine Learning.
    Responsibilities include building predictive models and analyzing large datasets.
    Preferred skills: Experience with cloud platforms like AWS, Azure, or GCP.
    Location: Mumbai, India.
    """

    parsed_jd = parse_job_description(jd_text)
    print(json.dumps(parsed_jd, indent=2))


    
