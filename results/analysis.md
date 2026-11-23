# Task 5: Comparative Analysis Report

**Course:** CS 413 – CS Elective 2 (Affective Computing)
**Topic:** High Inflation and Cost of Living in the Philippines
**Group:** Bea, Jesreal, Raphael, Gil, Angel
**Dataset:** 1,505 unique public comments from 60 sources (YouTube 1,059, Facebook 343, Reddit 103)

All numbers below come from `results/ml_results.txt`, `results/ml_metrics.json` and
`data/processed/lexicon_results.csv`. Rerun `python main.py analyze` to reproduce them.

## How to read the scores

We have no hand-labelled comments. Each comment's label is the majority vote of VADER, TextBlob
and AFINN on the English translation. The ML models are trained and tested on those labels, so
their accuracy measures how well TF-IDF + ML reproduces the lexicon vote, not how well it matches
human judgement. The lexicon "agreement" figures are inflated for the same reason: each lexicon is
one of the three voters.

## 1. Which method performed best?

| Method | Result |
|---|---|
| Logistic Regression (TF-IDF, balanced classes) | 66% accuracy, 0.66 macro-F1 |
| Multinomial Naive Bayes (TF-IDF) | 59% accuracy, 0.58 macro-F1 |
| VADER | agrees with the consensus on 86.4% of comments |
| AFINN | agrees with the consensus on 86.4% of comments |
| TextBlob | agrees with the consensus on 68.2% of comments |

- **Best ML model: Logistic Regression.** Its per-class F1 is even: negative 0.62, neutral 0.68,
  positive 0.67. Test set: 301 comments (1,204 for training).
- **Naive Bayes** leans on the positive class (recall 0.76) and misses half of the negative and
  neutral comments (recall 0.51 and 0.48).
- **Among lexicons,** VADER and AFINN track the consensus equally; TextBlob is the outlier.
- With chance at about 33% for three classes, 66% shows the model learned the lexicons' pattern,
  but a third of test comments are still labelled differently.

## 2. Why did the lexicons differ from ML?

1. **Different information.** A lexicon scores each word from a fixed list and sums the result.
   TF-IDF + ML has no built-in word polarity; it learns from 1,204 comments which words and
   two-word phrases go with each label. Words outside the lexicons (place names, politicians,
   untranslated Tagalog) can still carry weight for the model.
2. **The lexicons disagree with each other.** All three give the same label on only 47.6% of
   comments, and all three differ on 6.6%. TextBlob calls 40% of comments neutral and only 20%
   negative; AFINN calls 35% negative. The model is trained on a vote among sources that often
   conflict, which limits how high its score can go.
3. **Translation and code-switching.** 383 of 1,505 comments changed when translated. Taglish
   comments that Google detected as English were left as they were, so some Tagalog words still
   reach the lexicons, which ignore them and push the comment toward neutral.
4. **Sarcasm and short replies.** One-word or joking comments ("winner", laughing emojis after a
   complaint) get a positive score from surface words. Neither approach can see the irony.

## 3. What is the emotional distribution of the domain?

| Label | Comments | Share |
|---|---|---|
| Positive | 539 | 35.8% |
| Neutral | 527 | 35.0% |
| Negative | 439 | 29.2% |

By platform:

| Platform | Negative | Neutral | Positive |
|---|---|---|---|
| YouTube (1,059) | 35% | 33% | 32% |
| Reddit (103) | 25% | 27% | 48% |
| Facebook (343) | 12% | 45% | 43% |

- The split is close to even. The domain is not overwhelmingly negative by this measure.
- YouTube is the most negative platform; Facebook is the least.
- "Positive" here means positive wording, not satisfaction with prices. Sarcasm, jokes and
  praise for a video's host all count as positive, so the real level of frustration is probably
  higher than 29%.

Before translation the same pipeline reported 43% neutral, because the lexicons could not read
the Tagalog comments. Translating them moved many out of neutral.

## 4. How does this relate to affective computing?

- **Emotion from text at scale.** Affective computing aims to let machines recognise human
  emotion. Comment streams give a fast, low-cost signal of how people feel about prices, well
  ahead of quarterly consumer surveys.
- **Polarity is not emotion.** Positive/negative/neutral hides the difference between anger,
  fear, resignation and humour, which is what matters for cost-of-living discourse.
- **Language and culture matter.** English word lists miss Taglish, Cebuano and sarcasm. A useful
  affective system for Philippine social media needs multilingual models and human-labelled data.

## Limitations

- No human labels; all scores are relative to the lexicon vote.
- One YouTube video supplies 45% of the comments, and many comments react to the video or to
  other commenters rather than to prices. Only 397 comments contain a tracked price keyword.
- Machine translation adds noise, and mixed-language comments are only partly translated.
- Comment dates are estimated from relative timestamps ("3 weeks ago"); many are simply the
  collection date.
- The dataset was collected with unofficial tools (see `README.md`).
