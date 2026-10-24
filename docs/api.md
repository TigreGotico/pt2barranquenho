# API

The package exports two functions and one command.

## `translate(text: str) -> str`

`translate` converts one sentence or line of pt-PT text. It keeps the spacing and the punctuation of the input.

```python
translate("Estou a ver-te")       # 'Te tô bendu'
translate("Ainda hoje são amigos") # 'Inda oji sãu amigu'
```

Give it one sentence or one line at a time. Several rules look at the neighbouring words in the same clause: the pronoun *se* against the conjunction *se*, the place of a clitic, the determiner before a noun whose gender changes, and the constructions on the [Constructions page](constructions.md). A text with many sentences works, but a rule never looks past a full stop, a semicolon, a colon, a question mark or an exclamation mark. A text with several lines is translated line by line, so each line keeps its own case.

**Case.** A capital at the start of a word stays (*Ontem* > *Onten*). A line in capitals is converted in lowercase and given back in capitals (*ÉS TU?* > *ERI TÚ?*).

**What stays unchanged:**

- Template slots in braces: `{name}`.
- Numbers, Roman numerals and acronyms: *1940*, *VIII*, *PCP*.
- Initials: *E.* in *Joseph E. Johnston*.
- A name with an apostrophe between two letters (*O'Keeffe*, *d'Arc*) or with a capital inside (*McMaster*).
- A word with a letter that Portuguese does not use: *k*, *w*, *y*, *ll*, *th* or a final *t* (*William Shakespeare*). The Gramática keeps the spelling of imported names (II 2).

In a hyphenated compound, each part is checked on its own: *não-Ford* gives *nãu-Ford*, and *EUA-Japão* gives *EUA-Japãu*.

An imported name with Portuguese spelling still changes: *Peter* gives *Petê*. The spelling alone does not tell it from a Portuguese word.

## `word(w: str) -> str`

`word` converts one lowercase Portuguese word with the spelling rules only. It does not move pronouns, change determiners or apply any construction.

```python
word("fazer")      # 'fazê'
word("cantavam")   # 'cantabon'
word("três")       # 'trêh'
```

`word` first looks the word up in the closed classes of the Gramática: articles, pronouns, possessives, demonstratives, indefinites, interrogatives, numerals and irregular verb forms. Other words go through the spelling rules on the [How it works page](how-it-works.md). Give it a lowercase word; a capital is not handled.

## Command `pt2barranquenho`

The command reads standard input and prints `translate(line)` for each line, with the line's outer whitespace removed.
