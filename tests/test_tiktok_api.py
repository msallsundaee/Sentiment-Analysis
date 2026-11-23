import json
import re
import requests

def test_tiktok_api():
    # item_id from one of the TikTok URLs: https://www.tiktok.com/@mark.anthony5328/video/7588383574479342855
    item_id = "7588383574479342855"
    api_url = f"https://www.tiktok.com/api/comment/list/?aweme_id={item_id}&count=50&cursor=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://www.tiktok.com/@mark.anthony5328/video/{item_id}"
    }
    try:
        r = requests.get(api_url, headers=headers, timeout=10)
        print("TikTok API status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            comments = data.get("comments", [])
            print(f"TikTok comments found: {len(comments)}")
            if comments:
                print("First TikTok comment:", comments[0].get("text"))
            return len(comments)
    except Exception as e:
        print("TikTok API error:", e)
    return 0

if __name__ == "__main__":
    test_tiktok_api()
