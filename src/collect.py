"""Task 1: collect comments for every URL in data/posts.csv into data/raw/raw_comments.csv.
Stores text, timestamp and reaction count only: no names, handles, profile links or photos."""
import csv
import json
import re
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


SHEET = config.SHEET
HANDLE = re.compile(r"@[\w.\-]+")  # YouTube/Facebook reply handles are personal identifiers


def import_sheet():
    """Rebuild data/raw/raw_comments.csv from the group sheet, stripping @handles from both.
    If the sheet has a `Comment Text EN` column (=GOOGLETRANSLATE in Google Sheets), it becomes
    the translation cache, so `analyze` needs no translation service."""
    rows = list(csv.reader(open(SHEET, encoding="utf-8-sig", newline="")))
    col = {name.strip(): i for i, name in enumerate(rows[0]) if name.strip()}
    strip = lambda t: re.sub(r"\s+", " ", HANDLE.sub("", t)).strip()
    out, en, bad = [], {}, 0
    for r in rows[1:]:
        text = strip(r[col["Comment Text"]])
        r[col["Comment Text"]] = text
        if "Comment Text EN" in col and text:
            r[col["Comment Text EN"]] = t_en = strip(r[col["Comment Text EN"]])
            if not t_en or re.fullmatch(r"#[A-Z/0]+[!?]?", t_en) or t_en.lower().startswith("loading"):
                bad += 1  # formula error or cell exported before it finished
            else:
                en[text] = t_en
        if text:
            out.append({"text": text, "timestamp": r[col["Comment Date"]], "reactions": "",
                        "platform": r[col["Platform"]].lower(), "source_post": r[col["Source URL"]],
                        "collected_at": r[col["Date Collected"]]})
    csv.writer(open(SHEET, "w", encoding="utf-8-sig", newline=""), lineterminator="\n").writerows(rows)
    with open(config.RAW, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} comments to {config.RAW}")
    if "Comment Text EN" in col:
        if bad:
            raise SystemExit(f"{bad} rows have no usable translation (#ERROR / Loading / empty). "
                             "Let the sheet finish, re-export, and run import-sheet again.")
        config.TRANSLATIONS.write_text(json.dumps(en, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {len(en)} translations from the sheet to {config.TRANSLATIONS}")
    else:
        print("no `Comment Text EN` column in the sheet: translations not imported")


def sync_sheet(df):
    """Write the final consensus label back to the sheet, and blank keywords that are not in the comment
    (the scrape scripts filled 'bilihin' whenever nothing matched)."""
    label = dict(zip(df.text, df.label.str.capitalize()))
    rows = list(csv.reader(open(SHEET, encoding="utf-8-sig", newline="")))
    col = {name: i for i, name in enumerate(rows[0])}
    for r in rows[1:]:
        text = r[col["Comment Text"]]
        r[col["Sentiment"]] = label.get(text, "")  # blank = dropped as duplicate/too short
        if r[col["Keyword Matched"]].lower() not in text.lower():
            r[col["Keyword Matched"]] = ""
    csv.writer(open(SHEET, "w", encoding="utf-8-sig", newline=""), lineterminator="\n").writerows(rows)
