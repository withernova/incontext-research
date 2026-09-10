# Make LVLMs Focus: Context-Aware Attention Modulation for Better Multimodal In-Context Learning

Yanshu Li<sup>1</sup>, Jianjiang Yang<sup>2</sup>, Ziteng Yang<sup>1</sup>, Bozheng Li<sup>1</sup>, Ligong Han<sup>3</sup>, Hongyang He<sup>4</sup>, Zhengtao Yao<sup>5</sup>, Yingjie Victor Chen<sup>6</sup>, Songlin Fei<sup>6</sup>, Dongfang Liu<sup>7</sup>, Ruixiang Tang<sup>8∗</sup>

<sup>1</sup>Brown University   
<sup>2</sup>University of Bristol   
<sup>3</sup>MIT-IBM Watson AI Lab   
<sup>4</sup>University of Warwick   
<sup>5</sup>University of Southern California   
<sup>6</sup>Purdue University   
<sup>7</sup>Rochester Institute of Technology   
<sup>8</sup>Rutgers University   
yanshu li1@brown.edu, ruixiang.tang@rutgers.edu

## Abstract

Multimodal in-context learning (ICL) is becoming a key capability that allows large vision-language models (LVLMs) to adapt to novel tasks without parameter updates, which expands their usefulness in many real-world applications. However, ICL performance remains unstable even when the incontext demonstrations (ICDs) are well matched, showing that LVLMs still struggle to make full use of the provided context.‐ While existing work mainly focuses on prompt engineering or post-hoc logit calibration, we study the attention mechanisms inside LVLMs to address their inherent limitations. We identify two important weaknesses in their self-attention that hinder efective ICL. To address these weaknesses, we propose Context-Aware Modulated Attention (CAMA), a trainingfree and plug-and-play method that dynamically adjusts attention logits based on the input in-context sequence. CAMA uses a two-stage modulation process that strengthens attention to semantically important tokens, especially visual ones. Across four LVLMs and seven benchmarks, CAMA consistently outperforms vanilla models and baselines, showing clear efectiveness and generalization. It can also activate the intended benefits of prompt engineering methods and remains robust across diferent sequence configurations. Therefore, CAMA opens up new directions for improving multimodal reasoning through a deeper understanding of attention dynamics.

## Introduction

Large vision-language models (LVLMs) have emerged as powerful tools for multimodal information processing and generation (Zhao et al. 2025). Through large-scale pretraining, they integrate visual and textual signals into the shared representation space of large language models (LLMs) and have achieved notable success across vision-language tasks (Ye et al. 2023; Liu et al. 2023). However, adapting LVLMs to new domains remains challenging due to the high costs of multimodal data preparation and training.

To mitigate these costs, researchers are applying in-context learning (ICL), a technique widely used in LLMs (Brown et al. 2020; Dong et al. 2024), to LVLMs (Li 2025). In ICL, a few in-context demonstrations (ICDs) are incorporated into the input as reference examples, enabling the model to adapt to new tasks by interpreting these demonstrations without parameter updates. Recent advancements in model architectures and training protocols have enabled LVLMs to process multiple images and perform interleaved reasoning, making multimodal ICL practical (Alayrac et al. 2022; Laurenc¸on et al. 2024; Bai et al. 2025; Chen et al. 2025). These advances expand the practical scope of LVLMs (Doveh et al. 2024; Chen et al. 2024b; Guo et al. 2024).

![](images/3507d13b545857e1f3e8a1a9e72e6051183cc5faf471e7f38266898601b845f6.jpg)  
Figure 1: (a) Example of a 3-shot multimodal in-context sequence. (b)-(d) present the vanilla model, adding an instruction to the sequence, and our proposed method, CAMA, respectively. All attention heatmaps come from layer 18, and redder regions indicate stronger attention.

However, the benefits of multimodal ICL can be diminished by its pronounced instability. Recent studies have found that LVLM ICL performance is highly sensitive to subtle prompt details. Minor changes in the order or formatting of ICDs can cause significant performance swings (Liu et al. 2021; Gao, Fisch, and Chen 2021; Lu et al. 2022). This sensitivity intensifies as the number of ICDs grows or when complex multimodal reasoning is required (Chen et al. 2024d; Li et al. 2025c). To improve multimodal ICL in LVLMs, two main routes have been explored. The first optimizes the prompt. It adds guiding text, highlights key image regions, or selects and orders ICDs with predefined metrics (Li et al. 2023a; Yang et al. 2024b). However, prompt engineering requires substantial prior knowledge, lacks stability, and depends heavily on the base model. The second route edits models’ internal logits, as in contrastive decoding. This approach alters reasoning more directly but needs distorted inputs and extra forward passes for calibration (Liu, Zheng, and Chen 2024; Lee, Tsai, and Chiu 2024). Since practical ICL prioritizes eficiency, our work investigates the following questions: What is the intrinsic limitation underlying the instability of multimodal ICL in LVLMs? Can we address it using a more eficient, training-free method?

In pursuit of these questions, we examine the attention dynamics of LVLMs during multimodal ICL. Because their inputs interleave images and texts, we move beyond the existing focus on single-image scenarios and analyze LVLMs from two distinct perspectives: (1) text-based visual grounding within each image-text pair, and (2) query-sample-driven attention allocation across ICDs. We visualize attention deficits in both aspects through targeted experiments and verify that these deficits lead to insuficient utilization of the in-context sequence by the LVLM, resulting in unstable multimodal ICL. In response to these deficits, we present Context-Aware Modulated Attention (CAMA), a training-free method that dynamically modulates the model’s internal attention logits during inference based on the input context. CAMA addresses the two deficits with a two-stage modulation that targets the shallow and middle layers of the decoder. Stage I applies intra-ICD grounding, highlighting the image tokens in each ICD and in the query sample that best align with their accompanying text, which reduces the attention sink introduced by the interleaved image-text format. Stage II performs query-centric routing, reallocating attention among ICDs in proportion to their value to produce the desired answer, thus improving the use of context. Experiments demonstrate that CAMA delivers consistent performance gains for multimodal ICL, providing insights for reshaping attention mechanisms to build models with better visual capabilities.

The contributions of this paper are summarized below:

• We analyze LVLMs’ attention dynamics in multimodal ICL beyond single-image settings and reveal two deficits: weak vision-text alignment within each pair and misalignment between the query sample and its ICDs.

• Building on the identified deficits, we introduce CAMA, the first training-free and model-agnostic method designed to enhance multimodal ICL. CAMA applies a twostage modulation of internal attention logits that steers the model toward the tokens most relevant to ICL.

• Extensive experiments demonstrate that CAMA improves multimodal ICL across diverse LVLMs and benchmarks. Ablation studies confirm the necessity of each design and reveal CAMA’s broader potential.

In-context Learning (ICL). ICL enables models to solve unseen tasks by conditioning on an input sequence of input–output examples (i.e., ICDs) without updating any parameters (Brown et al. 2020; Dong et al. 2024). This capability markedly improves their practicality and is especially valued in resource-intensive multimodal domains (Wies, Levine, and Shashua 2023). Large vision–language models (LVLMs) gain ICL capabilities through targeted pretraining or fine-tuning on interleaved image–text data, as in Flamingo (Alayrac et al. 2022) and LLaVA-NeXT (Li et al. 2024). Now, it has become a core ability of commercial model families such as QwenVL (Bai et al. 2025) and InternVL (Chen et al. 2025). Consequently, recent work has begun to explore the mechanisms of multimodal ICL (Doveh et al. 2024; Chen et al. 2024b). However, few studies probe internal attention. Therefore, cross-modal interactions in multimodal ICL remain only partially understood, which prevents state-of-theart (SOTA) models from fully exploiting ICL’s potential.

Enhancing Multimodal ICL. Limited use of input-sequence information by LVLMs is considered a major source of instability in multimodal ICL (Liu et al. 2021; Gao, Fisch, and Chen 2021; Li et al. 2023b). Three solution paths have thus emerged. First, task-oriented datasets combined with instruction tuning (Jiang et al. 2024; Chen et al. 2024c) or direct preference optimization (DPO) (Jia et al. 2025) train LVLMs to reason across multiple ICDs. Second, prompt-level methods optimize ICD selection with metrics such as similarity scores and information entropy (Li et al. 2023a; Yang et al. 2024b; Zhou et al. 2024; Wu et al. 2022), or by training automatic selectors (Li et al. 2025d; Yang et al. 2024a). Third, calibration-based methods adjust LVLMs’ final logits using contrastive decoding (Kim et al. 2024; Fazli, Wei, and Zhu 2025; Li et al. 2025a). While these approaches improve performance, they all face challenges. The first requires extensive curated data and parameter updates, the second is less adaptable to fixed-prompt scenarios, and both depend on the base model. The third needs to design distorted input sequences, plus multiple forward passes. In contrast, our CAMA sidesteps all these drawbacks by modulating attention logits at inference time without additional data or tuning.

## Attention Dynamics in Multimodal ICL

## Background and Notation

Current-generation LVLMs generally consist of three core components: a vision encoder that processes images, a projector that converts visual features into embeddings, and an autoregressive LLM that decodes both image and text embeddings to produce output. In multimodal ICL, LVLM typically takes an interleaved image-text sequence as input, as illustrated in Figure 1(a). This work focuses mainly on visual question-answering (VQA), which emphasizes both visual perception and language-based reasoning.

We consider an LVLM M, which generates the answer 𝑦 given an 𝑛-shot sequence 𝑋 as input. 𝑋 consists of 𝑛 incontext demonstrations (ICDs) and a single query sample:

![](images/2e65b9509609be6ba971bf0f3dfb9ce700ebc69d8b09df9e82cbc905114cc6d3.jpg)

![](images/93fcad485f787dab7d6f307b7e012ace8349e964eaf322c2ad8774b6c1f2ff3a.jpg)

![](images/bf1785f7af52fbe303fd555dbfa782bac949f66a833ed5f5bfdc87750b6840a0.jpg)

![](images/f5e2cfd646559f078482ef8f4a7259f946ebb87d22ff70db1a9ed3c35b51e445.jpg)  
Figure 2: Layer-wise trends of the intra-ICD alignment score $s _ { a l i g n }$ and and the key ICD contribution score $s _ { c o n t r i b }$ in efective and inefective multimodal ICL. Pos 1, 2, and 3 denote the key ICD position in the sequence.

$$
\begin{array} { c } { y  M ( X ) , } \\ { \quad } \\ { X = ( X _ { 1 } ^ { I } , X _ { 1 } ^ { T } , \dotsc , X _ { n } ^ { I } , X _ { n } ^ { T } , X _ { n + 1 } ^ { I } , X _ { n + 1 } ^ { T } ) , } \end{array}\tag{1}
$$

