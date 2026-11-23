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
    
    comments = page.evaluate("""() => {
        const arts = [...document.querySelectorAll('div[role="article"]')].filter(a => {
            const lbl = a.getAttribute('aria-label') || '';
            return /comment|reply|sagot/i.test(lbl);
        });
        return arts.map(a => {
            const body = [...a.querySelectorAll('div[dir="auto"]')]
                .filter(d => !d.querySelector('div[dir="auto"]'))
                .map(d => {
                    const c = d.cloneNode(true);
                    c.querySelectorAll('a').forEach(x => x.remove());
                    return c.innerText.trim();
                })
                .filter(Boolean).join(' ');
            const lbl = a.getAttribute('aria-label') || '';
            return {text: body, label: lbl};
        }).filter(x => x.text);
    }""")
    
    print(f"Extracted {len(comments)} comments from Facebook!")
    for c in comments:
        print("->", c["text"][:100], "||", c["label"])
        
    browser.close()
