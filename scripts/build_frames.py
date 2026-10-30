"""Daily contribution chart drawn as a Flutter DevTools frame timeline.

Runs in GitHub Actions (see .github/workflows/frames.yml). Uses GITHUB_TOKEN to
read the contribution calendar. Without a token it renders demo data so the
layout can be previewed locally.

Run:  GITHUB_TOKEN=... python scripts/build_frames.py prapti-chauhan
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from pathlib import Path

from glyphs import THEMES, faces

OUT = Path(__file__).resolve().parent.parent / "assets"
DAYS = 91
W, H, M = 1200, 330, 40

QUERY = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""


def fetch(login):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        rnd = random.Random(7)
        today = dt.date.today()
        return [((today - dt.timedelta(days=DAYS - 1 - i)).isoformat(),
                 0 if rnd.random() < 0.22 else int(rnd.expovariate(0.28))) for i in range(DAYS)], True
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req))
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]
    return days[-DAYS:], False


def stats(days):
    counts = [c for _, c in days]
    total = sum(counts)
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c else 0
        longest = max(longest, cur)
    current = 0
    for c in reversed(counts):
        if not c:
            break
        current += 1
    by_wd = [0] * 7
    for d, c in days:
        by_wd[dt.date.fromisoformat(d).weekday()] += c
    busiest = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][by_wd.index(max(by_wd))]
    return total, total / len(counts), longest, current, busiest


def render(theme, days, login):
    t = THEMES[theme]
    F = faces()
    mono, monob = F["mono"], F["monob"]
    total, avg, longest, current, busiest = stats(days)
    peak = max(c for _, c in days) or 1

    chart_top, chart_bot = 104, 262
    ch = chart_bot - chart_top
    step = (W - 2 * M) / len(days)
    bw = step - 3

    out = [f'<rect width="{W}" height="{H}" rx="18" fill="{t["panel"]}"/>',
           f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{t["dim"]}"/>',
           monob.text("Performance", M, 46, 18, fill=t["ink"]),
           mono.text(f"flutter run --profile   @{login}", M + monob.width("Performance", 18) + 20, 46, 14, fill=t["stroke"]),
           mono.text(f"last {len(days)} days · rebuilt {dt.date.today():%d %b %Y}", W - M, 46, 13, fill=t["stroke"], anchor="end"),
           mono.text("FRAMES  (one frame = one day of commits, PRs, reviews and issues)", M, 84, 12, fill=t["stroke"], tracking=0.04)]

    for gy in range(4):
        y = chart_top + ch * gy / 3
        out.append(f'<line x1="{M}" x2="{W - M}" y1="{y:.1f}" y2="{y:.1f}" stroke="{t["faint"]}"/>')

    best_i = max(range(len(days)), key=lambda i: days[i][1])
    for i, (d, c) in enumerate(days):
        x = M + i * step
        if c == 0:
            out.append(f'<rect x="{x:.1f}" y="{chart_bot - 3}" width="{bw:.1f}" height="3" rx="1" fill="{t["dim"]}"/>')
            continue
        h = max(6, ch * c / peak)
        color = t["ink"] if i == best_i else t["accent"]
        out.append(f'<rect x="{x:.1f}" y="{chart_bot - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" '
                   f'fill="{color}" class="bar" style="animation-duration:{500 + i * 14}ms"><title>{d}: {c}</title></rect>')
    # month ticks
    for i, (d, _) in enumerate(days):
        dd = dt.date.fromisoformat(d)
        if dd.day == 1:
            x = M + i * step
            out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{chart_bot + 4}" y2="{chart_bot + 12}" stroke="{t["stroke"]}"/>')
            out.append(mono.text(dd.strftime("%b").upper(), x + 5, chart_bot + 14, 11, fill=t["stroke"]))

    # average line, like the 16ms frame-budget line in DevTools
    ay = chart_bot - ch * avg / peak
    out.append(f'<line x1="{M}" x2="{W - M}" y1="{ay:.1f}" y2="{ay:.1f}" stroke="{t["accentText"]}" stroke-dasharray="5 5" stroke-width="1.4"/>')
    label = f"avg {avg:.1f}/day"
    lw = mono.width(label, 12)
    out.append(f'<rect x="{W - M - lw - 14}" y="{ay - 22:.1f}" width="{lw + 14}" height="18" rx="4" fill="{t["panel"]}"/>')
    out.append(mono.text(label, W - M - 7, ay - 9, 12, fill=t["accentText"], anchor="end"))

    # footer stats
    cells = [("total", f"{total}"), ("longest streak", f"{longest}d"), ("current streak", f"{current}d"),
             ("busiest", busiest), ("peak frame", f"{peak}")]
    x = M
    for k, v in cells:
        out.append(mono.text(k, x, 304, 13, fill=t["stroke"]))
        kx = x + mono.width(k, 13) + 8
        out.append(monob.text(v, kx, 304, 15, fill=t["ink"]))
        x = kx + monob.width(v, 15) + 36

    style = """
    .bar{transform-box:fill-box;transform-origin:bottom;animation:grow cubic-bezier(.2,.8,.2,1)}
    @keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
    @media (prefers-reduced-motion: reduce){.bar{animation:none}}
    """
    defs = mono.defs() + monob.defs()
    desc = (f"Bar chart of daily GitHub contributions for the last {len(days)} days. Total {total}, "
            f"average {avg:.1f} per day, longest streak {longest} days, busiest weekday {busiest}.")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-labelledby="t d"><title id="t">Contribution frame timeline</title><desc id="d">{desc}</desc>'
            f'<style>{style}</style><defs>{defs}</defs>{"".join(out)}</svg>')


if __name__ == "__main__":
    login = sys.argv[1] if len(sys.argv) > 1 else "prapti-chauhan"
    days, demo = fetch(login)
    OUT.mkdir(exist_ok=True)
    for th in THEMES:
        (OUT / f"frames-{th}.svg").write_text(render(th, days, login), encoding="utf-8")
    print(("demo data" if demo else "live data"), len(days), "days")
