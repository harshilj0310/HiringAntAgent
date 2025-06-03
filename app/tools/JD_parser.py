import json
import os
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from io import BytesIO

# ============================================
# ✅ Setup Logging
# ============================================
log_file = os.path.join(os.path.dirname(__file__), "..", "logs", "jd_parser.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ============================================
# ✅ Load Environment Variables
# ============================================
load_dotenv()

# ============================================
# ✅ Prompt Template for JD Parsing
# ============================================
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
    - "job_type": (Full-time, Part-time, Contract, Internship etc.)
    - "education_required": (string)
    - "responsibilities": (list of key responsibilities)

    Job Description:
    {jd_text}

    JSON Output:
    """
)

# ✅ Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)
jd_parsing_chain = jd_parsing_prompt | llm

# ============================================
# ✅ JD Parsing Function
# ============================================
def parse_job_description(jd_input):
    jd_text = ""

    try:
        if isinstance(jd_input, bytes):
            try:
                # Try PDF first
                pdf_stream = BytesIO(jd_input)
                reader = PdfReader(pdf_stream)
                jd_text = " ".join(
                    page.extract_text() for page in reader.pages if page.extract_text()
                )
                logging.info("✅ Extracted text from PDF binary")
            except Exception as pdf_err:
                try:
                    # Fallback to decoding as plain text
                    jd_text = jd_input.decode("utf-8", errors="ignore")
                    logging.info("ℹ️ Binary input was plain text, decoded successfully")
                except Exception as txt_err:
                    logging.error(f"❌ Failed to parse binary JD: {txt_err}")
                    return {"error": f"Invalid binary input: {txt_err}"}

        elif isinstance(jd_input, str) and os.path.exists(jd_input):
            if jd_input.endswith(".pdf"):
                reader = PdfReader(jd_input)
                jd_text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
                logging.info(f"✅ Extracted text from PDF file: {jd_input}")
            else:
                with open(jd_input, "r", encoding="utf-8", errors="ignore") as f:
                    jd_text = f.read()
                    logging.info(f"✅ Read text from TXT file: {jd_input}")
        elif isinstance(jd_input, str):
            jd_text = jd_input
            logging.info("📄 Received raw JD text input.")
        else:
            raise TypeError("Input must be bytes, a file path string, or a raw string.")

        # Send to LLM
        response = jd_parsing_chain.invoke({"jd_text": jd_text})

        try:
            parsed_data = json.loads(response.content.strip())
            logging.info("✅ Successfully parsed JD JSON.")
        except json.JSONDecodeError as e:
            logging.error(f"❌ JSON parsing error from LLM: {e}")
            parsed_data = {"error": "Invalid JSON returned from model."}

        return parsed_data

    except Exception as e:
        logging.exception(f"❌ Unexpected error in parse_job_description: {e}")
        return {"error": str(e)}
