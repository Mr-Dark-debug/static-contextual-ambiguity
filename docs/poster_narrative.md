# Poster narrative

## One-sentence answer

On WiC validation, an unfine-tuned BERT target representation adds 11.6 accuracy
points over the train-selected local GloVe context average (67.1% versus 55.5%).

## Evidence sequence

1. A type-level GloVe target vector cannot change with context, so its paired
   cosine is exactly 1 and it collapses to one class.
2. Averaging nearby GloVe words restores some discriminative signal; ±2 tokens
   wins the prespecified training-only selection.
3. Mean-last-four BERT target vectors separate same- and different-sense score
   distributions more clearly and win the BERT training-only selection.
4. The paired 95% accuracy-difference interval for GloVe context minus BERT is
   [-16.9, -6.6] percentage points on 638 validation pairs.
5. BERT still misses 210 pairs, including confident errors, so the conclusion is
   about improved separation rather than solved lexical ambiguity.

## Poster flow

- Left: hypothesis, official data, representations, alignment, and the locked
  selection/evaluation boundary.
- Center: the answer in one large comparison chart, then the similarity
  distributions that explain the gain geometrically.
- Right: layer development, one success and one confident failure, limitations,
  and a bounded conclusion.

## Language guardrails

Use “validation,” never “test,” for the 638 scored examples. Use “supports” or
“outperformed under this protocol,” never “proves” or “understands.” State
“unfine-tuned” next to BERT. Treat layer 1-12 validation results as secondary
analysis. Do not infer causes from selected examples; label explanations as
plausible hypotheses.
