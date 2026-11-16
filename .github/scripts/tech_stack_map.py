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
    "dark": dict(accent="#3fb950", title="#f0f6fc", muted="#9198a1", bg="#0d1117",
                 card="#0d1117", border="#30363d", dot="#30363d", orbit="#30363d",
                 pill="#161b22", legend="#d1d7e0", other="#6e7681"),
    "light": dict(accent="#1a7f37", title="#1f2328", muted="#59636e", bg="#ffffff",
                  card="#ffffff", border="#d1d9e0", dot="#d1d9e0", orbit="#d1d9e0",
                  pill="#f6f8fa", legend="#1f2328", other="#8c959f"),
}
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif"
W, H = 920, 660
CX, CY = 460, 400
PAD = 28
ORBITS = [(340, 205), (220, 128)]  # (rx, ry) orbit luar dan dalam
RING_MIN = 0.04  # bahasa < 4% digabung jadi "lainnya" di cincin node


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
        rx, ry = ORBITS[i % 2]
        r["x"], r["y"] = CX + rx * math.cos(a), CY + ry * math.sin(a)
        r["up"] = math.sin(a) < -0.2  # node di bagian atas: label di atas node
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


def ring(r, mode, t):
    """Cincin komposisi bahasa di sekeliling node (donut dari share bahasa)."""
    parts = sorted(r["share"].items(), key=lambda kv: -kv[1])
    major = [(k, v) for k, v in parts if v >= RING_MIN]
    rest = 1 - sum(v for _, v in major)
    segs = [(color(k, mode), v) for k, v in major] + ([(t["other"], rest)] if rest > 0.005 else [])
    rad = r["r"] + 5
    gap = 2.5 if len(segs) > 1 else 0
    out, start = [], 0.0
    for c, v in segs:
        length = max(v * 100 - gap, 0.6)
        out.append(f'<circle cx="{r["x"]:.1f}" cy="{r["y"]:.1f}" r="{rad:.1f}" fill="none" stroke="{c}" '
                   f'stroke-width="3" stroke-linecap="round" pathLength="100" '
                   f'stroke-dasharray="{length:.2f} {100 - length:.2f}" '
                   f'transform="rotate({start * 3.6 - 90:.1f} {r["x"]:.1f} {r["y"]:.1f})"/>')
        start += v * 100
    return "".join(out)


def label(r, t):
    """Label nama + bahasa utama dalam pill, diletakkan menjauhi pusat map."""
    name = r["name"]
    sub = f'{r["primary"]} {round(r["share"].get(r["primary"], 0) * 100)}%'
    w = max(len(name) * 7.4, len(sub) * 6.4) + 22
    h = 38
    off = r["r"] + 13
    top = r["y"] - off - h if r["up"] else r["y"] + off
    x = r["x"]
    return (f'<rect x="{x - w / 2:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h}" rx="9" '
            f'fill="{t["pill"]}" fill-opacity=".92" stroke="{t["border"]}"/>'
            f'<text x="{x:.1f}" y="{top + 16:.1f}" font-family="{SANS}" font-size="12.5" font-weight="600" '
            f'fill="{t["title"]}" text-anchor="middle">{escape(name)}</text>'
            f'<text x="{x:.1f}" y="{top + 30:.1f}" font-family="{MONO}" font-size="10.5" '
            f'fill="{t["muted"]}" text-anchor="middle">{escape(sub)}</text>')


