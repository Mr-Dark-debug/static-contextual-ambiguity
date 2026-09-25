"""Compile the two active comparison posters without changing the canonical submission."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

VARIATIONS = {
    "poster_variation_1_standard.tex": "poster_variation_1_standard.pdf",
    "poster_variation_2_questions.tex": "poster_variation_2_questions.pdf",
}


def _find_tectonic(explicit: Path | None = None) -> Path:
    if explicit is not None:
        candidate = explicit.resolve()
        if candidate.is_file():
            return candidate
        raise RuntimeError(f"Tectonic executable not found: {candidate}")
    on_path = shutil.which("tectonic")
    if on_path:
        return Path(on_path).resolve()
    plugin_root = Path.home() / ".codex/plugins/cache/openai-bundled/latex"
    candidates = sorted(plugin_root.glob("*/bin/tectonic.exe"), reverse=True)
    if candidates:
        return candidates[0].resolve()
    raise RuntimeError("Tectonic executable not found; pass --tectonic explicitly")


def build_variations(root: Path, tectonic: Path) -> tuple[Path, ...]:
    root = root.resolve()
    source_dir = root / "poster/variations"
    build_dir = root / "tmp/poster_variations/build"
    output_dir = root / "output/pdf"
    build_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    expected_output_dir = (root / "output/pdf").resolve()
    if output_dir.resolve() != expected_output_dir:
        raise RuntimeError("refusing to clean an unexpected output directory")
    for stale in output_dir.glob("*.pdf"):
        if stale.name not in VARIATIONS.values():
            stale.unlink()

    built: list[Path] = []
    for source_name, output_name in VARIATIONS.items():
        source = source_dir / source_name
        if not source.is_file():
            raise RuntimeError(f"poster source not found: {source}")
        subprocess.run(
            [
                str(tectonic),
                "-X",
                "compile",
                "--outdir",
                str(build_dir),
                "--outfmt",
                "pdf",
                "--print",
                "--untrusted",
                source.name,
            ],
            cwd=source_dir,
            check=True,
        )
        compiled = build_dir / output_name
        if not compiled.is_file():
            raise RuntimeError(f"Tectonic did not create {compiled}")
        destination = output_dir / output_name
        shutil.copy2(compiled, destination)
        built.append(destination)
    return tuple(built)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tectonic", type=Path, help="path to tectonic executable")
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    tectonic = _find_tectonic(arguments.tectonic)
    built = build_variations(root, tectonic)
    print("Built poster variations:")
    for path in built:
        print(f"- {path}")


if __name__ == "__main__":
    main()
