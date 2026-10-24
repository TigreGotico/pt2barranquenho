"""The closed-class tables of Gramática III 1.1.2 to III 1.1.8 (PDF pages g24 to g28): personal pronouns,
possessives, demonstratives, relatives, indefinites and numerals. A possessive is tested before a noun, and a
compound numeral as its words. Left out: qual and quatro, where the Convenção prints cual and cuatru (rules/README.md),
and the 2nd person plural."""
import pytest

from pt2barranquenho import translate

# Portuguese and Barranquenho, "_" for a space.
TABLES = """eu eu|tu tú|ele eli|ela ela|nós nóh|eles elih|elas elah|vocês bocedi|comigo comigu|contigo contigu|mim min|ti ti
connosco connóh|dele deli|dela dela|deles delih|delas delah|nele neli|nela nela|neles nelih|nelas nelah
meu_pai mê_pai|teu_tio tê_tiu|seu_amigo sê_amigu|meus_pais mêh_pai|minha_casa minha_casa|minhas_casas minhah_casa
tuas_casas tuah_casa|suas_casas suah_casa|nosso_pai nossu_pai|nossos_pais nossuh_pai|nossas_casas nossah_casa
este ehti|esta ehta|estes ehtih|estas ehtah|esse essi|essa essa|esses essih|essas essah|aquele aqueli|aquela aquela
aqueles aquelih|aquelas aquelah|isto ihtu|isso issu|aquilo aquilu
cujo cuju|cuja cuja|cujos cujuh|cujas cujah|quanto quantu|quanta quanta|quantos quantuh|quantas quantah|quais quaih
algum algun|alguma alguma|alguns algunh|algumas algumah|nenhum nenhun|nenhuma nenhuma|nenhuns nenhunh|nenhumas nenhumah
outro otru|outra otra|outros otruh|outras otrah|todo todu|toda toda|todos toduh|todas todah|um un|uma uma|uns unh|umas umah
certo certu|certa certa|certos certuh|certas certah|muito muntu|muita munta|muitos muntuh|muitas muntah
pouco pocu|pouca poca|poucos pocuh|poucas pocah|qualquer qualqué|quaisquer quaihqué
alguém alguén|ninguém ninguén|nada nada|tudo tudu|outrem otrén
zero zeru|dois doih|duas duah|três trêh|cinco cincu|seis seih|sete seti|oito oitu|nove nobi|dez déh|onze onzi
doze dozi|treze trezi|catorze catorzi|quinze quinzi|dezasseis dezassei|dezassete dezasseti|dezoito dezoitu
dezanove dezanobi|vinte binti|vinte_e_um bintiun|vinte_e_dois bintidoi|vinte_e_três bintitré"""


@pytest.mark.parametrize(("pt", "barr"), [tuple(x.replace("_", " ") for x in pair.split())
                                          for pair in TABLES.replace("\n", "|").split("|")], ids=lambda x: x)
def test_printed_form(pt, barr):
    assert translate(pt) == barr
