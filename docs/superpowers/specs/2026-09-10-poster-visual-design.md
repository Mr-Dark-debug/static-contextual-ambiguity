# Evidence-led poster visual design

## Status and intent

This design implements the already approved goal constraints after the empirical
results are known. The poster must answer one question at viewing distance:
whether a frozen contextual target representation separates WiC senses better
than static target and lexical-context baselines.

## Approaches considered

1. **Results-first three-column narrative (selected).** Lead with the paired
   11.6-point accuracy difference, then let method and error evidence qualify it.
   This makes the answer immediate without hiding experimental controls.
2. **Methods-forward conference layout.** Give the data pipeline equal top-level
   weight with results. It is familiar, but the primary empirical contribution
   becomes visually timid.
3. **Single-chart minimalist layout.** Reserve most area for one large comparison
   plot. It is striking, but it cannot carry the required Hypothesis,
   Methodology, Results, layer analysis, error example, and limitations legibly.

## Poster architecture

Use one A1 portrait page (594 × 841 mm) with a compact title band and three
columns below it. Column one contains Hypothesis, Methodology, and the frozen
train-only selection flow. Column two contains the primary Result, with the model
comparison as the largest visual and similarity distributions below. Column
three contains the BERT layer curve, one paired qualitative contrast, limitations,
and a short conclusion. A narrow footer holds references, repository placeholder,
and provenance.

The reading order is explicit: question → controlled comparison → result → where
the result fails → bounded conclusion. Paragraph text is at least 24 pt; figure
labels are sized for their placed width rather than their source canvas.

## Visual language

- Background: warm off-white `#F7F4ED`; primary ink: navy `#17324D`.
- BERT: vermillion `#D55E00`; GloVe context: blue `#0072B2`; the context-free
  target diagnostic: neutral gray `#B8B8B8`.
- Same-sense and different-sense distribution fills use the Okabe–Ito green and
  purple pair. Color never carries meaning alone: labels, marks, and direct
  annotations remain present.
- Flat blocks, restrained rules, generous internal padding, no decorative stock
  imagery, gradients, or fake three-dimensional chart effects.

## Data and figure contract

Every plotted value must be read from `results/final/*.csv` or
`results/raw/scores.csv`; plotting code may not embed result numbers. Generate
PDF and SVG for placement plus 300-PPI PNGs for inspection. The four figure roles
are:

1. Primary validation accuracy with percentile intervals and direct values.
2. Same-/different-sense cosine distributions for selected GloVe context and
   selected BERT.
3. All 12 BERT layers, with the frozen mean-last-four result shown as a reference
   rather than a post-hoc layer winner.
4. One success/failure pair selected from the saved qualitative case table.

## Evidence copy

Lead claim: “Contextual target vectors add 11.6 accuracy points over local GloVe
context on WiC.” Pair it with the interval [-16.9, -6.6] percentage points for
GloVe minus BERT. State that the BERT encoder is unfine-tuned and the score is on
the official 638-pair validation set. Describe validation-layer behavior as a
secondary analysis, never as model selection.

## Appendix architecture

The appendix records the exact dataset release and license, preprocessing and
offset alignment, training-only selection ledger, full metrics and intervals,
layer table, error-partition method, environment, limitations, and complete
bibliography. It includes an explicitly unsigned integrity-declaration placeholder;
no signature is generated or imitated.

## Verification

Automated checks compare figure data to source tables, require at least 150 PPI
for raster previews, and test all code. PDF checks require one A1 portrait poster
page, embedded fonts, extractable mandatory headings, no unresolved citation
markers, exactly two files in `submission/`, and rendered visual inspection for
clipping, overlap, hierarchy, and legibility.

## Self-review

The design contains no unresolved content choice. Personal author and repository
details remain plainly labeled placeholders because the user did not supply them;
they are not fabricated. The selected layout, palette, result hierarchy, data
sources, appendix scope, and acceptance checks agree with the approved goal and
the existing implementation plan.
