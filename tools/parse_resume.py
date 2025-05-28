import json
import os
import logging
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# ============================================
# ✅ Load environment variables from .env
# ============================================
# .env must include: OPENAI_API_KEY=your_openai_api_key
load_dotenv()

# ============================================
# ✅ Setup logging
# ============================================
log_file = os.path.join(os.path.dirname(__file__), "..", "logs", "resume_parser.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    filename='/home/shivam/Intern_Work/HiringAntAgent/scripts/logs/app.log',
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ============================================
# ✅ Define the resume parsing prompt
# ============================================
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

# ============================================
# ✅ Initialize the LLM
# ============================================
llm = ChatOpenAI(model="gpt-4", temperature=0)

# ============================================
# ✅ Create parsing chain
# ============================================
parsing_chain = resume_parsing_prompt | llm

# ============================================
# ✅ Function to extract text from PDF
# ============================================
def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    text = ""
    file = None
    try:
        file = open(pdf_path, "rb")
        reader = PdfReader(file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        logging.info(f"✅ Extracted text from PDF: {pdf_path}")
    except Exception as e:
        logging.error(f"❌ Error reading PDF: {e}")
        raise e
    finally:
        if file:
            file.close()
    return text

# ============================================
# ✅ Function to parse resume
# ============================================
def parse_resume(resume_path):
    try:
        resume_text = extract_text_from_pdf(resume_path)
        response = parsing_chain.invoke({"resume_text": resume_text})
        parsed = json.loads(response.content.strip())
        logging.info(f"✅ Successfully parsed resume: {resume_path}")
        return parsed
    except json.JSONDecodeError as je:
        logging.error(f"❌ JSON parsing failed: {je}")
        return {"error": "Invalid JSON returned from model."}
    except Exception as e:
        logging.exception(f"❌ Exception during resume parsing: {e}")
        return {"error": str(e)}

# ============================================
# ✅ Define LangChain tool
# ============================================
resume_parsing_tool = Tool(
    name="Resume Parser",
    func=lambda: parse_resume("C:/Users/hp/Downloads/document.pdf"),  # Update path as needed
    description="Extracts structured information from a given resume."
)

# ============================================
# ✅ Run the tool
# ============================================
if __name__ == "__main__":
    try:
        resume_path = "C:/Users/hp/hiring-agent/HiringAntAgent/Resume/document (3) (1).pdf"  # Update this
        result = parse_resume(resume_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        logging.exception("❌ Failed to run resume parser script")
        print(f"Error: {e}")
