"""Kartu GitHub Stats bernuansa biru (pengganti kartu summary-cards dan streak).

Pemakaian: GITHUB_TOKEN=... python3 github_stats.py <folder-output>
Menghasilkan github-stats-{dark,light}.svg.
"""
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta
from html import escape

USER = "RiskiWahyuSaputra"
TITLE = "GITHUB STATS"
HEADLINE = "What I've been shipping"
WEEKS = 26         # jumlah minggu di heatmap
TOP_LANGS = 6
SKIP_LANGS = {"Dockerfile", "Shell", "PowerShell", "NSIS", "Batchfile", "Makefile", "Procfile"}

THEMES = {
    "dark": dict(card="#0d1117", border="#1f6feb55", tile="#161b22", tile_line="#30363d",
                 accent="#58a6ff", title="#f0f6fc", value="#e6edf3", muted="#9198a1",
                 cells=["#161b22", "#0c2d6b", "#1158c7", "#388bfd", "#79c0ff"]),
    "light": dict(card="#ffffff", border="#0969da55", tile="#f6f8fa", tile_line="#d1d9e0",
                  accent="#0969da", title="#1f2328", value="#1f2328", muted="#59636e",
                  cells=["#eff2f5", "#b6e3ff", "#54aeff", "#0969da", "#0a3069"]),
}
# biru-ungu-toska untuk bar bahasa, cukup kontras di kedua tema
LANG_PALETTE = ["#2f81f7", "#a371f7", "#3fb9b0", "#56d4dd", "#7d8cf5", "#8b949e"]
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif"
W, H = 920, 440
PAD = 28


def gql(query, **variables):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN wajib diisi")
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "User-Agent": "github-stats-card", "Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.loads(r.read())
    if out.get("errors"):
        raise SystemExit(f"graphql gagal: {out['errors']}")
    return out["data"]


