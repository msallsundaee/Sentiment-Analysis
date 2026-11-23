"""YouTube comments via the official YouTube Data API v3 (needs YOUTUBE_API_KEY)."""
import re

from googleapiclient.discovery import build

from src import config


def video_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([\w-]{11})", url)
    if not m:
        raise ValueError(f"no video id in {url}")
    return m.group(1)


def fetch(url, limit):
    yt = build("youtube", "v3", developerKey=config.secret("YOUTUBE_API_KEY"), cache_discovery=False)
    rows, token = [], None
    while len(rows) < limit:
        r = yt.commentThreads().list(part="snippet,replies", videoId=video_id(url), maxResults=100,
                                     textFormat="plainText", order="relevance", pageToken=token).execute()
        for item in r["items"]:
            top = item["snippet"]["topLevelComment"]["snippet"]
            replies = [c["snippet"] for c in item.get("replies", {}).get("comments", [])]
            for s in [top] + replies:  # text, time, likes only: author fields are never read
                rows.append({"text": s["textDisplay"], "timestamp": s["publishedAt"][:10], "reactions": s["likeCount"]})
        token = r.get("nextPageToken")
        if not token:
            break
    return rows[:limit]
