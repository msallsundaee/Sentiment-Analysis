import html
import re
import urllib.request
from youtube_comment_downloader import YoutubeCommentDownloader

def find_related_videos():
    query = "philippines+inflation+presyo+ng+bilihin+gma+news"
    url = f"https://www.youtube.com/results?search_query={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        page = resp.read().decode("utf-8", errors="ignore")

    vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', page)
    seen = set()
    unique = []
    for v in vids:
        if v not in seen:
            seen.add(v)
            unique.append(f"https://www.youtube.com/watch?v={v}")

    print(f"Found {len(unique)} candidate videos:")
    downloader = YoutubeCommentDownloader()
    valid_news = []
    for u in unique[:10]:
        try:
            req_v = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req_v, timeout=6) as resp_v:
                v_html = resp_v.read().decode("utf-8", errors="ignore")
                m = re.search(r"<title>(.*?)</title>", v_html)
                title = html.unescape(m.group(1)).replace(" - YouTube", "") if m else ""
            print(f"Checking: {title[:60]}... ({u})")
            if any(k in title.lower() for k in ["inflation", "presyo", "bilihin", "bigas", "gastos", "price"]):
                valid_news.append((u, title))
                print(f"  -> MATCHED: {title[:60]}")
        except Exception as e:
            pass
    return valid_news

if __name__ == "__main__":
    matches = find_related_videos()
    print(f"\nTotal matched news videos: {len(matches)}")
    for u, t in matches:
        print(" ", u, "::", t)
