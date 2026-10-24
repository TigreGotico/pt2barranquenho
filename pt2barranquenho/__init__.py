"""Rule-based European Portuguese to Barranquenho.

The rules follow two books by Gonçalves, Navas and Correia (Universidade de Évora, 2025): the Convenção Ortográfica
do Barranquenho and the Gramática Básica de Barranquenho. A comment that names "Convenção 2.1" or "Gramática III
1.1.3" points to the section that gives the rule, and rules/citations.tsv quotes each section with its page. A
comment that names "Portuguese" marks a rule from pt-PT grammar, not from the books: these find the stress of a word
or tell a pronoun from a conjunction.

    echo "Os meus tios compraram pão." | pt2barranquenho
"""
import re
import sys
import unicodedata

VOWELS = "aeiouáéíóúâêôãõàèòü"
ACCENTED = "áéíóúâêôãõàèò"
ACUTE = {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú"}

# Closed classes. The plural keeps the aspirated -h on these words, and on the first word of a noun phrase.
CLOSED = {
    # Articles and their contractions, Gramática III 1.1.1.
    "o": "u", "os": "uh", "a": "a", "as": "ah", "um": "un", "uns": "unh", "uma": "uma", "umas": "umah",
    "ao": "ò", "aos": "auh", "à": "à", "às": "àh", "do": "du", "dos": "duh", "da": "da", "das": "dah",
    "no": "nu", "nos": "nuh", "na": "na", "nas": "nah", "pelo": "pelu", "pelos": "peluh", "pela": "pela",
    "pelas": "pelah", "num": "nun", "nuns": "nunh", "numa": "numa", "numas": "numah", "dum": "dun",
    "duns": "dunh", "duma": "duma", "dumas": "dumah",
    # Personal pronouns and their contractions, Gramática III 1.1.2.
    "eu": "eu", "tu": "tú", "ele": "eli", "ela": "ela", "nós": "nóh", "vós": "bóh", "eles": "elih",
    "elas": "elah", "vocês": "bocedi", "mim": "min", "comigo": "comigu", "contigo": "contigu",
    "connosco": "connóh", "lhe": "le", "lhes": "leh", "vos": "buh", "dele": "deli", "deles": "delih",
    "delas": "delah", "nele": "neli", "neles": "nelih", "nelas": "nelah", "me": "me", "te": "te", "se": "se",
    "si": "si", "lho": "su", "lha": "sa", "lhos": "suh", "lhas": "sah",
    # Possessives, Gramática III 1.1.3.
    "meu": "mê", "teu": "tê", "seu": "sê", "meus": "mêh", "teus": "têh", "seus": "sêh", "minhas": "minhah",
    "tuas": "tuah", "suas": "suah", "nossos": "nossuh", "nossas": "nossah", "vosso": "bossu", "vossa": "bossa",
    "vossas": "bossah",
    # Demonstratives, Gramática III 1.1.4.
    "estes": "ehtih", "estas": "ehtah", "esses": "essih", "essas": "essah", "aqueles": "aquelih",
    "aquelas": "aquelah", "isto": "ihtu",
    # Relatives, Gramática III 1.1.5; indefinites, Gramática III 1.1.6.
    "cujos": "cujuh", "cujas": "cujah", "alguns": "algunh", "algumas": "algumah", "nenhuns": "nenhunh",
    "nenhumas": "nenhumah", "outro": "otru", "outra": "otra", "outros": "otruh", "outras": "otrah",
    "todos": "toduh", "todas": "todah", "certos": "certuh", "certas": "certah", "muito": "muntu", "muita": "munta",
    "muitos": "muntuh", "muitas": "muntah", "pouco": "pocu", "pouca": "poca", "poucos": "pocuh", "poucas": "pocah",
    "qualquer": "qualqué", "quaisquer": "quaihqué", "alguém": "alguén", "ninguém": "ninguén", "tudo": "tudu",
    # Interrogatives, Gramática III 1.1.7.
    "quanto": "quantu", "quanta": "quanta", "quantos": "quantuh", "quantas": "quantah", "quais": "quaih",
    # qual keeps its -l and takes cu, Convenção 2.6 (mal, tal, cual); the Gramática tables print quà.
    "qual": "cual",
    # Numerals, Gramática III 1.1.8.
    # outrem is oxytone: otrén, Gramática III 1.1.6.
    "outrem": "otrén",
    # Nouns in -or with an open final vowel, which the Portuguese spelling does not show: caló, Gramática II 2;
    # capela-mó, Convenção Aplicação.
    "calor": "caló", "mor": "mó",
    "dois": "doih", "duas": "duah", "três": "trêh", "seis": "seih", "dez": "déh", "dezasseis": "dezassei",
    "dezassete": "dezasseti",
    # Prepositions and conjunctions, Gramática III 1.2.6; e > i, Convenção 1.3; ou > o, Convenção 1.7; por > pur,
    # Convenção 2.7; também > tamén, Convenção sound table.
    "em": "en", "por": "pur", "sob": "so", "e": "i", "ou": "o", "mas": "mah", "também": "tamén",
    # até > ahta, the one preposition that differs, Gramática III 1.2.6.
    "até": "ahta",
    # Monosyllables keep the aspirated -h, Convenção 2.1.
    "mais": "maih", "pois": "poih", "deus": "deuh", "depois": "dehpoi",
    # Irregular verb forms, Gramática III 1.2.5; quer > què, Gramática III 1.1.2; sou, estou, Convenção 1.7;
    # vir > bi, Convenção 2.7. Existential há is ai in the Convenção 3.1 examples, and the h rule of Convenção 2.1
    # rules out the Gramática's hai.
    "somos": "semu", "és": "eri", "sou": "sô", "estou": "tô", "estive": "ehtubi", "andei": "andubi", "há": "ai",
    "quer": "què", "vir": "bi",
    # 3pl presents that keep their nasal, Gramática III 1.2.5: tenhen, ponhen, benhen.
    "têm": "tenhen", "põem": "ponhen", "vêm": "benhen",
    # The tables of ser, estar, haver and ter, Gramática III 1.2.5.4: the 2sg keeps its -h (Convenção 2.1) in forms
    # no noun shares, and haver drops its h.
    "hei": "ê", "hás": "áh", "estás": "ehtáh", "tinhas": "tinhah", "havias": "abiah", "sejas": "sejah",
    "tenhas": "tenhah", "estejas": "ehtejah", "hajas": "ajah", "fosses": "fossih", "tivesses": "tibessih",
    "estivesses": "ehtibessih", "houvesses": "obessih", "tiveras": "tiberah", "estiveras": "ehtiberah",
    "houveras": "oberah", "fores": "forih", "tiveres": "tiberih", "estiveres": "ehtiberih", "houveres": "oberih",
    "serias": "seriah", "terias": "teriah", "estarias": "ehtariah", "haverias": "aberiah",
}
# Object pronouns before the verb, Gramática IV 1.1, in their Gramática III 1.1.2 forms.
CLITICS = {"me": "me", "te": "te", "se": "se", "lhe": "le", "lhes": "leh", "nos": "nuh", "vos": "buh", "o": "u",
           "a": "a", "os": "uh", "as": "ah", "no": "u", "na": "a", "nas": "ah", "lo": "lu", "la": "la",
           "los": "luh", "las": "lah", "lho": "su", "lha": "sa", "lhos": "suh", "lhas": "sah"}
CLITIC_OUTPUT = {"me", "te", "se", "nuh", "buh", "le", "leh", "m'", "t'", "s'"}
# Nouns whose gender follows Spanish, Gramática III 1.2.2.1: the form, and the gender its article takes.
GENDER = {"leite": ("lêti", "f"), "mel": ("mé", "f"), "sangue": ("sangui", "f"), "riso": ("risa", "f"),
          "laranjeira": ("laranjêru", "m"), "macieira": ("maçanêru", "m"), "amendoeira": ("amendoêru", "m"),
          "cerejeira": ("cerejêru", "m"), "tangerineira": ("tangerinêru", "m"), "romãzeira": ("romanêru", "m"),
          "ameixieira": ("amexêru", "m"), "pessegueiro": ("melacatonêru", "m")}  # Gramática V 1.2: melacatonêru
# Words the books print in place of the Portuguese word, each also an entry of the Dicionário de Barranquenho (2025).
LEXICON = {
    "azinheira": ("azenhêra", "f"), "seixo": ("china", "f"), "bebedeira": ("chihpa", "f"),   # Gramática III 1.1.1
    "amendoim": ("arbelhana", "f"),                                                            # and Gramática V 1.1
    "leque": ("abanicu", "m"),                                                                 # Gramática III 1.1.4
    "advogado": ("abogadu", "m"),                                                              # Gramática III 1.1.5
    "javali": ("jabardu", "m"),                                                                # Gramática III 1.1.8
    "cãozinho": ("canitu", "m"),                                                               # Gramática III 1.2.4
    "nádega": ("nalga", "f"),                                                                  # Gramática II 1.6
    "bisca": ("brihca", "f"),                                                                  # Gramática IV 1.2
    "cócega": ("cohquilha", "f"),                                                              # Gramática V 1.2
    "terçol": ("terzuelu", "m"), "terçolho": ("terzuelu", "m"),                                # Gramática V 1.3
}
NOUNS = GENDER | LEXICON
# Determiners, masculine and feminine, in the forms word() gives them (Gramática III 1.1.1, III 1.1.4). A noun whose
# gender differs from the Portuguese one takes the other form: nah china (pt. 'nos seixos').
ARTICLES = [("u", "a"), ("uh", "ah"), ("un", "uma"), ("unh", "umah"), ("ò", "à"), ("auh", "àh"), ("du", "da"),
            ("duh", "dah"), ("nu", "na"), ("nuh", "nah"), ("pelu", "pela"), ("peluh", "pelah"), ("dun", "duma"),
            ("dunh", "dumah"), ("nun", "numa"), ("nunh", "numah")]
DEMONSTRATIVES = [("ehti", "ehta"), ("ehtih", "ehtah"), ("essi", "essa"), ("essih", "essah"), ("aqueli", "aquela"),
                  ("aquelih", "aquelah")]
DETERMINERS = ARTICLES + [(prep + m, prep + f) for prep in ("", "d", "n") for m, f in DEMONSTRATIVES]
ARTICLE_FLIP = {"m": {f: m for m, f in DETERMINERS}, "f": dict(DETERMINERS)}
# After a plural determiner a possessive or outro loses its own -h, Convenção 3: ah minha prima, uh tê pai; the
# Convenção text: todu uh otru.
AFTER_PLURAL = {"meus": "mê", "teus": "tê", "seus": "sê", "minhas": "minha", "tuas": "tua", "suas": "sua",
                "nossos": "nossu", "nossas": "nossa", "outros": "otru", "outras": "otra"}
# After a determiner and with no noun after it, the possessive is tonic and keeps the diphthong, Convenção 1.1:
# uh meu tamén, u seu a sê donu.
TONIC_POSSESSIVE = {"meu": "meu", "teu": "teu", "seu": "seu", "meus": "meuh", "teus": "teuh", "seus": "seuh"}
# Stems where pt-PT says [kw] or [gw] before e or i. The Portuguese spelling does not show it, so the list is
# lexical. Barranquenho writes cu (cincuenta, Convenção 2.1; cuatru, Convenção 2.4) and gü (agüentá, Convenção 2.5).
LABIOVELAR = {"cinquent": "cincuent", "frequent": "frecuent", "frequênc": "frecuênc", "tranquil": "trancuil",
              "delinquent": "delincuent", "eloquent": "elocuent", "consequent": "consecuent",
              "consequênc": "consecuênc", "sequestr": "secuestr", "aguent": "agüent", "linguíst": "lingüíst",
              "ungu": "ungü", "pinguin": "pingüin", "ensanguent": "ensangüent", "arguir": "argüir",
              "sequênc": "secuênc", "subsequent": "subsecuent", "bilingue": "bilingüe", "ambiguidad": "ambigüidad",
              "equestr": "ecuestr"}
# Monosyllables that keep the final -l, Convenção 2.6.
KEEP_L = {"mal", "tal", "qual"}
VINTE = {"um": "un", "uma": "uma", "dois": "doi", "duas": "dua", "três": "tré", "quatro": "cuatru", "cinco": "cincu",
         "seis": "sei", "sete": "seti", "oito": "oitu", "nove": "nobi"}
CLOSED.update({f"vinte_e_{pt}": "binti" + barr for pt, barr in VINTE.items()})
# The present and imperfect of ir are always ir. The preterite fui, foi, foram is also the preterite of ser
# (foi criar emprego), so it counts as ir only at the start of a clause or after a subject pronoun or an adverb.
IR = r"(?:vou|vais|vai|vamos|vão|ia|ias|íamos|iam)"
IR_PAST = r"(?:fui|foste|foi|fomos|foram)"
IR_PAST_AFTER = {"eu", "tu", "ele", "ela", "nós", "eles", "elas", "você", "vocês", "e", "já", "logo", "depois",
                 "então", "ontem", "hoje", "também"}
ESTAR = (r"(?:estou|estás|está|estamos|estão|estava|estavas|estávamos|estavam|esteve|estive|estiveram|estar|estará|"
         r"estaria|esteja|estejam|estivesse|estivessem|estando)")
CLITIC_WORDS = "me|te|se|nos|vos|lhe|lhes|o|a|os|as"
# Verbs that take a pseudo-reflexive pronoun, Gramática IV 1.4: casar, cair, dormir, ir, morrer, sair. The pronoun
# agrees with the person: me casê (Convenção 1.7), já se morreu.
PSEUDO_REFLEXIVE = re.compile(r"^(?:cas(?:ou|aram|ei|aste)|ca(?:iu|íram|í|íste)|morr(?:eu|eram|i|este|ia|iam)|"
                              r"sa(?:iu|íram|í|íste)|dorm(?:iu|iram)|foram)$")
PLURAL_DETERMINERS = {"os", "as", "estes", "estas", "esses", "essas", "aqueles", "aquelas", "meus", "teus", "seus",
                      "minhas", "tuas", "suas", "nossos", "nossas"}
# Gramática II 2 keeps the spelling of imported names (Valverde). The Portuguese input does not mark them, so the code
# finds only the words with letters and sequences Portuguese spelling does not use.
FOREIGN = re.compile(r"[kwyäëïöüåøñłčšžăőűæœß]|([bdfgpt])\1|l{2}|[^\Wcln]h|tz|^s[^aeiouáéíóúâêôãõ]|[^aeiouáéíóúâêôãõblrsmnxz]$")
MOTION = {"a", "à", "ao", "aos", "às", "para", "pra", "embora"}
# Portuguese: the pronoun se and the conjunction se are spelt alike, and the Convenção writes them se and si
# (Convenção 1.1). pt-PT never opens a clause with an atonic pronoun, so se at the start of a clause is the
# conjunction. After a subject pronoun or a word that draws the pronoun before the verb, se is the pronoun, unless the
# next word is one the pronoun cannot precede.
SUBJECTS = {"eu", "tu", "ele", "ela", "nós", "vós", "eles", "elas", "você", "vocês"}
PROCLISIS = SUBJECTS | {"não", "nunca", "jamais", "já", "também", "só", "ainda", "sempre", "bem", "mal", "talvez",
                        "que", "quem", "onde", "quando", "porque", "qual", "quanto", "tudo", "nada", "alguém",
                        "ninguém", "todos", "para", "de", "sem", "por", "logo", "assim", "aqui", "lá", "cá", "ali",
                        "aí", "hoje", "ontem", "amanhã"}
CONJUNCTION_NEXT = SUBJECTS | {"o", "a", "os", "as", "um", "uma", "uns", "umas", "isto", "isso", "aquilo", "este",
                               "esta", "esse", "essa", "aquele", "aquela", "por", "calhar", "não", "nunca", "alguém",
                               "ninguém", "tudo", "nada", "me", "te", "lhe", "lhes", "nos", "vos", "é",
                               "for", "fosse", "tiver", "tivesse", "houver", "estiver"}
# Verbs after which se opens an indirect question: não sei se vem.
QUESTION_VERBS = re.compile(r"^(?:sei|sabe|sabes|sabemos|sabem|saber|sabia|pergunt\w*|ver|vê|veja|vejo|depende|duvido)$")
# Portuguese: present subjunctive stems of -er and -ir verbs, whose 1pl in -amos is not the -emu present of -ar verbs
# (Gramática III 1.2.5.4: comamu, partamu, sejamu, ajamu).
SUBJUNCTIVE_STEM = re.compile(r"^(?:sej|haj|faç|dig|vej|poss|queir|saib|trag|ouç|peç|sig|consig|sint|durm|sirv|"
                              r"prefir|ponh|venh|caib|valh|perc|fuj|cubr|com|beb|escrev|viv|aprend|vend|corr|receb|"
                              r"respond|part|abr|decid|exist|permit|discut|insist|assist|sub|cumpr|resolv|conheç)amos$")
# Portuguese: the future subjunctive of a strong preterite stem, whose -er is not an infinitive (Gramática III
# 1.2.5.4: tibé, ehtibé, obé).
STRONG_FUTURE = re.compile(r"^(?:(?:es)?tiv|houv|fiz|pud|quis|diss|soub|troux|pus|coub)er$")
SUBJUNCTIVE = re.compile(r"(?:ss(?:e|es|em|emos)|[aeiô]r|[aeiô]res|[aeiô]rem|[aeiô]rmos)$")


def strip_accents(s: str) -> str:
    """Remove the acute and circumflex accents."""
    return unicodedata.normalize("NFC", "".join(c for c in unicodedata.normalize("NFD", s) if c not in "́̂"))


def singular(w: str) -> str:
    """Portuguese: the singular of a regular plural noun (seixos, amendoins, javalis), or the word itself."""
    if w.endswith("ns"):
        return w[:-2] + "m"
    return w[:-1] if w.endswith("s") and w[:-1] in NOUNS else w


def second_singular(pt: str, barr: str) -> bool:
    """Portuguese: whether a verb after tu or te is a 2sg form that lost its -s. A final nasal takes no -h: tú ten,
    Gramática III 1.2.5.4."""
    return pt.endswith("s") and not pt.endswith("mos") and pt not in CLOSED and not barr.endswith(("h", "n"))


def nuclei(w: str) -> list[re.Match]:
    """Portuguese: syllable nuclei. A vowel takes an optional falling glide (pai, céu, mãe); a hiatus counts twice
    (frio, tios); the u of que, gui is not a vowel."""
    w = re.sub(r"(?<=[qg])u(?=[eiéíê])", "_", w)
    return list(re.finditer(f"ão|ãe|õe|ãi|õi|[aeoáéóâêôàèãõ][iu](?![{VOWELS}])|[{VOWELS}]", w))


def stressed_nucleus(w: str) -> tuple[int, list[re.Match]]:
    """Portuguese: the index of the stressed nucleus by the accent rules, and the nuclei."""
    ns = nuclei(w)
    for i, n in enumerate(ns):
        if any(c in ACCENTED for c in n.group()) and n.group()[0] not in "ãõ":
            return i, ns
    for i, n in enumerate(ns):
        if n.group()[0] in "ãõ":
            return i, ns
    if len(ns) < 2:
        return 0, ns
    if re.search(r"([aeo]s?|[ae]m|ens)$", w):
        return len(ns) - 2, ns
    return len(ns) - 1, ns


def word(w: str) -> str:
    """Convert one lowercase Portuguese word, without context."""
    if w in CLOSED:
        return CLOSED[w]
    if not re.search(f"[{VOWELS}]", w):
        return w
    orig = w
    stress, groups = stressed_nucleus(w)
    final_stress = stress == len(groups) - 1
    mono = len(groups) == 1
    w = w.removeprefix("h")                                          # Convenção 2.1: omen
    w = w.replace("v", "b")                                          # Convenção 2: bibu, trabalhaba
    # 1pl: the preterite -ámos becomes -amu (Gramática III 1.2.5.4, the amá table), the present -amos becomes
    # -emu (Gramática III 1.2.5.2). The final -s goes below (Convenção 2.1).
    if w.endswith("ámos") and len(groups) > 2 and not re.search(r"[áí]", w[:-4]):
        return w[:-4] + "amu"
    if len(groups) > 2 and not any(c in ACCENTED for c in w) and not SUBJUNCTIVE_STEM.match(orig):
        w = re.sub(r"amos$", "emos", w)
    # The 1pl of the past subjunctive and the pluperfect is written with an acute: fóssemu, coméramu (Gramática III
    # 1.2.5.4).
    w = re.sub(r"[êô](?=(?:ssemos|ramos)$)", lambda m: {"ê": "é", "ô": "ó"}[m[0]], w)
    w = re.sub(r"ãos$", "õi", w)                                     # Gramática III 1.2.3: plural in -õi
    w = w.replace("ão", "ãu")                                        # Convenção 1.8.3: fejãu, leãu
    w = re.sub(r"ãe$|ães$", "ãi", w)                                 # Convenção 1.8.3: mãi, pãi
    w = re.sub(r"ões$", "õi", w)                                     # Convenção 1.8.3: patrõi
    if not final_stress:
        w = re.sub(r"am$", "on", w)                                  # Convenção 1.8.2: canton, ehtabon
    w = re.sub(f"(?<=[{VOWELS}])m$", "n", w)                         # Convenção 1.8.1: quen, bon
    w = re.sub(r"ã$", "án", w)                                       # Convenção 1.8.1: manhán
    for pt, barr in LABIOVELAR.items():                              # Convenção 2.4 and 2.5
        if w.startswith(pt):
            w = barr + w[len(pt):]
            break
    w = re.sub(r"qu(?=[aoáóâô])", "cu", w)                           # Convenção 2.4: cuatru
    w = re.sub(f"x(?=[^{VOWELS}])", "h", w)                          # Convenção 2.1: tehtu
    w = re.sub(r"ai(?=x)", "a", w)                                   # Convenção 1.7: abaxu
    # Convenção 1.7: a final stressed ou is ô in verbs (se labô); Convenção 1.4: elsewhere it is o (choriçu).
    w = re.sub(r"ou", "ô" if final_stress and w.endswith("ou") else "o", w)
    w = re.sub(r"ei(?=[aou]s?$)", "ê", w)                            # Convenção 1.7: idêa, rechêu
    now = nuclei(w)
    if len(now) == len(groups) and now[stress].group().startswith("ei"):
        w = w[:now[stress].start()] + "ê" + w[now[stress].start() + 2:]   # Convenção 1.7: primêra
    w = w.replace("ei", "e")                                         # Convenção 1.8.3: fejãu
    # A final -l, -r or -z after the stressed vowel is silent and the vowel takes an accent: Convenção 2.6 (ehpanhó),
    # Convenção 2.7 (cantá, senhô), Convenção 1.2 (colhê, azú). Monosyllables keep -l (mal, tal) and -z.
    m = re.search(r"([aeiouáéíóúêô])([lrz])$", w)
    if m and final_stress and not (mono and (m.group(2) == "z" or orig in KEEP_L)):
        v, c = m.groups()
        closed = {"e": "ê", "o": "ô"} if c == "r" and not STRONG_FUTURE.match(orig) else {"ê": "ê"}
        w = w[:m.start()] + closed.get(v, ACUTE.get(v, v))
    elif m and not final_stress and (m.group(1) in "ae" and m.group(2) in "lr" or m.groups() == ("o", "r")):
        # Convenção 1.1 and Convenção 4: an unstressed open final vowel before a lost -l or -r takes the grave
        # accent, and it carries no other accent (açucà, amabè, Bitò).
        w = strip_accents(w[:m.start()]) + {"a": "à", "e": "è", "o": "ò"}[m.group(1)]
    elif not final_stress and w.endswith("il"):
        w = strip_accents(w[:-1])                                    # Gramática III 1.2.3: difici
    w = re.sub(f"n?[sz](?=[^{VOWELS}s])", "h", w)                    # Convenção 2.1: Lihboa, ihtrumentu
    if w.endswith(("s", "z")):
        if mono and (w.endswith("z") or any(c in ACCENTED for c in w)) or orig.endswith("rás") and not orig.endswith("trás"):
            w = w[:-1] + "h"                       # Convenção 2.1: trêh, Deuh; the 2sg future, Gramática amaráh
        else:
            w = w[:-1]                                               # Convenção 2.1: Barrancu, ehpanhói
            if orig.endswith("ês"):
                w = re.sub(r"ê$", "é", w)                            # Gramática III 1.2.1: camponé
    if not final_stress:
        w = re.sub(r"o$", "u", w)                                    # Convenção 1.1: altu
        w = re.sub(r"e$", "i", w)                                    # Convenção 1.1: sempri
    elif not mono and re.search(f"(?:[^{VOWELS}]|[qg]u)[iu]$", w) and not any(c in ACCENTED for c in w):
        w = w[:-1] + ACUTE[w[-1]]                                    # Convenção 1.2: aquí
    return w


# gostar takes no preposition, and the person who likes takes a dative pronoun before a 3sg verb, Gramática IV 1.2
# (que tantu le gohtaba) and Convenção 3.1 (A min me gohta comunicá). Each finite form gives its pronoun and the 3sg
# form of its tense; None is a form whose person only a subject tells apart. Without a subject, gosta, gostou and
# gostará are 3sg, and gostava and gostaria are the polite 1sg of pt-PT (gostava de saber).
GOSTAR = {"gosto": ("me", "gosta"), "gostas": ("te", "gosta"), "gosta": (None, "gosta"), "gostamos": ("nos", "gosta"),
          "gostam": ("lhes", "gosta"), "gostava": (None, "gostava"), "gostavas": ("te", "gostava"),
          "gostávamos": ("nos", "gostava"), "gostavam": ("lhes", "gostava"), "gostei": ("me", "gostou"),
          "gostaste": ("te", "gostou"), "gostou": (None, "gostou"), "gostámos": ("nos", "gostou"),
          "gostaram": ("lhes", "gostou"), "gostaria": (None, "gostaria"), "gostarias": ("te", "gostaria"),
          "gostaríamos": ("nos", "gostaria"), "gostariam": ("lhes", "gostaria"), "gostarei": ("me", "gostará"),
          "gostarás": ("te", "gostará"), "gostará": (None, "gostará"), "gostaremos": ("nos", "gostará"),
          "gostarão": ("lhes", "gostará")}
# A subject pronoun becomes a + the tonic pronoun: A min me gohta.
LIKER = {"eu": ("a mim", "me"), "tu": ("a ti", "te"), "ele": ("a ele", "lhe"), "ela": ("a ela", "lhe"),
         "você": ("a você", "lhe"), "nós": ("a nós", "nos"), "eles": ("a eles", "lhes"), "elas": ("a elas", "lhes"),
         "vocês": ("a vocês", "lhes")}
# The thing liked loses de (gostamos dela > nuh guhtô). The books print no form for a 1st or 2nd person liked, so
# gostas de mim keeps de.
LIKED = "e|o|a|os|as|um|uma|uns|umas|est[eao]s?|ess[eao]s?|aquel[ea]s?|aquilo|isto|isso|el[ea]s?"
DEGREE = "muito|mais|tanto|bastante|imenso|pouco|menos"
GOSTAR_PHRASE = re.compile(rf"\b(?:({'|'.join(LIKER)})\s+)?(?:(não|nunca|já|também)\s+)?({'|'.join(GOSTAR)})\b(?!-)"
                           rf"(?!(?:\s+(?:{DEGREE}))?\s+de\s+(?:mim|ti|si|nós|você|vocês)\b)"
                           rf"(\s+(?:{DEGREE}))?(?:\s+d({LIKED})\b)?", re.IGNORECASE)


PREPOSITIONS = {"a", "à", "para", "de", "com", "por", "sem", "contra", "entre", "sobre", "até", "perante"}
CLAUSE_OPENERS = {"que", "e", "mas", "porque", "se", "também", "já", "ainda", "não", "pois", "quando", "eu"}


def without_de(m: re.Match) -> str:
    """Portuguese: a finite form of gostar rewritten as the dative construction (gosto de > me gosta)."""
    subject, negation, verb, adverb, liked = m.groups()
    before = (re.search(r"(\w*)\W*$", m.string[:m.start()])[1]).lower()
    if subject and before in PREPOSITIONS or verb.lower() == "gosto" and not subject and not negation and before \
            and before not in CLAUSE_OPENERS:
        return m[0]                             # a eli gosta: not a subject; o gosto, tem gosto: the noun
    pronoun, form = GOSTAR[verb.lower()]
    default = "me" if form in ("gostava", "gostaria") else "lhe"
    tonic, subject_pronoun = LIKER.get((subject or "").lower(), ("", default))
    if before in ("me", "te", "lhe", "nos", "lhes"):
        pronoun = subject_pronoun = ""                               # que tanto lhe gostava
    liked = "" if (liked or "e").lower() == "e" else liked
    words = [tonic, negation, pronoun or subject_pronoun, form, (adverb or "").strip(), liked]
    out = " ".join(w for w in words if w)
    return out[0].upper() + out[1:] if m[0][0].isupper() else out


# A preterite in a span of time that still goes on takes ter + participle, Gramática III 1.2.5.1: oji me tenhu atadu
# u lençu. Only the 1st and 3rd person singular are rewritten: their endings tell the person, while a 3rd person
# plural in -aram, -eram or -iram can be a present (preparam, esperam, retiram).
ONGOING = re.compile(r"\b(?:hoje|est[ea] (?:ano|semana|mês|manhã|tarde|noite))\b", re.IGNORECASE)
FINISHED = re.compile(r"\b(?:ontem|anteontem|antigamente|outrora|passad[ao])\b", re.IGNORECASE)
IRREGULAR_PRETERITE = {"fiz": ("tenho", "feito"), "fez": ("tem", "feito"), "vi": ("tenho", "visto"),
                       "viu": ("tem", "visto"), "dei": ("tenho", "dado"), "deu": ("tem", "dado"),
                       "pus": ("tenho", "posto"), "pôs": ("tem", "posto"), "vim": ("tenho", "vindo"),
                       "veio": ("tem", "vindo"), "tive": ("tenho", "tido"), "teve": ("tem", "tido"),
                       "estive": ("tenho", "estado"), "esteve": ("tem", "estado"), "escrevi": ("tenho", "escrito"),
                       "escreveu": ("tem", "escrito"), "abri": ("tenho", "aberto"), "abriu": ("tem", "aberto"),
                       "li": ("tenho", "lido"), "leu": ("tem", "lido")}
IRREGULAR_PRETERITE.update({"descobri": ("tenho", "descoberto"), "descobriu": ("tem", "descoberto"),
                            "cobri": ("tenho", "coberto"), "cobriu": ("tem", "coberto")})
# -arei, -erei and -irei are left out: they are also the 1sg future (farei, comprarei), so a preterite such as parei
# stays as it is.
REGULAR_PRETERITE = re.compile(r"^(\w*[aeiou]\w*?)((?<![aei]r)ei|ou|(?<=[cdtnsrlmvgbp])i|eu|iu)$")
NOT_PRETERITE = {"aqui", "ali", "daqui", "dali", "sei", "hei", "lei", "rei", "sou", "vou", "estou", "dou", "museu",
                 "europeu", "liceu", "judeu", "ateu", "coliseu", "apogeu", "teu", "seu", "meu"}


def perfect(m: re.Match) -> str:
    """Portuguese: a 1st or 3rd person singular preterite rewritten as ter + participle (comprei > tenho comprado)."""
    verb, clitic = m[1], m[2] or ""
    low = verb.lower()
    if verb != low:
        return m[0]                                                  # a name: Henri, Saudi
    if low in IRREGULAR_PRETERITE:
        aux, participle = IRREGULAR_PRETERITE[low]
    elif low not in NOT_PRETERITE | NOUNS.keys() and not any(c in ACCENTED for c in low) and \
            (form := REGULAR_PRETERITE.match(low)):
        stem, ending = form.groups()
        if ending in ("ei", "ou"):
            stem = re.sub(r"c$", "ç", re.sub(r"gu$", "g", stem)) if ending == "ei" else stem
            participle = re.sub(r"qu$", "c", stem) + "ado"
        else:
            participle = stem + ("ído" if stem[-1] in "aeiou" else "ido")                        # saído, construído
        aux = "tenho" if ending in ("ei", "i") else "tem"
    else:
        return m[0]
    return f"{aux}{clitic} {participle}"


def ongoing_perfect(clause: str) -> str:
    """Portuguese: the preterites next to hoje or este ano (the word before, the words after up to a subordinate
    clause) as ter + participle."""
    m = ONGOING.search(clause)
    if not m or FINISHED.search(clause):
        return clause
    start = re.search(r"(?:[\w-]+\s+)?$", clause[:m.start()]).start()
    stop = re.search(r"\b(?:que|porque|quando|se|mas|embora|como)\b", clause[m.end():])
    end = m.end() + stop.start() if stop else len(clause)
    span = clause[start:end]
    first = not clause[:start].strip() and span[:1].isupper() and not span[:2].isupper()
    if first:
        span = span[0].lower() + span[1:]                            # Acordei hoje: a verb, not a name
    span = re.sub(r"\b(\w+)(-(?:me|te|se|nos|vos|lhe|lhes|o|a|os|as))?\b(?!-)", perfect, span)
    return clause[:start] + (span[0].upper() + span[1:] if first else span) + clause[end:]


def translate(text: str) -> str:
    """Translate pt-PT text to Barranquenho, one sentence or line at a time. Spacing and punctuation are kept."""
    if text.isupper():
        return translate(text.lower()).upper()
    # de que ... gostava: the relative clause speaks of someone else, so the ambiguous form takes lhe.
    text = re.sub(r"\b([Dd])e (que|quem) ((?:\w+ ){0,2})(?=(gost\w*))",
                  lambda m: (m[2][0].upper() + m[2][1:] if m[1] == "D" else m[2]) + " " + m[3] +
                  ("lhe " if m[4].lower() in ("gostava", "gostaria") and not LIKER.keys() & set(m[3].lower().split())
                   else ""), text)
    text = GOSTAR_PHRASE.sub(without_de, text)
    text = "".join(ongoing_perfect(clause) for clause in re.split(r"([.;:!?]+)", text))
    # Impersonal faz + an amount of time takes haver, Convenção 3.1: poih, que ai binti anu. After a subject, faz is
    # fazer (u Joãu fah trinta anu), and without an amount it is the weather or a birthday (faz bom tempo, faz anos).
    text = re.sub(r"(^|[^\w\s]\s*|\b(?:que|pois|já|e|mas|porque|quase|agora|hoje|ainda)\s+)([Ff])az "
                  r"(?=(?:\d+|um|uma|dois|duas|três|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|quinze|vinte|"
                  r"trinta|quarenta|cinquenta|cem|muit[oa]s?|pouc[oa]s?|algu(?:m|ns)|algumas|uns|umas|vári[oa]s|"
                  r"bastantes?|tant[oa]s?|mais|menos) (?:\w+ )?(?:anos?|mês|meses|semanas?|dias?|horas?|minutos?|"
                  r"tempo)\b)",
                  lambda m: m[1] + ("H" if m[2] == "F" else "h") + "á ", text, flags=re.IGNORECASE)
    # Periphrases, Gramática IV 1.3 and Convenção 3.1. A pronoun on the infinitive climbs before the auxiliary
    # (me bô a labá, nuh ehtá bendu); estar a + infinitive takes the gerund; ir + infinitive takes a (bô a fazê).
    def climb(aux: str, verb: str, pronoun: str) -> str:
        if aux[0].isupper():
            aux, pronoun = aux[0].lower() + aux[1:], pronoun.capitalize()
        return f"{pronoun} {aux} {verb}"

    text = re.sub(rf"\b({ESTAR} a) (\w+[aei]r)-({CLITIC_WORDS})\b", lambda m: climb(m[1], m[2], m[3]), text,
                  flags=re.IGNORECASE)
    text = re.sub(rf"\b({ESTAR}(?:-\w+)?) a (\w+?)([aei])r\b", r"\1 \2\3ndo", text, flags=re.IGNORECASE)
    text = re.sub(rf"\b({IR}) (\w+[aeiô]r)-({CLITIC_WORDS})\b", lambda m: climb(m[1], "a " + m[2], m[3]), text,
                  flags=re.IGNORECASE)
    text = re.sub(rf"\b({IR}) (\w+[aeiô]r)\b", r"\1 a \2", text, flags=re.IGNORECASE)
    text = re.sub(rf"(\w*)(\W*)\b({IR_PAST}) (\w+[aeiô]r)\b",
                  lambda m: f"{m[1]}{m[2]}{m[3]} a {m[4]}" if not m[1] or m[1].lower() in IR_PAST_AFTER
                  or m[2].strip() else m[0], text, flags=re.IGNORECASE)
    # Convenção 2.7 prints ter que before an infinitive: a genti ten que tê fé.
    text = re.sub(r"\b(tenho|tens|tem|temos|têm|tinha|tinham|ter|terá|terão) de (?=\w+[aeiô]r\b)", r"\1 que ",
                  text, flags=re.IGNORECASE)
    # Gramática III 1.1.8 writes vinte e um as one word, and the unit loses its final -h: bintiun, bintidoi, bintitré.
    text = re.sub(r"\b([Vv])inte e (um|uma|dois|duas|três|quatro|cinco|seis|sete|oito|nove)\b",
                  lambda m: m[1] + "inte_e_" + m[2], text)
    # Convenção 1.6: ainda loses its first vowel, except at the end of a sentence.
    text = re.sub(r"\b([Aa])inda\b(?!\s*(?:[.!?…]|$))", lambda m: ("I" if m.group(1) == "A" else "i") + "nda", text)
    parts = re.split(r"(\w+(?:-\w+)*)", text)                      # separators at even indices, words at odd
    prev = None                          # index in parts of the previous word, when only spaces separate them
    prev_src = ""                        # that word in Portuguese, lowercased
    for i in range(1, len(parts), 2):
        tok, low = parts[i], parts[i].lower()
        if parts[i - 1].strip():
            prev, prev_src = None, ""
        before = parts[prev].lower() if prev is not None else ""
        next_src = parts[i + 2].lower() if i + 2 < len(parts) and parts[i + 1].strip() in ("", "{") else ""
        if parts[i - 1].endswith("{") and parts[i + 1].startswith("}"):
            continue                                                     # a template slot: {location}
        name_part = tok.isupper() and parts[i + 1].startswith(".") or tok[0].isupper() and "'" in (parts[i - 1][-1:], parts[i + 1][:1]) \
            or not tok.isupper() and any(c.isupper() for t in tok.split("-") for c in t[1:])
        if any(c.isdigit() for c in tok) or re.fullmatch(r"[IVXLCDM]+", tok) or (len(tok) > 1 and tok.isupper()) \
                or "-" not in low and FOREIGN.search(low) or name_part:
            prev, prev_src = i, low      # numbers, Roman numerals, acronyms, imported words, initials, O'Neill, McMaster
            continue
        verb, *clitics = low.split("-")
        if clitics and all(c in CLITICS for c in clitics):
            if clitics[-1] in ("lo", "la", "los", "las"):
                # Portuguese: entendêmo-lo, fazê-lo. The accent before -mo marks the stress for the clitic only.
                verb = re.sub(r"[êô](?=mo$)", lambda m: strip_accents(m[0]), verb) + "s" if verb.endswith("mo") else verb + "r"
            clitics.sort(key=lambda c: c not in ("me", "te"))
            pronouns = " ".join(CLITICS[c] for c in clitics)
            if verb.endswith("r"):
                res = word(verb) + "-" + pronouns.replace(" ", "-")    # Gramática IV 1.1: not before an infinitive
            else:
                res = pronouns + " " + word(verb)                       # Gramática IV 1.1: elih u torrabon lá
                if "te" in clitics and second_singular(verb, res):
                    res += "h"                                          # Convenção 2.1: te lembrah
        elif low == "se":
            res = "se" if prev_src in PROCLISIS and next_src not in CONJUNCTION_NEXT else "si"
            if prev is not None and prev_src not in PROCLISIS and not QUESTION_VERBS.match(prev_src) and \
                    next_src not in CONJUNCTION_NEXT and not SUBJUNCTIVE.search(next_src):
                res = "se"                                              # Convenção 1.1: i se paraba
        elif low in TONIC_POSSESSIVE and before and (not next_src or next_src in CLOSED):
            res = TONIC_POSSESSIVE[low][:-1] if before.endswith("h") and low.endswith("s") else TONIC_POSSESSIVE[low]
        elif low == "quem" and prev is None and "?" in "".join(parts[i:]).split(".")[0]:
            res = "quén"                                                # Gramática III 1.1.7: quén se casô?
        elif low in ("todos", "todas") and next_src in PLURAL_DETERMINERS:
            res = low[:-2] + "u" if low == "todos" else low[:-1]       # Convenção 2.1: todu uh otru
        elif low in AFTER_PLURAL and before.endswith("h"):
            res = AFTER_PLURAL[low]
        elif (noun := singular(low)) in NOUNS:
            res, gender = NOUNS[noun]                       # Convenção 2.1: the plural -h only on the determiner
            if before in ARTICLE_FLIP[gender]:
                flipped = ARTICLE_FLIP[gender][before]
                parts[prev] = flipped[0].upper() + flipped[1:] if parts[prev][0].isupper() else flipped
        else:
            res = "-".join(t if FOREIGN.search(t.lower()) else word(t.lower()) for t in tok.split("-"))
            if before in ("tú", "te") and second_singular(low, res):
                res += "h"                                                # Convenção 2.1: tú labah, ela laba
            if PSEUDO_REFLEXIVE.match(low) and before not in CLITIC_OUTPUT and (low != "foram" or next_src in MOTION):
                pronoun = "me" if re.search(r"(?:ei|í|i)$", low) else "te" if low.endswith("ste") else "se"
                res = f"{pronoun} {res}"                                 # Gramática IV 1.4: já se morreu
        if tok[0].isupper():
            res = "-".join(r[:1].upper() + r[1:] if t[:1].isupper() else r
                           for t, r in zip(tok.split("-"), res.split("-"))) if tok.count("-") == res.count("-") \
                else res[0].upper() + res[1:]
        parts[i] = res
        prev, prev_src = i, low
    # Convenção 1.5: me, te, se lose their vowel before a vowel (m'apeteci, s'usabon).
    return re.sub(r"(?<![\w-])([MmTtSs])e ([aeiouáéíóúâêôãõAEIOUÁÉÍÓÚÂÊÔ])", r"\1'\2", "".join(parts))


def main() -> None:
    for line in sys.stdin:
        print(translate(line.strip()))


if __name__ == "__main__":
    main()
