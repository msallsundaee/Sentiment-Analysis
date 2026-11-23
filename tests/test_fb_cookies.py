from src import config
from src.scraper import fb_cookies
from playwright.sync_api import sync_playwright

print(f"Reading cookies from {config.COOKIES}...")
cookies = fb_cookies(config.COOKIES)
print(f"Loaded {len(cookies)} Facebook cookies! c_user and xs present.")

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
    )
    ctx = pw.chromium.launch().new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 900}
    )
    ctx.add_cookies(cookies)
    page = ctx.new_page()
    
    test_fb_url = "https://www.facebook.com/share/p/1cTsq4e6ha/"
    print(f"Testing navigation to: {test_fb_url}...")
    page.goto(test_fb_url, wait_until="domcontentloaded", timeout=25000)
    page.wait_for_timeout(4000)
    print("Page URL after redirect:", page.url)
    print("Page Title:", page.title())
    
    # Check if login or checkpoint
    if "login" in page.url or "checkpoint" in page.url:
        print("Facebook asked for login/checkpoint.")
    else:
        print("Successfully authenticated and loaded post!")
        
    browser.close()
