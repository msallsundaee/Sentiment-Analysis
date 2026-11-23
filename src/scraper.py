"""Task 1: collect public Facebook comments (text, timestamp, reactions only; no names).

Read-only: it only opens public posts, expands comments and reads them.
"""
import csv
import os
import random
import sys
import time

from playwright.sync_api import sync_playwright

from src import config

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
ARTICLES = 'div[role="article"][aria-label^="Comment by"], div[role="article"][aria-label^="Reply by"]'

# Runs in the page. Drops every link's text (profile names, @mentions, URLs)
# so no personal identifier is stored.
EXTRACT_JS = r"""
() => [...document.querySelectorAll('%s')].map(a => {
  const body = [...a.querySelectorAll('div[dir="auto"]')]
    .filter(d => !d.querySelector('div[dir="auto"]'))
    .map(d => { const c = d.cloneNode(true); c.querySelectorAll('a').forEach(x => x.remove()); return c.innerText.trim(); })
    .filter(Boolean).join(' ');
  const t = ((a.getAttribute('aria-label') || '').match(/(\d+\s\w+\sago)$/) || ['', ''])[1];
  const r = [...a.querySelectorAll('[aria-label]')].map(x => x.getAttribute('aria-label')).find(s => /reaction/i.test(s)) || '';
  return {text: body, timestamp: t, reactions: (r.match(/[\d.,]+[KM]?/) || ['0'])[0]};
}).filter(c => c.text)
""" % ARTICLES


def fb_cookies(path):
    """Only facebook.com rows of a Netscape cookies.txt; the rest of the file is ignored."""
    out = {}
    for line in open(path, encoding="utf-8", errors="ignore"):
        p = line.rstrip("\n").removeprefix("#HttpOnly_").split("\t")
        if len(p) == 7 and p[0].endswith("facebook.com"):
            c = {"name": p[5], "value": p[6], "domain": p[0], "path": p[2], "secure": p[3] == "TRUE"}
            if float(p[4]) > 0:
                c["expires"] = float(p[4])
            out[p[5]] = c
    assert "c_user" in out and "xs" in out, f"no Facebook login cookies in {path}"
    return list(out.values())


def pause(a=1.5, b=3.5):
    time.sleep(random.uniform(a, b))  # slow on purpose: one human-speed reader


def click_text(page, texts):
    for t in texts:
        loc = page.get_by_text(t, exact=False)
        for i in range(loc.count()):
            try:
                loc.nth(i).click(timeout=2000)
                return True
            except Exception:
                pass
    return False


def scrape_post(page, url, limit):
    page.goto(url, wait_until="domcontentloaded")
    pause(4, 6)
    if "login" in page.url or "checkpoint" in page.url:
        sys.exit("Facebook asked for login/checkpoint. Stopping; cookies are not accepted.")
    if click_text(page, ["Most relevant", "Top comments"]):  # default sort hides most comments
        pause()
        click_text(page, ["All comments"])
        pause(3, 5)
    seen, stale = 0, 0
    while stale < 4:
        clicked = click_text(page, ["View more comments", "View previous comments", "replies", "reply"])
        arts = page.locator(ARTICLES)
        n = arts.count()
        if n:  # JS scroll: Playwright's visibility wait hangs on Facebook's virtualised list
            arts.nth(n - 1).evaluate("e => e.scrollIntoView({block: 'center'})")
        page.mouse.move(640, 500)  # wheel must be over the post modal, not the sidebar
        page.mouse.wheel(0, 2500)
        pause()
        stale = 0 if (n > seen or clicked) and n != seen else stale + 1
        seen = n
        print(f"  {n} comments loaded", end="\r")
        if n >= limit:
            break
    loc = page.get_by_role("button", name="See more", exact=True)  # expand truncated comments
    for i in range(min(loc.count(), 300)):
        try:
            loc.nth(i).click(timeout=1000)
        except Exception:
            pass
    return page.evaluate(EXTRACT_JS)[:limit]


def run(limit=400):
    urls = [u.strip() for u in open(config.POSTS) if u.strip() and not u.startswith("#")]
    if not urls:
        sys.exit(f"No URLs in {config.POSTS}")
    new = not config.RAW.exists()
    with sync_playwright() as pw, open(config.RAW, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "timestamp", "reactions", "source_post", "collected_at"])
        if new:
            w.writeheader()
        browser = pw.chromium.launch(headless=not os.environ.get("SHOW"))
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
        ctx.add_cookies(fb_cookies(config.COOKIES))
        page = ctx.new_page()
        for url in urls:
            print(url)
            try:
                rows = scrape_post(page, url, limit)
            except Exception as e:  # one bad post must not lose the rest
                print("  failed:", e)
                continue
            for r in rows:
                w.writerow({**r, "source_post": url, "collected_at": time.strftime("%Y-%m-%d")})
            f.flush()
            print(f"  saved {len(rows)} comments        ")
            pause(8, 15)
        browser.close()
