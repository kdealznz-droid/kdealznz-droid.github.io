"""Demo data: a made-up catalogue with 100 days of prices, so the engine and site can be tested before real
retailer feeds arrive. Every name says "Demo" and every retailer is "Demo Store"; the site shows a DEMO banner."""
from __future__ import annotations

import csv
import datetime as dt
import random
from pathlib import Path

from .catalog import CATEGORIES

BASE = {  # category: (price range, spec generators)
    "phones": ((349, 2199), lambda r: {"storage_gb": r.choice([128, 256, 512]), "camera_mp": r.choice([48, 50, 108, 200]),
                                        "battery_mah": r.choice([4000, 4500, 5000]), "screen_in": r.choice([6.1, 6.4, 6.7])}),
    "mobile-gear": ((19, 199), lambda r: {"watts": r.choice([20, 25, 45, 65]), "capacity_mah": r.choice([0, 10000, 20000])}),
    "wearables": ((79, 999), lambda r: {"battery_days": r.choice([1, 2, 7, 14]), "sensors": r.randint(2, 8), "screen_in": r.choice([1.2, 1.4, 1.9])}),
    "smart-home": ((29, 549), lambda r: {"protocols": r.randint(1, 4), "rating": round(r.uniform(3.6, 4.9), 1)}),
    "laptops": ((699, 3499), lambda r: {"ram_gb": r.choice([8, 16, 32]), "storage_gb": r.choice([256, 512, 1024]),
                                         "battery_h": r.choice([8, 12, 18]), "screen_in": r.choice([13.3, 14, 15.6, 16])}),
    "monitors": ((199, 1999), lambda r: {"screen_in": r.choice([24, 27, 32, 34]), "refresh_hz": r.choice([60, 75, 144, 165, 240]),
                                          "resolution_k": r.choice([1, 2, 4])}),
    "interactive": ((1999, 11999), lambda r: {"screen_in": r.choice([55, 65, 75, 86]), "touch_points": r.choice([20, 40]),
                                               "resolution_k": 4}),
}
TYPE = {"phones": "Phone", "mobile-gear": "Charger", "wearables": "Watch", "smart-home": "Smart Hub", "laptops": "Laptop",
        "monitors": "Monitor", "interactive": "Interactive Display"}


def make(out_dir: Path, today: dt.date, days: int = 100, seed: int = 2026) -> tuple[Path, dict]:
    r = random.Random(seed)
    products = []
    for cat, ((lo, hi), spec) in BASE.items():
        for i in range(10):
            usual = round(r.uniform(lo, hi), -1) - 1
            products.append({"id": f"demo-{cat}-{i}", "retailer": f"Demo Store {'ABC'[i % 3]}", "brand": "Demo",
                             "name": f"Demo {TYPE[cat]} {chr(65 + i)}{r.randint(1, 9)}", "category": cat, "usual": usual,
                             "url": f"https://example.com/demo/{cat}/{i}", "image": "", "specs": spec(r)})
    hist = {}
    for p in products:
        sale_days = set(r.sample(range(days - 1), r.randint(0, 3)))     # a few short sales in the past
        drop_today = r.random() < .22                                      # about a fifth are on a real deal today
        fake_was = r.random() < .1                                         # some have a made-up "was" price
        pts = []
        for k in range(days):
            d = (today - dt.timedelta(days=days - 1 - k)).isoformat()
            price = p["usual"] * (r.uniform(.85, .93) if k in sale_days else r.uniform(.98, 1.02))
            if k == days - 1:
                price = p["usual"] * (r.uniform(.72, .86) if drop_today else r.uniform(.97, 1.01))
            pts.append([d, round(price, 2)])
        hist[p["id"]] = pts[:-1]
        p["price"] = pts[-1][1]
        p["was"] = round(p["usual"] * 1.4, 2) if fake_was else ""
    path = out_dir / "demo_feed.csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        keys = sorted({k for c in BASE for k in BASE[c][1](random.Random(0))})
        w = csv.DictWriter(fh, ["id", "retailer", "brand", "name", "category", "price", "was", "url", "image", *keys])
        w.writeheader()
        for p in products:
            w.writerow({k: p.get(k, "") for k in ["id", "retailer", "brand", "name", "category", "price", "was", "url", "image"]} | p["specs"])
    return path, hist
