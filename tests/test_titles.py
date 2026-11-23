import re
import urllib.request
import requests

def get_page_title(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode("utf-8", errors="ignore")
            m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
            if m:
                t = m.group(1).replace(" - YouTube", "").replace(" : r/Philippines", "").strip()
                return t
    except Exception:
        pass
    return ""

test_urls = [
    "https://www.youtube.com/watch?v=RAKUaSAA0pE",
    "https://www.youtube.com/watch?v=QQO6rjhxf3M",
    "https://www.reddit.com/r/Philippines/comments/1xo7lfe/inflation_rises_to_78_in_october/"
]

for u in test_urls:
    print(u, "->", get_page_title(u))
