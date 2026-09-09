# Literature matrix

Sources were checked against the original paper, ACL Anthology metadata, the original WiC site, or the publisher record. “Claim supported here” is intentionally narrower than the paper's full argument.

## Camacho-Collados and Pilehvar (2018)

**Citation:** José Camacho-Collados and Mohammad Taher Pilehvar. 2018. “From Word to Sense Embeddings: A Survey on Vector Representations of Meaning.” *Journal of Artificial Intelligence Research* 63:743–788. https://doi.org/10.1613/jair.1.11259

**Research question:** How are word meanings represented as vectors, what motivates sense-level alternatives, how are such representations learned, and how should they be evaluated?

**Data:** A survey of lexical resources, intrinsic benchmarks, and downstream evaluations rather than one new dataset.

**Representation/model:** Static word vectors; unsupervised multi-prototype representations; knowledge-based sense/concept embeddings; early contextualized representations.

**Experiment:** Taxonomy and comparative analysis of prior methods and evaluations.

**Relevant findings:** A single vector for a polysemous word conflates information from its meanings—the “meaning conflation deficiency.” Sense representations can address that deficiency, but evaluation setup and sense inventories introduce their own problems.

**Limitation:** As a survey, it does not test our GloVe/BERT threshold pipeline or establish that sense-aware representations win every task.

**Claim supported here:** A context-independent target vector cannot change across two occurrences of the same lexical item and therefore cannot directly encode which sense is active.

## Pilehvar and Camacho-Collados (2019)

**Citation:** Mohammad Taher Pilehvar and Jose Camacho-Collados. 2019. “WiC: the Word-in-Context Dataset for Evaluating Context-Sensitive Meaning Representations.” *NAACL-HLT 2019*, 1267–1273. https://doi.org/10.18653/v1/N19-1128

**Research question:** Can a reliable, general benchmark directly evaluate whether a representation detects meaning change across contexts?

**Data:** WiC, built from lexicographic examples with expert-curated binary same/different labels. The SuperGLUE v2 release used here contains 5,428 balanced train, 638 balanced validation, and 1,400 unlabeled test pairs.

**Representation/model:** The paper evaluates contextualized word vectors, sense embeddings, and sentence baselines under a binary word-in-context formulation.

**Experiment:** Given two sentences and a marked common word, predict whether the word has the same meaning. The paper reports human performance and multiple representation baselines.

**Relevant findings:** WiC exposes context sensitivity more directly than context-free similarity datasets; the original site reports an 80.0% human upper-bound estimate and version-specific model baselines.

**Limitation:** Binary labels impose a boundary on graded meaning relatedness. The original and SuperGLUE releases differ in packaging/version details, so results must name the release and split.

**Claim supported here:** WiC operationalizes contextual meaning discrimination as the same target in two contexts with a same/different label.

## Loureiro et al. (2021)

**Citation:** Daniel Loureiro, Kiamehr Rezaee, Mohammad Taher Pilehvar, and Jose Camacho-Collados. 2021. “Analysis and Evaluation of Language Models for Word Sense Disambiguation.” *Computational Linguistics* 47(2):387–443. https://doi.org/10.1162/coli_a_00405

**Research question:** What word-sense information does BERT encode, what are its limitations, and how do fine-tuning and feature extraction compare for WSD?

**Data:** Unified all-words WSD benchmarks and controlled analyses with varying examples per sense.

**Representation/model:** BERT and related language models, compared through feature extraction and fine-tuning strategies.

**Experiment:** Quantitative and qualitative WSD analysis, including sense bias, part of speech, frequency, training-data availability, and feature-extraction versus fine-tuning.

**Relevant findings:** BERT captures coarse, high-level sense distinctions under favorable conditions. Averaged contextual features can work with few labeled examples and feature extraction is less sensitive to sense bias than fine-tuning in their setup. Practical WSD remains difficult outside ideal data/compute conditions.

**Limitation:** WSD with sense inventories and supervised sense examples is not our unsupervised cosine-threshold WiC setup.

**Claim supported here:** Pretrained BERT features contain recoverable word-sense information, but this does not imply perfect or universal sense separation.

**Metadata note:** The supplied 2020/arXiv entry used the preprint title “Language Models and Word Sense Disambiguation: An Overview and Analysis.” The verified archival article has the title and 2021 metadata above.

