"""Score the rules and the copy floor on every gold set and write benchmarks/results.json.

    uv run --with sacrebleu --with-editable . python scripts/benchmark.py
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from evaluate import score  # noqa: E402

from pt2barranquenho import translate  # noqa: E402

ROOT = Path(__file__).parent.parent
SETS = ["books", "convention_text", "external_respelled", "external"]


def main():
    results = {}
    for name in SETS:
        rows = list(csv.DictReader((ROOT / "gold" / f"{name}.tsv").read_text(encoding="utf-8").splitlines(),
                                   delimiter="\t"))
        hyps = {"copy": [r["pt"] for r in rows], "rules": [translate(r["pt"]) for r in rows]}
        groups = defaultdict(list)
        for i, r in enumerate(rows):
            groups["all"].append(i)
            groups[f"kind={r['kind']}"].append(i)
            groups[f"class={r['class']}"].append(i)
        results[name] = {}
        for group, idx in groups.items():
            cell = {"rows": len(idx)}
            for system, h in hyps.items():
                exact, chrf = score([rows[i] for i in idx], [h[i] for i in idx])
                cell[f"{system}_exact"] = round(exact, 4)
                cell[f"{system}_chrf2"] = round(chrf, 2)
            results[name][group] = cell
    out = ROOT / "benchmarks" / "results.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"sets in {len(SETS)}, sets out {len(results)} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
