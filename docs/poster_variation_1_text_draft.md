# Variation 1: proposed poster wording

This is a copy draft for review. It does not change the LaTeX poster or either submission PDF. Keep the title **Static vs Contextual Embeddings for Lexical Ambiguity: A Word-in-Context Evaluation**. The intended reading order is introduction, background and hypothesis in column one, method and the paired-outcomes figure in column two, then results, interpretation and conclusion in column three. Keep the heading **Hypothesis** singular.

## Introduction — Why did we do this?

Consider the word *bank*. In “She sat on the bank of the river,” it means the land beside the water. In “She deposited money at the bank,” it means a financial institution. The spelling is the same, but the meaning changes. This is called **lexical ambiguity**. We wanted to know whether a model's representation of *bank* changes with the sentence in a way that helps it recognise that difference.

## Background — What are we comparing?

A **word embedding** is a list of numbers that a model uses to represent a word. GloVe stores one embedding for each word, so it gives *bank* the same representation in both sentences. BERT reads each sentence before representing the marked word, so its representation can change between the river and money examples. The distinction matters because a fixed representation cannot, by itself, tell which use of *bank* we mean. Earlier work also used dictionaries or several vectors per word to address this problem (Camacho-Collados & Pilehvar, 2018).

The two meanings of *bank* are usually treated as **homonyms** because they are unrelated. A word can also have related meanings, called **polysemy**: *paper* can mean the material or a newspaper. We test whether a model can tell when two uses of the same word have the same meaning, without asking it to name the meaning (Pilehvar & Camacho-Collados, 2019).

## Hypothesis — What did we expect?

We expected BERT to answer this same-or-different question more accurately than a simple GloVe representation. GloVe gives the target word the same vector in both sentences. If we compare only those two identical vectors, the method has no information about the change in meaning and will give the same answer every time. The validation set has 319 “same meaning” and 319 “different meaning” pairs, so always giving one answer would get 319 of 638 correct: **50%**, or what we call “chance” here. We thought that looking at the nearby words would help GloVe somewhat, because *river* and *money* provide clues. BERT should help more because it uses the whole sentence when representing the target word.

## Methodology — What did we do?

### The dataset

Word-in-Context (**WiC**) gives the same target word in two sentences and asks whether it keeps the same meaning. We used the SuperGLUE version, with **5,428 training pairs** and **638 validation pairs**. We used the training pairs to choose our settings, then checked the final choices once on validation. The **1,400 public test pairs** have no public labels in this release, so we do not report a test score.

### The comparison

We tried three ways to represent the marked word. First, we compared its fixed GloVe vector in the two sentences. Second, we represented its **nearby words** with GloVe: we took up to two words immediately before the target and up to two immediately after it, left out the target itself, and averaged the available vectors. That is what “two words on each side” means. Third, we let a pretrained BERT model read each full sentence and used the marked word's representation from its last four processing layers. We did not fine-tune BERT for WiC.

For each pair, we measured how similar the two representations were using **cosine similarity**. A higher value means the vectors point in more similar directions. A cutoff, chosen from the training data, turned that number into “same meaning” or “different meaning.” Our main score is **accuracy**, the share of pairs answered correctly. We estimated the uncertainty in the difference between methods by resampling the 638 validation pairs 1,000 times.

**Figure beside this section:** retain the paired-outcomes chart, with the labels “both right,” “only BERT right,” “only nearby-word GloVe right,” and “both wrong.” Spell out that each bar counts sentence pairs. The “neither correct” count is 106.

## Results — What happened?

The fixed GloVe word vector answered **319 of 638 pairs correctly (50.0%)**. Using nearby words raised that to **354 (55.5%)**. BERT answered **428 (67.1%)** correctly. Compared with nearby-word GloVe, BERT got **74 more pairs right**, a gain of **11.6 percentage points**. A paired 95% bootstrap interval places that gain between **6.6 and 16.9 points**. This supports our expectation for these models on this WiC validation set.

**Main chart proposal:** show three large horizontal bars on the same 0–100% scale, directly labelled “GloVe word only — 50.0%, 319/638,” “GloVe nearby words — 55.5%, 354/638,” and “BERT word in its sentence — 67.1%, 428/638.” Below them, write “BERT answered 74 more of the 638 pairs correctly than nearby-word GloVe.” Leave macro F1, ROC-AUC and per-layer results in the appendix. Do not use the current small dot-and-whisker chart as the main figure.

## Discussion — Where did the systems struggle?

