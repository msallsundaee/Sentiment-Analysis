# Task 5: Comparative Analysis Report

**Course:** CS 413 – CS Elective 2 (Affective Computing)  
**Topic:** High Inflation and Cost of Living in the Philippines  
**Group:** Bea, Jesreal, Raphael, Gil, Angel  
**Dataset Size:** 1,510 unique public comments (YouTube: 1,062, Facebook: 345, Reddit: 103)

---

## 1. Which method performed best?

Between the machine learning models and the lexicon-based methods:
* **Best Machine Learning Model:** **Logistic Regression** (with balanced class weights) achieved the best overall performance with:
  * **Accuracy:** **65%** (vs. 63% for Multinomial Naive Bayes)
  * **Macro-averaged F1-Score:** **0.63** (vs. 0.61 for Naive Bayes)
  * **Per-Class F1-Scores:** Negative: 0.62, Neutral: 0.71, Positive: 0.57
* **Lexicon Methods:** 
  * **AFINN** exhibited the highest agreement with the consensus label (**87.3%**), closely followed by **VADER** (**85.2%**), while **TextBlob** lagged at **70.9%**.
* **Comparative Assessment:**
  * While lexicons rely on predefined general-purpose polarity dictionaries, **Logistic Regression + TF-IDF** performed best at identifying domain-specific terminology (e.g., *"presyo"*, *"bilihin"*, *"fuel subsidy"*, *"kadiwa"*, *"pamasahe"*). 
  * Naive Bayes suffered from its conditional independence assumption, struggling with negated sentiment and sarcastic phrasing common in Philippine political and economic discourse.

---

## 2. Why did the lexicons differ from ML?

The divergence between lexicon-based scores and machine learning predictions stems from three key factors:

1. **Static Polarity vs. Contextual Co-occurrence:**
   * Lexicons evaluate words in isolation based on static numerical scores. Words like *"shock"*, *"soar"*, or *"climb"* in economic news headlines (e.g., *"inflation soars to 7.8%"*) are treated as intensely negative by VADER/AFINN, even when the comment simply quotes statistical reports neutrally.
   * Conversely, ML with TF-IDF unigram and bigram features captures learned phrase combinations that distinguish informational commentary from genuine frustration.

2. **Taglish Code-Switching & Translation Noise:**
   * Philippine social media discourse frequently mixes English, Tagalog, and regional languages (Taglish). Because VADER, TextBlob, and AFINN are English-only, comments had to be machine-translated.
   * Translation often strips colloquial Tagalog slang and intensifiers (e.g., *"lutang"*, *"bangag"*, *"pahirap"*, *"diskarte"*), leading to lexicon misclassifications.

3. **Sarcasm and Cultural Satire:**
   * Many negative comments wrap criticism in humorous or satirical language (e.g., *"fine daw sabi bangag"*, *"senateflix directed by BBM"*, *"nobody eats a whole fish now"*). Lexicons fail to register irony and frequently label sarcastic praise as "Positive" due to surface words like *"fine"* or *"enjoy"*.

---

## 3. What is the emotional distribution of your domain?

Across the 1,510 public comments analyzed:
* **Neutral (43.1% – 651 comments):**
  * The largest single group comprises factual inquiries, news reposting, and citations of official statistics from the Philippine Statistics Authority (PSA) and Bangko Sentral ng Pilipinas (BSP) (e.g., discussions on the 7.2% and 7.8% CPI benchmarks).
* **Positive / Coping (31.1% – 470 comments):**
  * Expresses relief, optimism, mutual aid, and active coping strategies (e.g., support for Kadiwa discounted stores, urban farming, fuel subsidies for public transport drivers, and community solidarity).
* **Negative (25.8% – 389 comments):**
  * Marked by vocal frustration, economic anxiety, skepticism toward government price mitigation, and distress over grocery bills, rice price ceilings, and utility hikes.

---

## 4. How does this relate to affective computing?

Affective Computing focuses on enabling digital systems to recognize, interpret, process, and simulate human emotions:

1. **Real-Time Economic Emotional Barometer:**
   * Traditional economic monitoring relies on quarterly survey indices (e.g., Consumer Expectation Surveys) which have significant reporting lag. Affective computing applied to social media streams transforms unstructured public discourse into immediate, high-frequency emotional barometers of economic hardship.
2. **Beyond Polarity to Context-Aware Affect:**
   * This project highlights that true affective computing cannot rely solely on dictionary lookup tables. Emotional state estimation in diverse populations requires cultural context, code-switching tolerance, and multi-modal contextual embeddings.
3. **Actionable Civic Decision Support:**
   * By identifying spikes in negative public affect around specific price hikes (e.g., rice, transport fares, electricity), affective systems can help policymakers detect community vulnerability and target emergency subsidies before severe economic distress compounds.
