# pt2barranquenho

`pt2barranquenho` translates European Portuguese text into Barranquenho with hand-written rules. It is a baseline: no parallel corpus of Barranquenho exists to train a statistical model, so the rules come from the language's two reference books.

[Barranquenho](https://en.wikipedia.org/wiki/Barranquenho) is the language of Barrancos, a municipality of about 1,500 people on the Portuguese border with Spain. It has a Portuguese base with Andalusian and Extremaduran Spanish features. Portugal recognised it as cultural heritage in 2021, and its first orthographic convention, grammar and dictionary appeared in 2025.

## Install and use

```bash
uv pip install -e .
echo "A minha mãe disse-me que o leite estava frio." | pt2barranquenho
# A minha mãi me dissi que a lêti ehtaba friu.
```

```python
from pt2barranquenho import translate, word

translate("Ontem fomos à feira e comprámos três quilos de feijão.")
# 'Onten fomu à fêra i compramu trêh quilu de fejãu.'
word("espanhol")   # 'ehpanhó'
```

`translate` takes one sentence or line. `word` converts one lowercase word with no context.

## Sources

The rules follow two books. Section numbers in the code refer to the Gramática.

- Gonçalves, M. F., Navas, M. V. and Correia, V. M. D. (2025). *Convenção Ortográfica do Barranquenho*. Évora: Universidade de Évora. ISBN 978-972-778-463-9.
- Gonçalves, M. F., Navas, M. V. and Correia, V. M. D. (2025). *Gramática Básica de Barranquenho*. Évora: Universidade de Évora. ISBN 978-972-778-464-6.

## What the rules do

| Area | Portuguese | Barranquenho |
| --- | --- | --- |
| Spelling | `v`, initial `h` | `b`, dropped: *viva* > *biba*, *homem* > *omen* |
| Final vowels | unstressed `-o`, `-e` | `-u`, `-i`: *tempo* > *tempu*, *sempre* > *sempri* |
| Sibilants | `s`, `z`, `x` before a consonant | `h`: *Lisboa* > *Lihboa*, *texto* > *tehtu* |
| Final `-s` | on determiners and monosyllables | `h`: *os* > *uh*, *três* > *trêh* |
| Final `-s` | on nouns, adjectives and verbs | dropped: *os meninos* > *uh meninu* |
| Final `-l`, `-r`, `-z` | after the stressed vowel | dropped, vowel accented: *azul* > *azú*, *fazer* > *fazê* |
| Diphthongs | `ei`, `ou`, `-ão`, `-ães`, `-ões` | `ê`/`e`, `ô`/`o`, `-ãu`, `-ãi`, `-õi` |
| Verbs | `-ava`, `-avam`, `-amos`, `-ámos` | `-aba`, `-abon`, `-emu`, `-amu` |
| Pronouns | enclitic after a hyphen | proclitic: *casei-me* > *me casê*; elided before a vowel |
| Periphrases | *estar a* + infinitive; *ir* + infinitive | gerund; *í a* + infinitive |
| Pseudo-reflexives | *casar*, *cair*, *morrer*, *sair*, *dormir*, *ir* | take *se*: *já morreu* > *já se morreu* |
| Closed classes | articles, contractions, pronouns, possessives, demonstratives, indefinites, numerals | the tables of the Gramática |

## Evaluation

`gold/books.tsv` holds 307 Portuguese and Barranquenho pairs. Each one is printed in the books, and `scripts/verify_gold.py` checks every row against the page it cites. Each row has a kind (word, phrase, sentence) and a class:

- **regular**: the rules can predict it.
- **syntax**: it needs a construction rule.
- **lexical**: Barranquenho uses a different word, such as *cucarabacha* for *barata*.
- **idiom**: a fixed expression.

| Subset | Rows | Copy the Portuguese: exact | chrF2 | pt2barranquenho: exact | chrF2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| all | 307 | 0.091 | 40.5 | 0.811 | 82.3 |
| words | 212 | 0.123 | 44.2 | 0.877 | 81.4 |
| phrases | 42 | 0.048 | 37.6 | 0.857 | 90.2 |
| sentences | 53 | 0.000 | 39.5 | 0.509 | 80.6 |
| regular | 228 | 0.123 | 45.1 | 0.939 | 94.6 |
| syntax | 44 | 0.000 | 39.9 | 0.636 | 83.9 |
| lexical | 32 | 0.000 | 26.3 | 0.219 | 44.0 |
| idiom | 3 | 0.000 | 28.9 | 0.000 | 31.5 |

"Exact" accepts the reference or any alternative printed in the books, after lowercasing. chrF2 is corpus chrF from sacrebleu.

```bash
uv run --with sacrebleu --with-editable . python scripts/evaluate.py gold/books.tsv --errors
```

**This gold set is a development set, not a test set.** The rules were written from the same books, so these numbers show how well the rules cover the books' own examples. They do not measure translation of unseen text.

`gold/external.tsv` holds 36 pairs from outside the books: a municipal language study, community sayings, field transcriptions, press quotes and a blog. The rules never saw them. They are a weak test. They use older or personal spellings (*xobe* for *chobi*, *-om* for *-on*), and their Portuguese is often a free gloss. No row matches exactly.

| Subset | Rows | Copy the Portuguese: chrF2 | pt2barranquenho: chrF2 |
| --- | ---: | ---: | ---: |
| external | 36 | 37.1 | 39.2 |

A real test needs everyday Portuguese sentences that native speakers translate into the 2025 spelling.

## Limits

- Barranquenho has more variation than the books record. The books themselves disagree in places: *aqui* and *aquí*, *treh* and *trêh*, *ele* and *eli*.
- The rules do not choose Barranquenho-specific words. The 2025 dictionary lists them beside their Portuguese cognates, and context decides which one a speaker uses.
- Gender changes that follow Spanish (*o leite* > *a lêti*) cover only the nouns the Gramática names.
- Stress comes from the Portuguese accent rules. A word with irregular stress can get the wrong final vowel.
- No native speaker has reviewed the output.

## Licence

The code is Apache-2.0. The gold rows quote short examples from the two books and cite them by page. The rights to those texts stay with their authors.
