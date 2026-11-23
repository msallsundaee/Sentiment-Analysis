from itertools import islice
from youtube_comment_downloader import YoutubeCommentDownloader

d = YoutubeCommentDownloader()
url = "https://www.youtube.com/watch?v=X7xEuc6OsxM"
print(f"Downloading comments from {url}...")
comments = list(islice(d.get_comments_from_url(url), 10))
print(f"Fetched {len(comments)} comments!")
for c in comments:
    text = c.get("text", "").replace("\n", " ")
    print(f"- {text[:80]} | votes={c.get('votes')} | time={c.get('time')}")