where the query sample is indexed as $n + 1$ for unified notations. $X _ { i } ^ { I } \in \mathbb { R } ^ { S _ { i } ^ { I } \times D }$ denotes the token sequence of the 𝑖-th image, $X _ { i } ^ { \dot { T } } \in \mathbb { R } ^ { S _ { i } ^ { T } \times D }$ denotes the token sequence of the 𝑖-th text segment and 𝐷 is the dimensionality of hidden states. $S _ { i } ^ { I }$ and $\mathbf { \Psi } _ { S _ { i } ^ { T } }$ are the token counts of the 𝑖-th image and text segment, respectively. $\begin{array} { r } { S = \sum _ { i = 1 } ^ { n + 1 } ( S _ { i } ^ { I } + S _ { i } ^ { T } ) } \end{array}$ is the total length of the token sequence and S is its index set. Within each ICD, the text tokens can be further divided into a question part and an answer part, whose counts are $S _ { i } ^ { \mathcal { Q } }$ and $S _ { i } ^ { A } . \bar { \mathbf { S } } _ { i } ^ { I } , \mathbf { S } _ { i } ^ { Q }$ and $\mathbf { S } _ { i } ^ { A }$ denote the token index sets for the image, question, and answer of the 𝑖-th ICD, respectively.

The sequence 𝑋 is then passed to the LLM of M, which performs an 𝑁-layer decoder forward pass. Each layer contains a multi-head attention (MHA) module. The ℎ-th head in the 𝑙-th layer maps the hidden states of 𝑋 to queries $Q ^ { l , h } \in \mathbb { R } ^ { S \times D _ { k } }$ , keys $\dot { K } ^ { l , h } \in \mathbb { R } ^ { S \times D _ { k } }$ , and values $V ^ { l , h } \in \dot { \mathbb { R } } ^ { S \times D _ { k } }$ by linear transformations, where $D _ { k }$ is the head dimension. Attention logits $\mathbf { A } ^ { l , h } \in \mathbb { R } ^ { \tilde { S } \times S }$ is given by:

$$
\mathbf { A } ^ { l , h } = \frac { Q ^ { l , h } ( K ^ { l , h } ) ^ { \top } } { \sqrt { D _ { k } } } ,\tag{2}
$$

which directly reveals both the direction and intensity of interactions between any two tokens during the forward pass. After applying a causal mask followed by softmax, $\mathbf { A } ^ { l , \tilde { h } }$ becomes the attention weight matrix that is multiplied with the value $V ^ { l , h }$ to produce the head’s attention output.

## Attention Deficits of LVLMs

To understand the instability of multimodal in-context learning in LVLMs, we delve into the model’s attention mechanism to analyze its dynamics in both efective and inefective scenarios. Our objective is to uncover distinct patterns that distinguish these cases. Specifically, we investigate attention dynamics at two levels: (1) Within each ICD: We examine text-based visual grounding to verify whether the model pays attention to relevant objects in the images. (2) Across ICDs: We evaluate whether the model efectively distributes attention among diferent ICDs according to their relevance to the query. To ensure generalizable experimental results, we experiment with 3-shot settings on two LVLMs: Llava-NeXT-7B (Li et al. 2024) and Idefics2-8B (Laurenc¸on et al. 2024). Query samples and ICDs are taken from the validation and training sets of VQAv2, respectively.

Setups. We pair each query with three ICDs of the same question type (e.g., “How many” or “Is there”) and process the resulting sequences using both LVLMs. From this pool, we identify 2,500 sequences where LLaVA-NeXT-7B produces a correct answer while Idefics2-8B fails, and another 2,500 sequences with the opposite outcome. These form two distinct sets of 5,000 cases each: a “correct” group (indicating efective ICL) and a “wrong” group (indicating inefective ICL). For each sequence, we manually annotate bounding boxes on the ICD images based on their corresponding textual descriptions. We then extract attention maps from each model layer, identify the top 20% most-attended regions, and compute their Intersection over Union (IoU) with the annotated boxes to obtain the intra-ICD alignment score $s _ { \mathrm { a l i g n } } .$ Additionally, we sample 10,000 sequences from the original pool and replace two of the three ICDs in each sequence with unrelated images, leaving only one key ICD relevant to the query type. For each of these sequences, we generate three variants by positioning the key ICD in the first, second, and third slots, respectively. Using the same processing pipeline, we construct new correct and wrong groups of 5,000 cases each. For these, we compute saliency maps (Wang et al. 2023) at each layer and measure the proportion of information flow from the key ICD to the generated answer tokens, relative to the total layer-wise flow. This yields the contribution score $s _ { \mathrm { c o n t r i b } }$ . Experimental details are provided in Appendix 2.

Results. As shown in Figure 2, in the correct group, LVLMs exhibit significantly higher $s _ { \mathrm { a l i g n } }$ in the shallow layers (Layers 2–4), with the largest score gap compared to the wrong group also occurring in these early layers. This suggests that efective ICL relies on aligning visual attention with textual semantics from the outset. Furthermore, in the correct group, $s _ { \mathrm { c o n t r i b } }$ shows a marked increase beginning around Layer 10 and remains consistently high through Layer 20. In contrast, this rise is absent in the wrong group, where scores remain consistently lower. This indicates that mid-layer attention allocation—driven by the relevance of the query—is also critical for successful ICL. We refer to the failure of LVLMs to establish either of these attention dynamics as attention deficits, which contribute to instability in in-context learning. Additionally, we observe that the earlier an ICD appears in the sequence, the lower its alignment and contribution scores across all layers and both groups.

We distill three core findings from the above results:

• Finding 1: In shallow layers, LVLMs struggle to focus on visual information that aligns with the text semantics within each image-text pair.

![](images/9f3f1faef6896d00b2917de94092225c4b40f528d02de7ec8c520487d270c772.jpg)  
Figure 3: An overview pipeline of CAMA. A version with more details is provided in Appendix 1.

• Finding 2: In middle layers, LVLMs struggle to prioritize the key ICDs that match the query.

• Finding 3: Both deficits are amplified by the position of ICDs, with those earlier in the sequence experiencing more severe impacts.

## Method

## Overview

To mitigate the two attention deficits at inference time without training, we introduce Context-Aware Modulated Attention (CAMA). CAMA dynamically reshapes the internal attention logits according to the input sequence during the prefilling process, encouraging the model to focus on the tokens most key to efective ICL. The overall pipeline is depicted in Figure 3. Building on Finding 1 and 2, we divide CAMA into two stages, each attached to a diferent depth of the LLM and mainly aimed at a specific deficit:

• Stage I: In the shallow layers, CAMA performs Intra-ICD grounding. At this stage, for each ICD, we first locate the key image tokens that are essential to justify the provided answer. We then amplify the attention paid to these tokens so the model captures the critical visual cues, laying a solid foundation for subsequent ICL.

• Stage II: In the middle layers, CAMA performs querycentric routing. At this stage, we operate at the attention head level to manage the complex interactions between the query sample and the ICDs. Specifically, we identify the heads that exhibit the strongest query-to-ICD attention and rescale their logits based on the cross-modal similarity between the query and each ICD.

## Stage I: Intra-ICD grounding

Stage I operates on the shallow layer set $\mathcal { L } _ { \mathrm { s t a g e I } }$ , focusing on improving image-text alignment within each ICD to enhance LVLM’s early perception of key visual features. This not only mitigates the early attention deficits but also benefits subsequent layers. To achieve this goal, we first need to identify the key visual tokens in each ICD based on the semantics of its paired Q-A text. However, conventional metrics, such as summing attention scores from text to image tokens or relying on embedding similarity, are inadequate for multimodal ICL, as they may exacerbate attention deficits or fail to capture the nuanced semantics of Q-A dialogues (Marino et al. 2021). To address this, we introduce a dynamic attention increment strategy tailored to multimodal ICDs.

For the 𝑖-th ICD in 𝑋, we designate three anchor tokens $\mathbf { T } _ { i } \mathbf { : }$ the first token of the question ${ \bf S } _ { i } ^ { Q } [ 0 ]$ , the first token of the answer $\mathbf { S } _ { i } ^ { A } [ 0 ]$ and the last token of the answer $\mathbf { S } _ { i } ^ { A } [ - 1 ]$

In our setting, these tokens are typically $^ { 6 6 } \mathrm { Q } ^ { 3 } , \ ^ { 6 6 } \mathrm { A } ^ { 3 }$ , and a punctuation mark (as illustrated in Figure 1(a)). After the first layer, the forward pass enables these tokens to capture and summarize the semantics of the preceding tokens. Therefore, they can be treated as proxies for the overall semantics of the image, the question, and the answer. We begin by computing the attention distributions that these anchor tokens assign to every image token $j \in \mathbf { S } _ { i } ^ { I }$ in layer $l \in \mathcal { L } _ { \mathrm { s t a g e I } } ;$

$$
\begin{array} { r } { P _ { l } ( \mathbf { T } _ { i } ) = \operatorname { s o f t m a x } _ { j } \left( \frac { 1 } { H } \displaystyle \sum _ { h = 1 } ^ { H } \mathbf { A } ^ { l , h } ( \mathbf { T } _ { i } , j ) \right) \in { \mathbb { R } } ^ { 1 \times S _ { i } ^ { I } } , } \end{array}\tag{3}
$$

where $\mathbf { T } _ { i } \in \{ \mathbf { S } _ { i } ^ { Q } [ 0 ] , \mathbf { S } _ { i } ^ { A } [ 0 ] , \mathbf { S } _ { i } ^ { A } [ - 1 ] \}$ denotes the anchor tokens. The inner summation averages the logits over all 𝐻 heads in $l ,$ and the row-wise softmax turns this average into a probability distribution across the image tokens.

Next, we calculate the diferences between these distributions as dynamic attention increments. They provide biasreduced estimates of the image tokens’ contributions to both question understanding and answer making within each ICD. We quantify them by defining two non-negative forward gains $c _ { l , i } ^ { 1 } , \bar { c } _ { l , i } ^ { 2 } \in \dot { \mathbb { R } } ^ { 1 \times S _ { i } ^ { I } }$ in a divergence-like form:

$$
c _ { l , i } ^ { 1 } = \left[ P _ { l } ( \mathbf { S } _ { i } ^ { A } [ 0 ] ) - P _ { l } ( \mathbf { S } _ { i } ^ { Q } [ 0 ] ) \right] _ { + } \log \frac { P _ { l } ( \mathbf { S } _ { i } ^ { A } [ 0 ] ) } { P _ { l } ( \mathbf { S } _ { i } ^ { Q } [ 0 ] ) } ,\tag{4}
$$

$$
c _ { l , i } ^ { 2 } = \left[ P _ { l } ( \mathbf { S } _ { i } ^ { A } [ - 1 ] ) - P _ { l } ( \mathbf { S } _ { i } ^ { A } [ 0 ] ) \right] _ { + } \log \frac { P _ { l } ( \mathbf { S } _ { i } ^ { A } [ - 1 ] ) } { P _ { l } ( \mathbf { S } _ { i } ^ { A } [ 0 ] ) } ,\tag{5}
$$

where $[ \cdot ] _ { + }$ keeps only the positive values by setting all negative ones to zero. After summing the two gains, column 𝑗 is the score of the 𝑗-th image token:

$$
s _ { i , j } = \sum _ { l \in \mathcal { L } _ { \mathrm { s t a g e I } } } ( c _ { l , i } ^ { 1 } + c _ { l , i } ^ { 2 } ) [ j ] .\tag{6}
$$

A larger $s _ { i , j }$ means the token plays a greater role in the visual perception of the image by LVLM based on the corresponding Q-A pair and therefore is more closely aligned with the text semantics. For each 𝑖-th ICD, we take the image token indices with the top-𝑘 % scores and define them as the key set $\mathcal { K } _ { \mathcal { I } _ { i } }$ . Finally, we modulate the attention logits in Eq.2 to amplify the key image tokens’ incoming attention:

