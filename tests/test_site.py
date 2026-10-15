import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_every_buy_link_is_marked_and_disclosed():
    for c in ("demo", "run", "build"):
        subprocess.run([sys.executable, "-m", "deals", c, "--day", "2026-10-16"], cwd=ROOT, check=True)
    for f in (ROOT / "site").rglob("index.html"):
        h = f.read_text()
        assert "earns a commission" in h
        assert h.count('class="buy"') == h.count('rel="sponsored nofollow noopener" target="_blank">See it')


def test_unticked_deals_are_not_published(tmp_path):
    import json
    drafts = json.loads((ROOT / "data" / "drafts.json").read_text())
    drop = drafts["deals"][0]
    body = (ROOT / "REVIEW.md").read_text().replace(f"- [x] **{drop['title']}**", f"- [ ] **{drop['title']}**")
    f = tmp_path / "body.md"
    f.write_text(body)
    try:
        subprocess.run([sys.executable, "-m", "deals", "review", "--body-file", str(f)], cwd=ROOT, check=True)
        subprocess.run([sys.executable, "-m", "deals", "build", "--day", "2026-10-16"], cwd=ROOT, check=True)
        assert json.loads((ROOT / "data" / "drafts.json").read_text())["rejected"] == [drop["id"]]
        home = (ROOT / "site" / "index.html").read_text() + (ROOT / "site" / drop["category"] / "index.html").read_text()
        assert f'class="buy" href="{drop["url"]}"' not in home
    finally:
        subprocess.run([sys.executable, "-m", "deals", "run", "--day", "2026-10-16"], cwd=ROOT, check=True)


def test_no_shelly_or_personal_details_on_the_site():
    for f in (ROOT / "site").rglob("*.html"):
        h = f.read_text()
        assert "KDealz" in h and "Shelly" not in h and "Pavi" not in h
        assert "@" not in h.replace("kdealznz@gmail.com", "")
