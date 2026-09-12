# University of Trier logo

`university-trier.svg` is the unmodified official artwork downloaded from the
university's public website on 2026-09-13:

https://www.uni-trier.de/typo3conf/ext/zimktheme_unitrier/Resources/Public/Logos/Logo_Universitaet.svg

`university-trier.pdf` is a vector conversion for LaTeX. The poster preserves the
artwork's colors and aspect ratio, on a white background with clear space.

Reproduce the conversion from the repository root:

```powershell
uv run --with svglib --with reportlab python scripts/convert_poster_logo.py
```

The conversion verifies that the artwork contains only vector paths and removes
unused fallback font resources inserted by the converter. No visible geometry,
color or typography is altered.

The university owns the logo. Its detailed student corporate-design guidance
requires access through the campus network or VPN. No claim of certification
against that inaccessible manual is made.
