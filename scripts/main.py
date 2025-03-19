import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from HiringAntAgent.tools.parse_resume import resume_parsing_tool
from HiringAntAgent.tools.job_matching import job_matching_tool

# Load environment variables
load_dotenv()



# Initialize LLM (Agent's brain)
llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

# Define available tools for the agent
tools = [resume_parsing_tool, job_matching_tool]

# Initialize Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description", 
    verbose=True
)

# Function to interact with the agent
def run_agent(query):
    return agent.run(query)

if __name__ == "__main__":
    user_input = "Extract information from this resume: John Doe, Software Engineer, Python, 5 years experience"
    response = run_agent(user_input)
    print(response)
