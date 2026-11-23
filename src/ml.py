"""Task 4: TF-IDF + Logistic Regression / Naive Bayes, evaluated on a held-out split.

Labels are the lexicon consensus (no hand labels), so the ML score measures how well
a model imitates the lexicons, not agreement with human judgement. Stated in the report.
"""
import json
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from src import config
from src.lexicon import LEXICONS


def run(df, col="text_en"):
    out = [f"Comments: {len(df)}", "Label distribution:", df.label.value_counts().to_string(), ""]
    Xtr, Xte, ytr, yte = train_test_split(df[col], df.label, test_size=0.2, random_state=42, stratify=df.label)
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, stop_words="english")
    A, B = vec.fit_transform(Xtr), vec.transform(Xte)
    best, metrics = None, {}
    for name, model in [("LogisticRegression", LogisticRegression(max_iter=1000, class_weight="balanced")),
                        ("NaiveBayes", MultinomialNB())]:
        pred = model.fit(A, ytr).predict(B)
        kw = dict(labels=config.LABELS, zero_division=0)
        metrics[name] = classification_report(yte, pred, output_dict=True, **kw)
        f1 = metrics[name]["macro avg"]["f1-score"]
        out += [f"== {name} ==", classification_report(yte, pred, **kw), ""]
        ConfusionMatrixDisplay(confusion_matrix(yte, pred, labels=config.LABELS),
                               display_labels=config.LABELS).plot(cmap="Blues")
        plt.title(name)
        plt.tight_layout()
        plt.savefig(config.FIGURES / f"confusion_matrix_{name}.png", dpi=150)
        plt.close()
        if best is None or f1 > best[0]:
            best = (f1, name)
    shutil.copy(config.FIGURES / f"confusion_matrix_{best[1]}.png", config.FIGURES / "confusion_matrix.png")
    out.append(f"Best ML model by macro-F1: {best[1]}")
    out += ["", "Lexicon agreement with consensus label (inflated: consensus is built from them):"]
    out += [f"  {m}: {(df[f'{m}_label'] == df.label).mean():.3f}" for m in LEXICONS]
    config.ML_RESULTS.write_text("\n".join(out))
    config.ML_METRICS.write_text(json.dumps({"best": best[1], "train": len(ytr), "test": len(yte), "models": metrics}, indent=1))
    return "\n".join(out)
