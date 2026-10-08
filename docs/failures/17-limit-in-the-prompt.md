---
title: "Failure 17: Limit in the prompt"
permalink: /failures/17-limit-in-the-prompt/
---

# Failure 17: Limit in the prompt

*The prompt said refunds stop at $50. The customer asked for $120, and the agent paid it.*

## The scenario

A support agent can issue refunds. Its system prompt says: "Never refund more than $50 per order." A customer demands $120 and threatens to leave. The model, which wants to be helpful and has been pushed, calls the refund tool with 120. The tool refunds 120.

The limit was real in the sense that someone wrote it down. It was never enforced by anything that could say no.

Microsoft's AI Red Team lists this pattern in its taxonomy of agentic failure modes under *excessive agency* (an agent with broad scope takes actions beyond what was expected) and *incorrect permissions* (an agent holds more access than the situation should allow) ([Microsoft AI Red Team](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/Taxonomy-of-Failure-Mode-in-Agentic-AI-Systems-Whitepaper.pdf)). The demo is the smallest version of it.

The code is in [`17-limit-in-the-prompt`](https://github.com/MenokoOG/agent-autopsy/tree/main/17-limit-in-the-prompt). The model is a mock that gives in to pressure, so it shows the shape of the failure and says nothing about how often a real model does it.

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/17-limit-in-the-prompt/broken.py):

```python
SYSTEM_PROMPT = "You are a support agent. Never refund more than $50 per order."

def run_agent(customer_message, ledger):
    call = model(customer_message)
    # THE BUG: the only limit is the sentence in SYSTEM_PROMPT. Nothing in
    # the tool path checks the amount.
    return refund(ledger, **call["args"])
```

The run:

```text
prompt: You are a support agent. Never refund more than $50 per order.
refunded $120.00 on A100
ledger: [('A100', 120.0)]
```

The prompt is in the output, and the ledger ignores it.

## Why it happens

A system prompt is input to a probabilistic model. It shapes behavior and doesn't bind it. Pressure from a user, a long context that buries the instruction, or a prompt injection can all move the model off the rule. If the only copy of the rule is in the prompt, the rule fails whenever the model does.

The tool is the other half of the problem. It was written to do what the model asks. Its author assumed the prompt would keep the model in bounds, and the prompt's author assumed the tool would reject bad inputs. Each side relied on the other.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/17-limit-in-the-prompt/fixed.py) moves the rule into the tool.

**Check the limit where the money moves.**

```python
remaining = REFUND_LIMIT_PER_ORDER - self.refunded.get(order_id, 0.0)
if not self.enabled:
    reason = "bot disabled"
elif amount > remaining + 1e-9:
    reason = f"${amount:.2f} exceeds the ${remaining:.2f} left on {order_id}"
else:
    self.refunded[order_id] = self.refunded.get(order_id, 0.0) + amount
    self.ledger.append((order_id, amount))
    return f"refunded ${amount:.2f} on {order_id}"
self.escalations.append(f"{order_id}: {reason}")
return f"ESCALATED to a human: {reason}"
```

**Count what's already been paid.** The check uses the amount remaining on the order, not just the size of this request. A customer who asks for $20 three times doesn't get $60.

**Escalate, don't fail silently.** An over-limit request lands in a human queue with the reason attached. The customer isn't dropped, and a person decides.

**Keep a kill switch.** `disable()` stops the bot from acting at all. Every request after that goes to the queue.

Run it:

```text
prompt: You are a support agent. Never refund more than $50 per order.
ESCALATED to a human: $120.00 exceeds the $50.00 left on A100
then three small asks on the same order:
  refunded $20.00 on A100
  refunded $20.00 on A100
  ESCALATED to a human: $20.00 exceeds the $10.00 left on A100
ledger: [('A100', 20.0), ('A100', 20.0)]
after kill switch: ESCALATED to a human: bot disabled
human queue: ['A100: $120.00 exceeds the $50.00 left on A100', 'A100: $20.00 exceeds the $10.00 left on A100', 'A100: bot disabled']
```

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/17-limit-in-the-prompt/tests/test_fixed.py):

- `test_fixed_escalates_a_demand_over_the_limit` checks the $120 demand pays nothing.
- `test_fixed_pays_a_request_within_the_limit` checks normal refunds still work.
- `test_fixed_counts_earlier_refunds_so_splitting_fails` checks three $20 asks stop after two.
- `test_fixed_allows_a_refund_that_lands_exactly_on_the_limit` checks the boundary.
- `test_fixed_kill_switch_sends_everything_to_humans` checks the switch.
- `test_broken_pays_120_despite_the_prompt_saying_50` pins the original failure.

## Where the fix stops

- **The cap is per order.** A customer can open ten orders. Add limits per customer, per day and per agent, and watch the totals.
- **The number is still a guess.** $50 is a policy someone chose. Review it against real refund data, and make the limit configurable outside the model's reach.
- **The escalation queue is a new weak point.** If humans approve every item without reading, the limit has moved from code to a rubber stamp. See [failure 12]({{ '/failures/12-no-human-brake/' | relative_url }}) and [failure 14]({{ '/failures/14-rubber-stamp-verifier/' | relative_url }}).
- **The kill switch must be drilled.** A switch nobody has pressed may not work. Test it on a schedule, and make sure the fallback path has staff and a process.
- **Other limits need the same treatment.** Spending, data access, recipients and rate all belong in code. A useful review question is which rules in your prompt would cost you money if the model ignored them.

## The takeaway

A prompt is a request and code is a guarantee, so put every limit you can't afford to see broken in the tool, and keep a tested way to switch the bot off.

---

[&larr; Previous: Failure 16]({{ '/failures/16-silent-degradation/' | relative_url }}) · [Next: The field checklist &rarr;]({{ '/field-checklist/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
