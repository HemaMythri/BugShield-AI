# BugShield AI — Debugging & Root-Cause Analysis

BugShield AI is a portfolio project that analyzes error messages and bug reports through a staged workflow: triage, retrieval, diagnosis, and review. It uses retrieval-augmented generation (RAG) to ground suggestions in a small curated troubleshooting knowledge base.

## Features

- Streamlit dashboard for tracebacks and bug descriptions.
- Transparent rule-based triage with language, category, and heuristic severity.
- Semantic retrieval with Sentence Transformers and FAISS.
- Groq-hosted LLM for structured triage, diagnosis, and independent review.
- Evidence cards with relevance scores and source labels.
- Small deterministic evaluation benchmark for triage category accuracy and retrieval hit rate.
- Automated unit tests for the triage rules.
- No user code execution.

## Architecture

```text
Bug report / traceback
        |
        v
Stage 1: Triage (deterministic rules + LLM structured summary)
        |
        v
Stage 2: RAG retrieval (Sentence Transformers embeddings + FAISS)
        |
        v
Stage 3: Diagnosis (LLM receives issue + retrieved knowledge)
        |
        v
Stage 4: Review (LLM critiques evidence, uncertainty, and risky advice)
        |
        v
Root-cause hypotheses + debugging checklist + source evidence
```

These are distinct pipeline stages, not a claim that autonomous agents independently plan and execute tasks. The reviewer is a second model call and is not a formal safety guarantee.

## Technology stack

- Python
- Streamlit
- Groq API
- Sentence Transformers (`all-MiniLM-L6-v2`)
- FAISS and NumPy
- pytest

## Setup on Windows

Python 3.11 or 3.12 is recommended.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Open the local URL shown by Streamlit, usually `http://localhost:8501`. The first run downloads the embedding model and needs an internet connection.

## Configure the LLM

1. Create a Groq API key in your provider account.
2. Run the app and paste the key into the password field in the sidebar.
3. Keep the key out of source code, screenshots, and GitHub.
4. If the selected model is unavailable to your account, choose a currently supported model ID from the provider's model documentation.

## Demo inputs

Try these one at a time:

**Python missing dependency**
```text
Traceback (most recent call last):
  File "app.py", line 1, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

**Java null pointer**
```text
java.lang.NullPointerException: Cannot invoke "User.getName()" because "user" is null
    at UserService.getDisplayName(UserService.java:42)
```

**Invalid API key**
```text
HTTP 401 Unauthorized: invalid API key
```

**SQL table issue**
```text
SQLSTATE: relation "orders" does not exist
```

Ask the reviewer to distinguish known evidence from hypotheses. Do not apply suggested fixes without verifying them in your own environment.

## Evaluation

Run the benchmark from the Evaluation tab. It reports:
- Triage category accuracy across the included cases.
- Retrieval hit rate: whether the expected knowledge entry appears in the top three results.
- A per-case table and downloadable JSON report.

These metrics only describe the small built-in test set. They do not measure the correctness of the generated diagnosis. Add more representative test cases before making broader performance claims.

Run unit tests:

```powershell
python -m pytest -q
```

## Deploy to Streamlit Community Cloud

1. Push the repository to GitHub.
2. Open Streamlit Community Cloud and choose **Create app**.
3. Select your repository, branch, and `app.py` as the entrypoint.
4. Choose a supported Python version consistent with local testing.
5. Deploy and inspect the logs if dependency installation fails.
6. Enter your Groq key in the app sidebar when using the public demo.

The embedding model download and FAISS dependency can make the first startup slower. Test the cloud deployment with a small issue before sharing it.

## Limitations and next steps

- The knowledge base is small and manually curated.
- The triage severity is a keyword heuristic, not a calibrated risk score.
- Similarity scores are not probabilities and do not prove that a retrieved entry is correct.
- LLM output can hallucinate; the reviewer can also miss errors.
- No source code is executed or automatically patched.
- Next steps: expand verified knowledge, add language-specific test suites, track expert-rated diagnosis quality, and optionally add a sandboxed test-runner in a future version.

## Security

Do not paste credentials, private source code, personal data, or production logs into a public demo. Never commit API keys or secrets. Rotate any key exposed in a screenshot, chat, or repository.
