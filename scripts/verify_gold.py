"""Check that every gold row is printed in the books: the Barranquenho text, and each alternative, must appear on a
page the row cites. A row that fails names the pages where the text does appear.

    python scripts/verify_gold.py gold/books.tsv convencao=<pdf> gramatica=<pdf>
"""
import csv
import re
import subprocess
import sys
from pathlib import Path


def norm(s):
    s = s.lower().replace("’", "'").replace("´", "'").replace("‘", "'")
    return re.sub(r"[\s'.,;:?!()\"“”-]+", " ", s).strip()


def load_pages(books):
    """Normalised text of every PDF page, keyed c1, c2, ... for the Convenção and g1, g2, ... for the Gramática."""
    pages = {}
    for name, pdf in books.items():
        text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
        for i, page in enumerate(text.split("\f"), 1):
            page = re.sub(r"(Gramática Básica de Barranquenho|Convenção Ortográfica do Barranquenho)\s*\n", "", page)
            page = re.sub(r"(?m)^\s*\d+\s*$", "", page)              # page numbers
            pages[f"{name[0]}{i}"] = norm(page)
    return pages


def check(row_id, forms, cited_pages, pages):
    """Print and count the forms that are not on a cited page."""
    bad = 0
    for form in forms:
        f = norm(form)
        cited = [p for p in cited_pages if f in pages.get(p, "")]
        if not cited and f in " ".join(pages.get(p, "") for p in cited_pages):
            cited = cited_pages                                      # the text runs across a page break
        if not cited:
            bad += 1
            found = [p for p, t in pages.items() if f in t]
            print(f"{row_id}\t{form!r}\tcited {';'.join(cited_pages)}\tfound on {','.join(found) or 'no page'}")
    return bad


def main():
    gold, books = sys.argv[1], dict(a.split("=", 1) for a in sys.argv[2:])
    pages = load_pages(books)
    rows = list(csv.DictReader(Path(gold).read_text(encoding="utf-8").splitlines(), delimiter="\t"))
    bad = sum(check(r["id"], [r["barr"], r["pt"]] + [a for a in r["alt"].split("|") if a.strip()],
                    r["pages"].split(";"), pages) for r in rows)
    print(f"rows={len(rows)} forms not on a cited page={bad}", file=sys.stderr)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
