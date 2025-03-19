from langchain.prompts import PromptTemplate

resume_parsing_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template="""
    Extract the following information from the resume text below:
    - Name
    - Contact Information (email, phone, LinkedIn, etc.)
    - Skills (technical and soft skills)
    - Experience (job title, company, duration, responsibilities)
    - Education (degree, institution, graduation date)
    - Certifications
    - Projects (title, description, technologies used)
    - Languages (spoken or programming languages)

    Return the output in JSON format.

    Resume Text:
    {resume_text}
    """
)


job_matching_prompt = PromptTemplate(
    input_variables=["resume_data", "job_description"],
    template="""
    You are an AI assistant helping with recruitment. Match the following parsed resume data to the job description and provide a match score (0-100) along with a brief explanation:

    Resume Data: {resume_data}
    Job Description: {job_description}

    Output the match score and explanation in JSON format with keys 'score' and 'explanation'.
    """
)
