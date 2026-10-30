"""Builds the hero and inspector SVGs (light + dark).

Run:  python scripts/build_static.py
"""
from pathlib import Path

from glyphs import THEMES, faces

OUT = Path(__file__).resolve().parent.parent / "assets"
W = 1200
M = 56  # page padding, also drawn as hatched EdgeInsets in the skeleton


def svg_doc(w, h, title, desc, style, body, defs):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-labelledby="t d"><title id="t">{title}</title><desc id="d">{desc}</desc>'
            f'<style>{style}</style><defs>{defs}</defs>{body}</svg>')


# ---------------------------------------------------------------- hero

def hero(theme_name):
    t = THEMES[theme_name]
    F = faces()
    disp, mono, monob = F["display"], F["mono"], F["monob"]
    H = 566
    inner = W - 2 * M

    lines = ["PRAPTI", "CHAUHAN"]
    # equal-width poster type: each line gets its own size so both span the measure
    sizes = [inner / (disp.width(s, 1, tracking=-0.01)) for s in lines]
    cap = 0.715  # Archivo Black cap-height / em
    gap = 26
    top = 104
    blocks = []
    y = top
    for s, size in zip(lines, sizes):
        base = y + cap * size
        blocks.append((s, size, y, base))
        y = base + gap

    ink, skel = [], []
    for s, size, ytop, base in blocks:
        ink.append(disp.text(s, M, base, size, tracking=-0.01))
        # wireframe copy of the same glyphs
        skel.append(disp.text(s, M, base, size, tracking=-0.01, cls="wire",
                              extra=f'style="stroke-width:{1.6 * disp.upem / size:.1f}"'))
        hgt = base - ytop
        # constraint box
        skel.append(f'<rect x="{M}" y="{ytop:.1f}" width="{inner}" height="{hgt:.1f}" class="box"/>')
        # baseline + cap line running into the margins
        skel.append(f'<line x1="0" x2="{W}" y1="{base:.1f}" y2="{base:.1f}" class="base"/>')
        skel.append(f'<line x1="0" x2="{W}" y1="{ytop:.1f}" y2="{ytop:.1f}" class="capl"/>')
        # per-glyph advance boxes
        glyphs, _ = disp.shape(s, -0.01)
        sc = size / disp.upem
        xs = [M + gx * sc for _, gx, _ in glyphs] + [M + inner]
        for a, b in zip(xs, xs[1:]):
            skel.append(f'<rect x="{a:.1f}" y="{ytop:.1f}" width="{b - a:.1f}" height="{hgt:.1f}" class="adv"/>')
        skel.append(mono.text(f"Text(\"{s.title()}\")  {inner:.1f} × {hgt:.1f}", M + 6, ytop - 8, 12.5, fill=t["accentText"]))
        skel.append(mono.text("baseline", W - M - 4, base - 6, 11, fill=t["stroke"], anchor="end"))

    # padding hatching (EdgeInsets.symmetric(horizontal: 56))
    pad_top, pad_bot = blocks[0][2], blocks[-1][3]
    for x0 in (0, W - M):
        skel.append(f'<rect x="{x0}" y="{pad_top:.1f}" width="{M}" height="{pad_bot - pad_top:.1f}" fill="url(#hatch)"/>')
    skel.append(mono.text("EdgeInsets.symmetric(horizontal: 56)", M + 6, pad_bot + 22, 12.5, fill=t["accentText"]))

    # always-visible chrome
    meta_y = 58
    chrome = [
        mono.text("debugPaintSizeEnabled = true;", M, meta_y, 14, fill=t["stroke"]),
        mono.text("SURAT, IN   21.17°N  72.83°E", W - M, meta_y, 14, fill=t["stroke"], anchor="end"),
        f'<line x1="{M}" x2="{W - M}" y1="{meta_y + 16}" y2="{meta_y + 16}" stroke="{t["dim"]}" stroke-width="1"/>',
    ]
    foot_y = H - 46
    chrome.append(f'<line x1="{M}" x2="{W - M}" y1="{foot_y - 30}" y2="{foot_y - 30}" stroke="{t["dim"]}" stroke-width="1"/>')
    left = "Senior Flutter Engineer"
    lw = monob.width(left, 17)
    chrome.append(monob.text(left, M, foot_y, 17, fill=t["ink"]))
    chrome.append(mono.text("/  fintech + blockchain  /  4+ yrs  /  30+ apps shipped", M + lw + 16, foot_y, 17, fill=t["stroke"]))
    avail = "available for freelance"
    aw = mono.width(avail, 17)
    chrome.append(mono.text(avail, W - M, foot_y, 17, fill=t["accentText"], anchor="end"))
    cx = W - M - aw - 22
    chrome.append(f'<circle cx="{cx}" cy="{foot_y - 6}" r="5" fill="{t["accent"]}"/>'
                  f'<circle cx="{cx}" cy="{foot_y - 6}" r="5" fill="none" stroke="{t["accent"]}" class="ping"/>')

    # cursor path the reveal follows (wanders across both lines)
    pts = [(-160, 170), (220, 190), (420, 250), (610, 180), (800, 230), (1010, 200), (1100, 330),
           (880, 380), (640, 330), (420, 400), (190, 350), (-160, 370)]
    n = len(pts) - 1
    kf = []
    for i, (x, y) in enumerate(pts):
        kf.append(f"{i / n * 100:.2f}%{{transform:translate({x}px,{y}px)}}")
    kf_main = "@keyframes path{" + "".join(kf) + "}"

    dots = "".join(f'<circle cx="{x}" cy="{y}" r="1"/>' for x in range(M, W - M + 1, 34) for y in range(92, H - 80, 34))

    style = f"""
    .wire{{fill:none;stroke:{t['ink']}}}
    .box{{fill:none;stroke:{t['accent']};stroke-width:1.6;stroke-dasharray:7 5}}
    .adv{{fill:{t['accent']};fill-opacity:.05;stroke:{t['stroke']};stroke-width:1}}
    .base{{stroke:{t['accent']};stroke-width:1.6}}
    .capl{{stroke:{t['stroke']};stroke-width:1;stroke-dasharray:2 4}}
    .blob{{animation:path 11s cubic-bezier(.45,.05,.55,.95) infinite}}
    .blob.b2{{animation-delay:-10.65s}}
    .blob.b3{{animation-delay:-10.35s}}
    .ping{{transform-box:fill-box;transform-origin:center;animation:ping 2.2s ease-out infinite}}
    @keyframes ping{{0%{{transform:scale(1);opacity:.9}}100%{{transform:scale(2.6);opacity:0}}}}
    {kf_main}
    @media (prefers-reduced-motion: reduce){{.blob,.ping{{animation:none}}.blob{{transform:translate(560px,250px)}}.blob.b2,.blob.b3{{display:none}}}}
    """

    def blobs(color):
        return (f'<g class="blob"><circle r="118" fill="{color}"/></g>'
                f'<g class="blob b2"><circle r="84" fill="{color}"/></g>'
                f'<g class="blob b3"><circle r="52" fill="{color}"/></g>')

    defs_extra = f"""
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>
    <pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="9" stroke="{t['accent']}" stroke-width="1.2" opacity=".55"/></pattern>
    <mask id="show" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <rect width="{W}" height="{H}" fill="#000"/>{blobs('#fff')}</mask>
    <mask id="hide" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <rect width="{W}" height="{H}" fill="#fff"/>{blobs('#000')}</mask>
    """

    body = (f'<rect width="{W}" height="{H}" rx="18" fill="{t["bg"]}"/>'
            f'<g fill="{t["dim"]}" opacity=".7">{dots}</g>'
            + "".join(chrome)
            + f'<g fill="{t["ink"]}" mask="url(#hide)">{"".join(ink)}</g>'
            + f'<g mask="url(#show)">{"".join(skel)}</g>')
    defs = disp.defs() + mono.defs() + monob.defs() + defs_extra
    return svg_doc(W, H, "Prapti Chauhan, Senior Flutter Engineer",
                   "Poster type of the name Prapti Chauhan. A moving cursor peels the type back to show Flutter's "
                   "debug-paint layout skeleton: constraint boxes, baselines and padding.",
                   style, body, defs)


