"""Kartu "Now Playing" bergaya pemutar musik, versi gelap dan terang.

Data lagu (judul, artis, sampul) diambil dari kartu spotify-github-profile,
lalu digambar ulang supaya serasi dengan map tech stack.

Pemakaian: python3 now_playing.py <folder-output>
Menghasilkan now-playing-{dark,light}.svg.
"""
import os
import re
import sys
import urllib.request
from html import escape, unescape

SOURCE = ("https://spotify-github-profile.kittinanx.com/api/view?uid=31ashwdrxyilecvdrfqzsq7mr7sm"
          "&cover_image=true&theme=default&show_offline=false&interchange=false"
          "&profanity=false&hide_remaster=false")

THEMES = {
    "dark": dict(card="#0d1117", border="#30363d", veil="#0d1117", veil_op=".82", title="#f0f6fc",
                 muted="#9198a1", accent="#1ed760", track="#30363d", icon="#d1d7e0",
                 vinyl="#161b22", groove="#2d333b"),
    "light": dict(card="#ffffff", border="#d1d9e0", veil="#ffffff", veil_op=".86", title="#1f2328",
                  muted="#59636e", accent="#1a7f37", track="#d1d9e0", icon="#1f2328",
                  vinyl="#1f2328", groove="#3d444d"),
}
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif"
W, H = 840, 280
CV = 216            # ukuran sampul
CX0, CY0 = 32, 32   # pojok kiri atas sampul
VX, VY, VR = 250, 140, 104  # piringan hitam di belakang sampul
TX = 384            # awal kolom teks
TW = W - TX - 40    # lebar kolom teks


def fetch():
    req = urllib.request.Request(SOURCE, headers={"User-Agent": "now-playing-card"})
    with urllib.request.urlopen(req, timeout=60) as r:
        svg = r.read().decode("utf-8")

    def pick(cls):
        m = re.search(rf'class="{cls}"[^>]*>(.*?)</div>', svg, re.S)
        return unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""

    cover = re.search(r'src="data:image/[a-z]+;base64,\s*([A-Za-z0-9+/=\s]+)"[^>]*class="cover"', svg)
    status = pick("playing")
    data = dict(
        title=pick("song"),
        artist=pick("artist"),
        live=status.lower().startswith("now"),
        cover=re.sub(r"\s", "", cover.group(1)) if cover else "",
    )
    if not data["title"]:
        raise SystemExit("judul lagu tidak ditemukan di kartu sumber")
    return data


def clip(text, limit):
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def mime(b64):
    return "image/jpeg" if b64.startswith("/9j/") else "image/png"


def icons(t):
    """Baris kontrol: acak, mundur, pause, maju, ulang."""
    cy = 236
    c = t["icon"]
    mid = TX + TW / 2
    sx, px, nx, rx = mid - 120, mid - 60, mid + 60, mid + 120
    return "".join([
        # acak
        f'<g fill="none" stroke="{t["muted"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M{sx - 10},{cy - 6} h4 l12,12 h4 M{sx - 10},{cy + 6} h4 l3,-3 M{sx + 3},{cy - 3} l3,-3 h4"/>'
        f'<path d="M{sx + 7},{cy - 9} l3,3 -3,3 M{sx + 7},{cy + 3} l3,3 -3,3"/></g>',
        # mundur
        f'<g fill="{c}"><rect x="{px - 10}" y="{cy - 8}" width="3" height="16" rx="1"/>'
        f'<path d="M{px + 9},{cy - 8} v16 l-15,-8 z"/></g>',
        # pause dalam lingkaran
        f'<circle cx="{mid}" cy="{cy}" r="24" fill="{t["accent"]}"/>'
        f'<g fill="{t["card"]}"><rect x="{mid - 7}" y="{cy - 9}" width="5" height="18" rx="1.5"/>'
        f'<rect x="{mid + 2}" y="{cy - 9}" width="5" height="18" rx="1.5"/></g>',
        # maju
        f'<g fill="{c}"><path d="M{nx - 9},{cy - 8} v16 l15,-8 z"/>'
        f'<rect x="{nx + 7}" y="{cy - 8}" width="3" height="16" rx="1"/></g>',
        # ulang
        f'<g fill="none" stroke="{t["muted"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M{rx - 9},{cy + 2} v-4 a4,4 0 0 1 4,-4 h11 M{rx + 3},{cy - 9} l3,3 -3,3"/>'
        f'<path d="M{rx + 9},{cy - 2} v4 a4,4 0 0 1 -4,4 h-11 M{rx - 3},{cy + 9} l-3,-3 3,-3"/></g>',
    ])


def spotify_logo(x, y, r, color):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'
            f'<g fill="none" stroke="#000" stroke-opacity=".85" stroke-linecap="round">'
            f'<path d="M{x - r * .55},{y - r * .25} q{r * .6},{-r * .25} {r * 1.15},{r * .12}" stroke-width="{r * .2:.1f}"/>'
            f'<path d="M{x - r * .48},{y + r * .08} q{r * .5},{-r * .2} {r * .96},{r * .1}" stroke-width="{r * .16:.1f}"/>'
            f'<path d="M{x - r * .4},{y + r * .38} q{r * .4},{-r * .15} {r * .76},{r * .08}" stroke-width="{r * .13:.1f}"/></g>')


