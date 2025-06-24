import json
import os
import logging
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.config import CONFIG

load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
MODEL_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0))
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 2048))

log_file = os.path.join(os.path.dirname(__file__), "..", "logs", "matcher.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logger = logging.getLogger(__name__)

llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=MODEL_TEMPERATURE,
    max_tokens=MAX_TOKENS
)

match_prompt = PromptTemplate(
    input_variables=["resume_json", "jd_json"],
    template=CONFIG["prompts"]["match_prompt"]
)

chain = match_prompt | llm

def match_parsed_resume_to_job(resume_json, jd_json):
    try:
        logger.info("📩 Invoking LLM with resume and job description JSON.")
        logger.debug(f"Resume JSON: {json.dumps(resume_json)[:1000]}")
        logger.debug(f"JD JSON: {json.dumps(jd_json)[:1000]}")

        response = chain.invoke({
            "resume_json": json.dumps(resume_json),
            "jd_json": json.dumps(jd_json)
        })

        try:
            output = json.loads(response.content.strip())
            logger.info("✅ Successfully parsed LLM response.")
        except json.JSONDecodeError as je:
            logger.error(f"❌ Failed to parse JSON from LLM: {je}")
            return {
                "gpt_score": "N/A",
                "gpt_explanation": "Invalid JSON returned from model."
            }

        return {
            "gpt_score": output.get("gpt_score", "N/A"),
            "gpt_explanation": output.get("gpt_explanation", "No explanation provided.")
        }

    except Exception as e:
        logger.exception(f"❌ Exception during match_parsed_resume_to_job: {e}")
        return {
            "gpt_score": "N/A",
            "gpt_explanation": f"Error during matching: {str(e)}"
        }
