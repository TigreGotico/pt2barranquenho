"""Every gold row listed in gold/passing.txt must keep translating to its reference or an alternative. A rule
change that breaks one fails here; a change that fixes more rows adds them to the list."""
import csv
from pathlib import Path

from pt2barranquenho import translate

GOLD = Path(__file__).parent.parent / "gold"


def norm(s):
    return " ".join(s.lower().replace("’", "'").replace("´", "'").split())


def test_passing_rows_still_pass():
    lines = (GOLD / "books.tsv").read_text(encoding="utf-8").splitlines()
    rows = {r["id"]: r for r in csv.DictReader(lines, delimiter="\t")}
    expected = set(GOLD.joinpath("passing.txt").read_text().split())
    assert expected <= set(rows)
    broken = [i for i in sorted(expected)
              if norm(translate(rows[i]["pt"])) not in {norm(rows[i]["barr"])} | {norm(a) for a in rows[i]["alt"].split("|") if a.strip()}]
    assert not broken, f"rows that passed and now fail: {broken}"