$$
\mathbf { A } ^ { l , h } ( r , j ) \xleftarrow { } \mathbf { A } ^ { l , h } ( r , j ) + \frac { n - i + 1 } { n } \frac { s _ { i , j } } { \underset { j ^ { \prime } \in \mathcal { K } _ { T _ { i } } } { \operatorname* { m a x } } s _ { i , j ^ { \prime } } + \epsilon } .\tag{7}
$$

where $j \in \mathcal { K } _ { \bar { I } i }$ and 𝑟 denotes any later token in 𝑋. The factor $( n - i + 1 ) / n$ is used to ofset the position bias noted in Finding 3. Note that during this stage, we also detect and enhance the query sample’s key image tokens through only $c _ { l , n + 1 } ^ { 1 }$ . With intra-ICD grounding, image tokens that align well with corresponding textual semantics receive greater attention in subsequent layers and during answer generation, providing a bias-corrected basis for deeper reasoning.

## Stage II: Query-centric routing

After highlighting the most semantically aligned image tokens in Stage I, Stage II works on the middle layers $\mathcal { L } _ { \mathrm { s t a g e I I } }$ to refine the global information flow under the guidance of the query. Inspired by (Singh et al. 2024), which shows that specific attention heads dominate the information flow from the query sample to ICDs during ICL, we perform fine-grained and targeted modulation at the head level to lessen the influence of other complex interactions in multimodal ICL.

We first use the attention flow from the query sample to the context (i.e., ICDs) as a signal to identify query-centric heads. As information gradually shifts toward later tokens in the middle layers, and text typically exhibits a stronger attention-flow tendency (Gao et al. 2019), we measure the query→context flow using only the query sample’s text. Recall that $\mathbf { S } _ { n + 1 } ^ { T }$ denotes the text token index set of the query sample. For each head ℎ in layer $l \in \mathcal { L } _ { \mathrm { s t a g e I I } } .$ , we compute:

$$
\rho ^ { l , h } = \frac { 1 } { | \mathbf { S } _ { n + 1 } ^ { T } | } \sum _ { q \in \mathbf { S } _ { n + 1 } ^ { T } } \sum _ { c \in \mathbf { S } _ { c t x } } \mathbf { A } ^ { l , h } ( q , c ) ,\tag{8}
$$

where $\begin{array} { r } { \mathbf { S } _ { \mathrm { c t x } } = \bigcup _ { i = 1 } ^ { n } \bigl ( \mathbf { S } _ { i } ^ { I } \cup \mathbf { S } _ { i } ^ { Q } \cup \mathbf { S } _ { i } ^ { A } \bigr ) . \rho _ { l , h } } \end{array}$ aggregates the attention flow from the query sample to the preceding context, allowing us to quantify each head’s contribution in that direction. The heads are then ranked by $\rho _ { l , h } .$ , and the top- ${ k _ { \mathrm { I I } } } \%$ are chosen as query-centric heads, forming the set $\mathcal { H } _ { \iota } ^ { \mathrm { { \bar { Q } C } } }$

Next, we perform ICD-level attention modulation within each query-centric head. In the middle layers, token-level attention becomes blurred by aggregation and is suboptimal for separating the contributions of individual ICDs. Thus, we propose a similarity-based method. To balance semantic maturity and clarity, the hidden states from the final layer of Stage I, $\mathcal { L } _ { \mathrm { s t a g e I } } [ - 1 ]$ , are used for subsequent computations.

For the embeddings of the 𝑖-th ICD taken from $\bar { \mathcal { L } } _ { \mathrm { s t a g e I } } [ - 1 ]$ we compute the mean of the key image tokens $\mathcal { K } _ { \mathcal { T } _ { i } }$ to obtain a visual vector and the mean of all question-and-answer tokens to obtain a textual vector. We then concatenate these two vectors and apply ℓ<sub>2</sub>-normalization to the resulting embedding, yielding the joint representation $p _ { i }$ . We apply the same steps to the query sample to obtain $p _ { \mathrm { q u e r y } }$ . The cosine similarity between $p _ { i }$ and $p _ { \mathrm { q u e r y } }$ is the query-centric score:

$$
w _ { i } = \frac { \exp ( \langle p _ { i } , p _ { \mathrm { q u e r y } } \rangle ) } { \sum _ { k = 1 } ^ { n } \exp ( \langle p _ { k } , p _ { \mathrm { q u e r y } } \rangle ) } .\tag{9}
$$

The score $w _ { i }$ quantifies how semantically relevant each ICD is to the query sample. Applying this score in the query-centric heads mitigates the LVLM’s dificulty in locating crucial contexts and improves answer generation. Specifically, for each head $h \in \mathcal { H } _ { \iota } ^ { \mathrm { Q C } }$ in layer $l \in \mathcal { L } _ { \mathrm { s t a g e I I } }$ , we modulate the attention logits in Eq.2 as follows:

$$
\mathbf { A } ^ { l , h } ( r , J ) \ \gets \ \mathbf { A } ^ { l , h } ( r , J ) + \frac { n - i + 1 } { n } w _ { i } .\tag{10}
$$

We apply this modulation to all key image tokens and text tokens of each ICD to maintain completeness, so $J \in$ $( \mathcal { K } _ { \boldsymbol { \mathcal { I } } i } \cup \mathbf { S } _ { i } ^ { \boldsymbol { Q } } \cup \mathbf { S } _ { i } ^ { \boldsymbol { A } } )$ and 𝑟 denote any subsequent token in 𝑋. (𝑛− $i + 1 ) / n$ applies the same position decay as in Eq.7. Stage II enhances the attention given to each ICD in proportion to its contribution, ensuring that key information is not lost within the extensive context. The two stages of CAMA jointly enable the LVLM to exploit the provided context more efectively. All remaining layers maintain their original attention.

## Experiments

## Setup

Benchmarks and models. Following the standard multimodal ICL evaluation (Awadalla et al. 2023), we test CAMA on VQAv2 (Goyal et al. 2017), VizWiz (Gurari et al. 2018), and OK-VQA (Marino et al. 2019). To further assess the generalization of CAMA, we also evaluate it on GQA (Hudson and Manning 2019), TextVQA (Singh et al. 2019), the CLEVR subset of VL-ICL bench (Zong, Bohdal, and Hospedales 2025), and MMStar (Chen et al. 2024a). In addition to LLaVA-NeXT-7B and Idefics2-8B, we also report results on two latest LVLMs, InternVL2.5-8B (Chen et al. 2025) and Qwen2.5VL-7B (Bai et al. 2025).

Baselines. We compare CAMA with five baselines. (1) Vanilla denotes the vanilla models. (2) The instruction-augmented method (+Inst) add an instruction before each sequence: “First, study the examples we provide. Then utilize what you have learned to answer the new question.” (3) Contrastive decoding (CD) (Lee, Tsai, and Chiu 2024) replaces each ICD image with a blank one and uses the distorted logits to calibrate the original logits. (4) Visual enhancement (VE) (Su et al. 2025) manually draws a red bounding box around the relevant region of each ICD image. (5) SoFt Attention (SoFA) (Tian et al. 2025) is a training-free method that inserts a bidirectional attention mask after every two decoder layers, which reduces position bias when multiple images are contained in the input.

Appendix 3.1 provides further introductions to the benchmarks, models, baselines, and processing details.

Implementation details. For each benchmark, samples in its validation set act as query samples, each paired with eight randomly retrieved ICDs from the training split, forming an 8-shot sequence. Stage I is applied to the 2nd and 3rd layers. Stage II is applied to every second layer from the 7th through the 19th. We set $k _ { \mathrm { I } } = k _ { \mathrm { I I } } = 2 0$ . All experiments are conducted on NVIDIA H200 GPUs.

## Main Results

CAMA is efective and robust across all VQA benchmarks and LVLMs. Table 1 presents accuracy results across seven VQA benchmarks for four LVLMs with varying input image resolutions and LLM decoders. CAMA achieves the highest accuracy in all 28 experiments, surpassing all baselines. On average it raises accuracy over the vanilla models by 2.96%. Notably, stronger models benefit even more: InternVL2.5 and Qwen2.5VL see improvements of 3.61% and 3.15%, respectively, compared to 2.35% on LLaVA-NeXT and 2.73% on Idefics2. These findings demonstrate the strong efectiveness and generalization of CAMA. Thanks to its plug-and-play design, CAMA can consistently benefit the emerging open-source LVLMs, giving it promising practical value. Moreover, by outperforming SoFA’s mask-based strategy, CAMA confirms the advantage of modulating intermediate attention logits.

CAMA can activate the efect of prompt-based methods. We also report results that combine CAMA with a prompt-based baseline, as shown in Table 1 in the rows “CAMA(+Inst)” and “CAMA(VE)”. We find that a promptbased method alone gives only a marginal performance gain, which confirms the attention deficits inside LVLMs. When we add CAMA the model not only improves on its own but also activates the real benefit of these methods. For example, +Inst exceeds the vanilla model by just 0.27%, whereas CAMA lifts this improvement to 3.28% and adds another 0.32% over using CAMA alone. The performance gain brought by CAMA’s activation is most evident on CLEVR, where VE sharply reduces the dificulty of cognizing the original image-text mapping. This result further confirms CAMA’s practical promise, as it allows curated prompts to exert their full efect and maximizes model performance.

