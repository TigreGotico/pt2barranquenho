"""Score the translator on a gold file, by kind (word, phrase, sentence) and by class, against copying the Portuguese.

A hypothesis counts as exact when it equals the reference or any alternative after lowercasing and apostrophe
normalisation. chrF2 is corpus chrF from sacrebleu against the main reference.

    python scripts/evaluate.py gold/books.tsv [--errors]
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

from sacrebleu.metrics import CHRF

from pt2barranquenho import translate


def norm(s):
    return " ".join(s.lower().replace("’", "'").replace("´", "'").split())


def score(rows, hyps):
    exact = sum(norm(h) in {norm(r["barr"])} | {norm(a) for a in r["alt"].split("|") if a.strip()}
                for h, r in zip(hyps, rows))
    chrf = CHRF().corpus_score([norm(h) for h in hyps], [[norm(r["barr"]) for r in rows]]).score
    return exact / len(rows), chrf


def main():
    rows = list(csv.DictReader(Path(sys.argv[1]).read_text(encoding="utf-8").splitlines(), delimiter="\t"))
    systems = {"copy": [r["pt"] for r in rows], "rules": [translate(r["pt"]) for r in rows]}
    groups = defaultdict(list)
    for i, r in enumerate(rows):
        groups["all"].append(i)
        groups[f"kind={r['kind']}"].append(i)
        groups[f"class={r['class']}"].append(i)
    print("| Subset | Rows | Copy exact | Copy chrF2 | Rules exact | Rules chrF2 |\n| --- | ---: | ---: | ---: | ---: | ---: |")
    for g, idx in groups.items():
        sub = [rows[i] for i in idx]
        cells = [f"{x:.3f}" if j % 2 == 0 else f"{x:.1f}" for j, x in
                 enumerate(v for name in systems for v in score(sub, [systems[name][i] for i in idx]))]
        print(f"| {g} | {len(idx)} | " + " | ".join(cells) + " |")
    if "--errors" in sys.argv:
        for h, r in zip(systems["rules"], rows):
            if norm(h) not in {norm(r["barr"])} | {norm(a) for a in r["alt"].split("|") if a.strip()}:
                print(f"{r['id']}\t{r['class']}\t{r['pt']}\t{r['barr']}\t{h}")


if __name__ == "__main__":
    main()
