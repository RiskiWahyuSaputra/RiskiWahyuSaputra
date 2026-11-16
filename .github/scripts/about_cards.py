"""Kartu intro (nama, teks mengetik, status) dan kartu About Me bergaya editor kode.

Statis: jalankan ulang kalau isi berubah.
Pemakaian: python3 .github/scripts/about_cards.py img/about
Menghasilkan hero-{dark,light}.svg dan about-{dark,light}.svg.
"""
import os
import sys
from html import escape

NAME = "Riski Wahyu Saputra"
PHRASES = ["IT Developer", "Laravel · Next.js · TypeScript", "Always learning, always shipping"]
STATUS = [("live", "Open for work"), ("book", "Learning Next.js + TypeScript")]

# isi kartu About Me: (indent, key, value) ; value berupa string atau list string
ABOUT_VAR = "riski"
ABOUT = [
    ("role", "IT Developer"),
    ("code", ["JavaScript", "TypeScript", "PHP", "SQL"]),
    ("stack", ["Next.js", "React", "Laravel", "CodeIgniter", "Tailwind"]),
    ("tools", ["Git", "GitHub", "MySQL", "Linux", "Ubuntu"]),
    ("learning", "Next.js + TypeScript at scale"),
    ("motto", "Ship it, then make it better ⚡"),
]

THEMES = {
    "dark": dict(card="#0d1117", border="#1f6feb55", bar="#161b22", line="#30363d", title="#f0f6fc",
                 muted="#9198a1", accent="#58a6ff", live="#3fb950", chip="#161b22",
                 kw="#ff7b72", var="#d2a8ff", prop="#79c0ff", str="#a5d6ff", punct="#e6edf3", gutter="#6e7681"),
    "light": dict(card="#ffffff", border="#0969da55", bar="#f6f8fa", line="#d1d9e0", title="#1f2328",
                  muted="#59636e", accent="#0969da", live="#1a7f37", chip="#f6f8fa",
                  kw="#cf222e", var="#8250df", prop="#0550ae", str="#0a3069", punct="#1f2328", gutter="#8c959f"),
}
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif"
W = 920
PAD = 28


def typing(x, y, t):
    """Teks yang diketik lalu dihapus bergantian (SMIL, per karakter)."""
    size, cw = 20, 12.0          # lebar karakter dipaksa lewat textLength
    slot, n = 4.5, len(PHRASES)
    total = slot * n
    out = []
    for k, phrase in enumerate(PHRASES):
        chars = len(phrase)
        full = chars * cw
        start = k * slot
        type_end = start + 0.07 * chars
        hold_end = start + slot - 0.9
        erase_end = start + slot - 0.3
        times, widths = [0.0], [0]
        steps = chars
        for i in range(1, steps + 1):          # ketik
            times.append(start + (type_end - start) * i / steps)
            widths.append(i * cw)
        times.append(hold_end)
        widths.append(full)
        for i in range(1, steps + 1):          # hapus
            times.append(hold_end + (erase_end - hold_end) * i / steps)
            widths.append(full - i * cw)
        times.append(total)
        widths.append(0)
        kt = ";".join(f"{min(max(tm / total, 0), 1):.4f}" for tm in times)
        vals = ";".join(f"{w:.1f}" for w in widths)
        cid = f"type-{k}"
        out.append(
            f'<clipPath id="{cid}"><rect x="{x}" y="{y - size}" width="0" height="{size + 8}">'
            f'<animate attributeName="width" values="{vals}" keyTimes="{kt}" dur="{total}s" '
            f'calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>'
            f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{t["accent"]}" '
            f'textLength="{full:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#{cid})">{escape(phrase)}</text>'
        )
        if k == 0:  # kursor mengikuti teks: posisi x = awal + lebar yang terlihat
            cursor_kt, cursor_vals = [], []
        cursor_kt.extend(kt.split(";")[1:-1])
        cursor_vals.extend(f"{x + w + 3:.1f}" for w in widths[1:-1])
    cursor_kt = ["0.0000"] + cursor_kt + ["1.0000"]
    cursor_vals = [f"{x + 3:.1f}"] + cursor_vals + [f"{x + 3:.1f}"]
    out.append(
        f'<rect x="{x + 3}" y="{y - size + 2}" width="10" height="{size + 2}" fill="{t["accent"]}" opacity=".75">'
        f'<animate attributeName="x" values="{";".join(cursor_vals)}" keyTimes="{";".join(cursor_kt)}" '
        f'dur="{total}s" calcMode="discrete" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values=".75;0;.75" dur="1s" calcMode="discrete" '
        f'repeatCount="indefinite"/></rect>'
    )
    # versi diam (tanpa SMIL) cukup menampilkan frasa pertama, ditangani browser lewat nilai awal
    return "".join(out)


