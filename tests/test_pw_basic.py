from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
    )
    page = browser.new_page()
    page.goto("https://example.com")
    print("Example title:", page.title())
    browser.close()
    print("Browser test succeeded!")
