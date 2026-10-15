"""Build the static site (GitHub Pages): home with today's deals, a page per category, the guides, and the
disclosure. Every buy link is marked rel="sponsored nofollow" and every page says how the site earns."""
from __future__ import annotations

import html
from pathlib import Path

from .catalog import CATEGORIES

E = html.escape
CONTACT = "kdealznz@gmail.com"
DISCLOSURE = ("KDealz earns a commission when you buy through some links on this site, at no extra cost to you. "
              "It never changes which products we list or how we rank them. Prices are checked daily and can change; "
              "a saving is only shown when we have tracked the price for at least 21 days.")

CSS = """:root{--bg:#0b111b;--panel:#121b29;--ink:#eaf0f6;--ink2:#b0bac8;--ink3:#7d8899;--acc:#ffd27a;--good:#3fb87f;--etch:#24324a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--acc)}.wrap{max-width:1100px;margin:0 auto;padding:0 16px}
header.top{border-bottom:1px solid var(--etch);padding:14px 0}header.top .wrap{display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.logo{font-weight:800;font-size:20px;color:var(--ink);text-decoration:none}.logo b{color:var(--acc)}
nav a{color:var(--ink2);text-decoration:none;margin-right:12px;font-size:14px;white-space:nowrap}nav a:hover{color:var(--ink)}
.demo{background:#5a2a12;color:#ffd9c2;text-align:center;padding:8px 16px;font-weight:600;font-size:13px}
.disc{background:var(--panel);border:1px solid var(--etch);border-radius:10px;padding:10px 12px;font-size:12.5px;color:var(--ink3);margin:14px 0}
h1{font-size:28px;margin:20px 0 4px}h2{font-size:20px;margin:26px 0 10px}.sub{color:var(--ink2);margin:0 0 10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--etch);border-radius:14px;padding:14px;display:flex;flex-direction:column;gap:6px}
.card h3{margin:0;font-size:15.5px}.card p{margin:0;color:var(--ink2);font-size:13.5px}
.price{font-size:22px;font-weight:800}.was{color:var(--ink3);font-size:13px}.tag{display:inline-block;background:rgba(63,184,127,.15);color:var(--good);border-radius:6px;padding:2px 7px;font-size:12px;font-weight:700}
.buy{margin-top:auto;display:inline-block;background:var(--acc);color:#1d1503;text-decoration:none;font-weight:700;border-radius:9px;padding:8px 12px;text-align:center}
ol.picks{padding-left:20px}ol.picks li{margin:0 0 10px}ol.picks small{color:var(--ink3);display:block}
footer{border-top:1px solid var(--etch);margin-top:40px;padding:18px 0;color:var(--ink3);font-size:12.5px}
.cats{display:flex;flex-wrap:wrap;gap:8px}.cats a{background:var(--panel);border:1px solid var(--etch);border-radius:20px;padding:6px 12px;text-decoration:none;color:var(--ink)}"""


def page(title, body, demo, depth=0, desc=""):
    up = "../" * depth
    nav = "".join(f'<a href="{up}{k}/">{c["icon"]} {E(c["title"])}</a>' for k, c in CATEGORIES.items())
    return f"""<!doctype html><html lang="en-NZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · KDealz</title><meta name="description" content="{E(desc or 'Real price drops on phones, wearables, laptops, monitors and smart home tech in New Zealand, checked daily.')}">
<link rel="stylesheet" href="{up}style.css"></head><body>
{'<div class="demo">DEMO DATA: made-up products and prices for testing. Not real deals.</div>' if demo else ''}
<header class="top"><div class="wrap"><a class="logo" href="{up}">K<b>Dealz</b></a><nav>{nav}<a href="{up}guides/">📘 Guides</a></nav></div></header>
<main class="wrap">{body}<p class="disc">{E(DISCLOSURE)} <a href="{up}about/">How we pick deals</a></p></main>
<footer><div class="wrap">KDealz · independent tech deals for New Zealand · prices in NZD incl. GST</div></footer></body></html>"""


