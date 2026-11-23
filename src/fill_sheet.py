"""Scrape public comments from YouTube and Reddit URLs in the sheet,
classify language, keywords, and sentiment, and populate the CSV sheet.
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
    
    cebuano_count = len(tokens & CEBUANO_WORDS)
    if cebuano_count >= 2:
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
        with urllib.request.urlopen(req, timeout=5) as response:
            page_html = response.read().decode("utf-8", errors="ignore")
            m = re.search(r"<title>(.*?)</title>", page_html, re.IGNORECASE)
            if m:
                t = html.unescape(m.group(1)).replace(" - YouTube", "").replace(" : r/Philippines", "").strip()
                return t
    except Exception:
        pass
    # fallback from url slug
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
    # Lexicon scoring
    v_score = vader.polarity_scores(text)["compound"]
    tb_score = TextBlob(text).sentiment.polarity
    a_score = afinn.score(text)
    
    v_lbl = "Positive" if v_score >= 0.05 else "Negative" if v_score <= -0.05 else "Neutral"
    tb_lbl = "Positive" if tb_score >= 0.05 else "Negative" if tb_score <= -0.05 else "Neutral"
    a_lbl = "Positive" if a_score >= 1 else "Negative" if a_score <= -1 else "Neutral"
    
    votes = [v_lbl, tb_lbl, a_lbl]
    top = max(set(votes), key=votes.count)
    if votes.count(top) > 1:
        return top
    return "Neutral"

def run_scrape():
    vader = SentimentIntensityAnalyzer()
    afinn = Afinn()
    downloader = YoutubeCommentDownloader()
    
    with open("data/comments_sheet.csv", encoding="utf-8", errors="ignore") as f:
        existing_rows = list(csv.reader(f))
    
    header = existing_rows[0]
    # Keep dropdown reference columns from rows 2-10
    side_refs = [r[11:] if len(r) > 11 else [] for r in existing_rows]
    
    urls = []
    seen = set()
    for r in existing_rows[1:]:
        if len(r) > 1:
            u = r[1].strip()
            p = r[3].strip() if len(r) > 3 else ""
            if u and u.startswith("http") and u not in seen and "EXAMPLE" not in u:
                seen.add(u)
                urls.append((u, p))
    
    yt_urls = [u for u, p in urls if "youtube" in u or "youtu.be" in u or p.lower() == "youtube"]
    reddit_urls = [u for u, p in urls if "reddit" in u or p.lower() == "reddit"]
    
    print(f"Scraping from {len(yt_urls)} YouTube videos and {len(reddit_urls)} Reddit posts...")
    
    all_comments = []
    seen_texts = set()
    
    # 1. Scrape YouTube
    for i, u in enumerate(yt_urls, 1):
        title = get_page_title(u)
        print(f"[{i}/{len(yt_urls)}] YouTube: {title[:50]}...")
        count = 0
        try:
            for c in downloader.get_comments_from_url(u):
                raw_text = (c.get("text") or "").strip()
                clean_text = " ".join(raw_text.split())
                if len(clean_text) < 6 or clean_text in seen_texts:
                    continue
                seen_texts.add(clean_text)
                
                c_date = parse_relative_time(c.get("time"))
                reactions = c.get("votes", 0)
                lang = detect_language(clean_text)
                kw = extract_keyword(clean_text)
                sent = classify_sentiment(clean_text, vader, afinn)
                
                all_comments.append({
                    "Source URL": u,
                    "Source Title / Post": title,
                    "Platform": "Youtube",
                    "Date Collected": "2026-11-23",
                    "Comment Date": c_date,
                    "Comment Text": clean_text,
                    "Language": lang,
                    "Keyword Matched": kw,
                    "Sentiment": sent,
                    "reactions": reactions
                })
                count += 1
                if len(all_comments) >= 900:  # reserve room for reddit comments
                    break
            print(f"   -> Collected {count} comments")
        except Exception as e:
            print(f"   -> Error: {e}")
            
    # 2. Scrape Reddit
    print(f"\nScraping Reddit threads...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()
        for i, u in enumerate(reddit_urls, 1):
            if "reddit.com" not in u:
                continue
            title = u.rstrip("/").split("/")[-1].replace("_", " ").replace("-", " ").title()
            print(f"[{i}/{len(reddit_urls)}] Reddit: {title[:50]}...")
            try:
                page.goto(u, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(3000)
                for _ in range(5):
                    page.mouse.wheel(0, 1500)
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
                        clean_text = " ".join(body.split())
                        if len(clean_text) < 6 or "[deleted]" in clean_text or clean_text in seen_texts:
                            continue
                        seen_texts.add(clean_text)
                        
                        score = c.get_attribute("score") or "0"
                        lang = detect_language(clean_text)
                        kw = extract_keyword(clean_text)
                        sent = classify_sentiment(clean_text, vader, afinn)
                        
                        all_comments.append({
                            "Source URL": u,
                            "Source Title / Post": title,
                            "Platform": "Reddit",
                            "Date Collected": "2026-11-23",
                            "Comment Date": datetime.now().strftime("%Y-%m-%d"),
                            "Comment Text": clean_text,
                            "Language": lang,
                            "Keyword Matched": kw,
                            "Sentiment": sent,
                            "reactions": score
                        })
                        count += 1
                        if len(all_comments) >= 1000:
                            break
                    except Exception:
                        pass
                print(f"   -> Collected {count} comments")
            except Exception as e:
                print(f"   -> Error: {e}")
        browser.close()

    print(f"\nTotal scraped comments ready: {len(all_comments)}")
    
    # 3. Write out to data/comments_sheet.csv
    # Fill up to 1000 comments
    output_rows = [header]
    for idx in range(1000):
        cid = f"C{idx+1:04d}"
        side = side_refs[idx+1] if (idx + 1) < len(side_refs) else []
        if idx < len(all_comments):
            c = all_comments[idx]
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
                "" # Notes
            ]
        else:
            main_cols = [cid, "", "", "", "", "", "", "", "", "", ""]
        
        full_row = main_cols + side
        output_rows.append(full_row)
        
    with open("data/comments_sheet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerows(output_rows)
    print("Updated data/comments_sheet.csv with 1000 rows!")
    
    # 4. Write data/raw/raw_comments.csv for main.py analyze
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
    print(f"Updated {config.RAW} with {len(all_comments)} comments!")

    # 5. Update data/posts.csv
    unique_sources = set(c["Source URL"] for c in all_comments)
    with open(config.POSTS, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "platform"])
        for u in unique_sources:
            p = "youtube" if "youtube" in u else "reddit"
            w.writerow([u, p])
    print(f"Updated {config.POSTS} with {len(unique_sources)} sources!")

if __name__ == "__main__":
    run_scrape()
