"""Translate comments to English (the lexicons are English-only). Throttled, cached, fails loudly."""
import json
import time

from deep_translator import GoogleTranslator

from src import config


def translate_all(texts):
    cache = json.loads(config.TRANSLATIONS.read_text()) if config.TRANSLATIONS.exists() else {}
    tr, failed, out = GoogleTranslator(source="auto", target="en"), set(), []
    for t in texts:
        if t not in cache:
            for wait in (2, 10, 30, 60):  # back off when Google rate-limits
                try:
                    time.sleep(0.4)
                    cache[t] = tr.translate(t[:4000]) or t
                    break
                except Exception:
                    time.sleep(wait)
            else:
                failed.add(t)  # keep the original text, but don't cache it so a rerun retries
        out.append(cache.get(t, t))
    config.TRANSLATIONS.write_text(json.dumps(cache))
    assert len(failed) < 0.1 * len(texts), f"{len(failed)} translations failed; wait and rerun (cache keeps the rest)"
    return out
