import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv


# Load API key from .env
load_dotenv()


# Initialize GPT model (LangChain)
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Define a prompt template for GPT-based matching
matching_prompt = PromptTemplate(
    input_variables=["resume_data", "job_description"],
    template="""
    You are an AI assistant helping with recruitment. Match the following parsed resume data to the job description and provide a match score (0-100) along with a brief explanation:

    Resume Data: {resume_data}
    Job Description: {job_description}

    Output the match score and explanation in JSON format with keys 'score' and 'explanation'.
    """
)

# Create a LangChain chain for GPT-based matching
matching_chain = matching_prompt | llm


# Combined function to match parsed resume JSON to job description
def match_parsed_resume_to_job(resume_json_path, job_description):
    # Step 1: Load parsed resume JSON file
    with open(resume_json_path, "r", encoding="utf-8") as file:
        resume_text = file.read()

    # Step 2: Use GPT-based matching logic
    gpt_response = matching_chain.invoke({"resume_data": resume_text, "job_description": job_description})
    
    try:
        gpt_result = json.loads(gpt_response.content)
        gpt_score = gpt_result.get("score", 0)
        gpt_explanation = gpt_result.get("explanation", "No explanation provided.")
    except json.JSONDecodeError:
        gpt_score = 0
        gpt_explanation = "Failed to parse GPT response."



    # Step 4: Combine results into a final output
    final_result = {
        "gpt_score": gpt_score,
        "gpt_explanation": gpt_explanation,
    }

    return final_result






# Example usage (for testing purposes)
if __name__ == "__main__":
    test_resume_path = "C:\\Users\\hp\\hiring-agent\\HiringAntAgent\\data\\processed\\resume.json"
    test_job_description = "Looking for a GENAI Engineer with expertise in Python, Langchain, and  (AWS preferred)."
    result = match_parsed_resume_to_job(test_resume_path, test_job_description)
    print(json.dumps(result, indent=4))
