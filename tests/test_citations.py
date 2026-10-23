"""Each rule in rules/citations.tsv and the code that applies it must agree: an example pair the row carries translates
as the book prints it, the code cites every section the ledger names, and the ledger holds every section the code
cites."""
import csv
import re
from pathlib import Path

import pytest

import pt2barranquenho
from pt2barranquenho import translate

LEDGER_PATH = Path(__file__).parent.parent / "rules" / "citations.tsv"
LEDGER = list(csv.DictReader(LEDGER_PATH.read_text(encoding="utf-8").splitlines(), delimiter="\t"))
SOURCE = Path(pt2barranquenho.__file__).read_text(encoding="utf-8")


def norm(s):
    return " ".join(s.lower().replace("’", "'").replace("´", "'").split())


@pytest.mark.parametrize("row", [r for r in LEDGER if r["pt"]], ids=lambda r: r["rule"])
def test_example_translates_as_printed(row):
    assert norm(translate(row["pt"])) == norm(row["barr"])


@pytest.mark.parametrize("citation", sorted({f"{r['book']} {r['section']}" for r in LEDGER}))
def test_code_cites_the_section(citation):
    assert citation in SOURCE


def test_every_citation_in_the_code_is_in_the_ledger():
    cited = {" ".join(m) for m in re.findall(r"(Convenção|Gramática) ((?:[IV]+ )?\d+(?:\.\d+)*|sound table)", SOURCE)}
    assert cited - {f"{r['book']} {r['section']}" for r in LEDGER} == set()
