"""Read-only checks for the documented SDD Markdown subset; no semantic verdicts."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

SKIP_DIRS = {'.git', '.build', '__pycache__', 'node_modules', '.venv'}
ID = r'(?:FR|AC|ARC|PUC|PAC|PENV)-\d+|T\d{3,}'


def visible_lines(text: str) -> tuple[list[str], int | None]:
    """Blank fenced code, YAML front matter and HTML comments, preserving line numbers."""
    lines = text.splitlines()
    output = []
    fence = None
    front = bool(lines and lines[0].strip() == '---')
    comment = False
    for number, line in enumerate(lines, 1):
        if front:
            output.append('')
            if number > 1 and line.strip() in ('---', '...'):
                front = False
            continue
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
            output.append('')
            continue
        if marker:
            fence = (marker[1][0], len(marker[1]), number)
            output.append('')
            continue
        pieces = []
        while line:
            if comment:
                end = line.find('-->')
                if end < 0:
                    break
                line = line[end + 3:]
                comment = False
            else:
                start = line.find('<!--')
                if start < 0:
                    pieces.append(line)
                    break
                pieces.append(line[:start])
                line = line[start + 4:]
                comment = True
        output.append('' if line.startswith(('    ', '\t')) else ''.join(pieces))
    return output, fence[2] if fence else (1 if front else None)


def without_code(line: str) -> str:
    return re.sub(r'(`+)(?!`)(.+?)(?<!`)\1(?!`)', lambda m: ' ' * len(m[0]), line)


def cells(line: str) -> list[str]:
    line = without_code(line).strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|') and not line.endswith('\\|'):
        line = line[:-1]
    return [part.strip() for part in re.split(r'(?<!\\)\|', line)]


def slug(title: str) -> str:
    title = re.sub(r'!?\[([^]]+)\]\([^)]*\)', r'\1', title)
    title = re.sub(r'<[^>]*>', '', title)
    title = html.unescape(title).lower()
    return ''.join(c for c in title if c in '-_ ' or unicodedata.category(c)[0] in 'LN').replace(' ', '-')


def headings(lines: list[str]):
    for i, line in enumerate(lines):
        match = re.match(r'^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$', line)
        if match:
            yield i + 1, len(match[1]), match[2]
        elif i + 1 < len(lines) and line.strip() and not line.lstrip().startswith(('#', '|', '>')):
            underline = re.fullmatch(r' {0,3}(=+|-+)\s*', lines[i + 1])
            if underline:
                yield i + 1, 1 if underline[1][0] == '=' else 2, line.strip()


def anchor_set(lines: list[str]) -> set[str]:
    generated = set()
    for _, _, title in headings(lines):
        base = slug(title)
        anchor = base
        suffix = 0
        while anchor in generated:
            suffix += 1
            anchor = f'{base}-{suffix}'
        generated.add(anchor)
    explicit = set(re.findall(r'<[^>]+\b(?:id|name)=["\']([^"\']+)["\']', '\n'.join(lines)))
    return generated | explicit


def destination(value: str) -> str | None:
    """Parse a link destination, optionally followed by a quoted title."""
    value = value.strip()
    if value.startswith('<'):
        end = value.find('>')
        return value[1:end] if end >= 0 else None
    match = re.match(r'((?:\\.|[^\s])+)(?:\s+["\'].*["\'])?$', value)
    return re.sub(r'\\([() ])', r'\1', match[1]) if match else None


def inline_links(line: str):
    """Return destinations of single-line links, balancing parentheses in paths."""
    for match in re.finditer(r'(?<!\\)!?\[(?:\\.|[^]\\])*\]\(', line):
        start = match.end()
        depth = 1
        angle = start < len(line) and line[start] == '<'
        escaped = False
        for i in range(start, len(line)):
            char = line[i]
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif angle:
                if char == '>':
                    angle = False
            elif char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0:
                    yield destination(line[start:i])
                    break
        else:
            yield None


class Checker:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.diagnostics = []
        self.cache = {}
        self.checked = []

    def issue(self, path: Path, line: int, code: str, message: str, severity='error'):
        try:
            name = path.relative_to(self.root).as_posix()
        except ValueError:
            name = str(path)
        self.diagnostics.append(dict(file=name, line=line, code=code, severity=severity, message=message))

    def inside(self, path: Path) -> bool:
        return path == self.root or self.root in path.parents

    def read(self, path: Path):
        if path not in self.cache:
            try:
                text = path.read_bytes().decode('utf-8-sig')
                if '\x00' in text:
                    raise ValueError('NUL byte in Markdown')
                self.cache[path] = visible_lines(text)
            except (OSError, UnicodeError, ValueError) as exc:
                self.issue(path, 1, 'DOC001', f'Cannot read UTF-8 Markdown: {exc}')
                self.cache[path] = None
        return self.cache[path]

    def link(self, source: Path, line: int, value: str | None):
        if value is None:
            self.issue(source, line, 'DOC006', 'Malformed or unsupported single-line link destination')
            return
        value = html.unescape(value)
        try:
            url = urlsplit(value)
        except ValueError:
            self.issue(source, line, 'DOC006', 'Malformed link destination')
            return
        if url.scheme or url.netloc:
            return  # Never access the network.
        if re.search(r'<[^>]+>|\{[^}]+\}', unquote(url.path)):
            self.issue(source, line, 'DOC010', 'Placeholder destination not checked', 'warning')
            return
        path = unquote(url.path)
        target = (source.parent / path).resolve() if path else source
        if not self.inside(target):
            self.issue(source, line, 'DOC007', 'Local link leaves --root; target not read')
        elif not target.exists():
            self.issue(source, line, 'DOC007', f'Local target does not exist: {value}')
        elif url.fragment:
            if target.suffix.lower() != '.md':
                self.issue(source, line, 'DOC010', 'Non-Markdown fragment not checked', 'warning')
            else:
                content = self.read(target)
                if content is not None and unquote(url.fragment) not in anchor_set(content[0]):
                    self.issue(source, line, 'DOC008', f'Anchor does not exist: {value}')

    def check(self, path: Path):
        self.checked.append(path.relative_to(self.root).as_posix())
        content = self.read(path)
        if content is None:
            return
        lines, unclosed = content
        if unclosed:
            self.issue(path, unclosed, 'DOC002', 'Unclosed fenced code block or YAML front matter')
        previous = 0
        definitions = {}
        for number, level, title in headings(lines):
            if previous and level > previous + 1:
                self.issue(path, number, 'DOC003', f'Heading jumps from H{previous} to H{level}', 'warning')
            previous = level
        def define(identifier, number):
            if identifier in definitions:
                self.issue(path, number, 'DOC005', f'Duplicate declaration {identifier}; first at line {definitions[identifier]}')
            else:
                definitions[identifier] = number
        refs = {}
        for number, raw in enumerate(lines, 1):
            line = without_code(raw)
            ref = re.match(r'^ {0,3}\[([^]]+)\]:\s*(.*)$', line)
            if ref:
                key = ' '.join(ref[1].split()).casefold()
                if key in refs:
                    self.issue(path, number, 'DOC009', f'Duplicate reference label: {ref[1]}')
                refs[key] = destination(ref[2])
                self.link(path, number, refs[key])
        for number, raw in enumerate(lines, 1):
            line = without_code(raw)
            declaration = re.match(rf'^\s*(?:[-*+]\s+|#{{1,6}}\s+)({ID})\s*[:：]', line)
            if declaration:
                define(declaration[1], number)
            if re.match(r'^ {0,3}\[[^]]+\]:', line):
                continue
            for value in inline_links(line):
                self.link(path, number, value)
            for ref in re.finditer(r'(?<!!)\[([^]\n]+)\]\[([^]\n]*)\]|!\[([^]\n]*)\]\[([^]\n]*)\]', line):
                label = (ref[2] or ref[1]) if ref[1] is not None else (ref[4] or ref[3])
                if ' '.join(label.split()).casefold() not in refs:
                    self.issue(path, number, 'DOC009', f'Undefined reference label: {label}')
            # Only recognize tables with an actual delimiter row, not arbitrary pipes.
            if number < 2 or not re.fullmatch(r'\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*', line):
                continue
            header = cells(lines[number - 2])
            width = len(cells(line))
            if len(header) != width:
                self.issue(path, number - 1, 'DOC004', 'Table header and delimiter have different column counts')
            declares = bool(header and header[0].casefold() == 'id' and not any(x.casefold() in ('result', 'evidence', 'snapshot') for x in header))
            for index in range(number, len(lines)):
                row = lines[index]
                if not row.strip() or '|' not in without_code(row):
                    break
                values = cells(row)
                if len(values) != width:
                    self.issue(path, index + 1, 'DOC004', f'Table expects {width} columns, found {len(values)}')
                if declares and re.fullmatch(ID, values[0]):
                    define(values[0], index + 1)

    def run(self, inputs: list[str]):
        files = set()
        for value in inputs:
            path = (self.root / value).resolve()
            if not self.inside(path) or not path.exists():
                self.issue(path, 1, 'DOC000', 'Input missing or outside --root')
                continue
            candidates = path.rglob('*.md') if path.is_dir() else [path]
            for item in candidates:
                if item.suffix.lower() != '.md':
                    self.issue(item, 1, 'DOC000', 'Input must be Markdown or a directory')
                    continue
                if any(part in SKIP_DIRS for part in item.relative_to(self.root).parts):
                    continue
                resolved = item.resolve()
                if not self.inside(resolved):
                    self.issue(item, 1, 'DOC000', 'Symlink target leaves --root')
                else:
                    files.add(resolved)
        if not files and not self.diagnostics:
            self.issue(self.root, 1, 'DOC000', 'No Markdown files selected')
        for path in sorted(files):
            self.check(path)
        self.diagnostics.sort(key=lambda x: (x['file'], x['line'], x['code']))
        return {'schema_version': 1, 'scope': 'mechanical_only', 'files': self.checked,
                'diagnostics': self.diagnostics,
                'errors': sum(x['severity'] == 'error' for x in self.diagnostics),
                'warnings': sum(x['severity'] == 'warning' for x in self.diagnostics)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Project root; paths resolve relative to it')
    parser.add_argument('--format', choices=('text', 'json'), default='text')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as a nonzero result too')
    parser.add_argument('paths', nargs='+', help='Explicit Markdown files or directories to check')
    args = parser.parse_args(argv)
    result = Checker(args.root).run(args.paths)
    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in result['diagnostics']:
            print(f"{item['file']}:{item['line']}: {item['severity']} {item['code']}: {item['message']}")
        print(f"Checked {len(result['files'])} Markdown files: {result['errors']} errors, {result['warnings']} warnings (mechanical only)")
    return 1 if result['errors'] or (args.strict and result['warnings']) else 0


if __name__ == '__main__':
    sys.exit(main())
