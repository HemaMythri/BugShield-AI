from bugshield.triage import triage_issue

def test_missing_package():
    result = triage_issue("ModuleNotFoundError: No module named 'requests'")
    assert result["category"] == "Dependency / import"
    assert result["language"] == "Python"

def test_java_null_pointer():
    result = triage_issue("java.lang.NullPointerException at Service.java:10")
    assert result["category"] == "Type / value"
    assert result["language"] == "Java"

def test_api_key_error():
    result = triage_issue("HTTP 401 Unauthorized: invalid API key")
    assert result["category"] == "Network / configuration"

def test_high_severity_keyword():
    result = triage_issue("Production outage and data loss")
    assert result["severity"] == "High"
