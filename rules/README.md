# Rule citations

`citations.tsv` gives the source of each rule in `pt2barranquenho`. It has 95 rows: 54 cite the *Convenção Ortográfica do Barranquenho* and 41 cite the *Gramática Básica de Barranquenho*.

| Column | Content |
| --- | --- |
| `rule` | what the rule does |
| `book` | `Convenção` or `Gramática` |
| `section` | the section number in that book; Gramática sections start with the part (`III 1.1.3`) |
| `pages` | PDF pages, `c` for the Convenção and `g` for the Gramática, separated by `;` |
| `basis` | `rule` when the section states the rule; `example` when the section only prints a form that shows it |
| `quote` | text copied from the cited page |
| `pt`, `barr` | an example pair printed on the cited page, when the book prints one |

Three checks keep the ledger and the code together:

- `scripts/verify_citations.py` checks that the quote and the example pair appear on a cited page.
- `tests/test_citations.py` translates each of the 73 example pairs and expects the printed Barranquenho.
- The same test checks both directions between code and ledger. Every section the ledger names must appear in a code comment. Every "Convenção" or "Gramática" section a comment names must appear in the ledger.

```bash
python scripts/verify_citations.py rules/citations.tsv convencao=<Convenção PDF> gramatica=<Gramática PDF>
```

## Rules without a book source

Some rules come from Portuguese grammar, not from the books, and the code comments mark them "Portuguese":

- `nuclei` and `stressed_nucleus` find the stressed syllable by the Portuguese accent rules. The books state their rules by stress, and the Portuguese spelling shows where the stress falls.
- `SUBJECTS`, `PROCLISIS`, `CONJUNCTION_NEXT`, `QUESTION_VERBS` and `SUBJUNCTIVE` tell the pronoun *se* from the conjunction *se*. The Convenção writes them differently (*se*, *si*). The Portuguese input does not mark the difference, so the code decides from the neighbouring words: pt-PT never opens a clause with an atonic pronoun.
- `IR_PAST_AFTER` decides when *foi* + infinitive is *ir* and not *ser*, and `MOTION` when *foram* is a verb of motion.
- An enclitic *-lo* restores the verb's lost *-r* or *-s* (*fazê-lo* > *fazer*).

The nouns in `LEXICON` come from the Gramática examples. The *Dicionário de Barranquenho* (2025) has an entry for each one with the same Portuguese gloss, and its corrected edition is the Hugging Face dataset `TigreGotico/dicionario_barranquenho`. Words that the dictionary glosses broadly (*barquinaçu*: queda, rombo, solavanco) are left out.

Numbers, Roman numerals and all-capital acronyms pass through unchanged. This is an implementation choice.

## Where the books disagree

The ledger cites the Convenção where the two books differ, because the Convenção is the spelling norm.

| Portuguese | Convenção | Gramática | Code |
| --- | --- | --- | --- |
| há | *ai* (3.1) | *hai* (III 1.2.5), *á* (the abê table) | *ai*. The Convenção 2.1 rule drops the etymological *h*. |
| se, conjunction | *si* (1.1) | *se* in *se nãu te tibera bindu* (III 1.2.5.3) | *si* |
| tu cantas | *tú labah*: the 2nd person keeps *-h* (2.1) | *tú canta* (IV 1.5) | *-h* |
| muita | *muita genti* (3.1) | *munta* (III 1.1.6, Tabela 9) | *munta*. Convenção 1.8.3 writes the reduced [ũ] as *un*. |
| hora | no example | *qualqué hora* (III 1.1.6) | *ora*, by the Convenção 2.1 *h* rule |
| qual | *cual* (2.6) | *quà* (III 1.1.7, Tabela 10) | *cual* |
| também | *tamén* (sound table) | *tambén* (III 1.1.2) | *tamén* |
| quatro | *cuatru* (2.4) | *quatru* (III 1.1.8) | *cuatru* |
| está a perceber-me | no example | *m'ehtá a percebé*, and *nuh ehtá bendu* for *está-nos a ver* (IV 1.1, IV 1.3) | the gerund, as IV 1.3 states |
