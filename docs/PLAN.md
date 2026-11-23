# Implementation Plan: Sentiment Analysis Final Project

**Course:** CS 413 – CS Elective 2 (Affective Computing), Week 14
**Topic:** High Inflation and Cost of Living
**Status:** plan only. Nothing is built or scraped yet.

## What the assignment requires

- **Data:** 1000+ public comments on one domain. The intro says 500 and Task 1 says 1000+, so the target is 1000+.
- **Stored fields:** comment text, timestamp, reaction count (optional). No usernames, profile photos, profile links or personal information.
- **Tasks:** collect, preprocess, run at least two lexicons, train TF-IDF + Logistic Regression / Naive Bayes, compare the methods, present.
- **Ethics rules:**
  - Public pages, public posts and public news outlets only. No private groups or private individuals.
  - Observe only. No liking, replying or any other interaction.
  - Sensitive topics: do not store personal stories or distressing, identifying details.
  - Automation must not bypass security or privacy restrictions.
- **Group:** 4 members, and every member contributes to data collection, analysis, writing and presenting.

## Steps

| Step | What happens | Output |
|---|---|---|
| 0. Setup | Create a virtual environment and install the packages. Only `matplotlib` and `requests` are installed now. | `requirements.txt` |
| 1. Scrape | Playwright loads only the `facebook.com` cookies, opens each public post, switches to "All comments", expands and scrolls slowly, read-only. Drops duplicates and very short or emoji-only comments. | `raw_comments.csv` |
| 2. Preprocess | Lowercase, strip URLs, punctuation and emojis, tokenize, remove English and Tagalog stopwords, lemmatize. | `cleaned_comments.csv` |
| 3. Lexicons | VADER, TextBlob and AFINN polarity scores and Positive / Negative / Neutral labels, with distribution charts. | `lexicon_results.csv`, charts |
| 4. ML | TF-IDF, then Logistic Regression and Naive Bayes on an 80/20 split. Accuracy, precision, recall, F1, confusion matrix. | `ml_results.txt`, `confusion_matrix.png` |
| 5. Compare | Score the lexicons and the ML models against the same labels and answer the four Task 5 questions. | `analysis.md` |
| 6. Present | A 9-section deck following the Task 6 outline. | `.pptx` |

Packages to install: `playwright`, `pandas`, `nltk`, `scikit-learn`, `vaderSentiment`, `textblob`, `afinn`, `seaborn`, `deep-translator`.

### Task 5 questions to answer

1. Which method performed best?
2. Why did the lexicons differ from ML?
3. What is the emotional distribution of the domain?
4. How does this relate to affective computing?

### Task 6 presentation outline

1. Title page: group members, course, instructor, section, topic
2. Introduction: the domain and why sentiment analysis matters
3. Dataset and collection process: source links, ethical steps, number of comments
4. Preprocessing techniques: screenshots or summaries
5. Lexicon analysis: sample outputs, sentiment distribution chart
6. ML-based analysis: TF-IDF, model results, confusion matrix
7. Comparison and discussion: best model, emotional patterns, challenges
8. Conclusion and relation to affective computing
9. References

## Problems the assignment doesn't address

### 1. No ground-truth labels

The ML step needs labelled comments. Training on VADER's own output would be circular: the model would only learn to imitate VADER.

**Recommendation:** each of the four members hand-labels about 250 comments. A suggested label can be pre-filled for correction. The same labels then score the lexicons too, which is what makes "which method performed best" answerable.

### 2. Language

Philippine inflation comments will mostly be Tagalog, Taglish or Bisaya. VADER, TextBlob and AFINN are English-only.

**Recommendation:** add an English-translated column (Google Translate) for the lexicons, and train the ML model on the original text. Lemmatization will only really work on the English words.

### 3. Facebook account risk

Scraping while logged in is against Facebook's terms and can trigger a checkpoint or lock on the account. The scrape will be slow, read-only and limited to public news-page posts, but the risk belongs to the account owner.

**Fallback:** the YouTube Data API. The assignment allows YouTube comments, and it is an official API.

## About `cookies.txt`

- The Facebook session cookies (`c_user`, `xs`) are present and not expired, so login should work.
- The file is a full browser export. It also holds live sessions for Google/Gmail, claude.ai, Stripe, LinkedIn and Reddit.
- Only the `facebook.com` lines will be read.
- Do not share, submit or commit this file. It can be replaced with a Facebook-only version.

## Needed before scraping

1. **Post URLs:** 8–15 public posts about inflation or prices from news pages (Rappler, GMA News, ABS-CBN, Inquirer, a local CDO page), each with 150+ comments. Or a go-ahead to find them.
2. **Account risk:** accept it, switch to YouTube, or use both.
3. **Labelling:** hand-label as a group (recommended), or use lexicon pseudo-labels and note the limitation.
4. **Translation:** permission to send comment text (no names) to Google Translate.
5. **Title page details:** group members, section, instructor.

Once 1–4 are answered, work starts with the setup and a one-post scrape test before the full run.

## Not yet verified

- Whether the cookies actually log in.
- Whether Facebook's current page layout lets Playwright read comments. The one-post test will show both.
- Facebook timestamps are relative ("3w"), so stored dates will be approximate.
