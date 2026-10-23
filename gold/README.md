# Gold data

## books.tsv

`books.tsv` holds 307 pairs of European Portuguese and Barranquenho. Every pair is an example printed in the *Convenção Ortográfica do Barranquenho* (2025) or the *Gramática Básica de Barranquenho* (2025).

| Column | Content |
| --- | --- |
| `id` | `b001` to `b307` |
| `pt` | the Portuguese, as the book glosses it |
| `barr` | the Barranquenho, as printed |
| `alt` | other forms the books print for the same Portuguese, separated by `|` |
| `pages` | PDF pages: `c` for the Convenção, `g` for the Gramática, separated by `;` |
| `kind` | `word`, `phrase` or `sentence` |
| `class` | `regular`, `syntax`, `lexical` or `idiom` |
| `note` | a misprint, a disagreement between the books, or a construction |

**How it was built.** `scripts/extract_book_pairs.py` reads the glosses (`biba, dedu (pt. 'viva, dedo')`) and aligns lists of equal length. The candidates were then checked by hand:

- Rows that the extraction cut badly were dropped or repaired from the page.
- Sentences outside the gloss pattern were added: the syntax examples, the riddles and the expressions.
- Where the two books disagree, the more frequent form is the reference and the other goes in `alt`.

`scripts/verify_gold.py` then checks that both the Portuguese and every Barranquenho form appear on a cited page:

```bash
python scripts/verify_gold.py gold/books.tsv convencao=<Convenção PDF> gramatica=<Gramática PDF>
```

**Use.** This is a development set. The rules of `pt2barranquenho` come from the same books, so a score on this set measures coverage of the books, not translation of unseen text.

## passing.txt

`passing.txt` lists the ids that `pt2barranquenho` translates correctly. `tests/test_gold.py` fails when one of them breaks. When a change fixes more rows, add their ids to the list.

## Rights

The pairs quote the books, cite them by page and stay short. The rights to the texts stay with their authors.