## Zhou and Bollegala (2021)

**Citation:** Yi Zhou and Danushka Bollegala. 2021. “Learning Sense-Specific Static Embeddings using Contextualised Word Embeddings as a Proxy.” *Proceedings of PACLIC 35*, 493–502. https://aclanthology.org/2021.paclic-1.52/

**Research question:** Can sense information from contextualized embeddings be injected into compact static embeddings?

**Data:** Sense-annotated corpora and multiple WSD/sense-discrimination benchmarks.

**Representation/model:** Context Derived Embeddings of Senses (CDES), learned projection matrices that map pretrained static embeddings toward contextualized, sense-specific targets.

**Experiment:** Train CDES from contextual embeddings plus sense annotation, then compare learned sense-specific static embeddings with existing sense embeddings on WSD and discrimination.

**Relevant findings:** CDES produced competitive sense-specific static embeddings while retaining precomputable, lower-cost representations.

**Limitation:** CDES is supervised by sense annotations and uses contextual models as a teacher; it is not equivalent to the simple GloVe context average tested here.

**Claim supported here:** “Static” and “sense-specific” are not opposites: static vectors can be de-conflated through additional modeling, so our target-only GloVe result should not be generalized to every static representation.

## Trott and Bergen (2021)

**Citation:** Sean Trott and Benjamin Bergen. 2021. “RAW-C: Relatedness of Ambiguous Words in Context (A New Lexical Resource for English).” *ACL-IJCNLP 2021*, 7077–7087. https://doi.org/10.18653/v1/2021.acl-long.550

**Research question:** How closely do contextualized embedding distances track people's graded judgments about ambiguous word uses?

**Data:** RAW-C: 112 ambiguous English words, 672 sentence pairs, graded relatedness judgments, and sense-dominance estimates; reported average leave-one-annotator-out agreement is 0.79.

**Representation/model:** BERT and ELMo contextual target embeddings with cosine distance.

**Experiment:** Correlate model distances with human relatedness ratings and inspect systematic calibration errors for same-sense and homonymous uses.

**Relevant findings:** Contextual distance correlates with judgments but underestimates human similarity for same-sense uses and overestimates similarity for different-sense homonyms.

**Limitation:** RAW-C is graded and small, while WiC is binary; correlation and thresholded classification answer different questions.

**Claim supported here:** Cosine geometry is informative but imperfect, motivating both score-distribution plots and qualitative errors rather than accuracy alone.

## Haber and Poesio (2021)

**Citation:** Janosch Haber and Massimo Poesio. 2021. “Patterns of Polysemy and Homonymy in Contextualised Language Models.” *Findings of EMNLP 2021*, 2663–2676. https://doi.org/10.18653/v1/2021.findings-emnlp.226

**Research question:** Do contextualized embeddings reproduce human distinctions among identity of meaning, homonymy, and different types of polysemic alternation?

**Data:** Human-annotated graded sense similarity and co-predication judgments for 28 ambiguous English nouns.

**Representation/model:** Off-the-shelf contextualized language models, including BERT Large; target embeddings are compared by similarity and clustering.

**Experiment:** Compare embedding similarity with human ratings and inspect whether clustering recovers interpretation groupings.

**Relevant findings:** Human ratings place polysemic interpretations on a continuum. BERT Large correlated best among tested models but inconsistently reproduced some polysemy patterns while separating homonyms more confidently.

**Limitation:** The controlled noun set and graded annotations do not map directly to all WiC parts of speech or its binary labels.

**Claim supported here:** Contextual representations can distinguish clear sense contrasts yet remain unreliable for subtler related meanings.

**Metadata note:** The supplied title “Patterns of Lexical Ambiguity...” is not the archival title.

## Soper and Koenig (2022)

**Citation:** Elizabeth Soper and Jean-pierre Koenig. 2022. “When Polysemy Matters: Modeling Semantic Categorization with Word Embeddings.” *Proceedings of the 11th Joint Conference on Lexical and Computational Semantics*, 123–131. https://doi.org/10.18653/v1/2022.starsem-1.10

**Research question:** Does accounting for polysemy change how well static and sense-level embeddings model human semantic categorization?

**Data:** Coarse categories from a word-sorting task and fine-grained categories derived from context-free similarity judgments.

**Representation/model:** Previously studied static embeddings and sense-level embeddings.

