"""Ordinary pt-PT sentences that exercise one rule each, compared case-sensitively. Where a book prints the form, the
comment names the section; the other expected values follow from the rule the comment names."""
import pytest

from pt2barranquenho import translate

CASES = {
    # se: the conjunction is si, the pronoun se (Convenção 1.1); nãu sê si, Gramática III 1.2.5.1.
    "Se for preciso": "Si fô precisu",
    "Se é assim": "Si é assin",
    "Se tens fome": "Si ten fomi",
    "Não sei se vem": "Nãu sê si ben",
    "Só se ele quiser": "Só si eli quisê",
    "Queria que eles se casassem": "Queria que elih se casassen",
    "Se ele se lembrar": "Si eli se lembrá",
    "e se parava": "i se paraba",
    # The preterite of ser is not a periphrasis with ir, and foram takes se only as a verb of motion.
    "O objetivo foi criar emprego": "U objetibu foi criá empregu",
    "Os resultados foram muito bons": "Uh resultadu foron muntu bon",
    "e logo foram à missa": "i logu se foron à missa",
    "foi ver os pais": "foi a bê uh pai",
    # The pseudo-reflexive pronoun agrees with the person: me casê (Convenção 1.7).
    "Eu casei": "Eu me casê",
    # A pronoun stays after an infinitive (Gramática IV 1.1) and climbs before an auxiliary (Gramática IV 1.3).
    "Quero fazê-lo": "Queru fazê-lu",
    "Estou a ver-te": "Te tô bendu",
    "Vou lavar-me": "Me bô a labá",
    # Elision before a vowel, not across a hyphen (Convenção 1.5).
    "Me apetece": "M'apeteci",
    "é preciso ser-se engraçado": "é precisu sê-se engraçadu",
    # ainda: inda except at the end of a sentence, and the capital stays (Convenção 1.6).
    "Ainda hoje são amigos": "Inda oji sãu amigu",
    "Ainda não vi o João": "Inda nãu bi u Joãu",
    "Não vi o João ainda": "Nãu bi u Joãu ainda",
    # Only forms of estar and ter de + infinitive start a periphrasis.
    "A estrada a seguir": "A ehtrada a seguí",
    "Ele tem de tudo": "Eli ten de tudu",
    # Final -l: dropped except in mal, tal, cual (Convenção 2.6); unstressed -il (Gramática III 1.2.3).
    "sol": "só",
    "mal": "mal",
    "difícil": "difici",
    "circuito": "circuitu",
    # -ãos takes the plural -õi of the nouns in -ãu (Gramática III 1.2.3).
    "irmãos": "irmõi",
    # Case.
    "ÉS TU?": "ERI TÚ?",
    "Pedro-Miguel": "Pedru-Migué",
    "O PS e o PCP": "U PS i u PCP",
}


@pytest.mark.parametrize("pt", CASES)
def test_sentence(pt):
    assert translate(pt) == CASES[pt]
