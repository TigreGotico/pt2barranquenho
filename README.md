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

`translate` takes one sentence or line. It leaves template slots such as `{name}` as they are, so it can convert OVOS dialog files. `word` converts one lowercase word with no context.

## Sources

The rules follow two books. Each rule in the code names the section it comes from, and `rules/citations.tsv` quotes that section with its page; `rules/README.md` explains the checks and lists the places where the two books disagree.

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
| Pronouns | enclitic after a hyphen | before the verb, except after an infinitive: *casei-me* > *me casê*, *fazê-lo* > *fazê-lu*; elided before a vowel |
| Periphrases | *estar a* + infinitive; *ir* + infinitive | gerund; *í a* + infinitive |
| Pseudo-reflexives | *casar*, *cair*, *morrer*, *sair*, *dormir*, *ir* | take a pronoun of the same person: *já morreu* > *já se morreu*, *casei* > *me casê* |
| Conjunction *se* | *se* that is not an object pronoun | *si*: *como se fosse* > *comu si fossi* |
| Possessives | before a noun; tonic | *mê*, *tê*, *sê*; *meu*, *teu*, *seu*: *os meus também* > *uh meu tamén* |
| [kw], [gw] before *e*, *i* | *cinquenta*, *aguentar* | *cincuenta*, *agüentá* |
| Closed classes | articles, contractions, pronouns, possessives, demonstratives, indefinites, interrogatives, numerals | the tables of the Gramática |
| Noun gender | nouns whose gender follows Spanish | the article or demonstrative takes the other gender, singular and plural: *as laranjeiras* > *uh laranjêru*, *nos seixos* > *nah china* |
| Words | 13 nouns the books print in place of the Portuguese word, each also in the 2025 dictionary | *cócegas* > *cohquilha*, *javali* > *jabardu*, *pessegueiro* > *melacatonêru* |

## Evaluation

Four gold files test the translator. Each has the same columns; `gold/README.md` describes them.

| Set | Rows | What it is | Copy the Portuguese: chrF2 | pt2barranquenho: exact | pt2barranquenho: chrF2 |
| --- | ---: | --- | ---: | ---: | ---: |
| `convention_text.tsv` | 8 | the text the Convenção uses to show the norm applied: a municipal description of the Igreja Matriz, in Portuguese and in Barranquenho | 59.1 | 0.250 | 94.8 |
| `books.tsv` | 321 | the examples of the two books, each verified on its page | 40.3 | 0.841 | 84.4 |
| `external_respelled.tsv` | 34 | sentences from other sources, respelled into the 2025 norm | 34.2 | 0.088 | 60.3 |
| `external.tsv` | 36 | the same sentences in their published spelling | 37.1 | 0.000 | 39.4 |

"Exact" accepts the reference or any alternative printed in the books, after lowercasing. chrF2 is corpus chrF from sacrebleu.

```bash
uv run --with sacrebleu --with-editable . python scripts/evaluate.py gold/convention_text.tsv --errors
```

**`convention_text.tsv` is the best test of running text.** The rules were not written from it. It was first scored at chrF2 92.1 before any fix it prompted (Roman numerals, hyphenated compounds, *tamén*). It is short, and its Barranquenho is the authors' own rendering of a Portuguese original.

**`books.tsv` is a development set.** The rules come from the same books, so it measures how well the rules cover the books' own examples.

**The external sets test unseen speech.** The sources predate the 2025 norm and use their own spelling, and their Portuguese is often a free gloss. `external_respelled.tsv` keeps each speaker's words and grammar and changes only the spelling, following the Convenção. An independent review checked every row against the Convenção and the Gramática (`gold/external_respelled_review.tsv`). The respelling follows the same norm as the rules, so its scores are higher than `external.tsv`. Only the differences in words and grammar are evidence the respelling did not create.

A full test needs everyday Portuguese sentences that native speakers translate into the 2025 spelling.

## Limits

- Barranquenho has more variation than the books record. The books themselves disagree in places: *aqui* and *aquí*, *treh* and *trêh*, *ele* and *eli*.
- The rules choose a Barranquenho-specific word only for the 13 nouns the books print. The 2025 dictionary lists many more beside their Portuguese cognates, and context decides which one a speaker uses. Used as a word list, the dictionary lowers the scores.
- Gender changes that follow Spanish (*o leite* > *a lêti*) cover only the nouns the books name. The change reaches the determiner just before the noun, not an adjective or a possessive: *a minha macieira* keeps *minha*.
- A word keeps its spelling when it has a letter or a sequence Portuguese does not use (*k*, *w*, *y*, *ll*, *th*, *hn*, a final *t*), because the Gramática keeps the spelling of imported names. Initials (*E.*), names with an apostrophe (*O'Neill*) or a capital inside (*McMaster*), and words that start with *s* and a consonant (*Stefan*) also stay. An imported name spelled like a Portuguese word still changes: *Lars* gives *Lar*.
- Stress comes from the Portuguese accent rules. A word with irregular stress can get the wrong final vowel.
- The Portuguese spelling does not show vowel quality, so a final stressed *e* or *o* can take the wrong accent: *flor* gives *flô*. The code knows *caló* and *capela-mó* only because the books print them.
- The pronoun *se* and the conjunction *se* are told apart from the neighbouring words. A sentence fragment, or a pronoun at the start of a clause, gets *si*.
- The 2nd person singular keeps its *-h* only after *tú* or *te*, and in the irregular forms no noun shares (*ehtáh*, *tinhah*). Without the pronoun, *comes* and *come* look alike to the rules. *eras*, *foras* and *estavas* need *tú* too, because *eras* and *foras* are also nouns.
- The 2nd person plural (*vós*) is not translated. Portuguese from Portugal uses *vocês* in its place, and the tables print the *vós* forms with variants.
- `tests/test_paradigms.py` checks every person the Gramática tables print for *amá*, *comê*, *partí*, *sê*, *ehtá*, *abê* and *tê*, except the forms where the books disagree. `tests/test_closed_classes.py` does the same for the pronoun, possessive, demonstrative, relative, indefinite and numeral tables.
- *-amos* becomes *-emu*, except in the present subjunctive of the verbs in a closed list of stems (*comamu*, *partamu*). A subjunctive outside the list gets *-emu*.
- *foi*, *foram* + infinitive count as *ir* only at the start of a clause or after a subject pronoun or an adverb, because they are also forms of *ser*.
- No native speaker has reviewed the output.

## Licence

The code is Apache-2.0. The gold rows quote short examples from the two books and cite them by page. The rights to those texts stay with their authors.
