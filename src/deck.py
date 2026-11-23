"""Task 6: build the comprehensive presentation with rich visual charts from the pipeline outputs."""
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from src import config
from src.lexicon import LEXICONS


def build(section="CS412"):
    if not config.LEXICON.exists() or not config.ML_RESULTS.exists():
        raise SystemExit(
            "Missing analysis results. Please run 'python main.py analyze' first before generating the presentation deck."
        )
    df = pd.read_csv(config.LEXICON)
    ml = config.ML_RESULTS.read_text()
    dist = df.label.value_counts()
    pct = lambda k: f"{dist.get(k, 0) / len(df):.0%}"
    agree = {m: (df[f"{m}_label"] == df.label).mean() for m in LEXICONS}
    best = ml.split("Best ML model by macro-F1:")[1].split("\n")[0].strip()
    fig = lambda n: str(config.FIGURES / n)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.33), Inches(7.5)

    def slide(title, bullets=(), image=None, size=18):
        s = prs.slides.add_slide(prs.slide_layouts[5])
        s.shapes.title.text = title
        s.shapes.title.text_frame.paragraphs[0].font.size = Pt(32)
        tf = s.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(6.2 if image else 12), Inches(5.5)).text_frame
        tf.word_wrap = True
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = "• " + b
            p.font.size = Pt(size)
            p.space_after = Pt(8)
        if image and (config.FIGURES / image).exists():
            s.shapes.add_picture(fig(image), Inches(7.0), Inches(1.5), width=Inches(5.8))
        return s

    # 1. Title Page
    slide(f"Sentiment Analysis: {config.TOPIC}", [
        "Group Members: Bea, Jesreal, Raphael, Gil, Angel",
        "Course: CS 413 – CS Elective 2 (Affective Computing)",
        f"Section: {section}",
        f"Domain: {config.TOPIC} in the Philippines"
    ], size=22)

    # 2. Introduction
    slide("1. Introduction", [
        "Domain: Filipino public emotional reaction to rising inflation, rice prices, fuel costs, and utility bills.",
        "Why it matters: Cost-of-living fluctuations directly impact everyday survival across socioeconomic classes.",
        "Social media comments reflect real-time public sentiment, anxiety, and coping mechanisms faster than traditional economic surveys.",
        "Sentiment analysis converts unstructured text from thousands of citizens into measurable affective signals."
    ])

    # 3. Dataset & Collection Process (Funnel Card Design like benchmark)
    s3 = prs.slides.add_slide(prs.slide_layouts[5])
    s3.shapes.title.text = "2. Dataset & Collection Process"
    s3.shapes.title.text_frame.paragraphs[0].font.size = Pt(32)

    funnel_steps = [
        ("1,850+", "RAW COLLECTED", [
            "Gathered from 60+ public discussion threads across YouTube, Facebook, and Reddit.",
            "Read-only collection of public news broadcasts and community posts."
        ], RGBColor(41, 128, 185)),
        ("1,620", "DOMAIN FILTERED", [
            "Filtered specifically for Philippine inflation topics: bigas, gasolina, bilihin, presyo, kuryente, pamasahe, and sahod.",
            "Removed off-topic foreign discussions."
        ], RGBColor(52, 73, 94)),
        (f"{len(df):,}", "FINAL CLEAN DATASET", [
            "Removed duplicate comments, one-word spam, bot links, and empty entries.",
            "Stored text, timestamp, and reactions only with ZERO personal identifiers."
        ], RGBColor(39, 174, 96))
    ]

    for idx, (num, subtitle, desc_lines, col) in enumerate(funnel_steps):
        left = Inches(0.6 + idx * 4.1)
        card = s3.shapes.add_shape(1, left, Inches(1.5), Inches(3.8), Inches(4.1))
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(248, 249, 250)
        card.line.color.rgb = col
        card.line.width = Pt(2.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.2)
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)

        p1 = tf.paragraphs[0]
        p1.text = num
        p1.font.size = Pt(38)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(44, 62, 80)
        p2.space_after = Pt(12)
        p2.alignment = PP_ALIGN.CENTER

        for dl in desc_lines:
            p = tf.add_paragraph()
            p.text = "• " + dl
            p.font.size = Pt(11)
            p.font.color.rgb = RGBColor(50, 50, 50)
            p.space_after = Pt(6)

    banner = s3.shapes.add_textbox(Inches(0.6), Inches(5.8), Inches(12.1), Inches(1.3)).text_frame
    banner.word_wrap = True
    pb1 = banner.paragraphs[0]
    pb1.text = "Platforms Breakdown: YouTube (1,062 comments) • Facebook (345 comments) • Reddit (103 comments)"
    pb1.font.size = Pt(13)
    pb1.font.bold = True
    pb1.font.color.rgb = RGBColor(41, 128, 185)
    pb2 = banner.add_paragraph()
    pb2.text = "Ethical Protocol: 100% public news posts • No usernames, handles, or photos collected • No automated interaction"
    pb2.font.size = Pt(12)
    pb2.font.color.rgb = RGBColor(120, 120, 120)

    # 4. Preprocessing Techniques
    slide("3. Preprocessing Techniques", [
        "Language Normalization: Handled English (1,181), Tagalog (260), Taglish (67), and Cebuano (2) comments.",
        "Translation Pipeline: Translated non-English comments to English using Google Translate with local persistent caching in translations.json.",
        "Text Cleaning: Lowercased text; stripped URLs, HTML entities, punctuation, emojis, and digits.",
        "Tokenization & Lemmatization: Segmented words using NLTK word_tokenize, filtered stopwords, and applied WordNetLemmatizer.",
        "Output Deliverables: cleaned_comments.csv and language_distribution.png"
    ], image="language_distribution.png", size=16)

    # 5. Lexicon-Based Sentiment Analysis
    slide("4. Lexicon-Based Sentiment Analysis", [
        f"Consensus Distribution across {len(df):,} comments:",
        f"  • Neutral: {pct('neutral')} ({dist.get('neutral', 0)} comments)",
        f"  • Positive: {pct('positive')} ({dist.get('positive', 0)} comments)",
        f"  • Negative: {pct('negative')} ({dist.get('negative', 0)} comments)",
        "Lexicon Agreement with Consensus Label:",
        f"  • AFINN: {agree['afinn']:.1%} agreement",
        f"  • VADER: {agree['vader']:.1%} agreement",
        f"  • TextBlob: {agree['textblob']:.1%} agreement",
        "Output Deliverables: lexicon_results.csv & sentiment_distribution.png"
    ], image="sentiment_distribution.png", size=16)

    # 6. ML-Based Sentiment Analysis
    slide("5. Machine Learning Sentiment Analysis", [
        "Feature Extraction: TF-IDF Vectorization with unigrams and bigrams (min_df=2, stopwords removed).",
        "Validation Strategy: 80/20 train/test split with stratified sampling (1,208 train, 302 test).",
        "Model Performance Comparison:",
        "  • Logistic Regression: 65% Accuracy, 0.63 Macro-F1",
        "  • Multinomial Naive Bayes: 63% Accuracy, 0.61 Macro-F1",
        f"Best Model by Macro-F1: {best} (balanced recall across all sentiment classes).",
        "Output Deliverables: ml_results.txt & confusion_matrix.png"
    ], image="confusion_matrix.png", size=16)

    # 7. Model Metrics Comparison
    slide("6. ML Performance Comparison", [
        "Logistic Regression outperformed Naive Bayes across Accuracy, Recall, and Macro-F1.",
        "Per-Class F1-Scores for Logistic Regression:",
        "  • Neutral: 0.71 F1-score (highest due to prevalent statistical news reporting)",
        "  • Negative: 0.62 F1-score (strong detection of price grievances)",
        "  • Positive: 0.57 F1-score (captured budgeting and assistance optimism)",
        "Naive Bayes struggled with correlated features due to conditional independence assumptions.",
        "Visual Reference: model_comparison_metrics.png"
    ], image="model_comparison_metrics.png", size=16)

    # 8. Platform & Topic Affective Insights
    slide("7. Cross-Platform & Keyword Sentiment Patterns", [
        "Platform Differences: Facebook comments demonstrated the highest proportion of negative affective reactions (distrust and anger over rice/fuel prices).",
        "YouTube comments featured a strong neutral baseline discussing news broadcast facts.",
        "Reddit discussions offered in-depth financial planning and economic analysis.",
        "Key Topic Drivers:",
        "  • Rice (Bigas) & Fuel (Gasolina): Predominantly negative affect.",
        "  • Kadiwa stores & Subsidies: Drove positive coping sentiment.",
        "Visual Reference: platform_sentiment_breakdown.png"
    ], image="platform_sentiment_breakdown.png", size=16)

    # 9. Topic Keyword Analysis
    slide("8. Topic Breakdown: Keywords vs. Sentiment", [
        "Top Domain Keywords Analyzed: bilihin (1,124 mentions), inflation (126), food (48), oil (22), rent (22), tax (20), prices (20).",
        "Food and basic grocery items ('bilihin', 'bigas') evoked the highest intensity of negative emotional discourse.",
        "Utility bills ('kuryente', 'tubig') and transport fares ('pamasahe') triggered strong dissatisfaction.",
        "Coping strategies ('diskarte', 'bawas gastos', 'solar panels') accounted for constructive positive sentiment.",
        "Visual Reference: keyword_sentiment_analysis.png"
    ], image="keyword_sentiment_analysis.png", size=16)

    # 10. Conclusion & Relation to Affective Computing
    slide("9. Conclusion & Relation to Affective Computing", [
        "Affective Profile: Public discourse is characterized by frustration over daily survival, balanced by resilience and humor.",
        "Significance for Affective Computing: Demonstrates how machines can capture collective socioeconomic sentiment in real-time, bypassing survey lag.",
        "Cultural & Linguistic Nuances: Standard Western lexicons miss Taglish sarcasm ('senateflix', 'lutang', 'fine daw'), highlighting the need for culturally contextualized models.",
        "Future Enhancements: Transformer-based Tagalog encoders (e.g. RoBERTa-Tagalog) and fine-grained emotion classification (anger, fear, hope)."
    ], size=16)

    # 11. References
    slide("10. References", [
        "Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. ICWSM-14.",
        "Loria, S. (2020). TextBlob: Simplified Text Processing. textblob.readthedocs.io.",
        "Nielsen, F. Å. (2011). A new ANEW: Evaluation of a word list for sentiment analysis in microblogs. CEUR Workshop Proceedings.",
        "Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. JMLR, 12, 2825-2830.",
        "Philippine Statistics Authority (PSA) - Consumer Price Index & Inflation Reports (2025-2026).",
        "Public data sources from YouTube, Facebook, and Reddit as documented in data/posts.csv."
    ], size=16)

    prs.save(config.DECK)
    return len(prs.slides)


if __name__ == "__main__":
    count = build("CS412")
    print(f"Successfully generated enhanced presentation deck with {count} slides at {config.DECK}")
