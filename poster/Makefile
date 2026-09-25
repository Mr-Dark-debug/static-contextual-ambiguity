TECTONIC ?= tectonic
PDFTOPPM ?= pdftoppm

.PHONY: all poster preview clean

all: poster preview

poster: poster.pdf

preview: preview.png

approved_copy.tex: ../docs/poster_variation_1_text_draft.md ../scripts/render_poster_copy.py
	uv run python ../scripts/render_poster_copy.py

poster.pdf: poster.tex authors.tex generated_results.tex approved_copy.tex assets/university-trier.pdf
	$(TECTONIC) -X compile --outdir . --outfmt pdf --print --untrusted poster.tex

preview.png: poster.pdf
	$(PDFTOPPM) -png -r 150 -singlefile poster.pdf preview

clean:
	$(RM) poster.pdf preview.png poster.log poster.aux poster.xdv
