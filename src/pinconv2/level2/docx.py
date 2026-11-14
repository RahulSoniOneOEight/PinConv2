"""Minimal, dependency-free DOCX writer.

The review pack and the budget estimate need to reach a human who does not read
JSON. This writer produces a valid OOXML document with headings, paragraphs,
bullet lists and tables, using only the standard library.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

_DOC_HEAD = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
"""
_DOC_TAIL = """    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
    </w:sectPr>
  </w:body>
</w:document>
"""


def _run(text: str, *, bold: bool = False, size: int | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if size is not None:
        props.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    prop_xml = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f'<w:r>{prop_xml}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


@dataclass
class DocxBuilder:
    parts: list[str] = field(default_factory=list)

    def heading(self, text: str, level: int = 1) -> None:
        size = {1: 36, 2: 28, 3: 24}.get(level, 22)
        self.parts.append(
            f'<w:p><w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr>'
            f"{_run(text, bold=True, size=size)}</w:p>"
        )

    def paragraph(self, text: str, *, bold: bool = False) -> None:
        self.parts.append(f"<w:p>{_run(text, bold=bold)}</w:p>")

    def bullet(self, text: str) -> None:
        self.parts.append(f'<w:p><w:pPr><w:ind w:left="360"/></w:pPr>{_run("• " + text)}</w:p>')

    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        grid = "".join('<w:gridCol w:w="1400"/>' for _ in headers)
        border = "".join(
            f'<w:{edge} w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
            for edge in ("top", "left", "bottom", "right", "insideH", "insideV")
        )
        cells = "".join(
            f'<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/></w:tcPr>'
            f"<w:p>{_run(header, bold=True)}</w:p></w:tc>"
            for header in headers
        )
        body = [
            f"<w:tbl><w:tblPr><w:tblBorders>{border}</w:tblBorders></w:tblPr>"
            f"<w:tblGrid>{grid}</w:tblGrid>"
            f"<w:tr>{cells}</w:tr>"
        ]
        for row in rows:
            row_cells = "".join(
                f'<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/></w:tcPr>'
                f"<w:p>{_run(cell)}</w:p></w:tc>"
                for cell in row
            )
            body.append(f"<w:tr>{row_cells}</w:tr>")
        body.append("</w:tbl>")
        self.parts.append("".join(body))
        self.parts.append("<w:p/>")

    def page_break(self) -> None:
        self.parts.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    def save(self, path: Path) -> Path:
        document = _DOC_HEAD + "".join(self.parts) + _DOC_TAIL
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            entries = {
                "[Content_Types].xml": _CONTENT_TYPES,
                "_rels/.rels": _RELS,
                "word/document.xml": document,
            }
            for name, payload in entries.items():
                info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, payload)
        return path
