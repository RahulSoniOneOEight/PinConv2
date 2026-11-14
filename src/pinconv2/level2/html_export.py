"""Small Markdown-to-HTML renderer for review documents.

The DOCX is the formal handoff, but reviewers often need a file that opens in
any browser without Office. This renders the same Markdown into a standalone
HTML page with tables, headings, lists and links.
"""

from __future__ import annotations

import html
import re

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_CODE = re.compile(r"`([^`]+)`")


def _inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = _LINK.sub(r'<a href="\2">\1</a>', escaped)
    escaped = _BOLD.sub(r"<strong>\1</strong>", escaped)
    escaped = _CODE.sub(r"<code>\1</code>", escaped)
    return escaped


def _is_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(set(cell) <= {"-", ":"} and cell for cell in cells)


def markdown_to_html(markdown: str, title: str) -> str:
    lines = markdown.splitlines()
    parts: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("```"):
            index += 1
            code: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            index += 1
            parts.append(f"<pre><code>{html.escape(chr(10).join(code))}</code></pre>")
            continue
        if stripped.startswith("|"):
            rows: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(lines[index].strip())
                index += 1
            table_rows = [row for row in rows if not _is_separator(row)]
            if table_rows:
                parts.append("<table>")
                for row_index, row in enumerate(table_rows):
                    cells = [cell.strip() for cell in row.strip("|").split("|")]
                    tag = "th" if row_index == 0 else "td"
                    parts.append(
                        "<tr>"
                        + "".join(f"<{tag}>{_inline(cell)}</{tag}>" for cell in cells)
                        + "</tr>"
                    )
                parts.append("</table>")
            continue
        if stripped.startswith("#"):
            level = min(len(stripped) - len(stripped.lstrip("#")), 4)
            text = stripped[level:].strip()
            parts.append(f"<h{level}>{_inline(text)}</h{level}>")
            index += 1
            continue
        if stripped.startswith(("- ", "* ")):
            parts.append("<ul>")
            while index < len(lines) and lines[index].strip().startswith(("- ", "* ")):
                parts.append(f"<li>{_inline(lines[index].strip()[2:])}</li>")
                index += 1
            parts.append("</ul>")
            continue
        parts.append(f"<p>{_inline(stripped)}</p>")
        index += 1

    body = "\n".join(parts)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  body {{ font-family: Inter, Segoe UI, system-ui, sans-serif; max-width: 1100px;
         margin: 40px auto; padding: 0 24px; color: #1c1c1c; line-height: 1.55; }}
  h1 {{ border-bottom: 2px solid #c98a55; padding-bottom: 8px; }}
  h2 {{ margin-top: 32px; color: #5a2e1a; }}
  h3 {{ margin-top: 24px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 14px; }}
  th, td {{ border: 1px solid #d8d2c8; padding: 8px 10px; text-align: left;
            vertical-align: top; }}
  th {{ background: #f7f3ec; }}
  code {{ background: #f2eee8; padding: 2px 5px; border-radius: 4px; }}
  pre {{ background: #f7f3ec; padding: 14px; overflow-x: auto; }}
  a {{ color: #8a4b2a; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""
