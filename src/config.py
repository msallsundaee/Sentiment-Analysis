"""Single source of truth for paths and constants."""
import csv
import os
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent

COOKIES = ROOT / "secrets" / "cookies.txt"          # gitignored; only facebook.com rows are read
ENV = ROOT / "secrets" / ".env"                     # gitignored; API keys, KEY=value per line
POSTS = ROOT / "data" / "posts.csv"                 # input: url[,platform] per row

RAW = ROOT / "data" / "raw" / "raw_comments.csv"                    # Task 1 deliverable
CLEANED = ROOT / "data" / "processed" / "cleaned_comments.csv"      # Task 2 deliverable
LEXICON = ROOT / "data" / "processed" / "lexicon_results.csv"       # Task 3 deliverable
TRANSLATIONS = ROOT / "data" / "processed" / "translations.json"    # translation cache

FIGURES = ROOT / "results" / "figures"
ML_METRICS = ROOT / "results" / "ml_metrics.json"                   # same numbers, for deck/charts
ML_RESULTS = ROOT / "results" / "ml_results.txt"                    # Task 4 deliverable
DECK = ROOT / "results" / "Sentiment_Analysis_Inflation.pptx"       # Task 6 deliverable

SHEET = ROOT / "data" / "comments_sheet.csv"                        # group sheet: comments + Comment Text EN

LABELS = ["negative", "neutral", "positive"]
TOPIC = "High Inflation and Cost of Living"

for d in (RAW.parent, CLEANED.parent, FIGURES):
    d.mkdir(parents=True, exist_ok=True)


def secret(name, required=True):
    """API key from the environment or secrets/.env."""
    if name in os.environ:
        return os.environ[name]
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            k, _, v = line.partition("=")
            if k.strip() == name and v.strip():
                return v.strip().strip("\"'")
    if required:
        raise SystemExit(f"Missing {name}: add it to {ENV}")
    return None


def platform_of(url):
    host = urlparse(url).netloc.lower()
    for key, name in [("youtube.com", "youtube"), ("youtu.be", "youtube"), ("reddit.com", "reddit"),
                      ("facebook.com", "facebook"), ("fb.com", "facebook")]:
        if host.endswith(key):
            return name
    return "unsupported"


def read_urls():
    """URLs from data/posts.csv (a `url` column, else the first column). Header optional."""
    rows = [r for r in csv.reader(open(POSTS, encoding="utf-8-sig")) if r and not r[0].lstrip().startswith("#")]
    col = rows[0].index("url") if rows and "url" in [c.strip().lower() for c in rows[0]] else 0
    return [r[col].strip() for r in rows if r[col].strip().startswith("http")]
