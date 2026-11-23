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

### Task 1: Data Collection Summary
* **Total Collected:** **1,510 unique comments** (target was 1,000+).
* **Platforms Used:**
  * **YouTube:** 1,062 comments across official news broadcasts (*24 Oras*, *Balitanghali*, *SONA*, ANC) and public inflation explainers.
  * **Facebook:** 345 comments across 42 news posts using read-only browser session automation.
  * **Reddit:** 103 comments across *r/Philippines*, *r/phinvest*, *r/Philippines_Expats*, and *r/KaskasanBuddies*.
* **Ethical Protocol Compliance:**
  1. Only 100% publicly available posts and news threads were accessed.
  2. Zero usernames, handles, profile photos, or personal links were stored. Only comment text, date, and reactions were captured.
  3. Collection was strictly read-only; no liking, commenting, or interaction occurred.
* **Deliverable:** `data/raw/raw_comments.csv`

---

### Task 2: Preprocessing Summary
* **Language Handling:** Tagalog and Taglish comments were translated to English using deep-translator (Google Translate API) with local caching in `translations.json`.
* **Cleaning Steps Applied:**
  1. Stripping URLs, HTML entities, and formatting artifacts.
  2. Converting text to lowercase.
  3. Removing punctuation, special characters, digits, and emojis.
  4. Tokenizing words using NLTK `word_tokenize`.
  5. Filtering English stopwords via NLTK corpus.
  6. Applying WordNet lemmatization to extract word roots.
* **Deliverable:** `data/processed/cleaned_comments.csv`

---

### Task 3: Lexicon-Based Sentiment Analysis
* **Lexicons Evaluated:** VADER, TextBlob, and AFINN.
* **Labeling Rule:** Majority consensus vote across the three lexicons.
* **Results across 1,510 comments:**
  * **Neutral:** 651 comments (43.1%)
  * **Positive:** 470 comments (31.1%)
  * **Negative:** 389 comments (25.8%)
* **Agreement with Consensus:**
  * AFINN: 87.3%
  * VADER: 85.2%
  * TextBlob: 70.9%
* **Deliverables:** `data/processed/lexicon_results.csv`, `results/figures/sentiment_distribution.png`

---

### Task 4: Machine Learning-Based Sentiment Analysis
* **Feature Extraction:** TF-IDF Vectorizer with unigrams and bigrams (`ngram_range=(1,2)`, `min_df=2`, English stop words removed).
* **Validation Strategy:** 80/20 train/test stratified split (1,208 training samples, 302 test samples).
* **Model Performance Comparison:**

| Model | Accuracy | Precision (Macro) | Recall (Macro) | F1-Score (Macro) | Best Per-Class F1 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Logistic Regression** | **65%** | **0.64** | **0.64** | **0.63** | Neutral: 0.71, Neg: 0.62, Pos: 0.57 |
| **Multinomial Naive Bayes** | 63% | 0.64 | 0.60 | 0.61 | Neutral: 0.69, Neg: 0.60, Pos: 0.54 |

* **Best Model:** **Logistic Regression** achieved the highest macro-F1 (0.63) and balanced precision/recall across all three emotional classes.
* **Deliverables:** `results/ml_results.txt`, `results/figures/confusion_matrix.png`

---

### Task 5: Comparative Analysis & Discussion
1. **Which method performed best?**
   * Logistic Regression with TF-IDF performed best overall, achieving 65% accuracy and 0.63 macro-F1 score on unseen test data.
2. **Why did lexicons differ from ML?**
   * Lexicons rely on static, word-level dictionaries that miss domain context (e.g., treating statistical terms like "oil shock" or "inflation soars" as negative even in neutral reports). ML models learned multi-word associations directly from domain comments.
   * Cultural humor and Taglish political sarcasm ("senateflix", "lutang", "fine daw") consistently deceived lexicon sentiment lookup.
3. **What is the emotional distribution of your domain?**
   * Neutral dominates (43.1%), driven by economic news and PSA inflation updates.
   * Positive sentiment (31.1%) reflects community resilience, Kadiwa stores, and budgeting strategies.
   * Negative sentiment (25.8%) captures deep public frustration over basic food and transport costs.
4. **How does this relate to affective computing?**
   * Demonstrates how computational affective systems can serve as real-time barometers of public socioeconomic welfare, emphasizing the need for culturally tuned, multilingual NLP architectures.

---

### Task 6: Final Presentation Deliverable
* **Presentation Deck:** Generated and saved as `results/Sentiment_Analysis_Inflation.pptx` (9 slides conforming to the required outline).
