# Contributing a rule

Every rule in `pt2barranquenho` cites a section of the *Convenção* or the *Gramática*. A rule that comes from Portuguese grammar instead says "Portuguese" in its comment and is listed in `rules/README.md`. Where the two books disagree, the Convenção wins, and `rules/README.md` records the form the code follows.

## Steps

1. **Find the source.** Read the section of the book that states the rule or prints the form. Note the PDF page: `c` for the Convenção, `g` for the Gramática.
2. **Write a failing test.** Add an ordinary pt-PT sentence and its expected Barranquenho to `tests/test_sentences.py`, with a comment that names the section. Run the test and see it fail. A test that passes before the change proves nothing.
3. **Change the code.** Put the rule in `pt2barranquenho/__init__.py` with a comment that names the section, such as `# Convenção 2.1: tehtu`.
4. **Add a ledger row.** Add a row to `rules/citations.tsv` with the section, the page, a quote from the page and, if the book prints one, an example pair. `tests/test_citations.py` fails while the code and the ledger name different sections.
5. **Check the quote.** Run `scripts/verify_citations.py` against the two PDFs. It reports each quote or example that is not on its cited page.
6. **Run the full suite** and the evaluation on all four gold sets. A rule that fixes its own test can break other sentences, and the gold sets show it.

```bash
uv run --with pytest --with sacrebleu --with-editable . python -m pytest -q
python scripts/verify_citations.py rules/citations.tsv convencao=<Convenção PDF> gramatica=<Gramática PDF>
for f in books convention_text external_respelled external; do
  uv run --with sacrebleu --with-editable . python scripts/evaluate.py gold/$f.tsv | grep '^| all'
done
```

## When the books give no rule

Some sentences need a choice the books do not make: *gosto de ti*, the vowel quality of a final *-or*, a foreign name spelled like a Portuguese word. Leave the Portuguese construction and record the limit in `README.md`. A guess that looks like a rule is harder to find and remove later than a documented limit.

## Words from the dictionary

A noun goes into `LEXICON` only when the Gramática prints the Barranquenho word in place of the Portuguese one and the 2025 dictionary gives the same gloss. Used as a word list, the dictionary lowers the scores, because most entries sit beside a Portuguese cognate that speakers also use.
