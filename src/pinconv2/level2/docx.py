"""Standard DOCX writer built on python-docx.

The earlier hand-rolled OOXML package was structurally valid but minimal: some
Word versions refuse a package without the usual styles, properties and
relationships. This writer emits a normal Word document instead, and the review
pack also gets an HTML twin for viewers that cannot open DOCX.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.document import Document as DocumentType


class DocxBuilder:
    def __init__(self) -> None:
        self.document: DocumentType = Document()

    def heading(self, text: str, level: int = 1) -> None:
        self.document.add_heading(text, level=level)

    def paragraph(self, text: str, *, bold: bool = False) -> None:
        paragraph = self.document.add_paragraph()
        run = paragraph.add_run(text)
        run.bold = bold

    def bullet(self, text: str) -> None:
        self.document.add_paragraph(text, style="List Bullet")

    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        table = self.document.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        header_cells = table.rows[0].cells
        for index, header in enumerate(headers):
            header_cells[index].text = header
            for paragraph in header_cells[index].paragraphs:
                for run in paragraph.runs:
                    run.bold = True
        for row in rows:
            cells = table.add_row().cells
            for index, value in enumerate(row):
                if index < len(cells):
                    cells[index].text = value

    def page_break(self) -> None:
        self.document.add_page_break()  # type: ignore[no-untyped-call]

    def save(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.document.save(str(path))
        return path
