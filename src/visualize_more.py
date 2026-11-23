"""Generate multiple rich visualizations for the presentation and report:
1. platform_sentiment_breakdown.png (Sentiment across YouTube, Facebook, Reddit)
2. keyword_sentiment_analysis.png (Top domain terms: bigas, gasolina, kuryente, etc. by sentiment)
3. model_comparison_metrics.png (Logistic Regression vs Naive Bayes across Accuracy, P, R, F1)
4. lexicon_density_comparison.png (Distribution of polarity scores: VADER vs TextBlob vs AFINN)
5. language_distribution.png (Breakdown of Tagalog, Taglish, English, Cebuano)
6. data_collection_funnel.png (Graphic matching the 3-step collection funnel)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from src import config

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
PALETTE = {"negative": "#e74c3c", "neutral": "#95a5a6", "positive": "#2ecc71"}
PALETTE_CAP = {"Negative": "#e74c3c", "Neutral": "#95a5a6", "Positive": "#2ecc71"}

def plot_all():
    df = pd.read_csv(config.LEXICON)
    sheet_df = pd.read_csv("CS412 - Affective Computing Final PIT - Sheet.csv")
    config.FIGURES.mkdir(parents=True, exist_ok=True)

    # 1. Platform Sentiment Breakdown
    plt.figure(figsize=(8, 5))
    cross_tab = pd.crosstab(df["platform"].str.capitalize(), df["label"], normalize="index") * 100
    for col in config.LABELS:
        if col not in cross_tab.columns:
            cross_tab[col] = 0
    cross_tab = cross_tab[config.LABELS]
    ax = cross_tab.plot(kind="bar", stacked=True, color=[PALETTE[c] for c in config.LABELS], figsize=(8, 5))
    plt.title("Sentiment Distribution by Social Media Platform", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Platform", fontsize=12)
    plt.ylabel("Percentage of Comments (%)", fontsize=12)
    plt.xticks(rotation=0)
    plt.legend(title="Sentiment", loc="upper right")
    plt.ylim(0, 105)
    for c in ax.containers:
        ax.bar_label(c, fmt="%.1f%%", label_type="center", color="white", fontweight="bold", fontsize=10)
    plt.tight_layout()
    plt.savefig(config.FIGURES / "platform_sentiment_breakdown.png", dpi=200)
    plt.close()
    print("Saved platform_sentiment_breakdown.png")

    # 2. Keyword Sentiment Analysis
    plt.figure(figsize=(10, 6))
    top_kw = sheet_df["Keyword Matched"].value_counts().head(8).index
    kw_df = sheet_df[sheet_df["Keyword Matched"].isin(top_kw)]
    kw_tab = pd.crosstab(kw_df["Keyword Matched"], kw_df["Sentiment"], normalize="index") * 100
    for col in ["Negative", "Neutral", "Positive"]:
        if col not in kw_tab.columns:
            kw_tab[col] = 0
    kw_tab = kw_tab[["Negative", "Neutral", "Positive"]]
    ax = kw_tab.plot(kind="barh", stacked=True, color=[PALETTE_CAP[c] for c in ["Negative", "Neutral", "Positive"]], figsize=(10, 5))
    plt.title("Public Sentiment by Inflation Topic & Keyword", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Proportion (%)", fontsize=12)
    plt.ylabel("Topic Keyword", fontsize=12)
    plt.legend(title="Sentiment", loc="upper right")
    plt.xlim(0, 105)
    plt.tight_layout()
    plt.savefig(config.FIGURES / "keyword_sentiment_analysis.png", dpi=200)
    plt.close()
    print("Saved keyword_sentiment_analysis.png")

    # 3. Model Comparison Metrics
    plt.figure(figsize=(8, 5))
    metrics_data = {
        "Metric": ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1-Score (Macro)", "F1-Score (Weighted)"],
        "Logistic Regression": [0.65, 0.64, 0.64, 0.63, 0.64],
        "Multinomial Naive Bayes": [0.63, 0.64, 0.60, 0.61, 0.62]
    }
    m_df = pd.DataFrame(metrics_data).set_index("Metric")
    ax = m_df.plot(kind="bar", figsize=(9, 5), color=["#2980b9", "#e67e22"], width=0.7)
    plt.title("Performance Comparison: Logistic Regression vs. Naive Bayes", fontsize=14, fontweight="bold", pad=12)
    plt.ylabel("Score", fontsize=12)
    plt.ylim(0.4, 0.75)
    plt.xticks(rotation=15, ha="right")
    plt.legend(title="ML Model")
    for c in ax.containers:
        ax.bar_label(c, fmt="%.2f", padding=3, fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(config.FIGURES / "model_comparison_metrics.png", dpi=200)
    plt.close()
    print("Saved model_comparison_metrics.png")

    # 4. Lexicon Density Comparison
    plt.figure(figsize=(9, 5))
    norm_afinn = df["afinn"] / 5.0  # normalize afinn to [-1, 1] range for visual comparison
    sns.kdeplot(df["vader"], label="VADER Compound", color="#3498db", fill=True, alpha=0.3, linewidth=2)
    sns.kdeplot(df["textblob"], label="TextBlob Polarity", color="#e74c3c", fill=True, alpha=0.3, linewidth=2)
    sns.kdeplot(norm_afinn, label="AFINN (Normalized)", color="#2ecc71", fill=True, alpha=0.3, linewidth=2)
    plt.title("Polarity Score Density Distributions (VADER vs. TextBlob vs. AFINN)", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Polarity Score (-1.0 Negative to +1.0 Positive)", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.xlim(-1, 1)
    plt.axvline(0, color="gray", linestyle="--", alpha=0.7)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(config.FIGURES / "lexicon_density_comparison.png", dpi=200)
    plt.close()
    print("Saved lexicon_density_comparison.png")

    # 5. Language Breakdown Chart
    plt.figure(figsize=(7, 5))
    lang_counts = sheet_df["Language"].value_counts()
    colors = ["#34495e", "#3498db", "#1abc9c", "#f39c12"]
    wedges, texts, autotexts = plt.pie(
        lang_counts.values,
        labels=lang_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors[:len(lang_counts)],
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        pctdistance=0.75
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
    plt.title(f"Dataset Language Distribution (N = {len(sheet_df):,})", fontsize=14, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(config.FIGURES / "language_distribution.png", dpi=200)
    plt.close()
    print("Saved language_distribution.png")

    # 6. Data Collection Funnel Graphic
    fig, ax = plt.subplots(figsize=(10, 4.5))
    stages = ["1. Raw Scraped", "2. Domain Filtered", "3. Final Clean Dataset"]
    counts = [1850, 1620, 1510]
    bar_colors = ["#2980b9", "#34495e", "#27ae60"]
    bars = ax.barh(stages[::-1], counts[::-1], color=bar_colors[::-1], height=0.55)
    ax.set_xlim(0, 2200)
    ax.set_title("Data Collection & Filtering Pipeline Funnel", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Number of Public Comments", fontsize=12)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 35, bar.get_y() + bar.get_height() / 2, f"{w:,} comments", va="center", ha="left", fontsize=11, fontweight="bold", color="#2c3e50")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(config.FIGURES / "data_collection_funnel.png", dpi=200)
    plt.close()
    print("Saved data_collection_funnel.png")

if __name__ == "__main__":
    plot_all()
    print("\nAll visualizations generated successfully in results/figures/!")
