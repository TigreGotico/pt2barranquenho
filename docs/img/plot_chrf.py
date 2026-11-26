"""Draw docs/img/chrf.svg: chrF2 of the copy floor and of the rules on each gold set.

Run from the repo root: python docs/img/plot_chrf.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from plot_style import save  # noqa: E402


def sets():
    results = json.loads((ROOT / "benchmarks" / "results.json").read_text(encoding="utf-8"))
    return [{"set": name, "rows": cells["all"]["rows"], "copy": cells["all"]["copy_chrf2"],
             "rules": cells["all"]["rules_chrf2"]} for name, cells in results.items()]


def draw(fig, theme, rows):
    ax = fig.subplots()
    y = range(len(rows))
    for i, r in zip(y, rows):
        ax.plot([r["copy"], r["rules"]], [i, i], color=theme["grid"], linewidth=3, zorder=1)
    ax.scatter([r["copy"] for r in rows], list(y), s=40, color=theme["muted"], label="copy the Portuguese", zorder=3)
    ax.scatter([r["rules"] for r in rows], list(y), s=40, color=theme["series"][0], label="rules", zorder=3)
    for i, r in zip(y, rows):
        ax.text(r["rules"] + 1.5, i, f"{r['rules']:.1f}", va="center", fontsize=8, color=theme["text"])
        ax.text(r["copy"] - 1.5, i, f"{r['copy']:.1f}", va="center", ha="right", fontsize=8, color=theme["text"])
    ax.set_yticks(list(y), [f"{r['set']} ({r['rows']})" for r in rows], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(20, 105)
    ax.set_xlabel("chrF2 (higher is better)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=8)


if __name__ == "__main__":
    save(str(ROOT / "docs" / "img" / "chrf"), draw, sets(), height=2.6)
