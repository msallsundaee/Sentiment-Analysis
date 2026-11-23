import csv
import re
import time
from datetime import datetime, timedelta
from itertools import islice
from youtube_comment_downloader import YoutubeCommentDownloader
from playwright.sync_api import sync_playwright

def parse_relative_time(time_str):
    """Convert relative time like '3 weeks ago', '1 month ago' to YYYY-MM-DD."""
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

def scrape_youtube(yt_urls, max_per_video=100):
    downloader = YoutubeCommentDownloader()
    results = []
    for i, url in enumerate(yt_urls, 1):
        print(f"Scraping YouTube [{i}/{len(yt_urls)}]: {url}")
        count = 0
        try:
            for c in downloader.get_comments_from_url(url):
                text = (c.get("text") or "").strip()
                if not text or len(text) < 4:
                    continue
                # remove line breaks
                clean_text = " ".join(text.split())
                c_date = parse_relative_time(c.get("time"))
                results.append({
                    "Source URL": url,
                    "Platform": "Youtube",
                    "Comment Date": c_date,
                    "Comment Text": clean_text,
                    "reactions": c.get("votes", 0)
                })
                count += 1
                if count >= max_per_video:
                    break
            print(f"  -> Got {count} comments")
        except Exception as e:
            print(f"  -> Error: {e}")
    return results

def scrape_reddit(reddit_urls, max_per_thread=100):
    results = []
    print(f"\nScraping {len(reddit_urls)} Reddit URLs with Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()
        for i, url in enumerate(reddit_urls, 1):
            if "reddit.com" not in url:
                continue
            print(f"Scraping Reddit [{i}/{len(reddit_urls)}]: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(3000)
                # scroll a bit to load comments
                for _ in range(4):
                    page.mouse.wheel(0, 1500)
                    page.wait_for_timeout(1000)
                
                # shreddit-comment or regular comment div
                comments = page.locator("shreddit-comment").all()
                count = 0
                for c in comments:
                    try:
                        slot = c.locator("div[slot='comment']")
                        if slot.count() > 0:
                            body = slot.inner_text().strip()
                        else:
                            body = c.inner_text().strip()
                        if not body or len(body) < 5 or "[deleted]" in body:
                            continue
                        clean_text = " ".join(body.split())
                        # score
                        score_attr = c.get_attribute("score") or "0"
                        results.append({
                            "Source URL": url,
                            "Platform": "Reddit",
                            "Comment Date": datetime.now().strftime("%Y-%m-%d"),
                            "Comment Text": clean_text,
                            "reactions": score_attr
                        })
                        count += 1
                        if count >= max_per_thread:
                            break
                    except Exception:
                        pass
                print(f"  -> Got {count} comments")
            except Exception as e:
                print(f"  -> Error: {e}")
            time.sleep(1)
        browser.close()
    return results

if __name__ == "__main__":
    with open("CS412 - Affective Computing Final PIT - Sheet.csv", encoding="utf-8", errors="ignore") as f:
        rows = list(csv.DictReader(f))

    urls = []
    seen = set()
    for r in rows:
        u = (r.get("Source URL") or "").strip()
        p = (r.get("Platform") or "").strip().lower()
        if u and u.startswith("http") and u not in seen and "EXAMPLE" not in u:
            seen.add(u)
            urls.append((u, p))

    yt_urls = [u for u, p in urls if "youtube" in u or "youtu.be" in u or p == "youtube"]
    reddit_urls = [u for u, p in urls if "reddit" in u or p == "reddit"]

    print(f"Found {len(yt_urls)} YouTube URLs and {len(reddit_urls)} Reddit URLs")
    yt_comments = scrape_youtube(yt_urls, max_per_video=150)
    print(f"Total YouTube comments scraped: {len(yt_comments)}")
    reddit_comments = scrape_reddit(reddit_urls, max_per_thread=100)
    print(f"Total Reddit comments scraped: {len(reddit_comments)}")
    print(f"Combined total comments: {len(yt_comments) + len(reddit_comments)}")
