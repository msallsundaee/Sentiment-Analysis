from src import config
from src.scraper import fb_cookies
from playwright.sync_api import sync_playwright

cookies = fb_cookies(config.COOKIES)
with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
    )
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 900}
    )
    ctx.add_cookies(cookies)
    page = ctx.new_page()
    
    url = "https://www.facebook.com/share/p/1cTsq4e6ha/"
    page.goto(url, wait_until="domcontentloaded", timeout=25000)
    page.wait_for_timeout(5000)
    
    # Check page content
    page_text = page.locator("body").inner_text()
    print("Page preview (first 500 chars):")
    print(page_text[:500])
    
    # Look for comment-like text or elements
    articles = page.locator("div[role='article']").all()
    print(f"\nTotal div[role='article']: {len(articles)}")
    for a in articles:
        label = a.get_attribute("aria-label") or ""
        print(" - article aria-label:", label)
        
    browser.close()
