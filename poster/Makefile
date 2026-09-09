TECTONIC ?= tectonic

all: poster.pdf

poster.pdf: poster.tex generated_results.tex ../figures/model_comparison.pdf ../figures/similarity_distributions.pdf ../figures/layer_analysis.pdf ../figures/qualitative_cases.pdf
	$(TECTONIC) -X compile --outdir . --outfmt pdf --print --untrusted poster.tex

clean:
	$(RM) poster.pdf poster.log poster.aux poster.xdv