# ---------------------------------------------------------------- inspector

ROWS = [
    (0, "Prapti", "P", ""),
    (1, "Career", "C", "Column"),
    (2, "BVMInfotech", "T", "trainee · 2021"),
    (2, "RainInfotech", "S", "senior · 2022-26"),
    (3, "AtomWallet", "W", "10K+ users"),
    (3, "KelestialWallet", "W", "NFC cold wallet"),
    (3, "DiveWallet", "W", "Bloc"),
    (2, "Freelance", "F", "2026 →"),
    (1, "Hackathons", "H", "Column"),
    (2, "N8nHackathon2025", "A", "winner"),
    (2, "AIHackathon2026", "A", "impact award"),
]

DETAILS = [
    (4, "AtomWallet", "non-custodial crypto + USDT wallet", [
        ("activeUsers", "10,000+", True),
        ("state", "Provider  (migrated off GetX)", False),
        ("featureLeadTime", "-40%", True),
        ("apiLatency", "-30%  batching + caching", False),
        ("payments", "UPI · bank withdrawals · fiat", False),
        ("security", "RSA · Keystore/Keychain · AML", False),
    ]),
    (5, "KelestialWallet", "physical NFC card as a hardware wallet", [
        ("hardware", "NFC card → cold signer", True),
        ("seedPhraseExposed", "false", True),
        ("connect", "WalletConnect · DApp browser", False),
        ("backup", "encrypted · Google Drive", False),
        ("push", "FCM", False),
    ]),
    (6, "DiveWallet", "send, receive, swap, browse DApps", [
        ("state", "Bloc", True),
        ("architecture", "Clean Architecture", False),
        ("features", "send · receive · token swap", False),
        ("web3", "in-app DApp browser", False),
    ]),
    (7, "Freelance", "independent since Jul 2026", [
        ("clients", "fintech · business", False),
        ("owns", "scoping · estimates · architecture", False),
        ("alsoBuilds", "n8n · OpenAI · RAG · Pinecone", False),
        ("status", "available", True),
    ]),
    (9, "N8nHackathon2025", "AI automation track", [
        ("result", "Winner", True),
        ("built", "VISTA insurance-claims pipeline", False),
        ("plus", "AI content generation", False),
    ]),
    (10, "AIHackathon2026", "internal AI hackathon", [
        ("result", "Internal Impact Award", True),
        ("built", "AI newsletter automation", False),
        ("with", "CRM sync · real-time analytics", False),
    ]),
]


