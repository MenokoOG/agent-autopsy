"""Failure #16: Silent Degradation (BROKEN).

A fraud filter flags large transactions. Over eight weeks, fraudsters learn
to stay under the threshold. The filter misses more every week, but the
monitor watches overall accuracy, and accuracy stays high because fraud is
rare. No alert ever fires.

Run: python broken.py
"""

FLAG_ABOVE = 900.00
ACCURACY_ALERT_BELOW = 0.95
LEGIT_PER_WEEK = 980
FRAUD_PER_WEEK = 20


def make_week(week):
    """Deterministic transactions: (amount, is_fraud). From week 4, fraudsters
    adapt in steps of 5 per week and use amounts below the threshold."""
    legit = [(10.00 + (i * 7) % 800, False) for i in range(LEGIT_PER_WEEK)]
    adapted = min(FRAUD_PER_WEEK, max(0, week - 3) * 5)
    fraud = [(400.00 if i < adapted else 950.00, True) for i in range(FRAUD_PER_WEEK)]
    return legit + fraud


def model(amount):
    return amount > FLAG_ABOVE


def weekly_stats(transactions):
    correct = sum(model(amount) == is_fraud for amount, is_fraud in transactions)
    caught = sum(model(amount) for amount, is_fraud in transactions if is_fraud)
    return {"accuracy": correct / len(transactions), "caught": caught}


def monitor(stats):
    # THE BUG: the only metric is overall accuracy. With 2% fraud, a model
    # that misses every fraud case still scores 98%.
    return stats["accuracy"] < ACCURACY_ALERT_BELOW


if __name__ == "__main__":
    for week in range(1, 9):
        stats = weekly_stats(make_week(week))
        missed = FRAUD_PER_WEEK - stats["caught"]
        print(f"week {week}: accuracy {stats['accuracy']:.1%}, "
              f"missed fraud {missed}/{FRAUD_PER_WEEK}, alert={monitor(stats)}")
