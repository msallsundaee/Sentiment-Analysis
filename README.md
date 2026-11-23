# Sentiment Analysis: High Inflation and Cost of Living

CS 413 – CS Elective 2 (Affective Computing), Week 14 final project.
Group: Bea, Jesreal, Raphael, Gil, Angel. 

Collects public Facebook news-page comments about prices, rice, fuel and inflation, then compares
lexicon-based sentiment (VADER, TextBlob, AFINN) with TF-IDF + Logistic Regression / Naive Bayes.
The assignment is in `docs/`, the implementation plan in `docs/PLAN.md`.

## Layout

```
main.py              CLI entry point (scrape | analyze | deck)
src/
  config.py          paths and constants
  scraper.py         Task 1  Facebook comment collection (Playwright)
  translate.py       Google Translate to English, cached
  preprocess.py      Task 2  cleaning, tokenization, stopwords, lemmatization
  lexicon.py         Task 3  VADER / TextBlob / AFINN, labels, chart
  ml.py              Task 4  TF-IDF + LR / NB, metrics, confusion matrix
  deck.py            Task 6  PowerPoint
data/posts.txt       INPUT: one public post URL per line
data/raw/            raw_comments.csv
data/processed/      cleaned_comments.csv, lexicon_results.csv, translations.json
results/             ml_results.txt, deck, figures/
secrets/cookies.txt  Facebook session cookies (gitignored, never share)
tests/               python -m tests.test_basic
```

## Run

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/playwright install chromium
# put post URLs in data/posts.txt, cookies in secrets/cookies.txt
.venv/bin/python main.py scrape --limit 400
.venv/bin/python main.py analyze
.venv/bin/python main.py deck --section "<section>"
```

## Ethics and limits

- Public news-page posts only, read-only, no interaction. Only text, relative timestamp and reaction count are stored.
- ML labels are the lexicon consensus (no hand labels), so ML accuracy measures imitation of the lexicons.
- Non-English comments are machine-translated before the lexicons run; this adds noise.
- Scraping while logged in is against Facebook's terms and can lock the account.
