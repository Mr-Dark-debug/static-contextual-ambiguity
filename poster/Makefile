TECTONIC ?= tectonic
PDFTOPPM ?= pdftoppm

.PHONY: all poster preview clean

all: poster preview

poster: poster.pdf

preview: preview.png

poster.pdf: poster.tex generated_results.tex ../figures/model_comparison.pdf ../figures/similarity_distributions.pdf ../figures/layer_analysis.pdf ../figures/qualitative_cases.pdf
	$(TECTONIC) -X compile --outdir . --outfmt pdf --print --untrusted poster.tex

preview.png: poster.pdf
	$(PDFTOPPM) -png -r 150 -singlefile poster.pdf preview

clean:
	$(RM) poster.pdf preview.png poster.log poster.aux poster.xdv
