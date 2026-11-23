# Sentiment Analysis: High Inflation and Cost of Living

Analyses public YouTube, Facebook and Reddit comments about prices, rice, fuel and inflation, then compares
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
data/comments_sheet.csv  group sheet: all comments + `Comment Text EN` (=GOOGLETRANSLATE in Google Sheets)
data/raw/            raw_comments.csv (text, timestamp, reactions, platform, source)
data/processed/      cleaned_comments.csv, lexicon_results.csv, translations.json
results/             ml_results.txt, deck, figures/
secrets/.env         API keys (gitignored): YOUTUBE_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
secrets/cookies.txt  Facebook cookies, only for the opt-in scraper (gitignored, never share)
tests/               python -m tests.test_basic
```

## Run

### Setup Virtual Environment

**Windows (PowerShell):**
```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\playwright install chromium
```

**macOS / Linux:**
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
```

### Running the Tasks

1. **Quick Test / Seed Data (Optional):**
   ```powershell
   # Windows:
   .\.venv\Scripts\python -m src.seed_data
   # macOS/Linux:
   .venv/bin/python -m src.seed_data
   ```

2. **Collection (Task 1):**
   Put links in `data/posts.csv` and API keys in `secrets/.env`.
   ```powershell
   # Windows:
   .\.venv\Scripts\python main.py scrape --limit 400      # add --facebook to also scrape Facebook links
   # macOS/Linux:
   .venv/bin/python main.py scrape --limit 400
   ```

3. **Analysis (Tasks 2–4):**
   ```powershell
   # Windows:
   .\.venv\Scripts\python main.py analyze
   # macOS/Linux:
   .venv/bin/python main.py analyze
   ```

4. **Generate Presentation Deck (Task 6):**
   ```powershell
   # Windows:
   .\.venv\Scripts\python main.py deck --section "CS413"
   # macOS/Linux:
   .venv/bin/python main.py deck --section "CS413"
   ```

5. **Run Tests:**
   ```powershell
   # Windows:
   .\.venv\Scripts\python -m tests.test_basic
   # macOS/Linux:
   .venv/bin/python -m tests.test_basic
   ```

## Ethics and limits

- Public content only, read-only, no interaction. Only text, date and like/reaction count are stored; author fields are never read.
- ML labels are the lexicon consensus (no hand labels), so ML accuracy measures imitation of the lexicons.
- Non-English comments are machine-translated before the lexicons run; this adds noise.
- How the current dataset was collected: YouTube with `youtube-comment-downloader`, Reddit and Facebook with a Playwright browser (the one-off `src/scrape_*.py` / `src/master_scrape.py` scripts). These are not official APIs. `main.py scrape` is the official-API route (YouTube Data API, PRAW) and needs keys in `secrets/.env`.
- Facebook has no official API for other pages' comments; scraping it while logged in is against Facebook's terms and can lock the account.
- `@handles` are stripped from every comment (`main.py import-sheet`). One YouTube video supplies about 45% of the comments, and many comments react to the video rather than to prices.
- Translation uses the official Google Cloud Translation API when `GOOGLE_TRANSLATE_API_KEY` is set, else the free endpoint; the run aborts if translation fails rather than scoring untranslated text.
