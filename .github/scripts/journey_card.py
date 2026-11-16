"""Kartu "Journey": timeline pendidikan dan pengalaman kerja (mengikuti CV, terbaru di atas).

Statis: jalankan ulang kalau isi berubah.
Pemakaian: python3 .github/scripts/journey_card.py img/about
Menghasilkan journey-{dark,light}.svg.
"""
import os
import sys
import textwrap
from html import escape

# sumber: claw-portfolio/src/data/journey.ts (mengikuti CV)
JOURNEY = [
    dict(period="Aug 2026 – Present", title="IT Developer", org="BEST Corporation Syariah",
         note="PT Bandung Eco Sinergi Teknologi", kind="work", type="Full-time", place="Bandung",
         summary="Build internal web apps, handle helpdesk tickets, and integrate WhatsApp automation, "
                 "E-Sign, QR codes, and PDF/Excel reports.",
         tags=["Laravel", "PHP", "React", "Next.js", "MySQL"], current=True),
    dict(period="Feb 2026 – Jul 2026", title="IT Developer (Apprentice)", org="BEST Corporation Syariah",
         note="PT Bandung Eco Sinergi Teknologi", kind="work", type="Apprenticeship", place="Bandung",
         summary="Built REST API integrations and responsive React + Tailwind interfaces before being "
                 "hired full-time.",
         tags=["REST API", "React.js", "Tailwind CSS"]),
    dict(period="Sep 2023 – Sep 2026", title="D3 Informatics Management", org="Politeknik Negeri Lampung",
         note="Department of Information Technology", kind="education", type="Diploma", place="Bandar Lampung",
         summary="Software and web development fundamentals, including a QRIS-based practicum payment app "
                 "for the department.",
         tags=["Software Engineering", "Web Programming", "Database"]),
    dict(period="Feb 2022 – Jan 2022", title="Junior Web Developer", org="Telenergie Indonesia",
         note="", kind="work", type="Internship (PKL)", place="Bandar Lampung",
         summary="Designed and developed web applications with native PHP and MySQL, and Bootstrap frontends.",
         tags=["PHP Native", "MySQL", "Bootstrap"]),
]

THEMES = {
    "dark": dict(card="#0d1117", border="#1f6feb55", line="#30363d", title="#f0f6fc", text="#d1d7e0",
                 muted="#9198a1", accent="#58a6ff", live="#3fb950", chip="#161b22", edu="#a371f7"),
    "light": dict(card="#ffffff", border="#0969da55", line="#d1d9e0", title="#1f2328", text="#1f2328",
                  muted="#59636e", accent="#0969da", live="#1a7f37", chip="#f6f8fa", edu="#8250df"),
}
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif"
W, PAD = 920, 28
RAIL = 196          # x garis timeline
TX = RAIL + 28      # awal kolom isi
WRAP = 100          # karakter per baris ringkasan (13px)


def tags(x, y, items, t):
    out = []
    for tag in items:
        w = 16 + len(tag) * 6.6
        out.append(f'<rect x="{x + .5:.1f}" y="{y + .5}" width="{w:.1f}" height="21" rx="10.5" fill="{t["chip"]}" '
                   f'stroke="{t["line"]}"/><text x="{x + 8:.1f}" y="{y + 15}" font-family="{MONO}" '
                   f'font-size="11" fill="{t["muted"]}">{escape(tag)}</text>')
        x += w + 6
    return "".join(out)


