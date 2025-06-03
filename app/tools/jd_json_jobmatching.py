import json
import os
import logging
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# ============================================
# ✅ Setup Logging
# ============================================
log_file = os.path.join(os.path.dirname(__file__), "..", "logs", "matcher.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ============================================
# ✅ Load .env file (ensure it contains your OpenAI API key)
# ============================================
# .env content should include:
# OPENAI_API_KEY=your_openai_api_key_here
load_dotenv()

# ============================================
# ✅ Define Prompt and LLM
# ============================================
llm = ChatOpenAI(model="gpt-4", temperature=0)

match_prompt = PromptTemplate(
    input_variables=["resume_json", "jd_json"],
    template="""
You are a hiring assistant. Based on the following Job Description and Resume (both in JSON), evaluate how well the candidate fits the job.

Job Description:
{jd_json}

Resume:
{resume_json}

Respond ONLY in JSON format with:
- gpt_score: integer score from 0 to 100 indicating match quality.
- gpt_explanation: short explanation (2-3 lines) for the score.

JSON Output:
"""
)

chain = match_prompt | llm

# ============================================
# ✅ Matching Function
# ============================================
def match_parsed_resume_to_job(resume_json, jd_json):
    try:
        logging.info("📩 Invoking LLM with resume and job description JSON.")

        response = chain.invoke({
            "resume_json": json.dumps(resume_json),
            "jd_json": json.dumps(jd_json)
        })

        try:
            output = json.loads(response.content.strip())
            logging.info("✅ Successfully parsed LLM response.")
        except json.JSONDecodeError as je:
            logging.error(f"❌ Failed to parse JSON from LLM: {je}")
            return {
                "gpt_score": "N/A",
                "gpt_explanation": "Invalid JSON returned from model."
            }

        return {
            "gpt_score": output.get("gpt_score", "N/A"),
            "gpt_explanation": output.get("gpt_explanation", "No explanation provided.")
        }

    except Exception as e:
        logging.exception(f"❌ Exception during match_parsed_resume_to_job: {e}")
        return {
            "gpt_score": "N/A",
            "gpt_explanation": f"Error during matching: {str(e)}"
        }
