from playwright.sync_api import sync_playwright

def test_playwright_scrapes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 1. Test Reddit
        print("Testing Reddit via Playwright...")
        try:
            page.goto("https://www.reddit.com/r/Philippines/comments/1xo7lfe/inflation_rises_to_78_in_october/", timeout=20000)
            page.wait_for_timeout(3000)
            title = page.title()
            print("Reddit page title:", title)
            # Find comments
            comments = page.locator("shreddit-comment").all()
            print(f"Found {len(comments)} shreddit-comment elements")
            if comments:
                text = comments[0].locator("div[slot='comment']").inner_text()
                print("Sample comment:", text[:100])
        except Exception as e:
            print("Reddit error:", e)

        # 2. Test YouTube
        print("\nTesting YouTube via Playwright...")
        try:
            page.goto("https://www.youtube.com/watch?v=RAKUaSAA0pE", timeout=20000)
            page.wait_for_timeout(3000)
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(3000)
            title = page.title()
            print("YouTube page title:", title)
            comments = page.locator("#content-text").all()
            print(f"Found {len(comments)} YouTube comments")
            if comments:
                print("Sample YouTube comment:", comments[0].inner_text()[:100])
        except Exception as e:
            print("YouTube error:", e)

        browser.close()

if __name__ == "__main__":
    test_playwright_scrapes()
