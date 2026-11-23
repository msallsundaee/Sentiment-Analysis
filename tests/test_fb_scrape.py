from src import config
from src.scraper import fb_cookies, scrape_post
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
    print("Scraping Facebook post:", url)
    rows = scrape_post(page, url, 30)
    print(f"\nExtracted {len(rows)} comments from Facebook!")
    for r in rows[:5]:
        print("-", r["text"][:80], f"| date={r['timestamp']} | reactions={r['reactions']}")
    browser.close()
