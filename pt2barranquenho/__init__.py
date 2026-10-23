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

VOWELS = "aeiouáéíóúâêôãõàèü"
ACCENTED = "áéíóúâêôãõàè"
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
    "elas": "elah", "você": "bocê", "vocês": "bocedi", "mim": "min", "comigo": "comigu", "contigo": "contigu",
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
    "quanto": "quantu", "quanta": "quanta", "quantos": "quantuh", "quantas": "quantah", "qual": "quà",
    "quais": "quaih",
    # Numerals, Gramática III 1.1.8.
    "dois": "doih", "duas": "duah", "três": "trêh", "seis": "seih", "dez": "déh", "dezasseis": "dezassei",
    "dezassete": "dezasseti",
    # Prepositions and conjunctions, Gramática III 1.2.6; e > i, Convenção 1.3; ou > o, Convenção 1.7; por > pur,
    # Convenção 2.7; também > tamén, Convenção sound table.
    "em": "en", "por": "pur", "sob": "so", "e": "i", "ou": "o", "mas": "mah", "também": "tamén",
    # Monosyllables keep the aspirated -h, Convenção 2.1.
    "mais": "maih", "pois": "poih", "deus": "deuh", "depois": "dehpoi",
    # Irregular verb forms, Gramática III 1.2.5; quer > què, Gramática III 1.1.2; sou, estou, Convenção 1.7;
    # vir > bi, Convenção 2.7. Existential há is ai in the Convenção 3.1 examples, and the h rule of Convenção 2.1
    # rules out the Gramática's hai.
    "somos": "semu", "és": "eri", "sou": "sô", "estou": "tô", "estive": "ehtubi", "andei": "andubi", "há": "ai",
    "quer": "què", "vir": "bi",
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
          "ameixieira": ("amexêru", "m")}
ARTICLE_FLIP = {"m": {"a": "u", "uma": "un", "da": "du", "na": "nu", "à": "ò", "pela": "pelu"},
                "f": {"u": "a", "un": "uma", "du": "da", "nu": "na", "ò": "à", "pelu": "pela"}}
# After a plural determiner the possessive loses its own -h, Convenção 3: ah minha prima, uh tê pai.
POSSESSIVE_PLURAL = {"meus": "mê", "teus": "tê", "seus": "sê", "minhas": "minha", "tuas": "tua", "suas": "sua",
                     "nossos": "nossu", "nossas": "nossa"}
# After a determiner and with no noun after it, the possessive is tonic and keeps the diphthong, Convenção 1.1:
# uh meu tamén, u seu a sê donu.
TONIC_POSSESSIVE = {"meu": "meu", "teu": "teu", "seu": "seu", "meus": "meuh", "teus": "teuh", "seus": "seuh"}
# Stems where pt-PT says [kw] or [gw] before e or i. The Portuguese spelling does not show it, so the list is
# lexical. Barranquenho writes cu (cincuenta, Convenção 2.1; cuatru, Convenção 2.4) and gü (agüentá, Convenção 2.5).
LABIOVELAR = {"cinquent": "cincuent", "frequent": "frecuent", "frequênc": "frecuênc", "tranquil": "trancuil",
              "delinquent": "delincuent", "eloquent": "elocuent", "consequent": "consecuent",
              "consequênc": "consecuênc", "sequestr": "secuestr", "aguent": "agüent", "linguíst": "lingüíst",
              "ungu": "ungü", "pinguim": "pingüim", "ensanguent": "ensangüent", "arguir": "argüir"}
IR = r"(?:vou|vais|vai|vamos|vão|ia|ias|íamos|iam|fui|foste|foi|fomos|foram)"
CLITIC_WORDS = "me|te|se|nos|vos|lhe|lhes"
# Verbs that take a pseudo-reflexive se, Gramática IV 1.4: casar, cair, dormir, ir, morrer, sair.
PSEUDO_REFLEXIVE = re.compile(r"^(?:cas(?:ou|aram|ei|aste)|ca(?:iu|íram|í|íste)|morr(?:eu|eram|i|este|ia|iam)|"
                              r"sa(?:iu|íram|í|íste)|dorm(?:iu|iram)|foram)$")
