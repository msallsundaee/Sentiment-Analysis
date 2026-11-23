import tempfile
from pathlib import Path

"""Run: .venv/bin/python -m tests.test_basic"""
from src.lexicon import consensus, to_label
from src.preprocess import clean
from src.scraper import fb_cookies


def test_clean():
    assert clean("Check https://x.com NOW!!! 20 pesos 😡 rices") == "check peso rice"


def test_labels():
    assert to_label(0.5, 0.05) == "positive" and to_label(-0.5, 0.05) == "negative" and to_label(0, 0.05) == "neutral"
    assert consensus(["positive", "positive", "negative"]) == "positive"
    assert consensus(["positive", "neutral", "negative"]) == "neutral"


def test_cookies_only_facebook(tmp_path=None):
    if tmp_path is None:
        tmp_path = str(Path(tempfile.gettempdir()) / "_cookies_test.txt")
    rows = [".facebook.com\tTRUE\t/\tTRUE\t0\tc_user\t1", ".facebook.com\tTRUE\t/\tTRUE\t0\txs\t2",
            ".google.com\tTRUE\t/\tTRUE\t0\tSID\t3"]
    open(tmp_path, "w").write("\n".join(rows))
    assert {c["domain"] for c in fb_cookies(tmp_path)} == {".facebook.com"}


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
