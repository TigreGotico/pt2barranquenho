# Evaluation

Four gold files test the translator. `gold/README.md` describes their columns and how each was built.

| Set | Rows | What it is | Copy the Portuguese: chrF2 | Rules: exact | Rules: chrF2 |
| --- | ---: | --- | ---: | ---: | ---: |
| `gold/books.tsv` | 321 | the examples of the two books, each checked on its page | 40.3 | 0.841 | 85.1 |
| `gold/convention_text.tsv` | 8 | the text the Convenção prints to show the norm applied | 59.1 | 0.250 | 94.8 |
| `gold/external_respelled.tsv` | 34 | sentences from other sources, respelled into the 2025 norm | 34.2 | 0.118 | 61.7 |
| `gold/external.tsv` | 36 | the same sentences in their published spelling | 37.1 | 0.000 | 40.8 |

"Exact" accepts the reference or any alternative the books print, after lowercasing. chrF2 is corpus chrF from sacrebleu. "Copy the Portuguese" scores the input unchanged, as a floor.

## What each set measures

- `books.tsv` is a development set. The rules come from the same books, so its score measures how well the rules cover the books, not how well they translate unseen text.
- `convention_text.tsv` is the best test of running text. The rules were not written from it, but it is short.
- The two external sets are the only text the rules were not built from. Most of it predates the 2025 norm, and its Portuguese is often a free gloss. The respelled set changes only the spelling, so the difference between the two sets shows how much of the error is spelling.

A full test needs everyday Portuguese sentences that native speakers translate into the 2025 spelling. No such set exists yet.

## Commands

```bash
# Scores, by subset, for one gold file
uv run --with sacrebleu --with-editable . python scripts/evaluate.py gold/books.tsv

# The same, with every row the rules get wrong
uv run --with sacrebleu --with-editable . python scripts/evaluate.py gold/convention_text.tsv --errors

# Check that each gold pair is printed on its cited page
python scripts/verify_gold.py gold/books.tsv convencao=<Convenção PDF> gramatica=<Gramática PDF>
```

## Tests

`tests/` holds four suites:

| File | What it checks |
| --- | --- |
| `test_citations.py` | each example pair in `rules/citations.tsv` translates as printed, and the code and the ledger cite the same sections |
| `test_paradigms.py` | every person of the seven verb tables of the Gramática (*amá*, *comê*, *partí*, *sê*, *ehtá*, *abê*, *tê*), except where the books disagree |
| `test_closed_classes.py` | the 118 forms of the pronoun, possessive, demonstrative, relative, indefinite and numeral tables |
| `test_sentences.py` | ordinary sentences, one rule or one condition each |

```bash
uv run --with pytest --with sacrebleu --with-editable . python -m pytest -q
```
