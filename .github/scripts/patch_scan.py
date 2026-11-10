"""Ubah teks Role & Languages pada SVG system-scan dari gitskins."""
import re
import sys

ROLE = "IT Developer"


def value_after(label, svg, fn):
    # Nilai berada di <text> pertama setelah <text>Label</text>
    pattern = re.compile(r"(>" + label + r"</text>.*?<text[^>]*>)([^<]*)(</text>)", re.S)
    return pattern.sub(lambda m: m.group(1) + fn(m.group(2)) + m.group(3), svg, count=1)


def fix_langs(value):
    langs = [l.strip() for l in value.split(",")]
    out = []
    for l in langs:
        l = "PHP" if l == "HTML" else l
        if l and l not in out:
            out.append(l)
    return ", ".join(out)


for path in sys.argv[1:]:
    svg = open(path, encoding="utf-8").read()
    svg = value_after("Role", svg, lambda _: ROLE)
    svg = value_after("Languages", svg, fix_langs)
    open(path, "w", encoding="utf-8").write(svg)
