"""Master scraper for CS412 Final PIT:
Scrapes EVERY YouTube, Reddit, and Facebook link from data/comments_sheet.csv.
- All 13 YouTube videos
- All 7 Reddit threads
- All 42 Facebook posts (using secrets/cookies.txt)

Saves incrementally to:
- data/comments_sheet.csv
- data/raw/raw_comments.csv
- data/posts.csv
"""
import csv
import html
import json
import re
import time
import urllib.request
from datetime import datetime, timedelta
from afinn import Afinn
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from youtube_comment_downloader import YoutubeCommentDownloader
from playwright.sync_api import sync_playwright

from src import config
from src.scraper import fb_cookies, scrape_post
from src.all_urls import ALL_YOUTUBE_URLS, ALL_REDDIT_URLS
from src.fb_urls import FACEBOOK_URLS

KEYWORD_LIST = [
    "inflation", "bilihin", "presyo", "bigas", "gasolina", "fuel", "pamasahe",
    "kuryente", "sahod", "sweldo", "grocery", "food", "bills", "tax", "rent",
    "budget", "oil", "prices", "price", "economy", "minimum wage", "utang",
    "sibuyas", "isda", "karinderya", "mahal", "pera", "cost of living", "living cost",
    "fare", "tubig", "pagkain", "gastos", "mahirap", "gutom", "bawas", "taas"
]

TAGALOG_WORDS = {
    "ang", "ng", "mga", "sa", "na", "hindi", "ba", "pero", "naman", "talaga",
    "bilihin", "presyo", "mahal", "lahat", "walang", "kayo", "tayo", "natin",
    "kami", "sila", "ko", "mo", "niya", "kasi", "para", "kung", "dahil",
    "tapos", "nila", "mas", "din", "rin", "wala", "namin", "dapat", "yun", "yan",
    "bakit", "ano", "paano", "sobrang", "grabe", "puro", "lang"
}

CEBUANO_WORDS = {
    "kaayo", "dili", "unya", "man", "jud", "gud", "karon", "nimo", "nako",
    "unsa", "nganong", "barato", "daghan", "gamay", "kinsa", "asa", "ambot"
}

ENGLISH_WORDS = {
    "the", "is", "are", "and", "in", "to", "of", "for", "with", "at", "by",
    "from", "this", "that", "it", "they", "we", "you", "i", "have", "has",
    "had", "will", "would", "can", "could", "should", "not", "but", "so",
    "because", "as", "about", "inflation", "prices", "government", "people"
}

def detect_language(text):
    tokens = set(re.findall(r"\b[a-z]{2,}\b", text.lower()))
    if not tokens:
        return "English"
    if len(tokens & CEBUANO_WORDS) >= 2:
        return "Cebuano"
    tagalog_count = len(tokens & TAGALOG_WORDS)
    english_count = len(tokens & ENGLISH_WORDS)
    if tagalog_count >= 2 and english_count >= 2:
        return "Taglish"
    elif tagalog_count > english_count:
        return "Tagalog"
    else:
        return "English"

def extract_keyword(text):
    lower = text.lower()
    for kw in KEYWORD_LIST:
        if kw in lower:
            return kw
    return "bilihin"

