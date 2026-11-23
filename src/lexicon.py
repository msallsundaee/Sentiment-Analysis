"""Task 3: VADER / TextBlob / AFINN polarity, labels, consensus and summary chart."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from afinn import Afinn
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src import config

LEXICONS = ["vader", "textblob", "afinn"]


def to_label(score, cut):
    return "positive" if score >= cut else "negative" if score <= -cut else "neutral"


def consensus(labels):
    """Majority of the three lexicon labels; all different -> neutral."""
    top = max(set(labels), key=labels.count)
    return top if labels.count(top) > 1 else "neutral"


def score(df, col="text_en"):
    """Adds <lexicon> scores, <lexicon>_label and a consensus `label`. Runs on raw-ish
    text (not stemmed) because VADER relies on punctuation and capitals."""
    vader, afinn = SentimentIntensityAnalyzer(), Afinn()
    df["vader"] = df[col].map(lambda t: vader.polarity_scores(t)["compound"])
    df["textblob"] = df[col].map(lambda t: TextBlob(t).sentiment.polarity)
    df["afinn"] = df[col].map(afinn.score)
    for m, cut in [("vader", 0.05), ("textblob", 0.05), ("afinn", 1)]:
        df[f"{m}_label"] = df[m].map(lambda s: to_label(s, cut))
    df["label"] = [consensus(list(r)) for r in df[[f"{m}_label" for m in LEXICONS]].itertuples(index=False)]
    return df


def plot_distribution(df):
    cols = {m: df[f"{m}_label"] for m in LEXICONS} | {"consensus": df.label}
    counts = pd.DataFrame({k: v.value_counts().reindex(config.LABELS, fill_value=0) for k, v in cols.items()})
    counts.T.plot(kind="bar", stacked=True, color=["#c0392b", "#95a5a6", "#27ae60"], figsize=(7, 4))
    plt.title(f"Sentiment distribution: {config.TOPIC}")
    plt.ylabel("Comments")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(config.FIGURES / "sentiment_distribution.png", dpi=150)
    plt.close()
