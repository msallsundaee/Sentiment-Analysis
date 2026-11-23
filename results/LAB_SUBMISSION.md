# Laboratory Manual Submission Form

**Department of Computer Science**
**College of Information Technology and Computing**
**Course:** CS 413 – CS Elective 2 (Affective Computing)
**Sem & SY:** 1st Sem, SY 2025–2026
**Topic:** High Inflation and Cost of Living in the Philippines
**Week No(s):** Week 14
**Date:** November 23, 2026
**Group Members:** Bea, Jesreal, Raphael, Gil, Angel
**Course & Section:** BSCS 412 / CS 413

---

## Answer Starts Here:

### Task 1: Data Collection
* **Collected:** 1,510 public comments from 60 public videos, posts and threads; 1,505 remain after cleaning.
* **Platforms:** YouTube 1,059 comments (17 videos), Facebook 343 (38 posts), Reddit 103 (5 threads).
* **Method:** YouTube with `youtube-comment-downloader`; Reddit and Facebook read in a Playwright browser. Source links are in `data/posts.csv`.
* **Ethical protocol:**
  1. Public posts and videos only; no private groups or profiles.
  2. No names, profile links or photos stored. `@handles` inside replies were stripped from all 169 comments that had them.
  3. Read-only: no likes, replies or posts.
* **Stored fields:** comment text, date (estimated from relative timestamps), platform, source link.
* **Deliverable:** `data/raw/raw_comments.csv` (1,508 rows before de-duplication)

---

### Task 2: Preprocessing
* **Translation:** every comment was run through Google Translate (`GOOGLETRANSLATE` in Google Sheets, auto-detect to English); 383 comments changed.
* **Cleaning:** lowercase; remove URLs, punctuation, digits and emojis.
* **Tokenization:** NLTK `word_tokenize`.
* **Stopword removal:** NLTK English stopwords.
* **Lemmatization:** WordNet lemmatizer.
* **Deliverable:** `data/processed/cleaned_comments.csv` (1,505 rows)

---

### Task 3: Lexicon-Based Sentiment
* **Lexicons:** VADER, TextBlob, AFINN, each giving a polarity score and a Positive/Negative/Neutral label.
* **Final label:** majority vote of the three (all different = neutral).

| Label | Comments | Share |
|---|---|---|
| Positive | 539 | 35.8% |
| Neutral | 527 | 35.0% |
| Negative | 439 | 29.2% |

* **Agreement with the vote:** VADER 86.4%, AFINN 86.4%, TextBlob 68.2%. All three agree on 47.6% of comments.
* **Deliverables:** `data/processed/lexicon_results.csv`, `results/figures/sentiment_distribution.png`, `results/figures/lexicon_density_comparison.png`

---

### Task 4: ML-Based Sentiment Analysis
* **Features:** TF-IDF, unigrams and bigrams, `min_df=2`, English stopwords removed.
* **Split:** 80/20 stratified (1,204 train, 301 test).
* **Labels:** the lexicon vote from Task 3 (no hand labels).

| Model | Accuracy | Precision (macro) | Recall (macro) | F1 (macro) | Per-class F1 (neg / neu / pos) |
|---|---|---|---|---|---|
| **Logistic Regression** | **66%** | **0.66** | **0.66** | **0.66** | 0.62 / 0.68 / 0.67 |
| Multinomial Naive Bayes | 59% | 0.61 | 0.58 | 0.58 | 0.58 / 0.54 / 0.63 |

* **Best model:** Logistic Regression.
* **Deliverables:** `results/ml_results.txt`, `results/figures/confusion_matrix.png`

---

### Task 5: Comparative Analysis
Full write-up: `results/analysis.md`.
1. **Which method performed best?** Logistic Regression (66% accuracy, 0.66 macro-F1) beat Naive Bayes (59%, 0.58). Among lexicons, VADER and AFINN match the vote most often. Because the labels are the lexicon vote, the ML score shows how well the model reproduces the lexicons, not human judgement.
2. **Why did lexicons differ from ML?** Lexicons add up fixed word scores; the model learns from the comments which words and phrases go with each label, including words the lexicons do not know. The three lexicons also disagree with each other on about half the comments, and translation leaves some Taglish untranslated.
3. **Emotional distribution:** close to even: 35.8% positive, 35.0% neutral, 29.2% negative. YouTube is the most negative platform (35%), Facebook the least (12%). Sarcasm and jokes are counted as positive, so real frustration is likely higher.
4. **Relation to affective computing:** comment streams can act as a fast signal of public feeling about prices, but word-polarity tools built for English miss Taglish, sarcasm and specific emotions, so culturally aware models and human-labelled data are needed.

**Limitations:** no human labels; one YouTube video supplies 45% of the comments; many comments are not directly about prices; dates are approximate.

---

### Task 6: Final Presentation
* `results/Sentiment_Analysis_Inflation.pptx` (11 slides: title, the 9 required sections with two extra analysis slides, references).
