"""Score the classifier against a labeled CSV and compute honest reply rates."""
import csv
from collections import Counter

from .rules import HUMAN, MACHINE, classify


def load(path: str) -> list[dict]:
    return list(csv.DictReader(open(path, newline="")))


def evaluate(rows: list[dict], clf=classify) -> dict:
    preds = [clf(r["text"])[0] for r in rows]
    labels = sorted({r["label"] for r in rows} | set(preds))
    pairs = [(r["label"], p) for r, p in zip(rows, preds)]
    per = {}
    for lab in labels:
        tp = sum(1 for t, p in pairs if t == lab and p == lab)
        fp = sum(1 for t, p in pairs if t != lab and p == lab)
        fn = sum(1 for t, p in pairs if t == lab and p != lab)
        prec = tp / (tp + fp) if tp + fp else None
        rec = tp / (tp + fn) if tp + fn else None
        per[lab] = {"precision": prec, "recall": rec, "support": tp + fn}
    correct = sum(1 for t, p in pairs if t == p)
    return {"n": len(rows), "accuracy": correct / len(rows), "per_label": per,
            "errors": [(r["text"], t, p) for r, (t, p) in zip(rows, pairs) if t != p]}


def reply_rates(contacted: int, predicted_labels: list[str]) -> dict:
    """Raw vs human reply rate. The denominator is CONTACTED, never replies."""
    c = Counter(predicted_labels)
    machine = sum(c[l] for l in MACHINE)
    human = sum(c[l] for l in HUMAN)
    return {"contacted": contacted, "raw_reply_rate": len(predicted_labels) / contacted,
            "machine_replies": machine, "human_replies": human,
            "human_reply_rate": human / contacted,
            "positive": c["positive"], "positive_rate": c["positive"] / contacted}
