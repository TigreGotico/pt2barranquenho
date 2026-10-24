"""Choose pt-PT sentences from OVOS dialog and intent files for a native speaker to translate, spread over the rule areas.

    python scripts/native_sheet.py <file.dialog|file.intent>... > gold/native_todo.tsv

A line qualifies when it has 4 to 25 words, no template syntax, Portuguese function words, and no pt-BR
marker. The lines are sorted by a hash of their text, so the same files always give the same sheet. Each area
takes up to its quota in that order; plain spelling fills the rest. No skill gives more than PER_SOURCE lines,
and one skill gives one line per opening two words, so the expansions of one intent template count once.
"""
import csv
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

from pt2barranquenho import translate

SIZE = 150
PER_SOURCE = 10
# Checked in order: a line belongs to the first area whose pattern it matches.
AREAS = {
    "gostar": (re.compile(r"\bgost\w+", re.IGNORECASE), 15),
    "faz": (re.compile(r"\bfaz\s+(?:\w+\s+)?(?:anos?|meses|dias|horas|minutos|semanas|tempo)\b", re.IGNORECASE), 10),
    "perfect": (re.compile(r"\b(?:tenho|tens|tem|temos|têm)\s+\w+(?:ado|ido)\b", re.IGNORECASE), 15),
    "periphrasis": (re.compile(r"\b(?:estou|estás|está|estamos|estão|estava)\s+a\s+\w+r\b|\b(?:vou|vais|vai|vamos|vão)\s+\w+r\b"
                               r"|\b(?:tenho|tens|tem|temos|têm)\s+de\b", re.IGNORECASE), 30),
    "pronoun": (re.compile(r"\w-(?:me|te|se|lhe|lhes|nos|vos|o|a|os|as|lo|la)\b|\b(?:me|te|se|lhe|nos)\s+\w+[aeo]\b",
                           re.IGNORECASE), 30),
}
PORTUGUESE = re.compile(r"\b(?:o|a|os|as|de|do|da|que|não|um|uma|para|com|em|no|na|é|eu)\b", re.IGNORECASE)
# The OVOS pt-PT files carry pt-BR lines and broken ones: a clitic before the verb at the start, a possessive
# without its article, a gerund, BR vocabulary, "tu" with a 3rd person verb, words typed without accents, and
# a determiner that does not agree with its noun.
NOT_PT_PT = re.compile(r"\bvocê|\bcara\b|\bgente\b|\btela\b|\bplayer\b|\bmídia|\bhabilidades?\b|\bretorn\w+"
                       r"|\w+ndo\b|\btu gostaria\b|\btenho certeza|\bpor favor me\b|\b(?:para|com|de) (?:meu|minha|sua)\b"
                       r"|(?:^|[.!?]\s+)(?:me|te|se|lhe|meu|minha|meus|minhas)\s|\bsua própria"
                       r"|\b(?:estao|esta a|ultima|nao|voce)\b|\w+cao\b|\bo reprodução|\bé tu é", re.IGNORECASE)
TEMPLATE = re.compile(r"[{}()|\[\]<>#]|\s{2}")    # two spaces: a slot cut out of an intent template


def area(line: str) -> str:
    return next((name for name, (pattern, _) in AREAS.items() if pattern.search(line)), "spelling")


def qualifies(line: str) -> bool:
    words = re.findall(r"\w{4,}", line.lower())
    if words and any(w[:4] == words[-1][:4] for w in words[:-1]):     # "a hora actual horas": a broken expansion
        return False
    return 4 <= len(line.split()) <= 25 and not TEMPLATE.search(line) and len(PORTUGUESE.findall(line)) >= 2 \
        and not NOT_PT_PT.search(line)


def main():
    lines = {}
    for path in map(Path, sys.argv[1:]):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if qualifies(line):
                lines.setdefault(line, path.parts[path.parts.index("locale") - 1].replace("_", "-")
                                 if "locale" in path.parts else path.parent.name)
    print(f"files={len(sys.argv) - 1} lines={len(lines)}", file=sys.stderr)
    ordered = sorted(lines, key=lambda s: hashlib.sha256(s.encode()).hexdigest())
    chosen, taken, openings = [], Counter(), set()
    for name, (pattern, quota) in [*AREAS.items(), ("spelling", (None, SIZE))]:
        for line in ordered:
            opening = (lines[line], *line.lower().split()[:2])
            if len(chosen) < SIZE and taken[name] < quota and line not in chosen and area(line) == name \
                    and taken[lines[line]] < PER_SOURCE and opening not in openings:
                chosen.append(line)
                openings.add(opening)
                taken[name] += 1
                taken[lines[line]] += 1
    out = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    out.writerow(["id", "pt", "rules", "barr", "area", "source"])
    for i, line in enumerate(chosen, 1):
        out.writerow([f"n{i:03d}", line, translate(line), "", area(line), lines[line]])
    print(f"rows={len(chosen)} " + " ".join(f"{k}={taken[k]}" for k in [*AREAS, "spelling"]), file=sys.stderr)


if __name__ == "__main__":
    main()