<table><tr><td>LVLM</td><td>Method</td><td>VQAV2</td><td>VizWiz</td><td>OK-VQA</td><td>GQA</td><td>TextVQA</td><td>CLEVR</td><td>MMStar</td><td>Avg.</td></tr><tr><td rowspan="7">LLaVA-NeXT</td><td>Vanilla</td><td>61.86</td><td>37.64</td><td>57.63</td><td>55.38</td><td>61.93</td><td>16.50</td><td>44.72</td><td>47.95</td></tr><tr><td>+Inst</td><td>61.69</td><td>38.52</td><td>58.21</td><td>55.70</td><td>61.74</td><td>17.46</td><td>43.95</td><td>48.18</td></tr><tr><td>CD</td><td>61.79</td><td>37.70</td><td>57.48</td><td>55.46</td><td>62.07</td><td>17.18</td><td>41.59</td><td>47.61</td></tr><tr><td>VE</td><td>61.94</td><td>37.58</td><td>57.97</td><td>55.29</td><td>61.78</td><td>18.16</td><td>44.92</td><td>48.23</td></tr><tr><td>SoFA</td><td>63.21</td><td>38.09</td><td>58.14</td><td>57.42</td><td>62.28</td><td>14.29</td><td>45.71</td><td>48.45</td></tr><tr><td>CAMA</td><td>64.46</td><td>39.87</td><td>59.94</td><td>58.60</td><td>63.40</td><td>18.67</td><td>47.16</td><td>50.30</td></tr><tr><td>CAMA(+Inst)</td><td>64.89</td><td>40.23</td><td>60.27</td><td>58.71</td><td>63.61</td><td>21.28</td><td>47.42</td><td>50.92</td></tr><tr><td rowspan="9">Idefics2</td><td>CAMA(VE)</td><td>65.24</td><td>40.67</td><td>60.58</td><td>59.04</td><td>64.07</td><td>23.17</td><td>47.71</td><td>51.50</td></tr><tr><td>Vanilla</td><td>57.32</td><td>38.46</td><td>43.60</td><td>57.49</td><td>70.02</td><td>34.61</td><td>42.65</td><td>49.16</td></tr><tr><td>+Inst</td><td>57.61</td><td>38.25</td><td>43.75</td><td>57.38</td><td>70.30</td><td>35.48</td><td>42.51</td><td>49.21</td></tr><tr><td>CD</td><td>56.83</td><td>38.19</td><td>43.47</td><td>57.30</td><td>68.87</td><td>33.70</td><td>41.49</td><td>48.55</td></tr><tr><td>VE</td><td>57.28</td><td>38.89</td><td>44.26</td><td>57.98</td><td>71.18</td><td>36.41</td><td>42.93</td><td>49.85</td></tr><tr><td>SoFA</td><td>59.04</td><td>38.95</td><td>46.12</td><td>57.75</td><td>72.31</td><td>34.44</td><td>43.29</td><td>50.27</td></tr><tr><td>CAMA</td><td>60.53</td><td>39.90</td><td>47.23</td><td>59.79</td><td>74.38</td><td>36.52</td><td>44.86</td><td>51.89</td></tr><tr><td>CAMA(+Inst)</td><td>60.74</td><td>40.37</td><td>47.69</td><td>60.00</td><td>76.21</td><td>38.95</td><td>44.59</td><td>52.40</td></tr><tr><td>CAMA(VE)</td><td>60.82</td><td>40.16</td><td>47.80</td><td>60.08</td><td>75.72</td><td>39.58</td><td>45.27</td><td>52.78</td></tr><tr><td rowspan="8">InternVL2.5</td><td>Vanilla</td><td>69.58</td><td>58.27</td><td>62.32</td><td>67.21</td><td>80.29</td><td>56.91</td><td>62.70</td><td>65.33</td></tr><tr><td>+Inst</td><td>69.89</td><td>58.92</td><td>62.18</td><td>67.53</td><td>81.10</td><td>57.34</td><td>62.38</td><td></td></tr><tr><td>CD</td><td>69.81</td><td>58.79</td><td>63.01</td><td>67.54</td><td>80.17</td><td>57.11</td><td>62.56</td><td>65.53 65.57</td></tr><tr><td>VE</td><td>69.80</td><td>58.96</td><td>63.14</td><td>67.28</td><td>80.39</td><td>59.53</td><td>62.95</td><td></td></tr><tr><td>SoFA</td><td>70.85</td><td>59.62</td><td>62.48</td><td>68.30</td><td>82.75</td><td>59.12</td><td>62.70</td><td>66.00</td></tr><tr><td>CAMA</td><td>72.54</td><td>62.15</td><td>66.27</td><td>70.68</td><td>85.19</td><td>61.45</td><td>64.27</td><td>66.55</td></tr><tr><td>CAMA(+Inst)</td><td>72.61</td><td>62.48</td><td>65.58</td><td>70.93</td><td>85.46</td><td>64.67</td><td>63.37</td><td>68.94</td></tr><tr><td>CAMA(VE)</td><td>72.85</td><td>64.57</td><td>66.73</td><td>71.30</td><td>85.66</td><td>64.90</td><td>63.79</td><td>68.97</td></tr><tr><td rowspan="8">Qwen2.5VL</td><td>Vanilla</td><td>71.94</td><td>57.39</td><td></td><td></td><td></td><td></td><td></td><td>69.97</td></tr><tr><td></td><td>72.43</td><td></td><td>65.70</td><td>82.31</td><td>83.61</td><td>62.83</td><td>65.18</td><td>69.85</td></tr><tr><td>+Inst</td><td></td><td>57.80</td><td>66.18</td><td>83.57</td><td>83.72</td><td>63.65</td><td>66.03</td><td>70.43</td></tr><tr><td>CD</td><td>72.31</td><td>57.35</td><td>66.07</td><td>82.49</td><td>83.76</td><td>62.72</td><td>65.63</td><td>70.05</td></tr><tr><td>VE</td><td>72.69</td><td>59.30</td><td>66.41</td><td>84.55</td><td>83.92</td><td>63.26</td><td>66.47</td><td>70.94</td></tr><tr><td>SoFA</td><td>72.31</td><td>59.06</td><td>67.28</td><td>84.52</td><td>84.34</td><td>64.85</td><td>66.87</td><td>71.32</td></tr><tr><td>CAMA</td><td>74.96</td><td>60.83</td><td>68.80</td><td>85.32</td><td>87.14</td><td>66.15</td><td>67.78</td><td>73.00</td></tr><tr><td>CAMA(+Inst) CAMA(VE)</td><td>74.79 75.22</td><td>61.28 62.37</td><td>69.21 69.74</td><td>85.26 85.69</td><td>86.87 87.89</td><td>67.02 66.81</td><td>67.39 67.70</td><td>73.12 73.63</td></tr></table>

Table 1: Accuracy of 8-shot ICL on seven VQA benchmarks for four LVLMs under diferent enhancement methods. The highest value is highlighted in bold, and the second highest is underlined. The cells shaded in light gray present the results of CAMA.

<table><tr><td>Method</td><td>Image captioning Flickr30k MSCOCO</td><td>Hatefulmemes</td><td>Classification Storytelling L-I-VST</td></tr><tr><td>Vanilla</td><td>69.93 112.46</td><td>75.16</td><td>38.61</td></tr><tr><td>+Inst</td><td>71.28 114.36</td><td>76.20</td><td>38.46</td></tr><tr><td>CD</td><td>72.35 114.97</td><td>74.38</td><td>40.32</td></tr><tr><td>SoFA</td><td>72.65 115.89</td><td>76.51</td><td>40.41</td></tr><tr><td>CAMA</td><td>73.88 116.72</td><td>77.49</td><td>41.79</td></tr><tr><td>CAMA(+Inst)</td><td>74.37</td><td>117.04 77.93</td><td>42.38</td></tr></table>

Table 2: Average performance of 8-shot multimodal ICL on four benchmarks spanning three additional tasks, reported using CIDEr↑ , ROC-AUC↑, and L-I-score↑, respectively.

CAMA exhibits strong cross-task generalization. To fully evaluate the generalization of CAMA, we introduce three additional tasks beyond VQA: image captioning, image classification, and visual storytelling. In these tasks, the text paired with each image is no longer a Q-A pair; instead, it is a caption, a class label, or a narrative sentence, and all three start with the prefix “A:”. The text part of the query sample only contains $\mathbf { \ddot { A } } \mathbf { \dot { : } } \mathbf { \vec { \mu } }$ . Therefore, for these tasks, Stage I of CAMA is based solely on attention gains $c _ { l , i } ^ { 1 }$ to identify key image tokens. The results are reported in Table 2. CAMA again achieves superior performance on all these tasks and activates the gains of +Inst, showing that its benefits extend beyond VQA to broader interleaved scenarios.

## Ablation Study and Analyses

Adaptability to diverse ICD counts. It is non-trivial for enhancement methods to adapt to diferent shot counts to meet various practical needs. As Figure 4(a) shows, CAMA consistently outperforms the vanilla model in 2, 4, 8, and 16-shot configurations, yielding gains of 2.15% to 6.52%. These results validate CAMA’s generalization across diverse scenarios and its ability to meet varying requirements. Meanwhile, CAMA’s advantage grows as the sequence length increases, which aligns with Finding 3 because longer contexts intensify positional bias. As LVLM context windows expand and many-shot ICL becomes feasible, CAMA provides a promising path for further progress.

![](images/e0335ca6ebcaa8268af5c371333d534958bb973213226d1671bd4ecebec71186.jpg)

![](images/e5057c6a27c1652b57060837f9caaa1493612fd70b99a52f4485583b41cc789d.jpg)  
Figure 4: Average performance ofCAMA across four LVLMs and seven VQA benchmarks as the count of ICDs and sequence configuration strategies vary.

<table><tr><td>Method</td><td colspan="4">VQAv2 VizWiz OK-VQA GQA TextVQA</td></tr><tr><td>CAMA</td><td>68.12</td><td>50.69 60.56</td><td>68.60</td><td>77.53</td></tr><tr><td>w/o Stage I</td><td>67.05</td><td>49.23 48.87</td><td>59.46 68.09</td><td>76.99</td></tr><tr><td>w/o Stage II</td><td>66.41</td><td>58.40</td><td>67.21</td><td>76.08</td></tr><tr><td colspan="5">Stage I</td></tr><tr><td>w/o increment</td><td>67.14 48.86</td><td>59.28</td><td>67.39</td><td>76.80</td></tr><tr><td>w/o top-k1%</td><td>67.44 50.10</td><td>59.82</td><td>67.93</td><td>77.14</td></tr><tr><td>w/o position</td><td>67.91 50.12</td><td>60.02</td><td>68.05</td><td>76.98</td></tr><tr><td colspan="5">Stage II</td></tr><tr><td>w/o top-k11%</td><td>67.18</td><td>49.25</td><td>59.84 68.11</td><td>76.69</td></tr><tr><td> $L _ { \mathrm { s t a g e I } } [ 0 ]$ </td><td>67.85</td><td>49.16 60.28</td><td>68.20</td><td>77.05</td></tr><tr><td>w/o position</td><td>68.03</td><td>49.84</td><td>60.19 68.20</td><td>77.12</td></tr></table>

Table 3: Average 8-shot performance of CAMA on four LVLMs under diferent ablation settings. “w/o increment” disables dynamic attention increment and computes the attention score using only $\mathbf { S } _ { i } ^ { A } [ - 1 ]$ . “w/o top $k _ { \mathrm { I } } \mathrm { { ^ { q } o } } / k _ { \mathrm { I I } } \mathrm { { ^ { q } o } } ^ { \mathrm { { , * } } }$ applies CAMA to all image tokens or heads. $\^ { \mathrm { \sc } } \bar { L } _ { \mathrm { s t a g e I } } [ 0 ] ^ { \mathrm { \sc , } }$ computes similarity with embeddings from $L _ { \mathrm { s t a g e I } } [ 0 ]$ . “w/o position” removes the position-decay factor.

Adaptability to diverse sequence configurations. The in-context sequence configuration is key to ICL performance. Our main experiments build sequences using uniform random sampling (RS), whereas some advanced systems leverage embedding similarity to improve sequence quality further. Each candidate ICD and the query sample are encoded using CLIP-ViT-L/14 to compute cosine similarity, and the top eight matches are selected as ICDs. I2I uses image embeddings only, while IQ2IQ concatenates image and question embeddings. We also adopt TACO (Li et al. 2025d), a SOTA language-model-based ICD retriever. As shown in Figure 4(b), CAMA consistently improves accuracy by 2.59% to 5.08%. Stronger retrieval brings larger gains, indicating that CAMA’s activation efect also applies to configuration methods. This compatibility allows CAMA to integrate smoothly with future ICL advances.

