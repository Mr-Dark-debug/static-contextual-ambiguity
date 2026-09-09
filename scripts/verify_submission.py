"""Fail closed unless the staged submission PDFs satisfy the release gates."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import DictionaryObject

A1_POINTS = (1683.78, 2383.94)
A4_POINTS = (595.28, 841.89)
EXPECTED_FILES = {"appendix.pdf", "poster.pdf"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _walk_resource_fonts(resources: DictionaryObject) -> Iterator[DictionaryObject]:
    """Yield font dictionaries, including fonts nested in imported PDF figures."""
    fonts = resources.get("/Font")
    if fonts:
        for reference in fonts.get_object().values():
            yield reference.get_object()
    xobjects = resources.get("/XObject")
    if xobjects:
        for reference in xobjects.get_object().values():
            xobject = reference.get_object()
            nested = xobject.get("/Resources")
            if nested:
                yield from _walk_resource_fonts(nested.get_object())


def _font_is_embedded(font: DictionaryObject) -> bool:
    # Matplotlib's PDF backend embeds glyph outlines as Type 3 CharProcs rather
    # than attaching a FontFile stream to the descriptor.
    if font.get("/Subtype") == "/Type3" and font.get("/CharProcs"):
        return True
    candidates = [font]
    descendants = font.get("/DescendantFonts")
    if descendants:
        candidates.extend(ref.get_object() for ref in descendants.get_object())
    for candidate in candidates:
        descriptor = candidate.get("/FontDescriptor")
        if descriptor:
            descriptor = descriptor.get_object()
            if any(descriptor.get(key) for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                return True
    return False


def _assert_size(page: object, expected: tuple[float, float], label: str) -> None:
    actual = (float(page.mediabox.width), float(page.mediabox.height))
    if any(
        abs(measured - required) > 0.1
        for measured, required in zip(actual, expected, strict=True)
    ):
        raise RuntimeError(f"{label} has page size {actual}, expected {expected} points")


def _verify_fonts(reader: PdfReader, label: str) -> int:
    fonts: dict[str, bool] = {}
    for page in reader.pages:
        resources = page.get("/Resources")
        if not resources:
            continue
        for font in _walk_resource_fonts(resources.get_object()):
            name = str(font.get("/BaseFont", "unnamed font"))
            fonts[name] = fonts.get(name, False) or _font_is_embedded(font)
    missing = sorted(name for name, embedded in fonts.items() if not embedded)
    if missing:
        raise RuntimeError(f"{label} contains non-embedded fonts: {missing}")
    if not fonts:
        raise RuntimeError(f"{label} exposes no fonts for verification")
    return len(fonts)


def _verify_text(reader: PdfReader, required: tuple[str, ...], label: str) -> int:
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    missing = [heading for heading in required if heading not in text]
    if missing:
        raise RuntimeError(f"{label} is missing extractable text: {missing}")
    return len(text)


def verify(root: Path) -> None:
    submission = root / "submission"
    actual = {path.name for path in submission.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        expected = sorted(EXPECTED_FILES)
        raise RuntimeError(f"submission must contain exactly {expected}: {sorted(actual)}")

    source_paths = {
        "poster.pdf": root / "poster/poster.pdf",
        "appendix.pdf": root / "appendix/appendix.pdf",
    }
    for name, source in source_paths.items():
        staged = submission / name
        if _sha256(source) != _sha256(staged):
            raise RuntimeError(f"{name} differs from its built source")

    poster = PdfReader(submission / "poster.pdf")
    if len(poster.pages) != 1:
        raise RuntimeError(f"poster must have one page, found {len(poster.pages)}")
    _assert_size(poster.pages[0], A1_POINTS, "poster")
    poster_chars = _verify_text(
        poster,
        ("Hypothesis", "Methodology", "Results", "Limitations", "Conclusion"),
        "poster",
    )
    poster_fonts = _verify_fonts(poster, "poster")

    appendix = PdfReader(submission / "appendix.pdf")
    if len(appendix.pages) != 8:
        raise RuntimeError(f"appendix must have eight pages, found {len(appendix.pages)}")
    for index, page in enumerate(appendix.pages, start=1):
        _assert_size(page, A4_POINTS, f"appendix page {index}")
    appendix_chars = _verify_text(
        appendix,
        (
            "Method and Results Appendix",
            "Primary validation results",
            "References",
            "unsigned placeholder",
        ),
        "appendix",
    )
    appendix_fonts = _verify_fonts(appendix, "appendix")

    print(
        "Submission verified: exactly two PDFs; poster=1 A1 page, "
        f"{poster_fonts} embedded fonts, {poster_chars} text characters; appendix=8 A4 "
        f"pages, {appendix_fonts} embedded fonts, {appendix_chars} text characters."
    )


def main() -> None:
    verify(Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    main()
