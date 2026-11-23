"""Task 6: build the 9-section presentation from the pipeline outputs."""
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt

from src import config
from src.lexicon import LEXICONS


def build(section="________"):
    df = pd.read_csv(config.LEXICON)
    ml = config.ML_RESULTS.read_text()
    posts = [u.strip() for u in open(config.POSTS) if u.strip() and not u.startswith("#")]
    dist = df.label.value_counts()
    pct = lambda k: f"{dist.get(k, 0) / len(df):.0%}"
    agree = {m: (df[f"{m}_label"] == df.label).mean() for m in LEXICONS}
    best = ml.split("Best ML model by macro-F1:")[1].split("\n")[0].strip()
    fig = lambda n: str(config.FIGURES / n)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.33), Inches(7.5)

    def slide(title, bullets=(), image=None, size=20):
        s = prs.slides.add_slide(prs.slide_layouts[5])
        s.shapes.title.text = title
        s.shapes.title.text_frame.paragraphs[0].font.size = Pt(34)
        tf = s.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(6.2 if image else 12), Inches(5.5)).text_frame
        tf.word_wrap = True
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text, p.font.size, p.space_after = "• " + b, Pt(size), Pt(8)
        if image:
            s.shapes.add_picture(image, Inches(7), Inches(1.6), width=Inches(5.9))

    pages = sorted({p.split("facebook.com/")[-1].split("/")[0] for p in posts})
    slide(f"Sentiment Analysis: {config.TOPIC}", [
        "Group: Bea, Jesreal, Raphael, Gil, Angel",
        "Course: CS 413 – CS Elective 2 (Affective Computing)",
        "Instructor: Love", f"Section: {section}", f"Topic: {config.TOPIC}"], size=24)
    slide("Introduction", [
        "Domain: Filipino public reaction to high inflation, rice and fuel prices",
        "Social media comments show how people feel about prices, faster than surveys",
        "Sentiment analysis turns thousands of comments into a measurable emotional signal"])
    slide("Dataset & Collection Process", [
        f"{len(df)} public Facebook comments from {len(posts)} public news-page posts",
        "Stored: comment text, relative timestamp, reaction count. No names, photos or profile links",
        "Public posts only; read-only (no likes, replies or posting)",
        "Non-English comments translated to English (Google Translate) for the lexicons",
        "Sources: " + ", ".join(pages)], size=18)
    slide("Preprocessing Techniques", [
        "Translate to English; lowercase; remove URLs, punctuation, digits, emojis",
        "Tokenize (NLTK); remove English stopwords; lemmatize (WordNet)",
        "Output: cleaned_comments.csv"])
    slide("Lexicon Analysis (VADER / TextBlob / AFINN)", [
        f"Consensus labels: {pct('negative')} negative, {pct('neutral')} neutral, {pct('positive')} positive",
        "Label = majority vote of the three lexicons"], image=fig("sentiment_distribution.png"))
    slide("ML-Based Analysis", [
        "TF-IDF (unigrams + bigrams) on translated text",
        "Logistic Regression and Multinomial Naive Bayes, 80/20 stratified split",
        "Labels come from lexicon consensus (see limitation)",
        f"Best model by macro-F1: {best}"], image=fig("confusion_matrix.png"))
    slide("Comparison & Discussion", [
        "Lexicon agreement with consensus: " + ", ".join(f"{k} {v:.0%}" for k, v in agree.items()),
        "Lexicon scores ignore sarcasm, Taglish slang and context",
        "ML learns domain words (bigas, presyo, gasolina) that lexicons miss",
        "Challenges: translation noise, labels derived from lexicons (circular)"], size=18)
    slide("Conclusion & Affective Computing", [
        "Cost-of-living talk is mostly negative/frustrated, often wrapped in humor",
        "Affective computing needs context + culture, not just word polarity",
        "Next: hand-labelled gold set, multilingual model (e.g. a Tagalog-aware transformer)"])
    slide("References", [
        "Hutto & Gilbert (2014). VADER. ICWSM.", "Loria. TextBlob. textblob.readthedocs.io",
        "Nielsen (2011). AFINN lexicon.", "Pedregosa et al. (2011). scikit-learn. JMLR.",
        "Public Facebook posts listed on the dataset slide"])
    prs.save(config.DECK)
    return len(prs.slides)
