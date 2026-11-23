import json
import urllib.request
import requests

def test_reddit():
    url = "https://www.reddit.com/r/Philippines/comments/1xo7lfe/inflation_rises_to_78_in_october/.json"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print("Reddit HTTP status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            title = data[0]["data"]["children"][0]["data"]["title"]
            comments = data[1]["data"]["children"]
            print(f"Reddit post title: {title}")
            print(f"Reddit top-level comments count: {len(comments)}")
            if comments:
                first_body = comments[0]["data"].get("body", "")[:100]
                print(f"Sample comment: {first_body}")
            return True
    except Exception as e:
        print("Reddit test failed:", e)
    return False

def test_youtube():
    # test using yt-dlp or youtube_comment_downloader if available, or playwright
    url = "https://www.youtube.com/watch?v=RAKUaSAA0pE"
    import subprocess
    try:
        res = subprocess.run(
            ["yt-dlp", "--skip-download", "--write-comments", "--dump-json", url],
            capture_output=True, text=True, timeout=15
        )
        print("yt-dlp return code:", res.returncode)
        if res.returncode == 0:
            info = json.loads(res.stdout.splitlines()[0])
            comments = info.get("comments", [])
            print(f"YouTube title: {info.get('title')}")
            print(f"YouTube comments count: {len(comments)}")
            return True
        else:
            print("yt-dlp stderr:", res.stderr[:200])
    except Exception as e:
        print("YouTube test failed:", e)
    return False

if __name__ == "__main__":
    print("Testing Reddit...")
    test_reddit()
    print("\nTesting YouTube...")
    test_youtube()
