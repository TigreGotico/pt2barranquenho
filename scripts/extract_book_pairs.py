"""Extract candidate Portuguese/Barranquenho pairs from the glosses of the 2025 books, with the PDF page of each.

The books gloss Barranquenho examples as `bar1, bar2 (pt. 'pt1, pt2')`. Lists of equal length align item by item.
The output is a candidate list for review, not gold: every row is checked by hand before it enters gold/books.tsv.

    python scripts/extract_book_pairs.py convencao=<pdf> gramatica=<pdf> > candidates.tsv
"""
import re
import subprocess
import sys

GLOSS = re.compile(r"([^():;•▪<>]{2,160}?)\s*\((?:'|‘)?\s*(?:pt|port|por)\.?\s*([^)]{1,200})\)")
STRIP = " .‘’'\"“”-"


def pages(pdf):
    text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    return text.split("\f")


def main():
    seen = set()
    n_gloss = 0
    print("pt\tbarr\tsource\tpage")
    for arg in sys.argv[1:]:
        source, pdf = arg.split("=", 1)
        for page_no, page in enumerate(pages(pdf), 1):
            for m in GLOSS.finditer(re.sub(r"\s+", " ", page)):
                n_gloss += 1
                left = re.split(r"[:–]| - ", m.group(1))[-1]
                right = re.sub(r"esp\.[^,]*,?", "", m.group(2)).strip("‘’'\"“” ")
                bar = [w.strip(STRIP) for w in re.split(r"[,;]", left) if w.strip(STRIP)]
                pt = [w.strip(STRIP) for w in re.split(r"[,;]", right) if w.strip(STRIP)]
                if bar and len(bar) == len(pt):
                    for b, p in zip(bar, pt):
                        if (p, b, source) not in seen:
                            seen.add((p, b, source))
                            print(f"{p}\t{b}\t{source}\t{page_no}")
    print(f"glosses={n_gloss} pairs={len(seen)}", file=sys.stderr)


if __name__ == "__main__":
    main()
