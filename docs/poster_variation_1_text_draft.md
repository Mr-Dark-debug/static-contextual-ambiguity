# Static vs Contextual Embeddings for Lexical Ambiguity: A Word-in-Context Evaluation

## Introduction

Consider these two sentences:

“She sat on the *bank* of the river.” Here, *bank* means the land beside the water.

“She deposited money at the *bank*.” Here, *bank* means a financial institution.

As we can see, the word *bank* is written exactly the same way in both sentences, but its meaning changes because of the context around it. This is called **lexical ambiguity**.

In this project, we wanted to understand whether a computer model can recognise this difference. More specifically, we wanted to see whether the way a model represents a word changes when that same word appears in a different context, and whether that change helps the model decide if the word has the same meaning or a different meaning.

## Inspiration

Our experiment was inspired mainly by the **Word-in-Context, or WiC, task introduced by Pilehvar and Camacho-Collados (2019)**. Instead of asking a model to choose a dictionary definition for a word, WiC asks a much simpler question: when the same word appears in two sentences, **does it have the same meaning in both sentences or not?**

We were also interested in a problem discussed by **Camacho-Collados and Pilehvar (2018)**. Traditional word representations often store only one representation for a word, even when that word has several meanings. Their work discusses different ways of representing multiple meanings more clearly. This led us to compare a simple fixed representation with representations that use the surrounding context.

## Background

Computers do not understand words directly in the way humans do. Language models usually represent words using **embeddings**, which are lists of numbers that capture information about a word.

In our experiment, we worked with two pretrained approaches: **GloVe** and **BERT**.

**GloVe** creates one stored vector for each word based on how words appear together across a large amount of text. This means that *bank* receives the same basic GloVe representation whether we are talking about a river bank or a financial bank. Because this representation does not change with the sentence, it is called a **static embedding**.

**BERT**, on the other hand, reads the sentence around a word before creating its representation. The representation of *bank* in a sentence about a river can therefore be different from the representation of *bank* in a sentence about money. This is called a **contextual representation**.

The two meanings of *bank* in our example are usually considered **homonyms** because the meanings are unrelated. Words can also have several related meanings, which is called **polysemy**. For example, *paper* can refer to the material we write on or to a newspaper.

Our task does not require the model to explain which exact meaning is being used. It only has to decide whether the marked word has the **same meaning** in two sentences or a **different meaning**.

## Hypothesis

We expected that using more information from the sentence would make it easier to recognise changes in meaning.

If we use only GloVe's stored representation of the target word, the word *bank* receives exactly the same vector in both sentences. The model therefore has no information about whether one sentence is talking about a river and the other about money. It sees the same representation twice.

Our validation data contains **638 sentence pairs**, with **319 same-meaning pairs and 319 different-meaning pairs**. Because the two classes are perfectly balanced, a method that always gives the same answer would still get half of them correct. That is why **50% is our simple baseline**.

We expected that adding nearby words such as *river* or *money* would give GloVe some useful context and improve this result. We expected BERT to perform better again because it uses information from the entire sentence when creating the representation of the target word.

## Methodology

### The Dataset

We used the **SuperGLUE version of the Word-in-Context dataset, WiC**, for all three comparison methods.

Every WiC example contains **two sentences containing the same target word**. The dataset also tells us whether that word has the same meaning in both sentences or whether its meaning changes.

For example, a pair could contain *bank* in a sentence about a river and *bank* in a sentence about money. That pair would be labelled **different meaning**. If both sentences used *bank* to describe a financial institution, the pair would be labelled **same meaning**.

The dataset contains **5,428 labelled training pairs** and **638 labelled validation pairs**.

We used the training data to decide the configuration of our methods, such as how many nearby words to use with GloVe, which BERT representations to combine, and what similarity value should separate “same meaning” from “different meaning.” After making those choices, we kept them fixed and measured the final performance on the 638 validation pairs.

The dataset also contains **1,400 test pairs**, but their correct answers are not publicly included in this version of SuperGLUE. Without those correct answers, we cannot check how many test examples our methods answered correctly. For that reason, the results presented here are based on the validation set.

### The Comparison

We used **two pretrained model families, GloVe and BERT, but compared them in three different ways**. The dataset remained exactly the same for all three methods.