# Portuguese: words after which pt-PT puts an object pronoun before the verb. After them a free-standing se is the
# pronoun.
PROCLISIS = {"não", "nunca", "jamais", "já", "também", "só", "ainda", "sempre", "bem", "mal", "talvez", "que",
             "quem", "onde", "quando", "porque", "qual", "quanto", "tudo", "nada", "alguém", "ninguém", "todos",
             "para", "de", "sem", "por", "se", "logo", "assim", "aqui", "lá", "cá", "ali", "aí", "hoje", "ontem",
             "amanhã"}
# Portuguese: elsewhere se is the conjunction when the next word cannot follow the pronoun: a determiner, a subject
# pronoun, a preposition, a negation, or a subjunctive or infinitive (se fosse, se chover).
CONJUNCTION_NEXT = {"o", "a", "os", "as", "um", "uma", "uns", "umas", "eu", "tu", "ele", "ela", "nós", "vós", "eles",
                    "elas", "você", "vocês", "isto", "isso", "aquilo", "este", "esta", "esse", "essa", "aquele",
                    "aquela", "por", "calhar", "não", "nunca", "alguém", "ninguém", "tudo", "nada"}
SUBJUNCTIVE = re.compile(r"(?:ss(?:e|es|em|emos)|[aeiô]r|[aeiô]res|[aeiô]rem|[aeiô]rmos)$")


def strip_accents(s: str) -> str:
    """Remove the acute and circumflex accents."""
    return unicodedata.normalize("NFC", "".join(c for c in unicodedata.normalize("NFD", s) if c not in "́̂"))


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
    if len(groups) > 2 and not any(c in ACCENTED for c in w):
        w = re.sub(r"amos$", "emos", w)
    w = re.sub(r"ãos$", "õi", w)                                     # Gramática III 1.2.3: plural in -õi
    w = w.replace("ão", "ãu")                                        # Convenção 1.8.3: fejãu, leãu
    w = re.sub(r"ãe$|ães$", "ãi", w)                                 # Convenção 1.8.3: mãi, pãi
    w = re.sub(r"ões$", "õi", w)                                     # Convenção 1.8.3: patrõi
    if not final_stress:
        w = re.sub(r"am$", "on", w)                                  # Convenção 1.8.2: canton, ehtabon
    w = re.sub(f"(?<=[{VOWELS}])m$", "n", w)                         # Convenção 1.8.1: quen, bon
    w = re.sub(r"ui(?=t)", "un", w)                                  # Convenção 1.8.3: muntu
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
    m = re.search(r"([aeiouêô])([lrz])$", w)
    if m and final_stress and not (mono and m.group(2) in "lz"):
        v, c = m.groups()
        w = w[:m.start()] + ({"e": "ê", "o": "ô"} if c == "r" else {"ê": "ê"}).get(v, ACUTE.get(v, v))
    elif m and not final_stress and m.group(1) in "ae" and m.group(2) in "lr":
        # Convenção 1.1 and Convenção 4: an unstressed open final vowel before a lost -l or -r takes the grave
        # accent, and it carries no other accent (açucà, amabè).
        w = strip_accents(w[:m.start()]) + {"a": "à", "e": "è"}[m.group(1)]
    w = re.sub(f"n?[sz](?=[^{VOWELS}s])", "h", w)                    # Convenção 2.1: Lihboa, ihtrumentu
    if w.endswith(("s", "z")):
        if mono and (w.endswith("z") or any(c in ACCENTED for c in w)):
            w = w[:-1] + "h"                                         # Convenção 2.1: trêh, Deuh
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


