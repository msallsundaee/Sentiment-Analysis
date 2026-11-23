from youtube_comment_downloader import YoutubeCommentDownloader
import csv

downloader = YoutubeCommentDownloader()
with open("CS412 - Affective Computing Final PIT - Sheet.csv", encoding="utf-8", errors="ignore") as f:
    rows = list(csv.DictReader(f))

urls = []
seen = set()
for r in rows:
    u = (r.get("Source URL") or "").strip()
    if ("youtube.com" in u or "youtu.be" in u) and u not in seen and "EXAMPLE" not in u:
        seen.add(u)
        urls.append(u)

total = 0
for u in urls:
    count = 0
    try:
        for c in downloader.get_comments_from_url(u):
            count += 1
            if count >= 300:
                break
        print(f"{u}: {count} comments")
        total += count
    except Exception as e:
        print(f"{u}: error {e}")

print(f"Total YouTube comments available (capped at 300/vid): {total}")