def inspector(theme_name):
    t = THEMES[theme_name]
    F = faces()
    mono, monob = F["mono"], F["monob"]
    H = 560
    split = 560
    row_h = 36
    row0 = 112
    slot = 3.6
    n = len(DETAILS)
    dur = slot * n

    out = [f'<rect width="{W}" height="{H}" rx="18" fill="{t["panel"]}"/>',
           f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{t["dim"]}"/>']
    # tab bar
    out.append(f'<line x1="0" x2="{W}" y1="52" y2="52" stroke="{t["dim"]}"/>')
    for i, c in enumerate((t["dim"], t["dim"], t["dim"])):
        out.append(f'<circle cx="{28 + i * 18}" cy="26" r="5.5" fill="{c}"/>')
    x = 100
    for i, tab in enumerate(["Flutter Inspector", "Performance", "Network", "Logging"]):
        f = monob if i == 0 else mono
        out.append(f.text(tab, x, 31, 14, fill=t["ink"] if i == 0 else t["stroke"]))
        w = f.width(tab, 14)
        if i == 0:
            out.append(f'<rect x="{x}" y="49" width="{w}" height="3" fill="{t["accent"]}"/>')
        x += w + 34
    out.append(mono.text("lib/prapti_chauhan.dart", W - 28, 31, 13, fill=t["stroke"], anchor="end"))
    out.append(f'<line x1="{split}" x2="{split}" y1="52" y2="{H}" stroke="{t["dim"]}"/>')
    out.append(mono.text("WIDGET TREE", 28, 86, 12, fill=t["stroke"], tracking=0.08))
    out.append(mono.text("DETAILS", split + 32, 86, 12, fill=t["stroke"], tracking=0.08))

    def row_y(i):
        return row0 + i * row_h

    # tree guides
    for i, (d, *_rest) in enumerate(ROWS):
        if d == 0:
            continue
        px = 36 + (d - 1) * 26
        # find parent row
        p = max(j for j in range(i) if ROWS[j][0] == d - 1)
        out.append(f'<path d="M{px} {row_y(p) + 8} V{row_y(i)} H{px + 14}" fill="none" stroke="{t["dim"]}" stroke-width="1.2"/>')

    def row_svg(i, color, badge_fill, badge_ink):
        d, name, badge, note = ROWS[i]
        bx = 28 + d * 26
        y = row_y(i)
        s = [f'<rect x="{bx}" y="{y - 10}" width="20" height="20" rx="5" fill="{badge_fill}"/>',
             monob.text(badge, bx + 10, y + 5, 12, fill=badge_ink, anchor="middle"),
             mono.text(name, bx + 30, y + 5.5, 16, fill=color)]
        nw = mono.width(name, 16)
        if note:
            s.append(mono.text(note, bx + 30 + nw + 12, y + 5.5, 13, fill=t["stroke"]))
        return "".join(s)

    for i in range(len(ROWS)):
        out.append(row_svg(i, t["ink"], t["faint"], t["stroke"]))

    # selection states, one per detail, sharing a timeline
    kfs = []
    for k, (ri, name, sub, props) in enumerate(DETAILS):
        a, b = k / n * 100, (k + 1) / n * 100
        e = 0.9
        if k == 0:
            frames = f"0%,{b - e:.2f}%{{opacity:1}}{b:.2f}%,{100 - e:.2f}%{{opacity:0}}100%{{opacity:1}}"
        else:
            frames = f"0%,{a:.2f}%{{opacity:0}}{a + e:.2f}%,{b - e:.2f}%{{opacity:1}}{b:.2f}%,100%{{opacity:0}}"
        kfs.append(f"@keyframes s{k}{{{frames}}}")
        y = row_y(ri)
        g = [f'<g class="sel{' first' if k == 0 else ''}" style="animation-name:s{k}">',
             f'<rect x="12" y="{y - 17}" width="{split - 24}" height="34" rx="8" fill="{t["accent"]}" opacity=".14"/>',
             f'<rect x="12" y="{y - 17}" width="3" height="34" rx="1.5" fill="{t["accent"]}"/>',
             row_svg(ri, t["accentText"], t["accent"], t["panel"])]
        # details pane
        dx = split + 32
        g.append(monob.text(name, dx, 136, 28, fill=t["ink"]))
        g.append(mono.text(sub, dx, 166, 15, fill=t["stroke"]))
        g.append(f'<line x1="{dx}" x2="{W - 32}" y1="190" y2="190" stroke="{t["dim"]}"/>')
        for j, (key, val, hi) in enumerate(props):
            py = 228 + j * 40
            g.append(mono.text(key, dx, py, 15, fill=t["stroke"]))
            g.append(mono.text(":", dx + 196, py, 15, fill=t["dim"]))
            g.append((monob if hi else mono).text(val, dx + 214, py, 15, fill=t["accentText"] if hi else t["ink"]))
            g.append(f'<line x1="{dx}" x2="{W - 32}" y1="{py + 15}" y2="{py + 15}" stroke="{t["faint"]}"/>')
        # progress bar for this slot
        g.append(f'<rect x="{dx}" y="{H - 40}" width="{W - 32 - dx}" height="3" rx="1.5" fill="{t["faint"]}"/>')
        g.append(f'<rect x="{dx}" y="{H - 40}" width="{W - 32 - dx}" height="3" rx="1.5" fill="{t["accent"]}" class="prog"/>')
        g.append(mono.text(f"{k + 1:02d} / {n:02d}", W - 32, H - 52, 12, fill=t["stroke"], anchor="end"))
        g.append("</g>")
        out.append("".join(g))

    style = f"""
    .sel{{opacity:0;animation-duration:{dur}s;animation-iteration-count:infinite;animation-timing-function:linear}}
    .prog{{transform-box:fill-box;transform-origin:left;animation:prog {slot}s linear infinite}}
    @keyframes prog{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
    {''.join(kfs)}
    @media (prefers-reduced-motion: reduce){{.sel{{animation:none}}.sel.first{{opacity:1}}.prog{{animation:none}}}}
    """
    defs = mono.defs() + monob.defs()
    desc = "A Flutter DevTools style inspector of Prapti's career. " + " ".join(
        f"{name}: " + ", ".join(f"{k} {v}" for k, v, _ in props) + "." for _, name, _, props in DETAILS)
    return svg_doc(W, H, "Career, shown as a Flutter widget tree", desc, style, "".join(out), defs)



# ---------------------------------------------------------------- tap-to-inspect nodes

NODES = [
    ("bvm", 2, "BVMInfotech", "T", "trainee · 2021", "where it started", [
        ("role", "Flutter Trainee", True),
        ("period", "Aug 2021 to Mar 2022", False),
        ("next", "RainInfotech, Apr 2022", False),
    ]),
    ("rain", 2, "RainInfotech", "S", "senior · 2022-26", "Senior Flutter Engineer, Apr 2022 to Jun 2026", [
        ("productionWallets", "3  (architecture lead)", True),
        ("architecture", "Clean Architecture · Bloc · Provider", False),
        ("security", "RSA · Secure Storage · Keystore/Keychain · JWT", False),
        ("mentored", "2-3 junior developers", False),
        ("launchCriticalBugs", "0", True),
    ]),
] + [(name.lower(), 3 if "Wallet" in name else 2, name,
      "W" if "Wallet" in name else ("F" if name == "Freelance" else "A"),
      ROWS[ri][3], sub, props) for ri, name, sub, props in DETAILS]


def node_card(theme_name, node):
    t = THEMES[theme_name]
    F = faces()
    mono, monob = F["mono"], F["monob"]
    _, _, name, _, _, sub, props = node
    Hh = 150 + len(props) * 40
    dx = 32
    out = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{Hh - 1}" rx="14" fill="{t["panel"]}" stroke="{t["accent"]}"/>',
           f'<rect x="0.5" y="0.5" width="4" height="{Hh - 1}" rx="2" fill="{t["accent"]}"/>',
           mono.text("DETAILS", dx, 40, 12, fill=t["stroke"], tracking=0.08),
           monob.text(name, dx, 80, 26, fill=t["ink"]),
           mono.text(sub, dx + monob.width(name, 26) + 18, 80, 15, fill=t["stroke"]),
           f'<line x1="{dx}" x2="{W - 32}" y1="102" y2="102" stroke="{t["dim"]}"/>']
    for j, (key, val, hi) in enumerate(props):
        py = 138 + j * 40
        out.append(mono.text(key, dx, py, 15, fill=t["stroke"]))
        out.append(mono.text(":", dx + 220, py, 15, fill=t["dim"]))
        out.append((monob if hi else mono).text(val, dx + 238, py, 15, fill=t["accentText"] if hi else t["ink"]))
        out.append(f'<line x1="{dx}" x2="{W - 32}" y1="{py + 15}" y2="{py + 15}" stroke="{t["faint"]}"/>')
    desc = f"{name}, {sub}. " + "; ".join(f"{k}: {v}" for k, v, _ in props)
    return svg_doc(W, Hh, f"{name} details", desc, "", "".join(out), mono.defs() + monob.defs())


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for th in THEMES:
        (OUT / f"hero-{th}.svg").write_text(hero(th), encoding="utf-8")
        (OUT / f"inspector-{th}.svg").write_text(inspector(th), encoding="utf-8")
        (OUT / "nodes").mkdir(exist_ok=True)
        for node in NODES:
            (OUT / "nodes" / f"{node[0]}-card-{th}.svg").write_text(node_card(th, node), encoding="utf-8")
    for p in sorted(OUT.rglob("*.svg")):
        print(p.name, f"{p.stat().st_size / 1024:.0f} KB")
