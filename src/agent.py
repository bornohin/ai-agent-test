import os
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

def read_file(file_path: Path) -> str:
    """Helper function to read text from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Required file not found at: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading file {file_path}: {str(e)}")

def screen_candidate(
    job_description: str,
    resume_path: str = "data/resume.txt",
    system_prompt_path: str = "prompts/system_prompt.md",
    model_name: str = "gemini-2.5-flash"
) -> str:
    """
    Screens a candidate's resume against a job description using the Gemini API.

    Args:
        job_description: The text of the job description to match against.
        resume_path: The file path to the candidate's resume.
        system_prompt_path: The file path to the system prompt instructions.
        model_name: The Gemini model identifier to use.

    Returns:
        The markdown assessment string from Gemini.
    """
    # Define absolute or relative paths
    base_dir = Path(__file__).resolve().parent.parent
    abs_resume_path = base_dir / resume_path
    abs_prompt_path = base_dir / system_prompt_path

    # Read system prompt and resume content
    system_prompt_content = read_file(abs_prompt_path)
    resume_content = read_file(abs_resume_path)

    # Ensure API Key is mapped correctly for LangChain Google GenAI client
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    # Initialize the ChatGoogleGenerativeAI model
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
        max_output_tokens=1000
    )

    # Structure messages
    messages = [
        SystemMessage(content=system_prompt_content),
        HumanMessage(content=f"Please analyze this job description against the candidate resume.\n\n"
                             f"### JOB DESCRIPTION:\n{job_description}\n\n"
                             f"### CANDIDATE RESUME:\n{resume_content}")
    ]

    # Call the API
    response = llm.invoke(messages)
    
    return str(response.content)
