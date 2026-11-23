# Sentiment Analysis: High Inflation and Cost of Living

Collects public YouTube and Reddit comments (official APIs) about prices, rice, fuel and inflation, then compares
lexicon-based sentiment (VADER, TextBlob, AFINN) with TF-IDF + Logistic Regression / Naive Bayes.
The assignment is in `docs/`, the implementation plan in `docs/PLAN.md`.

## Layout

```
main.py              CLI entry point (scrape | analyze | deck)
src/
  config.py          paths and constants
  collect.py         Task 1  routes each URL to a collector, writes raw_comments.csv
  youtube.py         YouTube Data API v3 collector
  reddit.py          Reddit collector (PRAW)
  scraper.py         optional Facebook browser scraper (Playwright, opt-in)
  translate.py       Google Translate to English, cached
  preprocess.py      Task 2  cleaning, tokenization, stopwords, lemmatization
  lexicon.py         Task 3  VADER / TextBlob / AFINN, labels, chart
  ml.py              Task 4  TF-IDF + LR / NB, metrics, confusion matrix
  deck.py            Task 6  PowerPoint
data/posts.csv       INPUT: url[,platform] per row
data/raw/            raw_comments.csv (text, timestamp, reactions, platform, source)
data/processed/      cleaned_comments.csv, lexicon_results.csv, translations.json
results/             ml_results.txt, deck, figures/
secrets/.env         API keys (gitignored): YOUTUBE_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
secrets/cookies.txt  Facebook cookies, only for the opt-in scraper (gitignored, never share)
tests/               python -m tests.test_basic
```

## Run

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/playwright install chromium
# put links in data/posts.csv and API keys in secrets/.env
.venv/bin/python main.py scrape --limit 400      # add --facebook to also scrape Facebook links
.venv/bin/python main.py analyze
.venv/bin/python main.py deck --section "<section>"
```

## Ethics and limits

- Public content only, read-only, no interaction. Only text, date and like/reaction count are stored; author fields are never read.
- ML labels are the lexicon consensus (no hand labels), so ML accuracy measures imitation of the lexicons.
- Non-English comments are machine-translated before the lexicons run; this adds noise.
- YouTube and Reddit use their official APIs. Facebook has no official API for other pages' comments, so Facebook scraping is opt-in and against Facebook's terms (can lock the account).
