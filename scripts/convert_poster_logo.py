"""Convert the official path-only SVG logo to a font-free vector PDF.

Run with: uv run --with svglib --with reportlab python scripts/convert_poster_logo.py
"""

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, NameObject
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg


def main() -> None:
    assets = Path(__file__).resolve().parents[1] / "poster/assets"
    drawing = svg2rlg(str(assets / "university-trier.svg"))
    raw = BytesIO(renderPDF.drawToString(drawing))
    reader = PdfReader(raw)
    page = reader.pages[0]
    content = ContentStream(page.get_contents(), reader)
    # ReportLab adds unused Times-Roman state to path-only SVG conversions.
    # Assert that no text is painted before removing empty text objects/fonts.
    if any(operator in {b"Tj", b"TJ", b"'", b'"'} for _, operator in content.operations):
        raise ValueError("logo contains painted text and needs font embedding")
    filtered = []
    in_text = False
    for operands, operator in content.operations:
        if operator == b"BT":
            in_text = True
        elif operator == b"ET":
            in_text = False
        elif not in_text:
            filtered.append((operands, operator))
    content.operations = filtered
    page[NameObject("/Contents")] = content
    page["/Resources"].pop("/Font", None)
    writer = PdfWriter()
    writer.add_page(page)
    writer.add_metadata(
        {"/Title": "Universitaet Trier - official logo", "/Creator": "SVG vector conversion"}
    )
    with (assets / "university-trier.pdf").open("wb") as handle:
        writer.write(handle)


if __name__ == "__main__":
    main()
