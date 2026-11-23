"""Task 2: cleaning, tokenization, stopword removal, lemmatization."""
import os
import re
import string

import certifi
import nltk
import pandas as pd

from src import config

# python.org builds on macOS ship without CA certs, which makes nltk.download fail
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4", "brown"]:
    assert nltk.download(pkg, quiet=True), f"NLTK download failed: {pkg}"

from nltk.corpus import stopwords  # noqa: E402  (needs the data above)
from nltk.stem import WordNetLemmatizer  # noqa: E402
from nltk.tokenize import word_tokenize  # noqa: E402

# shortcut: English stopwords only; Tagalog filler mostly disappears after translation
_STOP, _LEM = set(stopwords.words("english")), WordNetLemmatizer()


def clean(text):
    t = re.sub(r"http\S+|www\.\S+", " ", text.lower())
    t = t.translate(str.maketrans("", "", string.punctuation))
    t = re.sub(r"[^a-z\s]", " ", t)  # drops digits and emojis
    return " ".join(_LEM.lemmatize(w) for w in word_tokenize(t) if w not in _STOP and len(w) > 1)


def load_raw():
    if not config.RAW.exists() or config.RAW.stat().st_size == 0:
        raise SystemExit(
            f"Missing or empty {config.RAW}.\n"
            "Run 'python main.py scrape' first (or place comments in data/raw/raw_comments.csv)."
        )
    df = pd.read_csv(config.RAW).dropna(subset=["text"]).drop_duplicates("text")
    if len(df) == 0:
        raise SystemExit(f"No valid comments with text found in {config.RAW}.")
    return df[df.text.str.len() > 3].reset_index(drop=True)
