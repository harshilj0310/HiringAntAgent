from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

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

def match_parsed_resume_to_job(resume_json, jd_json):
    import json

    try:
        response = chain.invoke({
            "resume_json": json.dumps(resume_json),
            "jd_json": json.dumps(jd_json)
        })

        output = json.loads(response.content.strip())
        return {
            "gpt_score": output.get("gpt_score", "N/A"),
            "gpt_explanation": output.get("gpt_explanation", "No explanation provided.")
        }
    except Exception as e:
        return {
            "gpt_score": "N/A",
            "gpt_explanation": f"Error during matching: {str(e)}"
        }
