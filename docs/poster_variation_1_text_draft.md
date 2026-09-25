# Static vs Contextual Embeddings for Lexical Ambiguity: A Word-in-Context Evaluation

## Introduction

In “She sat on the *bank* of the river,” *bank* means the land beside the water. In “She deposited money at the *bank*,” it means a financial institution. The spelling is the same in both sentences, but the meaning changes with the words around it. This is called **lexical ambiguity**. We wanted to find out whether a computer can represent *bank* differently in those two sentences and tell that its meaning has changed. Our experiment follows the question behind the Word-in-Context (WiC) dataset introduced by Pilehvar and Camacho-Collados (2019): does the same word have the same meaning in two sentences?

## Background

A **word embedding** is a list of numbers used to represent a word. We compared two existing approaches. **GloVe** is a pretrained method that learns a stored vector for each word from patterns of words appearing together in text (Pennington et al., 2014). It is called *static* because the vector for *bank* stays the same whether the sentence is about a river or money. **BERT** is a pretrained language model that reads the surrounding sentence before producing a representation for each occurrence of a word (Devlin et al., 2019). Its representation of *bank* can therefore change with the sentence. We did not retrain either model on WiC examples.

We made this comparison because one stored vector can mix a word's different meanings together, a problem discussed by Camacho-Collados and Pilehvar (2018). Their survey also describes methods that give a word separate representations for its different senses. We test a simpler contrast between a fixed word vector, fixed vectors combined from nearby words, and a word representation produced from the full sentence.

The two meanings of *bank* above are **homonyms** because they are unrelated. When meanings are related, the word is **polysemous**: *paper* can mean the material or a newspaper. WiC does not ask us to choose a dictionary definition. It asks whether the marked word has the **same meaning** in both sentences or a **different meaning**.

## Hypothesis

We expected BERT to answer that same-or-different question more accurately than GloVe. If we use only GloVe's stored vector for the marked word, the two copies of *bank* get identical vectors. Comparing them gives the same similarity score every time, so this method cannot tell the river example from the money example. Half of the validation pairs have the same meaning and half have different meanings. A method that always chooses one answer would therefore get 319 of 638 pairs right, or **50%**. We expected the words near the target, such as *river* or *money*, to give a GloVe-based method some useful clues. BERT reads the full sentence when representing the target, so we expected it to do better still.

## Methodology

### The dataset

We used one dataset for all three comparison methods: the SuperGLUE release of **WiC**, or Word-in-Context. Each example contains two sentences with the same marked word and an answer saying whether that word has the same meaning in both. There are **5,428 labelled training pairs** and **638 labelled validation pairs**. We used training data to choose the number of nearby words for GloVe, which BERT layer outputs to combine, and the similarity cutoff for each method. Once those choices were fixed, we measured performance on validation. The release also includes **1,400 test pairs**, but does not provide their correct answers, so we cannot calculate a test score from them.

### The comparison

We used **two pretrained model families, GloVe and BERT, in three ways**. First, we compared the stored GloVe vector for the marked word in each sentence. Second, we represented each occurrence using GloVe vectors for the words around it. We took up to two words before and two words after the target, left out the target itself, and averaged the available vectors. For example, in “The muddy river *bank* flooded after rain,” the selected words are *muddy*, *river*, *flooded* and *after*. This example explains the window; it is not a WiC result. Third, we let BERT read each full sentence and extracted the marked word's representation. BERT-base processes text through 12 layers. We averaged the outputs for the target word from its last four layers, without further training BERT on WiC.

Each method gives us one representation for the marked word in each sentence. We compare the two representations using **cosine similarity**, a number that is higher when the vectors point in more similar directions. We then use a cutoff chosen from the training data: scores at or above it mean “same meaning,” and lower scores mean “different meaning.” **Accuracy** is the percentage of validation pairs answered correctly. To check how much the difference between the methods might vary with the particular pairs sampled, we also repeated the comparison on 1,000 resamples of the validation set.

## Results

The target-word GloVe method answered **319 of 638 pairs correctly (50.0%)**. Using nearby GloVe words raised this to **354 pairs (55.5%)**. BERT answered **428 pairs correctly (67.1%)**. Compared with nearby-word GloVe, BERT got **74 more pairs right**, a gain of **11.6 percentage points**. The estimated 95% interval for that gain was **6.6 to 16.9 points**. This matches our expectation on this validation set: nearby words helped a little, while the full-sentence BERT representation helped more.

Looking at the two stronger methods pair by pair adds detail. Both were right on **250 pairs**. BERT alone was right on **178**, nearby-word GloVe alone on **104**, and both were wrong on **106**. These counts show why BERT's overall lead does not mean it succeeds on every example.

## Conclusion

In this WiC experiment, letting the representation of a word depend on its sentence made it easier to recognise when its meaning changed. Nearby words improved on a fixed GloVe target vector, and BERT gave the best result of the three methods we tested. BERT still missed **210 of 638 pairs**, so there is room to understand where these representations struggle. Our result is about this English validation set, a frozen BERT model and a simple GloVe context method; it does not show that every contextual method beats every static one.
