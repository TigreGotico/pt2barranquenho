"""The filter that chooses sentences for the native-speaker sheet."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("native_sheet", Path(__file__).parent.parent / "scripts" / "native_sheet.py")
native_sheet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native_sheet)


@pytest.mark.parametrize("line", [
    "Não sei do que estás a falar!",
    "Concentra-te no que estás a fazer.",
    "Queres definir esta como a tua cor de olhos predefinida?",
])
def test_a_pt_pt_line_qualifies(line):
    assert native_sheet.qualifies(line)


@pytest.mark.parametrize("line", [
    "Me dê uma atualização de notícias internacionais",          # clitic before the verb at the start
    "Meu cérebro está projetado para entender cores em R G B.",  # possessive without its article
    "Parece que eu tive um erro tentando definir a cor",          # gerund
    "onde posso encontrar as capturas de tela",                  # BR vocabulary
    "diz-me quem esta a bordo da estacao espacial",              # words without accents
    "Qual a cor que tu gostaria de usar?",                       # tu with a 3rd person verb
    "abrir o reprodução de media",                               # determiner does not agree
    "eu gostaria de saber a hora actual horas",                  # broken intent expansion
    "ir para a  faixa  a seguir",                                # slot cut out of a template
    "diz-me as horas em {location}",                             # template syntax
    "word net does not know the answer",                         # not Portuguese
])
def test_a_pt_br_or_broken_line_is_left_out(line):
    assert not native_sheet.qualifies(line)


def test_area_takes_the_first_matching_area():
    assert native_sheet.area("eu gosto de tirar fotos") == "gostar"
    assert native_sheet.area("Não sei do que estás a falar!") == "periphrasis"
    assert native_sheet.area("Diz-me a previsão do tempo") == "pronoun"
    assert native_sheet.area("põe o volume no máximo") == "spelling"