A **same-meaning pair** has the target word used with the same meaning in both sentences. In a **different-meaning pair**, its meaning changes. BERT got **247 of 319 same-meaning pairs** right, but only **181 of 319 different-meaning pairs**. Nearby-word GloVe got **148 same-meaning pairs** and **206 different-meaning pairs** right. These counts show that the two systems make different kinds of mistakes under their chosen cutoffs.

BERT was right where nearby-word GloVe was wrong on **178 pairs**. GloVe was right where BERT was wrong on **104**. Both were wrong on **106**. For example, WiC labels “engrave a letter” and “engrave a pen” as different meanings, but BERT marked them as the same. This shows a failure in one real pair. It does not tell us exactly why BERT made that error.

## Conclusion — What can we take from this?

For this WiC comparison, a word representation that changes with its sentence worked better than a fixed GloVe vector or a simple average of nearby words. BERT still missed **210 of 638 pairs**. Our result covers one English validation set, one frozen BERT model and one simple GloVe context method, so it does not rank all static and contextual methods.

## Copy and layout notes for the next poster revision

- Place **Introduction**, **Background**, and **Hypothesis** one below the other, with normal paragraph spacing. Do not use `\vfill` to force large blank gaps between them.
- Keep **Methodology** as two connected subsections, “The dataset” and “The comparison.” Place the paired-outcomes figure near the explanation of how the systems were evaluated.
- Use **Results** as the largest visual area. The main chart should show percentage and number correct for all three methods at a size readable from a distance.
- Keep a brief **Discussion** and **Conclusion**. Use complete sentences rather than isolated label-and-fragment lines.
- Remove the full reference block. Keep two compact author–year citations in the background and point to the complete bibliography in `appendix.pdf`.
- Put a real GitHub repository link or QR code in the eventual **Methodology** area: `https://github.com/Mr-Dark-debug/static-contextual-ambiguity`.
- Before PDF production, check A1 portrait, one page, body text at least 24 pt, chart labels at a readable size, embedded fonts, and any raster image at at least 150 PPI at the placed size.

## Rule audit of the current variation 1

The audit uses the requirements in the supplied `goal-objective.md`, the existing project style guide, the current TeX source and the saved experiment results. It does not claim an independently checked university handout.

| Requirement | Current variation 1 | Next revision |
| --- | --- | --- |
| One-page DIN A1 portrait | Pass: 594 × 841 mm | Keep it. |
| Hypothesis, Methodology and Results visible | Partial: the first heading says “Hypotheses” | Use the required singular heading “Hypothesis.” |
| Body paragraphs at least 24 pt | Pass for the main body: 25 pt. The chart caption is 22 pt and the reference block is 17 pt. | Keep body copy at least 24 pt. Remove the reference block and size any supporting labels for the final page. |
| Readable charts and figures | Fail in practice: the accuracy chart is too small at its current placement. It was made 14 inches wide, then reduced to roughly half width in the right column, shrinking 15–24 pt source labels to about 7–12 pt on the page. | Replace it with three direct-labelled horizontal bars, with percent and correct-pair count, drawn at their actual placed size. Increase the paired-outcome chart labels as needed. |
| At least 150 PPI for raster graphics | The imported charts and logo are vector PDFs. Raster previews were generated at high resolution. | Verify any new raster asset at its final placed size. |
| Explain data, models, similarity, threshold and evaluation | Partial: the facts are present but “±2,” chance and sense labels are unexplained | Use the connected method and definitions above. |
| Reproducibility and GitHub link or QR | Partial: train-only selection is described, but there is no repository link or QR | Add the real repository link and a concise train/validation statement. |
| Real, traceable results and limitations | Pass numerically. The explanation is too terse. | Keep the saved values and use the results and discussion copy above. |
| Compact citations, full bibliography in appendix | Fail: the poster has numbered citations and a full footer block | Use compact author–year citations in the background and keep complete entries in the appendix. |
| Exactly `poster.pdf` and `appendix.pdf` in the final submission | Pass for the current `submission/` directory | Keep the comparison drafts outside it. |
| Complete personal submission | Pending: the appendix still has author/repository placeholders and an unsigned declaration placeholder | The students must supply the approved declaration and sign it before hand-in. |

Overall, the current PDFs are technically valid A1 files and their results are verified, but variation 1 does **not** yet meet the requested clarity, chart legibility, citation style and repository-link requirements. This draft addresses the wording only. A later design pass must typeset and check the revised copy before it can be called a compliant final poster.
