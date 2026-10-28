import argparse
import csv
import sys

from .evaluate import evaluate, load, reply_rates
from .rules import classify


def main():
    ap = argparse.ArgumentParser(description="Classify cold-email replies.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("eval", help="score against a labeled CSV (columns: text,label)")
    e.add_argument("path")
    e.add_argument("--errors", action="store_true", help="print every miss")
    e.add_argument("--method", choices=["rules", "llm"], default="rules")
    e.add_argument("--model", default="openai/gpt-4o-mini")
    c = sub.add_parser("classify", help="label a CSV with a 'text' column; writes to stdout")
    c.add_argument("path")
    r = sub.add_parser("rates", help="raw vs human reply rate for a CSV of replies")
    r.add_argument("path")
    r.add_argument("--contacted", type=int, required=True)
    a = ap.parse_args()

    if a.cmd == "eval":
        clf = classify
        if a.method == "llm":
            from .llm import classify_llm
            clf = lambda t: classify_llm(t, a.model)
        res = evaluate(load(a.path), clf)
        print(f"n={res['n']}  accuracy={res['accuracy']:.1%}")
        for lab, m in res["per_label"].items():
            p = "-" if m["precision"] is None else f"{m['precision']:.0%}"
            rc = "-" if m["recall"] is None else f"{m['recall']:.0%}"
            print(f"  {lab:15} precision {p:>4}  recall {rc:>4}  support {m['support']}")
        if a.errors:
            for text, true, pred in res["errors"]:
                print(f"\nMISS true={true} pred={pred}: {text}")
    elif a.cmd == "classify":
        rows = load(a.path)
        w = csv.writer(sys.stdout)
        w.writerow(["text", "label"])
        for row in rows:
            w.writerow([row["text"], classify(row["text"])[0]])
    else:
        labels = [classify(row["text"])[0] for row in load(a.path)]
        res = reply_rates(a.contacted, labels)
        for k, v in res.items():
            print(f"{k}: {v:.2%}" if isinstance(v, float) else f"{k}: {v}")


if __name__ == "__main__":
    main()
