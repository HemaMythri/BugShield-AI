import re

def triage_issue(text: str, selected_language: str = "Auto-detect") -> dict:
    """Deterministic first-pass triage; intentionally transparent and testable."""
    t = text.lower()
    if selected_language != "Auto-detect":
        language = selected_language
    elif "traceback (most recent call last)" in t or "modulenotfounderror" in t or "indentationerror" in t or "typeerror:" in t:
        language = "Python"
    elif "exception in thread" in t or "java.lang." in t or "nullpointerexception" in t or "cannot find symbol" in t:
        language = "Java"
    elif "uncaught typeerror" in t or "undefined is not" in t or "referenceerror:" in t:
        language = "JavaScript"
    elif "ora-" in t or "syntax error at or near" in t or "sqlstate" in t:
        language = "SQL"
    else:
        language = "Unknown"

    rules = [
        ("Dependency / import", ["modulenotfounderror", "no module named", "cannot find module", "importerror", "package does not exist"]),
        ("Type / value", ["typeerror", "valueerror", "cannot read properties", "undefined is not", "nullpointerexception"]),
        ("Syntax", ["syntaxerror", "syntax error", "indentationerror", "expected ':'", "unexpected token"]),
        ("Database", ["ora-", "sqlstate", "connection refused", "database is locked", "relation does not exist"]),
        ("Network / configuration", ["timeout", "connection refused", "401 unauthorized", "403 forbidden", "invalid api key", "model_not_found"]),
        ("Runtime / logic", ["indexerror", "keyerror", "assertionerror", "runtimeerror", "out of range"]),
    ]
    category = "General debugging"
    for label, needles in rules:
        if any(n in t for n in needles):
            category = label
            break

    severe_terms = ["data loss", "production outage", "security breach", "credential leak", "corruption"]
    if any(x in t for x in severe_terms):
        severity = "High"
    elif any(x in t for x in ["crash", "fatal", "cannot start", "unhandled exception", "production"]):
        severity = "Medium"
    else:
        severity = "Low / Unknown"

    return {
        "language": language,
        "category": category,
        "severity": severity,
        "symptom_terms": _extract_terms(t),
    }

def _extract_terms(text: str):
    candidates = [
        "modulenotfounderror", "importerror", "typeerror", "valueerror", "syntaxerror",
        "indentationerror", "nullpointerexception", "cannot find symbol", "ora-",
        "connection refused", "timeout", "invalid api key", "model_not_found",
        "indexerror", "keyerror", "assertionerror",
    ]
    found = [term for term in candidates if term in text]
    return found[:6]
