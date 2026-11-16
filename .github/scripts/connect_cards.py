"""Kartu tautan "Connect with me" (statis, cukup dijalankan ulang kalau isi berubah).

Pemakaian: python3 .github/scripts/connect_cards.py img/connect
Menghasilkan <nama>-{dark,light}.svg untuk tiap tautan, plus portfolio-{dark,light}.svg
dari tangkapan layar img/connect/portfolio-shot.jpg (ganti file itu kalau situs berubah).
Ikon: Font Awesome Free 6 (CC BY 4.0).
"""
import base64
import os
import sys
from html import escape

LINKS = [
    dict(key="instagram", name="Instagram", handle="@arskies_", note="Daily life",
         view="0 0 448 512", fill="url(#ig)",
         path="M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141zm0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7zm146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8zm76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8zM398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.5-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.5 9 132.1s2.7 102.7-9 132.1z"),
    dict(key="linkedin", name="LinkedIn", handle="in/riski-wahyu-saputra", note="Work & career",
         view="0 0 448 512", fill="#0a66c2",
         path="M100.28 448H7.4V148.9h92.88zM53.79 108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 448h-92.68V302.4c0-34.7-.7-79.2-48.29-79.2-48.29 0-55.69 37.7-55.69 76.7V448h-92.78V148.9h89.08v40.8h1.3c12.4-23.5 42.69-48.3 87.88-48.3 94 0 111.28 61.9 111.28 142.3V448z"),
    dict(key="github", name="GitHub", handle="@RiskiWahyuSaputra", note="Code & projects",
         view="0 0 496 512", fill="mono",
         path="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8z"),
]

THEMES = {
    "dark": dict(card="#0d1117", border="#30363d", title="#f0f6fc", muted="#9198a1",
                 chip="#161b22", arrow="#58a6ff", mono_bg="#f0f6fc", mono_fg="#0d1117"),
    "light": dict(card="#ffffff", border="#d1d9e0", title="#1f2328", muted="#59636e",
                  chip="#f6f8fa", arrow="#0969da", mono_bg="#1f2328", mono_fg="#ffffff"),
}
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif"
W, H = 320, 100
ARROW = "M438.6 278.6c12.5-12.5 12.5-32.8 0-45.3l-160-160c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L338.8 224 32 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l306.7 0L233.4 393.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l160-160z"


def card(link, mode):
    t = THEMES[mode]
    mono = link["fill"] == "mono"
    tile = t["mono_bg"] if mono else link["fill"]
    glyph = t["mono_fg"] if mono else "#fff"
    vb_w = int(link["view"].split()[2])
    scale = 26 / 512  # ikon setinggi 26px
    ix = 22 + (56 - vb_w * scale) / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{escape(link["name"])} {escape(link["handle"])}">'
        "<style>.go{animation:go 2.4s ease-in-out infinite}@keyframes go{50%{transform:translateX(3px)}}"
        ".in{animation:in .5s ease-out backwards}@keyframes in{from{opacity:0;transform:translateY(6px)}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>"
        '<defs><linearGradient id="ig" x1="0" y1="1" x2="1" y2="0">'
        '<stop offset="0" stop-color="#feda75"/><stop offset=".3" stop-color="#fa7e1e"/>'
        '<stop offset=".6" stop-color="#d62976"/><stop offset="1" stop-color="#4f5bd5"/></linearGradient></defs>'
        f'<g class="in"><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t["card"]}" '
        f'stroke="{t["border"]}"/>'
        f'<rect x="22" y="22" width="56" height="56" rx="14" fill="{tile}"/>'
        f'<path transform="translate({ix:.1f} 37) scale({scale:.4f})" fill="{glyph}" d="{link["path"]}"/>'
        f'<text x="94" y="42" font-family="{SANS}" font-size="17" font-weight="700" fill="{t["title"]}">'
        f'{escape(link["name"])}</text>'
        f'<text x="94" y="62" font-family="{MONO}" font-size="11.5" fill="{t["muted"]}">{escape(link["handle"])}</text>'
        f'<text x="94" y="80" font-family="{SANS}" font-size="11.5" fill="{t["muted"]}" opacity=".8">'
        f'{escape(link["note"])}</text>'
        f'<circle cx="{W - 32}" cy="{H / 2}" r="14" fill="{t["chip"]}" stroke="{t["border"]}"/>'
        f'<g class="go"><path transform="translate({W - 38.5} {H / 2 - 6.5}) scale(.029)" fill="{t["arrow"]}" '
        f'd="{ARROW}"/></g></g></svg>'
    )


PORTFOLIO = dict(
    url="portofolio-sigma-three-87.vercel.app",
    headline="Selected work & projects",
    lines=["A closer look at what I design,", "build and ship for the web."],
    shot="portfolio-shot.jpg",  # tangkapan layar situs, disimpan di folder output
)
BLUE = {"dark": ("#1f6feb", "#58a6ff", "#1f6feb55"), "light": ("#0969da", "#0969da", "#0969da55")}


