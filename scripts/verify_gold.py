"""Check that every gold row is printed in the books: the Barranquenho text, and each alternative, must appear on a
page the row cites. A row that fails names the pages where the text does appear.

    python scripts/verify_gold.py gold/books.tsv convencao=<pdf> gramatica=<pdf>
"""
import csv
import re
import subprocess
import sys


def norm(s):
    s = s.lower().replace("’", "'").replace("´", "'").replace("‘", "'")
    return re.sub(r"[\s'.,;:?!()\"“”-]+", " ", s).strip()


def main():
    gold, books = sys.argv[1], dict(a.split("=", 1) for a in sys.argv[2:])
    pages = {}
    for name, pdf in books.items():
        text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
        for i, page in enumerate(text.split("\f"), 1):
            page = re.sub(r"(Gramática Básica de Barranquenho|Convenção Ortográfica do Barranquenho)\s*\n", "", page)
            page = re.sub(r"(?m)^\s*\d+\s*$", "", page)              # page numbers
            pages[f"{name[0]}{i}"] = norm(page)
    rows = list(csv.DictReader(open(gold, encoding="utf-8"), delimiter="\t"))
    bad = 0
    for r in rows:
        for form in [r["barr"], r["pt"]] + [a for a in r["alt"].split("|") if a.strip()]:
            f = norm(form)
            cited = [p for p in r["pages"].split(";") if f in pages.get(p, "")]
            if not cited and f in " ".join(pages.get(p, "") for p in r["pages"].split(";")):
                cited = [r["pages"]]                                 # the text runs across a page break
            if not cited:
                bad += 1
                found = [p for p, t in pages.items() if f in t]
                print(f"{r['id']}\t{form!r}\tcited {r['pages']}\tfound on {','.join(found) or 'no page'}")
    print(f"rows={len(rows)} forms not on a cited page={bad}", file=sys.stderr)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