**Experiment:** Predict category structure at two granularities and compare representation families.

**Relevant findings:** Sense-level embeddings strongly outperformed static embeddings on coarse word-sorting categories but performed approximately equally on fine-grained categories derived from context-free similarity judgments.

**Limitation:** Categorization is not WiC classification; task definition materially changes the comparison.

**Claim supported here:** Contextual or sense-specific representations are not universally superior. Any advantage in our study is specific to word-in-context discrimination.

## Fodor, De Deyne, and Suzuki (2023)

**Citation:** James Fodor, Simon De Deyne, and Shinsuke Suzuki. 2023. “The Importance of Context in the Evaluation of Word Embeddings: The Effects of Antonymy and Polysemy.” *Proceedings of IWCS 2023*, 155–172. https://aclanthology.org/2023.iwcs-1.17/

**Research question:** Why do embeddings fail on some human word-similarity judgments, especially antonymy and polysemy, and can added context improve fit?

**Data:** Several experimental semantic similarity/relatedness datasets, including antonym and polysemy subsets; contextual information drawn from corpora and dictionaries.

**Representation/model:** Static and transformer embeddings, with additional corpus- or dictionary-derived context for transformer representations.

**Experiment:** Measure fit between embedding similarity and human judgments, then test whether incorporating extra context improves it.

**Relevant findings:** Models performed reasonably overall but fit antonym and polysemy judgments poorly; added context improved transformer fit in their experiments.

**Limitation:** The paper studies mostly context-free word-pair judgments with implicit/constructed context, not marked target uses in WiC sentences.

**Claim supported here:** Evaluation context changes what embedding similarity means, supporting an explicitly contextual benchmark and a cautious interpretation of cosine scores.

## Cevoli et al. (2023, optional interpretive source)

**Citation:** Benedetta Cevoli, Chris Watkins, Yang Gao, and Kathleen Rastle. 2023. “Shades of meaning: Uncovering the geometry of ambiguous word representations through contextualised language models.” arXiv:2304.13597. https://doi.org/10.48550/arXiv.2304.13597

**Research question:** Does contextual-model geometry capture distinctions among unambiguous, homonymous, and polysemous words that accord with lexicographic and psychological accounts?

**Data:** Simulations over contextual uses of words grouped by lexical-ambiguity class.

**Representation/model:** Contextual language-model representations and geometric analyses.

**Experiment:** Compare within- and between-use geometry across ambiguity types.

**Relevant findings:** The reported geometry distinguishes fine-grained ambiguity classes in ways aligned with lexicographic and psychological theory.

**Limitation:** This is an arXiv preprint in the verified source used here, and its simulations do not validate our WiC classifier.

**Claim supported here:** Meaning relatedness may form graded geometric structure, so a binary threshold is an analytical simplification.

## Model sources

### Pennington, Socher, and Manning (2014)

**Citation:** Jeffrey Pennington, Richard Socher, and Christopher Manning. 2014. “GloVe: Global Vectors for Word Representation.” *EMNLP 2014*, 1532–1543. https://doi.org/10.3115/v1/D14-1162

**Use here:** Defines the global log-bilinear static-vector method and supports the identity/model provenance of the GloVe baseline. It does not claim that a simple averaged context is optimal.

### Devlin et al. (2019)

**Citation:** Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. “BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.” *NAACL-HLT 2019*, 4171–4186. https://doi.org/10.18653/v1/N19-1423

**Use here:** Defines BERT's bidirectional contextual pretraining and base architecture. It does not establish our layer/pooling winner; that must come from training-only selection.

## Poster-writing sources

### Erren and Bourne (2007)

**Citation:** Thomas C. Erren and Philip E. Bourne. 2007. “Ten Simple Rules for a Good Poster Presentation.” *PLOS Computational Biology* 3(5):e102. https://doi.org/10.1371/journal.pcbi.0030102

**Use here:** Supports one clear message, logical visual movement, concise scientific reporting, meaningful graphics, and a 24 pt minimum.

### NIH Office of Intramural Training & Education

**Source:** “Creating a Scientific Poster.” https://www.training.nih.gov/creating-a-scientific-poster/

**Use here:** Supports light background/dark text, direct graphic labels, visual-first content, generous whitespace, and substantially larger than 24 pt body text when space permits. Its prescribed board dimensions do not override the exam's DIN A1 requirement.