The superiority of CAMA designs. We conduct a comprehensive ablation study on the two stages of CAMA and the key components within each stage (Table 3). Removing either Stage I or Stage II leads to a noticeable drop in performance, with the absence of Stage II resulting in a more substantial degradation. This confirms that the two-stage modulation is necessary and that stronger query-guided reasoning is more crucial for multimodal ICL. Disabling each key design of a stage also produces diferent levels of degradation. We draw the following conclusions: (1) Selecting the key image tokens is essential when enhancing image tokens in shallow layers. It prevents our modulation from being diluted by the later softmax. (2) Query-centric heads play a vital role in multimodal ICL. Targeted enhancement of these heads promotes specific information flows. (3) The dynamic attention increment cleverly avoids the bias introduced by the attention sink. (4) The position-decay factor in CAMA efectively alleviates position bias when LVLMs perform ICL with long sequences, preventing crucial information at the beginning of the sequence from being overlooked. This is particularly important in multimodal ICL, where each image consumes a large number of tokens and leads to long contexts, thereby improving overall performance. Intuitively, as the number of ICD shots increases, the role of the position factor becomes more significant, as discussed in Appendix 3.2.

![](images/73dde88bf2667ca54c08266dc86367ad8503da2cfa2c2fe29d28ec7ebf140623.jpg)  
Figure 5: Average performance of CAMA on seven VQA benchmarks while varying $L _ { \mathrm { s t a g e I } }$ $L _ { \mathrm { { s t a g e I I } } }$ <sub>I</sub>, 𝑘<sub>I</sub> $k _ { \mathrm { { I } } } .$ , and $k _ { \mathrm { I I } }$ . Random7 means randomly choosing seven layers.

Impact of the selection of layers and hyperparameters. As shown in Figure 5, the performance of CAMA remains stable as we vary the layers where the two stages are applied. Meanwhile, when $k _ { \mathrm { I } }$ is set between 20% and $4 0 \%$ CAMA stays consistent, and when $k _ { \mathrm { I I } }$ is between 10% and 30%, CAMA also stays consistent. This behavior indicates that query-centric heads are more targeted than key image tokens, yet both possess a relatively wide optimal range. The results demonstrate that CAMA is robust to layer and hyperparameter choices and does not require carefully curated tuning strategies, highlighting its practicality and eficiency. Case Study. In the case of Figure 1, we observe that CAMA reshapes attention, guiding the model to focus on visual features aligned with the text and relevant to the query. This shows the depth of CAMA’s ability to address attention deficits. We provide additional qualitative visualizations and failure case analysis in Appendix 3.4. For challenging tasks like CLEVR with vague text, Stage I’s dynamic attention increment helps locate key tokens. For MMStar, which involves complex long-text tasks, CAMA enables deeper reasoning. This highlights CAMA’s potential in complicated or reasoning-intensive scenarios, such as multimodal Chain-of-Thought (CoT) (Zhang et al. 2023).

## Conclusion

We introduce CAMA, a training-free and plug-and-play attention modulation method that enhances multimodal ICL. We begin by analyzing the attention dynamics of LVLMs in this setting and, guided by the findings, design a two-stage modulation pipeline for CAMA. CAMA efectively corrects attention deficits and guides the model to focus on image regions that contribute the most to multimodal ICL. Experiments across multiple benchmarks and LVLMs show that CAMA achieves superior results. We believe that CAMA can inspire new directions for future advances of LVLM.

Limitations. As CAMA needs to modulate LVLM’s attention, it introduces additional latency compared with the vanilla model. However, this latency is acceptable, especially in light of the performance gains brought by CAMA. An efficiency analysis is provided in Appendix 3.5.

## Acknowledgments

We acknowledge the computing resources provided by NSF ACCESS.

## References

Alayrac, J.-B.; Donahue, J.; Luc, P.; Miech, A.; Barr, I.; Hasson, Y.; Lenc, K.; Mensch, A.; Millican, K.; Reynolds, M.; et al. 2022. Flamingo: a visual language model for fewshot learning. Advances in neural information processing systems, 35: 23716–23736.

Awadalla, A.; Gao, I.; Gardner, J.; Hessel, J.; Hanafy, Y.; Zhu, W.; Marathe, K.; Bitton, Y.; Gadre, S.; Sagawa, S.; Jitsev, J.; Kornblith, S.; Koh, P. W.; Ilharco, G.; Wortsman, M.; and Schmidt, L. 2023. OpenFlamingo: An Open-Source Framework for Training Large Autoregressive Vision-Language Models. arXiv:2308.01390.

Bai, S.; Chen, K.; Liu, X.; Wang, J.; Ge, W.; Song, S.; Dang, K.; Wang, P.; Wang, S.; Tang, J.; Zhong, H.; Zhu, Y.; Yang, M.; Li, Z.; Wan, J.; Wang, P.; Ding, W.; Fu, Z.; Xu, Y.; Ye, J.; Zhang, X.; Xie, T.; Cheng, Z.; Zhang, H.; Yang, Z.; Xu, H.; and Lin, J. 2025. Qwen2.5-VL Technical Report. arXiv:2502.13923.

Brown, T. B.; Mann, B.; Ryder, N.; Subbiah, M.; Kaplan, J.; Dhariwal, P.; Neelakantan, A.; Shyam, P.; Sastry, G.; Askell, A.; Agarwal, S.; Herbert-Voss, A.; Krueger, G.; Henighan, T.; Child, R.; Ramesh, A.; Ziegler, D. M.; Wu, J.; Winter, C.; Hesse, C.; Chen, M.; Sigler, E.; Litwin, M.; Gray, S.; Chess, B.; Clark, J.; Berner, C.; McCandlish, S.; Radford, A.; Sutskever, I.; and Amodei, D. 2020. Language Models are Few-Shot Learners. arXiv:2005.14165.

Chen, L.; Li, J.; Dong, X.; Zhang, P.; Zang, Y.; Chen, Z.; Duan, H.; Wang, J.; Qiao, Y.; Lin, D.; et al. 2024a. Are we on the right way for evaluating large vision-language models? Advances in Neural Information Processing Systems, 37: 27056–27087.

Chen, S.; Han, Z.; He, B.; Liu, J.; Buckley, M.; Qin, Y.; Torr, P.; Tresp, V.; and Gu, J. 2024b. Can Multimodal Large Language Models Truly Perform Multimodal In-Context Learning? arXiv:2311.18021.

Chen, T.; Zhang, E.; Gao, Y.; Li, K.; Sun, X.; Zhang, Y.; Li, H.; and Ji, R. 2024c. Mmict: Boosting multi-modal finetuning with in-context examples. ACM Transactions on Multimedia Computing, Communications and Applications.

Chen, Y.; Zhao, C.; Yu, Z.; McKeown, K.; and He, H. 2024d. On the Relation between Sensitivity and Accuracy in Incontext Learning. arXiv:2209.07661.

Chen, Z.; Wang, W.; Cao, Y.; Liu, Y.; Gao, Z.; Cui, E.; Zhu,J.; Ye, S.; Tian, H.; Liu, Z.; Gu, L.; Wang, X.; Li, Q.; Ren, Y.;Chen, Z.; Luo, J.; Wang, J.; Jiang, T.; Wang, B.; He, C.; Shi,B.; Zhang, X.; Lv, H.; Wang, Y.; Shao, W.; Chu, P.; Tu, Z.;He, T.; Wu, Z.; Deng, H.; Ge, J.; Chen, K.; Zhang, K.; Wang,L.; Dou, M.; Lu, L.; Zhu, X.; Lu, T.; Lin, D.; Qiao, Y.; Dai,J.; and Wang, W. 2025. Expanding Performance Boundariesof Open-Source Multimodal Models with Model, Data, andTest-Time Scaling. arXiv:2412.05271.

Dong, Q.; Li, L.; Dai, D.; Zheng, C.; Ma, J.; Li, R.; Xia, H.; Xu, J.; Wu, Z.; Liu, T.; Chang, B.; Sun, X.; Li, L.; and Sui, Z. 2024. A Survey on In-context Learning. arXiv:2301.00234.

Doveh, S.; Perek, S.; Mirza, M. J.; Lin, W.; Alfassy, A.; Arbelle, A.; Ullman, S.; and Karlinsky, L. 2024. Towards multimodal in-context learning for vision & language models. arXiv preprint arXiv:2403.12736.

Fazli, M.; Wei, B.; and Zhu, Z. 2025. Mitigating Hallucination in Large Vision-Language Models via Adaptive Attention Calibration. arXiv preprint arXiv:2505.21472.

Fu, T.; Xu, X.; Xu, W.; Chen, J.; Ren, R.; Deng, B.; Zhao, X.; Cao, J.; and Cao, X. 2025. Two Heads are Better than One: Distilling Large Language Model Features Into Small Models with Feature Decomposition and Mixture. arXiv:2511.07110.

Gao, P.; Jiang, Z.; You, H.; Lu, P.; Hoi, S. C.; Wang, X.; and Li, H. 2019. Dynamic fusion with intra-and inter-modality attention flow for visual question answering. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, 6639–6648.

Gao, T.; Fisch, A.; and Chen, D. 2021. Making Pre-trained Language Models Better Few-shot Learners. arXiv:2012.15723.

Goyal, Y.; Khot, T.; Summers-Stay, D.; Batra, D.; and Parikh, D. 2017. Making the V in VQA Matter: Elevating the Role of Image Understanding in Visual Question Answering. In Conference on Computer Vision and Pattern Recognition (CVPR).

Guo, Q.; Wang, L.; Wang, Y.; Ye, W.; and Zhang, S. 2024. What makes a good order of examples in in-context learning. In Findings of the Association for Computational Linguistics: ACL 2024, 14892–14904.

Gurari, D.; Li, Q.; Stangl, A. J.; Guo, A.; Lin, C.; Grauman, K.; Luo, J.; and Bigham, J. P. 2018. VizWiz Grand Challenge: Answering Visual Questions from Blind People. arXiv:1802.08218.

Huang, S.; Luo, H.; Jing, H.; Zhang, Q.; Chang, L.; Feng, Y.; Lin, X.; Qin, C.; Chen, H.; Jia, S.; et al. 2025. NEED: Cross-Subject and Cross-Task Generalization for Video and Image Reconstruction from EEG Signals. In The Thirtyninth Annual Conference on Neural Information Processing Systems.

Hudson, D. A.; and Manning, C. D. 2019. GQA: A New Dataset for Real-World Visual Reasoning and Compositional Question Answering. arXiv:1902.09506.

Jia, H.; Jiang, C.; Xu, H.; Ye, W.; Dong, M.; Yan, M.; Zhang, J.; Huang, F.; and Zhang, S. 2025. Symdpo: Boosting incontext learning of large multimodal models with symbol demonstration direct preference optimization. In Proceedings of the Computer Vision and Pattern Recognition Conference, 9361–9371.

Jiang, D.; He, X.; Zeng, H.; Wei, C.; Ku, M.; Liu, Q.; and Chen, W. 2024. Mantis: Interleaved multi-image instruction tuning. arXiv preprint arXiv:2405.01483.

Kiela, D.; Firooz, H.; Mohan, A.; Goswami, V.; Singh, A.; Ringshia, P.; and Testuggine, D. 2020. The hateful memes challenge: Detecting hate speech in multimodal memes. Advances in neural information processing systems, 33: 2611– 2624.

Kim, Y.; Kim, H. J.; Park, C.; Park, C.; Cho, H.; Kim, J.; Yoo, K. M.; Lee, S.-g.; and Kim, T. 2024. Adaptive contrastive decoding in retrieval-augmented generation for handling noisy contexts. arXiv preprint arXiv:2408.01084.

Laurenc¸on, H.; Tronchon, L.; Cord, M.; and Sanh, V. 2024. What matters when building vision-language models? Advances in Neural Information Processing Systems, 37: 87874–87907.

