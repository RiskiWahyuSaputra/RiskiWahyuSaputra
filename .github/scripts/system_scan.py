"""Buat SVG kartu "system scan" bergaya terminal (pengganti gitskins).

Pemakaian: python3 system_scan.py <folder-output>
Menghasilkan system-scan-{dark,light}.svg.
"""
import io
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from html import escape

from PIL import Image, ImageOps

USER = "RiskiWahyuSaputra"
ROLE = "IT Developer"
STATUS = "Building | Learning | Shipping"
LANGS = "JavaScript, TypeScript, PHP, Blade"

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
W, H = 860, 400
RAMP = " .:-=+*cs#%@"  # dari terang ke gelap
ASCII_COLS, ASCII_ROWS = 46, 30

THEMES = {
    "dark": dict(bg="#0d1117", panel="#010409", border="#1f6feb55", line="#30363d",
                 accent="#58a6ff", label="#79c0ff", value="#c9d1d9", muted="#6e7681",
                 art="#58a6ff", live="#3fb950"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", border="#0969da55", line="#d0d7de",
                  accent="#0969da", label="#0550ae", value="#1f2328", muted="#6e7781",
                  art="#0969da", live="#1a7f37"),
}


def request(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "system-scan"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def get(url):
    return json.loads(request(url))


def stats():
    user = get(f"https://api.github.com/users/{USER}")
    stars, page = 0, 1
    while True:
        repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}")
        stars += sum(r["stargazers_count"] for r in repos if not r["fork"])
        if len(repos) < 100:
            break
        page += 1

    contrib = active = None
    if os.environ.get("GITHUB_TOKEN"):
        q = ('query($u:String!){user(login:$u){contributionsCollection{contributionCalendar'
             '{totalContributions weeks{contributionDays{contributionCount}}}}}}')
        try:
            body = json.dumps({"query": q, "variables": {"u": USER}}).encode()
            cal = json.loads(request("https://api.github.com/graphql", body))
            cal = cal["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            contrib = cal["totalContributions"]
            active = sum(1 for w in cal["weeks"] for d in w["contributionDays"]
                         if d["contributionCount"] > 0)
        except Exception as e:  # kartu tetap dibuat tanpa data kontribusi
            print("graphql gagal:", e, file=sys.stderr)

    joined = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    rows = [
        ("Subject", user.get("name") or USER),
        ("Handle", f"@{USER.lower()}"),
        ("Role", ROLE),
        ("Status", STATUS),
        ("Languages", LANGS),
        ("Repositories", str(user["public_repos"])),
        ("Stars", str(stars)),
        ("Followers", str(user["followers"])),
    ]
    if contrib is not None:
        rows += [("Contributions", f"{contrib:,} (1y)"), ("Active Days", f"{active} (1y)")]
    rows += [("Joined", joined.strftime("%b %Y")), ("Contact", f"github.com/{USER.lower()}")]
    return user["avatar_url"], rows


def ascii_art(avatar_url):
    img = Image.open(io.BytesIO(request(avatar_url + "&s=200"))).convert("L")
    img = ImageOps.autocontrast(img)
    img = img.resize((ASCII_COLS, ASCII_ROWS))
    px = img.load()
    lines = []
    for y in range(ASCII_ROWS):
        row = ""
        for x in range(ASCII_COLS):
            # lingkaran seperti foto profil; latar putih dibuang
            dx = (x + 0.5) / ASCII_COLS - 0.5
            dy = (y + 0.5) / ASCII_ROWS - 0.5
            v = px[x, y]
            if dx * dx + dy * dy > 0.25 or v > 232:
                row += " "
            else:
                row += RAMP[max(1, (255 - v) * (len(RAMP) - 1) // 255)]
        lines.append(row)
    return lines


def render(mode, art, rows):
    t = THEMES[mode]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'role="img" aria-label="{escape(USER)} system scan" font-family="{MONO}">',
         '<style>.c{animation:b 1.1s steps(1) infinite}@keyframes b{50%{opacity:0}}'
         '.r{animation:f .4s ease-out backwards}@keyframes f{from{opacity:0}}'
         '.s{animation:sc 4s linear infinite}@keyframes sc{from{transform:translateY(0)}'
         'to{transform:translateY(330px)}}'
         '@media (prefers-reduced-motion:reduce){.c,.s{animation:none}.r{animation:none}}</style>',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>']
    # bar judul
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        o.append(f'<circle cx="{20 + i * 16}" cy="20" r="5" fill="{c}"/>')
    o.append(f'<text x="{W/2}" y="24" text-anchor="middle" font-size="11" fill="{t["muted"]}">'
             f'{USER.lower()}@github ~ $ ./profile-scan --live</text>')
    o.append(f'<circle cx="{W-58}" cy="20" r="3.5" fill="{t["live"]}" class="c"/>'
             f'<text x="{W-48}" y="24" font-size="10" font-weight="700" fill="{t["live"]}">LIVE</text>')
    o.append(f'<line x1="1" y1="38" x2="{W-1}" y2="38" stroke="{t["line"]}"/>')

    # panel kiri: ascii avatar
    lx, ly, lw, lh = 16, 52, 330, 332
    o.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="8" fill="{t["panel"]}" stroke="{t["line"]}"/>')
    o.append(f'<text x="{lx+12}" y="{ly+18}" font-size="9" font-weight="700" letter-spacing="1.5" '
             f'fill="{t["accent"]}">VISUAL.MAP</text>')
    o.append(f'<clipPath id="cl"><rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="8"/></clipPath>')
    o.append(f'<g font-size="9.6" fill="{t["art"]}" xml:space="preserve">')
    for i, line in enumerate(art):
        o.append(f'<text x="{lx+24}" y="{ly+40+i*9.6:.1f}" textLength="282" lengthAdjust="spacing">'
                 f'{escape(line)}</text>')
    o.append('</g>')
    o.append(f'<g clip-path="url(#cl)"><rect class="s" x="{lx}" y="{ly}" width="{lw}" height="2" '
             f'fill="{t["accent"]}" opacity=".5"/></g>')

    # panel kanan: info
    rx, rw = 360, W - 376
    o.append(f'<rect x="{rx}" y="{ly}" width="{rw}" height="{lh}" rx="8" fill="{t["panel"]}" stroke="{t["line"]}"/>')
    o.append(f'<text x="{rx+12}" y="{ly+18}" font-size="9" font-weight="700" letter-spacing="1.5" '
             f'fill="{t["accent"]}">SYSTEM.INFO</text>')
    gap = min(26, (lh - 44) / len(rows))
    for i, (k, v) in enumerate(rows):
        y = ly + 44 + i * gap
        o.append(f'<g class="r" style="animation-delay:{i*0.12:.2f}s">'
                 f'<text x="{rx+16}" y="{y:.1f}" font-size="12" font-weight="700" fill="{t["label"]}">{escape(k)}</text>'
                 f'<line x1="{rx+120}" y1="{y-4:.1f}" x2="{rx+178}" y2="{y-4:.1f}" stroke="{t["line"]}" '
                 f'stroke-dasharray="2 3"/>'
                 f'<text x="{rx+188}" y="{y:.1f}" font-size="12" fill="{t["value"]}">{escape(v)}</text></g>')
    y = ly + 44 + len(rows) * gap
    if y < ly + lh - 8:
        o.append(f'<text x="{rx+16}" y="{y:.1f}" font-size="12" fill="{t["accent"]}">$ '
                 f'<tspan class="c">█</tspan></text>')
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    o.append(f'<text x="{W-24}" y="{ly+18}" text-anchor="end" font-size="9" fill="{t["muted"]}">'
             f'updated {stamp}</text>')
    o.append('</svg>')
    return "\n".join(o)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    avatar, rows = stats()
    art = ascii_art(avatar)
    for mode in THEMES:
        with open(os.path.join(out, f"system-scan-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(render(mode, art, rows))


if __name__ == "__main__":
    main()