**1. GloVe target word only**

For the first method, we used only the stored GloVe vector of the marked word.

For example, if the target word is *bank*, GloVe uses the same stored representation of *bank* in both the river sentence and the money sentence. This gives us a useful baseline showing what happens when the surrounding sentence is ignored.

**2. GloVe with nearby words**

For the second method, we tried to give GloVe some context.

Instead of using the target word itself, we looked at up to **two words before and two words after it** and combined their GloVe representations.

For example:

“The **muddy river** *bank* **flooded after** rain.”

For the target word *bank*, we use the nearby words *muddy*, *river*, *flooded*, and *after*. Their vectors are averaged to create a simple representation of the context around *bank*.

This allows words such as *river*, *money*, *water*, or *deposit* to provide clues about which meaning is being used.

**3. BERT using the full sentence**

For the third method, BERT reads the complete sentence before representing the target word.

BERT-base processes a sentence through **12 successive layers**, where each layer gradually builds a richer representation using information from the sentence. Instead of using only one of these stages, our selected configuration combines the representation of the target word from the **final four layers**.

We used BERT as a pretrained model. We did not retrain or fine-tune BERT on the WiC task itself.

### Deciding Same Meaning or Different Meaning

For every WiC example, each method produces one representation of the target word from the first sentence and another from the second sentence.

We then compare those two representations using **cosine similarity**. In simple terms, this gives us a number showing how similar the two representations are.

A higher similarity suggests that the word is being represented in a similar way in both sentences. A lower similarity suggests that its representation has changed.

Using the training data, we selected a cutoff value for each method. If the similarity is above that cutoff, we predict **same meaning**. If it is below the cutoff, we predict **different meaning**.

Finally, we calculate **accuracy**, which simply means the percentage of the 638 validation pairs that each method classified correctly.

## Results

The difference between the three methods was clear.

Using only the **GloVe target word**, the method correctly answered **319 of 638 pairs**, giving an accuracy of **50.0%**. This is exactly what we expected from a representation that remains identical for the target word regardless of its sentence.

When we added the **nearby words around the target**, GloVe improved to **354 correct pairs**, or **55.5% accuracy**. This shows that even a small amount of surrounding context provided useful information.

The strongest result came from **BERT using the target word in its full sentence**. BERT correctly classified **428 of 638 pairs**, giving an accuracy of **67.1%**.

So, compared with nearby-word GloVe, BERT correctly answered **74 additional sentence pairs**. That is an improvement of **11.6 percentage points**.

We also repeatedly resampled the validation examples to check whether this advantage depended heavily on a particular set of examples. Across 1,000 such resamples, the estimated 95% interval for BERT's improvement over nearby-word GloVe was **6.6 to 16.9 percentage points**. In other words, the advantage remained positive throughout that interval.

Looking more closely at the two stronger methods, **both BERT and nearby-word GloVe were correct on 250 pairs**. BERT was correct while nearby-word GloVe was wrong on **178 pairs**, while nearby-word GloVe was correct and BERT was wrong on **104 pairs**. Both methods were wrong on **106 pairs**.

This is important because BERT performed better overall, but it was not correct on every example.

## Conclusion

Our experiment shows that **the context around a word matters when trying to recognise its meaning**.

When GloVe looked only at the target word, it achieved **50.0% accuracy** because the word received the same representation regardless of the sentence. Adding a few nearby words increased the result to **55.5%**, showing that even simple contextual information helped.

BERT performed best at **67.1% accuracy** because its representation of the target word could change according to the complete sentence around it.

The experiment therefore supports what we expected at the beginning: a representation that changes with context is more useful for this Word-in-Context task than using one fixed representation of the word.

At the same time, BERT still answered **210 of the 638 validation pairs incorrectly**, so contextual representations do not solve lexical ambiguity perfectly. What made this project interesting for us was seeing this difference directly in an experiment we built and evaluated ourselves, rather than only reading about static and contextual embeddings in theory.

The result is specific to the methods and English WiC validation data used in this experiment, but it gives us a clear practical example of why modern language models use the surrounding sentence when representing ambiguous words.

*If you think this is all AI-generated, I will take it as an honour. After enough late nights working with AI, even this human can seem difficult to disambiguate.*
