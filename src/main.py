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

    # Validate that ANTHROPIC_API_KEY is available
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        print("Please create a '.env' file in the project root with your API key, like so:", file=sys.stderr)
        print("   ANTHROPIC_API_KEY=your-api-key-here", file=sys.stderr)
        sys.exit(1)

def main():
    setup_environment()

    parser = argparse.ArgumentParser(
        description="Job Application Screener Agent - Analyze resumes against JDs using Claude."
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
        default="claude-3-5-sonnet-20240620",
        help="Claude model to use (default: claude-3-5-sonnet-20240620)"
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

    print("Analyzing candidate match with Claude...")
    
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