def load():
    d = gql("""query($u:String!){user(login:$u){
      createdAt followers{totalCount}
      pullRequests{totalCount} issues{totalCount}
      repositories(ownerAffiliations:OWNER,isFork:false,first:100,privacy:PUBLIC){totalCount nodes{
        stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
      contributionsCollection{totalCommitContributions contributionCalendar{totalContributions
        weeks{contributionDays{date contributionCount}}}}}}""", u=USER)["user"]

    # total kontribusi sepanjang masa: satu jendela per tahun sejak akun dibuat
    start = datetime.fromisoformat(d["createdAt"].replace("Z", "+00:00")).year
    years = range(start, date.today().year + 1)
    parts = " ".join(
        f'y{y}:contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{y}-12-31T23:59:59Z")'
        f'{{contributionCalendar{{totalContributions}}}}' for y in years)
    yearly = gql(f"query($u:String!){{user(login:$u){{{parts}}}}}", u=USER)["user"]
    all_time = sum(v["contributionCalendar"]["totalContributions"] for v in yearly.values())

    days = [(date.fromisoformat(x["date"]), x["contributionCount"])
            for w in d["contributionsCollection"]["contributionCalendar"]["weeks"]
            for x in w["contributionDays"]]
    days = [x for x in days if x[0] <= date.today()]

    langs = {}
    for repo in d["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            if e["node"]["name"] not in SKIP_LANGS:
                langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]

    return dict(
        since=start,
        all_time=all_time,
        year=d["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        commits=d["contributionsCollection"]["totalCommitContributions"],
        prs=d["pullRequests"]["totalCount"],
        issues=d["issues"]["totalCount"],
        repos=d["repositories"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in d["repositories"]["nodes"]),
        followers=d["followers"]["totalCount"],
        days=days,
        langs=langs,
    )


def streaks(days):
    longest = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current = 0
    # hari ini belum ada kontribusi tidak memutus streak
    seq = days[:-1] if days and days[-1][1] == 0 else days
    for _, n in reversed(seq):
        if not n:
            break
        current += 1
    return current, longest


def fmt(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 10000 else f"{n:,}"


def tile(x, y, w, h, value, label, t, delay):
    return (f'<g class="rise" style="animation-delay:{delay:.2f}s">'
            f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="12" fill="{t["tile"]}" '
            f'stroke="{t["tile_line"]}"/>'
            f'<rect x="{x + 16}" y="{y + 18}" width="18" height="3" rx="1.5" fill="{t["accent"]}"/>'
            f'<text x="{x + 16}" y="{y + 58}" font-family="{SANS}" font-size="28" font-weight="700" '
            f'letter-spacing="-.02em" fill="{t["value"]}">{value}</text>'
            f'<text x="{x + 16}" y="{y + 80}" font-family="{MONO}" font-size="11" letter-spacing=".06em" '
            f'fill="{t["muted"]}">{escape(label)}</text></g>')


def heatmap(days, x0, y0, t):
    recent = days[-WEEKS * 7:]
    # mulai dari hari Minggu supaya kolom = minggu
    while recent and recent[0][0].weekday() != 6:
        recent = recent[1:]
    peak = max((n for _, n in recent), default=0) or 1
    size, gap = 13, 3
    out = []
    for i, (day, n) in enumerate(recent):
        col, row = divmod(i, 7)
        level = 0 if n == 0 else min(4, 1 + int(3 * n / peak))
        out.append(f'<rect x="{x0 + col * (size + gap)}" y="{y0 + row * (size + gap)}" width="{size}" '
                   f'height="{size}" rx="3" fill="{t["cells"][level]}" class="cell" '
                   f'style="animation-delay:{0.3 + col * 0.02:.2f}s"><title>{day:%d %b %Y}: {n}</title></rect>')
    months, last = [], None
    for i in range(0, len(recent), 7):
        m = recent[i][0].strftime("%b")
        if m != last:
            months.append(f'<text x="{x0 + (i // 7) * (size + gap)}" y="{y0 - 8}" font-family="{MONO}" '
                          f'font-size="10" fill="{t["muted"]}">{m}</text>')
            last = m
    legend_x = x0 + (WEEKS - 1) * (size + gap) + size
    legend = [f'<text x="{legend_x - 5 * (size - 2 + 3) - 8}" y="{y0 + 7 * (size + gap) + 14}" '
              f'font-family="{MONO}" font-size="10" fill="{t["muted"]}" text-anchor="end">less</text>']
    for k, c in enumerate(t["cells"]):
        legend.append(f'<rect x="{legend_x - (5 - k) * (size - 2 + 3) + 3}" y="{y0 + 7 * (size + gap) + 4}" '
                      f'width="{size - 2}" height="{size - 2}" rx="2.5" fill="{c}"/>')
    legend.append(f'<text x="{legend_x + 6}" y="{y0 + 7 * (size + gap) + 14}" font-family="{MONO}" '
                  f'font-size="10" fill="{t["muted"]}">more</text>')
    return "".join(out + months + legend)


def languages(langs, x0, y0, w, t):
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:TOP_LANGS - 1]
    rest = total - sum(v for _, v in top)
    rows = top + ([("Other", rest)] if rest > 0 else [])
    out = [f'<clipPath id="langbar"><rect x="{x0}" y="{y0}" width="{w}" height="10" rx="5"/></clipPath>',
           f'<g clip-path="url(#langbar)">']
    x = x0
    for i, (_, v) in enumerate(rows):
        seg = w * v / total
        out.append(f'<rect x="{x:.1f}" y="{y0}" width="{seg + .5:.1f}" height="10" fill="{LANG_PALETTE[i]}"/>')
        x += seg
    out.append("</g>")
    for i, (name, v) in enumerate(rows):
        cy = y0 + 36 + i * 22
        out.append(f'<circle cx="{x0 + 5}" cy="{cy - 4}" r="5" fill="{LANG_PALETTE[i]}"/>'
                   f'<text x="{x0 + 18}" y="{cy}" font-family="{SANS}" font-size="13" fill="{t["value"]}">'
                   f'{escape(name)}</text>'
                   f'<text x="{x0 + w}" y="{cy}" font-family="{MONO}" font-size="12" '
                   f'fill="{t["muted"]}" text-anchor="end">{100 * v / total:.1f}%</text>')
    return "".join(out)


def card(s, mode):
    t = THEMES[mode]
    current, longest = streaks(s["days"])
    meta = f'@{USER} · since {s["since"]}'
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="GitHub stats: {s["all_time"]} contributions, {s["commits"]} commits this year, '
        f'{s["prs"]} pull requests, {s["stars"]} stars">',
        "<style>.rise{animation:rise .6s ease-out backwards}"
        "@keyframes rise{from{opacity:0;transform:translateY(6px)}}"
        ".cell{animation:pop .4s ease-out backwards}@keyframes pop{from{opacity:0}}"
        ".flame{animation:flick 1.6s ease-in-out infinite alternate}@keyframes flick{to{opacity:.55}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>',
        f'<text x="{PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="12" letter-spacing=".14em" '
        f'fill="{t["accent"]}"><tspan font-size="9">●</tspan> {TITLE}</text>',
        f'<text x="{W - PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="11.5" fill="{t["muted"]}" '
        f'text-anchor="end">{escape(meta)}</text>',
        f'<text x="{PAD}" y="{PAD + 50}" font-family="{SANS}" font-size="26" font-weight="700" '
        f'letter-spacing="-.02em" fill="{t["title"]}">{HEADLINE}</text>',
    ]
    tiles = [
        (fmt(s["all_time"]), "CONTRIBUTIONS"),
        (fmt(s["commits"]), "COMMITS · 12 MO"),
        (fmt(s["prs"]), "PULL REQUESTS"),
        # bintang baru ditampilkan kalau sudah ada, sebelumnya jumlah repo publik
        (fmt(s["stars"]), "STARS EARNED") if s["stars"] else (fmt(s["repos"]), "PUBLIC REPOS"),
    ]
    gap = 14
    tw = (W - 2 * PAD - 3 * gap) / 4
    for i, (v, label) in enumerate(tiles):
        p.append(tile(PAD + i * (tw + gap), 98, tw, 96, v, label, t, 0.05 * i))

    # panel bawah kiri: heatmap + streak
    y = 218
    p.append(f'<text x="{PAD}" y="{y + 14}" font-family="{MONO}" font-size="11" letter-spacing=".1em" '
             f'fill="{t["muted"]}">LAST {WEEKS} WEEKS · {fmt(s["year"])} IN 12 MO</text>')
    p.append(heatmap(s["days"], PAD, y + 44, t))
    sx = PAD + WEEKS * 16 + 22
    p.append(f'<line x1="{sx}" y1="{y + 4}" x2="{sx}" y2="{H - PAD}" stroke="{t["tile_line"]}"/>')
    # streak, di antara heatmap dan bahasa
    stx = sx + 24
    p.append(f'<g class="rise" style="animation-delay:.3s">'
             f'<text x="{stx}" y="{y + 14}" font-family="{MONO}" font-size="11" letter-spacing=".1em" '
             f'fill="{t["muted"]}">STREAK</text>'
             f'<path class="flame" d="M{stx + 9},{y + 40} c6,7 9,12 9,18 a9,9 0 0 1 -18,0 c0,-5 3,-8 5,-10 '
             f'c0,4 2,6 4,6 c1,-4 -1,-9 0,-14 z" fill="{t["accent"]}"/>'
             f'<text x="{stx + 28}" y="{y + 66}" font-family="{SANS}" font-size="28" font-weight="700" '
             f'fill="{t["value"]}">{current}</text>'
             f'<text x="{stx}" y="{y + 90}" font-family="{MONO}" font-size="11" fill="{t["muted"]}">'
             f'current days</text>'
             f'<text x="{stx}" y="{y + 138}" font-family="{SANS}" font-size="22" font-weight="700" '
             f'fill="{t["value"]}">{longest}</text>'
             f'<text x="{stx}" y="{y + 158}" font-family="{MONO}" font-size="11" fill="{t["muted"]}">'
             f'longest · 12 mo</text></g>')
    lx = stx + 130
    p.append(f'<line x1="{lx - 22}" y1="{y + 4}" x2="{lx - 22}" y2="{H - PAD}" stroke="{t["tile_line"]}"/>')
    p.append(f'<g class="rise" style="animation-delay:.4s">'
             f'<text x="{lx}" y="{y + 14}" font-family="{MONO}" font-size="11" letter-spacing=".1em" '
             f'fill="{t["muted"]}">TOP LANGUAGES</text>'
             f'{languages(s["langs"], lx, y + 34, W - PAD - lx, t)}</g>')
    p.append("</svg>")
    return "".join(p)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "dist"
    os.makedirs(out, exist_ok=True)
    s = load()
    for mode in THEMES:
        with open(os.path.join(out, f"github-stats-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(card(s, mode))
    print({k: v for k, v in s.items() if k not in ("days", "langs")}, "streak", streaks(s["days"]))


if __name__ == "__main__":
    main()