def card(d, mode):
    t = THEMES[mode]
    sid = f"np-{mode}"
    img = f'data:{mime(d["cover"])};base64,{d["cover"]}' if d["cover"] else ""
    status = "NOW PLAYING" if d["live"] else "RECENTLY PLAYED"
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{escape(status.title())}: {escape(d["title"])} by {escape(d["artist"])}">',
        "<style>"
        ".spin{animation:spin 6s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}"
        ".eq{animation:eq 1s ease-in-out infinite alternate}"
        "@keyframes eq{0%{transform:scaleY(.25)}100%{transform:scaleY(1)}}"
        ".bar{animation:bar 24s linear infinite}@keyframes bar{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
        ".rise{animation:rise .7s ease-out backwards}"
        "@keyframes rise{from{opacity:0;transform:translateY(8px)}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}.bar{transform:scaleX(.4)}}"
        "</style>",
        "<defs>",
        f'<clipPath id="{sid}-card"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
        f'<clipPath id="{sid}-cover"><rect x="{CX0}" y="{CY0}" width="{CV}" height="{CV}" rx="12"/></clipPath>',
        f'<clipPath id="{sid}-label"><circle cx="{VX}" cy="{VY}" r="30"/></clipPath>',
        f'<filter id="{sid}-blur" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="40"/></filter>',
        f'<filter id="{sid}-shadow" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".35"/></filter>',
        f'<linearGradient id="{sid}-prog" x1="0" x2="1"><stop offset="0" stop-color="{t["accent"]}"/>'
        f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity=".7"/></linearGradient>',
        "</defs>",
        # latar: sampul diburamkan, ditutup lapisan warna tema
        f'<g clip-path="url(#{sid}-card)"><rect width="{W}" height="{H}" fill="{t["card"]}"/>',
    ]
    if img:
        p.append(f'<image href="{img}" x="-40" y="-120" width="{W + 80}" height="{W + 80}" '
                 f'preserveAspectRatio="xMidYMid slice" filter="url(#{sid}-blur)" opacity=".9"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="{t["veil"]}" opacity="{t["veil_op"]}"/></g>')
    p.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{t["border"]}"/>')

    # piringan hitam berputar di belakang sampul
    grooves = "".join(f'<circle cx="{VX}" cy="{VY}" r="{r}" fill="none" stroke="{t["groove"]}" stroke-width=".8"/>'
                      for r in range(40, VR - 4, 9))
    label = (f'<image href="{img}" x="{VX - 30}" y="{VY - 30}" width="60" height="60" '
             f'clip-path="url(#{sid}-label)" preserveAspectRatio="xMidYMid slice"/>' if img
             else f'<circle cx="{VX}" cy="{VY}" r="30" fill="{t["accent"]}"/>')
    p.append(f'<g class="spin" style="transform-origin:{VX}px {VY}px">'
             f'<circle cx="{VX}" cy="{VY}" r="{VR}" fill="{t["vinyl"]}"/>{grooves}'
             f'<path d="M{VX + 30},{VY - 82} A88,88 0 0 1 {VX + 84},{VY - 26}" fill="none" stroke="#fff" '
             f'stroke-opacity=".1" stroke-width="8" stroke-linecap="round"/>'
             f'{label}<circle cx="{VX}" cy="{VY}" r="4" fill="{t["card"]}"/></g>')

    # sampul album
    if img:
        p.append(f'<g filter="url(#{sid}-shadow)"><image href="{img}" x="{CX0}" y="{CY0}" width="{CV}" height="{CV}" '
                 f'clip-path="url(#{sid}-cover)" preserveAspectRatio="xMidYMid slice"/></g>')
    else:
        p.append(f'<rect x="{CX0}" y="{CY0}" width="{CV}" height="{CV}" rx="12" fill="{t["track"]}"/>')
    p.append(f'<rect x="{CX0 + .5}" y="{CY0 + .5}" width="{CV - 1}" height="{CV - 1}" rx="12" fill="none" '
             f'stroke="#fff" stroke-opacity=".12"/>')

    # status + equalizer
    bars = "".join(
        f'<rect x="{TX + i * 5}" y="44" width="3" height="14" rx="1.5" fill="{t["accent"]}" class="eq" '
        f'style="transform-origin:{TX + i * 5 + 1.5}px 58px;animation-delay:{(-0.13 * (i * 3 % 7)):.2f}s;'
        f'animation-duration:{0.6 + i * 0.15:.2f}s"/>' for i in range(4))
    p.append(f'<g class="rise">{bars}<text x="{TX + 28}" y="56" font-family="{MONO}" font-size="12" '
             f'letter-spacing=".14em" fill="{t["accent"]}">{status}</text></g>')
    p.append(spotify_logo(W - 54, 51, 13, t["accent"]))

    # judul dan artis
    p.append(f'<g class="rise" style="animation-delay:.1s">'
             f'<text x="{TX}" y="108" font-family="{SANS}" font-size="30" font-weight="700" letter-spacing="-.02em" '
             f'fill="{t["title"]}">{escape(clip(d["title"], 24))}</text>'
             f'<text x="{TX}" y="140" font-family="{SANS}" font-size="17" fill="{t["muted"]}">'
             f'{escape(clip(d["artist"], 40))}</text></g>')

    # progress bar (dekoratif, berjalan terus)
    p.append(f'<g class="rise" style="animation-delay:.2s">'
             f'<rect x="{TX}" y="176" width="{TW}" height="5" rx="2.5" fill="{t["track"]}"/>'
             f'<rect x="{TX}" y="176" width="{TW}" height="5" rx="2.5" fill="url(#{sid}-prog)" class="bar" '
             f'style="transform-origin:{TX}px 178px"/></g>')
    p.append(f'<g class="rise" style="animation-delay:.3s">{icons(t)}</g>')
    p.append("</svg>")
    return "".join(p)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "dist"
    os.makedirs(out, exist_ok=True)
    data = fetch()
    for mode in THEMES:
        with open(os.path.join(out, f"now-playing-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(card(data, mode))
    print(f'{"now" if data["live"] else "recent"}: {data["title"]} - {data["artist"]}')


if __name__ == "__main__":
    main()
