"""Builds every animated SVG in assets/ (except stats.svg, see stats.py).

Run: python3 scripts/build.py
"""
import colorsys, html, pathlib, re, textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = ROOT / "assets"
ICONS = ROOT / "scripts" / "icons"
(A / "projects").mkdir(parents=True, exist_ok=True)
SANS = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', Consolas, 'Courier New', monospace"
G, IN = "#10D59A", "#6366F1"  # emerald + indigo, the brand pair
PV = "#7F75E8"  # predev. brand purple
e = html.escape


def dark(hexc, f):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, max(0, l * f), s)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


STYLE = """
  .fl { animation: fl 4s ease-in-out infinite; }
  @keyframes fl { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-7px); } }
  .sh { animation: sh 4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
  @keyframes sh { 0%,100% { transform: scaleX(1); opacity: .45; } 50% { transform: scaleX(.8); opacity: .2; } }
  .fp { animation: fp 9s cubic-bezier(.45,0,.2,1) infinite; transform-box: fill-box; transform-origin: center; }
  @keyframes fp { 0%,78% { transform: scaleX(1) skewY(0); } 83% { transform: scaleX(.02) skewY(-12deg); } 88% { transform: scaleX(-1) skewY(0); }
                  93% { transform: scaleX(.02) skewY(12deg); } 98%,100% { transform: scaleX(1) skewY(0); } }
  .glow { animation: glow 6s ease-in-out infinite; }
  @keyframes glow { 0%,100% { opacity: .35; } 50% { opacity: .6; } }
  .up { animation: up .8s cubic-bezier(.2,.7,.2,1) backwards; }
  @keyframes up { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
"""

DEFS = f"""
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070d14"/><stop offset=".55" stop-color="#0a1a1c"/><stop offset="1" stop-color="#0f1030"/></linearGradient>
  <linearGradient id="face" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#14202a"/><stop offset="1" stop-color="#0d141c"/></linearGradient>
  <linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".2"/><stop offset=".45" stop-color="#fff" stop-opacity=".03"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="ac" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{G}"/><stop offset="1" stop-color="{IN}"/></linearGradient>
  <radialGradient id="o1"><stop offset="0" stop-color="{G}" stop-opacity=".45"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></radialGradient>
  <radialGradient id="o2"><stop offset="0" stop-color="{IN}" stop-opacity=".45"/><stop offset="1" stop-color="{IN}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="#fff" fill-opacity=".06"/></pattern>
  <filter id="bl" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
"""


