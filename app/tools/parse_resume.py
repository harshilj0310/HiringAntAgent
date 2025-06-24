import json
import os
import logging
from io import BytesIO
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.config import CONFIG

load_dotenv()

logger = logging.getLogger(__name__)

resume_prompt_template = CONFIG.get("prompts", {}).get("resume_parsing", "")
if not resume_prompt_template or "{resume_text}" not in resume_prompt_template:
    logger.critical("❌ Resume parsing prompt is missing or invalid in CONFIG.")
    raise ValueError("Invalid prompt template. Please define `resume_parsing` properly in CONFIG.")

resume_parsing_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template=resume_prompt_template
)

model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
temperature = float(os.getenv("OPENAI_TEMPERATURE", 0))
max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 1024))

try:
    llm = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        request_timeout=15
    )
except Exception as e:
    logger.critical(f"❌ Failed to initialize LLM: {e}")
    raise

parsing_chain = resume_parsing_prompt | llm

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        pdf_stream = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)
        text = "\n".join(filter(None, [page.extract_text() for page in reader.pages]))
        logger.info("✅ Extracted text from PDF bytes")
        return text
    except Exception as e:
        logger.error(f"❌ Error reading PDF bytes: {e}")
        raise ValueError("Unable to read PDF content.")

def extract_text_from_pdf(pdf_path: str) -> str:
    if not os.path.exists(pdf_path) or not pdf_path.lower().endswith(".pdf"):
        raise FileNotFoundError(f"Invalid file path: {pdf_path}")
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            text = "\n".join(filter(None, [page.extract_text() for page in reader.pages]))
            logger.info(f"✅ Extracted text from PDF: {pdf_path}")
            return text
    except Exception as e:
        logger.error(f"❌ Error reading PDF: {e}")
        raise ValueError("Unable to extract text from PDF.")

def parse_resume(input_data: bytes | str) -> dict:
    try:
        if isinstance(input_data, bytes):
            resume_text = extract_text_from_pdf_bytes(input_data)
        elif isinstance(input_data, str):
            resume_text = extract_text_from_pdf(input_data)
        else:
            raise TypeError("parse_resume input must be a file path string or bytes")

        resume_text = resume_text[:3000]
        logger.debug("🔍 Resume text sent to GPT (truncated):")
        logger.debug(resume_text)

        response = parsing_chain.invoke({"resume_text": resume_text})
        parsed = json.loads(response.content.strip())
        logger.info("✅ Successfully parsed resume")
        return parsed

    except json.JSONDecodeError as je:
        logger.error(f"❌ JSON parsing failed: {je}")
        return {"error": "Invalid JSON returned from model."}
    except Exception as e:
        logger.exception(f"❌ Exception during resume parsing: {e}")
        return {"error": str(e)}
