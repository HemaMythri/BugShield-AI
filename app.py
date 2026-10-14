import json
import os
from pathlib import Path

import streamlit as st

from bugshield.pipeline import run_analysis
from bugshield.retrieval import KnowledgeRetriever
from bugshield.evaluation import run_benchmark

st.set_page_config(
    page_title="BugShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Keep credentials outside source code. Configure GROQ_API_KEY in
# .streamlit/secrets.toml locally and in the hosting provider's Secrets settings.
def get_api_key() -> str:
    try:
        secret_value = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        secret_value = ""
    return str(secret_value or os.getenv("GROQ_API_KEY", "")).strip()


def get_model_id() -> str:
    try:
        model_value = st.secrets.get("GROQ_MODEL", "openai/gpt-oss-120b")
    except Exception:
        model_value = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    return str(model_value or "openai/gpt-oss-120b").strip()


API_KEY = get_api_key()
MODEL_ID = get_model_id()
TOP_K = 4

st.markdown(
    """
    <style>
      :root { --navy: #12213a; --blue: #4f83e5; --pale: #f3f6fb; }
      .block-container { max-width: 1450px; padding-top: 1.4rem; padding-bottom: 2rem; }
      [data-testid="stSidebar"] { background: #f3f6fb; }
      .hero { background: linear-gradient(115deg,#101b30,#1b3558); color:#fff;
              padding:1.5rem 1.65rem; border-radius:18px; margin-bottom:1rem;
              border:1px solid #2a4265; }
      .hero h1 { color:#fff; margin:0 0 .35rem 0; font-size:2.25rem; }
      .hero p { color:#d3deed; margin:0; font-size:1rem; }
      .status { padding: .9rem 1rem; border-radius:12px; margin:.65rem 0; }
      .status-good { background:#dff3e9; color:#137548; }
      .status-warn { background:#fff3d4; color:#8b5a00; }
      .panel { border:1px solid #e0e6ef; border-radius:13px; padding:1rem;
               background:#fff; margin:.5rem 0; }
      .stage { border-left:4px solid #5685d8; background:#f5f8fe; padding:.8rem 1rem;
               margin:.55rem 0; border-radius:8px; }
      .small-muted { color:#68758a; font-size:.88rem; }
      div.stButton > button[kind="primary"] { border-radius:10px; min-height:2.8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_retriever():
    return KnowledgeRetriever()


# Sidebar: product-style status panel instead of a visible credential form.
with st.sidebar:
    st.markdown("## 🛡️ BugShield AI")
    st.caption("Debugging intelligence workspace")
    st.divider()
    st.markdown("### System Status")
    if API_KEY:
        st.markdown('<div class="status status-good">● AI service configured</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status status-warn">● Setup required</div>', unsafe_allow_html=True)
        st.caption("Configure the API key once in the app's local secrets file. It will not be requested in the interface.")
    st.markdown("**Knowledge Base:** Ready")
    st.markdown("**Evidence Review:** Enabled")
    st.divider()
    st.markdown("### Workflow Stages")
    st.caption("1. Triage  →  2. Retrieve  →  3. Diagnose  →  4. Review")
    st.divider()
    st.markdown("### Safety Guardrails")
    st.caption("• Submitted code is not executed.")
    st.caption("• Suggested fixes are hypotheses; review before applying.")
    st.caption("• Do not submit passwords, tokens, or private production data.")

st.markdown(
    """
    <div class="hero">
      <h1>🛡️ BugShield AI</h1>
      <p>AI-assisted debugging and root-cause analysis, grounded in troubleshooting evidence.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info("Describe an error to receive a structured diagnosis, related troubleshooting evidence, and a review of the proposed steps.")

if not API_KEY:
    with st.expander("One-time setup needed", expanded=True):
        st.markdown(
            """
            The interface is ready, but the AI service key has not been configured on this machine.

            **In VS Code:** create `.streamlit/secrets.toml` and add these two lines, replacing the placeholder with your own key:

            ```toml
            GROQ_API_KEY = "paste-your-key-here"
            GROQ_MODEL = "openai/gpt-oss-120b"
            ```

            Save the file and restart Streamlit. The secrets file is excluded from Git by `.gitignore`; never commit it.
            """
        )

tab_analyze, tab_eval, tab_about = st.tabs(["🔎 Analyze an issue", "🧪 Evaluation", "ℹ️ How it works"])

with tab_analyze:
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.subheader("Describe the bug")
        language = st.selectbox("Language / environment", ["Auto-detect", "Python", "Java", "JavaScript", "SQL", "Other"])
        title = st.text_input("Short title (optional)", placeholder="e.g., ImportError while starting app")
        bug_text = st.text_area(
            "Error message, traceback, or bug description",
            height=230,
            placeholder="What happened? What did you expect? Include the relevant error message...",
        )
        extra_context = st.text_area(
            "What have you tried? (optional)",
            height=90,
            placeholder="Environment, recent changes, attempted fixes...",
        )
        analyze = st.button(
            "🔍  Analyze Issue",
            type="primary",
            use_container_width=True,
            disabled=not bug_text.strip() or not API_KEY,
        )
        st.caption("Text analysis only — BugShield does not run or modify your code.")

    with right:
        st.subheader("Analysis pipeline")
        st.markdown('<div class="stage"><b>Stage 1 · Triage</b><br/>Identify the language, issue category, and likely severity.</div>', unsafe_allow_html=True)
        st.markdown('<div class="stage"><b>Stage 2 · Evidence retrieval</b><br/>Find similar symptoms in the troubleshooting knowledge base.</div>', unsafe_allow_html=True)
        st.markdown('<div class="stage"><b>Stage 3 · Root-cause analysis</b><br/>Generate likely causes and practical debugging steps.</div>', unsafe_allow_html=True)
        st.markdown('<div class="stage"><b>Stage 4 · Fix review</b><br/>Check evidence, uncertainty, and potentially risky recommendations.</div>', unsafe_allow_html=True)

    if analyze:
        with st.spinner("Analyzing issue: triage → retrieval → diagnosis → review..."):
            try:
                result = run_analysis(
                    bug_text=bug_text.strip(),
                    title=title.strip(),
                    language=language,
                    extra_context=extra_context.strip(),
                    api_key=API_KEY,
                    model=MODEL_ID,
                    retriever=get_retriever(),
                    top_k=TOP_K,
                )
                st.session_state["last_result"] = result
            except Exception as exc:
                st.error("The analysis could not be completed. Check the configured key, model availability, internet connection, and terminal logs.")
                with st.expander("Technical details"):
                    st.code(str(exc))

    result = st.session_state.get("last_result")
    if result:
        st.divider()
        st.subheader("Analysis report")
        triage = result["triage"]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Detected language", triage.get("language", "Unknown"))
        k2.metric("Issue category", triage.get("category", "Unknown"))
        k3.metric("Severity estimate", triage.get("severity", "Unknown"))
        k4.metric("Evidence passages", len(result["evidence"]))
        st.caption("Severity is a heuristic estimate based on the submitted text, not a formal incident rating.")
        st.markdown("### 🧠 Root-cause analysis")
        st.markdown(result["diagnosis"])
        st.markdown("### ✅ Reviewer notes")
        st.markdown(result["review"])
        st.markdown("### 📚 Retrieved evidence")
        if not result["evidence"]:
            st.warning("No relevant knowledge entries were retrieved. Treat the diagnosis as less grounded.")
        for i, item in enumerate(result["evidence"], start=1):
            with st.expander(f"{i}. {item.get('title', 'Knowledge entry')} · relevance {item.get('score', 0.0):.3f}"):
                if item.get("symptoms"):
                    st.markdown("**Symptoms**")
                    st.write(item["symptoms"])
                if item.get("cause"):
                    st.markdown("**Likely cause**")
                    st.write(item["cause"])
                if item.get("fix"):
                    st.markdown("**Suggested checks / fix**")
                    st.write(item["fix"])
                if item.get("tags"):
                    st.caption(f"Tags: {item['tags']}")
                st.caption(f"Knowledge source: {item.get('source', 'troubleshooting knowledge base')}")
        with st.expander("Technical pipeline details (JSON)"):
            st.code(json.dumps({
                "triage": result["triage"],
                "retrieved_items": [
                    {"title": e["title"], "source": e["source"], "score": e["score"]}
                    for e in result["evidence"]
                ],
                "review": result["review"],
            }, indent=2), language="json")

with tab_eval:
    st.subheader("Regression benchmark")
    st.write("Evaluate the built-in examples for triage category accuracy and knowledge retrieval. This benchmark does not establish that every generated diagnosis is correct.")
    if st.button("▶ Run benchmark", type="primary"):
        with st.spinner("Evaluating triage and retrieval..."):
            try:
                st.session_state["benchmark"] = run_benchmark(get_retriever())
            except Exception as exc:
                st.error("The benchmark could not be completed.")
                with st.expander("Technical details"):
                    st.code(str(exc))
    report = st.session_state.get("benchmark")
    if report:
        a, b, c = st.columns(3)
        a.metric("Triage category accuracy", f"{report['category_accuracy']:.0%}")
        b.metric("Retrieval hit rate", f"{report['retrieval_hit_rate']:.0%}")
        c.metric("Cases evaluated", report["cases"])
        st.dataframe(report["details"], use_container_width=True, hide_index=True)
        st.download_button("Download benchmark report", json.dumps(report, indent=2), file_name="bugshield_benchmark.json", mime="application/json")
        st.caption("Report these measured results honestly; the built-in test set is small.")

with tab_about:
    st.subheader("How BugShield works")
    st.code("""Bug report / traceback
        ↓
Stage 1: Rule-based triage + structured model output
        ↓
Stage 2: Semantic retrieval (Sentence Transformers + FAISS)
        ↓
Stage 3: Diagnosis grounded in retrieved knowledge
        ↓
Stage 4: Reviewer checks evidence, uncertainty, and risk
        ↓
Root-cause hypotheses + debugging steps + supporting evidence""", language="text")
    st.markdown("**Technology stack**")
    st.markdown("- Python and Streamlit for the interface\n- Hosted language model for diagnosis and review\n- Sentence Transformers and FAISS for semantic retrieval\n- Pytest for automated checks")
    st.markdown("**Important limitations**")
    st.markdown("- The app analyzes text; it does not execute submitted code.\n- Retrieved material supports a diagnosis but does not prove a fix is correct.\n- The reviewer is an additional model pass, not a formal safety guarantee.\n- The included knowledge base is intentionally small and should be expanded with verified material.")

st.divider()
st.caption("BugShield AI · Educational portfolio project · Verify every proposed fix before applying it.")