def chip(x_right, y, kind, label, t):
    w = 46 + len(label) * 7.3
    x = x_right - w
    if kind == "live":
        icon = (f'<circle cx="{x + 22}" cy="{y + 18}" r="9" fill="{t["live"]}" opacity=".25" class="ping" '
                f'style="transform-origin:{x + 22}px {y + 18}px"/>'
                f'<circle cx="{x + 22}" cy="{y + 18}" r="4.5" fill="{t["live"]}"/>')
        color = t["live"]
    else:
        icon = (f'<path d="M{x + 14},{y + 11} h6 a3,3 0 0 1 3,3 v11 a2.5,2.5 0 0 0 -2.5,-2.5 h-6.5 z '
                f'M{x + 30},{y + 11} h-6 a3,3 0 0 0 -3,3 v11 a2.5,2.5 0 0 1 2.5,-2.5 h6.5 z" fill="none" '
                f'stroke="{t["accent"]}" stroke-width="1.6" stroke-linejoin="round"/>')
        color = t["accent"]
    return (f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="35" rx="17.5" fill="{t["chip"]}" '
            f'stroke="{t["line"]}"/>{icon}'
            f'<text x="{x + 38}" y="{y + 22.5}" font-family="{MONO}" font-size="12" fill="{color}">'
            f'{escape(label)}</text>')


def hero(mode):
    t = THEMES[mode]
    h = 176
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" '
        f'aria-label="{escape(NAME)}: {escape(", ".join(PHRASES))}. {escape(", ".join(s for _, s in STATUS))}.">',
        "<style>.in{animation:in .6s ease-out backwards}@keyframes in{from{opacity:0;transform:translateY(8px)}}"
        ".ping{animation:ping 2s ease-out infinite}@keyframes ping{from{transform:scale(.6);opacity:.6}"
        "to{transform:scale(1.8);opacity:0}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>",
        f'<defs><radialGradient id="hero-glow" cx=".1" cy="0" r=".9"><stop offset="0" stop-color="{t["accent"]}" '
        f'stop-opacity=".16"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient></defs>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>',
        f'<rect width="{W}" height="{h}" rx="16" fill="url(#hero-glow)"/>',
        f'<g class="in"><text x="{PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="12" letter-spacing=".14em" '
        f'fill="{t["accent"]}"><tspan font-size="9">●</tspan> WHOAMI</text>'
        f'<text x="{PAD}" y="{PAD + 62}" font-family="{SANS}" font-size="34" font-weight="700" '
        f'letter-spacing="-.02em" fill="{t["title"]}">Hi, I\'m {escape(NAME)}</text></g>',
        f'<text x="{PAD}" y="{PAD + 112}" font-family="{MONO}" font-size="20" fill="{t["muted"]}">$</text>',
        typing(PAD + 22, PAD + 112, t),
    ]
    for i, (kind, label) in enumerate(STATUS):
        p.append(f'<g class="in" style="animation-delay:{.2 + i * .1:.1f}s">'
                 f'{chip(W - PAD, PAD + 4 + i * 46, kind, label, t)}</g>')
    p.append("</svg>")
    return "".join(p)


