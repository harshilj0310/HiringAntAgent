import json
import os
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv

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
# You must create a .env file with:
# OPENAI_API_KEY=your_openai_api_key_here
load_dotenv()

# ============================================
# ✅ Prompt Template for Job Description Parsing
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
    - "job_type": (Full-time, Part-time, Contract, etc.)
    - "education_required": (string)
    - "responsibilities": (list of key responsibilities)

    Job Description:
    {jd_text}

    JSON Output:
    """
)

# ✅ Initialize the LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)
jd_parsing_chain = jd_parsing_prompt | llm

# ============================================
# ✅ JD Parsing Function
# ============================================
def parse_job_description(jd_input):
    jd_text = ""
    file_obj = None

    try:
        # If the input is a file path
        if isinstance(jd_input, str) and os.path.exists(jd_input):
            if jd_input.endswith(".pdf"):
                try:
                    reader = PdfReader(jd_input)
                    jd_text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
                    logging.info(f"✅ Extracted text from PDF: {jd_input}")
                except Exception as e:
                    logging.error(f"❌ Error reading PDF file: {jd_input} - {e}")
                    return {"error": str(e)}
            else:  # assume .txt
                try:
                    file_obj = open(jd_input, "r", encoding="utf-8", errors="ignore")
                    jd_text = file_obj.read()
                    logging.info(f"✅ Read text from file: {jd_input}")
                except Exception as e:
                    logging.error(f"❌ Error reading text file: {jd_input} - {e}")
                    return {"error": str(e)}
                finally:
                    if file_obj:
                        file_obj.close()
        else:
            # assume it's raw text
            jd_text = jd_input
            logging.info(f"📄 Received raw JD text input.")

        # Send to LLM
        response = jd_parsing_chain.invoke({"jd_text": jd_text})

        try:
            parsed_data = json.loads(response.content.strip())
            logging.info("✅ Successfully parsed JD JSON.")
        except json.JSONDecodeError as e:
            logging.error(f"❌ JSON parsing error from LLM response: {e}")
            parsed_data = {"error": "Invalid JSON returned from model"}

        return parsed_data

    except Exception as e:
        logging.exception(f"❌ Unexpected error in parse_job_description: {e}")
        return {"error": str(e)}

# # ============================================
# # ✅ Demo Run
# # ============================================
# if __name__ == "__main__":
#     sample_jd = """
#     We are hiring a Data Scientist with 3+ years of experience in Python, NLP, and Machine Learning.
#     Responsibilities include building predictive models and analyzing large datasets.
#     Preferred skills: Experience with cloud platforms like AWS, Azure, or GCP.
#     Location: Mumbai, India.
#     Job Type: Full-time
#     Education: B.Tech or higher in CS or related field
#     """
#     result = parse_job_description(sample_jd)
#     print(json.dumps(result, indent=2, ensure_ascii=False))
