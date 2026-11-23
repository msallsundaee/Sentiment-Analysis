"""Task 1: collect comments for every URL in data/posts.csv into data/raw/raw_comments.csv.
Stores text, timestamp and reaction count only: no names, handles, profile links or photos."""
import csv
import time

from src import config, reddit, scraper, youtube

FIELDS = ["text", "timestamp", "reactions", "platform", "source_post", "collected_at"]
API = {"youtube": youtube.fetch, "reddit": reddit.fetch}


def run(limit=400, facebook=False):
    urls = config.read_urls()
    if not urls:
        raise SystemExit(f"No URLs in {config.POSTS}")
    new = not config.RAW.exists()
    with open(config.RAW, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()

        def save(url, platform, rows):
            for r in rows:
                w.writerow({**r, "platform": platform, "source_post": url, "collected_at": time.strftime("%Y-%m-%d")})
            f.flush()
            print(f"  {platform}: saved {len(rows)} comments  {url[:70]}")

        fb = []
        for url in urls:
            p = config.platform_of(url)
            if p in API:
                try:
                    save(url, p, API[p](url, limit))
                except Exception as e:  # one bad link must not lose the rest
                    print(f"  failed ({p}): {str(e)[:100]}  {url[:70]}")
            elif p == "facebook":
                fb.append(url)
            else:
                print(f"  skipped (unsupported): {url[:70]}")
        if fb and not facebook:
            print(f"  skipped {len(fb)} Facebook links (browser scraping is opt-in: add --facebook)")
        elif fb:
            for url, rows in scraper.fetch_many(fb, limit):
                save(url, "facebook", rows)