def frame(w, h, body, style="", defs=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>{STYLE}{style}</style>
<defs>{DEFS}{defs}<clipPath id="c"><rect width="{w}" height="{h}" rx="20"/></clipPath></defs>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" fill="url(#dots)"/>
  <circle class="glow" cx="{w - 60}" cy="50" r="280" fill="url(#o2)"/>
  <circle class="glow" style="animation-delay:-3s" cx="70" cy="{h - 30}" r="240" fill="url(#o1)"/>
  {body}
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="19.5" fill="none" stroke="#fff" stroke-opacity=".1"/>
</svg>"""


def tile3d(w, h, col, r=14, depth=6):
    """The raised card face every section uses."""
    return f"""<rect y="{depth}" width="{w}" height="{h}" rx="{r}" fill="{dark(col, .35)}"/>
    <rect y="{depth / 2}" width="{w}" height="{h}" rx="{r}" fill="{dark(col, .5)}"/>
    <rect width="{w}" height="{h}" rx="{r}" fill="url(#face)"/>
    <rect width="{w}" height="{h}" rx="{r}" fill="{col}" fill-opacity=".06"/>
    <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r - .5}" fill="none" stroke="{col}" stroke-opacity=".38"/>"""


def icon_tile(emoji, col, size, delay):
    r = size * .25
    return f"""<g class="fp" style="animation-delay:{delay:.2f}s">
    <rect y="{size * .12:.1f}" width="{size}" height="{size}" rx="{r}" fill="{dark(col, .4)}"/>
    <rect y="{size * .06:.1f}" width="{size}" height="{size}" rx="{r}" fill="{dark(col, .65)}"/>
    <rect width="{size}" height="{size}" rx="{r}" fill="#1a2430"/>
    <rect width="{size}" height="{size}" rx="{r}" fill="{col}" fill-opacity=".18"/>
    <text x="{size / 2}" y="{size * .68:.1f}" text-anchor="middle" font-size="{size * .48:.0f}">{emoji}</text>
    <rect width="{size}" height="{size}" rx="{r}" fill="url(#gloss)"/>
    <rect x=".5" y=".5" width="{size - 1}" height="{size - 1}" rx="{r - .5}" fill="none" stroke="{col}" stroke-opacity=".6"/>
  </g>"""


def write(name, svg):
    (A / name).write_text(svg)


# ---------------- header ----------------
def header():
    W, H = 1200, 380
    # terminal lines appear one by one, then the whole thing loops
    term = [
        ("#6b7280", "$ ", "#e5e7eb", "git push origin main"),
        ("#10D59A", "✓ ", "#a9b3c9", "tests passed"),
        ("#10D59A", "✓ ", "#a9b3c9", "docker image built"),
        ("#10D59A", "✓ ", "#a9b3c9", "migrations applied"),
        ("#10D59A", "✓ ", "#a9b3c9", "swarm rollout · replicas healthy"),
        ("#818CF8", "→ ", "#e5e7eb", "shipped to production 🚀"),
    ]
    n = len(term)
    rows = "".join(
        f'<text x="24" y="{76 + i * 25}" class="tl t{i}"><tspan fill="{c1}">{e(p)}</tspan><tspan fill="{c2}">{e(t)}</tspan></text>'
        for i, (c1, p, c2, t) in enumerate(term))
    cyc = 9
    tl_css = "".join(
        f".t{i} {{ animation: tl{i} {cyc}s steps(1) infinite; }} @keyframes tl{i} {{ 0% {{ opacity: 0; }} {int((i + 1) * 9)}% {{ opacity: 1; }} 94% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}\n"
        for i in range(n))
    chips = [("🏢", "predev. Solutions", 200, PV), ("⚡", "6+ yrs in production", 206, "#fff"), ("📍", "Cairo, Egypt", 146, "#fff")]
    cx, ch = 72, ""
    for emo, label, w, col in chips:
        hl = col != "#fff"
        ch += (f'<rect x="{cx}" y="290" width="{w}" height="36" rx="18" fill="{col}" fill-opacity="{.2 if hl else .06}" stroke="{col}" stroke-opacity="{.7 if hl else .12}"/>'
               f'<text x="{cx + w / 2}" y="313" text-anchor="middle" fill="{"#e6e3ff" if hl else "#aab3c8"}" font-weight="{600 if hl else 400}">{emo}  {e(label)}</text>')
        cx += w + 12
    body = f"""
  <circle class="orb" cx="1000" cy="90" r="160" fill="{IN}" opacity=".5" filter="url(#blur)"/>
  <circle class="orb o2" cx="1130" cy="300" r="120" fill="{G}" opacity=".35" filter="url(#blur)"/>
  <circle class="orb o3" cx="720" cy="360" r="100" fill="#22D3EE" opacity=".18" filter="url(#blur)"/>
  <rect class="shine" x="0" y="0" width="300" height="{H}" fill="url(#shg)" transform="skewX(-20)"/>

  <g transform="translate(770 62)" class="up" style="animation-delay:1s">
    <rect width="370" height="236" rx="14" fill="#0b1117" fill-opacity=".88" stroke="#fff" stroke-opacity=".1"/>
    <path d="M.5 14.5a14 14 0 0 1 14-14h341a14 14 0 0 1 14 14V40H.5z" fill="#121a22"/>
    <circle cx="22" cy="20" r="6" fill="#ff5f57"/><circle cx="42" cy="20" r="6" fill="#febc2e"/><circle cx="62" cy="20" r="6" fill="#28c840"/>
    <text x="350" y="25" text-anchor="end" font-family="{MONO}" font-size="12" fill="#6b7280">~/ynmo-pay — deploy</text>
    <g font-family="{MONO}" font-size="13.5" xml:space="preserve">{rows}</g>
    <rect class="cur" x="24" y="{76 + n * 25 - 14}" width="9" height="17" fill="{G}"/>
  </g>

  <text class="up" style="animation-delay:.15s" x="72" y="104" font-family="{MONO}" font-size="18" fill="{G}">// hello world, I'm</text>
  <text class="up" style="animation-delay:.4s" x="68" y="178" font-family="{SANS}" font-size="68" font-weight="800" fill="#f4f7fb" letter-spacing="-1.5">Mario Mamdouh</text>
  <rect class="bar" x="72" y="198" width="200" height="6" rx="3" fill="url(#ac)"/>
  <text class="up" style="animation-delay:.7s" x="72" y="250" font-family="{SANS}" font-size="27" font-weight="600" fill="#d7dcf0"><tspan fill="#A9A3FF">Founder &amp; CEO</tspan> <tspan fill="#6b7280">·</tspan> Software Engineer</text>
  <g class="up" style="animation-delay:1s" font-family="{SANS}" font-size="15.5">{ch}</g>
"""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{STYLE}
  .orb {{ animation: orb 9s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  .o2 {{ animation-duration: 12s; animation-delay: -4s; }} .o3 {{ animation-duration: 15s; animation-delay: -7s; }}
  @keyframes orb {{ 0%,100% {{ transform: translate(0,0) scale(1); }} 50% {{ transform: translate(-30px,18px) scale(1.12); }} }}
  .bar {{ animation: grow 1.2s .6s cubic-bezier(.2,.7,.2,1) both; transform-origin: left; transform-box: fill-box; }}
  @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
  .cur {{ animation: blink 1s steps(1) infinite; }} @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .shine {{ animation: shine 7s linear infinite; }} @keyframes shine {{ from {{ transform: translateX(-400px); }} to {{ transform: translateX(1700px); }} }}
  {tl_css}
</style>
<defs>{DEFS}
  <linearGradient id="shg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="42"/></filter>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  {body}
</g>
</svg>"""
    write("header.svg", svg)


# ---------------- impact numbers ----------------
IMPACT = [
    ("⏳", "6+", "years shipping", "production software, end to end", G),
    ("🧭", "18", "months as Tech Lead", "architecture · reviews · mentoring", IN),
    ("🚀", "12+", "products shipped", "SaaS · marketplaces · fintech", "#F59E0B"),
    ("👥", "2M+", "monthly visitors", "on platforms I built for", "#22D3EE"),
    ("💰", "$5.5M", "VC-backed SaaS", "core engineer on Ynmo", "#EC4899"),
    ("🌍", "4", "regions served", "Egypt · Saudi · Gulf · Europe", "#F43F5E"),
]


def impact():
    W, cols, cw, ch, gx, gy, x0, y0 = 920, 3, 276, 118, 18, 26, 22, 26
    rows = (len(IMPACT) + cols - 1) // cols
    H = y0 + rows * (ch + gy) + 4
    out = []
    for i, (emo, num, label, sub, col) in enumerate(IMPACT):
        r, c = divmod(i, cols)
        x, y, d = x0 + c * (cw + gx), y0 + r * (ch + gy), -(r * .5 + c * .35)
        out.append(f"""<g transform="translate({x} {y})"><g class="fl" style="animation-delay:{d:.2f}s">
  {tile3d(cw, ch, col)}
  <g transform="translate(20 20)">{icon_tile(emo, col, 42, i * .9)}</g>
  <text class="pop" style="animation-delay:{.2 + i * .15:.2f}s" x="76" y="50" font-family="{SANS}" font-size="34" font-weight="800" fill="#f4f7fb">{e(num)}</text>
  <text x="76" y="76" font-family="{SANS}" font-size="14" font-weight="600" fill="{col}">{e(label)}</text>
  <text x="20" y="102" font-family="{SANS}" font-size="13.5" fill="#a9b3c9">{e(sub)}</text>
</g></g>""")
    write("impact.svg", frame(W, H, "".join(out), """
  .pop { animation: pop .9s cubic-bezier(.2,1.6,.4,1) backwards; transform-box: fill-box; transform-origin: left center; }
  @keyframes pop { from { opacity: 0; transform: scale(.4); } to { opacity: 1; transform: none; } }"""))


# ---------------- about code card ----------------
def about():
    K, S, F, N, C, T, P = "#c678dd", "#98c379", "#61afef", "#d19a66", "#6b7280", "#e5e7eb", "#e06c75"
    Y = "#e5c07b"
    rows = [
        [(K, "final class "), (Y, "Mario "), (K, "extends "), (Y, "Engineer"), (T, " {")],
        [(T, "")],
        [(K, "    public "), (P, "$role"), (T, "     = "), (S, "'Founder & CEO'"), (T, ";")],
        [(K, "    public "), (P, "$company"), (T, "  = "), (S, "'predev. Solutions'"), (T, ";")],
        [(K, "    public "), (P, "$previous"), (T, " = "), (S, "['Senior SWE', 'Tech Lead']"), (T, ";")],
        [(K, "    public "), (P, "$years"), (T, "    = "), (N, "6"), (T, "; "), (C, "// and counting")],
        [(T, "")],
        [(K, "    public function "), (F, "focus"), (T, "(): "), (Y, "array"), (T, " {")],
        [(K, "        return "), (T, "["), (S, "'payments'"), (T, ", "), (S, "'microservices'"), (T, ",")],
        [(T, "                "), (S, "'system design'"), (T, ", "), (S, "'cloud'"), (T, "];")],
        [(T, "    }")],
        [(T, "")],
        [(K, "    public function "), (F, "ship"), (T, "("), (Y, "Idea "), (P, "$idea"), (T, "): "), (Y, "Product"), (T, " {")],
        [(K, "        return "), (P, "$idea"), (T, "->"), (F, "design"), (T, "()->"), (F, "test"), (T, "()->"), (F, "deploy"), (T, "();")],
        [(T, "    }")],
        [(T, "}")],
    ]
    body = ""
    for i, r in enumerate(rows):
        ts = "".join(f'<tspan fill="{c}">{e(t)}</tspan>' for c, t in r)
        body += f'<text x="16" y="{72 + i * 22}" xml:space="preserve" class="l" style="animation-delay:{.12 * i:.2f}s"><tspan fill="#3f4a56">{i + 1:>2}  </tspan>{ts}</text>'
    aw, ah = 560, 72 + len(rows) * 22 + 12
    write("about.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{aw}" height="{ah}" viewBox="0 0 {aw} {ah}">
<style>.l{{animation:in .5s ease backwards}}@keyframes in{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
.cur{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}</style>
<rect x=".5" y=".5" width="{aw - 1}" height="{ah - 1}" rx="14" fill="#0b1117" stroke="#fff" stroke-opacity=".12"/>
<path d="M.5 14.5a14 14 0 0 1 14-14h{aw - 29}a14 14 0 0 1 14 14V40H.5z" fill="#121a22"/>
<circle cx="22" cy="20" r="6" fill="#ff5f57"/><circle cx="42" cy="20" r="6" fill="#febc2e"/><circle cx="62" cy="20" r="6" fill="#28c840"/>
<text x="{aw / 2}" y="25" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="#8b95ab">app/Engineers/Mario.php</text>
<g font-family="{MONO}" font-size="13.5">{body}</g>
<rect class="cur" x="40" y="{72 + (len(rows) - 1) * 22 + 6}" width="8" height="15" fill="{G}"/>
</svg>''')


# ---------------- what I bring ----------------
SERVICES = [
    ("💳", "Payments & Fintech", "#F59E0B", "Card gateways, BNPL, bank APIs over OAuth2/mTLS, secure webhooks and end-to-end reconciliation."),
    ("🧱", "System Design", IN, "Microservices, multi-tenant SaaS and event-driven flows, designed to be boring to operate."),
    ("🔌", "APIs & Backends", "#FF2D20", "Laravel, Yii2 and NestJS services with queues, caching, locks and race-condition-safe writes."),
    ("☁️", "Cloud & DevOps", "#22D3EE", "Docker Swarm and Kubernetes on GCP/AWS, CI/CD pipelines, alerting and zero-downtime deploys."),
    ("🖥️", "Full-Stack & Mobile", G, "Next.js, React, Vue and Angular front-ends, plus Flutter apps, all bilingual AR/EN and RTL-first."),
    ("🧑‍🏫", "Technical Leadership", "#EC4899", "Architecture decisions, code review, mentoring and turning business goals into shippable scope."),
]


def services():
    W, cols, cw, ch, gx, gy, x0, y0 = 920, 3, 272, 156, 22, 34, 25, 28
    rows = (len(SERVICES) + cols - 1) // cols
    H = y0 + rows * (ch + gy) + 6
    out = []
    for i, (emo, title, col, desc) in enumerate(SERVICES):
        r, c = divmod(i, cols)
        x, y, d = x0 + c * (cw + gx), y0 + r * (ch + gy), -(r * .5 + c * .35)
        lines = "".join(f'<text x="22" y="{96 + k * 19}">{e(l)}</text>' for k, l in enumerate(textwrap.wrap(desc, 36)[:3]))
        out.append(f"""<g transform="translate({x} {y})">
  <ellipse class="sh" style="animation-delay:{d:.2f}s" cx="{cw / 2}" cy="{ch + 16}" rx="{cw / 2 - 26}" ry="5" fill="{col}" filter="url(#bl)"/>
  <g class="fl" style="animation-delay:{d:.2f}s">
    {tile3d(cw, ch, col, 16, 7)}
    <g transform="translate(22 18)">{icon_tile(emo, col, 44, i * .8)}</g>
    <text x="80" y="47" font-family="{SANS}" font-size="17" font-weight="700" fill="#f4f7fb">{e(title)}</text>
    <g font-family="{SANS}" font-size="13" fill="#a9b3c9">{lines}</g>
  </g>
</g>""")
    write("services.svg", frame(W, H, "".join(out)))


# ---------------- career timeline ----------------
CAREER = [
    ("2020", "OTG", "Backend Developer", "Cairo", "#F43F5E",
     ["Scalable APIs", "DB replication", "Unit → E2E tests"]),
    ("2022", "Tod-z", "Software Engineer", "Estonia · remote", "#F59E0B",
     ["Marketplace", "Full-stack Laravel", "AWS deploys"]),
    ("2022", "Kick Start Interactive", "Software Engineer", "Contract · remote", "#22D3EE",
     ["Web ⇄ mobile sync", "Cross-team Agile"]),
    ("2023", "REFILEX", "Tech Lead", "Cairo", IN,
     ["Led the team", "Architecture", "Mentoring"]),
    ("2025", "Evolvice GmbH", "Senior SWE", "Germany · remote", G,
     ["Payments service", "Bank APIs · mTLS", "Swarm on GCP"]),
    ("2026", "predev.", "Founder & CEO", "Cairo · 14 people", PV,
     ["Founded & run it", "8+ products live", "Team of 14"]),
]


def career():
    W, x0, colw, top, cardh = 920, 16, 148, 104, 164
    H = top + cardh + 34
    ax = 44
    out = [f'<line x1="{ax}" x2="{W - ax}" y1="56" y2="56" stroke="#fff" stroke-opacity=".12" stroke-width="3" stroke-linecap="round"/>',
           f'<line class="run" x1="{ax}" x2="{W - ax}" y1="56" y2="56" stroke="url(#run)" stroke-width="3" stroke-linecap="round"/>']
    for m, (year, co, role, where, col, pts) in enumerate(CAREER):
        cx = x0 + m * colw + colw / 2
        now = m == len(CAREER) - 1
        out.append(f"""<g transform="translate({cx} 56)">
  <circle class="pl" style="animation-delay:{m * .5:.1f}s" r="16" fill="{col}" fill-opacity=".25"/>
  <circle r="10" fill="{dark(col, .5)}"/><circle r="8" cy="-1.5" fill="{col}"/>
</g>
<text x="{cx}" y="30" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="700" fill="{col}">{year}{" → NOW" if now else ""}</text>
<text x="{cx}" y="90" text-anchor="middle" font-family="{SANS}" font-size="12" fill="#8b95ab">{e(where)}</text>""")
        x, w, d = x0 + m * colw + 6, colw - 12, -(m * .4)
        name = co if len(co) < 14 else co.replace(" Interactive", "").replace(" GmbH", "")
        bl = "".join(f'<text x="14" y="{86 + k * 22}"><tspan fill="{col}">▸ </tspan>{e(p)}</text>'
                     for k, p in enumerate(pts))
        out.append(f"""<g transform="translate({x} {top})"><g class="fl" style="animation-delay:{d:.2f}s">
  {tile3d(w, cardh, col, 12, 6)}
  <rect width="{w}" height="4" rx="2" fill="{col}"/>
  <rect width="{w}" height="{cardh}" rx="12" fill="url(#gloss)" opacity=".5"/>
  <text x="14" y="32" font-family="{SANS}" font-size="15.5" font-weight="700" fill="#f4f7fb">{e(name)}</text>
  <text x="14" y="54" font-family="{MONO}" font-size="10.5" font-weight="700" fill="{col}">{e(role.upper())}</text>
  <g font-family="{SANS}" font-size="11" fill="#a9b3c9">{bl}</g>
</g></g>""")
    write("career.svg", frame(W, H, "".join(out), """
  .run { stroke-dasharray: 140 2000; animation: run 5s linear infinite; }
  @keyframes run { from { stroke-dashoffset: 140; } to { stroke-dashoffset: -900; } }
  .pl { animation: pl 2.4s ease-out infinite; transform-box: fill-box; transform-origin: center; }
  @keyframes pl { 0% { transform: scale(.6); opacity: .9; } 100% { transform: scale(1.9); opacity: 0; } }""",
                                f'<linearGradient id="run" gradientUnits="userSpaceOnUse" x1="44" x2="876"><stop offset="0" stop-color="{IN}"/><stop offset="1" stop-color="{G}"/></linearGradient>'))


# ---------------- architecture: the payment service ----------------
def architecture():
    W, H = 920, 470
    nodes = {  # key: (x, y, w, h, emoji, title, sub, colour)
        "web": (24, 70, 170, 62, "🖥️", "Web apps", "Next.js · Blade", "#22D3EE"),
        "mob": (24, 156, 170, 62, "📱", "Mobile apps", "Flutter", "#22D3EE"),
        "adm": (24, 242, 170, 62, "🧩", "Admin panel", "Filament", "#22D3EE"),
        "svc": (300, 130, 250, 118, "💳", "Payment service", "Laravel · REST · Filament", G),
        "mf": (686, 30, 210, 58, "🏦", "Card gateway", "MyFatoorah", "#F59E0B"),
        "tb": (686, 104, 210, 58, "🛍️", "BNPL", "Tabby", "#EC4899"),
        "stc": (686, 178, 210, 58, "🔐", "Bank B2B payroll", "OAuth2 + mTLS", IN),
        "q": (300, 314, 250, 58, "📨", "Webhooks → queue", "Redis · unique locks", "#F43F5E"),
        "acc": (686, 314, 210, 58, "📒", "Accounting sync", "Qoyod · two-way", "#A78BFA"),
    }
    edges = [("web", "svc"), ("mob", "svc"), ("adm", "svc"), ("svc", "mf"), ("svc", "tb"), ("svc", "stc"),
             ("mf", "q"), ("tb", "q"), ("svc", "q"), ("q", "acc")]

    def anchor(k, side):
        x, y, w, h = nodes[k][:4]
        return {"r": (x + w, y + h / 2), "l": (x, y + h / 2), "b": (x + w / 2, y + h), "t": (x + w / 2, y)}[side]

    out = []
    for i, (a, b) in enumerate(edges):
        if a in ("mf", "tb"):  # webhooks come back from the provider down to the queue
            (x1, y1), (x2, y2) = anchor(a, "l"), anchor("q", "r")
            path = f"M{x1},{y1} C{x1 - 70},{y1} {x2 + 70},{y2} {x2},{y2}"
        elif a == "svc" and b == "q":
            (x1, y1), (x2, y2) = anchor(a, "b"), anchor(b, "t")
            path = f"M{x1},{y1} L{x2},{y2}"
        else:
            (x1, y1), (x2, y2) = anchor(a, "r"), anchor(b, "l")
            mx = (x1 + x2) / 2
            path = f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"
        col = nodes[b][7] if a != "svc" or b == "q" else nodes[b][7]
        dur = 2.4 + (i % 3) * .4
        out.append(f'<path d="{path}" fill="none" stroke="#fff" stroke-opacity=".1" stroke-width="2"/>'
                   f'<path class="flow" style="animation-duration:{dur}s" d="{path}" fill="none" stroke="{col}" stroke-opacity=".75" stroke-width="2" stroke-dasharray="6 10"/>'
                   f'<circle r="4.5" fill="{col}"><animateMotion dur="{dur}s" begin="{-i * .37:.2f}s" repeatCount="indefinite" path="{path}"/></circle>')
    for k, (x, y, w, h, emo, title, sub, col) in nodes.items():
        big = k == "svc"
        d = -(hash(k) % 10) * .3
        out.append(f"""<g transform="translate({x} {y})"><g class="{"fl" if big else ""}" style="animation-delay:{d:.1f}s">
  {tile3d(w, h, col, 12, 5)}
  {'<rect class="ring" x="-4" y="-4" width="%d" height="%d" rx="15" fill="none" stroke="%s" stroke-width="2"/>' % (w + 8, h + 8, col) if big else ""}
  <text x="16" y="{h / 2 + (-6 if big else 7)}" font-size="{30 if big else 20}">{emo}</text>
  <text x="{58 if big else 48}" y="{h / 2 - (8 if big else 3)}" font-family="{SANS}" font-size="{18 if big else 14}" font-weight="700" fill="#f4f7fb">{e(title)}</text>
  <text x="{58 if big else 48}" y="{h / 2 + (14 if big else 15)}" font-family="{MONO}" font-size="{12 if big else 11}" fill="{col}">{e(sub)}</text>
  {f'<text x="16" y="{h - 16}" font-family="{SANS}" font-size="12" fill="#8b95ab">secure webhooks · reconciliation</text>' if big else ""}
</g></g>""")
    # deploy lane
    out.append(f"""<g transform="translate(24 404)">
  <rect width="872" height="44" rx="12" fill="#fff" fill-opacity=".04" stroke="#fff" stroke-opacity=".1" stroke-dasharray="4 6"/>
  <g font-family="{MONO}" font-size="12.5" fill="#a9b3c9">
    <text x="18" y="27"><tspan fill="{G}">⬢ </tspan>Bitbucket CI/CD</text>
    <text x="196" y="27">→</text>
    <text x="222" y="27"><tspan fill="#22D3EE">🐳 </tspan>Docker images</text>
    <text x="386" y="27">→</text>
    <text x="412" y="27"><tspan fill="{IN}">☁ </tspan>Docker Swarm on Google Cloud</text>
    <text x="664" y="27">→</text>
    <text x="690" y="27"><tspan fill="#F59E0B">🔔 </tspan>Slack / email alerts</text>
  </g>
</g>
<text x="24" y="{H - 2}" font-family="{SANS}" font-size="1" fill="none">.</text>""")
    write("architecture.svg", frame(W, H, "".join(out), """
  .flow { animation: flow 2.4s linear infinite; }
  @keyframes flow { to { stroke-dashoffset: -32; } }
  .ring { animation: ring 2.6s ease-in-out infinite; }
  @keyframes ring { 0%,100% { opacity: .15; } 50% { opacity: .8; } }"""))


# ---------------- project cards ----------------
PROJECTS = [
    ("ynmo", "🧸", "Ynmo", "VC-backed SaaS suite · $5.5M", G,
     "Early-childhood development & special-education platform for nurseries, therapy centres and families across the Gulf.",
     ["Laravel", "Multi-tenant", "RTL", "Subscriptions"]),
    ("ynmopay", "💳", "Ynmo Pay", "Payment microservice", "#F59E0B",
     "MyFatoorah cards, Tabby BNPL and STC Bank B2B payroll behind one API, with two-way Qoyod accounting sync.",
     ["OAuth2/mTLS", "Webhooks", "Swarm", "GCP"]),
    ("aqarmap", "🏙️", "Aqarmap", "Real-estate marketplace · 2M+/mo", "#3B82F6",
     "Compound ratings that let buyers check a compound before they buy, running at national scale in Egypt.",
     ["Backend APIs", "Reports", "Filtering", "Scale"]),
    ("aqarmapsa", "🇸🇦", "Aqarmap Saudi", "Riyadh marketplace", "#22D3EE",
     "Backend and APIs for the Saudi platform connecting buyers, investors, developers and brokers around new projects.",
     ["REST APIs", "Backend", "KSA", "Bilingual"]),
    ("ispeaker", "🎙️", "iSpeaker Live", "Social e-learning · end to end", IN,
     "Feeds, courses, self-hosted Jitsi live rooms, consultations, a PayPal wallet, RTL invoices and a Flutter app.",
     ["Laravel", "Next.js", "Flutter", "Jitsi"]),
    ("quick", "🛵", "Quick App", "Delivery super-app · predev.", "#F43F5E",
     "One cart across five verticals, a seven-state live order tracker and push for customers, shops and drivers.",
     ["Laravel", "Flutter", "Realtime", "Push"]),
    ("todz", "🤝", "tod-Z", "Freelance marketplace", "#EC4899",
     "Two-sided marketplace with separate onboarding tracks, a talent assessment pipeline and secured payments.",
     ["Laravel", "Payments", "AWS", "Full-stack"]),
    ("otlob", "🩺", "Otlob Tabib", "Home-healthcare platform", "#14B8A6",
     "Bookings, scheduling and the multi-specialty request flow behind the iOS and Android apps.",
     ["Laravel", "APIs", "Scheduling", "Mobile"]),
    ("mueaqib", "🏛️", "Mueaqib", "Gov-services marketplace · KSA", "#A78BFA",
     "Connects citizens with licensed offices for government and administrative transactions, aligned with Vision 2030.",
     ["Marketplace", "KSA", "RTL", "Workflows"]),
    ("propertyturkey", "🏝️", "Property Turkey", "International real-estate portal", "#EAB308",
     "Long-running investment portal for overseas buyers across Istanbul and the Turkish coast.",
     ["Yii2", "Multilingual", "SEO", "CMS"]),
]


NOT_LIVE = {"ynmopay"}  # internal service, no public page


def projects():
    W, H = 440, 230
    PAD, EDGE = 10, 9
    CW, CH = W, H + PAD + EDGE + 16
    for n, (slug, icon, name, kind, col, desc, tags) in enumerate(PROJECTS):
        dl_ = -(n * .55)
        dl = "".join(f'<text x="26" y="{112 + i * 22}">{e(l)}</text>' for i, l in enumerate(textwrap.wrap(desc, 56)[:4]))
        x, tg = 26, ""
        for t in tags:
            w = int(len(t) * 7.4 + 22)
            tg += f'<rect x="{x}" y="{H - 44}" width="{w}" height="24" rx="12" fill="{col}" fill-opacity=".14" stroke="{col}" stroke-opacity=".45"/><text x="{x + w / 2}" y="{H - 27.5}" text-anchor="middle">{e(t)}</text>'
            x += w + 8
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}">
<style>
  .fl {{ animation: fl 4.2s ease-in-out infinite; animation-delay: {dl_:.2f}s; }}
  @keyframes fl {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-{PAD}px); }} }}
  .sh {{ animation: sh 4.2s ease-in-out infinite; animation-delay: {dl_:.2f}s; transform-box: fill-box; transform-origin: center; }}
  @keyframes sh {{ 0%,100% {{ transform: scaleX(1); opacity: .45; }} 50% {{ transform: scaleX(.86); opacity: .2; }} }}
  .fp {{ animation: fp 9s cubic-bezier(.45,0,.2,1) infinite; animation-delay: {n * .7:.2f}s; transform-box: fill-box; transform-origin: center; }}
  @keyframes fp {{ 0%,78% {{ transform: scaleX(1) skewY(0); }} 83% {{ transform: scaleX(.02) skewY(-12deg); }} 88% {{ transform: scaleX(-1) skewY(0); }}
                   93% {{ transform: scaleX(.02) skewY(12deg); }} 98%,100% {{ transform: scaleX(1) skewY(0); }} }}
  .g {{ animation: pulse 4s ease-in-out infinite; }} @keyframes pulse {{ 0%,100% {{ opacity: .35; }} 50% {{ opacity: .6; }} }}
  .sw {{ animation: sw 7s ease-in-out infinite; animation-delay: {n * .9:.2f}s; }}
  @keyframes sw {{ 0%,70% {{ transform: translateX(-260px); }} 100% {{ transform: translateX({W + 260}px); }} }}
  .live {{ animation: live 1.6s ease-in-out infinite; }} @keyframes live {{ 50% {{ opacity: .25; }} }}
</style>
<defs>
  <linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#121c26"/><stop offset="1" stop-color="#0b1117"/></linearGradient>
  <radialGradient id="r" cx="1" cy="0" r="1"><stop offset="0" stop-color="{col}" stop-opacity=".5"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>
  <linearGradient id="gl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".45" stop-color="#fff" stop-opacity=".04"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="swg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="ed" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{dark(col, .35)}"/><stop offset=".5" stop-color="{dark(col, .55)}"/><stop offset="1" stop-color="{dark(col, .3)}"/></linearGradient>
  <clipPath id="c"><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16"/></clipPath>
  <filter id="bl" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="5"/></filter>
</defs>
<ellipse class="sh" filter="url(#bl)" cx="{W / 2}" cy="{CH - 9}" rx="{W / 2 - 30}" ry="7" fill="{col}" opacity=".4"/>
<g class="fl"><g transform="translate(0 {PAD})">
  <rect x="0" y="{EDGE}" width="{W}" height="{H}" rx="16" fill="url(#ed)"/>
  <rect x="0" y="{EDGE / 2}" width="{W}" height="{H}" rx="16" fill="{dark(col, .45)}"/>
  <g clip-path="url(#c)">
    <rect width="{W}" height="{H}" fill="url(#b)"/>
    <rect class="g" width="{W}" height="{H}" fill="url(#r)"/>
    <rect width="{W}" height="4" fill="{col}"/>
    <rect class="sw" x="0" y="0" width="180" height="{H}" fill="url(#swg)" transform="skewX(-20)"/>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="#fff" stroke-opacity=".12"/>
  <g transform="translate(26 22)"><g class="fp">
    <rect x="0" y="6" width="48" height="48" rx="12" fill="{dark(col, .4)}"/>
    <rect x="0" y="3" width="48" height="48" rx="12" fill="{dark(col, .65)}"/>
    <rect width="48" height="48" rx="12" fill="#1a2430"/>
    <rect width="48" height="48" rx="12" fill="{col}" fill-opacity=".16"/>
    <text x="24" y="32" text-anchor="middle" font-size="23">{icon}</text>
    <rect width="48" height="48" rx="12" fill="url(#gl)"/>
    <rect x=".5" y=".5" width="47" height="47" rx="11.5" fill="none" stroke="{col}" stroke-opacity=".6"/>
  </g></g>
  <text x="88" y="46" font-family="{SANS}" font-size="19" font-weight="700" fill="#f4f7fb">{e(name)}</text>
  <text x="88" y="67" font-family="{MONO}" font-size="11.5" fill="{col}" letter-spacing=".4">{e(kind.upper())}</text>
  {"" if slug in NOT_LIVE else f'''<g transform="translate({W - 74} 26)"><rect width="52" height="20" rx="10" fill="#10D59A" fill-opacity=".12" stroke="#10D59A" stroke-opacity=".5"/>
    <circle class="live" cx="12" cy="10" r="3.5" fill="#10D59A"/><text x="33" y="14" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="#10D59A">LIVE</text></g>'''}
  <g font-family="{SANS}" font-size="14" fill="#a9b3c9">{dl}</g>
  <g font-family="{SANS}" font-size="11.5" font-weight="600" fill="#e5e7eb">{tg}</g>
</g></g>
</svg>"""
        write(f"projects/{slug}.svg", svg)


# ---------------- tech stack ----------------
TILE = "#1f2833"


def sk(name, pfx):
    s = (ICONS / f"sk_{name}.svg").read_text()
    inner = re.search(r"<g transform=\"translate\(0, 0\)\">\s*(<svg.*</svg>)\s*</g>", s, re.S).group(1)
    for i in set(re.findall(r'id="([^"]+)"', inner)):
        inner = inner.replace(f'id="{i}"', f'id="{pfx}{i}"').replace(f"url(#{i})", f"url(#{pfx}{i})").replace(f'href="#{i}"', f'href="#{pfx}{i}"')
    head, rest = inner.strip().split(">", 1)
    head = re.sub(r'\s(width|height)="[^"]*"', "", head)
    return head.replace("<svg", '<svg x="0" y="0" width="72" height="72"', 1) + ">" + rest


def si(name, color):
    s = (ICONS / f"si_{name}.svg").read_text()
    d = re.search(r'<path d="([^"]+)"', s).group(1)
    tf = "translate(22 22) scale(8.833)" if name == "filament" else "translate(60 60) scale(5.667)"  # filament's path is 24px-wide art
    return (f'<svg x="0" y="0" width="72" height="72" viewBox="0 0 256 256"><rect width="256" height="256" rx="60" fill="{TILE}"/>'
            f'<path transform="{tf}" fill="{color}" d="{d}"/></svg>')


STACK = [
    ("Backend", "⚙️", [("PHP", "sk", "php", "#777BB4"), ("Laravel", "sk", "laravel", "#FF2D20"), ("Yii2", "si", "yii", "#40B3D8"),
                       ("Node.js", "sk", "nodejs", "#5FA04E"), ("NestJS", "sk", "nestjs", "#E0234E"), ("C#", "sk", "cs", "#9B4F96"),
                       ("Java", "sk", "java", "#ED8B00")]),
    ("Frontend", "🎨", [("TypeScript", "sk", "ts", "#3178C6"), ("JavaScript", "sk", "js", "#F0DB4F"), ("Next.js", "sk", "nextjs", "#E6EDF3"),
                        ("React", "sk", "react", "#61DAFB"), ("Vue.js", "sk", "vue", "#4FC08D"), ("Angular", "sk", "angular", "#DD0031"),
                        ("Tailwind", "sk", "tailwind", "#38BDF8")]),
    ("Mobile", "📱", [("Flutter", "sk", "flutter", "#44D1FD"), ("Dart", "sk", "dart", "#0175C2")]),
    ("Data", "🗄️", [("MySQL", "sk", "mysql", "#4479A1"), ("PostgreSQL", "sk", "postgres", "#4169E1"), ("Redis", "sk", "redis", "#FF4438"),
                    ("MongoDB", "sk", "mongodb", "#47A248"), ("Meilisearch", "si", "meilisearch", "#FF5CAA")]),
    ("Cloud", "☁️", [("Google Cloud", "sk", "gcp", "#4285F4"), ("AWS", "sk", "aws", "#FF9900"), ("DigitalOcean", "si", "digitalocean", "#0080FF"),
                     ("Docker", "sk", "docker", "#2496ED"), ("Kubernetes", "sk", "kubernetes", "#326CE5"), ("Nginx", "sk", "nginx", "#009639"),
                     ("Linux", "sk", "linux", "#FCC624")]),
    ("APIs", "🔌", [("GraphQL", "sk", "graphql", "#E10098"), ("Swagger", "si", "swagger", "#85EA2D"), ("JWT / OAuth2", "si", "jsonwebtokens", "#D63AFF"),
                    ("PayPal", "si", "paypal", "#2997E6"), ("Filament", "si", "filament", "#FDAE4B")]),
    ("Workflow", "🧰", [("Git", "sk", "git", "#F05032"), ("GitHub", "sk", "github", "#E6EDF3"), ("Bitbucket", "sk", "bitbucket", "#2684FF"),
                        ("Jira", "si", "jira", "#2684FF"), ("Postman", "sk", "postman", "#FF6C37"), ("VS Code", "sk", "vscode", "#23A9F2")]),
]


def tech():
    W, LBL, X0, STEP, ROWH, TOP = 920, 170, 196, 100, 128, 30
    H = TOP + ROWH * len(STACK) + 10
    out = []
    for r, (cat, emo, items) in enumerate(STACK):
        y = TOP + r * ROWH
        if r:
            out.append(f'<line x1="24" x2="{W - 24}" y1="{y - 10}" y2="{y - 10}" stroke="#fff" stroke-opacity=".06"/>')
        out.append(f'<g transform="translate(24 {y + 20})"><rect width="{LBL - 20}" height="40" rx="20" fill="{G}" fill-opacity=".1" stroke="{G}" stroke-opacity=".45"/>'
                   f'<text x="{(LBL - 20) / 2}" y="26" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="700" fill="#d7fbe9">{emo} {cat}</text></g>')
        for c, (name, src, key, col) in enumerate(items):
            x, d = X0 + c * STEP, r * .35 + c * .22
            icon = sk(key, f"t{r}{c}_") if src == "sk" else si(key, col)
            out.append(f'''<g transform="translate({x} {y})">
  <ellipse class="sh" style="animation-delay:-{d:.2f}s" cx="36" cy="92" rx="30" ry="5" fill="{col}" opacity=".35"/>
  <g class="fl" style="animation-delay:-{d:.2f}s"><g class="fp" style="animation-delay:{d * 1.6:.2f}s">
    <rect x="0" y="7" width="72" height="72" rx="17" fill="{dark(col, .45)}"/>
    <rect x="0" y="3.5" width="72" height="72" rx="17" fill="{dark(col, .7)}"/>
    {icon}
    <rect width="72" height="72" rx="17" fill="url(#gloss)"/>
    <rect x=".5" y=".5" width="71" height="71" rx="16.5" fill="none" stroke="{col}" stroke-opacity=".55"/>
  </g></g>
  <text x="36" y="112" text-anchor="middle" font-family="{SANS}" font-size="11.5" font-weight="600" fill="#9aa4bb">{name}</text>
</g>''')
    write("tech-stack.svg", frame(W, H, "".join(out)))


# ---------------- predev. ----------------
PREDEV_LIVE = ["Rakeez", "Quick App", "iSpeaker", "Arabook", "Sofqaat", "Boutros Afandy", "NileMed", "BioTechnology Egypt"]


def predev():
    W, H = 920, 318
    stats = [("👥", "14", "full-time specialists"), ("🚢", "8+", "products live"), ("🏭", "10", "industries served")]
    out = [f"""<g class="up">
  <text x="36" y="62" font-family="{SANS}" font-size="46" font-weight="800" fill="#f4f7fb" letter-spacing="-1">predev<tspan fill="{PV}">.</tspan></text>
  <text x="36" y="92" font-family="{MONO}" font-size="13" fill="{PV}" letter-spacing="1.5">SOLUTIONS · CAIRO SOFTWARE HOUSE</text>
  <rect x="36" y="110" width="178" height="30" rx="15" fill="{PV}" fill-opacity=".2" stroke="{PV}" stroke-opacity=".7"/>
  <text x="125" y="130" text-anchor="middle" font-family="{SANS}" font-size="13.5" font-weight="700" fill="#e6e3ff">Founder &amp; CEO</text>
  <g font-family="{SANS}" font-size="14" fill="#a9b3c9">
    <text x="36" y="172">Strategy, design and engineering under one roof:</text>
    <text x="36" y="194">mobile apps, web platforms and the brands that</text>
    <text x="36" y="216">sell them, Arabic-first for Egypt and the Gulf.</text>
  </g>
</g>"""]
    for i, (emo, num, label) in enumerate(stats):
        x, y = 470, 28 + i * 64
        out.append(f"""<g transform="translate({x} {y})"><g class="fl" style="animation-delay:{-i * .4:.1f}s">
  {tile3d(414, 50, PV, 12, 5)}
  <text x="18" y="33" font-size="20">{emo}</text>
  <text x="56" y="35" font-family="{SANS}" font-size="24" font-weight="800" fill="#f4f7fb">{num}</text>
  <text x="{56 + len(num) * 16 + 12}" y="33" font-family="{SANS}" font-size="14.5" fill="#c9c5ff">{label}</text>
</g></g>""")
    # ticker of live products
    chips, x = "", 0
    for name in PREDEV_LIVE * 2:
        w = int(len(name) * 8 + 44)
        chips += (f'<rect x="{x}" width="{w}" height="30" rx="15" fill="#fff" fill-opacity=".05" stroke="{PV}" stroke-opacity=".45"/>'
                  f'<circle class="live" cx="{x + 16}" cy="15" r="4" fill="{G}"/><text x="{x + 28}" y="20" font-family="{SANS}" font-size="13" font-weight="600" fill="#e5e7eb">{e(name)}</text>')
        x += w + 10
    half = x / 2
    out.append(f"""<text x="36" y="{H - 52}" font-family="{MONO}" font-size="11.5" fill="#8b95ab" letter-spacing="1">LIVE IN PRODUCTION</text>
<svg x="200" y="{H - 72}" width="{W - 236}" height="34"><g class="tk">{chips}</g></svg>""")
    write("predev.svg", frame(W, H, "".join(out), f"""
  .tk {{ animation: tk 26s linear infinite; }} @keyframes tk {{ to {{ transform: translateX(-{half:.0f}px); }} }}
  .live {{ animation: lv 1.6s ease-in-out infinite; }} @keyframes lv {{ 50% {{ opacity: .25; }} }}""",
        f'<radialGradient id="pv"><stop offset="0" stop-color="{PV}" stop-opacity=".5"/><stop offset="1" stop-color="{PV}" stop-opacity="0"/></radialGradient>').replace(
        'fill="url(#o2)"', 'fill="url(#pv)"', 1))


# ---------------- divider + footer ----------------
def divider():
    write("divider.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="6" viewBox="0 0 1200 6">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".5" stop-color="{G}"/><stop offset=".75" stop-color="{IN}"/><stop offset="1" stop-color="{IN}" stop-opacity="0"/></linearGradient></defs>
<rect width="1200" height="6" rx="3" fill="url(#g)"/></svg>''')


def footer():
    W, H = 1200, 170
    wave = lambda y, a: f"M0 {y} C300 {y - a} 600 {y + a} 900 {y} S1200 {y - a} 1500 {y} V{H} H0Z"
    write("footer.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>.w{{animation:w 8s ease-in-out infinite alternate}}.w2{{animation-duration:11s;animation-delay:-3s}}
@keyframes w{{from{{transform:translateX(0)}}to{{transform:translateX(-300px)}}}}
.t{{animation:t 3s ease-in-out infinite}}@keyframes t{{50%{{opacity:.75}}}}</style>
<defs><linearGradient id="a" x1="0" x2="1"><stop offset="0" stop-color="{G}"/><stop offset="1" stop-color="{IN}"/></linearGradient></defs>
<path class="w w2" d="{wave(70, 40)}" fill="url(#a)" opacity=".35"/>
<path class="w" d="{wave(88, 30)}" fill="url(#a)"/>
<text class="t" x="600" y="140" text-anchor="middle" font-family="{SANS}" font-size="28" font-weight="800" fill="#fff">Let’s build something reliable together</text>
</svg>''')


if __name__ == "__main__":
    for f in (header, predev, impact, about, services, career, architecture, projects, tech, divider, footer):
        f()
    print("assets built:", sorted(p.name for p in A.rglob("*.svg")))
