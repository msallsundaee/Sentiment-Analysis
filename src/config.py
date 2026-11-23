"""Single source of truth for paths and constants."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

COOKIES = ROOT / "secrets" / "cookies.txt"          # gitignored; only facebook.com rows are read
POSTS = ROOT / "data" / "posts.txt"                 # input: one post URL per line

RAW = ROOT / "data" / "raw" / "raw_comments.csv"                    # Task 1 deliverable
CLEANED = ROOT / "data" / "processed" / "cleaned_comments.csv"      # Task 2 deliverable
LEXICON = ROOT / "data" / "processed" / "lexicon_results.csv"       # Task 3 deliverable
TRANSLATIONS = ROOT / "data" / "processed" / "translations.json"    # translation cache

FIGURES = ROOT / "results" / "figures"
ML_RESULTS = ROOT / "results" / "ml_results.txt"                    # Task 4 deliverable
DECK = ROOT / "results" / "Sentiment_Analysis_Inflation.pptx"       # Task 6 deliverable

LABELS = ["negative", "neutral", "positive"]
TOPIC = "High Inflation and Cost of Living"

for d in (RAW.parent, CLEANED.parent, FIGURES):
    d.mkdir(parents=True, exist_ok=True)
