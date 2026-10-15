# KDealz

Honest, mostly automated affiliate deals for consumer electronics in New Zealand: phones, mobile gear, wearables,
smart home and IoT, laptops, monitors and interactive displays.

## How it works

1. **Every morning (about 7am NZ)** a GitHub Action reads the retailers' product feeds (Commission Factory data
   feeds), keeps each product's price history and finds genuine deals: at or below the 90-day low, at least 8% under
   the usual price, with at least 21 days of history. Retailers' "was" prices are never trusted.
2. It drafts deal posts and "best ... under $X" guides ranked by a value score, and opens a pull request
   **"Deals for review"** with a tick box next to every deal.
3. **Approve on your phone** in the GitHub app: untick any deal you don't want, wait about 30 seconds for the
   "Record review choices" check, then merge to publish. Close the pull request to publish nothing.
4. Merging rebuilds the site on GitHub Pages. Every buy link is `rel="sponsored nofollow"` and every page discloses
   the commission (ASA and Fair Trading Act).

All dates are New Zealand dates (Pacific/Auckland).

## Run it

```
python -m deals demo     # made-up demo catalogue (site shows a DEMO banner)
python -m deals run      # feeds -> history -> drafts + REVIEW.md
python -m deals build    # site/ from the approved drafts
python -m pytest -q
```

Going live: put the Commission Factory feed URL in the repo secret `FEED_URL`, switch `config.json` to the real feed
mapping (add each retailer's own category names to `categories`) and set `"demo": false`.
