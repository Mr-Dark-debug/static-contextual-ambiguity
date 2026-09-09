# Writing and poster style guide

This guide is a quality standard, not a detector-evasion recipe. The objective is clear scientific communication whose claims can be checked against the experiment.

## The reader's path

The poster must work at three distances:

1. **Across the room:** title, the bank/river problem, and the one-sentence result.
2. **At one step:** the research question, three conditions, largest comparison figure, and takeaway.
3. **Up close:** thresholds, confidence intervals, failure example, limitations, and compact citations.

The scan path is top → Hypothesis → Methodology → Results → Takeaway. Three columns and restrained dividers should make this order obvious without decorative arrows everywhere.

## Evidence order

Prefer:

```text
observation → measured evidence → bounded interpretation
```

Example structure after results exist:

> BERT placed the two label groups farther apart. Its held-out ROC-AUC was X versus Y for Static Context. This supports context-sensitive target geometry on WiC; it does not prove that BERT represents human senses perfectly.

Never start with a grand conclusion and search for a number to decorate it.

## Sentence rules

- Put the actor and action early: “BERT separated...” beats “A separation was observed...”
- Name the data or model instead of using empty subjects such as “the results.”
- Prefer concrete verbs: *separated, overlapped, misclassified, increased, selected*.
- Use “significant” only for a stated statistical procedure and result.
- Keep one claim per sentence when a sentence carries a number.
- Vary sentence length, but keep poster paragraphs to two or three short sentences.
- Define WiC, GloVe, BERT, cosine similarity, and macro F1 once. Avoid new acronyms.
- Use first person sparingly where it clarifies agency: “We froze thresholds on train.”

## Delete-on-sight phrases

Remove or rewrite these unless their literal meaning is necessary:

- “In today's rapidly evolving landscape”
- “It is important to note that”
- “This study aims to” after the study has already been run
- repeated “Furthermore” or “Moreover”
- “delve into,” “pivotal,” “multifaceted,” “leveraging”
- “robust” without a measured perturbation or replication test
- “novel” without a defensible novelty claim
- “demonstrates superior capabilities”
- “underscores the importance”
- “the results speak for themselves”

These phrases are not banned because a machine might use them. They are weak because they consume scarce poster space without telling the reader what happened.

## Claims and uncertainty

- Say “on the 638 WiC validation pairs,” not “in language.”
- Distinguish **target-only static GloVe** from the entire class of static or sense-specific embeddings.
- Call Static Target a diagnostic. Its near-constant similarity is inherent, not an empirical upset.
- Compare Static Context with BERT most prominently.
- Report confidence intervals beside main metrics.
- If a paired difference interval includes zero, say the result is inconclusive at that uncertainty level.
- Do not turn correlation, cosine distance, or a 2-D projection into proof of human-like understanding.
- Separate observed error patterns from plausible explanations.

## Section-specific copy

### Hypothesis

- Start with the marked *bank* contrast, then one sentence on meaning conflation.
- State the research question verbatim or nearly so.
- State H1 and H2 as predictions with reasons.
- Use 2–4 citations that directly support the background, not a miniature bibliography.

### Methodology

- Use a pipeline diagram and labels more than prose.
- Show sample counts and explicitly label validation as held out.
- Name GloVe 6B 300d, selected context window, `bert-base-uncased`, frozen feature extraction, WordPiece mean pooling, cosine, train-only thresholds, macro F1, and 1,000 bootstraps.
- Include a repository QR placeholder only if no real URL is available; never encode an invented link.

### Results

- Let the largest chart answer the research question.
- Follow it with the distribution plot that explains separation and the layer/error item that adds nuance.
- Put the strongest limitation next to the claim it bounds.
- End with one evidence-based takeaway, not a generic future-work paragraph.

## Typography and layout

- DIN A1 portrait: 594 × 841 mm.
- Body text target: 28–32 pt; absolute floor: 24 pt.
- Use a sans-serif family for poster copy and chart labels.
- Light neutral background, dark text, one controlled accent, and a color-blind-safe comparison color.
- Direct-label important chart elements where feasible.
- Prefer one strong chart to two small redundant charts.
- Preserve whitespace; do not shrink type to rescue an overfilled block.
- Put detailed references and extra metrics in the appendix.

## Final editing pass

For every sentence, ask:

1. Does it make a specific claim?
2. Can the claim be traced to a source or saved result?
3. Does the uncertainty match the evidence?
4. Could half the words say the same thing?
5. Does the reader need it on the poster rather than in the appendix?

For every visual, ask:

1. What question does this answer?
2. Is the source file named in code or caption metadata?
3. Are labels readable at placed size?
4. Does color add meaning?
5. Would removing it damage the argument?

## Sources that shaped this guide

- Erren and Bourne (2007) describe a poster as a concise, message-led medium and recommend a minimum 24 pt font, logical movement, and graphics used to clarify complexity.
- The NIH poster guidance recommends light backgrounds with dark text, direct graphic labeling, figure-heavy communication, and large body/legend type.
- Empirical studies of post-ChatGPT academic corpora, such as Geng and Trotta (2024), show measurable shifts in word-frequency patterns. That evidence does **not** justify detector gaming or a universal list of “AI words.” Our editing rule is functional: delete language that is vague, repetitive, inflated, or unsupported regardless of who wrote it.
