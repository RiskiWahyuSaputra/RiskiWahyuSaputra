"""Buat SVG map tech stack dari daftar repo pilihan (pengganti map gitskins).

Pemakaian: python3 tech_stack_map.py <folder-output>
Menghasilkan tech-stack-{dark,light}.svg dan tech-stack-legend-{dark,light}.svg.
"""
import base64
import json
import math
import os
import sys
import urllib.request
from html import escape
from itertools import combinations

USER = "RiskiWahyuSaputra"
REPOS = [
    "Qbot",
    "SDN21-TulangBawangUdik",
    "TokoQ-UMKM",
    "smart-resource-optimizer",
    "StockFlow-Commerce",
    "livechat-laravel",
    "warehouse_monitoring",
    "ai-stock-trading-office",
    "qite",
    "FreshScan-AI",
]
TITLE = "TECH STACK"
HEADLINE = "The stack behind everything I build"
SUBTITLE = "Size is code size. Lines join projects that share a language."

# Bahasa "pendukung" tidak dipakai untuk menarik garis antar-project,
# karena hampir semua project web memakainya.
SUPPORT = {"CSS", "HTML", "JavaScript", "Shell", "PowerShell", "NSIS", "Dockerfile"}
MIN_SHARE = 0.25  # garis ditarik bila bahasa itu >= 25% kode di kedua repo

LANG_COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "PHP": "#4F5D95",
    "Blade": "#f7523f", "Python": "#3572A5", "QML": "#44a51c", "Rust": "#dea584",
    "HTML": "#e34c26", "CSS": "#563d7c", "Vue": "#41b883", "Go": "#00ADD8",
    "Dart": "#00B4AB", "Java": "#b07219", "Kotlin": "#A97BFF", "Shell": "#89e051",
}
LIGHT_OVERRIDE = {"#f1e05a": "#9d923b"}  # kuning tidak terbaca di latar terang

THEMES = {
    "dark": dict(accent="#3fb950", title="#f0f6fc", muted="#9198a1",
                 spoke="#262c36", legend="#d1d7e0"),
    "light": dict(accent="#1a7f37", title="#1f2328", muted="#59636e",
                  spoke="#e4e8ec", legend="#1f2328"),
}
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif"
W, H = 880, 620
CX, CY = 440, 355


