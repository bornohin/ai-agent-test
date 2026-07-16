# Job Application Screener Agent

An intelligent, AI-powered agent designed to evaluate job descriptions against a candidate's resume (Tom Islam). Built with Python, LangChain, and the Gemini API, the application calculates a match score, identifies critical skill gaps, and generates a tailored cover letter introduction.

## Project Structure

```text
├── data/
│   └── resume.txt          # Candidate resume (Tom Islam)
├── prompts/
│   └── system_prompt.md    # Instructions and role definition for Gemini
├── src/
│   ├── agent.py            # Core LangChain & Gemini integration logic
│   └── main.py             # CLI entrypoint, argument parsing, & env setup
├── .env.example            # Environment variables template
├── requirements.txt        # Project dependencies
└── README.md               # Setup and usage guide
```

---

## Getting Started

### 1. Prerequisites
- Python 3.9 or higher
- A Gemini API Key (Google AI Studio)

### 2. Installation
Clone or navigate to this directory, then set up a virtual environment and install the required dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Open `.env` in a text editor and replace the placeholder value with your real Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

---

## Usage

You can run the screener agent from your terminal. The CLI supports screening by passing a direct text string or reading from a text file containing the job description.

### Option A: Screen using a job description file (Recommended)
1. Save the job description to a text file (e.g., `jd.txt`).
2. Run the agent using the `--jd-file` or `-f` flag:
   ```bash
   python src/main.py --jd-file jd.txt
   ```

### Option B: Screen using an inline job description
Provide the job description directly in the command line using the `--jd` or `-j` flag:
```bash
python src/main.py --jd "We are looking for a Senior Software Engineer specializing in GCP, Python, and automated pipelines..."
```

### Advanced Options
You can inspect all CLI flags using the help command:
```bash
python src/main.py --help
```

Available arguments:
- `--jd` / `-j`: Inline job description text.
- `--jd-file` / `-f`: Path to a file containing the job description.
- `--resume` / `-r`: Custom path to a resume file (defaults to `data/resume.txt`).
- `--prompt` / `-p`: Custom path to the system prompt markdown file (defaults to `prompts/system_prompt.md`).
- `--model` / `-m`: Customize the Gemini model (defaults to `gemini-1.5-flash`).

---

## Clean Architecture Principles

This project utilizes a clean separation of concerns:
- **Presentation / CLI Layer (`src/main.py`)**: Responsible for reading command line input, loading environment variables, validating that credentials and paths are present, and displaying the evaluation report.
- **Service / Agent Layer (`src/agent.py`)**: Manages the orchestration logic, handles files (loading prompts and resumes), formats message structures, and handles Gemini API invocation.
- **Configuration & Knowledge Base (`/prompts`, `/data`)**: System prompts and static information (like the resume) are externalized, ensuring they can be updated independently without changing source code.