def translate(text: str) -> str:
    """Translate pt-PT text to Barranquenho, one sentence or line at a time. Spacing and punctuation are kept."""
    # Periphrases, Gramática IV 1.3 and Convenção 3.1: estar a + infinitive takes the gerund (nuh ehtá bendu);
    # ir + infinitive takes a (bô a fazê), and a pronoun on the infinitive climbs before ir (me bô a labá).
    text = re.sub(r"\b(est\w+(?:-\w+)?) a (\w+?)([aei])r\b", r"\1 \2\3ndo", text, flags=re.IGNORECASE)
    text = re.sub(rf"\b({IR}) (\w+[aeiô]r)-({CLITIC_WORDS})\b", r"\3 \1 a \2", text, flags=re.IGNORECASE)
    text = re.sub(rf"\b({IR}) (\w+[aeiô]r)\b", r"\1 a \2", text, flags=re.IGNORECASE)
    # Convenção 2.7: a genti ten que tê fé.
    text = re.sub(r"\b(tenho|tens|tem|temos|têm|tinha|tinham|ter|terá|terão) de\b", r"\1 que", text, flags=re.IGNORECASE)
    # Convenção 1.6: inda at the start of a sentence, ainda at the end.
    text = re.sub(r"^(\W*)ainda\b", r"\1inda", text, flags=re.IGNORECASE)
    parts = re.split(r"(\w+(?:-\w+)*)", text)                      # separators at even indices, words at odd
    prev = None                          # index in parts of the previous word, when only spaces separate them
    prev_src = ""                        # that word in Portuguese, lowercased
    for i in range(1, len(parts), 2):
        tok, low = parts[i], parts[i].lower()
        if parts[i - 1].strip():
            prev, prev_src = None, ""
        before = parts[prev].lower() if prev is not None else ""
        next_src = parts[i + 2].lower() if i + 2 < len(parts) and not parts[i + 1].strip() else ""
        if any(c.isdigit() for c in tok) or re.fullmatch(r"[IVXLCDM]+", tok) or (len(tok) > 1 and tok.isupper()):
            prev, prev_src = i, low                                      # numbers, Roman numerals, acronyms
            continue
        verb, *clitics = low.split("-")
        if clitics and all(c in CLITICS for c in clitics):
            # Gramática IV 1.1: the pronoun goes before the verb (elih u torrabon lá), me before se (me se meti).
            if clitics[-1] in ("lo", "la", "los", "las"):
                verb += "s" if verb.endswith("mo") else "r"            # Portuguese: entendêmo-lo, fazê-lo
            clitics.sort(key=lambda c: c not in ("me", "te"))
            res = " ".join(CLITICS[c] for c in clitics) + " " + word(verb)
        elif low == "se" and prev_src not in PROCLISIS and (next_src in CONJUNCTION_NEXT or SUBJUNCTIVE.search(next_src)):
            res = "si"                                                  # Convenção 1.1: comu si fossi
        elif low in TONIC_POSSESSIVE and before and (not next_src or next_src in CLOSED):
            res = TONIC_POSSESSIVE[low][:-1] if before.endswith("h") and low.endswith("s") else TONIC_POSSESSIVE[low]
        elif low == "quem" and prev is None and "?" in "".join(parts[i:]).split(".")[0]:
            res = "quén"                                                # Gramática III 1.1.7: quén se casô?
        elif low in POSSESSIVE_PLURAL and before.endswith("h"):
            res = POSSESSIVE_PLURAL[low]
        elif low in GENDER:
            res, gender = GENDER[low]
            if before in ARTICLE_FLIP[gender]:
                flipped = ARTICLE_FLIP[gender][before]
                parts[prev] = flipped[0].upper() + flipped[1:] if parts[prev][0].isupper() else flipped
        else:
            res = "-".join(word(t) for t in low.split("-"))
            if before == "tú" and low.endswith("s") and low not in CLOSED and not res.endswith("h"):
                res += "h"                                                # Convenção 2.1: tú labah, ela laba
            if PSEUDO_REFLEXIVE.match(low) and before not in CLITIC_OUTPUT:
                res = "se " + res                                         # Gramática IV 1.4: já se morreu
        parts[i] = res[0].upper() + res[1:] if tok[0].isupper() else res
        prev, prev_src = i, low
    # Convenção 1.5: me, te, se lose their vowel before a vowel (m'apeteci, s'usabon).
    return re.sub(r"\b([mts])e ([aeiouáéíóúâêôãõ])", r"\1'\2", "".join(parts))


def main() -> None:
    for line in sys.stdin:
        print(translate(line.strip()))


if __name__ == "__main__":
    main()
