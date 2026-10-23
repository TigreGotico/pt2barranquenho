"""The verb tables of Gramática III 1.2.5.4 (PDF pages g33 to g39), person by person. The 2sg is tested after tu, the
context that marks it. Left out: the 2pl, which pt-PT replaces with vocês; estou and estive, where the Convenção and
the Gramática text print tô and ehtubi; the 3pl present subjunctive, which the tables print as coman, partan but also
as sejon, tenhon."""
import pytest

from pt2barranquenho import translate

# Six persons per tense, Portuguese then Barranquenho; "-" marks a person that is not tested.
TABLES = {
    "amar": [
        ("amo amas ama amamos - amam", "amu amah ama amemu - amon"),
        ("ame ames ame amemos - amem", "ami amih ami amemu - amen"),
        ("amava amavas amava amávamos - amavam", "amaba amabah amaba amábamu - amabon"),
        ("amasse amasses amasse amássemos - amassem", "amassi amassih amassi amássemu - amassen"),
        ("amei amaste amou amámos - amaram", "amê amahti amô amamu - amaron"),
        ("amara amaras amara amáramos - amaram", "amara amarah amara amáramu - amaron"),
        ("amarei amarás amará amaremos - amarão", "amarê amaráh amará amaremu - amarãu"),
        ("amar amares amar amarmos - amarem", "amá amarih amá amarmu - amaren"),
        ("amaria amarias amaria amaríamos - amariam", "amaria amariah amaria amaríamu - amarion"),
    ],
    "comer": [
        ("como comes come comemos - comem", "comu comih comi comemu - comen"),
        ("coma comas coma comamos - -", "coma comah coma comamu - -"),
        ("comia comias comia comíamos - comiam", "comia comiah comia comíamu - comion"),
        ("comesse comesses comesse comêssemos - comessem", "comessi comessih comessi coméssemu - comessen"),
        ("comi comeste comeu comemos - comeram", "comí comehti comeu comemu - comeron"),
        ("comera comeras comera comêramos - comeram", "comera comerah comera coméramu - comeron"),
        ("comerei comerás comerá comeremos - comerão", "comerê comeráh comerá comeremu - comerãu"),
        ("comeria comerias comeria comeríamos - comeriam", "comeria comeriah comeria comeríamu - comerion"),
    ],
    "partir": [
        ("parto partes parte partimos - partem", "partu partih parti partimu - parten"),
        ("parta partas parta partamos - -", "parta partah parta partamu - -"),
        ("partia partias partia partíamos - partiam", "partia partiah partia partíamu - partion"),
        ("partisse partisses partisse partíssemos - partissem", "partissi partissih partissi partíssemu - partissen"),
        ("parti partiste partiu partimos - partiram", "partí partihti partiu partimu - partiron"),
        ("partira partiras partira partíramos - partiram", "partira partirah partira partíramu - partiron"),
        ("partirei partirás partirá partiremos - partirão", "partirê partiráh partirá partiremu - partirãu"),
        ("partiria partirias partiria partiríamos - partiriam", "partiria partiriah partiria partiríamu - partirion"),
    ],
    "ser": [
        ("sou és é somos - são", "sô eri é semu - sãu"),
        ("seja sejas seja sejamos - sejam", "seja sejah seja sejamu - sejon"),
        ("era eras era éramos - eram", "era erah era éramu - eron"),
        ("fosse fosses fosse fôssemos - fossem", "fossi fossih fossi fóssemu - fossen"),
        ("fui foste foi fomos - foram", "fui fohti foi fomu - foron"),
        ("fora foras fora fôramos - foram", "fora forah fora fóramu - foron"),
        ("serei serás será seremos - serão", "serê seráh será seremu - serãu"),
        ("for fores for formos - forem", "fô forih fô formu - foren"),
        ("seria serias seria seríamos - seriam", "seria seriah seria seríamu - serion"),
    ],
    "estar": [
        ("- estás está estamos - estão", "- ehtáh ehtá ehtemu - ehtãu"),
        ("esteja estejas esteja estejamos - estejam", "ehteja ehtejah ehteja ehtejemu - ehtejon"),
        ("estava estavas estava estávamos - estavam", "ehtaba ehtabah ehtaba ehtábamu - ehtabon"),
        ("estivesse estivesses estivesse estivéssemos - estivessem",
         "ehtibessi ehtibessih ehtibessi ehtibéssemu - ehtibessen"),
        ("- estiveste esteve estivemos - estiveram", "- ehtibehti ehtebi ehtibemu - ehtiberon"),
        ("estivera estiveras estivera estivéramos - -", "ehtibera ehtiberah ehtibera ehtibéramu - -"),
        ("estarei estarás estará estaremos - estarão", "ehtarê ehtaráh ehtará ehtaremu - ehtarãu"),
        ("estiver estiveres estiver estivermos - estiverem", "ehtibé ehtiberih ehtibé ehtibermu - ehtiberen"),
        ("estaria estarias - estaríamos - estariam", "ehtaria ehtariah - ehtaríamu - ehtarion"),
    ],
    "haver": [
        ("hei hás - havemos - hão", "ê áh - abemu - ãu"),
        ("haja hajas haja hajamos - hajam", "aja ajah aja ajamu - ajon"),
        ("havia havias havia havíamos - haviam", "abia abiah abia abíamu - abion"),
        ("houvesse houvesses houvesse houvéssemos - houvessem", "obessi obessih obessi obéssemu - obessen"),
        ("houve houveste houve houvemos - houveram", "obi obehti obi obemu - oberon"),
        ("houvera houveras houvera houvéramos - houveram", "obera oberah obera obéramu - oberon"),
        ("haverei haverás haverá haveremos - haverão", "aberê aberáh aberá aberemu - aberãu"),
        ("houver houveres houver houvermos - houverem", "obé oberih obé obermu - oberen"),
        ("haveria haverias haveria haveríamos - haveriam", "aberia aberiah aberia aberíamu - aberion"),
    ],
    "ter": [
        ("tenho tens tem temos - têm", "tenhu ten ten temu - tenhen"),
        ("tenha tenhas tenha tenhamos - tenham", "tenha tenhah tenha tenhemu - tenhon"),
        ("tinha tinhas tinha tínhamos - tinham", "tinha tinhah tinha tínhamu - tinhon"),
        ("tivesse tivesses tivesse tivéssemos - tivessem", "tibessi tibessih tibessi tibéssemu - tibessen"),
        ("tive tiveste teve tivemos - tiveram", "tibi tibehti tebi tibemu - tiberon"),
        ("tivera tiveras tivera tivéramos - -", "tibera tiberah tibera tibéramu - -"),
        ("tiver tiveres tiver tivermos - tiverem", "tibé tiberih tibé tibermu - tiberen"),
        ("teria terias teria teríamos - teriam", "teria teriah teria teríamu - terion"),
    ],
}
NONFINITE = [("amado", "amadu"), ("amando", "amandu"), ("comer", "comê"), ("comido", "comidu"),
             ("comendo", "comendu"), ("partir", "partí"), ("partido", "partidu"), ("partindo", "partindu"),
             ("ser", "sê"), ("sido", "sidu"), ("sendo", "sendu"), ("estado", "ehtadu"), ("estando", "ehtandu"),
             ("haver", "abê"), ("havido", "abidu"), ("havendo", "abendu"), ("ter", "tê"), ("tido", "tidu")]


def cases():
    for tenses in TABLES.values():
        for pt, barr in tenses:
            for person, (p, b) in enumerate(zip(pt.split(), barr.split(), strict=True)):
                if p != "-":
                    yield (f"tu {p}", f"tú {b}") if person == 1 else (p, b)
    yield from NONFINITE


@pytest.mark.parametrize(("pt", "barr"), list(cases()), ids=lambda x: x)
def test_printed_form(pt, barr):
    assert translate(pt) == barr