def entry(e, y, t, i):
    color = t["live"] if e.get("current") else (t["edu"] if e["kind"] == "education" else t["accent"])
    lines = textwrap.wrap(e["summary"], WRAP)
    org = escape(e["org"]) + (f' <tspan fill="{t["muted"]}">· {escape(e["note"])}</tspan>' if e["note"] else "")
    kind_label = "EDUCATION" if e["kind"] == "education" else "WORK"
    node = (f'<circle cx="{RAIL}" cy="{y + 6}" r="12" fill="{color}" opacity=".25" class="ping" '
            f'style="transform-origin:{RAIL}px {y + 6}px"/>' if e.get("current") else "")
    node += (f'<circle cx="{RAIL}" cy="{y + 6}" r="7" fill="{t["card"]}" stroke="{color}" stroke-width="2.5"/>'
             f'<circle cx="{RAIL}" cy="{y + 6}" r="3" fill="{color}"/>')
    body = [
        f'<text x="{RAIL - 26}" y="{y + 11}" font-family="{MONO}" font-size="12" fill="{color}" '
        f'text-anchor="end">{escape(e["period"])}</text>',
        f'<text x="{RAIL - 26}" y="{y + 29}" font-family="{MONO}" font-size="10.5" letter-spacing=".1em" '
        f'fill="{t["muted"]}" text-anchor="end">{kind_label}</text>',
        node,
        f'<text x="{TX}" y="{y + 12}" font-family="{SANS}" font-size="17" font-weight="700" '
        f'fill="{t["title"]}">{escape(e["title"])}</text>',
        f'<text x="{W - PAD}" y="{y + 11}" font-family="{MONO}" font-size="11" fill="{color}" '
        f'text-anchor="end">{escape(e["type"])}{" · now" if e.get("current") else ""}</text>',
        f'<text x="{TX}" y="{y + 33}" font-family="{SANS}" font-size="13.5" fill="{t["text"]}">{org}'
        f'<tspan fill="{t["muted"]}"> · {escape(e["place"])}</tspan></text>',
    ]
    ly = y + 56
    for k, line in enumerate(lines):
        body.append(f'<text x="{TX}" y="{ly + k * 19}" font-family="{SANS}" font-size="13" '
                    f'fill="{t["muted"]}">{escape(line)}</text>')
    ty = ly + (len(lines) - 1) * 19 + 12
    body.append(tags(TX, ty, e["tags"], t))
    height = ty + 22 - y
    return f'<g class="in" style="animation-delay:{.1 + i * .12:.2f}s">{"".join(body)}</g>', height


def card(mode):
    t = THEMES[mode]
    top, gap = 112, 30
    parts, y = [], top
    for i, e in enumerate(JOURNEY):
        svg, h = entry(e, y, t, i)
        parts.append(svg)
        y += h + gap
    bottom = y - gap
    h = bottom + PAD + 6
    work = sum(1 for e in JOURNEY if e["kind"] == "work")
    edu = len(JOURNEY) - work
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h:.0f}" viewBox="0 0 {W} {h:.0f}" '
        f'role="img" aria-label="Journey: ' + escape("; ".join(
            f'{e["period"]} {e["title"]} at {e["org"]}' for e in JOURNEY)) + '">'
        "<style>.in{animation:in .6s ease-out backwards}@keyframes in{from{opacity:0;transform:translateY(8px)}}"
        ".ping{animation:ping 2s ease-out infinite}@keyframes ping{from{transform:scale(.6);opacity:.6}"
        "to{transform:scale(1.8);opacity:0}}"
        ".rail{stroke-dasharray:1;stroke-dashoffset:1;animation:rail 1.4s ease-out forwards}"
        "@keyframes rail{to{stroke-dashoffset:0}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}.rail{stroke-dashoffset:0}}</style>"
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1:.0f}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>'
        f'<text x="{PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="12" letter-spacing=".14em" '
        f'fill="{t["accent"]}"><tspan font-size="9">●</tspan> JOURNEY</text>'
        f'<text x="{W - PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="11.5" fill="{t["muted"]}" '
        f'text-anchor="end">{work} work · {edu} education · newest first</text>'
        f'<text x="{PAD}" y="{PAD + 50}" font-family="{SANS}" font-size="26" font-weight="700" '
        f'letter-spacing="-.02em" fill="{t["title"]}">Where I\'ve been</text>'
        f'<line x1="{RAIL}" y1="{top + 6}" x2="{RAIL}" y2="{bottom - 10:.0f}" stroke="{t["line"]}" stroke-width="2" '
        f'class="rail" pathLength="1"/>'
        + "".join(parts) + "</svg>"
    )


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "img/about"
    os.makedirs(out, exist_ok=True)
    for mode in THEMES:
        with open(os.path.join(out, f"journey-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(card(mode))


if __name__ == "__main__":
    main()
