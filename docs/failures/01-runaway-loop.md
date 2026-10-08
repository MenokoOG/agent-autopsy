---
title: "Failure 1: The runaway loop"
permalink: /failures/01-runaway-loop/
---

# Failure 1: The runaway loop

*An agent calls itself forever, and the first sign is the bill.*

## The scenario

You ship an agent that decides when it's finished. In testing it takes three passes and says DONE. In production an edge case shows up: the model keeps "improving" its draft and never says the word. Nothing outside the model is watching, so the loop keeps going until your rate limit or your wallet trips.

The code for this lesson is in [`01-runaway-loop`](https://github.com/MenokoOG/agent-autopsy/tree/main/01-runaway-loop).

## The bug

Here's the loop from [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/01-runaway-loop/broken.py):

```python
while True:
    reply = model(messages)
    tokens_burned += len(reply.split()) * 2  # rough cost proxy
    print(f"step={len(messages) // 2 + 1}  tokens~{tokens_burned}  {reply[:60]}")
    messages.append({"role": "assistant", "content": reply})
    messages.append({"role": "user", "content": "Continue. Reply DONE when finished."})

    if "DONE" in reply:  # the model never says it
        return reply
```
{: data-hl="1,8"}

Look at what can end this loop. One thing: the string `DONE` appearing in the model's reply. The code counts tokens, and it prints them, but nothing reads that number to make a decision. The counter is a speedometer on a car with no brakes.

The mock model in the repo reproduces the production edge case. It answers `Draft 1: still refining the summary, one more pass...`, then `Draft 2`, and so on. Run it and you'll see the step counter climb until you press Ctrl+C:

```text
WARNING: no stop guard. Ctrl+C to escape.

step=1  tokens~18  Draft 1: still refining the summary, one more pass...
step=2  tokens~36  Draft 2: still refining the summary, one more pass...
```

The cost proxy is crude. It charges two "tokens" per word of the reply and ignores the growing message history. Real usage climbs faster, because every call re-sends the whole conversation. A loop that costs a little per step early costs more per step later.

## Why it happens

The loop gives the model two jobs at once: do the work, and decide the work is over. Models are good at the first job. The second job depends on a phrase appearing in free-form text, and a model has plenty of reasons not to emit it. It may want one more pass. It may phrase the ending differently. It may hit an instruction conflict. You can't enumerate those reasons in advance, so you can't prevent them with a better prompt.

The principle is old and applies to any loop: the thing being supervised can't be the only thing supervising.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/01-runaway-loop/fixed.py) adds three limits the model can't override:

```python
MAX_STEPS = 10          # hard iteration cap
TOKEN_BUDGET = 4_000    # rough token ceiling
TIMEOUT_SECONDS = 60    # wall-clock kill switch
```

And the loop becomes a bounded `for`:

```python
for step in range(1, max_steps + 1):
    reply = model(messages)
    tokens_burned += len(reply.split()) * 2
    log.append({"step": step, "tokens": tokens_burned, "reply": reply})
    messages.append({"role": "assistant", "content": reply})

    if "DONE" in reply:
        return {"answer": reply, "stopped_by": "model", "steps": step, "log": log}
    if tokens_burned >= token_budget:
        return {"answer": None, "stopped_by": "token_budget", "steps": step, "log": log}
    if time.monotonic() - started >= timeout:
        return {"answer": None, "stopped_by": "timeout", "steps": step, "log": log}

    messages.append({"role": "user", "content": "Continue. Reply DONE when finished."})

return {"answer": None, "stopped_by": "max_steps", "steps": max_steps, "log": log}
```

Four details are worth your attention.

**Every exit says why it exited.** The return value carries `stopped_by`, which is one of `model`, `token_budget`, `timeout` or `max_steps`. When an agent gets cut off, the first question is which guard fired. Now you can answer it from the result instead of from a hunch.

**Every step is logged.** The `log` list holds the step number, the running token count and the reply. When the cap trips, you can read what the model was doing in its last ten turns. That's your diagnostic.

**The limits are parameters.** `run_agent` takes `max_steps`, `token_budget` and `timeout` as arguments with the constants as defaults. That's what makes the tests fast: a test can set `max_steps=5` and finish in milliseconds.

**A cut-off returns `answer: None`.** The function doesn't hand back the last draft and pretend it finished. A caller has to handle the "didn't finish" case on purpose.

Run it with the mock and you get ten lines, then the verdict:

```text
stopped_by=max_steps after 10 steps
  step=1 tokens~18  Draft 1: still refining the summary, one more pass...
  ...
  step=10 tokens~180  Draft 10: still refining the summary, one more pass...
```

With the mock, the step cap fires first. At 18 tokens per step, 4,000 would take far longer to reach. That tells you something about sizing: the guards should cover different failure shapes. A cap on steps catches chatty loops with short replies. A token budget catches loops where each reply is huge. A timeout catches slow calls. Set all three, because you don't know which shape you'll get.

## The proof

[`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/01-runaway-loop/tests/test_fixed.py) has five tests:

- `test_fixed_stops_at_max_steps` feeds a model that never says DONE and checks the result is `max_steps` after exactly 5 steps.
- `test_fixed_stops_on_token_budget` sets a budget of 50 and checks the budget guard fires.
- `test_fixed_still_finishes_normally` checks a model that says DONE at step 3 still returns `stopped_by == "model"`. A guard that breaks the happy path is a bad guard.
- `test_fixed_logs_every_step` checks the log holds steps 1 through 4.
- `test_broken_never_stops` runs the broken loop with a model that raises after 50 calls, and asserts the exception fires. It proves the broken version has no exit of its own.

That last one is an unusual test. It pins the bug in place, so nobody "simplifies" the fixed version back into a `while True` later and calls it cleanup.

## Where the fix stops

Be straight with yourself about what these limits don't cover.

- **A single hung call.** The timeout is checked after each model call returns. If one call hangs for ten minutes, the guard doesn't fire until it comes back. In production, set a timeout on the HTTP request itself.
- **Overshoot.** The budget check runs after the spend. A step can push you past the ceiling before the guard sees it.
- **The cost proxy.** `len(reply.split()) * 2` is a stand-in. Use the token counts your API returns, and count input tokens too.
- **Cost across runs.** These guards bound one run. A scheduler that restarts a stopped agent every minute still burns money. Put a spend cap at the account level as well.

## The takeaway

Never let an agent be the only thing deciding when to stop. Put the iteration cap, the token budget and the timeout outside the model's reach, and log every step so you can read what it was doing when you cut it off.

---

[Next: Failure 2, the stuck agent &rarr;]({{ '/failures/02-stuck-agent/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