Laurenc¸on, H.; Marafioti, A.; Sanh, V.; and Tronchon, L. 2024. Building and better understanding vision-language models: insights and future directions. arXiv:2408.12637.

Lee, Y.-L.; Tsai, Y.-H.; and Chiu, W.-C. 2024. Delve into visual contrastive decoding for hallucination mitigation oflarge vision-language models. arXiv preprint arXiv:2412.06775.

Li, F.; Zhang, R.; Zhang, H.; Zhang, Y.; Li, B.; Li, W.; Ma, Z.; and Li, C. 2024. Llava-next-interleave: Tackling multiimage, video, and 3d in large multimodal models. arXiv preprint arXiv:2407.07895.

Li, J.; Zhang, J.; Jie, Z.; Ma, L.; and Li, G. 2025a. Mitigating hallucination for large vision language model by intermodality correlation calibration decoding. arXiv preprint arXiv:2501.01926.

Li, L.; Peng, J.; Chen, H.; Gao, C.; and Yang, X. 2023a. How to Configure Good In-Context Sequence for Visual Question Answering. arXiv:2312.01571.

Li, Q.; Ye, Z.; Feng, X.; Zhong, W.; Ma, W.; and Feng, X. 2025b. Causal Tracing of Object Representations in Large Vision Language Models: Mechanistic Interpretability and Hallucination Mitigation. arXiv preprint arXiv:2511.05923.

Li, X.; Lv, K.; Yan, H.; Lin, T.; Zhu, W.; Ni, Y.; Xie, G.; Wang, X.; and Qiu, X. 2023b. Unified Demonstration Retriever for In-Context Learning. arXiv:2305.04320.

Li, Y. 2025. Advancing Multimodal In-Context Learning in Large Vision-Language Models with Task-aware Demonstrations. arXiv preprint arXiv:2503.04839.

Li, Y.; He, H.; Cao, Y.; Cheng, Q.; Fu, X.; and Tang, R. 2025c. M2IV: Towards Eficient and Fine-grained Multimodal In-Context Learning in Large Vision-Language Models. arXiv preprint arXiv:2504.04633.

Li, Y.; Yun, T.; Yang, J.; Feng, P.; Huang, J.; and Tang, R. 2025d. TACO: Enhancing Multimodal In-context Learning via Task Mapping-Guided Sequence Configuration. arXiv preprint arXiv:2505.17098.

Lin, T.-Y.; Maire, M.; Belongie, S.; Hays, J.; Perona, P.; Ramanan, D.; Dollar, P.; and Zitnick, C. L. 2014. Microsoft´ coco: Common objects in context. In European conference on computer vision, 740–755. Springer.

Liu, H.; Li, C.; Wu, Q.; and Lee, Y. J. 2023. Visual instruction tuning. Advances in neural information processing systems, 36: 34892–34916.

Liu, J.; Shen, D.; Zhang, Y.; Dolan, B.; Carin, L.; and Chen, W. 2021. What Makes Good In-Context Examples for GPT-3? arXiv:2101.06804.

Liu, S.; Zheng, K.; and Chen, W. 2024. Paying More Attention to Image: A Training-Free Method for Alleviating Hallucination in LVLMs. arXiv:2407.21771.

Lu, Y.; Bartolo, M.; Moore, A.; Riedel, S.; and Stenetorp, P. 2022. Fantastically Ordered Prompts and Where to Find Them: Overcoming Few-Shot Prompt Order Sensitivity. arXiv:2104.08786.

Marino, K.; Chen, X.; Parikh, D.; Gupta, A.; and Rohrbach, M. 2021. Krisp: Integrating implicit and symbolic knowledge for open-domain knowledge-based vqa. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, 14111–14121.

Marino, K.; Rastegari, M.; Farhadi, A.; and Mottaghi, R. 2019. OK-VQA: A Visual Question Answering Benchmark Requiring External Knowledge. arXiv:1906.00067.

Singh, A.; Natarajan, V.; Shah, M.; Jiang, Y.; Chen, X.; Batra, D.; Parikh, D.; and Rohrbach, M. 2019. Towards VQA Models That Can Read. arXiv:1904.08920.

Singh, A. K.; Moskovitz, T.; Hill, F.; Chan, S. C.; and Saxe, A. M. 2024. What needs to go right for an induction head? a mechanistic study of in-context learning circuits and their formation. arXiv preprint arXiv:2404.07129.

Su, Z.; Xia, P.; Guo, H.; Liu, Z.; Ma, Y.; Qu, X.; Liu, J.; Li, Y.; Zeng, K.; Yang, Z.; et al. 2025. Thinking with Images for Multimodal Reasoning: Foundations, Methods, and Future Frontiers. arXiv preprint arXiv:2506.23918.

Tian, X.; Zou, S.; Yang, Z.; and Zhang, J. 2025. Identifying and Mitigating Position Bias of Multi-image Vision-Language Models. arXiv preprint arXiv:2503.13792.

Wang, L.; Li, L.; Dai, D.; Chen, D.; Zhou, H.; Meng, F.; Zhou, J.; and Sun, X. 2023. Label Words are Anchors: An Information Flow Perspective for Understanding In-Context Learning. In Bouamor, H.; Pino, J.; and Bali, K., eds., Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, 9840–9855. Singapore: Association for Computational Linguistics.

Wies, N.; Levine, Y.; and Shashua, A. 2023. The learnability of in-context learning. Advances in Neural Information Processing Systems, 36: 36637–36651.

Wu, Z.; Wang, Y.; Ye, J.; and Kong, L. 2022. Self-adaptive in-context learning: An information compression perspective for in-context example selection and ordering. arXiv preprint arXiv:2212.10375.

Yang, X.; Peng, Y.; Ma, H.; Xu, S.; Zhang, C.; Han, Y.; and Zhang, H. 2024a. Lever LM: configuring in-context sequence to lever large vision language models. Advances in Neural Information Processing Systems, 37: 100341–100368.

Yang, X.; Wu, Y.; Yang, M.; Chen, H.; and Geng, X. 2024b. Exploring Diverse In-Context Configurations for Image Captioning. arXiv:2305.14800.

Ye, Q.; Xu, H.; Xu, G.; Ye, J.; Yan, M.; Zhou, Y.; Wang, J.; Hu, A.; Shi, P.; Shi, Y.; et al. 2023. mplug-owl: Modularization empowers large language models with multimodality. arXiv preprint arXiv:2304.14178.

Ye, Z.; Li, Q.; Feng, X.; Qin, L.; Huang, Y.; Li, B.; Jiang, K.; Xiang, Y.; Zhang, Z.; Lu, Y.; et al. 2025. CLAIM: Mitigating Multilingual Object Hallucination in Large Vision-Language Models with Cross-Lingual Attention Intervention. arXiv preprint arXiv:2506.11073.

Young, P.; Lai, A.; Hodosh, M.; and Hockenmaier, J. 2014. From image descriptions to visual denotations: New similarity metrics for semantic inference over event descriptions. Transactions of the Association for Computational Linguistics, 2: 67–78.

Zhang, D.; Lei, J.; Li, J.; Wang, X.; Liu, Y.; Yang, Z.; Li, J.; Wang, W.; Yang, S.; Wu, J.; et al. 2025. Critic-v: Vlm critics help catch vlm errors in multimodal reasoning. In Proceedings ofthe Computer Vision and Pattern Recognition Conference, 9050–9061.

Zhang, Z.; Zhang, A.; Li, M.; Zhao, H.; Karypis, G.; and Smola, A. 2023. Multimodal chain-of-thought reasoning in language models. arXiv preprint arXiv:2302.00923.

Zhao, W. X.; Zhou, K.; Li, J.; Tang, T.; Wang, X.; Hou, Y.; Min, Y.; Zhang, B.; Zhang, J.; Dong, Z.; Du, Y.; Yang, C.; Chen, Y.; Chen, Z.; Jiang, J.; Ren, R.; Li, Y.; Tang, X.; Liu, Z.; Liu, P.; Nie, J.-Y.; and Wen, J.-R. 2025. A Survey of Large Language Models. arXiv:2303.18223.

Zhou, Y.; Li, X.; Wang, Q.; and Shen, J. 2024. Visual incontext learning for large vision-language models. arXiv preprint arXiv:2402.11574.

Zong, Y.; Bohdal, O.; and Hospedales, T. 2025. VL-ICL Bench: The Devil in the Details of Multimodal In-Context Learning. arXiv:2403.13164.

## Appendix

## 1 Figure of Pipeline

We present a detailed version of CAMA’s pipeline in Figure 6.

## 2 Experiments on Attention Deficits in LVLMs

Query–ICD Pairing and Dataset Construction. We conduct experiments on the VQAv2 dataset. In the training set, each instance consists of an image, a question, and an answer. The validation set does not include answers. We treat every example in the validation set as a query sample. For each query sample, we randomly retrieve three instances with the same question type from the training set based on the annotated question type (e.g. ”Is there” and ”How many”). These instances serve as ICDs for the given query sample. The resulting 4-tuple

$$
s _ { i } = \left\{ \mathrm { I C D } _ { i , 1 } , \mathrm { I C D } _ { i , 2 } , \mathrm { I C D } _ { i , 3 } , q _ { i } \right\}\tag{11}
$$

forms a homogeneous 3-shot in-context sequence. This yields a corpus ${ \cal { S } } = \{ s _ { i } \} _ { i = 1 } ^ { N }$ whose size 𝑁 matches VQAv2’s validation set.

Model Inference and Correct / Wrong Split. Each sequence $s _ { i }$ is fed into two LVLMs, LLaVA-NeXT-7B $( M _ { 1 } )$ and Idefics2-8B (M ), producing answers $\hat { a } _ { i } ^ { ( 1 ) }$ and $\hat { a } _ { i } ^ { ( 2 ) }$ , respectively. Comparing them with the ground-truth $\dot { a } _ { i } ^ { \star }$ , we collect

$$
C _ { 1 } = \Big \{ s _ { i } \big | \hat { a } _ { i } ^ { ( 1 ) } = a _ { i } ^ { \star } , \hat { a } _ { i } ^ { ( 2 ) } \neq a _ { i } ^ { \star } \Big \} ,\tag{12}
$$

$$
C _ { 2 } = \Big \{ s _ { i } \big | \hat { a } _ { i } ^ { ( 1 ) } \neq a _ { i } ^ { \star } , \hat { a } _ { i } ^ { ( 2 ) } = a _ { i } ^ { \star } \Big \} .\tag{13}
$$

We randomly sample 2,500 sequences from each of $C _ { 1 }$ and $C _ { 2 } ,$ and each sequence corresponds to one correct case and one wrong case. Consequently, we obtain two case groups: the correct group $\mathcal { G } _ { \mathrm { c o r r e c t } }$ and, symmetrically, a wrong group $\mathcal { G } _ { \mathrm { w r o n g } }$ of the same size (5,000 each). We use $\mathcal { G } _ { \mathrm { c o r r e c t } }$ to represent efective ICL and $\mathcal { G } _ { \mathrm { w r o n g } }$ to represent inefective ICL.

