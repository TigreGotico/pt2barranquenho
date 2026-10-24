# Constructions

These rules change more than the spelling of one word. Each one cites the book section that prints it. Where the books give only examples, the code adds conditions from Portuguese grammar so that ordinary sentences keep their meaning. `tests/test_sentences.py` holds a test for each condition below.

## Pronoun placement

A pronoun after a hyphen moves before the verb, except after an infinitive (Gramática IV 1.1). On an infinitive after an auxiliary, it moves before the auxiliary (Gramática IV 1.3).

| Portuguese | Barranquenho |
| --- | --- |
| A minha mãe disse-me | A minha mãi me dissi |
| Quero fazê-lo | Queru fazê-lu |
| Vou lavar-me | Me bô a labá |
| Estou a ver-te | Te tô bendu |

## Periphrases

*estar a* + infinitive takes the gerund, and *ir* + infinitive takes *a* (Convenção 3.1). *ter de* + infinitive becomes *ter que* (Convenção 2.7). *foi* and *foram* + infinitive count as *ir* only at the start of a clause or after a subject pronoun or an adverb, because they are also forms of *ser*.

| Portuguese | Barranquenho |
| --- | --- |
| foi ver os pais | foi a bê uh pai |
| Ele tem de sair | Eli ten que saí |

## *se*: pronoun or conjunction

The Convenção writes the conjunction *si* and the pronoun *se* (1.1). The Portuguese input does not mark the difference, so the code decides from the neighbouring words: pt-PT never opens a clause with an unstressed pronoun.

| Portuguese | Barranquenho |
| --- | --- |
| Se tens fome | Si ten fomi |
| Não sei se vem | Nãu sê si ben |
| e se parava | i se paraba |

## Pseudo-reflexive verbs

*casar*, *cair*, *morrer*, *sair*, *dormir* and *ir* take a pronoun of the same person (Gramática IV 1.4, Convenção 1.7): *Eu casei* > *Eu me casê*, *já morreu* > *já se morreu*. *foram* takes the pronoun only as a verb of motion.

## *gostar*

*gostar* loses *de* and takes a dative pronoun before a 3rd person form (Gramática IV 1.2, Convenção 3.1). A subject pronoun becomes *a* + the stressed pronoun.

| Portuguese | Barranquenho |
| --- | --- |
| gosta de tomar umas chispas | le gohta tomá umah chihpa |
| Eu não gosto do mar | A min nãu me gohta u má |
| porque gostamos dela | porqui nuh gohta |
| Gostava de saber isso | Me gohtaba sabê issu |
| O meu avô gostava de pescar | U mê abô le gohtaba pehcá |

The conditions:

- *gostava* and *gostaria* are 1st or 3rd person. At the start of a clause they take the polite 1st person of pt-PT (*me*); after a noun, the 3rd person (*le*).
- A 3rd person pronoun liked goes with its *de*: the Gramática prints *porqui nuh guhtô* for *porque gostamos dela*.
- *gosto* is the noun after a determiner, a preposition or a form of *ter*, and when nothing liked follows: *com muito gosto*, *Gosto é gosto*.
- A 1st or 2nd person liked keeps *de* and the Portuguese verb (*gosto de ti* > *gohtu de ti*). The books print no form for it.

## *faz* + a span of time

An impersonal *faz* before a span of time becomes *há*, written *ai* (Convenção 3.1). The span needs an amount, and it must end the phrase or open a *que* clause. Otherwise *faz* is the weather, a birthday or a habit.

| Portuguese | Barranquenho |
| --- | --- |
| pois faz vinte anos | poih ai binti anu |
| Hoje faz bom tempo | Oji fah bon tempu |

## The compound perfect

In a span of time that still goes on, Barranquenho uses *ter* + participle where Portuguese uses the preterite (Gramática III 1.2.5.1).

| Portuguese | Barranquenho |
| --- | --- |
| Hoje atei-me o lenço | Oji me tenhu atadu u lençu |
| Ontem comprei pão | Onten comprê pãu |

The rule applies only next to *hoje*, *este ano* or a similar span, and only to the 1st and 3rd person singular. It stops at a comma or a subordinate clause, and it skips a clause dated with *ontem*, *há dez anos* or a year. It leaves out the forms in *-arei*, *-erei*, *-irei* and *-orei*, which can be futures, and a word after an article, which is a noun. Other uses of the compound perfect depend on meaning and are not rewritten.

## Gender

A noun whose gender follows Spanish changes the article or demonstrative before it, in the singular and the plural and in the contractions (Gramática III 1.1.1, III 1.1.4).

| Portuguese | Barranquenho |
| --- | --- |
| As laranjeiras | Uh laranjêru |
| nos seixos | nah china |
| A minha mãe disse-me que o leite estava frio. | A minha mãi me dissi que a lêti ehtaba friu. |

The change reaches the determiner just before the noun, not an adjective or a possessive.

## Words from the books

Thirteen nouns take the Barranquenho word the Gramática prints in place of the Portuguese one, each also in the 2025 dictionary: *Tenho cócegas* > *Tenhu cohquilha*, *nos seixos* > *nah china*. The dictionary lists many more words beside their Portuguese cognates, but context decides which one a speaker uses, so the rules use only these.