def get(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": "tech-stack-map"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if raw else json.loads(data)


def color(lang, mode):
    c = LANG_COLORS.get(lang, "#8b949e")
    return LIGHT_OVERRIDE.get(c, c) if mode == "light" else c


def load():
    repos = []
    for name in REPOS:
        info = get(f"https://api.github.com/repos/{USER}/{name}")
        langs = get(f"https://api.github.com/repos/{USER}/{name}/languages")
        total = sum(langs.values()) or 1
        share = {k: v / total for k, v in langs.items()}
        # Bahasa utama: bahasa non-pendukung terbesar, kalau ada
        core = [k for k in sorted(share, key=share.get, reverse=True) if k not in SUPPORT]
        primary = core[0] if core else (info.get("language") or "Other")
        repos.append(dict(name=info["name"], primary=primary, share=share, size=total))
    return repos


def layout(repos):
    order = sorted(repos, key=lambda r: (r["primary"], r["name"].lower()))
    n = len(order)
    for i, r in enumerate(order):
        a = -math.pi / 2 + 2 * math.pi * i / n
        rx, ry = (345, 205) if i % 2 == 0 else (225, 130)
        r["x"], r["y"] = CX + rx * math.cos(a), CY + ry * math.sin(a)
    logs = [math.log(r["size"]) for r in order]
    lo, hi = min(logs), max(logs)
    for r, lg in zip(order, logs):
        r["r"] = 7 + 7 * ((lg - lo) / (hi - lo) if hi > lo else 0.5)
    return order


def edges(repos):
    out = []
    for a, b in combinations(repos, 2):
        shared = [
            (min(a["share"][k], b["share"][k]), k)
            for k in a["share"].keys() & b["share"].keys()
            if k not in SUPPORT and min(a["share"][k], b["share"][k]) >= MIN_SHARE
        ]
        if shared:
            out.append((a, b, max(shared)[1]))
    return out


def map_svg(repos, links, avatar, mode):
    t = THEMES[mode]
    sid = f"ts-{mode}"
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Tech stack map of {len(repos)} projects by Riski Wahyu Saputra">',
        "<style>.draw{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.2s ease-out forwards}"
        "@keyframes draw{to{stroke-dashoffset:0}}"
        ".pop{transform:scale(0);animation:pop .6s cubic-bezier(.2,1.4,.4,1) forwards}"
        "@keyframes pop{to{transform:scale(1)}}"
        ".pulse{animation:pulse 3s ease-out infinite}"
        "@keyframes pulse{from{transform:scale(.8);opacity:.9}to{transform:scale(1.5);opacity:0}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}"
        ".draw{stroke-dashoffset:0}.pop{transform:none}}</style>",
        f'<text x="0" y="26" font-family="{MONO}" font-size="12" letter-spacing=".14em" fill="{t["accent"]}">{TITLE}</text>',
        f'<text x="0" y="56" font-family="{SANS}" font-size="26" font-weight="700" letter-spacing="-.02em" fill="{t["title"]}">{HEADLINE}</text>',
        f'<text x="0" y="80" font-family="{SANS}" font-size="14" fill="{t["muted"]}">{SUBTITLE}</text>',
    ]
    for i, r in enumerate(repos):
        p.append(f'<line x1="{CX}" y1="{CY}" x2="{r["x"]:.1f}" y2="{r["y"]:.1f}" stroke="{t["spoke"]}" '
                 f'class="draw" pathLength="1" style="animation-delay:{i * 0.04:.2f}s"/>')
    for i, (a, b, lang) in enumerate(links):
        mx, my = (a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2
        qx, qy = mx + (CX - mx) * 0.3, my + (CY - my) * 0.3
        c = color(lang, mode)
        eid = f"{sid}-e{i}"
        p.append(f'<path id="{eid}" d="M{a["x"]:.1f},{a["y"]:.1f} Q{qx:.1f},{qy:.1f} {b["x"]:.1f},{b["y"]:.1f}" '
                 f'fill="none" stroke="{c}" stroke-opacity=".55" stroke-width="1.6" class="draw" '
                 f'pathLength="1" style="animation-delay:{0.6 + i * 0.05:.2f}s"/>')
        begin = 1.5 + i * 0.4
        # opacity 0 sampai animasi mulai, supaya titik tidak nongol di pojok (0,0)
        p.append(f'<circle r="3" fill="{c}" opacity="0"><set attributeName="opacity" to="1" begin="{begin:.1f}s"/>'
                 f'<animateMotion dur="{3.5 + (i % 4) * 0.9:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite">'
                 f'<mpath href="#{eid}"/></animateMotion></circle>')
    for i, r in enumerate(repos):
        c = color(r["primary"], mode)
        x, y, rad = r["x"], r["y"], r["r"]
        p.append(
            f'<g class="pop" style="animation-delay:{0.2 + i * 0.05:.2f}s;transform-origin:{x:.0f}px {y:.0f}px">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad * 1.5:.1f}" fill="{c}" opacity=".16"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="{c}"/>'
            f'<text x="{x:.1f}" y="{y + rad * 1.5 + 14:.1f}" font-family="{SANS}" font-size="12.5" font-weight="600" '
            f'fill="{t["title"]}" text-anchor="middle">{escape(r["name"])}</text>'
            f'<text x="{x:.1f}" y="{y + rad * 1.5 + 28:.1f}" font-family="{MONO}" font-size="10.5" '
            f'fill="{t["muted"]}" text-anchor="middle">{escape(r["primary"])}</text></g>'
        )
    p.append(f'<circle cx="{CX}" cy="{CY}" r="44" fill="none" stroke="{t["accent"]}" stroke-opacity=".5" '
             f'class="pulse" style="transform-origin:{CX}px {CY}px"/>')
    p.append(f'<defs><clipPath id="{sid}-av"><circle cx="{CX}" cy="{CY}" r="34"/></clipPath></defs>')
    p.append(f'<circle cx="{CX}" cy="{CY}" r="36" fill="none" stroke="{t["accent"]}" stroke-opacity=".6"/>')
    p.append(f'<image href="data:image/jpeg;base64,{avatar}" x="{CX - 34}" y="{CY - 34}" width="68" height="68" '
             f'clip-path="url(#{sid}-av)" preserveAspectRatio="xMidYMid slice"/>')
    p.append("</svg>")
    return "".join(p)


def legend_svg(repos, mode):
    t = THEMES[mode]
    counts = {}
    for r in repos:
        counts[r["primary"]] = counts.get(r["primary"], 0) + 1
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="34" viewBox="0 0 {W} 34" '
         f'role="img" aria-label="Languages in the tech stack">']
    x = 0
    for lang, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        label = f"{lang} · {n}"
        p.append(f'<circle cx="{x + 6}" cy="16" r="6" fill="{color(lang, mode)}"/>'
                 f'<text x="{x + 18}" y="21" font-family="{MONO}" font-size="13" fill="{t["legend"]}">{escape(label)}</text>')
        x += 18 + len(label) * 8 + 26
    p.append("</svg>")
    return "".join(p)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "dist"
    os.makedirs(out, exist_ok=True)
    repos = layout(load())
    links = edges(repos)
    avatar = base64.b64encode(get(f"https://github.com/{USER}.png?size=136", raw=True)).decode()
    for mode in THEMES:
        with open(os.path.join(out, f"tech-stack-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(map_svg(repos, links, avatar, mode))
        with open(os.path.join(out, f"tech-stack-legend-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(legend_svg(repos, mode))
    for a, b, lang in links:
        print(f"{a['name']} <-> {b['name']} ({lang})")


if __name__ == "__main__":
    main()