def portfolio(shot_b64, mode):
    t = THEMES[mode]
    btn, accent, glow = BLUE[mode]
    pw, ph = 960, 280
    bx, by, bw = 470, 30, 458            # jendela browser
    bar = 30
    bh = ph - 2 * by
    lines = "".join(f'<tspan x="36" dy="{0 if i == 0 else 21}">{escape(s)}</tspan>'
                    for i, s in enumerate(PORTFOLIO["lines"]))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{pw}" height="{ph}" viewBox="0 0 {pw} {ph}" role="img" '
        f'aria-label="Portfolio: {escape(PORTFOLIO["url"])}">'
        "<style>.in{animation:in .6s ease-out backwards}@keyframes in{from{opacity:0;transform:translateY(8px)}}"
        ".go{animation:go 2.4s ease-in-out infinite}@keyframes go{50%{transform:translateX(3px)}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>"
        "<defs>"
        f'<clipPath id="pf-shot"><path d="M{bx},{by + bar} h{bw} v{bh - bar - 12} a12,12 0 0 1 -12,12 '
        f'h{-(bw - 24)} a12,12 0 0 1 -12,-12 z"/></clipPath>'
        f'<radialGradient id="pf-glow" cx=".72" cy=".5" r=".5"><stop offset="0" stop-color="{accent}" '
        f'stop-opacity=".18"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>'
        f'<filter id="pf-shadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="12" '
        f'stdDeviation="14" flood-color="#000" flood-opacity=".3"/></filter>'
        "</defs>"
        f'<rect x=".5" y=".5" width="{pw - 1}" height="{ph - 1}" rx="16" fill="{t["card"]}" stroke="{glow}"/>'
        f'<rect width="{pw}" height="{ph}" rx="16" fill="url(#pf-glow)"/>'
        # teks kiri
        f'<g class="in"><text x="36" y="58" font-family="{MONO}" font-size="12" letter-spacing=".14em" '
        f'fill="{accent}"><tspan font-size="9">●</tspan> PORTFOLIO</text>'
        f'<text x="36" y="96" font-family="{SANS}" font-size="28" font-weight="700" letter-spacing="-.02em" '
        f'fill="{t["title"]}">{escape(PORTFOLIO["headline"])}</text>'
        f'<text x="36" y="126" font-family="{SANS}" font-size="15" fill="{t["muted"]}">{lines}</text>'
        f'<text x="36" y="182" font-family="{MONO}" font-size="12" fill="{t["muted"]}">↗ {escape(PORTFOLIO["url"])}</text>'
        f'<rect x="36" y="200" width="170" height="44" rx="22" fill="{btn}"/>'
        f'<text x="60" y="227" font-family="{SANS}" font-size="15" font-weight="600" fill="#fff">Visit portfolio</text>'
        f'<g class="go"><path transform="translate(176 215.5) scale(.029)" fill="#fff" d="{ARROW}"/></g></g>'
        # jendela browser berisi tangkapan layar
        f'<g class="in" style="animation-delay:.15s"><g filter="url(#pf-shadow)">'
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" fill="{t["chip"]}" stroke="{t["border"]}"/></g>'
        f'<circle cx="{bx + 18}" cy="{by + bar / 2}" r="5" fill="#ff5f57"/>'
        f'<circle cx="{bx + 34}" cy="{by + bar / 2}" r="5" fill="#febc2e"/>'
        f'<circle cx="{bx + 50}" cy="{by + bar / 2}" r="5" fill="#28c840"/>'
        f'<rect x="{bx + 120}" y="{by + 7}" width="{bw - 240}" height="16" rx="8" fill="{t["card"]}" '
        f'stroke="{t["border"]}"/>'
        f'<text x="{bx + bw / 2}" y="{by + 19}" font-family="{MONO}" font-size="9.5" fill="{t["muted"]}" '
        f'text-anchor="middle">{escape(PORTFOLIO["url"])}</text>'
        f'<image href="data:image/jpeg;base64,{shot_b64}" x="{bx}" y="{by + bar}" width="{bw}" height="{bh - bar}" '
        f'clip-path="url(#pf-shot)" preserveAspectRatio="xMidYMin slice"/></g>'
        "</svg>"
    )


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "img/connect"
    os.makedirs(out, exist_ok=True)
    for link in LINKS:
        for mode in THEMES:
            with open(os.path.join(out, f'{link["key"]}-{mode}.svg'), "w", encoding="utf-8") as f:
                f.write(card(link, mode))
    shot = os.path.join(out, PORTFOLIO["shot"])
    if os.path.exists(shot):
        with open(shot, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        for mode in THEMES:
            with open(os.path.join(out, f"portfolio-{mode}.svg"), "w", encoding="utf-8") as f:
                f.write(portfolio(b64, mode))


if __name__ == "__main__":
    main()
