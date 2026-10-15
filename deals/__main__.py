"""KDealz command line.

  python -m deals demo              make demo data (made-up products, 100 days of prices)
  python -m deals run               read the feeds, update price history, draft today's deals and guides for review
  python -m deals review --body-file F   record which deals were unticked in the review pull request
  python -m deals build             build the site from what has been approved (merged)

The daily GitHub Action runs `run` and opens a pull request "Deals for review" with a tick box per deal.
On the phone: untick a deal to reject it, merge to publish the rest, close to publish nothing.
Dates are New Zealand dates (Pacific/Auckland), whatever timezone the machine runs in.
"""
import argparse
import datetime as dt
import re
from zoneinfo import ZoneInfo
from pathlib import Path

from . import engine, sample, site

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def cfg():
    return engine.read_json(ROOT / "config.json", {"demo": True, "feeds": [{"path": "data/demo_feed.csv", "mapping": {}}]})


def cmd_demo(a):
    path, hist = sample.make(DATA, dt.date.fromisoformat(a.day))
    engine.write_json(DATA / "history.json", hist)
    print("demo feed:", path.relative_to(ROOT))


def cmd_run(a):
    c = cfg()
    products = []
    for f in c["feeds"]:
        products += engine.load_feed(ROOT / f["path"], f.get("mapping", {}))
    hist = engine.update_history(engine.read_json(DATA / "history.json", {}), products, a.day)
    engine.write_json(DATA / "history.json", hist)
    deals = engine.find_deals(products, hist, a.day)
    drafts = {"day": a.day, "demo": c.get("demo", False), "deals": [engine.draft_post(d) for d in deals],
              "guides": engine.draft_guides(products)}
    engine.write_json(DATA / "drafts.json", drafts)
    lines = [f"# Deals for review · {a.day}", "", f"{len(products)} products checked, {len(drafts['deals'])} genuine deals, "
             f"{len(drafts['guides'])} guides.", "",
             "**Untick any deal you don't want**, wait about 30 seconds for the check to finish, then **merge** to publish. "
             "Close this pull request to publish nothing.", ""]
    lines += [f"- [x] **{d['title']}** ({d['drop_pct']}% under usual ${d['usual']:,.0f}, value {d['value']:.0f}/100) <!-- id:{d['id']} -->"
              for d in drafts["deals"]]
    (ROOT / "REVIEW.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:3]))


TICK = re.compile(r"^\s*[-*] \[( |x|X)\] .*<!-- id:(\S+) -->", re.M)


def unticked(body: str) -> list[str]:
    """Deal ids whose box is unticked in the review pull request text."""
    return sorted(i for box, i in TICK.findall(body) if box == " ")


def cmd_review(a):
    d = engine.read_json(DATA / "drafts.json", {"deals": []})
    known = {x["id"] for x in d["deals"]}
    d["rejected"] = [i for i in unticked(Path(a.body_file).read_text(encoding="utf-8")) if i in known]
    engine.write_json(DATA / "drafts.json", d)
    print(f"{len(known) - len(d['rejected'])} deals approved, {len(d['rejected'])} rejected")


def cmd_build(a):
    d = engine.read_json(DATA / "drafts.json", {"day": a.day, "demo": True, "deals": [], "guides": []})
    rej = d.get("rejected", [])
    site.build(ROOT / "site", d["deals"], d["guides"], d.get("demo", True), d["day"], rej)
    print("site built:", len(d["deals"]) - len(set(rej) & {x["id"] for x in d["deals"]}), "deals,", len(d["guides"]), "guides")


if __name__ == "__main__":
    p = argparse.ArgumentParser(prog="deals")
    p.add_argument("cmd", choices=["demo", "run", "review", "build"])
    p.add_argument("--day", default=dt.datetime.now(ZoneInfo("Pacific/Auckland")).date().isoformat())
    p.add_argument("--body-file", help="review: a file holding the pull request text")
    a = p.parse_args()
    {"demo": cmd_demo, "run": cmd_run, "review": cmd_review, "build": cmd_build}[a.cmd](a)