def code_lines(t):
    """Baris kode About Me sebagai list tspan berwarna."""
    def s(v):
        return f'<tspan fill="{t["str"]}">"{escape(v)}"</tspan>'
    pun = lambda c: f'<tspan fill="{t["punct"]}">{escape(c)}</tspan>'
    keyw = max(len(k) for k, _ in ABOUT) + 1
    lines = [f'<tspan fill="{t["kw"]}">const</tspan> <tspan fill="{t["var"]}">{ABOUT_VAR}</tspan> '
             f'{pun("=")} {pun("{")}']
    for key, val in ABOUT:
        pad = " " * (keyw - len(key))
        if isinstance(val, list):
            body = pun("[") + pun(", ").join(s(v) for v in val) + pun("]")
        else:
            body = s(val)
        lines.append(f'  <tspan fill="{t["prop"]}">{key}</tspan>{pun(":")}{pad}{body}{pun(",")}')
    lines.append(pun("};"))
    return lines


def about(mode):
    t = THEMES[mode]
    lines = code_lines(t)
    lh, top = 26, 84
    h = top + (len(lines) - 1) * lh + 36
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" '
        f'aria-label="About me: ' + escape("; ".join(f"{k}: {v if isinstance(v, str) else ', '.join(v)}"
                                                for k, v in ABOUT)) + '">',
        "<style>.ln{animation:ln .45s ease-out backwards}@keyframes ln{from{opacity:0;transform:translateX(-6px)}}"
        ".caret{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>",
        f'<defs><clipPath id="ab-card"><rect width="{W}" height="{h}" rx="16"/></clipPath></defs>',
        f'<g clip-path="url(#ab-card)"><rect width="{W}" height="{h}" fill="{t["card"]}"/>'
        f'<rect width="{W}" height="44" fill="{t["bar"]}"/>'
        f'<line x1="0" y1="44" x2="{W}" y2="44" stroke="{t["line"]}"/></g>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="16" fill="none" stroke="{t["border"]}"/>',
        # titik jendela + tab file
        f'<circle cx="24" cy="22" r="6" fill="#ff5f57"/><circle cx="44" cy="22" r="6" fill="#febc2e"/>'
        f'<circle cx="64" cy="22" r="6" fill="#28c840"/>',
        f'<path d="M92,44 v-28 a6,6 0 0 1 6,-6 h124 a6,6 0 0 1 6,6 v28 z" fill="{t["card"]}" stroke="{t["line"]}"/>'
        f'<rect x="92" y="42" width="136" height="4" fill="{t["card"]}"/>'
        f'<rect x="92" y="10" width="136" height="2" rx="1" fill="{t["accent"]}"/>'
        f'<rect x="106" y="20" width="16" height="16" rx="3" fill="#3178c6"/>'
        f'<text x="114" y="32" font-family="{SANS}" font-size="8.5" font-weight="700" fill="#fff" '
        f'text-anchor="middle">TS</text>'
        f'<text x="130" y="32" font-family="{MONO}" font-size="12.5" fill="{t["title"]}">about.ts</text>',
        f'<text x="{W - 24}" y="27" font-family="{MONO}" font-size="11" fill="{t["muted"]}" text-anchor="end">'
        f'TypeScript · UTF-8 · LF</text>',
    ]
    for i, line in enumerate(lines):
        y = top + i * lh
        p.append(f'<g class="ln" style="animation-delay:{0.1 + i * 0.09:.2f}s">'
                 f'<text x="46" y="{y}" font-family="{MONO}" font-size="13" fill="{t["gutter"]}" '
                 f'text-anchor="end">{i + 1}</text>'
                 f'<text x="66" y="{y}" font-family="{MONO}" font-size="14.5" xml:space="preserve">{line}</text></g>')
    cy = top + (len(lines) - 1) * lh
    p.append(f'<rect class="caret" x="86" y="{cy - 14}" width="8" height="18" fill="{t["accent"]}" opacity=".8"/>')
    p.append("</svg>")
    return "".join(p)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "img/about"
    os.makedirs(out, exist_ok=True)
    for mode in THEMES:
        with open(os.path.join(out, f"hero-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(hero(mode))
        with open(os.path.join(out, f"about-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(about(mode))


if __name__ == "__main__":
    main()
