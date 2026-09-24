# Three Poster Variations: Design Specification

## Objective

Create three separate A1 portrait research posters from the supplied content structures. Each poster must explain lexical ambiguity before presenting the experiment, preserve the verified experimental record, and remain readable at poster scale.

The existing poster and the two canonical submission files remain unchanged. The new posters are comparison candidates, not replacements for `submission/poster.pdf`.

## Shared factual foundation

All three posters use the same verified project evidence:

- SuperGLUE WiC: 5,428 training pairs, 638 validation pairs, and 1,400 public test pairs without public labels.
- GloVe target diagnostic: 50.0% accuracy, 0.333 macro F1, and 0.500 ROC-AUC.
- GloVe context with a selected window of plus or minus two words: 55.5% accuracy, 0.551 macro F1, and 0.580 ROC-AUC.
- Frozen BERT target representation using the mean of the last four layers: 67.1% accuracy, 0.667 macro F1, and 0.716 ROC-AUC.
- BERT improvement over GloVe context: 11.6 percentage points, with a paired 95% bootstrap interval of 6.6 to 16.9 points from 1,000 resamples.
- Paired outcomes: BERT alone correct on 178 pairs, GloVe context alone correct on 104 pairs, and both wrong on 106 pairs.
- BERT made 210 errors on the 638 validation pairs.

No result may be typed independently into the poster source when a generated result macro is available. The generated values remain traceable to committed result artifacts.

## Shared identity and visual system

Each poster will use:

- A1 portrait dimensions.
- A white background, dark navy text, Trier blue accents, and restrained orange highlights.
- The official University Trier vector logo.
- A centered title block.
- Choudhary Prashant Santosh (1910474) and Rahul Khunt (1911272), centered beneath the title.
- University of Trier, MSc Natural Language Processing, and the course name.
- Large sans-serif type, clear section hierarchy, generous whitespace, and no dense card grid.
- The existing verified accuracy chart where it supports the narrative.
- One short scope or limitation statement integrated into the conclusion rather than a separate limitations panel.

The three posters share branding but not page structure. This keeps them comparable while allowing the user to judge three genuinely different communication strategies.

## Variation 1: Standard academic structure

Filename: `output/pdf/poster_variation_1_standard.pdf`

This version follows the familiar academic reading order. It uses three balanced columns below the centered header:

1. Introduction, definitions, and related work.
2. Hypotheses and methodology.
3. Results, discussion, conclusion, and compact references.

The results table and accuracy chart provide complementary views. The prose remains explanatory enough for a reader who has not studied embeddings, but paragraphs are shortened for poster reading. The three hypotheses retain the user's wording while clarifying that the target-only GloVe condition is a diagnostic rather than a competitive classifier.

## Variation 2: Question-led structure

Filename: `output/pdf/poster_variation_2_questions.pdf`

This version uses a two-column question-and-answer narrative:

- What is the problem?
- What do the terms mean?
- What have others done?
- What did we expect?
- What did we do?
- What did we find?
- Where do the systems fail?
- So what?

The result is designed for non-specialist scanning. A large central result band bridges the columns, making the 50.0%, 55.5%, and 67.1% comparison the visual anchor. Short answers replace conventional academic section labels without weakening the methodological detail.

## Variation 3: Concise numbered structure

Filename: `output/pdf/poster_variation_3_concise.pdf`

This version emphasizes distance readability. It uses eight numbered sections with short bullets and a strong vertical rhythm. The poster contains the fewest words of the three, the largest section labels, and prominent numerical callouts for the three accuracy values and the 11.6-point gain.

The concise version still defines lexical ambiguity, homonymy, polysemy, embeddings, cosine similarity, and the WiC decision task. It does not reduce the poster to unexplained results.

## Citations

Names, years, and titles will follow `references/references.bib`. The core references are:

- Pilehvar and Camacho-Collados (2019) for WiC.
- Pennington, Socher, and Manning (2014) for GloVe.
- Devlin et al. (2019) for BERT.
- Camacho-Collados and Pilehvar (2018) for static, sense-specific, and contextual representations.
- Loureiro et al. (2021) for word sense disambiguation and language models.
- Haber and Poesio (2021) for polysemy and homonymy in contextual models.

References will be compact and human-readable. No unverified citation or placeholder will appear.

## Source organization

The editable TeX sources will live under `poster/variations/`. Shared identity, generated result macros, figures, and logo assets will be reused rather than copied when practical. Each variation will compile independently to its own PDF.

Rendered inspection images and other temporary QA files will stay outside the final submission directory. The three requested comparison PDFs will be copied into `output/pdf/`. The canonical `submission/` directory will remain unchanged with exactly `poster.pdf` and `appendix.pdf`.

## Verification

Each PDF must pass these checks:

- exactly one page;
- A1 portrait media box;
- embedded fonts and extractable text;
- no clipped, overlapping, missing, or unreadably small content;
- the correct authors and enrollment numbers;
- visible definitions, hypotheses, methodology, results, conclusion, and references;
- every reported experimental value agrees with committed result artifacts;
- the latest rendered PNG has been visually inspected;
- the Git working tree is clean after committing, and the remote `main` revision matches the local revision after pushing.

## Deliverables

- Three editable LaTeX source files and any small shared helper file required by them.
- Three A1 poster PDFs in `output/pdf/` with the stable filenames specified above.
- Updated build and verification automation covering all three variants.
- A committed and pushed Git revision containing the sources and generated PDFs.
