# Poster narrative

## One-sentence answer

BERT answered 428 of 638 WiC validation pairs correctly. Nearby-word GloVe
answered 354 correctly, giving BERT 74 extra correct answers.

## Evidence sequence

1. A type-level GloVe target vector cannot change with context, so its paired
   cosine is exactly 1 and it collapses to one class.
2. Averaging nearby GloVe words restores some discriminative signal; ±2 tokens
   wins the prespecified training-only selection.
3. Mean-last-four BERT target vectors separate same- and different-sense score
   distributions more clearly and win the BERT training-only selection.
4. BERT exceeds nearby-word GloVe by 11.6 percentage points. Its paired 95%
   interval is [6.6, 16.9] points on 638 validation pairs.
5. BERT still misses 210 pairs, including confident errors, so the conclusion is
   about improved separation rather than solved lexical ambiguity.

## Poster flow

- Centered header: official university logo, full academic title, two names and
  enrollment numbers, university, degree and course.
- First row: lexical ambiguity, context, homonymy, polysemy and word embeddings
  on the left. Static and contextual embeddings, how GloVe and BERT work, and
  the pretraining-versus-per-occurrence distinction on the right.
- Second row: dictionary/knowledge-based and supervised sense disambiguation,
  WiC's same/different question and our hypothesis on the left. The three model
  conditions, cosine/cutoff decision rule, training-only selection and validation
  evaluation on the right.
- Wide results row: accuracy dots, bootstrap ranges, percentages and exact correct
  counts. The positive BERT advantage is stated in a short sentence.
- Last row: a short conclusion linking the result to the hypothesis and noting
  the remaining errors on this evaluation.
- Footer: five numbered references and a pointer to the existing appendix.

The 13 September revision uses white space and thin rules instead of containers.
Distribution, layer and example figures remain in the research artifacts and the
corresponding analyses remain in the appendix. The poster has no separate limitations
or success/warning panel. It uses short sentences without semicolons.

Following the user's concept-first revision, the paired-outcome bar chart is also
supplementary. Its four categories still include all 106 neither-correct cases,
regardless of the third target-only diagnostic.

## Language guardrails

Use “validation,” never “test,” for the 638 scored examples. Use “supports” or
“outperformed under this protocol,” never “proves” or “understands.” State
“unfine-tuned” next to BERT. Treat layer 1-12 validation results as secondary
analysis. Do not infer causes from selected examples; label explanations as
plausible hypotheses.
