from pathlib import Path
from runpy import run_path
from shutil import copy2

import pytest
from pypdf import PdfReader, PdfWriter

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/build_submission.py"
_append_signed_declaration = run_path(str(SCRIPT_PATH))["_append_signed_declaration"]


def test_signed_declaration_replaces_placeholder_page(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    appendix = tmp_path / "appendix.pdf"
    copy2(root / "appendix/appendix.pdf", appendix)
    declaration = tmp_path / "signed.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=595.28, height=841.89)
    with declaration.open("wb") as handle:
        writer.write(handle)

    _append_signed_declaration(appendix, declaration)

    result = PdfReader(appendix)
    assert len(result.pages) == 8
    text = "\n".join(page.extract_text() or "" for page in result.pages)
    assert "unsigned placeholder" not in text.lower()


def test_signed_declaration_must_exist(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="signed declaration not found"):
        _append_signed_declaration(tmp_path / "appendix.pdf", tmp_path / "missing.pdf")
