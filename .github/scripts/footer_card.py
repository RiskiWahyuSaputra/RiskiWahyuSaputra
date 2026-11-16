"""Kartu penutup README: GIF dalam bingkai + salam penutup.

Statis: GIF diubah ke WebP animasi (jauh lebih kecil) lalu disematkan ke SVG.
Pemakaian: python3 .github/scripts/footer_card.py img/about
Menghasilkan footer-{dark,light}.svg dari img/king-king-baldwin.gif.
"""
import base64
import io
import os
import sys
from html import escape

from PIL import Image, ImageSequence

GIF = "img/king-king-baldwin.gif"
LABEL = "SIGNING OFF"
HEADLINE = "Thanks for stopping by."
LINES = ["If something here sparks an idea,", "let's build it together."]
MOTTO = "Ship it, then make it better"
HANDLE = "@RiskiWahyuSaputra"

THEMES = {
    "dark": dict(card="#0d1117", border="#1f6feb55", title="#f0f6fc", muted="#9198a1", accent="#58a6ff",
                 frame="#30363d", chip="#161b22", star="#e3b341"),
    "light": dict(card="#ffffff", border="#0969da55", title="#1f2328", muted="#59636e", accent="#0969da",
                  frame="#d1d9e0", chip="#f6f8fa", star="#9a6700"),
}
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif"
W, H = 920, 300
PAD = 32
SIZE = 236  # ukuran GIF di kartu


def webp_b64(path):
    src = Image.open(path)
    frames, durs = [], []
    for f in ImageSequence.Iterator(src):
        frames.append(f.convert("RGB").copy())
        durs.append(f.info.get("duration", 60))
    buf = io.BytesIO()
    frames[0].save(buf, "WEBP", save_all=True, append_images=frames[1:], duration=durs, loop=0,
                   quality=75, method=6)
    return base64.b64encode(buf.getvalue()).decode()


def star(x, y, r, color):
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * .45
        pts.append(f"{x + rr * math.cos(a):.1f},{y + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}"/>'


def card(img, mode):
    t = THEMES[mode]
    gx, gy = PAD, (H - SIZE) / 2
    tx = gx + SIZE + 44
    lines = "".join(f'<tspan x="{tx}" dy="{0 if i == 0 else 22}">{escape(s)}</tspan>' for i, s in enumerate(LINES))
    chip_w = 34 + len(HANDLE) * 7.3 + 52
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{escape(HEADLINE)} {escape(" ".join(LINES))} From {escape(HANDLE)}">'
        "<style>.in{animation:in .7s ease-out backwards}@keyframes in{from{opacity:0;transform:translateY(8px)}}"
        ".tw{animation:tw 2.4s ease-in-out infinite}@keyframes tw{50%{transform:scale(.8) rotate(18deg)}}"
        ".wave{animation:wave 3s ease-in-out infinite}@keyframes wave{50%{opacity:.35}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>"
        "<defs>"
        f'<clipPath id="ft-gif"><rect x="{gx}" y="{gy}" width="{SIZE}" height="{SIZE}" rx="14"/></clipPath>'
        f'<radialGradient id="ft-glow" cx=".18" cy=".5" r=".45"><stop offset="0" stop-color="{t["accent"]}" '
        f'stop-opacity=".2"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>'
        "</defs>"
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>'
        f'<rect width="{W}" height="{H}" rx="16" fill="url(#ft-glow)"/>'
        # GIF dalam bingkai
        f'<rect x="{gx - 6}" y="{gy - 6}" width="{SIZE + 12}" height="{SIZE + 12}" rx="18" fill="none" '
        f'stroke="{t["accent"]}" stroke-opacity=".35" class="wave"/>'
        f'<image href="data:image/webp;base64,{img}" x="{gx}" y="{gy}" width="{SIZE}" height="{SIZE}" '
        f'clip-path="url(#ft-gif)" preserveAspectRatio="xMidYMid slice"/>'
        f'<rect x="{gx + .5}" y="{gy + .5}" width="{SIZE - 1}" height="{SIZE - 1}" rx="14" fill="none" '
        f'stroke="{t["frame"]}"/>'
        # teks
        f'<g class="in" style="animation-delay:.1s">'
        f'<text x="{tx}" y="78" font-family="{MONO}" font-size="12" letter-spacing=".14em" fill="{t["accent"]}">'
        f'<tspan font-size="9">●</tspan> {LABEL}</text>'
        f'<text x="{tx}" y="120" font-family="{SANS}" font-size="32" font-weight="700" letter-spacing="-.02em" '
        f'fill="{t["title"]}">{escape(HEADLINE)}</text>'
        f'<text x="{tx}" y="152" font-family="{SANS}" font-size="16" fill="{t["muted"]}">{lines}</text></g>'
        f'<g class="in" style="animation-delay:.25s">'
        f'<text x="{tx}" y="210" font-family="{MONO}" font-size="13" fill="{t["muted"]}">'
        f'<tspan fill="{t["accent"]}">//</tspan> {escape(MOTTO)}</text>'
        f'<rect x="{tx + .5}" y="226.5" width="{chip_w:.1f}" height="35" rx="17.5" fill="{t["chip"]}" '
        f'stroke="{t["frame"]}"/>'
        f'<g class="tw" style="transform-origin:{tx + 20}px 244px">{star(tx + 20, 244, 8, t["star"])}</g>'
        f'<text x="{tx + 36}" y="248.5" font-family="{MONO}" font-size="12.5" fill="{t["title"]}">From '
        f'<tspan fill="{t["accent"]}">{escape(HANDLE)}</tspan></text></g>'
        "</svg>"
    )


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "img/about"
    os.makedirs(out, exist_ok=True)
    img = webp_b64(GIF)
    for mode in THEMES:
        with open(os.path.join(out, f"footer-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(card(img, mode))


if __name__ == "__main__":
    main()
