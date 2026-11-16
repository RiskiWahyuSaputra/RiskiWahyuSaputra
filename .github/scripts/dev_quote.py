"""Kartu "Random Dev Quote", quote berganti tiap 12 jam (ikut jadwal workflow system scan).

Pemakaian: python3 dev_quote.py <folder-output>
Menghasilkan dev-quote-{dark,light}.svg.
"""
import os
import sys
import textwrap
from datetime import datetime, timezone
from html import escape

QUOTES = [
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.",
     "Harold Abelson"),
    ("Any fool can write code that a computer can understand. Good programmers write code that humans "
     "can understand.", "Martin Fowler"),
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
    ("There are only two hard things in Computer Science: cache invalidation and naming things.",
     "Phil Karlton"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("Adding manpower to a late software project makes it later.", "Fred Brooks"),
    ("Walking on water and developing software from a specification are easy if both are frozen.",
     "Edward V. Berard"),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ("Before software can be reusable it first has to be usable.", "Ralph Johnson"),
    ("Testing shows the presence, not the absence of bugs.", "Edsger W. Dijkstra"),
    ("Real artists ship.", "Steve Jobs"),
    ("Fix the cause, not the symptom.", "Steve Maguire"),
    ("Optimism is an occupational hazard of programming: feedback is the treatment.", "Kent Beck"),
    ("Controlling complexity is the essence of computer programming.", "Brian Kernighan"),
    ("Debugging is twice as hard as writing the code in the first place.", "Brian Kernighan"),
    ("Truth can only be found in one place: the code.", "Robert C. Martin"),
    ("Clean code always looks like it was written by someone who cares.", "Michael Feathers"),
    ("Simplicity is the soul of efficiency.", "R. Austin Freeman"),
    ("Deleted code is debugged code.", "Jeff Sickel"),
]

THEMES = {
    "dark": dict(card="#0d1117", border="#1f6feb55", accent="#58a6ff", accent2="#a371f7",
                 title="#f0f6fc", muted="#9198a1", line="#30363d"),
    "light": dict(card="#ffffff", border="#0969da55", accent="#0969da", accent2="#8250df",
                  title="#1f2328", muted="#59636e", line="#d1d9e0"),
}
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif"
SERIF = "Georgia,'Times New Roman',serif"
W, H = 920, 230
PAD = 28
WRAP = 58  # karakter per baris pada ukuran 23px


def pick(now):
    slot = now.timetuple().tm_yday * 2 + (now.hour >= 12) + now.year * 1000
    i = slot % len(QUOTES)
    return i, QUOTES[i]


def card(i, quote, author, mode):
    t = THEMES[mode]
    lines = textwrap.wrap(quote, WRAP)
    size = 23 if len(lines) <= 2 else 20
    lh = size * 1.45
    block = lh * (len(lines) - 1)
    # quote + baris penulis ditaruh di tengah area di bawah header
    y0 = 142 - (block + 40) / 2 + size * 0.35
    text = "".join(f'<tspan x="120" y="{y0 + k * lh:.1f}">{escape(s)}</tspan>' for k, s in enumerate(lines))
    ay = y0 + block + 40
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="&#8220;{escape(quote)}&#8221; by {escape(author)}">'
        "<style>.in{animation:in .7s ease-out backwards}"
        "@keyframes in{from{opacity:0;transform:translateY(8px)}}"
        ".mark{animation:mark 1s cubic-bezier(.2,1.4,.4,1) backwards}"
        "@keyframes mark{from{opacity:0;transform:scale(.6)}}"
        ".caret{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>"
        f'<defs><linearGradient id="q-{mode}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/>'
        f'</linearGradient></defs>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>'
        f'<rect x="0" y="40" width="4" height="{H - 80}" rx="2" fill="url(#q-{mode})"/>'
        f'<text x="{PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="12" letter-spacing=".14em" '
        f'fill="{t["accent"]}"><tspan font-size="9">●</tspan> DEV QUOTE</text>'
        f'<text x="{W - PAD}" y="{PAD + 18}" font-family="{MONO}" font-size="11.5" fill="{t["muted"]}" '
        f'text-anchor="end">#{i + 1:02d}/{len(QUOTES)} · new quote every 12h</text>'
        f'<g class="mark" style="transform-origin:66px {y0:.0f}px">'
        f'<text x="40" y="{y0 + 58:.1f}" font-family="{SERIF}" font-size="120" font-weight="700" fill="url(#q-{mode})" '
        f'opacity=".9">&#8220;</text></g>'
        f'<g class="in" style="animation-delay:.15s"><text font-family="{SANS}" font-size="{size}" '
        f'font-weight="600" letter-spacing="-.01em" fill="{t["title"]}">{text}</text></g>'
        f'<g class="in" style="animation-delay:.35s">'
        f'<rect x="120" y="{ay - 5:.1f}" width="22" height="2" rx="1" fill="{t["accent"]}"/>'
        f'<text x="152" y="{ay:.1f}" font-family="{MONO}" font-size="13" fill="{t["accent"]}">'
        f'{escape(author)}</text>'
        f'<rect class="caret" x="{152 + len(author) * 7.9:.1f}" y="{ay - 12:.1f}" width="7" height="15" '
        f'fill="{t["accent"]}" opacity=".7"/></g>'
        "</svg>"
    )


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "dist"
    os.makedirs(out, exist_ok=True)
    i, (quote, author) = pick(datetime.now(timezone.utc))
    if len(sys.argv) > 2:  # untuk uji tampilan: python3 dev_quote.py out <nomor>
        i = int(sys.argv[2]) % len(QUOTES)
        quote, author = QUOTES[i]
    for mode in THEMES:
        with open(os.path.join(out, f"dev-quote-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(card(i, quote, author, mode))
    print(f"#{i + 1}: {quote} — {author}")


if __name__ == "__main__":
    main()
