from itertools import islice
from youtube_comment_downloader import YoutubeCommentDownloader
import csv

downloader = YoutubeCommentDownloader()

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

print("Checking YouTube and Reddit URLs...")
yt_urls = [u for u, p in urls if "youtube" in u or "youtu.be" in u or p == "youtube"]
reddit_urls = [u for u, p in urls if "reddit" in u or p == "reddit"]

print(f"Total YouTube URLs: {len(yt_urls)}")
print(f"Total Reddit URLs: {len(reddit_urls)}")

for i, u in enumerate(yt_urls, 1):
    try:
        sample = list(islice(downloader.get_comments_from_url(u), 15))
        print(f"[{i}/{len(yt_urls)}] YouTube: {len(sample)} comments sampled from {u}")
    except Exception as e:
        print(f"[{i}/{len(yt_urls)}] YouTube failed for {u}: {e}")
