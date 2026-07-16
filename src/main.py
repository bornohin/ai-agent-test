import warnings
# Suppress deprecation and version warnings from dependencies to keep CLI output clean
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*OpenSSL.*")
warnings.filterwarnings("ignore", message=".*LibreSSL.*")

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Import agent logic
from agent import screen_candidate

def setup_environment():
    """Loads environment variables and validates configuration."""
    # Look for .env file in the project root directory
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / ".env"
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        # Load from system environment/default search path
        load_dotenv()

    # Validate that GEMINI_API_KEY or GOOGLE_API_KEY is available
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        print("Error: Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set.", file=sys.stderr)
        print("Please create a '.env' file in the project root with your API key, like so:", file=sys.stderr)
        print("   GEMINI_API_KEY=your-gemini-api-key-here", file=sys.stderr)
        sys.exit(1)

def main():
    setup_environment()

    parser = argparse.ArgumentParser(
        description="Job Application Screener Agent - Analyze resumes against JDs using Gemini."
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--jd", "-j",
        type=str,
        help="The inline job description text to screen against."
    )
    group.add_argument(
        "--jd-file", "-f",
        type=str,
        help="Path to a text file containing the job description."
    )
    
    parser.add_argument(
        "--resume", "-r",
        type=str,
        default="data/resume.txt",
        help="Path to the resume file (default: data/resume.txt)"
    )
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        default="prompts/system_prompt.md",
        help="Path to the system prompt file (default: prompts/system_prompt.md)"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="gemini-2.5-flash",
        help="Gemini model to use (default: gemini-2.5-flash)"
    )

    args = parser.parse_args()

    # Determine job description text
    if args.jd_file:
        jd_path = Path(args.jd_file)
        if not jd_path.exists():
            print(f"Error: Job description file not found at: {jd_path}", file=sys.stderr)
            sys.exit(1)
        try:
            with open(jd_path, "r", encoding="utf-8") as file:
                job_description = file.read()
        except Exception as e:
            print(f"Error reading job description file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        job_description = args.jd

    if not job_description.strip():
        print("Error: The job description cannot be empty.", file=sys.stderr)
        sys.exit(1)

    print("Analyzing candidate match with Gemini...")
    
    try:
        assessment = screen_candidate(
            job_description=job_description,
            resume_path=args.resume,
            system_prompt_path=args.prompt,
            model_name=args.model
        )
        print("\n--- SCREENING REPORT ---")
        print(assessment)
        print("------------------------")
    except Exception as e:
        print(f"An error occurred during screening: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