Intra-ICD Alignment Score $s _ { \mathbf { a l i g n } } .$ For every ICD position $p \in \{ 1 , 2 , 3 \}$ within a sequence $s _ { i } .$ , we manually annotate the regions in its image that are related to the semantics of the corresponding $\mathbf { Q - \bar { A } }$ pair with red bounding boxes, denoted as $\mathcal { B } _ { i , p } .$ . Each $\mathcal { B } _ { i , p }$ contains the visual cues necessary to derive the answer from the question. We conduct two additional human verification passes on the annotations to ensure their reliability. At decoder layer 𝑙 we extract the attention matrix $\mathbf { A } _ { i , l } \in \mathbb { R } ^ { S ^ { \mathrm { \mathrm { { t o t a l } } } _ { i } } \times S ^ { \mathrm { { t o t a l } } _ { i } } }$ , where $S ^ { \mathrm { t o t a l } _ { i } }$ denotes the total length of $s _ { i }$ and the generated tokens. We convert it to a heat map $\mathbf { H } _ { i , l }$ via row-wise max–normalization. Let $\mathcal { V } _ { i , p }$ denote the set of visual tokens of $\mathrm { I C D } _ { i , p }$ . We extract the top-20% highestvalued tokens within $\ddot { \mathcal { V } _ { i , p } }$ to form the salient region:

$$
R _ { i , p , l } \ = \ \mathrm { T o p } \mathrm { - } 2 0 \% \big ( \mathbf { H } _ { i , l } ( \nu ) \big ) .\tag{14}
$$

The layer-wise alignment score for $\mathrm { I C D } _ { i , p }$ at the 𝑖-th decoder layer is defined as:

$$
s _ { \mathrm { a l i g n } } ^ { ( i , p ) } ( l ) = \mathrm { I o U } ( \mathcal { R } _ { i , p , l } , \mathcal { B } _ { i , p } ) ,\tag{15}
$$

where IoU(·, ·) denotes the computation of Intersection over Union (IoU) and $\mathcal { R } _ { i , p , l }$ is the image region composed of $R _ { i , p , l }$ . We compute the alignment scores for every case in G<sub>correct</sub> and $\mathcal { G } _ { \mathrm { w r o n g } }$ . A higher $s _ { \mathrm { a l i g n } }$ indicates that the LVLM focuses more on regions within each image that are semantically aligned with the paired text during multimodal ICL.

![](images/949db3d77463476c3c48c023f66a1c6b5e71396036ae05f1bb69f6627017d015.jpg)  
Figure 6: Overview pipeline of CAMA. CAMA consists of two stages. Stage I is applied to the shallow layers of the LVLM decoder. At this stage, CAMA performs intra-ICD grounding. For each ICD, CAMA first locates the key image tokens that are essential to justify the provided answer by computing dynamic attention increments from the anchor tokens to every image token, and then amplifies the attention paid to these tokens so the model captures the critical visual cues. Stage II is applied to the middle layers of the LVLM decoder. In this stage, CAMA operates at the level of attention heads to manage the complex interactions between the query sample and the ICDs. It identifies the heads that exhibit the strongest query-to-ICD attention and rescales their logits based on the cross-modal similarity between the query sample and each ICD.

ICD Contribution Perturbation. To study whether LVLMs can correctly locate the key ICD within the input sequence via self-attention, we sample 10, 000 additional sequences from S. For each sequence, we keep one randomly chosen ICD unchanged, denoted $\mathrm { I C D } ^ { \dag }$ , and replace the other two ICDs with samples from the HatefulMemes dataset. This setup ensures that every sequence $s _ { i }$ contains one ICD that is semantically closest to the query sample, whereas the remaining two ICDs are almost irrelevant. For every sequence, three variants are generated by placing $\mathrm { I C D } ^ { \dag }$ in the first, second, or third position, respectively, yielding 30,000 perturbed sequences. Using the same correct/wrong split procedure described above, we obtain new $\mathcal { G } _ { \mathrm { c o r r e c t } } ^ { \prime }$ and $\mathcal { G ^ { \prime } } _ { \mathrm { { w r o n g } } }$ sets, each containing 5,000 cases.

Saliency-Based Contribution Score $s _ { \mathbf { c o n t r i b } } .$ To quantify the token-level information flow we compute a saliency score matrix $I _ { i } \in \mathbb { R } ^ { S _ { i } ^ { \mathrm { t o t a l } } \times S _ { i } ^ { \mathrm { t o t a l } } }$ at each 𝑙-th decoder layer:

$$
\begin{array} { r } { I _ { i , l } \ = \ \big | \ A _ { i , l } \ \odot \ \frac { \partial \mathcal { L } ( s _ { i } ) } { \partial A _ { i , l } } \big | , } \end{array}\tag{16}
$$

where $A _ { i , l }$ denotes the post-softmax attention matrix, $\mathcal { L } ( s _ { i } )$ is the loss function for input $s _ { i } , ~ \odot$ denotes element-wise (Hadamard) product, and the absolute value is applied element-wise. $I _ { i , l } ( m , n )$ reflects the significance of the information flow from the 𝑛-th token to the 𝑚-th token at the 𝑙-th layer.

Through perturbation, we place the key ICD at position $p \in \{ 1 , 2 , 3 \}$ within a sequence $s _ { i } .$ . Let $\mathbf { V } _ { i , p } ^ { \dagger }$ denote the index set of visual tokens from that position, $\mathbf { V } _ { i }$ denote the union index set of visual tokens from all three ICDs and the query sample, and ${ \bf S } _ { i } ^ { \mathrm { a n s } }$ denote the index set of the generated answer tokens. The layer-wise contribution score for position $p$ is defined as

$$
s _ { \mathrm { c o n t r i b } } ^ { ( i , p ) } ( l ) \ = \ \frac { \displaystyle { \sum _ { \nu \in { \bf V } _ { i , p } ^ { \dag } } \sum _ { t \in { \bf S } _ { i } ^ { \mathrm { a n s } } } I _ { i , l } ( \nu , t ) } } { \displaystyle { \sum _ { \nu ^ { \prime } \in { \bf V } _ { i } } \sum _ { t \in { \bf S } _ { i } ^ { \mathrm { a n s } } } I _ { i , l } ( \nu ^ { \prime } , t ) } } ,\tag{17}
$$

i.e. the fraction of answer-directed saliency that can be traced back to the visual tokens of the key ICD in position 𝑝. A higher $s _ { \mathrm { c o n t r i b } }$ indicates that a larger proportion of the answerrelated signal is attributable to the key ICD.

## 3 Experiments

## 3.1 Setup Details

Benchmarks. In this work, to verify that CAMA can be broadly applied to various multimodal ICL tasks, we follow common evaluation protocols and include several more challenging benchmarks, using a total of eleven benchmarks:

• VQAv2: VQAv2 contains 443,757 samples in the training set and 214,354 in the validation set. It is a classic VQA benchmark that tests a model’s ability to understand both the image and the question across diverse real-world scenarios. The images are sourced from the MSCOCO dataset, and the evaluation metric is Accuracy.

• VizWiz: VizWiz contains 20,523 samples in the training set and 4,319 in the validation set. It presents a more challenging setting with lower-quality images, along with many unanswerable cases, pushing models to handle uncertainty based on the format learned from ICDs. Its evaluation metric is Accuracy.

• OK-VQA: OK-VQA contains 9,055 samples in the training set and 5,000 in the validation set. It requires the model to incorporate external knowledge beyond the image content and the context to generate correct answers. The evaluation metric is Accuracy.

• GQA: GQA contains 943k samples in the training set and 132k in the validation set. This benchmark requires the model to perform multi-step, compositional reasoning when answering VQA questions, rather than relying on answer priors. The evaluation metric is Accuracy.

• TextVQA: TextVQA contains 34,602 samples in the training set and 5,000 in the validation set. Questions deliberately reference scene text (“What does the billboard $\mathrm { s a y 2 ^ { , 9 } } )$ , forcing models to integrate OCR output with visual and linguistic cues. The evaluation metric is Accuracy.

• CLEVR: CLEVR Count Induction (CLEVR), a subset from VL-ICL bench, contains 800 samples in the training set and 200 in the validation set. Each ICD image is paired with an obscure query formatted as an attribute–number pair that identifies specific objects based on four attributes: size, shape, color, or material. We reformat them like “(Q: Red. A: 2.)”. The task requires models to perform challenging reasoning, first recognizing the task pattern, then counting the correct number of objects. The evaluation metric is Accuracy.

• MMStar: MMStar consists of 1,500 hand-picked, visionindispensable samples balanced across 6 core skills and 18 fine-grained axes. Every item was filtered from 22,000 candidates to eliminate data leakage and questions answerable by language alone, so models cannot “cheat” with memorized knowledge. Since it does not provide a predefined training and validation split, we divide the data using a 7:3 ratio. The evaluation metric is Accuracy, and the reported results are weighted averages across its six subtasks.

• Flickr30k (Young et al. 2014): Flickr30k contains 29,783 samples in the training set and 1,000 in the validation set. It consists of images showing everyday activities, each paired with multiple human-written captions that provide concise descriptions of the scenes. The evaluation metric is CIDEr.

• MSCOCO (Lin et al. 2014): MSCOCO contains 82,783 samples in the training set and 40,504 in the validation set. It is a widely used benchmark featuring a diverse range of images with detailed and richly descriptive captions, ideal for evaluating a model’s overall perception and description capabilities. The evaluation metric is CIDEr.

• Hatefulmemes (Kiela et al. 2020): HatefulMemes contains 8,500 samples in the training set and 500 in the validation set. It is designed to reflect real-world challenges found in internet multimodal data. The task requires the model to jointly interpret both the image and the overlaid text to detect instances of hate speech. The evaluation metric is ROC-AUC.

• L-I-VST (Li et al. 2024): L-I-VST refers to the Visual StoryTelling subset of LLaVA-Interleave Bench, containing 400 samples. Each sample is an interleaved image-text sequence, where the model is required to generate a new sentence for a given image based on preceding imagesentence pairs, forming a coherent story.

Models. In this work, we evaluate CAMA on four LVLMs with diverse LLM backbones, training data, and numbers of tokens per image.

• LLaVA-NeXT-7B: LLaVA-NeXT-7B uses CLIP-L/336 as the vision encoder and Mistral-7B as the LLM backbone. It is instruction-tuned on high-quality visualinstruction pairs that emphasize OCR and logical reasoning while reusing the eficient LLaVA-1.5 training recipe. It converts each image into up to 2,880 tokens for highresolution inputs. Considering its context length, we set the number of tokens per image to 576.

• Idefics2-8B: Idefics2-8B uses SigLIP-SO400M as the vision encoder and Mistral-7B as the LLM backbone. Its training happens in two stages: (1) pre-training on OBELICS at 384<sup>2</sup> resolution, and (2) native-resolution fine-tuning (≤ 980 px) that adds OCR-heavy corpora such as PDFA, Rendered-Text and IDL, followed by instruction tuning on the 50-dataset Cauldron mix plus nine text-only sets. It converts each image into 64 tokens.

• InternVL2.5-8B: InternVL2.5-8B uses InternViT-300M as the vision encoder and InternLM 2.5-7B chat as the LLM backbone. It uses a three-stage curriculum (MLP warm-up → optional ViT incremental learning → full instruction tuning) combined with dynamic high-resolution tiling, JPEG-robust augmentation, and a stringent datafiltering pipeline for training. It can adjust the number of tokens per image based on input resolution. We set this number to 900 for consistency.

