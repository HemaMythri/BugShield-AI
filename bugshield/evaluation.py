from bugshield.triage import triage_issue

CASES = [
    {"name":"Missing Python package","input":"ModuleNotFoundError: No module named 'requests'","language":"Auto-detect","category":"Dependency / import","expected_kb":"Python dependency missing"},
    {"name":"Python indentation","input":"IndentationError: expected an indented block after if statement","language":"Auto-detect","category":"Syntax","expected_kb":"Python indentation error"},
    {"name":"Java null pointer","input":"java.lang.NullPointerException at UserService.java:42","language":"Auto-detect","category":"Type / value","expected_kb":"Java NullPointerException"},
    {"name":"Invalid API key","input":"HTTP 401 Unauthorized: invalid API key","language":"Auto-detect","category":"Network / configuration","expected_kb":"API key or authentication error"},
    {"name":"SQL missing relation","input":"SQLSTATE: relation does not exist","language":"Auto-detect","category":"Database","expected_kb":"SQL relation or table not found"},
    {"name":"Python index error","input":"IndexError: list index out of range","language":"Auto-detect","category":"Runtime / logic","expected_kb":"Python index out of range"},
]

def run_benchmark(retriever):
    rows = []
    category_hits = 0
    retrieval_hits = 0
    for case in CASES:
        triage = triage_issue(case["input"], case["language"])
        cat_ok = triage["category"] == case["category"]
        category_hits += int(cat_ok)
        results = retriever.search(case["input"], top_k=3)
        titles = [r["title"] for r in results]
        ret_ok = case["expected_kb"] in titles
        retrieval_hits += int(ret_ok)
        rows.append({
            "case": case["name"],
            "expected category": case["category"],
            "predicted category": triage["category"],
            "triage correct": cat_ok,
            "expected knowledge": case["expected_kb"],
            "retrieval hit": ret_ok,
            "top retrieved": titles[0] if titles else "None",
        })
    n = len(CASES)
    return {
        "cases": n,
        "category_accuracy": category_hits / n,
        "retrieval_hit_rate": retrieval_hits / n,
        "details": rows,
    }
