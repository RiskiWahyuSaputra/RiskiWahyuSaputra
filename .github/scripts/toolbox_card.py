"""Kartu "Toolbox": ikon tech stack per kategori (pengganti tabel skillicons).

Statis: ikon diambil sekali dari skillicons.dev (MIT) lalu disematkan ke SVG.
Pemakaian: python3 .github/scripts/toolbox_card.py img/about
Menghasilkan toolbox-{dark,light}.svg.
"""
import base64
import os
import sys
import urllib.request
from html import escape

GROUPS = [
    ("FRONTEND", [("html", "HTML"), ("css", "CSS"), ("js", "JavaScript"), ("ts", "TypeScript"),
                  ("react", "React"), ("nextjs", "Next.js"), ("tailwind", "Tailwind")]),
    ("BACKEND & DATABASE", [("php", "PHP"), ("laravel", "Laravel"), ("codeigniter", "CodeIgniter"),
                            ("mysql", "MySQL")]),
    ("TOOLS & ENVIRONMENT", [("git", "Git"), ("github", "GitHub"), ("vscode", "VS Code"),
                             ("linux", "Linux"), ("ubuntu", "Ubuntu")]),
]
NO_ICON = {"codeigniter"}  # tidak tersedia di skillicons, digambar sendiri

THEMES = {
    "dark": dict(card="#0d1117", border="#1f6feb55", panel="#161b22", line="#30363d", title="#f0f6fc",
                 muted="#9198a1", accent="#58a6ff", name="#d1d7e0", ci_bg="#242938"),
    "light": dict(card="#ffffff", border="#0969da55", panel="#f6f8fa", line="#d1d9e0", title="#1f2328",
                  muted="#59636e", accent="#0969da", name="#1f2328", ci_bg="#f4f2ed"),
}
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif"
W, PAD, GAP = 920, 28, 14
ICON, CELL_W, CELL_H, COLS = 48, 64, 82, 4


def fetch(key, mode):
    url = f"https://skillicons.dev/icons?i={key}&theme={mode}"
    req = urllib.request.Request(url, headers={"User-Agent": "toolbox-card"})
    with urllib.request.urlopen(req, timeout=30) as r:
        svg = r.read()
    if b"undefined" in svg:
        raise SystemExit(f"ikon {key} tidak ada di skillicons, tambahkan ke NO_ICON")
    return base64.b64encode(svg).decode()


def codeigniter(x, y, t):
    """Ikon pengganti CodeIgniter: kotak bulat + api oranye."""
    s = ICON / 48
    return (f'<rect x="{x}" y="{y}" width="{ICON}" height="{ICON}" rx="{12 * s}" fill="{t["ci_bg"]}"/>'
            f'<path transform="translate({x} {y}) scale({s})" fill="#ee4323" d="M22 9c1 6-4 8-6 13-2 4-1 9 2 12'
            f'-1-3 0-6 3-8-1 4 2 6 4 7 2 1 3 4 2 6 4-2 7-6 6-11-1-4-4-6-4-9-2 2-2 4-1 6-3-2-4-7-3-11'
            f'-1 0-2 0-3 1 0-3 0-5 0-6z"/>'
            f'<path transform="translate({x} {y}) scale({s})" fill="#ee4323" opacity=".55" '
            f'd="M14 36c3 3 7 4 10 4s7-1 10-4c-2 4-6 6-10 6s-8-2-10-6z"/>')


def card(icons, mode):
    t = THEMES[mode]
    total = sum(len(items) for _, items in GROUPS)
    pw = (W - 2 * PAD - 2 * GAP) / 3
    rows = max((len(items) + COLS - 1) // COLS for _, items in GROUPS)
    top = 104
    ph = 46 + rows * CELL_H + 8
    h = top + ph + PAD
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h:.0f}" viewBox="0 0 {W} {h:.0f}" '
        f'role="img" aria-label="Toolbox: ' + escape("; ".join(
            f"{g.title()}: {', '.join(n for _, n in items)}" for g, items in GROUPS)) + '">',
        "<style>.pop{animation:pop .5s cubic-bezier(.2,1.4,.4,1) backwards}"
        "@keyframes pop{from{opacity:0;transform:scale(.6)}}"
        ".in{animation:in .6s ease-out backwards}@keyframes in{from{opacity:0;transform:translateY(8px)}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1:.0f}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>',
        f'<text x="{PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="12" letter-spacing=".14em" '
        f'fill="{t["accent"]}"><tspan font-size="9">●</tspan> TOOLBOX</text>',
        f'<text x="{W - PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="11.5" fill="{t["muted"]}" '
        f'text-anchor="end">{total} tools · {len(GROUPS)} categories</text>',
        f'<text x="{PAD}" y="{PAD + 50}" font-family="{SANS}" font-size="26" font-weight="700" '
        f'letter-spacing="-.02em" fill="{t["title"]}">What I work with</text>',
    ]
    n = 0
    for gi, (group, items) in enumerate(GROUPS):
        px = PAD + gi * (pw + GAP)
        p.append(f'<g class="in" style="animation-delay:{gi * .1:.1f}s">'
                 f'<rect x="{px + .5:.1f}" y="{top + .5}" width="{pw - 1:.1f}" height="{ph - 1}" rx="12" '
                 f'fill="{t["panel"]}" stroke="{t["line"]}"/>'
                 f'<text x="{px + 18:.1f}" y="{top + 28}" font-family="{MONO}" font-size="11" letter-spacing=".1em" '
                 f'fill="{t["muted"]}">{escape(group)}</text>'
                 f'<text x="{px + pw - 18:.1f}" y="{top + 28}" font-family="{MONO}" font-size="11" '
                 f'fill="{t["accent"]}" text-anchor="end">{len(items):02d}</text></g>')
        grid_w = COLS * CELL_W
        gx = px + (pw - grid_w) / 2
        for i, (key, name) in enumerate(items):
            col, row = i % COLS, i // COLS
            cx = gx + col * CELL_W + CELL_W / 2
            iy = top + 46 + row * CELL_H
            ix = cx - ICON / 2
            if key in NO_ICON:
                art = codeigniter(ix, iy, t)
            else:
                art = (f'<image href="data:image/svg+xml;base64,{icons[key]}" x="{ix:.1f}" y="{iy}" '
                       f'width="{ICON}" height="{ICON}"/>')
            p.append(f'<g class="pop" style="animation-delay:{.25 + n * .04:.2f}s;transform-origin:{cx:.0f}px '
                     f'{iy + ICON / 2:.0f}px">{art}'
                     f'<text x="{cx:.1f}" y="{iy + ICON + 18}" font-family="{SANS}" font-size="11" '
                     f'fill="{t["name"]}" text-anchor="middle">{escape(name)}</text></g>')
            n += 1
    p.append("</svg>")
    return "".join(p)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "img/about"
    os.makedirs(out, exist_ok=True)
    keys = [k for _, items in GROUPS for k, _ in items if k not in NO_ICON]
    for mode in ("dark", "light"):
        icons = {k: fetch(k, mode) for k in keys}
        with open(os.path.join(out, f"toolbox-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(card(icons, mode))


if __name__ == "__main__":
    main()
