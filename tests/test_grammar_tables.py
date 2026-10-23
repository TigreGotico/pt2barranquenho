"""The paradigms printed in the Gramática Básica de Barranquenho (2025), table by table. The expected forms are
copied from the book, so a failure here is a rule that disagrees with the grammar."""
import pytest

from pt2barranquenho import translate, word

ARTICLES = {  # Tabelas 1 to 3
    "o": "u", "os": "uh", "a": "a", "as": "ah", "um": "un", "uns": "unh", "uma": "uma", "umas": "umah",
    "ao": "ò", "aos": "auh", "à": "à", "às": "àh", "do": "du", "dos": "duh", "da": "da", "das": "dah",
    "no": "nu", "nos": "nuh", "na": "na", "nas": "nah", "pelo": "pelu", "pelos": "peluh", "pela": "pela",
    "pelas": "pelah", "num": "nun", "nuns": "nunh", "numa": "numa", "numas": "numah", "dum": "dun", "duns": "dunh",
}
DETERMINERS = {  # Tabelas 4 to 9
    "eu": "eu", "tu": "tú", "ele": "eli", "eles": "elih", "elas": "elah", "nós": "nóh", "mim": "min",
    "comigo": "comigu", "connosco": "connóh", "meu": "mê", "teu": "tê", "seu": "sê", "meus": "mêh",
    "este": "ehti", "esta": "ehta", "estes": "ehtih", "estas": "ehtah", "esse": "essi", "essa": "essa",
    "aquele": "aqueli", "aquela": "aquela", "aqueles": "aquelih", "isto": "ihtu", "isso": "issu",
    "aquilo": "aquilu", "algum": "algun", "alguns": "algunh", "nenhum": "nenhun", "outro": "otru",
    "todos": "toduh", "muito": "muntu", "muita": "munta", "pouco": "pocu", "qualquer": "qualqué",
    "alguém": "alguén", "ninguém": "ninguén", "tudo": "tudu", "dois": "doih", "três": "trêh", "seis": "seih",
    "dez": "déh", "onze": "onzi", "doze": "dozi", "catorze": "catorzi", "dezoito": "dezoitu", "dezanove": "dezanobi",
    "vinte": "binti", "dezasseis": "dezassei",
}
VERBS = {  # amá and comê, regular paradigms
    "amar": "amá", "amo": "amu", "ama": "ama", "amamos": "amemu", "amam": "amon", "amava": "amaba",
    "amávamos": "amábamu", "amavam": "amabon", "amei": "amê", "amou": "amô", "amámos": "amamu",
    "amaram": "amaron", "amando": "amandu", "amado": "amadu", "amasse": "amassi",
    "comer": "comê", "como": "comu", "come": "comi", "comemos": "comemu", "comem": "comen", "comia": "comia",
    "comíamos": "comíamu", "comiam": "comion", "comi": "comí", "comeu": "comeu", "comeram": "comeron",
    "comendo": "comendu", "comido": "comidu",
}
SENTENCES = {  # IV Sintaxe
    "vou lavar-me": "me bô a labá",
    "foi ver os pais": "foi a bê uh pai",
    "está-nos a ver": "nuh ehtá bendu",
    "mete-se-me na cabeça": "me se meti na cabeça",
    "já morreu": "já se morreu",
    "e logo foram à missa": "i logu se foron à missa",
    "eles torravam-no lá": "elih u torrabon lá",
}


@pytest.mark.parametrize("pt,barr", ARTICLES.items())
def test_articles(pt, barr):
    assert word(pt) == barr


@pytest.mark.parametrize("pt,barr", DETERMINERS.items())
def test_determiners_and_pronouns(pt, barr):
    assert word(pt) == barr


@pytest.mark.parametrize("pt,barr", VERBS.items())
def test_regular_verbs(pt, barr):
    assert word(pt) == barr


@pytest.mark.parametrize("pt,barr", SENTENCES.items())
def test_syntax(pt, barr):
    assert translate(pt) == barr


def test_case_is_kept():
    assert translate("Os meus tios moram em Barrancos.") == "Uh mê tiu moron en Barrancu."
