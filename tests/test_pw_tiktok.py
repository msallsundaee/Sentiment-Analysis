from playwright.sync_api import sync_playwright

def test_tiktok():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()
        url = "https://www.tiktok.com/@gmanews/video/7704671362719255809"
        print("Loading TikTok:", url)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(4000)
            print("Title:", page.title())
            comments = page.locator("[data-e2e='comment-level-1']").all()
            print("Comments found:", len(comments))
            if comments:
                print("First comment:", comments[0].inner_text()[:100])
        except Exception as e:
            print("TikTok error:", e)
        browser.close()

if __name__ == "__main__":
    test_tiktok()
