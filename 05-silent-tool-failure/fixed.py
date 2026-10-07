"""Failure #5 — Silent Tool Failure (FIXED).

One rule: check the tool result before it touches the context window.
A failed tool is a failed step — surface it, don't summarize it.

Run: python fixed.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os

TASK = "Summarize this quarter's sales report from the internal dashboard."
REPORT_URL = "https://dashboard.internal/reports/q3-sales"


class ToolFailure(Exception):
    """A tool returned an error. The agent must not pretend otherwise."""


def fetch_url(url):
    return {"status": 500, "body": "<html>500 Internal Server Error</html>"}


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    return "Q3 sales grew 8% quarter-over-quarter, led by the west region."


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def checked_fetch(url, fetch=fetch_url):
    # THE FIX: validate at the tool boundary. Errors become exceptions,
    # not context. This is the only diff that matters in this lesson.
    response = fetch(url)
    if response["status"] != 200:
        raise ToolFailure(f"fetch_url({url!r}) returned HTTP {response['status']}")
    return response["body"]


def run_agent(task, model=MODEL, fetch=fetch_url):
    try:
        body = checked_fetch(REPORT_URL, fetch=fetch)
    except ToolFailure as failure:
        # Fail loud and honest. A visible error beats an invisible lie.
        return {"ok": False, "summary": None, "error": str(failure)}

    messages = [{"role": "user", "content": f"{task}\n\nReport contents:\n{body}"}]
    return {"ok": True, "summary": model(messages), "error": None}


if __name__ == "__main__":
    result = run_agent(TASK)
    if result["ok"]:
        print(result["summary"])
    else:
        print(f"AGENT HALTED: {result['error']}")
