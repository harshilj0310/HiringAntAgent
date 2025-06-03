import json
import os
import logging,yaml
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from io import BytesIO

def extract_text_from_pdf_bytes(pdf_bytes):
    try:
        pdf_stream = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        logging.info(f"✅ Extracted text from PDF bytes")
        return text
    except Exception as e:
        logging.error(f"❌ Error reading PDF bytes: {e}")
        raise e
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
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ============================================
# ✅ Define the resume parsing prompt
# ============================================
# Load YAML config once at the module level
CONFIG_PATH = 'app/config.yaml'

with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

resume_prompt_template = config.get("prompts", {}).get("resume_parsing", "")

resume_parsing_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template=resume_prompt_template
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
def parse_resume(input_data):
    """
    input_data: str (file path) OR bytes (PDF content)
    """
    try:
        if isinstance(input_data, bytes):
            resume_text = extract_text_from_pdf_bytes(input_data)
        elif isinstance(input_data, str):
            resume_text = extract_text_from_pdf(input_data)
        else:
            raise TypeError("parse_resume input must be file path string or bytes")

        response = parsing_chain.invoke({"resume_text": resume_text})
        parsed = json.loads(response.content.strip())
        logging.info(f"✅ Successfully parsed resume")
        return parsed

    except json.JSONDecodeError as je:
        logging.error(f"❌ JSON parsing failed: {je}")
        return {"error": "Invalid JSON returned from model."}
    except Exception as e:
        logging.exception(f"❌ Exception during resume parsing: {e}")
        return {"error": str(e)}
