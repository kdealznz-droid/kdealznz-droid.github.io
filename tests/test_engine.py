import datetime as dt
from deals import engine

DAY = "2026-10-16"
def hist(prices):
    d0 = dt.date.fromisoformat(DAY)
    return [[(d0 - dt.timedelta(days=len(prices) - i)).isoformat(), v] for i, v in enumerate(prices)]
P = {"id": "x", "category": "phones", "price": 800.0, "specs": {"storage_gb": 256}, "name": "X", "retailer": "R", "url": "u"}

def test_real_drop_is_a_deal():
    d = engine.check(P, hist([1000.0] * 60), DAY)
    assert d and d["drop_pct"] == 20 and d["save"] == 200

def test_no_history_no_claim():
    assert engine.check(P, hist([1000.0] * 10), DAY) is None

def test_not_lowest_in_90_days_is_not_a_deal():
    assert engine.check(P, hist([1000.0] * 50 + [750.0] + [1000.0] * 20), DAY) is None

def test_small_drop_is_not_a_deal():
    assert engine.check({**P, "price": 960.0}, hist([1000.0] * 60), DAY) is None

def test_fake_was_price_is_never_used():
    d = engine.draft_post({**engine.check(P, hist([1000.0] * 60), DAY), "value": 50})
    assert "$1,000" in d["body"] and "1,400" not in d["body"]
