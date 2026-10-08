"""Failure #16: Silent Degradation (FIXED).

The monitor tracks recall (the share of real fraud caught), because accuracy
hides rare-event failures. Each metric has a threshold and a named owner,
and a breach produces an alert that says who acts and what to do first.

Run: python fixed.py
"""
from dataclasses import dataclass

FLAG_ABOVE = 900.00
LEGIT_PER_WEEK = 980
FRAUD_PER_WEEK = 20


@dataclass(frozen=True)
class MonitorConfig:
    metric: str
    min_value: float
    owner: str
    action: str

    def __post_init__(self):
        if not self.owner.strip() or not self.action.strip():
            raise ValueError("a monitor needs a named owner and a first action")


CONFIG = MonitorConfig(metric="recall", min_value=0.90, owner="fraud-ops",
                       action="route all transactions to manual review")


def make_week(week):
    legit = [(10.00 + (i * 7) % 800, False) for i in range(LEGIT_PER_WEEK)]
    adapted = min(FRAUD_PER_WEEK, max(0, week - 3) * 5)
    fraud = [(400.00 if i < adapted else 950.00, True) for i in range(FRAUD_PER_WEEK)]
    return legit + fraud


def model(amount):
    return amount > FLAG_ABOVE


def weekly_stats(transactions):
    correct = sum(model(amount) == is_fraud for amount, is_fraud in transactions)
    fraud_total = sum(is_fraud for _, is_fraud in transactions)
    caught = sum(model(amount) for amount, is_fraud in transactions if is_fraud)
    return {"accuracy": correct / len(transactions),
            "recall": caught / fraud_total if fraud_total else 1.0,
            "caught": caught}


def monitor(stats, config=CONFIG):
    value = stats[config.metric]
    if value < config.min_value:
        return {"alert": True, "owner": config.owner, "action": config.action,
                "detail": f"{config.metric} {value:.0%} is below {config.min_value:.0%}"}
    return {"alert": False}


if __name__ == "__main__":
    for week in range(1, 9):
        stats = weekly_stats(make_week(week))
        result = monitor(stats)
        line = f"week {week}: accuracy {stats['accuracy']:.1%}, recall {stats['recall']:.0%}"
        if result["alert"]:
            line += f"  ALERT -> {result['owner']}: {result['action']} ({result['detail']})"
        print(line)
