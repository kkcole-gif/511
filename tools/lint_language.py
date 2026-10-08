#!/usr/bin/env python3
"""List wording on a page to check against the ENG 511 writing rules.

    python3 tools/lint_language.py preview/perusall.html [more pages]

Reads only the words a reader sees (and, on the schedule page, the text held
in its script). Reports em dashes, semicolons, words on the avoid list, and
contrast frames. A hit inside a quotation or a title is fine: the tool does
not know the difference, so a person or an editor decides.
"""
import re, sys
from html.parser import HTMLParser

AVOID = ("can may just that very really literally actually certainly probably basically could maybe delve "
         "embark enlightening esteemed craft crafting imagine realm game-changer unlock discover skyrocket abyss "
         "revolutionize disruptive utilize tapestry illuminate unveil pivotal intricate elucidate hence furthermore "
         "however harness exciting groundbreaking cutting-edge remarkable navigating landscape testament moreover "
         "boost powerful inquiries ever-evolving").split()
PHRASES = ["shed light", "dive deep", "remains to be seen", "in summary", "in conclusion"]
FLAG = ["significant", "increasingly", "consequences", "parameter"]
CONTRAST = [r"\bnot (?:just|only|merely|simply)\b", r"\brather than\b", r", not \w", r"\bnot \w+(?: \w+){0,4},? but\b",
            r"\b(?:isn't|aren't|is not|are not) [^.?!]{0,40}[.;:] (?:It|They|This)(?:'s| is| are)\b"]


class Text(HTMLParser):
    def __init__(self, scripts):
        super().__init__(convert_charrefs=True)
        self.skip = None; self.scripts = scripts; self.out = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip = tag
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = None
    def handle_data(self, data):
        line = self.getpos()[0]
        if self.skip == 'style': return
        if self.skip == 'script':
            if self.scripts:
                for i, row in enumerate(data.split('\n')):
                    code = re.search(r'function |=>|document\.|const |let |var |return |\bif \(', row)
                    if re.search(r'["\'`]', row) and not row.strip().startswith('//') and not code:
                        self.out.append((line + i, row.strip()))
            return
        if data.strip():
            for i, row in enumerate(data.split('\n')):
                if row.strip(): self.out.append((line + i, row.strip()))


def hits(text):
    found = []
    for m in re.finditer('—', text): found.append(('em dash', m))
    for m in re.finditer(r'(?<!&nbsp)(?<!&amp)(?<!&\w\w\w)(?<!&\w\w)(?<!&\w\w\w\w\w);(?=\s+\w)', text): found.append(('semicolon', m))
    for w in AVOID:
        flags = 0 if w == 'may' else re.I
        for m in re.finditer(r'(?<![\w-])%s(?![\w-])' % re.escape(w), text, flags): found.append(('avoid: ' + w, m))
    for p in PHRASES:
        for m in re.finditer(re.escape(p), text, re.I): found.append(('avoid: ' + p, m))
    for w in FLAG:
        for m in re.finditer(r'\b%s\b' % w, text, re.I): found.append(('check: ' + w, m))
    for p in CONTRAST:
        for m in re.finditer(p, text, re.I): found.append(('contrast frame?', m))
    return found


def main():
    total = 0
    for path in sys.argv[1:]:
        parser = Text(scripts=path.endswith('index.html'))
        parser.feed(open(path, encoding='utf-8').read())
        n = 0
        for line, text in parser.out:
            for kind, m in hits(text):
                a, b = max(0, m.start() - 60), min(len(text), m.end() + 60)
                print(f"{path}:{line}: {kind:18s} | ...{text[a:m.start()]}[[{m.group(0)}]]{text[m.end():b]}...")
                n += 1
        print(f"{path}: {n} to check\n"); total += n
    return 0


if __name__ == '__main__':
    sys.exit(main())
