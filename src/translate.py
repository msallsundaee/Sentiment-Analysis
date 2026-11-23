"""Translate comments to English (the lexicons are English-only). Throttled, cached, fails loudly."""
import json
import time

from deep_translator import GoogleTranslator

from src import config


"""Translate comments to English (the lexicons are English-only). Throttled, cached, fails loudly."""
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from deep_translator import GoogleTranslator

from src import config


def translate_one(text):
    tr = GoogleTranslator(source="auto", target="en")
    for wait in (1, 2):
        try:
            res = tr.translate(text[:4000])
            return text, res or text
        except Exception:
            time.sleep(wait)
    return text, text


def translate_all(texts):
    cache = json.loads(config.TRANSLATIONS.read_text("utf-8")) if config.TRANSLATIONS.exists() else {}
    to_translate = [t for t in texts if t not in cache]
    
    if to_translate:
        print(f"Translating {len(to_translate)} comments with concurrent workers...", flush=True)
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(translate_one, t) for t in to_translate]
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    orig, res = future.result()
                    cache[orig] = res
                except Exception:
                    pass
                if i % 30 == 0 or i == len(to_translate):
                    print(f"  Translated {i}/{len(to_translate)} comments...", flush=True)
                    config.TRANSLATIONS.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        config.TRANSLATIONS.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Translation complete! All cached.", flush=True)

    return [cache.get(t, t) for t in texts]
