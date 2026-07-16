# Interview Questions & Answers: Job Application Screener Agent

This guide covers potential technical interview questions and answers based on the architecture, technologies, and debug workflows used in this project.

---

### Q1: Explain the architectural design of this project and why Separation of Concerns (SoC) was prioritized.
**Answer:**
The project is built on **Clean Architecture** principles to separate presentation, business logic, and configuration:
- **CLI/Presentation Layer (`src/main.py`)**: Responsible solely for user interaction, command-line argument parsing, and environment setup/validation.
- **Service/Agent Layer (`src/agent.py`)**: Handles the business logic of loading files (prompts and resumes) and invoking the LLM client. It doesn't care how the job description was acquired (whether from a file or inline string).
- **Data & Configuration Layer (`/data`, `/prompts`)**: Stores system prompts and candidate profiles as static files.

**Benefit:** This isolation makes unit testing and maintenance straightforward. For example, we can switch from a CLI to a Web UI (FastAPI/Streamlit) without changing any of the agent logic in `src/agent.py`. Similarly, we can modify the system instructions in `system_prompt.md` without modifying Python code.

---

### Q2: What issue did you encounter with Google Cloud Application Default Credentials (ADC) and how was it solved?
**Answer:**
On systems where developers have local Google Cloud SDK configurations active, the environment often contains variables like `GOOGLE_APPLICATION_CREDENTIALS` or global configurations pointing to default GCP credentials.

When `ChatGoogleGenerativeAI` initializes, the underlying Google Auth SDK prefers GCP Service Account credentials (OAuth 2.0 Bearer tokens) over developer API keys. If the endpoint (`generativelanguage.googleapis.com`) expects an API key but receives a GCP OAuth token, it rejects the request with a `401 ACCESS_TOKEN_TYPE_UNSUPPORTED` error.

**Solution:**
We programmatically isolated the Python process context by stripping out conflicting GCP variables:
```python
gcp_vars = ["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GCLOUD_PROJECT"]
for var in gcp_vars:
    os.environ.pop(var, None)
```
This forces the Google GenAI library to fallback and exclusively use the developer `GOOGLE_API_KEY` provided in the `.env` file.

---

### Q3: Why is `load_dotenv(override=True)` used instead of the default `load_dotenv()`?
**Answer:**
By default, `load_dotenv()` will *not* overwrite environment variables that are already defined in the active terminal shell. If a developer had previously run `export GEMINI_API_KEY=old_or_invalid_key` in their terminal session, the default `load_dotenv()` would ignore the updated key in the `.env` file.

Using `override=True` ensures that the values defined in the project's local `.env` file always take precedence, preventing silent overrides and configuration sync issues in long-lived terminal sessions.

---

### Q4: How did you diagnose and resolve the premature truncation of the Gemini API output?
**Answer:**
Initially, the screening report was cutting off mid-sentence. 

**Diagnosis:**
1. Created a standalone test script (`test_gemini.py`) to bypass LangChain parameters and invoke the API raw.
2. Discovered that the truncation was happening due to specifying `max_output_tokens=1000` with the `ChatGoogleGenerativeAI` wrapper in this particular client version.

**Resolution:**
Removing the `max_output_tokens` parameter allowed the model to leverage its default maximum response context, printing the complete report.

---

### Q5: How was the macOS OpenSSL LibreSSL version mismatch resolved for `urllib3`?
**Answer:**
On macOS, Python environments running `urllib3` v2.x often throw a `NotOpenSSLWarning` because urllib3 v2 requires OpenSSL 1.1.1+, whereas the macOS system python is compiled against LibreSSL.

**Resolution:**
We pinned `urllib3<2.0.0` in `requirements.txt`. Version 1.x of `urllib3` does not enforce the OpenSSL 1.1.1+ check, eliminating the console warning while retaining full compatibility with LangChain and Google GenAI libraries.
