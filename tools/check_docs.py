"""Documentation checks run in CI; standard library only.

1. Every relative Markdown link in the repo points to an existing file, and every
   #anchor into a Markdown file matches a heading in that file.
2. Every DAX measure defined in a .dax file is listed on the KPI wiki page with a
   `### <Measure name>` heading, its DAX code matches the source, and the page
   lists no measure that does not exist.

External http(s) links are NOT fetched (that would make CI depend on other sites).

Usage: python tools/check_docs.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KPI_PAGE = ROOT / "docs" / "wiki" / "KPI-Definitions.md"
SKIP_DIRS = {".git", ".venv", ".test-deps", "node_modules", ".pytest_cache"}

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|!\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# A top-level DAX definition: "Name =" starting in column 0 (not a comment or VAR).
DEF_RE = re.compile(r"^(?!VAR\b|RETURN\b)([A-Za-z][A-Za-z0-9 %_.\-]*?)\s*=(?!=)")


def markdown_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md")
                  if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts))


def strip_code(text: str) -> list[str]:
    """Return lines outside fenced code blocks, with inline code removed."""
    lines, fenced = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line.strip()):
            fenced = not fenced
            lines.append("")
            continue
        lines.append("" if fenced else re.sub(r"`[^`]*`", "", line))
    return lines


def slug(heading: str) -> str:
    """Approximate GitHub's heading anchor algorithm."""
    text = re.sub(r"<[^>]+>", "", heading)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower().replace("`", "")
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    found, counts, fenced = set(), {}, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE_RE.match(line.strip()):
            fenced = not fenced
            continue
        match = None if fenced else HEADING_RE.match(line)
        if match:
            base = slug(match.group(2))
            n = counts.get(base, 0)
            counts[base] = n + 1
            found.add(base if n == 0 else f"{base}-{n}")
    return found


def check_links() -> list[str]:
    errors = []
    for md in markdown_files():
        rel_md = md.relative_to(ROOT)
        for lineno, line in enumerate(strip_code(md.read_text(encoding="utf-8")), 1):
            for match in LINK_RE.finditer(line):
                target = match.group(1) or match.group(2)
                if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):  # http:, mailto:, etc.
                    continue
                path_part, _, anchor = target.partition("#")
                dest = md if not path_part else (md.parent / path_part).resolve()
                where = f"{rel_md}:{lineno}: {target}"
                if not dest.exists():
                    errors.append(f"{where} -> missing file")
                elif anchor and dest.suffix == ".md" and anchor.lower() not in anchors(dest):
                    errors.append(f"{where} -> no heading for #{anchor}")
    return errors


def dax_measures() -> dict[str, str]:
    """Map measure name -> normalized definition, from every .dax file in the repo."""
    measures = {}
    for dax in sorted(ROOT.rglob("*.dax")):
        if SKIP_DIRS.intersection(dax.relative_to(ROOT).parts):
            continue
        text = dax.read_text(encoding="utf-8")
        if re.search(r"^//.*New table", text, re.M):  # calculated table, e.g. Date.dax
            continue
        current = None
        for line in text.splitlines():
            match = DEF_RE.match(line)
            if match:
                current = match.group(1).strip()
                measures[current] = [line]
            elif current and line.strip() and not line.startswith("//"):
                measures[current].append(line)
    return {name: " ".join(" ".join(body).split()) for name, body in measures.items()}


def check_kpi_page() -> list[str]:
    if not KPI_PAGE.exists():
        return [f"{KPI_PAGE.relative_to(ROOT)} does not exist"]
    text = KPI_PAGE.read_text(encoding="utf-8")
    headings = {m.group(1).strip() for m in re.finditer(r"^###\s+(.+?)\s*$", text, re.M)}
    code_lines = [line for block in re.findall(r"```dax\n(.*?)```", text, re.S)
                  for line in block.splitlines() if not line.lstrip().startswith("//")]
    page_code = " ".join(" ".join(code_lines).split())
    measures = dax_measures()
    errors = []
    if not measures:
        errors.append("no DAX measures found in any .dax file")
    for name, definition in measures.items():
        if name not in headings:
            errors.append(f"measure '{name}' has no '### {name}' heading on the KPI page")
        elif definition not in page_code:
            errors.append(f"measure '{name}': DAX on the KPI page differs from the .dax source")
    for heading in sorted(headings - measures.keys()):
        errors.append(f"KPI page heading '### {heading}' is not a measure in any .dax file")
    return errors


def main() -> int:
    link_errors, kpi_errors = check_links(), check_kpi_page()
    print(f"Markdown files checked: {len(markdown_files())}")
    print(f"DAX measures found: {len(dax_measures())}")
    for error in link_errors + kpi_errors:
        print(f"ERROR {error}")
    if link_errors or kpi_errors:
        print(f"FAIL: {len(link_errors)} link error(s), {len(kpi_errors)} KPI page error(s)")
        return 1
    print("PASS: relative links/anchors resolve; every DAX measure is on the KPI page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
