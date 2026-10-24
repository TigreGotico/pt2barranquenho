# How it works

`translate` runs in three stages. First, passes over the Portuguese text rewrite the constructions that span several words. Then a loop converts each word, looking at its neighbours. Last, a pass elides the pronouns before a vowel. All the code is in `pt2barranquenho/__init__.py`. Each rule carries a comment that names its book section, such as `Convenção 2.1` or `Gramática III 1.2.5.4`.

## Stage 1: passes over the Portuguese text

The passes run in this order, and each one works on Portuguese, before any spelling changes:

1. **A line in capitals** is converted in lowercase and given back in capitals.
2. ***de que* + *gostar***: *De que gostas?* loses *de* (Gramática IV 1.2).
3. ***gostar***: the verb loses *de* and takes a dative pronoun (`GOSTAR_PHRASE`, `without_de`).
4. **The compound perfect**: in a clause with *hoje* or *este ano*, a singular preterite becomes *ter* + participle (`ongoing_perfect`, Gramática III 1.2.5.1).
5. ***faz* + time**: an impersonal *faz* before a span of time becomes *há* (Convenção 3.1).
6. **Periphrases**: *estar a* + infinitive takes the gerund, *ir* + infinitive takes *a*, and *ter de* becomes *ter que*. A pronoun on the infinitive moves before the auxiliary (Gramática IV 1.3, Convenção 3.1, Convenção 2.7).
7. ***vinte e N*** becomes one word (Gramática III 1.1.8).
8. ***ainda*** becomes *inda*, except at the end of a sentence (Convenção 1.6).

The [Constructions page](constructions.md) shows each one with examples.

## Stage 2: the word loop

The text is split into words and separators. For each word, the loop decides from the word and its neighbours:

- **Pass through**: template slots, numbers, Roman numerals, acronyms, initials, names and imported words stay as they are (see the [API page](api.md)).
- **Enclitic pronouns**: *casei-me* becomes *me casê*. A pronoun stays after an infinitive: *fazê-lo* becomes *fazê-lu* (Gramática IV 1.1).
- ***se***: the conjunction is *si*, the pronoun is *se* (Convenção 1.1). The loop decides from the word before and the word after.
- **Possessives**: before a noun *mê*, *tê*, *sê*; alone *meu*, *teu*, *seu* (Gramática III 1.1.3).
- **Plural determiners**: the plural *-h* goes on the determiner only: *todas as casas* > *toda ah casa* (Convenção 2.1).
- **Gender**: a noun whose gender follows Spanish changes the determiner before it: *as laranjeiras* > *uh laranjêru* (Gramática III 1.1.1).
- **Pseudo-reflexive verbs**: *casar*, *cair*, *morrer*, *sair*, *dormir* and *ir* take a pronoun of the same person: *já morreu* > *já se morreu* (Gramática IV 1.4).
- **2nd person singular**: after *tú* or *te*, a verb that lost its *-s* takes *-h*: *tu comes* > *tú comih* (Convenção 2.1).
- **Everything else** goes through `word`.

## Stage 3: elision

*me*, *te* and *se* lose their vowel before a vowel: *me apetece* > *m'apeteci* (Convenção 1.5).

## The spelling rules in `word`

`word` converts one word. It first finds the stressed syllable by the Portuguese accent rules (`stressed_nucleus`), because the books state their rules by stress. Then it applies these rules in order:

| Rule | Example | Source |
| --- | --- | --- |
| initial *h* is dropped | *homem* > *omen* | Convenção 2.1 |
| *v* becomes *b* | *viva* > *biba* | Convenção 2 |
| 1pl present *-amos* > *-emu*, preterite *-ámos* > *-amu* | *amamos* > *amemu*, *comprámos* > *compramu* | Gramática III 1.2.5.2, III 1.2.5.4 |
| nasal endings | *canção* > *cançãu*, *mãe* > *mãi*, *irmãos* > *irmõi*, *cantavam* > *cantabon* | Convenção 1.8.1, 1.8.2, 1.8.3 |
| [kw] and [gw] before *e*, *i* | *cinquenta* > *cincuenta* | Convenção 2.4, 2.5 |
| *s*, *z*, *x* before a consonant become *h* | *Lisboa* > *Lihboa*, *texto* > *tehtu* | Convenção 2.1 |
| *ou* and *ei* reduce | *primeira* > *primêra*, *beijo* > *bêju* | Convenção 1.4, 1.7 |
| a final *-l*, *-r*, *-z* after the stressed vowel is dropped, and the vowel takes an accent | *azul* > *azú*, *fazer* > *fazê*, *espanhol* > *ehpanhó* | Convenção 1.2, 2.6, 2.7 |
| an unstressed open vowel before a lost *-l* or *-r* takes the grave accent | *Vítor* > *Bitò* | Convenção 1.1 |
| a final *-s* is *-h* on monosyllables, dropped elsewhere | *três* > *trêh*, *os meninos* > *uh meninu* | Convenção 2.1 |
| unstressed final *-o*, *-e* become *-u*, *-i* | *tempo* > *tempu*, *sempre* > *sempri* | Convenção 1.1 |
| a stressed final *i* or *u* takes the acute | *aqui* > *aquí* | Convenção 1.2 |

A final stressed *e* or *o* before a lost *-r* keeps its Portuguese quality: closed *ê*, *ô* (*fazê*, *senhô*), and open *é*, *ó* in a short list of words that are open in pt-PT (*mulhé*, *melhó*). The spelling of Portuguese does not show the quality, so the list is lexical (Convenção 1.2).