• Qwen2.5VL-7B: Qwen2.5VL-7B uses a windowattention ViT that supports dynamic spatial/temporal sampling and multi-resolution RoPE as the vision encoder and Qwen 2.5-7B as the LLM backbone. It is pretrained on 4.1 T text tokens plus large-scale image + video data, then instruction-tuned for chat-style vision-language tasks. It can also adjust the number of tokens per image based on input resolution. We set this number to 1156 for consistency.

Baselines. Given that no existing method enhances multimodal ICL by modulating the intermediate attention logits of LVLMs and we are the first to do so, we select the following baselines for comparison:

• Vanilla: Vanilla denotes directly feeding the LVLM with in-context sequences of the form (𝐼<sub>1</sub>, 𝑇<sub>1</sub>, ..., 𝐼 , 𝑇 , 𝑄𝑢𝑒𝑟𝑦𝑆𝑎𝑚𝑝𝑙𝑒) to perform ICL.

• +Inst: Instruction augmented (+Inst) prepends to the vanilla sequence a sentence that explicitly instructs the model to carry out ICL: “First, study the examples we provide. Then utilize what you have learned to answer the new question.” Notably, this sentence achieves the best overall performance among the three styles we tested and is therefore adopted in our main experiments. The other two variants are “Please make full use of the provided examples to solve a new image-related question” and “Here are several example image-text pairs, along with a new image and question. Please perform in-context learning. (Fu et al. 2025)

• CD: Contrastive decoding (CD) constructs a distorted variant targeted to a selected part of the input, separately feeds the original and distorted sequences into the model, and collects their final output logits. By calibrating the vanilla logits with those from the distorted input, we obtain new logits whose distribution implicitly ensures that the model attends to the selected part. In LVLMs, CD is typically employed to encourage the model to rely more on visual evidence and thus mitigate hallucination or language prior (Li et al. 2025b; Ye et al. 2025). A common practice is to either add noise to the input image or directly replace it with a blank image. CD can likewise enhance multimodal ICL. We observe that replacing the images with blank images yields a larger improvement than adding noise. After calibration, the resulting logits accentuate the influence of the ICDs. Formally, CD is presented by:

$$
( 1 + \alpha ) \operatorname { l o g i t s } _ { \theta } ( y _ { t } \mid y _ { < t } , X ) - \alpha \operatorname { l o g i t s } _ { \theta } ( y _ { t } \mid y _ { < t } , { \hat { X } } ) ,\tag{18}
$$

where 𝜃 denotes the $\mathbf { L V L M } , y _ { t }$ denotes the model output at time step 𝑡, and 𝑋 and 𝑋<sup>ˆ</sup> denote the vanilla sequence and the distorted sequence, respectively. 𝛼 is a user-defined value. For all VQA benchmarks, we set $\alpha = 0 . 4$ . For other benchmarks, we set $\alpha = 0 . 6$ (Huang et al. 2025; Zhang et al. 2025).

• VE: Visual enhancement (VE) is an efective strategy for improving LVLM performance that requires only changes in the input images. It works by manually highlighting the visual features that the user considers important, thereby increasing the model’s awareness of them. For each image in the ICDs of a vanilla sequence, we draw red bounding boxes around the regions mentioned by the accompanying text and feed the annotated sequence to the model. An image can contain multiple bounding boxes. Every annotation undergoes two additional human checks to ensure that the highlighted visual cues accurately reflect the textual semantics.

• SoFA: Soft Attention (SoFA) is a training-free and plugand-play module for LVLMs that alleviates position bias by reshaping inter-image attention. Specifically, rather than employing purely causal (unidirectional) attention among visual tokens, SoFA defines a soft attention mask to add its bidirectional counterpart:

$$
\mathbf { M } _ { \mathrm { { s o f t } } } = \left( 1 - \sigma \right) \mathbf { 1 } _ { \mathrm { { c a u s a l } } } + \sigma \mathbf { 1 } _ { \mathrm { { b i d i r e c t i o n a l } } } ,\tag{19}
$$

and computes the resulting attention output as

$$
\mathbf { H } _ { \mathrm { s o f t } } = \mathrm { S o f t m a x } \bigg ( \frac { Q K ^ { \top } } { \sqrt { d } } \bigg ) \odot \mathbf { M } _ { \mathrm { s o f t } } V ,\tag{20}
$$

where $\sigma \in [ 0 , 1 ]$ controls the interpolation degree between causal and bidirectional masks and is selected via a small validation set. The interpolation is applied every two layers to preserve the model’s original training dynamics. By smoothing positional cues and reinforcing early-image interactions while preserving text autoregression, SoFA achieves balanced reasoning over all image positions and significantly reduces prediction inconsistency. It has also been found to improve the performance of multimodal ICL.

## 3.2 Impact of Position Factor under Varying ICD Shot Counts

Figure 7 reports the performance drop that occurs when the position-decay factors are removed from Stage I or Stage II at shot counts of 4, 8, and 16. As the number of shots increases, the benefit contributed by the position factor grows steadily, which corroborates Finding 3. With more shots in a sequence, earlier ICDs sufer greater attention deficits. The position factor compensates for this imbalance and thus becomes crucial when extending CAMA to long-context and many-shot scenarios.

![](images/b9bf2f980018b2cd12a6cab3d852e2b656c0da04db2cb5a71f52e3fb3daf92ec.jpg)  
Figure 7: Average performance comparison of CAMA (Vanilla vs. w/o position-decay factors) under diferent shot counts.

<table><tr><td>Method</td><td colspan="4">VQAv2 VizWiz OK-VQA GQA TextVQA</td></tr><tr><td> ${ \bf S } _ { i } ^ { Q } [ 0 ]$   $\mathbf { S } _ { i } ^ { t } [ - 2 ]$ </td><td>68.12 67.34</td><td>50.69 49.83</td><td>60.56 68.60 60.03 67.84</td><td>77.53 76.91 76.58</td></tr><tr><td> $\mathbf { S } _ { i } ^ { \tilde { I } } [ - 1 ]$   $\mathbf { S } _ { i } ^ { A } [ 0 ]$   ${ \bf S } _ { i } ^ { \dot { Q } } [ - 1 ]$ </td><td>67.15 68.12 67.93</td><td>49.37 50.69 50.92</td><td>59.12 60.56 60.27</td><td>67.75 68.60 77.53 68.35 77.16</td></tr><tr><td> ${ \bf S } _ { i } ^ { Q } [ - 2 ]$  Random(SQ)</td><td>67.87 67.21</td><td>50.42 49.92</td><td>59.84 59.15 60.71</td><td>68.39 76.95 67.78 76.71 68.41 76.82</td></tr><tr><td> $\mathbf { S } _ { i } ^ { A } [ - 1 ]$   ${ \bf S } _ { i } ^ { Q } [ - 2 ]$  Random(SA) 67.32</td><td>68.12 68.04</td><td>50.69 50.48</td><td>60.56</td><td>68.60 77.53</td></tr></table>

Table 4: Average performance of CAMA with diferent threeanchor-token combinations. The first row in each block corresponds to the original anchor-token selection. Random(·) denotes a token randomly chosen from the sequence ·.

## 3.3 Impact of the Selection of Anchor Tokens

In computing the dynamic attention increments, the choice of the three anchor tokens is critical. For eficiency and owing to the semantic accumulation that emerges in the middle layers, we select $\mathbf { S } _ { i } ^ { Q } [ 0 ] , \mathbf { S } _ { i } ^ { A } [ 0 ]$ , and $\mathbf { S } _ { i } ^ { A } [ - 1 ]$ as the anchor tokens. We then vary each of these anchor tokens to investigate their influence on CAMA performance, and the results are presented in Table 4. The findings show that semantic accumulation indeed facilitates the calculation of dynamic attention increments, allowing the last tokens to summarize the semantics of the preceding tokens. In contrast, the final tokens of an image are less representative and cannot serve as suitable anchor tokens, which further indicates that attention deficits also exist within image tokens and that their semantics often drift toward the subsequent text.

![](images/a53980c769f68829e2690f6f68e39d399163a795479e8cbd47cacf42811403f2.jpg)  
Figure 8: Qualitative visualizations of CAMA on four cases.

## 3.4 Additional Qualitative Visualizations

In Figure 8, we present the ICL enhancement results of CAMA for four input sequences by visualizing the image attention in the 19th decoder layer of LLaVA-NeXT-7B. In (a), the sequence comes from CLEVR. This benchmark poses a challenge for the model to identify the task mapping in ICL because of its subtle textual descriptions. Through dynamic attention increments, CAMA highlights the key visual features that align with the text semantics, helping the model infer the correct task mapping. As shown in the figure, the model accurately locates the objects whose attributes match those in the question and successfully performs the counting task. In (b), the example illustrates a typical VQA scenario. In this sequence, although the third ICD and the query sample both depict cakes as the main subject, the first ICD is actually more crucial for solving the query sample, as both focus on identifying food ingredients. CAMA efectively prevents the first ICD from being overlooked due to position bias, guiding the model’s attention toward the connection between “drink” and “strawberry” in the first ICD. This association helps the model identify the relationship between “cake” and “banana” in the query sample, enabling it to provide the correct answer. In (c), the example is from L-I-VST, which requires the model to complete an interleaved story. While reinforcing the alignment between each image–text pair, CAMA also guides the model to focus on consistent visual cues between earlier images and the query sample image, such as “a girl wearing pink clothes,” thereby recognizing the narrative as a coherent story. This enables the model to generate text that follows the format established in the preceding context. In (d), the sequence comes from MMStar, which presents tasks in a multiple-choice format and requires the LVLM to recognize the emotion in an image. CAMA identifies the second ICD as the most helpful for answering the query sample, since both images are cat memes. The perception of the second image is thus enhanced, allowing it to fully capture the connection between the cat’s expression and its ground-truth option “sadness.” When interpreting the query sample image, the model focuses more on the cat’s expression rather than the text in the image, demonstrating CAMA’s ability to deeply promote efective multimodal ICL. However, in our experiments we also find that CAMA struggles when the incontext sequence contains too much irrelevant information, such as cases where seven out of eight or all ICDs are unrelated to the query sample or provide misleading content. In these situations, the dificulty of appropriately allocating attention in Stage II prevents the model’s behavior from being steered in the desired direction. These failure cases highlight that improving the quality of sequence configuration remains important.

<table><tr><td>Method</td><td>Inference Latency</td><td>Accuracy (%)</td></tr><tr><td>Vanilla</td><td>4.70s</td><td>58.07</td></tr><tr><td>CD</td><td>9.42s</td><td>57.95</td></tr><tr><td>SoFA</td><td>4.72s</td><td>59.15</td></tr><tr><td>CAMA</td><td>4.94s</td><td>61.03</td></tr></table>

Table 5: Comparison of average inference latency and Accuracy of four methods in the 8-shot setting.

## 3.5 Eficiency Analysis

As shown in Table 5, CAMA introduces only a small increase in inference latency compared with the vanilla model and SoFA, while delivering substantial performance gains. Compared with CD, which requires two forward passes, CAMA also achieves a clear eficiency advantage. When the number of ICDs is smaller, the added inference latency of CAMA further reduces. Therefore, although CAMA incurs some additional cost, its cost-efectiveness in practical applications remains superior.