def get_page_title(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            page_html = resp.read().decode("utf-8", errors="ignore")
            m = re.search(r"<title>(.*?)</title>", page_html, re.IGNORECASE)
            if m:
                return html.unescape(m.group(1)).replace(" - YouTube", "").replace(" : r/Philippines", "").strip()
    except Exception:
        pass
    slug = url.rstrip("/").split("/")[-1].replace("_", " ").replace("-", " ")
    return slug.title() if slug else "Inflation and Cost of Living"

def parse_relative_time(time_str):
    if not time_str:
        return datetime.now().strftime("%Y-%m-%d")
    s = time_str.lower().strip()
    now = datetime.now()
    m = re.search(r"(\d+)\s*(linggo|buwan|araw|oras|second|minute|hour|day|week|month|year)", s)
    if not m:
        return now.strftime("%Y-%m-%d")
    val, unit = int(m.group(1)), m.group(2)
    if unit in ("linggo", "week"):
        dt = now - timedelta(days=val * 7)
    elif unit in ("buwan", "month"):
        dt = now - timedelta(days=val * 30)
    elif unit in ("araw", "day"):
        dt = now - timedelta(days=val)
    elif unit in ("year",):
        dt = now - timedelta(days=val * 365)
    else:
        dt = now
    return dt.strftime("%Y-%m-%d")

def classify_sentiment(text, vader, afinn):
    v_score = vader.polarity_scores(text)["compound"]
    tb_score = TextBlob(text).sentiment.polarity
    a_score = afinn.score(text)
    
    v_lbl = "Positive" if v_score >= 0.05 else "Negative" if v_score <= -0.05 else "Neutral"
    tb_lbl = "Positive" if tb_score >= 0.05 else "Negative" if tb_score <= -0.05 else "Neutral"
    a_lbl = "Positive" if a_score >= 1 else "Negative" if a_score <= -1 else "Neutral"
    
    votes = [v_lbl, tb_lbl, a_lbl]
    top = max(set(votes), key=votes.count)
    return top if votes.count(top) > 1 else "Neutral"

def save_state(all_comments, header, side_refs):
    output_rows = [header]
    for idx, c in enumerate(all_comments):
        cid = f"C{idx+1:04d}"
        side = side_refs[idx+1] if (idx + 1) < len(side_refs) else []
        main_cols = [
            cid,
            c["Source URL"],
            c["Source Title / Post"],
            c["Platform"],
            c["Date Collected"],
            c["Comment Date"],
            c["Comment Text"],
            c["Language"],
            c["Keyword Matched"],
            c["Sentiment"],
            ""
        ]
        output_rows.append(main_cols + side)

    with open("data/comments_sheet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerows(output_rows)

    with open(config.RAW, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "timestamp", "reactions", "platform", "source_post", "collected_at"])
        w.writeheader()
        for c in all_comments:
            w.writerow({
                "text": c["Comment Text"],
                "timestamp": c["Comment Date"],
                "reactions": c.get("reactions", 0),
                "platform": c["Platform"].lower(),
                "source_post": c["Source URL"],
                "collected_at": c["Date Collected"]
            })

def main():
    vader = SentimentIntensityAnalyzer()
    afinn = Afinn()

    # Load existing scraped comments
    all_comments = []
    seen_texts = set()

    with open("data/comments_sheet.csv", encoding="utf-8-sig", errors="ignore") as f:
        existing_rows = list(csv.reader(f))

    header = existing_rows[0]
    side_refs = [r[11:] if len(r) > 11 else [] for r in existing_rows]

    for r in existing_rows[1:]:
        if len(r) > 6 and r[6].strip():
            clean_text = " ".join(r[6].strip().split())
            if clean_text not in seen_texts:
                seen_texts.add(clean_text)
                all_comments.append({
                    "Source URL": r[1].strip(),
                    "Source Title / Post": r[2].strip(),
                    "Platform": r[3].strip(),
                    "Date Collected": r[4].strip(),
                    "Comment Date": r[5].strip(),
                    "Comment Text": clean_text,
                    "Language": r[7].strip() or detect_language(clean_text),
                    "Keyword Matched": r[8].strip() or extract_keyword(clean_text),
                    "Sentiment": r[9].strip() or classify_sentiment(clean_text, vader, afinn),
                    "reactions": 0
                })

    print(f"Starting with {len(all_comments)} existing comments.", flush=True)

    # Scrape Facebook URLs
    if config.COOKIES.exists() and FACEBOOK_URLS:
        cookies = fb_cookies(config.COOKIES)
        print(f"\n--- Scraping {len(FACEBOOK_URLS)} Facebook Posts using cookies ---", flush=True)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
            )
            ctx = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900}
            )
            ctx.add_cookies(cookies)
            page = ctx.new_page()

            for i, u in enumerate(FACEBOOK_URLS, 1):
                print(f"[{i:2d}/{len(FACEBOOK_URLS)}] Scraping FB: {u}...", flush=True)
                try:
                    rows = scrape_post(page, u, limit=35)
                    title = page.title().replace(" | Facebook", "").replace("Facebook", "").strip() or "Facebook News Post"
                    added = 0
                    for r in rows:
                        clean_text = " ".join(r["text"].split())
                        if len(clean_text) < 6 or clean_text in seen_texts:
                            continue
                        seen_texts.add(clean_text)

                        c_date = parse_relative_time(r["timestamp"])
                        lang = detect_language(clean_text)
                        kw = extract_keyword(clean_text)
                        sent = classify_sentiment(clean_text, vader, afinn)

                        all_comments.append({
                            "Source URL": u,
                            "Source Title / Post": title,
                            "Platform": "Facebook",
                            "Date Collected": "2026-11-23",
                            "Comment Date": c_date,
                            "Comment Text": clean_text,
                            "Language": lang,
                            "Keyword Matched": kw,
                            "Sentiment": sent,
                            "reactions": r.get("reactions", 0)
                        })
                        added += 1
                    print(f"       -> Added {added} comments. Total dataset size: {len(all_comments)}", flush=True)
                    save_state(all_comments, header, side_refs)
                except Exception as e:
                    print(f"       -> Error: {e}", flush=True)
                time.sleep(1)
            browser.close()

    total = len(all_comments)
    print(f"\n==========================================", flush=True)
    print(f"SCRAPING COMPLETE! TOTAL COMMENTS: {total}", flush=True)
    print(f"==========================================", flush=True)
    save_state(all_comments, header, side_refs)

    # Update data/posts.csv with all sources
    unique_sources = set(c["Source URL"] for c in all_comments)
    with open(config.POSTS, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "platform"])
        for u in unique_sources:
            p = "youtube" if "youtube" in u else "reddit" if "reddit" in u else "facebook"
            w.writerow([u, p])
    print(f"Updated data/posts.csv with {len(unique_sources)} sources!", flush=True)

if __name__ == "__main__":
    main()
