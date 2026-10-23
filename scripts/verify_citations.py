"""Check that every rule in rules/citations.tsv is printed in the books: the quoted text, and the example pair
when the row has one, must appear on a page the row cites.

    python scripts/verify_citations.py rules/citations.tsv convencao=<pdf> gramatica=<pdf>
"""
import csv
import sys
from pathlib import Path

from verify_gold import check, load_pages


def main():
    ledger, books = sys.argv[1], dict(a.split("=", 1) for a in sys.argv[2:])
    pages = load_pages(books)
    rows = list(csv.DictReader(Path(ledger).read_text(encoding="utf-8").splitlines(), delimiter="\t"))
    bad = sum(check(r["rule"], [f for f in (r["quote"], r["pt"], r["barr"]) if f], r["pages"].split(";"), pages)
              for r in rows)
    print(f"rules={len(rows)} quotes or examples not on a cited page={bad}", file=sys.stderr)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
