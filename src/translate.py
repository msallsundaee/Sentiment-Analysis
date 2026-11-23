"""Translate comments to English (the lexicons are English-only). Throttled, cached, fails loudly."""
import json
import time

import requests

from src import config


def _official(texts, key):
    """Google Cloud Translation API v2 (official, needs GOOGLE_TRANSLATE_API_KEY). 100 texts per call."""
    out = {}
    for i in range(0, len(texts), 100):
        chunk = texts[i:i + 100]
        r = requests.post("https://translation.googleapis.com/language/translate/v2", params={"key": key},
                          json={"q": [t[:4000] for t in chunk], "target": "en", "format": "text"}, timeout=60)
        r.raise_for_status()
        for t, tr in zip(chunk, r.json()["data"]["translations"]):
            out[t] = tr["translatedText"] or t
        print(f"  {min(i + 100, len(texts))}/{len(texts)}", flush=True)
    return out


def _free(text):
    """Unofficial Google endpoint (no key). shortcut: may be rate-limited or change without notice;
    set GOOGLE_TRANSLATE_API_KEY to use the official API instead."""
    r = requests.get("https://translate.googleapis.com/translate_a/single", timeout=30,
                     params={"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": text[:4000]})
    r.raise_for_status()
    return "".join(seg[0] for seg in r.json()[0] if seg[0])


def translate_all(texts):
    """English text passes through unchanged (source=auto). Failed rows are never cached,
    so a rerun retries only them; the run aborts rather than score untranslated text."""
    cache = json.loads(config.TRANSLATIONS.read_text("utf-8")) if config.TRANSLATIONS.exists() else {}
    todo = [t for t in dict.fromkeys(texts) if t not in cache]
    failed = 0
    if todo:
        print(f"Translating {len(todo)} comments...", flush=True)
    key = config.secret("GOOGLE_TRANSLATE_API_KEY", required=False)
    if todo and key:
        cache.update(_official(todo, key))
        todo = []
    for i, t in enumerate(todo, 1):
        for wait in (5, 30):  # back off when Google rate-limits
            try:
                time.sleep(0.5)  # sequential + throttled: parallel workers trip the rate limit
                cache[t] = _free(t) or t
                break
            except Exception:
                time.sleep(wait)
        else:
            failed += 1
            if failed >= 5 and failed == i:  # blocked from the start: stop instead of waiting hours
                break
        if i % 50 == 0:
            print(f"  {i}/{len(todo)}", flush=True)
            config.TRANSLATIONS.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    config.TRANSLATIONS.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    missing = sum(t not in cache for t in texts)
    if missing:
        raise SystemExit(f"{missing} translations failed (Google rate limit?). Nothing was scored. "
                         "Wait and rerun (finished ones are cached), or set GOOGLE_TRANSLATE_API_KEY in secrets/.env.")
    return [cache[t] for t in texts]
