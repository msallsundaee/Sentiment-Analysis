import requests

def test_reddit():
    url = "https://www.reddit.com/r/Philippines/comments/1xo7lfe/inflation_rises_to_78_in_october/.json"
    headers_list = [
        {"User-Agent": "script:sentiment-analysis-school-project:v1.0 (by /u/Educational_Pitch)"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"},
        {"User-Agent": "android:myredditapp:v1.0"}
    ]
    for i, h in enumerate(headers_list):
        try:
            r = requests.get(url, headers=h, timeout=10)
            print(f"Header {i} status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                comments = data[1]["data"]["children"]
                print(f"Success! Found {len(comments)} comments")
                for c in comments[:3]:
                    body = c["data"].get("body", "")
                    print(" -", body[:80])
                return True
        except Exception as e:
            print(f"Header {i} error:", e)

    # Also test old.reddit.com
    try:
        url_old = "https://old.reddit.com/r/Philippines/comments/1xo7lfe/inflation_rises_to_78_in_october/.json"
        r = requests.get(url_old, headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}, timeout=10)
        print(f"old.reddit.com status: {r.status_code}")
        if r.status_code == 200:
            print("old.reddit success!")
    except Exception as e:
        print("old.reddit error:", e)

    return False

if __name__ == "__main__":
    test_reddit()
