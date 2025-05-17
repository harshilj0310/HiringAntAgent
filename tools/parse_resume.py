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
resume_parsing_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template="""
    Extract the following information from the resume text below:
    - Name
    - Contact Information (email, phone, LinkedIn, etc.)
    - Skills (technical and soft skills)
    - Experience (job title, company, duration, responsibilities)
    - Education (degree, institution, graduation date)
    - Certifications
    - Projects (title, description, technologies used)
    - Languages (spoken or programming languages)

    Return the output in JSON format.

    Resume Text:
    {resume_text}
    """
)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create parsing chain (Prompt -> LLM)
parsing_chain = resume_parsing_prompt | llm  

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")
    
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    return text

# Function to parse the resume using the chain
def parse_resume(resume_path):
    resume_text = extract_text_from_pdf(resume_path)
    parsed_data = parsing_chain.invoke({"resume_text": resume_text})  # Use the chain directly
    return json.loads(parsed_data.content)

# Define LangChain tool
resume_parsing_tool = Tool(
    name="Resume Parser",
    func=lambda: parse_resume("C:/Users/hp/Downloads/document.pdf"),  # Change this path
    description="Extracts structured information from a given resume."
)

# Run the tool
if __name__ == "__main__":
    try:
        resume_path = "C:/Users/hp/hiring-agent/HiringAntAgent/Resume/document (3) (1).pdf"  # Change this to your resume path
        parsed_resume = parse_resume(resume_path)
        print(json.dumps(parsed_resume, indent=2))
    except Exception as e:
        print(f"Error: {e}")
