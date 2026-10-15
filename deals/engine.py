"""KDealz engine: read retailer feeds, keep price history, find real deals, draft posts.

A deal is only a deal if the price today is genuinely low for that product:
  * at or below its lowest price in the last 90 days, and
  * at least 8% under its usual (median) price over those 90 days, and
  * we have at least 21 days of history (no history, no claim).
A retailer's "was" price is ignored unless we saw the product sell at that price in the last 90 days.
Claiming a saving we can't show would breach the Fair Trading Act, so the engine never does it.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import statistics
from pathlib import Path

from .catalog import CATEGORIES, SPEC_LABEL

MIN_DAYS, WINDOW, MIN_DROP = 21, 90, 0.08


# ------------------------------------------------------------------ feeds
def load_feed(path: Path, mapping: dict) -> list[dict]:
    """Read a retailer product feed (CSV) into KDealz's shape using a column mapping from config.json."""
    out = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            g = lambda k, d="": (row.get(mapping.get(k, k)) or d).strip()
            cat = mapping.get("categories", {}).get(g("category"), g("category"))
            if cat not in CATEGORIES:
                continue
            try:
                price = float(g("price").replace("$", "").replace(",", ""))
            except ValueError:
                continue
            specs = {}
            for s in CATEGORIES[cat]["specs"]:
                try:
                    specs[s] = float(g(s, "0"))
                except ValueError:
                    pass
            out.append({"id": g("id"), "retailer": g("retailer"), "name": g("name"), "brand": g("brand"), "category": cat,
                        "price": round(price, 2), "url": g("url"), "image": g("image"), "specs": specs})
    return out


# ------------------------------------------------------------------ history
def update_history(hist: dict, products: list[dict], day: str) -> dict:
    """Add today's price for every product (one point per day) and keep a year of history."""
    cutoff = (dt.date.fromisoformat(day) - dt.timedelta(days=365)).isoformat()
    for p in products:
        pts = [x for x in hist.get(p["id"], []) if x[0] != day and x[0] >= cutoff]
        pts.append([day, p["price"]])
        hist[p["id"]] = sorted(pts)
    return hist


# ------------------------------------------------------------------ deals
def check(p: dict, pts: list, day: str) -> dict | None:
    start = (dt.date.fromisoformat(day) - dt.timedelta(days=WINDOW)).isoformat()
    past = [v for d, v in pts if start <= d < day]
    if len({d for d, _ in pts if start <= d < day}) < MIN_DAYS:
        return None
    usual, low = statistics.median(past), min(past)
    drop = 1 - p["price"] / usual
    if p["price"] > low or drop < MIN_DROP:
        return None
    return {**p, "usual": round(usual, 2), "low90": round(low, 2), "drop_pct": round(drop * 100), "save": round(usual - p["price"], 2),
            "lowest_90": p["price"] < low, "days": len(past)}


def value_score(p: dict, peers: list[dict]) -> float:
    """0-100: how much product you get for the money, against the same category."""
    w = CATEGORIES[p["category"]]["weights"]
    s = 0.0
    for k, wt in w.items():
        vals = [q["specs"].get(k, 0) for q in peers] or [1]
        top = max(vals) or 1
        s += wt * p["specs"].get(k, 0) / top
    prices = [q["price"] for q in peers]
    cheap = (min(prices) / p["price"]) if p["price"] else 0
    return round(100 * (0.7 * s + 0.3 * cheap), 1)


def find_deals(products: list[dict], hist: dict, day: str) -> list[dict]:
    deals = [d for p in products if (d := check(p, hist.get(p["id"], []), day))]
    by_cat = {}
    for p in products:
        by_cat.setdefault(p["category"], []).append(p)
    for d in deals:
        d["value"] = value_score(d, by_cat[d["category"]])
    return sorted(deals, key=lambda d: (-d["drop_pct"], -d["value"]))


# ------------------------------------------------------------------ writing
def spec_line(p: dict) -> str:
    bits = []
    for k in CATEGORIES[p["category"]]["specs"]:
        v = p["specs"].get(k)
        if v and k == "resolution_k":
            bits.append({1: "Full HD", 2: "QHD", 4: "4K", 5: "5K", 8: "8K"}.get(int(v), f"{int(v)}K"))
            continue
        if v:
            v = int(v) if float(v).is_integer() else v
            bits.append(f"{v}{SPEC_LABEL[k]}" if SPEC_LABEL[k].startswith(("″", "W", "K", "Hz")) else f"{v} {SPEC_LABEL[k]}")
    return " · ".join(bits)


def draft_post(d: dict) -> dict:
    cat = CATEGORIES[d["category"]]
    head = f"{d['name']}: ${d['price']:,.0f} at {d['retailer']}"
    lowest = "the lowest we've seen in 90 days" if d["lowest_90"] else "matching its 90-day low"
    body = (f"Usually about ${d['usual']:,.0f} over the last {d['days']} days we've tracked it, now ${d['price']:,.0f} "
            f"({d['drop_pct']}% under its usual price, {lowest}). {spec_line(d)}. Value score {d['value']:.0f}/100 against other "
            f"{cat['title']} we track.")
    return {"id": d["id"], "kind": "deal", "category": d["category"], "title": head, "body": body, "price": d["price"],
            "usual": d["usual"], "drop_pct": d["drop_pct"], "url": d["url"], "retailer": d["retailer"], "value": d["value"]}


def draft_guides(products: list[dict]) -> list[dict]:
    """'Best <category> under $X' guides: the top 5 by value score in each price band."""
    out = []
    for key, cat in CATEGORIES.items():
        peers = [p for p in products if p["category"] == key]
        if not peers:
            continue
        for band in cat["bands"]:
            pool = sorted((p for p in peers if p["price"] <= band), key=lambda p: -value_score(p, peers))[:5]
            if len(pool) < 3:
                continue
            out.append({"id": f"guide-{key}-{band}", "kind": "guide", "category": key,
                        "title": f"Best {cat['title']} under ${band:,}",
                        "picks": [{"name": p["name"], "retailer": p["retailer"], "price": p["price"], "url": p["url"],
                                   "why": spec_line(p), "value": value_score(p, peers)} for p in pool]})
    return out


# ------------------------------------------------------------------ files
def read_json(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False))