def card(p):
    return (f'<article class="card"><span class="tag">{p["drop_pct"]}% under usual</span><h3>{E(p["title"].split(":")[0])}</h3>'
            f'<div><span class="price">${p["price"]:,.0f}</span> <span class="was">usually ${p["usual"]:,.0f} · {E(p["retailer"])}</span></div>'
            f'<p>{E(p["body"])}</p><a class="buy" href="{E(p["url"])}" rel="sponsored nofollow noopener" target="_blank">See it at {E(p["retailer"])}</a></article>')


def guide_html(g):
    return "<ol class=\"picks\">" + "".join(
        f'<li><b>{E(x["name"])}</b>, ${x["price"]:,.0f} at {E(x["retailer"])} · <a href="{E(x["url"])}" rel="sponsored nofollow noopener" target="_blank">see it</a>'
        f'<small>{E(x["why"])} · value score {x["value"]:.0f}/100</small></li>' for x in g["picks"]) + "</ol>"


def build(out: Path, deals: list[dict], guides: list[dict], demo: bool, day: str, rejected=()):
    deals = [d for d in deals if d["id"] not in set(rejected)]
    out.mkdir(parents=True, exist_ok=True)
    (out / "style.css").write_text(CSS)
    (out / ".nojekyll").write_text("")
    cats = '<div class="cats">' + "".join(f'<a href="{k}/">{c["icon"]} {E(c["title"])}</a>' for k, c in CATEGORIES.items()) + "</div>"
    top = sorted(deals, key=lambda d: (-d["drop_pct"], -d["value"]))[:12]
    body = (f"<h1>Real price drops, checked daily</h1><p class=\"sub\">Phones, mobile gear, wearables, smart home, laptops, monitors and "
            f"interactive displays in New Zealand. Updated {E(day)}. A deal only shows when today's price beats its own 90-day history.</p>{cats}"
            f"<h2>Today's best deals</h2><div class=\"grid\">{''.join(map(card, top)) or '<p>No genuine deals today. We would rather show nothing than a fake saving.</p>'}</div>")
    (out / "index.html").write_text(page("Real price drops on tech", body, demo))
    for k, c in CATEGORIES.items():
        ds = [d for d in deals if d["category"] == k]
        gs = [g for g in guides if g["category"] == k]
        b = (f"<h1>{c['icon']} {E(c['title'])} deals</h1><div class=\"grid\">{''.join(map(card, ds)) or '<p>No genuine deals in this category today.</p>'}</div>"
             + "".join(f"<h2>{E(g['title'])}</h2>{guide_html(g)}" for g in gs))
        (out / k).mkdir(exist_ok=True)
        (out / k / "index.html").write_text(page(f"{c['title']} deals", b, demo, 1))
    (out / "guides").mkdir(exist_ok=True)
    gb = "<h1>Buying guides</h1>" + "".join(f"<h2>{E(g['title'])}</h2>{guide_html(g)}" for g in guides)
    (out / "guides" / "index.html").write_text(page("Buying guides", gb, demo, 1))
    (out / "about").mkdir(exist_ok=True)
    ab = ("<h1>How we pick deals</h1><p>KDealz reads retailers' product lists every day and keeps each product's price history. "
          "A product is a deal only when today's price is at or below its lowest price in the last 90 days and at least 8% under its usual price, "
          "with at least 21 days of history. We ignore \"was\" prices we haven't seen ourselves.</p><p>Guides rank products by a value score: "
          "the specs that matter for that kind of product against its price, compared with everything else we track. Every post is reviewed by a person with years of "
          "experience in consumer electronics before it goes live.</p>"
          f"<p>Questions, corrections or a price we got wrong? Email <a href=\"mailto:{CONTACT}\">{CONTACT}</a>.</p>")
    (out / "about" / "index.html").write_text(page("How we pick deals", ab, demo, 1))
