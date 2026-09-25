"""Convert the approved Markdown wording into a small, reproducible TeX input."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/poster_variation_1_text_draft.md"
TARGET = ROOT / "poster/approved_copy.tex"
INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*)")


def escape_plain(value: str) -> str:
    value = value.replace("\u201c", "``").replace("\u201d", "''").replace("\u2019", "'")
    value = value.replace("\u2013", "--").replace("\u2014", "---")
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return re.sub(r"[\\&%$#_{}]", lambda match: replacements[match.group()], value)


def inline_tex(value: str) -> str:
    parts: list[str] = []
    for piece in INLINE.split(value):
        if piece.startswith("**") and piece.endswith("**"):
            parts.append(r"\textbf{" + escape_plain(piece[2:-2]) + "}")
        elif piece.startswith("*") and piece.endswith("*"):
            parts.append(r"\emph{" + escape_plain(piece[1:-1]) + "}")
        else:
            parts.append(escape_plain(piece))
    return "".join(parts)


def render(source: str) -> str:
    output = ["% Generated from docs/poster_variation_1_text_draft.md. Do not edit by hand."]
    for block in re.split(r"\n\s*\n", source.strip()):
        block = " ".join(line.strip() for line in block.splitlines())
        if block.startswith("# "):
            continue  # The title belongs to the poster header.
        if block.startswith("## "):
            title = block[3:]
            output.append(r"\PosterSection{" + inline_tex(title) + "}")
            if title == "Results":
                output.append(r"\PosterAccuracyChart")
        elif block.startswith("### "):
            output.append(r"\PosterSubsection{" + inline_tex(block[4:]) + "}")
        else:
            output.append(inline_tex(block) + r"\par")
    return "\n\n".join(output) + "\n"


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    rendered = render(source)
    TARGET.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"Rendered {TARGET} from {SOURCE}")


if __name__ == "__main__":
    main()