def map_svg(repos, links, avatar, mode):
    t = THEMES[mode]
    sid = f"ts-{mode}"
    langs = {k for r in repos for k in r["share"]}
    stats = f"{len(repos)} projects · {len(langs)} languages · {len(links)} links"
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Tech stack map of {len(repos)} projects by Riski Wahyu Saputra">',
        "<style>.draw{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.2s ease-out forwards}"
        "@keyframes draw{to{stroke-dashoffset:0}}"
        ".pop{transform:scale(0);animation:pop .6s cubic-bezier(.2,1.4,.4,1) forwards}"
        "@keyframes pop{to{transform:scale(1)}}"
        ".fade{opacity:0;animation:fade .6s ease-out forwards}"
        "@keyframes fade{to{opacity:1}}"
        ".pulse{animation:pulse 3s ease-out infinite}"
        "@keyframes pulse{from{transform:scale(.8);opacity:.9}to{transform:scale(1.6);opacity:0}}"
        ".orbit{animation:orbit 40s linear infinite}"
        "@keyframes orbit{to{stroke-dashoffset:-200}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}"
        ".draw{stroke-dashoffset:0}.pop{transform:none}.fade{opacity:1}}</style>",
        "<defs>",
        f'<pattern id="{sid}-dots" width="18" height="18" patternUnits="userSpaceOnUse">'
        f'<circle cx="1.5" cy="1.5" r="1.1" fill="{t["dot"]}"/></pattern>',
        f'<radialGradient id="{sid}-fade" cx="{CX / W:.3f}" cy="{CY / H:.3f}" r=".62">'
        f'<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        f'<mask id="{sid}-mask"><rect width="{W}" height="{H}" fill="url(#{sid}-fade)"/></mask>',
        f'<radialGradient id="{sid}-glow"><stop offset="0" stop-color="{t["accent"]}" stop-opacity=".28"/>'
        f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>',
        f'<clipPath id="{sid}-av"><circle cx="{CX}" cy="{CY}" r="34"/></clipPath>',
        "</defs>",
        # kartu + grid titik yang memudar ke tepi
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="url(#{sid}-dots)" mask="url(#{sid}-mask)"/>',
        f'<text x="{PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="12" letter-spacing=".14em" fill="{t["accent"]}">'
        f'<tspan font-size="9">●</tspan> {TITLE}</text>',
        f'<text x="{W - PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="11.5" fill="{t["muted"]}" '
        f'text-anchor="end">{stats}</text>',
        f'<text x="{PAD}" y="{PAD + 50}" font-family="{SANS}" font-size="26" font-weight="700" letter-spacing="-.02em" '
        f'fill="{t["title"]}">{HEADLINE}</text>',
        f'<text x="{PAD}" y="{PAD + 74}" font-family="{SANS}" font-size="14" fill="{t["muted"]}">{SUBTITLE}</text>',
        f'<circle cx="{CX}" cy="{CY}" r="150" fill="url(#{sid}-glow)"/>',
    ]
    for rx, ry in ORBITS:
        p.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry}" fill="none" stroke="{t["orbit"]}" '
                 f'stroke-dasharray="2 6" class="orbit"/>')
    for i, r in enumerate(repos):
        p.append(f'<line x1="{CX}" y1="{CY}" x2="{r["x"]:.1f}" y2="{r["y"]:.1f}" '
                 f'stroke="{color(r["primary"], mode)}" stroke-opacity=".22" '
                 f'class="draw" pathLength="1" style="animation-delay:{i * 0.04:.2f}s"/>')
    for i, (a, b, lang) in enumerate(links):
        mx, my = (a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2
        qx, qy = mx + (CX - mx) * 0.3, my + (CY - my) * 0.3
        c = color(lang, mode)
        eid = f"{sid}-e{i}"
        p.append(f'<path id="{eid}" d="M{a["x"]:.1f},{a["y"]:.1f} Q{qx:.1f},{qy:.1f} {b["x"]:.1f},{b["y"]:.1f}" '
                 f'fill="none" stroke="{c}" stroke-opacity=".6" stroke-width="1.8" stroke-linecap="round" '
                 f'class="draw" pathLength="1" style="animation-delay:{0.6 + i * 0.05:.2f}s"/>')
        begin = 1.5 + i * 0.4
        # opacity 0 sampai animasi mulai, supaya titik tidak nongol di pojok (0,0)
        p.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{begin:.1f}s"/>'
                 f'<circle r="7" fill="{c}" opacity=".25"/><circle r="3" fill="{c}"/>'
                 f'<animateMotion dur="{3.5 + (i % 4) * 0.9:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite">'
                 f'<mpath href="#{eid}"/></animateMotion></g>')
    for i, r in enumerate(repos):
        c = color(r["primary"], mode)
        x, y, rad = r["x"], r["y"], r["r"]
        p.append(
            f'<g class="pop" style="animation-delay:{0.2 + i * 0.05:.2f}s;transform-origin:{x:.0f}px {y:.0f}px">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad * 2.1:.1f}" fill="{c}" opacity=".12"/>'
            f'{ring(r, mode, t)}'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="{c}" stroke="{t["card"]}" stroke-width="2"/></g>'
        )
    for i, r in enumerate(repos):
        p.append(f'<g class="fade" style="animation-delay:{0.5 + i * 0.05:.2f}s">{label(r, t)}</g>')
    p.append(f'<circle cx="{CX}" cy="{CY}" r="44" fill="none" stroke="{t["accent"]}" stroke-opacity=".5" '
             f'class="pulse" style="transform-origin:{CX}px {CY}px"/>')
    p.append(f'<circle cx="{CX}" cy="{CY}" r="38" fill="{t["card"]}" stroke="{t["accent"]}" stroke-width="2"/>')
    p.append(f'<image href="data:image/jpeg;base64,{avatar}" x="{CX - 34}" y="{CY - 34}" width="68" height="68" '
             f'clip-path="url(#{sid}-av)" preserveAspectRatio="xMidYMid slice"/>')
    p.append(f'<text x="{CX}" y="{CY + 58}" font-family="{MONO}" font-size="11" font-weight="600" '
             f'fill="{t["accent"]}" text-anchor="middle">@{USER}</text>')
    p.append("</svg>")
    return "".join(p)


def legend_svg(repos, mode):
    t = THEMES[mode]
    counts = {}
    for r in repos:
        counts[r["primary"]] = counts.get(r["primary"], 0) + 1
    chips = []
    for lang, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        chips.append((lang, n, 34 + len(lang) * 7.8 + len(str(n)) * 7.8 + 22))
    gap = 10
    total = sum(w for *_, w in chips) + gap * (len(chips) - 1)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="40" viewBox="0 0 {W} 40" '
         f'role="img" aria-label="Languages in the tech stack">']
    x = max((W - total) / 2, 0)
    for lang, n, w in chips:
        c = color(lang, mode)
        p.append(f'<rect x="{x + .5:.1f}" y="4.5" width="{w - 1:.1f}" height="31" rx="15.5" '
                 f'fill="{t["pill"]}" stroke="{t["border"]}"/>'
                 f'<circle cx="{x + 18:.1f}" cy="20" r="5.5" fill="{c}"/>'
                 f'<text x="{x + 30:.1f}" y="24.5" font-family="{MONO}" font-size="13" fill="{t["legend"]}">'
                 f'{escape(lang)} <tspan fill="{t["muted"]}">{n}</tspan></text>')
        x += w + gap
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
