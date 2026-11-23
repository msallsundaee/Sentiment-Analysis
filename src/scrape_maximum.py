"""Maximal scraper for Philippine inflation & cost of living comments.
Collects from all sheet YouTube & Reddit URLs plus top official Philippine news broadcasts.
Saves all comments to CS412 - Affective Computing Final PIT - Sheet.csv and data/raw/raw_comments.csv.
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
            html_content = resp.read().decode("utf-8", errors="ignore")
            m = re.search(r"<title>(.*?)</title>", html_content, re.IGNORECASE)
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
    m = re.search(r"(\d+)\s*(second|minute|hour|day|week|month|year)", s)
    if not m:
        return now.strftime("%Y-%m-%d")
    val, unit = int(m.group(1)), m.group(2)
    if "second" in unit or "minute" in unit or "hour" in unit:
        dt = now
    elif "day" in unit:
        dt = now - timedelta(days=val)
    elif "week" in unit:
        dt = now - timedelta(days=val * 7)
    elif "month" in unit:
        dt = now - timedelta(days=val * 30)
    elif "year" in unit:
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

def main():
    vader = SentimentIntensityAnalyzer()
    afinn = Afinn()
    downloader = YoutubeCommentDownloader()

    with open("CS412 - Affective Computing Final PIT - Sheet.csv", encoding="utf-8-sig", errors="ignore") as f:
        existing_rows = list(csv.reader(f))

    header = existing_rows[0]
    side_refs = [r[11:] if len(r) > 11 else [] for r in existing_rows]

    # Sheet URLs
    sheet_yt = []
    sheet_reddit = []
    seen = set()
    for r in existing_rows[1:]:
        if len(r) > 1:
            u = r[1].strip()
            p = r[3].strip().lower() if len(r) > 3 else ""
            if u and u.startswith("http") and u not in seen and "EXAMPLE" not in u:
                seen.add(u)
                if "youtube" in u or "youtu.be" in u or p == "youtube":
                    sheet_yt.append(u)
                elif "reddit" in u or p == "reddit":
                    sheet_reddit.append(u)

    # Additional matched official news broadcasts on Philippine inflation / bilihin
    extra_news_yt = [
        "https://www.youtube.com/watch?v=s7ebnJQ7AG8",  # 24 Oras: Inflation speeds up to 7.2%
        "https://www.youtube.com/watch?v=2ZnWP9GrHCo",  # Balitanghali: PSA Inflation rate
        "https://www.youtube.com/watch?v=ZWLg1Sj9dLg",  # Unang Balita: Inflation rate nitong Oktubre tumaas sa 7.8%
        "https://www.youtube.com/watch?v=NhvR5RTiw-0",  # Balitanghali: Inflation eases to 6.4%
        "https://www.youtube.com/watch?v=PjARE6wkzeI",  # 24 Oras: Bilis ng pagmahal ng bilihin at serbisyo
        "https://www.youtube.com/watch?v=9EoLbGOuJ8Q",  # Balitanghali: Inflation eases to 6.8%
        "https://www.youtube.com/watch?v=_dgOT2pmyJg",  # GMA Integrated News: Inflation rate umakyat
        "https://www.youtube.com/watch?v=Z8jw421moQM",  # Balitanghali: Bumilis sa 2% ang inflation
    ]

    all_yt = sheet_yt + [u for u in extra_news_yt if u not in seen]
    all_reddit = sheet_reddit

    print(f"Total YouTube targets: {len(all_yt)}")
    print(f"Total Reddit targets: {len(all_reddit)}")

    all_comments = []
    seen_texts = set()

    # 1. Scrape YouTube (NO arbitrary cap per video)
    print("\n--- Scraping YouTube Videos ---")
    for i, u in enumerate(all_yt, 1):
        title = get_page_title(u)
        print(f"[{i}/{len(all_yt)}] {title[:55]}...")
        count = 0
        try:
            for c in downloader.get_comments_from_url(u):
                raw = (c.get("text") or "").strip()
                clean = " ".join(raw.split())
                if len(clean) < 6 or clean in seen_texts:
                    continue
                seen_texts.add(clean)

                c_date = parse_relative_time(c.get("time"))
                reactions = c.get("votes", 0)
                lang = detect_language(clean)
                kw = extract_keyword(clean)
                sent = classify_sentiment(clean, vader, afinn)

                all_comments.append({
                    "Source URL": u,
                    "Source Title / Post": title,
                    "Platform": "Youtube",
                    "Date Collected": "2026-11-23",
                    "Comment Date": c_date,
                    "Comment Text": clean,
                    "Language": lang,
                    "Keyword Matched": kw,
                    "Sentiment": sent,
                    "reactions": reactions
                })
                count += 1
            print(f"  -> Extracted {count} comments")
        except Exception as e:
            print(f"  -> Error: {e}")

    # 2. Scrape Reddit with Playwright deep scroll
    print("\n--- Scraping Reddit Threads ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()
        for i, u in enumerate(all_reddit, 1):
            if "reddit.com" not in u:
                continue
            title = u.rstrip("/").split("/")[-1].replace("_", " ").replace("-", " ").title()
            print(f"[{i}/{len(all_reddit)}] {title[:55]}...")
            try:
                page.goto(u, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(3000)
                # deep scroll
                for _ in range(8):
                    page.mouse.wheel(0, 2000)
                    page.wait_for_timeout(800)

                page_title = page.title().replace(" : r/Philippines", "").replace(" - Reddit", "").strip()
                if page_title and "Reddit" not in page_title:
                    title = page_title

                comments = page.locator("shreddit-comment").all()
                count = 0
                for c in comments:
                    try:
                        slot = c.locator("div[slot='comment']")
                        body = slot.inner_text().strip() if slot.count() > 0 else c.inner_text().strip()
                        clean = " ".join(body.split())
                        if len(clean) < 6 or "[deleted]" in clean or clean in seen_texts:
                            continue
                        seen_texts.add(clean)

                        score = c.get_attribute("score") or "0"
                        lang = detect_language(clean)
                        kw = extract_keyword(clean)
                        sent = classify_sentiment(clean, vader, afinn)

                        all_comments.append({
                            "Source URL": u,
                            "Source Title / Post": title,
                            "Platform": "Reddit",
                            "Date Collected": "2026-11-23",
                            "Comment Date": datetime.now().strftime("%Y-%m-%d"),
                            "Comment Text": clean,
                            "Language": lang,
                            "Keyword Matched": kw,
                            "Sentiment": sent,
                            "reactions": score
                        })
                        count += 1
                    except Exception:
                        pass
                print(f"  -> Extracted {count} comments")
            except Exception as e:
                print(f"  -> Error: {e}")
        browser.close()

    total = len(all_comments)
    print(f"\n==========================================")
    print(f"TOTAL UNIQUE COMMENTS COLLECTED: {total}")
    print(f"==========================================")

    # 3. Write out to CS412 - Affective Computing Final PIT - Sheet.csv
    # Save every comment collected
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
            ""  # Notes
        ]
        output_rows.append(main_cols + side)

    with open("CS412 - Affective Computing Final PIT - Sheet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerows(output_rows)
    print(f"Updated CS412 - Affective Computing Final PIT - Sheet.csv with {total} comments!")

    # 4. Write data/raw/raw_comments.csv
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
    print(f"Updated {config.RAW} with {total} comments!")

    # 5. Write data/posts.csv
    unique_sources = set(c["Source URL"] for c in all_comments)
    with open(config.POSTS, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "platform"])
        for u in unique_sources:
            p = "youtube" if "youtube" in u else "reddit"
            w.writerow([u, p])
    print(f"Updated {config.POSTS} with {len(unique_sources)} source posts!")

if __name__ == "__main__":
    main()
