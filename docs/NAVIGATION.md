# Navigating this repo

A guide: what each file is, how the data flows, and where to look.
For setup and run commands see the top-level `README.md`.

## What this project is

Sentiment analysis of public comments on **High Inflation and Cost of Living** in the Philippines
(CS 413 – Affective Computing, Week 14 final project). We collected 1,510 comments from YouTube,
Facebook and Reddit, then compared lexicon-based sentiment (VADER, TextBlob, AFINN) with
TF-IDF + Logistic Regression / Naive Bayes.

## Start here (by what you need)

| I want to... | Open |
|---|---|
| Present or submit | `results/Sentiment_Analysis_Inflation.pptx` (Task 6) and `results/LAB_SUBMISSION.md` (lab form) |
| Read the findings | `results/analysis.md` (Task 5) |
| See the raw data | `data/comments_sheet.csv` (all comments, with the English translation column) |
| See the numbers behind the slides | `results/ml_results.txt`, `results/ml_metrics.json` |
| See the charts | `results/figures/` |
| Know the original assignment | `docs/Week 14 - Sentiment Analysis.docx` |
| Re-run the analysis | `README.md`, then `main.py` |

## The process, step by step

```
data/posts.csv (source links)
      │  collected earlier with the scrape scripts (Task 1)
      ▼
data/comments_sheet.csv  ──►  python main.py import-sheet
      │  (comments + `Comment Text EN`, translated with GOOGLETRANSLATE in Google Sheets)
      ▼
data/raw/raw_comments.csv              Task 1  raw comments, @handles removed
      │  python main.py analyze
      ▼
data/processed/cleaned_comments.csv    Task 2  translated, cleaned, tokenized, lemmatized
data/processed/lexicon_results.csv     Task 3  VADER / TextBlob / AFINN scores and labels
results/ml_results.txt                 Task 4  TF-IDF + LR / NB metrics (+ ml_metrics.json)
results/figures/*.png                          charts and confusion matrices
results/analysis.md                    Task 5  comparison write-up (written from the results)
      │  python main.py deck
      ▼
results/Sentiment_Analysis_Inflation.pptx      Task 6  presentation
```

1. **Collect:** comments were scraped from the links in `data/posts.csv`.
2. **Translate:** the sheet's `Comment Text EN` column holds Google Translate output, because the lexicons only read English.
3. **Clean:** lowercase, strip URLs/punctuation/digits/emojis, tokenize, remove stopwords, lemmatize.
4. **Label:** each comment gets a score from three lexicons; the final label is the majority vote.
5. **Train:** TF-IDF features feed Logistic Regression and Naive Bayes on an 80/20 split. The labels are the lexicon vote, not hand labels.
6. **Report:** figures, `analysis.md`, and the deck are built from those results.

## Folder guide

### `data/`
| File | What it is |
|---|---|
| `posts.csv` | The 60 source links (`url`, `platform`) |
| `comments_sheet.csv` | The group sheet: every comment with source, platform, language, keyword, sentiment label and `Comment Text EN` |
| `raw/raw_comments.csv` | Task 1 deliverable: text, date, platform, source link |
| `processed/cleaned_comments.csv` | Task 2 deliverable |
| `processed/lexicon_results.csv` | Task 3 deliverable: scores, per-lexicon labels, consensus `label` |
| `processed/translations.json` | Translation cache (gitignored; rebuilt by `import-sheet`) |

### `results/`
| File | What it is |
|---|---|
| `Sentiment_Analysis_Inflation.pptx` | Final presentation (11 slides) |
| `analysis.md` | Task 5 comparative analysis |
| `LAB_SUBMISSION.md` | Filled lab manual submission form |
| `ml_results.txt`, `ml_metrics.json` | Task 4 metrics (text, and machine-readable for the deck and charts) |
| `figures/` | Charts used in the deck; `confusion_matrix.png` is the best model's |

### `src/` – the pipeline (this is the code that matters)
| File | Role |
|---|---|
| `config.py` | All paths and constants in one place |
| `collect.py` | `import-sheet` (rebuild raw data and translations from the sheet) and `scrape` routing; also writes labels back to the sheet |
| `youtube.py`, `reddit.py` | Official-API collectors (need keys in `secrets/.env`) |
| `scraper.py` | Optional Facebook browser scraper (Playwright), off by default |
| `translate.py` | Reads translations from the cache; fails loudly rather than scoring untranslated text |
| `preprocess.py` | Task 2 cleaning, tokenization, lemmatization |
| `lexicon.py` | Task 3 scoring, consensus vote, distribution chart |
| `ml.py` | Task 4 TF-IDF + models, metrics, confusion matrices |
| `visualize_more.py` | Extra charts (platform, keyword, language, model comparison, funnel) |
| `deck.py` | Builds the PowerPoint; every number is computed from the results |

### `src/` – one-off collection and helper scripts (not part of the pipeline)
These were used to gather the data and are kept for reference. You do not need them to reproduce the analysis.

| File | What it was for |
|---|---|
| `master_scrape.py`, `scrape_maximum.py`, `scrape_all_platforms.py`, `scrape_sheet_urls.py`, `fill_sheet.py` | Successive attempts to scrape the sheet's links and fill the sheet (overlapping; they contain copy-pasted helpers) |
| `all_urls.py`, `fb_urls.py` | Hard-coded URL lists used by the scrapers |
| `find_news_videos.py` | Looked up YouTube news videos to add as sources |
| `count_comments.py`, `inspect_sheet.py`, `inspect_fb_dom.py` | Quick inspection helpers |
| `seed_data.py` | **Synthetic demo comments for testing only. Not used for the real results; never include them in a submission.** |

### `tests/`
| File | What it is |
|---|---|
| `test_basic.py` | The real unit tests (text cleaning, label rules, cookie filtering). Run: `.venv/bin/python -m tests.test_basic` |
| `test_fb_*.py`, `test_pw_*.py`, `test_playwright.py`, `test_reddit.py`, `test_yt*.py`, `test_scrapers.py`, `test_tiktok_api.py`, `test_titles.py` | Scratch experiments from developing the scrapers. They have no assertions and some open live sites (Facebook ones use `secrets/cookies.txt`). Do not run them casually. |

### `docs/`
| File | What it is |
|---|---|
| `Week 14 - Sentiment Analysis.docx` | The assignment |
| `PLAN.md` | The original implementation plan (historical; `README.md` and this file describe what was built) |
| `NAVIGATION.md` | This guide |

### `secrets/` (gitignored, never commit or share)
| File | What it is |
|---|---|
| `.env` | API keys (YouTube, Reddit, optional Google Translate) |
| `cookies.txt` | Browser cookies for the Facebook scraper. It contains logged-in sessions for other sites too. |

## Commands cheat sheet

```bash
.venv/bin/python main.py import-sheet            # sheet -> raw_comments.csv + translations
.venv/bin/python main.py analyze                 # Tasks 2-4, figures, sheet labels
.venv/bin/python main.py deck --instructor "Love" --section "CS412"   # Task 6 deck
.venv/bin/python -m tests.test_basic             # unit tests
```

Order matters: `import-sheet` → `analyze` → `deck`. After changing `data/comments_sheet.csv`, run all three.

## Known limits (also stated in the reports)

- No hand labels: the ML score shows how well the model copies the lexicon vote.
- One YouTube video supplies about 45% of the comments, and many comments react to the video rather than to prices.
- Comment dates are estimated from relative timestamps ("3 weeks ago").
- Machine translation adds noise; some Taglish stays partly untranslated.
- The data was collected with unofficial scraping tools (see `README.md`).
