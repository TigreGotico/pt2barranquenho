# pt2barranquenho documentation

`pt2barranquenho` converts European Portuguese (pt-PT) text into Barranquenho, the language of Barrancos on the Portuguese border with Spain. It uses hand-written rules from two reference books, the *Convenção Ortográfica do Barranquenho* and the *Gramática Básica de Barranquenho* (Gonçalves, Navas, Correia; Universidade de Évora, 2025). No parallel corpus of Barranquenho exists, so the rules are the baseline until native data is available.

The output follows the spelling and grammar rules of the two books. It is not a native translation: no speaker has reviewed it, and Barranquenho has words and turns of phrase that rules cannot predict.

| Page | Content |
| --- | --- |
| [Quickstart](quickstart.md) | install, the command line, the Python call, the browser demo |
| [API](api.md) | `translate` and `word`: what they accept and what they leave unchanged |
| [How it works](how-it-works.md) | the order of the passes and the spelling rules of `word` |
| [Constructions](constructions.md) | the sentence-level rules: pronouns, periphrases, *gostar*, *faz*, the compound perfect, gender |
| [Evaluation](evaluation.md) | the gold sets, the scores and the commands that produce them |
| [Contributing](contributing.md) | how to add or change a rule with its citation and its test |

Two reference files sit beside these pages. `rules/README.md` explains the citation ledger and lists the rules that come from Portuguese grammar, not from the books. `gold/README.md` describes each gold set and how it was built. The limits of the rules are listed in the main `README.md`.
