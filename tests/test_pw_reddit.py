from playwright.sync_api import sync_playwright

def test_reddit():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()
        url = "https://www.reddit.com/r/Philippines/comments/1xo7lfe/inflation_rises_to_78_in_october/"
        print("Loading Reddit post:", url)
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        print("Title:", page.title())
        comments = page.locator("shreddit-comment").all()
        print(f"shreddit-comment count: {len(comments)}")
        for c in comments[:5]:
            try:
                body = c.locator("div[slot='comment']").inner_text().strip()
                score = c.get_attribute("score")
                print(f"Comment (score={score}): {body[:70]}")
            except Exception as e:
                pass
        browser.close()

if __name__ == "__main__":
    test_reddit()
