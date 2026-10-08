# Failure #16: Silent Degradation

> Fraud got through for four straight weeks. The dashboard said 98% accuracy the whole time.

## What it looks like in production

A model gets worse slowly because the world changed: attackers adapt, inputs shift, a dependency updates. The monitor tracks one number, overall accuracy, and for a rare event that number barely moves. A filter that misses every fraud case still scores 98% when 98% of the traffic is legitimate. No alert fires, so no one acts.

## The lesson

**Monitor the metric that matches the harm, give it a threshold, and name the person who acts when it breaches.**

## Files in this folder

- `broken.py`: alerts on accuracy only, so eight weeks of decay pass without an alert.
- `fixed.py`: alerts on recall, requires a named owner and first action for every monitor, and reports who should do what.
- `tests/`: pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # missed fraud 20/20 by week 7, alert=False every week
python fixed.py    # first ALERT in week 4, with an owner and an action
```

## The fix in one sentence

Pick the metric that measures the thing you can't afford to miss, set a threshold, and refuse to accept a monitor that has no owner or first action.

## Read the lesson

Full written walkthrough: [Failure 16 in *The Agent Autopsy* series](https://menokoog.github.io/agent-autopsy/failures/16-silent-degradation/).
