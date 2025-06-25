import json
import os
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from io import BytesIO
from app.config import CONFIG

load_dotenv(override=True)

MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
MODEL_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0))
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 2048))

logger = logging.getLogger(__name__)

jd_parsing_prompt = PromptTemplate(
    input_variables=["jd_text"],
    template=CONFIG["prompts"]["jd_parsing"]
)

llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=MODEL_TEMPERATURE,
    max_tokens=MAX_TOKENS
)

jd_parsing_chain = jd_parsing_prompt | llm

def parse_job_description(jd_input):
    logger.info("Entering the JD Parser function")
    jd_text = ""

    try:
        if isinstance(jd_input, bytes):
            try:
                pdf_stream = BytesIO(jd_input)
                reader = PdfReader(pdf_stream)
                jd_text = " ".join(
                    page.extract_text() for page in reader.pages if page.extract_text()
                )
                logger.info("✅ Extracted text from PDF binary")
            except Exception:
                try:
                    jd_text = jd_input.decode("utf-8", errors="ignore")
                    logger.info("ℹ️ Binary input was plain text, decoded successfully")
                except Exception as txt_err:
                    logger.error(f"❌ Failed to parse binary JD: {txt_err}")
                    return {"error": f"Invalid binary input: {txt_err}"}

        elif isinstance(jd_input, str) and os.path.exists(jd_input):
            if jd_input.endswith(".pdf"):
                reader = PdfReader(jd_input)
                jd_text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
                logger.info(f"✅ Extracted text from PDF file: {jd_input}")
            else:
                with open(jd_input, "r", encoding="utf-8", errors="ignore") as f:
                    jd_text = f.read()
                    logger.info(f"✅ Read text from TXT file: {jd_input}")
        elif isinstance(jd_input, str):
            jd_text = jd_input
            logger.info("📄 Received raw JD text input.")
        else:
            raise TypeError("Input must be bytes, a file path string, or a raw string.")

        logger.debug(f"🔍 JD text sent to LLM (truncated): {jd_text[:1000]}")

        response = jd_parsing_chain.invoke({"jd_text": jd_text})

        try:
            parsed_data = json.loads(response.content.strip())
            logger.info("✅ Successfully parsed JD JSON.")
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error from LLM: {e}")
            parsed_data = {"error": "Invalid JSON returned from model."}

        return parsed_data

    except Exception as e:
        logger.exception(f"❌ Unexpected error in parse_job_description: {e}")
        return {"error": str(e)}
