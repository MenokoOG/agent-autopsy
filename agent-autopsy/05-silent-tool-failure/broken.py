"""Failure #5 — Silent Tool Failure (BROKEN).

The fetch tool returns an HTTP 500. The agent stuffs the error page into
context like it's data, the model gamely summarizes garbage, and the user
gets a confident answer built on nothing. Exit code 0. Nobody notices.

Run: python broken.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os

TASK = "Summarize this quarter's sales report from the internal dashboard."
REPORT_URL = "https://dashboard.internal/reports/q3-sales"


def fetch_url(url):
    # Simulates the flaky internal service. In prod this is a real request
    # that fails at the worst possible time.
    return {"status": 500, "body": "<html>500 Internal Server Error</html>"}


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    # Models do their best with whatever you hand them — including garbage.
    return ("Q3 sales look steady overall. The report highlights internal "
            "server performance as a key operational theme this quarter.")


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def run_agent(task, model=MODEL, fetch=fetch_url):
    response = fetch(REPORT_URL)

    # THE BUG: the status code is never checked. The error page goes into
    # context as if it were the report, and the model summarizes it.
    messages = [{"role": "user",
                 "content": f"{task}\n\nReport contents:\n{response['body']}"}]
    summary = model(messages)
    return {"ok": True, "summary": summary}  # "ok" — nothing was ok


if __name__ == "__main__":
    result = run_agent(TASK)
    print(f"ok={result['ok']}\n{result['summary']}")
