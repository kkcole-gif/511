#!/usr/bin/env python3
"""Connect ENG 511 pages to theme.css.

Run from the repository root:   python3 tools/apply_theme.py
Run on named pages only:        python3 tools/apply_theme.py nov24_workshop.html

The script is safe to run twice. For each page it
  1. removes the Google Fonts request,
  2. points every font to a variable set in theme.css,
  3. points stray hard-coded colors to a variable set in theme.css,
  4. marks the page light-only and, for a dated page, marks its day,
  5. links theme.css after the page's own <style> block.
Every variable keeps the page's old value as a fallback, so a page still
renders if theme.css fails to load. Page content is never touched.
"""
import datetime, glob, os, re, sys

YEAR = 2026
SKIP = {'writing_framework.html'}          # already in the register, has its own tokens
LINK = '<link rel="stylesheet" href="theme.css">'

FONTS = [  # (pattern on the family list, variable)
    (r"'Playfair Display'[^;}\"]*", '--font-head'),
    (r"'Spectral'[^;}\"]*", '--font-head'),
    (r"'Source Serif 4'[^;}\"]*", '--font-body'),
    (r"'IBM Plex Sans'[^;}\"]*", '--font-body'),
    (r"'DM Mono'[^;}\"]*", '--font-label'),
    (r"'IBM Plex Mono'[^;}\"]*", '--font-label'),
]
COLORS = {
    '--h-tint': ['#F2EFE9', '#EEF0F2', '#F5F4F1'],
    '--h-white': ['#FFF6F4', '#FFFCFA', '#FFE4B5'],
    '--h-mist': ['#E8A000', '#FFF3C4'],
    '--h-umber': ['#1C1410', '#C0392B', '#C44', '#12362A'],
    '--h-dusk': ['#B85A2C'],
    '--h-rule': ['#E8C4A8', '#D9D0E8', '#D0D9EF', '#C8BCE8', '#EAC8A8', '#C5DDD0',
                 '#E8D8B8', '#D8CCE8', '#C9C0E8', '#B0D9C0', '#E8A882', '#E8D4CB'],
    '--h-rule-dark': ['#2E231C'],
    '--sidebar-muted': ['#4A3A2E'],
}
HEX = {h.upper(): var for var, hs in COLORS.items() for h in hs}
HEX_RE = re.compile(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')
DONE_RE = re.compile(r'(var\(--[\w-]+,[^()]*(?:\([^()]*\))?[^()]*\))')   # a value this script already wrote
MONTHS = {'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}


def restyle_css(css):
    out = []
    for line in css.split('\n'):
        if re.match(r'\s*--[\w-]+\s*:', line):      # a variable definition: leave it
            out.append(line)
            continue
        for pat, var in FONTS:
            line = re.sub(r'(font-family\s*:\s*)(' + pat + r')',
                          lambda m: f"{m.group(1)}var({var}, {m.group(2).strip()})", line)
        # text on a dark band is solid white, and a pill on a dark band darkens the band
        line = re.sub(r'(?<![\w-])(color\s*:\s*)(rgba\(255,\s*255,\s*255,\s*0?\.\d+\))',
                      r'\1var(--h-on-dark, \2)', line)
        line = re.sub(r'(?<![\w-])(background(?:-color)?\s*:\s*)(rgba\(255,\s*255,\s*255,\s*0?\.[1-3]\d*\))',
                      r'\1var(--h-pill, \2)', line)
        parts = DONE_RE.split(line)
        for i in range(0, len(parts), 2):
            parts[i] = HEX_RE.sub(lambda m: f"var({HEX[m.group(0).upper()]}, {m.group(0)})"
                                  if m.group(0).upper() in HEX else m.group(0), parts[i])
        line = ''.join(parts)
        out.append(line)
    return '\n'.join(out)


def restyle(html, name):
    # 1. fonts are system fonts now
    html = re.sub(r'[ \t]*<link[^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>[ \t]*\n?', '', html)
    # 2 and 3. style blocks and style attributes
    html = re.sub(r'(<style[^>]*>)(.*?)(</style>)',
                  lambda m: m.group(1) + restyle_css(m.group(2)) + m.group(3), html, flags=re.S)
    html = re.sub(r'style="([^"]*)"', lambda m: 'style="' + restyle_css(m.group(1)).replace('"', "'") + '"', html)
    # 4. light only, and the day
    attrs = ' data-theme="light"'
    m = re.match(r'([a-z]{3})(\d\d)_', name)
    if m and m.group(1) in MONTHS:
        day = datetime.date(YEAR, MONTHS[m.group(1)], int(m.group(2))).weekday()
        attrs += ' data-day="%s"' % {1: 'tue', 3: 'thu'}.get(day, 'tue')
    if 'data-theme=' not in html.split('>', 2)[1] + html.split('>', 3)[2]:
        html = re.sub(r'<html\b([^>]*)>', lambda m: '<html' + m.group(1) + attrs + '>', html, count=1)
    # 5. the link
    if LINK not in html:
        if '</head>' in html:
            html = html.replace('</head>', LINK + '\n</head>', 1)
        else:                                   # a page with no </head>: after its last style block
            i = html.rfind('</style>') + len('</style>')
            html = html[:i] + '\n' + LINK + html[i:]
    return html


def main():
    pages = sys.argv[1:] or sorted(glob.glob('*.html'))
    for p in pages:
        if os.path.basename(p) in SKIP:
            continue
        old = open(p, encoding='utf-8').read()
        new = restyle(old, os.path.basename(p))
        if new != old:
            open(p, 'w', encoding='utf-8').write(new)
            print('updated', p)
        else:
            print('no change', p)


if __name__ == '__main__':
    main()
