"""Task 6: build the comprehensive presentation with rich visual charts from the pipeline outputs."""
import json

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from src import config
from src.lexicon import LEXICONS


def build(section="CS412", instructor="________"):
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

    # every number on the slides is computed here, nothing is typed in by hand
    pretty = lambda m: {"LogisticRegression": "Logistic Regression", "NaiveBayes": "Naive Bayes"}.get(m, m)
    plat_name = lambda p: {"youtube": "YouTube"}.get(p.lower(), p.capitalize())
    mm = json.loads(config.ML_METRICS.read_text())
    lr, nb = mm["models"]["LogisticRegression"], mm["models"]["NaiveBayes"]
    plat = df.platform.str.capitalize().value_counts()
    plat_txt = " • ".join(f"{plat_name(k)} ({v:,} comments)" for k, v in plat.items())
    share = pd.crosstab(df.platform.str.capitalize(), df.label, normalize="index").reindex(columns=config.LABELS, fill_value=0)
    top_src = df.source_post.value_counts(normalize=True).iloc[0]
    sheet = pd.read_csv(config.SHEET)
    n_sheet, n_raw = len(sheet), len(pd.read_csv(config.RAW))
    kws = sheet.dropna(subset=["Sentiment"])["Keyword Matched"].dropna().value_counts()
    n_changed = int((df.text != df.text_en).sum())
    lang_of = sheet.drop_duplicates("Comment Text").set_index("Comment Text")["Language"]
    lang_txt = ", ".join(f"{k} ({v:,})" for k, v in df.text.map(lang_of).value_counts().items())

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.33), Inches(7.5)

    def slide(title, bullets=(), image=None, size=18):
        s = prs.slides.add_slide(prs.slide_layouts[5])
        s.shapes.title.text = title
        s.shapes.title.text_frame.paragraphs[0].font.size = Pt(32)
        t = s.shapes.title
        t.left, t.top, t.width, t.height = Inches(0.6), Inches(0.35), Inches(12.1), Inches(1.0)
        tf = s.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(6.2 if image else 12), Inches(5.5)).text_frame
        tf.word_wrap = True
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = b if b.startswith("  ") else "• " + b
            p.font.size = Pt(size)
            p.space_after = Pt(8)
        if image and (config.FIGURES / image).exists():
            s.shapes.add_picture(fig(image), Inches(7.0), Inches(1.5), width=Inches(5.8))
        return s

    # 1. Title Page
    slide(f"Sentiment Analysis: {config.TOPIC}", [
        "Group Members: Bea, Jesreal, Raphael, Gil, Angel",
        "Course: CS 413 – CS Elective 2 (Affective Computing)",
        f"Instructor: {instructor}",
        f"Section: {section}",
        f"Topic: {config.TOPIC} in the Philippines"
    ], size=22)

    # 2. Introduction
    slide("1. Introduction", [
        "Domain: Filipino public emotional reaction to rising inflation, rice prices, fuel costs, and utility bills.",
        "Why it matters: Cost-of-living fluctuations directly impact everyday survival across socioeconomic classes.",
        "Social media comments reflect real-time public sentiment, anxiety, and coping mechanisms faster than traditional economic surveys.",
        "Sentiment analysis turns a large set of unstructured comments into measurable affective signals."
    ])

    # 3. Dataset & Collection Process (Funnel Card Design like benchmark)
    s3 = prs.slides.add_slide(prs.slide_layouts[5])
    s3.shapes.title.text = "2. Dataset & Collection Process"
    s3.shapes.title.text_frame.paragraphs[0].font.size = Pt(32)
    t3 = s3.shapes.title
    t3.left, t3.top, t3.width, t3.height = Inches(0.6), Inches(0.35), Inches(12.1), Inches(1.0)

    funnel_steps = [
        (f"{n_sheet:,}", "COLLECTED", [
            f"Public comments from {df.source_post.nunique()} videos, posts and threads (data/posts.csv).",
            "Public pages only, read-only. Facebook needed a logged-in browser session."
        ], RGBColor(41, 128, 185)),
        (f"{n_raw:,}", "IDENTIFIERS REMOVED", [
            "@handles in replies stripped from every comment.",
            "Rows that were only a handle dropped."
        ], RGBColor(52, 73, 94)),
        (f"{len(df):,}", "FINAL DATASET", [
            "Exact duplicates and comments of 3 characters or fewer removed.",
            "Stored: text, date, platform, source link. No names, handles or photos."
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
    pb1.text = f"Platforms: {plat_txt}. Largest single source: {top_src:.0%} of all comments."
    pb1.font.size = Pt(13)
    pb1.font.bold = True
    pb1.font.color.rgb = RGBColor(41, 128, 185)
    pb2 = banner.add_paragraph()
    pb2.text = "Ethics: public posts only • no usernames, handles or photos stored • read-only, no interaction • dates from relative timestamps are approximate"
    pb2.font.size = Pt(12)
    pb2.font.color.rgb = RGBColor(120, 120, 120)

    # 4. Preprocessing Techniques
    slide("3. Preprocessing Techniques", [
        f"Languages (keyword-based detection): {lang_txt}.",
        f"Translation: every comment run through Google Translate (GOOGLETRANSLATE in Google Sheets, auto-detect to English); {n_changed:,} were changed.",
        "Text Cleaning: Lowercased text; stripped URLs, HTML entities, punctuation, emojis, and digits.",
        "Tokenization & Lemmatization: Segmented words using NLTK word_tokenize, filtered stopwords, and applied WordNetLemmatizer.",
        "Output Deliverables: cleaned_comments.csv and language_distribution.png"
    ], image="language_distribution.png", size=16)

    # 5. Lexicon-Based Sentiment Analysis
    slide("4. Lexicon-Based Sentiment Analysis", [
        f"Consensus Distribution across {len(df):,} comments:",
        f"    – Positive: {pct('positive')} ({dist.get('positive', 0)} comments)",
        f"    – Neutral: {pct('neutral')} ({dist.get('neutral', 0)} comments)",
        f"    – Negative: {pct('negative')} ({dist.get('negative', 0)} comments)",
        "Lexicon Agreement with Consensus Label:",
        f"    – VADER: {agree['vader']:.1%}   AFINN: {agree['afinn']:.1%}   TextBlob: {agree['textblob']:.1%}",
        "(each lexicon is one of the three voters, so these figures are inflated)",
        "Output Deliverables: lexicon_results.csv & sentiment_distribution.png"
    ], image="sentiment_distribution.png", size=16)

    # 6. ML-Based Sentiment Analysis
    slide("5. Machine Learning Sentiment Analysis", [
        "Feature Extraction: TF-IDF Vectorization with unigrams and bigrams (min_df=2, stopwords removed).",
        f"Validation: 80/20 stratified split ({mm['train']:,} train, {mm['test']:,} test).",
        "Labels: lexicon majority vote (no hand labels), so scores show how well ML imitates the lexicons.",
        f"    – Logistic Regression: {lr['accuracy']:.0%} accuracy, {lr['macro avg']['f1-score']:.2f} macro-F1",
        f"    – Multinomial Naive Bayes: {nb['accuracy']:.0%} accuracy, {nb['macro avg']['f1-score']:.2f} macro-F1",
        f"Best model by macro-F1: {pretty(best)}.",
        "Output Deliverables: ml_results.txt & confusion_matrix.png"
    ], image="confusion_matrix.png", size=16)

    # 7. Model Metrics Comparison
    b = mm["models"][mm["best"]]
    slide("6. ML Performance Comparison", [
        f"Best model by macro-F1: {pretty(best)}.",
        f"Per-class F1 ({pretty(best)}):",
        *[f"    – {k.capitalize()}: {b[k]['f1-score']:.2f} (precision {b[k]['precision']:.2f}, recall {b[k]['recall']:.2f})" for k in config.LABELS],
        f"Naive Bayes is uneven: it finds {nb['positive']['recall']:.0%} of positive comments but only {nb['neutral']['recall']:.0%} of neutral ones.",
        "Chart: model_comparison_metrics.png"
    ], image="model_comparison_metrics.png", size=16)

    # 8. Comparison & discussion (platform view)
    slide("7. Comparison & Discussion", [
        *[f"{plat_name(p)} (n={plat[p.capitalize()]:,}): {r.negative:.0%} negative, {r.neutral:.0%} neutral, {r.positive:.0%} positive" for p, r in share.iterrows()],
        f"Most negative: {plat_name(share.negative.idxmax())}. Most positive: {plat_name(share.positive.idxmax())}. Reddit is a small sample.",
        "Lexicons vs ML: lexicons score words one by one; TF-IDF + ML learns which words and phrases go with each label in this domain.",
        f"Challenges: labels come from the lexicons themselves; translation noise; sarcasm; one source is {top_src:.0%} of the data; many comments react to the video, not to prices.",
    ], image="platform_sentiment_breakdown.png", size=16)

    # 9. Topic keywords
    slide("8. Topic Keywords vs. Sentiment", [
        f"{int(kws.sum()):,} of {len(df):,} comments contain a tracked price keyword.",
        "Most frequent: " + ", ".join(f"{k} ({v})" for k, v in kws.head(7).items()) + ".",
        "The chart shows the sentiment split for each keyword; small groups are indicative only.",
    ], image="keyword_sentiment_analysis.png", size=16)

    # 10. Conclusion & Relation to Affective Computing
    slide("9. Conclusion & Relation to Affective Computing", [
        f"Emotional distribution: {pct('negative')} negative, {pct('neutral')} neutral, {pct('positive')} positive (lexicon consensus).",
        "Affective computing: comment streams give a fast, cheap signal of how people feel about prices, ahead of surveys.",
        "Limits: word-polarity lexicons built for English miss Taglish, sarcasm and context, so the signal needs culturally aware models and human-labelled data.",
        "Future Enhancements: Transformer-based Tagalog encoders (e.g. RoBERTa-Tagalog) and fine-grained emotion classification (anger, fear, hope)."
    ], size=16)

    # 11. References
    slide("10. References", [
        "Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. ICWSM-14.",
        "Loria, S. (2020). TextBlob: Simplified Text Processing. textblob.readthedocs.io.",
        "Nielsen, F. Å. (2011). A new ANEW: Evaluation of a word list for sentiment analysis in microblogs. CEUR Workshop Proceedings.",
        "Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. JMLR, 12, 2825-2830.",
        "Picard, R. W. (1997). Affective Computing. MIT Press.",
        "Public data sources from YouTube, Facebook, and Reddit as documented in data/posts.csv."
    ], size=16)

    prs.save(config.DECK)
    return len(prs.slides)


if __name__ == "__main__":
    count = build()
    print(f"Successfully generated enhanced presentation deck with {count} slides at {config.DECK}")
