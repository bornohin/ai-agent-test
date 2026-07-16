# Interview Questions & Answers: Job Application Screener Agent

This guide covers potential technical interview questions and answers, structured in order of priority from high-level concepts and tech stack decisions to deep technical troubleshooting.

---

## Part 1: High-Level Concepts & Tech Stack (Priority Group A)

### Q1: What is the Job Application Screener Agent and what does it do?
**Answer:**
It is an AI-powered automation tool designed to streamline candidate screening by evaluating how well a candidate's resume matches a specific Job Description (JD). 
It reads a candidate's resume (e.g., `resume.txt`) and a target JD, then sends them to the Google Gemini model using a structured prompt. The agent outputs:
1. A quantitative **Match Score (1-10)**.
2. A list of the **Top 3 Skill Gaps** between the candidate's experience and the JD.
3. A **Tailored Cover Letter Introduction** (max 150 words) that highlights matching strengths (specifically Python, GCP, Azure, and automation).

---

### Q2: What technology stack was selected for this project and why?
**Answer:**
- **Python**: Selected as the primary programming language due to its industry-standard status for AI development, fast prototyping capability, and extensive package ecosystem.
- **LangChain (`langchain` & `langchain-google-genai`)**: Used as the AI orchestration framework because it abstracts API interaction, cleanly separates message roles (System vs. Human), and makes switching LLM providers (e.g., from Anthropic to Gemini) minimal-effort.
- **Google Gemini (`gemini-2.5-flash`)**: Chosen as the LLM backend for its speed, low latency, strong reasoning capabilities, and ease of access via Google AI Studio.
- **python-dotenv**: Integrated to securely load configuration keys (`GEMINI_API_KEY`) from local `.env` files rather than hardcoding credentials.

---

## Part 2: Architecture & Design Principles (Priority Group B)

### Q3: Explain the architectural design of this project and why Separation of Concerns (SoC) was prioritized.
**Answer:**
The project is built on **Clean Architecture** principles to isolate presentation, logic, and configuration:
- **CLI/Presentation Layer (`src/main.py`)**: Handles command-line arguments, checks files, loads/overrides environments, and displays results.
- **Service/Agent Layer (`src/agent.py`)**: Manages the LLM connection, constructs prompt templates, and executes the call. It remains agnostic of how the JD was loaded (file vs. inline).
- **Data & Configuration Layer (`/data`, `/prompts`)**: Decouples the prompt instructions and the resume from Python code.

**Benefit:** This makes changes modular. We can migrate the interface from a CLI to a Web UI (like Streamlit or FastAPI) without modifying any core agent code in `src/agent.py`.

---

### Q4: Why is the system prompt configured externally in `system_prompt.md` rather than embedded in code?
**Answer:**
Prompt engineering is an iterative process. Storing the system prompt in [prompts/system_prompt.md](file:///Users/mdislam/Documents/META/ai_agent/prompts/system_prompt.md) instead of hardcoding it as a Python string offers key advantages:
1. **No Code Re-deployments**: The AI's behavior, instructions, and target output constraints can be adjusted dynamically without modifying or risking python code regressions.
2. **Readability**: Prompts can get long and require markdown layout formatting. Storing it as a `.md` file enables syntax highlighting and clean authoring.

---

## Part 3: Debugging & Troubleshooting (Priority Group C)

### Q5: What issue did you encounter with Google Cloud Application Default Credentials (ADC) and how was it solved?
**Answer:**
On systems with active Google Cloud SDK installations, the environment often exports credentials like `GOOGLE_APPLICATION_CREDENTIALS` or global configurations pointing to default GCP credentials.

When `ChatGoogleGenerativeAI` initialized, the underlying Google Auth SDK preferred GCP Service Account credentials (OAuth 2.0 Bearer tokens) over developer API keys. Because the developer Gemini endpoint expects an API key, sending it as an OAuth token caused a `401 ACCESS_TOKEN_TYPE_UNSUPPORTED` error.

**Solution:**
We programmatically isolated the Python process environment inside `src/agent.py` by clearing conflicting GCP variables before model instantiation:
```python
gcp_vars = ["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GCLOUD_PROJECT"]
for var in gcp_vars:
    os.environ.pop(var, None)
```
This forces the Google GenAI SDK to fall back and successfully use the developer `GOOGLE_API_KEY`.

---

### Q6: Why was it necessary to use `load_dotenv(override=True)` instead of default `load_dotenv()`?
**Answer:**
By default, `load_dotenv()` will *not* overwrite environment variables that are already defined in the active terminal shell. If a developer had previously run `export GEMINI_API_KEY=old_or_invalid_key` in their active terminal session, the default `load_dotenv()` would ignore the updated key in the `.env` file.

Using `override=True` ensures that the values defined in the project's local `.env` file always take precedence, preventing configuration conflicts in long-lived terminal sessions.

---

### Q7: How did you diagnose and resolve the premature truncation of the Gemini API output?
**Answer:**
Initially, the screening report was cutting off mid-sentence. 

**Diagnosis:**
1. Created a standalone test script (`test_gemini.py`) to bypass LangChain parameters and invoke the API raw.
2. Discovered that the truncation was happening due to specifying `max_output_tokens=1000` with the `ChatGoogleGenerativeAI` wrapper in this particular client version.

**Resolution:**
Removing the `max_output_tokens` parameter allowed the model to leverage its default maximum response context, printing the complete report.

---

### Q8: How was the macOS OpenSSL LibreSSL version mismatch resolved for `urllib3`?
**Answer:**
On macOS, Python environments running `urllib3` v2.x often throw a `NotOpenSSLWarning` because urllib3 v2 requires OpenSSL 1.1.1+, whereas the macOS system python is compiled against LibreSSL.

**Resolution:**
We pinned `urllib3<2.0.0` in `requirements.txt`. Version 1.x of `urllib3` does not enforce the OpenSSL 1.1.1+ check, eliminating the console warning while retaining full compatibility with LangChain and Google GenAI libraries.
