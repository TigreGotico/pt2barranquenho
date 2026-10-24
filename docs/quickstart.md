# Quickstart

## Install

The package has no dependencies. Install it from the repository:

```bash
git clone https://github.com/TigreGotico/pt2barranquenho
cd pt2barranquenho
uv pip install -e .
```

## Command line

`pt2barranquenho` reads Portuguese from standard input, one line at a time, and prints one Barranquenho line for each:

```bash
echo "Os meus tios compraram pão." | pt2barranquenho
# Uh mê tiu compraron pãu.

pt2barranquenho < dialog.txt > dialog.barr.txt
```

## Python

```python
from pt2barranquenho import translate, word

translate("A minha mãe disse-me que o leite estava frio.")
# 'A minha mãi me dissi que a lêti ehtaba friu.'

word("espanhol")
# 'ehpanhó'
```

`translate` takes one sentence or line. `word` takes one lowercase word and applies the spelling rules with no context. The [API page](api.md) gives the details.

## OVOS dialog files

`translate` leaves template slots, names and acronyms as they are, so it can convert the dialog files of an OVOS skill line by line:

```python
translate("Eu sou {name}")       # 'Eu sô {name}'
translate("O PS e o PCP")        # 'U PS i u PCP'
```

## Browser demo

The Hugging Face Space [TigreGotico/pt2barranquenho](https://huggingface.co/spaces/TigreGotico/pt2barranquenho) runs the same package in the browser with Pyodide. The page is `space/index.html` in this repository. It loads `pt2barranquenho/__init__.py` from the Space files, so a new version of the package needs a new upload of that file.
