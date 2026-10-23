"""Rule-based Portuguese (pt-PT) to Barranquenho, after the 2025 Convenção Ortográfica do Barranquenho and the
Gramática Básica de Barranquenho (Gonçalves, Navas, Ferreira). Section numbers below refer to the Gramática.

    echo "Os meus tios compraram pão." | pt2barranquenho
"""
import re
import sys
import unicodedata

VOWELS = "aeiouáéíóúâêôãõàèü"
ACCENTED = "áéíóúâêôãõàè"
ACUTE = {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú"}

# Closed classes, from Tabelas 1 to 10: articles and their contractions, pronouns, possessives, demonstratives,
# indefinites, relatives, interrogatives and numerals. The plural keeps the aspirated -h on these words only.
CLOSED = {
    "o": "u", "os": "uh", "a": "a", "as": "ah", "um": "un", "uns": "unh", "uma": "uma", "umas": "umah",
    "ao": "ò", "aos": "auh", "à": "à", "às": "àh", "do": "du", "dos": "duh", "da": "da", "das": "dah",
    "no": "nu", "nos": "nuh", "na": "na", "nas": "nah", "pelo": "pelu", "pelos": "peluh", "pela": "pela",
    "pelas": "pelah", "num": "nun", "nuns": "nunh", "numa": "numa", "numas": "numah", "dum": "dun",
    "duns": "dunh", "duma": "duma", "dumas": "dumah", "em": "en", "por": "pur", "e": "i", "ou": "o",
    "eu": "eu", "tu": "tú", "ele": "eli", "ela": "ela", "nós": "nóh", "vós": "bóh", "eles": "elih",
    "elas": "elah", "você": "bocê", "vocês": "bocedi", "mim": "min", "comigo": "comigu", "contigo": "contigu",
    "connosco": "connóh", "lhe": "le", "lhes": "leh", "vos": "buh", "dele": "deli", "deles": "delih",
    "delas": "delah", "nele": "neli", "neles": "nelih", "nelas": "nelah",
    "meu": "mê", "teu": "tê", "seu": "sê", "meus": "mêh", "teus": "têh", "seus": "sêh", "minhas": "minhah",
    "tuas": "tuah", "suas": "suah", "nossos": "nossuh", "nossas": "nossah", "vosso": "bossu", "vossa": "bossa",
    "vossas": "bossah", "estes": "ehtih", "estas": "ehtah", "esses": "essih", "essas": "essah",
    "aqueles": "aquelih", "aquelas": "aquelah", "isto": "ihtu",
    "alguns": "algunh", "algumas": "algumah", "nenhuns": "nenhunh", "nenhumas": "nenhumah", "outro": "otru",
    "outra": "otra", "outros": "otruh", "outras": "otrah", "todos": "toduh", "todas": "todah",
    "certos": "certuh", "certas": "certah", "muito": "muntu", "muita": "munta", "muitos": "muntuh",
    "muitas": "muntah", "pouco": "pocu", "pouca": "poca", "poucos": "pocuh", "poucas": "pocah",
    "qualquer": "qualqué", "quaisquer": "quaihqué", "alguém": "alguén", "ninguém": "ninguén", "tudo": "tudu",
    "cujos": "cujuh", "cujas": "cujah", "quantos": "quantuh", "quantas": "quantah", "qual": "quà",
    "quais": "quaih", "dois": "doih", "duas": "duah", "três": "trêh", "seis": "seih", "dez": "déh",
    "dezasseis": "dezassei", "dezassete": "dezasseti", "mais": "maih", "mas": "mah", "sob": "so", "me": "me", "te": "te", "se": "se", "si": "si",
    "quanto": "quantu", "quanta": "quanta", "pois": "poih", "deus": "deuh", "depois": "dehpoi",
    # Verb forms the Gramática gives as irregular (1.2.5, 1.6).
    "lho": "su", "lha": "sa", "lhos": "suh", "lhas": "sah",
    "quer": "què", "há": "hai", "somos": "semu", "és": "eri", "sou": "sô", "estou": "tô", "estive": "ehtubi",
    "andei": "andubi", "vir": "bi",
}
# Atonic object pronouns that move before the verb (1.1.2, 1.8): elided before a vowel when the table allows it.
CLITICS = {"me": ("me", "m'"), "te": ("te", "t'"), "se": ("se", "s'"), "lhe": ("le", "le "), "lhes": ("leh", "leh "),
           "nos": ("nuh", "nuh "), "vos": ("buh", "buh "), "o": ("u", "u "), "a": ("a", "a "), "os": ("uh", "uh "),
           "as": ("ah", "ah "), "no": ("u", "u "), "na": ("a", "a "),
           "nas": ("ah", "ah "), "lo": ("lu", "lu "), "la": ("la", "la "), "los": ("luh", "luh "),
           "las": ("lah", "lah "), "lho": ("su", "su "), "lha": ("sa", "sa "), "lhos": ("suh", "suh "),
           "lhas": ("sah", "sah ")}
# Nouns whose gender follows Spanish (1.2.2.1): the form and the article that goes with it.
GENDER = {"leite": ("lêti", "f"), "mel": ("mé", "f"), "sangue": ("sangui", "f"), "riso": ("risa", "f"),
          "laranjeira": ("laranjêru", "m"), "macieira": ("maçanêru", "m"), "amendoeira": ("amendoêru", "m"),
          "cerejeira": ("cerejêru", "m"), "tangerineira": ("tangerinêru", "m"), "romãzeira": ("romanêru", "m"),
          "ameixieira": ("amexêru", "m")}
ARTICLE_FLIP = {"m": {"a": "u", "uma": "un", "da": "du", "na": "nu", "à": "ò", "pela": "pelu"},
                "f": {"u": "a", "un": "uma", "du": "da", "nu": "na", "ò": "à", "pelu": "pela"}}
# After a plural determiner the possessive drops its own plural mark: ah minha filha, uh tê pai.
POSSESSIVE_PLURAL = {"meus": "mê", "teus": "tê", "seus": "sê", "minhas": "minha", "tuas": "tua", "suas": "sua",
                     "nossos": "nossu", "nossas": "nossa"}
IR = r"(?:vou|vais|vai|vamos|vão|ia|ias|íamos|iam|fui|foste|foi|fomos|foram)"
CLITIC_WORDS = "me|te|se|nos|vos|lhe|lhes"
CLITIC_OUTPUT = {"me", "te", "se", "nuh", "buh", "le", "leh", "m'", "t'", "s'"}
# Verbs that take a pseudo-reflexive se in their finite forms (IV 1.4): casar, cair, dormir, ir, morrer, sair.
PSEUDO_REFLEXIVE = re.compile(r"^(?:cas(?:ou|aram|ei|aste)|ca(?:iu|íram|í|íste)|morr(?:eu|eram|i|este)|"
                              r"sa(?:iu|íram|í|íste)|dorm(?:iu|iram)|foram)$")


def strip_acute(s):
    return unicodedata.normalize("NFC", "".join(c for c in unicodedata.normalize("NFD", s) if c not in "́̂"))


def nuclei(w):
    """Syllable nuclei: a vowel with an optional falling glide (pai, céu, mãe); a hiatus counts twice (frio, tios)."""
    w = re.sub(r"(?<=[qg])u(?=[eiéíê])", "_", w)                    # the u of que, gui is not a vowel
    return list(re.finditer(f"ão|ãe|õe|ãi|õi|[aeoáéóâêôàèãõ][iu](?![{VOWELS}])|[{VOWELS}]", w))


def stressed_nucleus(w):
    """Index of the stressed nucleus, by the Portuguese accent rules."""
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


def word(w):
    if w in CLOSED:
        return CLOSED[w]
    if not re.search(f"[{VOWELS}]", w):
        return w
    orig = w
    stress, groups = stressed_nucleus(w)
    final_stress = stress == len(groups) - 1
    mono = len(groups) == 1
    if w.startswith("h"):
        w = w[1:]
    w = w.replace("v", "b")
    # 1pl: the present -amos becomes -emu, the preterite -ámos becomes -amu (1.2.5.2 and the amá table).
    if w.endswith("ámos") and len(groups) > 2 and not re.search(r"[áí]", w[:-4]):
        return re.sub(r"ámos$", "amu", w)
    w = re.sub(r"amos$", "emos", w) if len(groups) > 2 and not any(c in ACCENTED for c in w) else w
    w = re.sub(r"ãos$", "õi", w)                                     # irmãos > irmõi: plural of -ãu is -õi (1.2.3)
    w = w.replace("ão", "ãu")
    w = re.sub(r"ães$", "ãi", w)
    w = re.sub(r"ões$", "õi", w)
    w = re.sub(r"ãe$", "ãi", w)
    w = re.sub(r"am$", "on", w) if not final_stress else w
    w = re.sub(f"(?<=[{VOWELS}])m$", "n", w)
    w = re.sub(r"ui(?=t)", "un", w)
    w = re.sub(r"qu(?=[aoáóâô])", "cu", w)                            # quando > cuandu (2.1.1)
    w = re.sub(f"x(?=[^{VOWELS}])", "h", w)                          # texto > tehtu
    w = re.sub(r"ai(?=x)", "a", w)                                   # abaixo > abaxu (1.6)
    w = re.sub(r"ou", "ô" if final_stress and re.search(r"ou$", w) else "o", w)
    w = re.sub(r"ei(?=[aou]s?$)", "ê", w)                           # ideia > idêa, recheio > rechêu (1.6)
    groups_now = nuclei(w)
    if len(groups_now) == len(groups) and groups_now[stress].group().startswith("ei"):
        g = groups_now[stress]
        w = w[:g.start()] + "ê" + w[g.start() + 2:]
    w = w.replace("ei", "e")
    # Final -l, -r, -z after the stressed vowel are silent (2.1.4, 2.1.5); monosyllables keep -l (mal, tal).
    m = re.search(r"([aeiouêô])([lrz])$", w)
    if m and final_stress and not (mono and m.group(2) == "l") and not (mono and m.group(2) == "z"):
        v, c = m.group(1), m.group(2)
        w = w[:m.start()] + ({"e": "ê", "o": "ô"} if c == "r" else {"ê": "ê"}).get(v, ACUTE.get(v, v))
    elif m and not final_stress and m.group(1) in "ae" and m.group(2) in "lr":
        w = strip_acute(w[:m.start()]) + {"a": "à", "e": "è"}[m.group(1)]   # açúcar > açucà, amável > amabè
    w = re.sub(f"n?[sz](?=[^{VOWELS}s])", "h", w)                  # Lisboa > Lihboa, instrumento > ihtrumentu
    if w.endswith(("s", "z")):
        if mono and (w.endswith("z") or any(c in ACCENTED for c in w)):
            w = w[:-1] + "h"                                         # mês > mêh, fez > feh; pais > pai
        else:
            w = w[:-1]
            w = re.sub(r"ê$", "é", w) if orig.endswith("ês") else w  # português > portugué
    if not final_stress:
        w = re.sub(r"o$", "u", w)
        w = re.sub(r"e$", "i", w)
    elif not mono and re.search(f"(?:[^{VOWELS}]|[qg]u)[iu]$", w) and not any(c in ACCENTED for c in w):
        w = w[:-1] + ACUTE[w[-1]]                                    # aqui > aquí
    return w


def translate(text):
    """Translate pt-PT text to Barranquenho, one sentence or line at a time."""
    # Periphrases (IV 1.3): estar a + infinitive takes the gerund; ir + infinitive takes a, and a clitic on the
    # infinitive climbs before ir (vou lavar-me > me bô a labá).
    text = re.sub(r"\b(est\w+(?:-\w+)?) a (\w+?)([aei])r\b", r"\1 \2\3ndo", text, flags=re.I)
    text = re.sub(rf"\b({IR}) (\w+[aeiô]r)-({CLITIC_WORDS})\b", r"\3 \1 a \2", text, flags=re.I)
    text = re.sub(rf"\b({IR}) (\w+[aeiô]r)\b", r"\1 a \2", text, flags=re.I)
    text = re.sub(r"\b(tenho|tens|tem|temos|têm|tinha|tinham|ter) de\b", r"\1 que", text, flags=re.I)
    text = re.sub(r"\b(como )se\b", r"\1si", text, flags=re.I)
    text = re.sub(r"\b([Ss])e (?=(?:o|a|os|as|eu|tu|ele|ela|nós|você|vocês)\b)", lambda m: ("S" if m.group(1) == "S" else "s") + "i ", text, flags=re.I)
    text = re.sub(r"^(\W*)ainda\b", r"\1inda", text, flags=re.I)
    out = []
    for tok in re.findall(r"\w+(?:-\w+)*|[^\w\s]", text):
        if not tok[0].isalnum():
            out.append(tok)
            continue
        low = tok.lower()
        verb, *clitics = low.split("-")
        if clitics and all(c in CLITICS for c in clitics):
            if clitics[-1] in ("lo", "la", "los", "las"):
                verb += "s" if verb.endswith("mo") else "r"            # entendêmo-lo, fazê-lo
            clitics.sort(key=lambda c: c not in ("me", "te"))          # me se meti (IV 1.1)
            res = " ".join(CLITICS[c][0] for c in clitics) + " " + word(verb)
        elif low in POSSESSIVE_PLURAL and out and out[-1].endswith("h"):
            res = POSSESSIVE_PLURAL[low]
        elif low in GENDER:
            res, gender = GENDER[low]
            if out and out[-1].lower() in ARTICLE_FLIP[gender]:
                out[-1] = ARTICLE_FLIP[gender][out[-1].lower()]
        else:
            res = " ".join(word(t) for t in low.split("-"))
            if PSEUDO_REFLEXIVE.match(low) and not (out and out[-1].lower() in CLITIC_OUTPUT):
                res = "se " + res                                         # já se morreu (IV 1.4)
        out.append(res[0].upper() + res[1:] if tok[0].isupper() else res)
    s = " ".join(out)
    s = re.sub(r"\b([mts])e ([aeiouáéíóúâêôãõ])", r"\1'\2", s)         # m'apeteci, s'usabon (1.8)
    s = re.sub(r"\s([?.!,;:\])])", r"\1", s)
    return re.sub(r"([\[(¿¡])\s", r"\1", s)


def main():
    for line in sys.stdin:
        print(translate(line.strip()))


if __name__ == "__main__":
    main()
