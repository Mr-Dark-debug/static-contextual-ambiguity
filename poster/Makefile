TECTONIC ?= tectonic
PDFTOPPM ?= pdftoppm

.PHONY: all poster preview clean

all: poster preview

poster: poster.pdf

preview: preview.png

poster.pdf: poster.tex authors.tex generated_results.tex assets/university-trier.pdf ../figures/poster_accuracy.pdf
	$(TECTONIC) -X compile --outdir . --outfmt pdf --print --untrusted poster.tex

preview.png: poster.pdf
	$(PDFTOPPM) -png -r 150 -singlefile poster.pdf preview

clean:
	$(RM) poster.pdf preview.png poster.log poster.aux poster.xdv
