---
title: "Failure 5: Silent tool failure"
permalink: /failures/05-silent-tool-failure/
---

# Failure 5: Silent tool failure

*The dashboard returned a 500. The agent summarized the error page and called it a sales report.*

## The scenario

An internal service has a bad moment: HTTP 500, a timeout, an empty body. Your agent fetches the quarterly sales report from it. Nobody checks the status code. The error page goes into the context window as if it were the report, the model does its best with what it was handed, and the user gets a fluent, confident summary built on nothing. The process exits with code 0. Your monitoring shows success.

Nobody finds out until someone makes a decision from the numbers.

The code is in [`05-silent-tool-failure`](https://github.com/MenokoOG/agent-autopsy/tree/main/05-silent-tool-failure).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/05-silent-tool-failure/broken.py):

```python
def fetch_url(url):
    return {"status": 500, "body": "<html>500 Internal Server Error</html>"}

...

def run_agent(task, model=MODEL, fetch=fetch_url):
    response = fetch(REPORT_URL)

    messages = [{"role": "user",
                 "content": f"{task}\n\nReport contents:\n{response['body']}"}]
    summary = model(messages)
    return {"ok": True, "summary": summary}  # "ok", nothing was ok
```

The function reads `response['body']` and never reads `response['status']`. It then returns `"ok": True` unconditionally. Here's the output:

```text
ok=True
Q3 sales look steady overall. The report highlights internal server performance as a key operational theme this quarter.
```

The model did what models do. It treated the text as a report and produced a summary that sounds like one. It even found a "theme" in the error page. From the outside, that output looks the same as a good run. That's what makes this failure expensive: there's no crash, no log line and no visible difference.

## Why it happens

Two habits cause it.

The first is treating a tool call like a function call in a language with exceptions. In your own code, a failed function throws. A web request doesn't. It returns a response object that says it failed, and you have to look.

The second is the context window itself. Anything you put in the prompt becomes "data" to the model. The model has no way to know the text came from a failed request. It can only work with what it sees. If you hand it garbage, it produces fluent garbage.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/05-silent-tool-failure/fixed.py) puts a check at the boundary where tool results enter the system:

```python
class ToolFailure(Exception):
    """A tool returned an error. The agent must not pretend otherwise."""


def checked_fetch(url, fetch=fetch_url):
    response = fetch(url)
    if response["status"] != 200:
        raise ToolFailure(f"fetch_url({url!r}) returned HTTP {response['status']}")
    return response["body"]


def run_agent(task, model=MODEL, fetch=fetch_url):
    try:
        body = checked_fetch(REPORT_URL, fetch=fetch)
    except ToolFailure as failure:
        return {"ok": False, "summary": None, "error": str(failure)}

    messages = [{"role": "user", "content": f"{task}\n\nReport contents:\n{body}"}]
    return {"ok": True, "summary": model(messages), "error": None}
```

The pattern is small:

1. A wrapper, `checked_fetch`, is the only way the agent reaches the tool.
2. The wrapper turns a bad status into an exception, `ToolFailure`.
3. The agent catches it and returns `ok: False` with the error message and no summary.

Run it:

```text
AGENT HALTED: fetch_url('https://dashboard.internal/reports/q3-sales') returned HTTP 500
```

That line is worse to look at than the confident summary. It's also true.

The key design choice is where the check lives. It sits at the tool boundary, before anything reaches the prompt. Once an error page is in the context, it's too late. You'd be asking the model to notice that its own input is garbage, and it won't reliably do that.

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/05-silent-tool-failure/tests/test_fixed.py):

- `test_fixed_surfaces_tool_failure` checks a 500 produces `ok: False` and an error naming the status.
- `test_fixed_checked_fetch_raises` tests the wrapper on its own.
- `test_fixed_still_works_when_tool_is_healthy` guards the happy path.
- `test_broken_reports_success_on_garbage` keeps the original lie on record.

## Where the fix stops

- **Only a 500 is covered here.** The check is `status != 200`. Real services fail in more ways. A 200 can carry an error body, like a JSON `{"error": ...}`, or an HTML login page, or an empty string. Validate the shape of the result, not only the status code.
- **Redirects and other 2xx codes.** A 204 or a 206 is a success that this check would reject. Decide per tool what "good" means and write it down.
- **No retry.** A transient 500 might succeed on the second try. The fix reports the failure and stops. Add a bounded retry with backoff if the tool is flaky, and apply the lesson from [failure 1]({{ '/failures/01-runaway-loop/' | relative_url }}) to the retry count.
- **The caller must handle `ok: False`.** The fix only helps if the code that calls the agent reads the flag. A caller that ignores `ok` and prints `summary` has rebuilt the bug one level up.
- **Monitor the failure.** `ok: False` should raise an alert or increment a metric. A visible error that nobody sees is only a quieter silent failure.

## The takeaway

Check every tool result at the boundary, before it touches the context window. A failed tool is a failed step. Surface it, and never summarize it.

---

[&larr; Previous: Failure 4]({{ '/failures/04-tool-hallucination/' | relative_url }}) · [Next: Failure 6, wrong tool pick &rarr;]({{ '/failures/06-wrong-tool-pick/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
