"""Step 1a — the router (rung 2: classical ML). Ticket text -> status | impact | cause_credit | unrelated, with a confidence.
Trained on data/tickets_synthetic.csv (synthetic, never the eval-set). Word + character n-grams, so short and non-English tickets still get a score."""
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline, make_union

DATA = os.path.join(os.path.dirname(__file__), "data", "tickets_synthetic.csv")
MODEL = None


def train(csv_path=DATA):
    """Fit TF-IDF (words + characters) + logistic regression on text -> category. Return the fitted pipeline."""
    global MODEL
    df = pd.read_csv(csv_path)
    features = make_union(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
                          TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True))
    MODEL = make_pipeline(features, LogisticRegression(max_iter=2000))
    MODEL.fit(df["text"], df["category"])
    return MODEL


def predict(text):
    """Return (category, confidence). Confidence = max predict_proba."""
    if MODEL is None:
        train()
    proba = MODEL.predict_proba([text])[0]
    i = proba.argmax()
    return MODEL.classes_[i], float(proba[i])
