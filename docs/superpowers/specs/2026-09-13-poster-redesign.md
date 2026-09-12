# Poster readability redesign

The user requested a centered academic title and author block for two people,
their enrollment numbers, university details and the official Trier logo.
They requested simpler words, clearer charts, consistent alignment, removal of
the success/warning and limitations panels, fewer divisions and no excessive
semicolons. The follow-up explicitly asks to continue and supplies the current
poster as a visual reference. This authorizes implementation and visual revision.

## Design

Use a white A1 portrait page with navy type, Trier blue and one orange comparison
color. Center the full research title, two author slots and university/course
details. Preserve the official logo artwork and aspect ratio. Body sections sit
directly on the page with aligned margins, thin rules and consistent spacing.
Use two equal columns for concepts/model definitions and related approaches/method,
then a wide primary results chart and a short conclusion.

Three alternatives were considered: retaining the original three narrow columns,
a two-column open layout with a wide results figure, and a single giant result
with only supporting footnotes. Choose the second because it accommodates the
long academic title and makes the charts readable without tiny type.

Explain the task before discussing models. Define an embedding as a numerical
word representation and WiC as deciding whether a word has the same meaning in
two sentences. Use bank to illustrate homonymy and newspaper to illustrate polysemy.
Explain both models, their mechanisms and related sense-disambiguation methods
before stating the hypothesis. Display accuracy and correct-answer counts in a
horizontal dot-and-interval plot. The paired-outcome bar chart is supplementary
after the user's explicit request for more conceptual explanation. Derive every number
from the saved results and predictions. State the positive BERT-minus-GloVe gain
and interval. Explain intervals in a short caption. Keep English validation
scope and frozen-model status in ordinary method/conclusion text.

Remove the old slogan, orange banner, distributions, layer curve, qualitative
success/warning graphic, standalone limitations panel and defensive technical
headings from the poster. Retain the full analyses in the existing research
artifacts and appendix. Do not rerun or retune models for a visual revision.

## Sources inspected on 2026-09-13

- https://aclanthology.org/2023.findings-acl.550.pdf, p. 4: grouped comparison bars
  and labelled scatter plots.
- https://aclanthology.org/2020.acl-main.422.pdf, p. 9: labelled layer line plots.
- https://kib.ki.se/en/visualise-present/poster-design: simplify plots, use white
  space for grouping, put authors under the title, label figures directly.
- https://library.port.ac.uk/academic-support/presentations-and-group-work/academic-posters:
  two columns for portrait posters and large body text.
- Official logo asset:
  https://www.uni-trier.de/typo3conf/ext/zimktheme_unitrier/Resources/Public/Logos/Logo_Universitaet.svg
- Trier's detailed student corporate-design guidance requires campus/VPN access.
  The public official artwork can be sourced and preserved, but full manual
  compliance cannot be certified from the accessible pages.

## Acceptance

- Exactly one A1 poster page with no clipping or overlapping content.
- Centered title, two names/enrollment numbers and affiliation. The user supplied
  Choudhary Prashant Santosh (1910474) and Rahul Khunt (1911272) during this revision.
- Body 27 pt or larger, captions 24 pt or larger and legible chart labels.
- No bordered content containers, success/warning panel or limitations heading.
- Numbers and paired outcome categories agree with the 638 saved predictions.
- Rebuild vector figures and poster, render the whole page at 150 PPI and inspect.
- Submission still contains exactly poster.pdf and appendix.pdf.
- Existing appendix and empirical result files are unchanged.

## Final refinement and validation

The user approved the cleaner visual direction and requested a stronger teaching
sequence. The final page therefore defines the topic and competing representations
before the study. References [4] and [5] support ambiguity terminology and related
approaches, using verified papers already in the project bibliography:

- https://aclanthology.org/2021.findings-emnlp.226/
- https://aclanthology.org/2021.cl-2.14/, discussion of WSD approach families.

The final poster has one chart. The paired-outcome chart remains reproducible in
the figure directory. Both authors and enrollment numbers are supplied, and the
page has no personal-data placeholders.
