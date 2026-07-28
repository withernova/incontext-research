# Your Large Vision-Language Model Only Needs A Few Attention Heads For Visual Grounding

Seil Kang Jinyeong Kim Junhyeok Kim Seong Jae Hwang Yonsei University

{seil, jinyeong1324, timespt, seongjae}@yonsei.ac.kr

## Abstract

Visual grounding seeks to localize the image region corresponding to a free-form text description. Recently, the strong multimodal capabilities of Large Vision-Language Models (LVLMs) have driven substantial improvements in visual grounding, though they inevitably requirefine-tuning and additional model components to explicitly generate bounding boxes or segmentation masks. However, we discover that a few attention heads in frozen LVLMs demonstrate strong visual grounding capabilities. We refer to these heads, which consistently capture object locations related to text semantics, as localization heads. Using localization heads, we introduce a straightforward and effective training-free visual grounding framework that utilizes textto-image attention mapsfrom localization heads to identify the target objects. Surprisingly, only three out of thousands of attention heads are sufficient to achieve competitive localization performance compared to existing LVLM-based visual grounding methods that require fine-tuning. Our findings suggest that LVLMs can innately ground objects based on a deep comprehension of the text-image relationship, as they implicitly focus on relevant image regions to generate informative text outputs. All the source codes will be made available to the public.

## 1. Introduction

Visual grounding is a task that, given textual descriptions, identifies and localizes relevant objects within an image, producing outputs such as bounding boxes [39, 70] or segmentation masks [18]. Recently, this vision-language task, which inherently requires a deep understanding of the relationship between images and text, has seen significant advancements with the emergence of powerful Large Vision-Language Models (LVLMs) [28, 35, 36, 56]. However, since LVLMs are primarily designed to generate text outputs, directly leveraging them as a vision-language tool to identify and localize objects within an image (i.e., visual grounding) presents technical challenges. Inevitably, current LVLM-based visual grounding methods require explicit fine-tuning of LVLMs with additional visual grounding datasets and modifications to model components to enable the generation of bounding boxes [6, 61, 68] or segmentation masks [26, 45, 65, 74].

![](images/b007b1a686fdcef9baad5870daeeb9a61e725e25e38aef2487fe0252f77b0a38.jpg)

<details>
<summary>text_image</summary>

GT
Average
L14 H24
L14 H13
Expression: the pizza mouth.
Mask:
Expression: guy in the right.
Mask:
Expression: girl on outer seat long hair no sleeves on.
Mask:
</details>

Figure 1. Visualization of the text-to-image attention maps from LLaVA-1.5-7B [35]. While the average attention map initially seems uninformative for localization, a closer examination reveals that LVLM possesses built-in localization heads that consistently capture key areas of an image corresponding to the referring text, regardless of sample variations. L14 H24 refers to the 24th attention head in the 14th layer of the LVLM.

Despite the interesting integration of LVLMs in previous visual grounding works, a fundamental question remains: since LVLMs generate text outputs that imply an understanding of specific image regions, is it possible to explicitly observe this mechanism in action? In other words, we ask whether we can extract how the LVLMs “focus” on specific image regions corresponding to given text descriptions for visual grounding. A natural first approach to addressing this question might be to examine the text-to-image attention maps, which reveal how a text description attends to different image patches. To explore this, we visualize the average attention maps of LVLMs across various layers and heads—a common method in ViTs [11, 73] and diffusion models (DMs) [4, 17, 54]—anticipating that they would capture the regions associated with the referring text. However, unlike the interpretable attention patterns observed in ViTs and DMs, the text-to-image attention maps in LVLMs appear sparse and contain significant noise, as illustrated in the second column of Fig. 1. This suggests that the current use of LVLM attention maps may struggle to accurately pinpoint relevant objects for visual grounding.

However, interestingly, our work reveals that not the average of the attention maps, but some small subset of attention heads are capable of providing tangible and precise text-image attention maps. In particular, we find that a few attention heads in LVLMs consistently capture regions in images corresponding to the referred text, regardless of the samples. We refer to these heads as localization heads. For example, as presented in the third and fourth columns of Fig. 1, the attention maps of the 24th head of the 14th layer (L14 H24) and the 13th head of the 14th layer (L14 H13) in LLaVA-1.5-7B [35] consistently highlight the regions of interest based on the referred text.

In this work, we introduce how we systematically identify such localization heads based on two explicit criteria. (1) We measure how much each attention head focuses on the image by calculating the attention sum and only select the heads that dominantly attend to the image. (2) Among these heads, the ones that specifically pay attention to a certain region of the image, which is measured by spatial entropy [2], are considered to effectively localize the referred object. We validate that the selected localization heads consistently capture objects closely associated with the text.

With our localization heads, we introduce a simple yet effective training-free visual grounding framework. The attention maps from the localization heads are assembled to predict the bounding box or mask of the referred object. Notably, only three localization heads are enough to localize the referred object within the image, suggesting that they are highly specialized to attend to relevant image regions. As shown in Fig. 2, in contrast to existing fine-tuning based methods, our framework is training-free, eliminating the need for additional fine-tuning LVLMs for visual grounding tasks.

We validate our approach across ten different LVLMs with varying parameter counts, architectures, and training datasets, demonstrating its broad applicability. Our framework outperforms the existing training-free methods by significant margins. Furthermore, our method performs comparably to specially fine-tuned LVLMs for visual grounding tasks (e.g., LISA [26]). The results indicate that LVLMs can serve as effective text-referring localizers, intrinsically identifying regions that are relevant and coherent with the text expression. To the best of our knowledge, we are the first to identify the localization properties of specific attention heads in LVLMs.

![](images/d7a7cb1c6d4ec76302949c665b2c3f11f40101c91d8761eec7d4e46c2ba6f7a0.jpg)  
Figure 2. Comparison of LVLM frameworks for visual grounding. (a) Existing methods generally fine-tune a LVLM to leverage specialized tokens (e.g., [SEG]) or language descriptions for visual grounding. (b) Our framework utilizes the attention maps of only a few localization heads from frozen LVLMs.

In summary, our contributions are as follows:

• We discover that the specific attention heads in LVLMs have the capability for visual grounding, which we refer to as localization heads.  
• We propose a simple yet effective framework for LVLMbased training-free visual grounding with localization heads. The attention maps from a few localization heads are utilized to predict the bounding box or mask of the referred object.  
• We evaluate our approach across various LVLMs. Our framework demonstrates superior performance by a large margin compared to other training-free methods and even performs comparably to fine-tuned methods.

## 2. Related Works

Visual Grounding. Visual grounding aims to identify the region in the image based on a free-form natural language expression [5], which has expanded the scope of detection and segmentation tasks to a more realistic scenario [50, 66]. Two prominent tasks within visual grounding are Referring Expression Comprehension (REC) [39, 70] and Referring Expression Segmentation (RES) [18, 34]. REC focuses on localizing a referred object in an image and generating a bounding box, while RES further requires a pixel-level segmentation mask. In order to address these tasks, numerous studies have been conducted to explore effective methods that consider both text and visual information simultaneously [23, 29, 33, 42, 49, 62, 67, 75].

Application of LVLMs in Grounding Tasks. Recently, visual grounding has been significantly advanced by leveraging the outstanding vision-language processing capabilities of LVLMs. To incorporate LVLMs into visual grounding tasks, existing methods include visual grounding datasets in the training process and implement additional components to extract localization information. For example, LISA [26] introduces [SEG] token as a mask embedding and generates a segmentation mask using additional mask decoder [24]. F-LMM [64] leverages the attention weights of frozen LVLMs, but still requires training its mask refinement modules on visual grounding datasets. In contrast, we propose a training-free visual grounding method that directly utilizes LVLMs.

Training-Free Visual Grounding. Given the high performance of multimodal foundation models across diverse vision-language tasks, training-free visual grounding emerges as a new research direction. Existing trainingfree methods typically apply internal features or attention maps from CLIP [44] or Text-to-Image Diffusion Models (DMs) [47]. CLIP-based methods typically employ off-theshelf models [24, 46] to generate region proposals and select the most relevant bounding box [52] or mask [53, 71] based on the CLIP similarity score with the text query. On the other hand, DM-based methods utilize the residue of the text-to-image diffusion process (e.g., the attention map) to predict the segmentation mask [3, 40]. Our work advances this line of research by introducing the first LVLM-based training-free visual grounding framework.

## 3. Background

Notation. Large Vision-Language Models (LVLMs) typically consist of three main components: a vision encoder, a projector, and a large language model. For an input image $X _ { \mathrm { v } }$ , the vision encoder and the projector transform the image into a sequence of visual embedding $Z _ { \mathrm { v } } \in \mathbb { R } ^ { P ^ { 2 } \times d }$ where $P ^ { 2 }$ is the number of flattened image tokens and d is the hidden dimension. Similarly, an input text $X _ { \mathrm { t } }$ is converted into a sequence of token embeddings $Z _ { \mathrm { t } } ~ \in ~ \mathbb { R } ^ { L \times d }$ where L is the number of tokens in the text. The visual and textual embeddings are concatenated as $Z ^ { 0 } = [ Z _ { \mathrm { v } } ; Z _ { \mathrm { t } } ] \ \in$ $\mathbb { R } ^ { ( P ^ { 2 } + L ) \times d }$ and fed into the large language model (LLM) as the input embeddings.

Multi-Head Self-Attention. The input embeddings $Z ^ { 0 }$ pass through a series of decoder blocks, which consists of multi-head self-attention and feed-forward neural network module. Specifically, we focus on the attention heads, as these are the only components where tokens interact. In layer ℓ and head $h ,$ the hidden state from the previous layer $Z ^ { \ell - 1 }$ is projected into query $Q ,$ key $\kappa ,$ , and value $V \in \mathbb { R } ^ { ( P ^ { 2 } + L ) \times d _ { h } }$ matrices, where $d _ { h }$ is the hidden dimension of the attention head. Then, the attention head com-

putes the attention weights as:

$$
\mathrm{Attn} ^ {\ell , h} (\boldsymbol {Z} ^ {\ell - 1}) = \operatorname{softmax} \left(\frac {\boldsymbol {Q} \boldsymbol {K} ^ {\top}}{\sqrt {d _ {h}}}\right). \tag {1}
$$

Note that the attention weights reflect the similarity between the query Q and key K matrices.

Investigation of Image-Text Interaction. Considering that LLM decoding operates in an auto-regressive manner, information flows from preceding tokens to subsequent ones, resulting in the final token to encapsulate the context of the entire sentence [20, 59]. Thus, we posit that the query vector of the last input text token $\mathbf { \widetilde { q } _ { \mathrm { t x t } } }$ serves as a representative query for the whole sentence. For example, in the sentence “the pizza mouth.” in Fig. 1, the query vector of the last token [.] is utilized in our experiments. To investigate image-text interactions, we examine the attention weights of where the query is $\mathbf { \widetilde { q } _ { \mathrm { t x t } } }$ and keys are image tokens. Specifically, considering a slight modification of Eq. (1), for the attention weights $\mathbf { \Omega } _ { \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { a } ^ { \ell , h } }$ at layer ℓ and head h with $\mathbf { \widetilde { q } _ { \mathrm { t x t } } }$ as a query token:

$$
\boldsymbol {a} ^ {\ell , h} = \operatorname{softmax} \left(\frac {\boldsymbol {q} _ {\mathrm{txt}} \boldsymbol {K} ^ {\top}}{\sqrt {d _ {h}}}\right) \in \mathbb {R} ^ {P ^ {2} + L}, \tag {2}
$$

we focus on the first $P ^ { 2 }$ components, $a ^ { \ell , h } [ 1 : { \cal P } ^ { 2 } ]$ , for our analysis. In the following sections of this paper, this will also be denoted as Lℓ Hh for simplicity. For example, L5 H3 refers to the third attention head in the fifth layer of the LVLM.

## 4. Towards Discovering Localization Heads

Recent studies [9, 57, 76] have shown that the attention heads exhibit distinct characteristics, motivating us to find specific heads possessing the potential to serve as effective text referring localizers. In this section, we propose attention sum and spatial entropy in Sec. 4.1 as two criteria for selecting such heads. Through experiments in Sec. 4.2, we validate that the heads capturing objects corresponding to the text description can be successfully identified based on the proposed criteria. Note that the first two layers of the LLM are consistently excluded in our analyses, as the early layers are known to operate differently from the other layers [25]. To demonstrate the generalizability of our findings, we conduct experiments across various LVLMs [7, 8, 30, 35, 36, 38, 69] and datasets [18, 22]. Details of the experimental setup and more results are provided in the Appendix Sec. A. and C., respectively.

## 4.1. Criteria to Find Localization Heads

Our final goal is to identify heads that excel in text referring. To achieve this, we propose two criteria in this section.

Criterion 1: Attention Sum. To identify heads that predominantly focus on the overall image, we first consider attention sum $\begin{array} { r } { S _ { \mathrm { i m g } } ^ { \ell , h } = \sum _ { i = 1 } ^ { P ^ { 2 } } { \pmb a } ^ { \ell , h } [ i ] } \end{array}$ , which quantifies the relevance of image information to $\mathbf { \phi } _ { q _ { \mathrm { t x t } } }$ within individual attention heads. Then, the average $S _ { \mathrm { i m g } } ^ { \ell , h }$ for each head is computed across 1,000 random samples from RefCOCO [22] training set.

![](images/dec2e2b1ca08b436a4349fbb3b15dc263b0585657a35718cfb65e4d7cec450f3.jpg)  
Figure 3. Average $S _ { \mathrm { i m g } } ^ { \ell , h }$ values for each attention head. We sort the heads in ascending order of $S _ { \mathrm { i m g } } ^ { \ell , h }$ . Attention heads with $S _ { \mathrm { i m g } } ^ { \ell , h } \ge \tau$ are considered to effectively attend to the image, where τ is the threshold determined by the maximum curvature in the graph.

As shown in Fig. 3, most attention heads exhibit low $S _ { \mathrm { i m g } } ^ { \ell , h }$ values, indicating that relatively few heads contribute significantly to the model’s text-image interaction. To distinguish heads with high $S _ { \mathrm { i m g } } ^ { \ell , h }$ from those with low values, we set the threshold $\tau$ at the point of the maximum curvature in the graph $( e . g . , \tau = 0 . 2 4$ in LLaVA-1.5-7B [35]). We deem the heads with $S _ { \mathrm { i m g } } ^ { \ell , h } \geq \tau$ to effectively attend to image. While we adopt the maximum curvature as a practical choice, we note that our analysis remains robust across a range of reasonable τ values. For analyses using alternative τ values, please refer to Appendix Sec. C.

Criterion 2: Spatial Entropy. For an attention head to be considered effective at focusing on objects, it must not only have a high attention sum value for the image but also concentrate its attention specifically around the objects. Since it is reasonable to assume that the object patches tend to stay near each other [51, 58, 72], we evaluate how locally a cluster is formed in each attention map through spatial entropy [2, 41] to identify localization heads.

Fig. 4 presents an example of how spatial entropy is calculated. First, we reshape the attention weights $\pmb { a } ^ { \ell , \hat { h } } [ 1 : P ^ { 2 } ]$ into a $P \times P$ attention map $A ^ { \ell , h }$ . The attention map is binarized by assigning a value of 1 to elements above the mean and 0 to those below it [41]. Next, we identify connected components $C _ { i } \ [ 1 4 ]$ , defined as a set of coordinates connected via 8-neighbors. Then, for the set of N connected components $\{ C _ { i } \} _ { i = 1 } ^ { N }$ , the spatial entropy H is calculated

![](images/183dd71cbf4b540416e76ae3227fa67319f627bac5fe7e5c85543aba4bcf5d31.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
  subgraph L18_H10
  A["Image Data"] -->|Binarize| B1["C1 C2"]
  B1 --> C1["C1"]
  B1 --> C2["C2"]
  end
  subgraph L32_H10
  A -->|Binarize| A1["C1 C3 C2"]
  A -->|Binarize| A2["C1 C3 C2"]
  A2 --> C2["C2"]
  A2 --> C3["C3"]
  A2 --> C4["C4"]
  A2 --> C5["C5"]
  end
  subgraph L18_H10
  C1 -->|Low HA^l,h| C1
  end
  subgraph L32_H10
  C1 -->|High HA^l,h| C1
  C2 -->|Low HA^l,h| C2
  C2 -->|High HA^l,h| C2
  end
```
</details>

Figure 4. Illustration of the process for calculating spatial entropy. The attention map is binarized, and the spatial entropy is computed based on the sizes of its connected components $\{ C _ { i } \} _ { i = 1 } ^ { N }$

![](images/254e6dc05892a4fe17a955651a0969b12511dd92d05b7217a1cf6a4ed09c9ea1.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
  A["LVLM"] --> B["Collect all attention maps"]
  B --> C["Select 10 heads with the lowest H(A^ℓ,h)"]
  C --> D["Calculate selection frequency across samples"]
  D --> E["Selection frequency (L14-H24) to L17-H11"]
```
</details>

Figure 5. Overview of finding localization heads. We first identify heads with high attention sum. Then, we evaluate spatial entropy for each head and select 10 heads with the lowest spatial entropy. We repeat this process for 1,000 image-text pairs and calculate the selection frequency of each head.

as:

$$
H (\boldsymbol {A} ^ {\ell , h}) = - \sum_ {i = 1} ^ {N} P (C _ {i}) \log P (C _ {i}), \tag {3}
$$

where $\begin{array} { r } { P ( C _ { i } ) = | C _ { i } | / \sum _ { i = 1 } ^ { N } | C _ { i } | } \end{array}$ . As a result, an attention map $A ^ { \ell , \dot { h } }$ is considered effectively localized if it exhibits low spatial entropy. For more mathematical details on spatial entropy, please refer to the Appendix Sec. B.

## 4.2. Finding Localization Heads via Criteria

In this section, we utilize the two criteria described earlier to select a small subset of attention heads. Then, we demonstrate that the selected heads effectively capture objects relevant to the text.

![](images/ebf886447d4a391dc209d5277cd3a4dd5b4870c994fac7eb698b7c9361acaa25.jpg)  
Figure 6. (a) Selection frequency of individual heads. Only a few heads exhibit high selection frequency, suggesting that their attention maps are consistently well-localized. We calculate the selection frequency five times and report the average and standard deviation. (b) Scatte plot illustrating the relationship between selection frequency rank and each head’s average IoU. Heads with higher selection frequency tend to show higher IoU values, indicating that they capture text semantics more effectively. The Spearman correlation coefficient (ρ) between rank and IoU is displayed in the top-right corner. The results of the Spearman correlation are statistically significant (p < 0.001).

To begin with, we rank all attention heads in order of how well they meet our criteria. Specifically, for 1,000 random image-text samples from the RefCOCO [22] training set, we retain all the heads that satisfy $S _ { \mathrm { i m g } } ^ { \ell , h } \geq \tau$ . Among these heads, we calculate the frequency with which each head exhibits the 10-lowest spatial entropy across the samples to identify heads consistently exhibiting low spatial entropy. We refer to this metric as the selection frequency. The overall process is illustrated in Fig. 5, and the results are reported in Fig. 6(a). Now, we assign ranks to each head based on their selection frequency, with higher-ranked heads being those with high selection frequency. For example, in Fig. 6(a), with LLaVA-1.5-7B [35], head L14 H24 ranks first, followed by head L14 H13 in second place.

Finally, we aim to demonstrate that higher-ranked heads are more effective at capturing objects relevant to the text. To this end, we binarize the attention maps of each head to obtain pseudo-masks and measure the IoU between these pseudo-masks and the ground truth (GT) masks. Then, we visualize the relationship between head ranks, derived from Fig. 6(a), and their IoU values as a scatter plot, shown in Fig. 6(b). Note that only the heads with a selection frequency of at least 1% are considered in this analysis.

As visualized in Fig. 6(b), attention heads with higher selection frequency tend to exhibit higher average IoU. We also calculate the Spearman correlation coefficient to quantitatively evaluate the relationship between the selection frequency and IoU. The correlation coefficients are above 0.7 for all LVLMs, indicating strong positive correlations. This trend becomes increasingly evident for heads with higher ranks, leading us to conclude that a small number of top-ranked heads strongly capture semantic information. We refer to these heads as localization heads. Since the trend consistently appears across various LVLMs (see Appendix Sec. C. for trends across more LVLMs), we claim that localization heads are an innate property of LVLMs.

![](images/fc5b16537d22f793849495ea1f3db656f34604ee2957a9bf0b7a16c5659c57c2.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
  subgraph Layer1
    L14_H1["L14 H1"]
    L14_H32["L14 H32"]
  end

  subgraph Layer2
    L14_H24["L14 H24"]
    L14_H13["L14 H13"]
    L14_H26["L14 H26"]
  end

  subgraph Processing
    SAM["SAM"]
    GPass["Gaussian Smoothing"]
  end

  L14_H1 --> L14_H32
  L14_H32 --> L14_H24
  L14_H24 --> GPass
  L14_H13 --> GPass
  L14_H26 --> GPass
  GPass --> SAM
  SAM --> GPass
  SAM --> SAM
```
</details>

Figure 7. Our training-free visual grounding framework. Attention maps of localization heads are assembled into a combined map, which is then used to define the bounding box or segmentation mask.

## 5. Visual Grounding with Localization Heads

In the previous section, we demonstrated that our criteria effectively identifies text-referring localization heads. Building on this, we propose a simple yet effective method to solve visual grounding tasks using these localization heads.

Specifically, our objective is to perform visual grounding tasks, given an LVLM. To achieve this, the localization heads of the LVLM must first be identified. Following the process we described in Sec. 4.2 and Fig. 5, we rank the heads based on the selection frequency and select the heads with the k-highest rank. Subsequently, an imagetext pair for which a mask is to be generated is fed into the LVLM, and attention maps are extracted from the localization heads.

As illustrated in Fig. 7, Gaussian smoothing is applied to each attention map of the localization head to preserve detailed localization information while minimizing potential random noise. The resulting maps are assembled through element-wise summation to produce the combined map. This combined map is then binarized to produce the pseudo-mask. Finally, the largest rectangle encompassing the pseudo-mask is identified and can be used as a bounding box. Additionally, this bounding box can serve as a prompt for SAM [24] to address the segmentation task. Additional details on the algorithm used to find the bounding box are provided in Appendix. Sec. B, and the ablation study on Gaussian smoothing is presented in Appendix. Sec. D.

Table 1. Comparison of our method with existing fine-tuning based and training-free methods on the REC (Referring Expression Comprehension) task. All fine-tuning based methods are trained on the training set of the corresponding datasets. Best performance is col ored in red for fine-tuning and in blue for training-free methods.

<table><tr><td rowspan="2">Method</td><td colspan="3">RefCOCO</td><td colspan="3">RefCOCO+</td><td colspan="2">RefCOCOg</td></tr><tr><td>val</td><td>testA</td><td>testB</td><td>val</td><td>testA</td><td>testB</td><td>val</td><td>test</td></tr><tr><td colspan="9">Fine-tuning based methods</td></tr><tr><td>MDETR [21]</td><td>86.8</td><td>89.6</td><td>81.4</td><td>79.5</td><td>84.1</td><td>70.6</td><td>81.6</td><td>80.9</td></tr><tr><td>SeqTR [77]</td><td>87.0</td><td>90.2</td><td>83.6</td><td>78.7</td><td>84.5</td><td>71.9</td><td>82.7</td><td>83.4</td></tr><tr><td>G-DINO [37]</td><td>89.2</td><td>91.9</td><td>86.0</td><td>81.1</td><td>87.4</td><td>74.7</td><td>84.2</td><td>84.9</td></tr><tr><td>ONE-PEACE [60]</td><td>92.6</td><td>94.2</td><td>89.3</td><td>88.8</td><td>92.2</td><td>83.2</td><td>89.2</td><td>89.3</td></tr><tr><td>UNINEXT [31]</td><td>92.6</td><td>94.3</td><td>91.5</td><td>85.2</td><td>89.6</td><td>79.8</td><td>88.7</td><td>89.4</td></tr><tr><td colspan="9">Fine-tuning based methods w/ LVLMs</td></tr><tr><td>Shikra-7B [6]</td><td>87.0</td><td>90.6</td><td>80.2</td><td>81.6</td><td>87.4</td><td>72.1</td><td>82.3</td><td>82.2</td></tr><tr><td>Ferret-7B [68]</td><td>87.5</td><td>91.4</td><td>82.5</td><td>80.8</td><td>87.4</td><td>73.1</td><td>83.9</td><td>84.8</td></tr><tr><td>Shikra-13B [6]</td><td>87.8</td><td>91.1</td><td>81.8</td><td>82.9</td><td>87.8</td><td>74.4</td><td>82.6</td><td>83.2</td></tr><tr><td>Ferret-13B [68]</td><td>89.5</td><td>92.4</td><td>84.4</td><td>82.8</td><td>88.1</td><td>75.2</td><td>85.8</td><td>86.3</td></tr><tr><td>CogVLM-17B [61]</td><td>92.8</td><td>94.8</td><td>89.0</td><td>88.7</td><td>92.9</td><td>83.4</td><td>89.8</td><td>90.8</td></tr><tr><td colspan="9">Training-free methods</td></tr><tr><td>ReCLIP [52]</td><td>45.8</td><td>46.1</td><td>47.1</td><td>47.9</td><td>50.1</td><td>45.1</td><td>59.3</td><td>59.0</td></tr><tr><td>Han et al. [15]</td><td>49.4</td><td>47.8</td><td>51.7</td><td>48.9</td><td>50.0</td><td>46.9</td><td>61.0</td><td>60.0</td></tr><tr><td>GroundVLP [48]</td><td>65.0</td><td>73.5</td><td>55.0</td><td>68.8</td><td>78.1</td><td>57.3</td><td>74.7</td><td>75.0</td></tr><tr><td colspan="9">Training-free methods w/ LVLMs (Ours)</td></tr><tr><td>DeepSeek-VL-1.3B</td><td>73.2</td><td>77.7</td><td>70.7</td><td>62.0</td><td>66.7</td><td>57.1</td><td>65.2</td><td>69.3</td></tr><tr><td>Mini-Gemini-2B</td><td>74.0</td><td>77.5</td><td>71.1</td><td>62.5</td><td>67.8</td><td>59.3</td><td>65.1</td><td>69.3</td></tr><tr><td>InternVL-6B</td><td>85.2</td><td>86.4</td><td>78.5</td><td>78.0</td><td>83.3</td><td>71.9</td><td>81.1</td><td>80.5</td></tr><tr><td>Yi-VL-6B</td><td>85.1</td><td>86.8</td><td>78.4</td><td>78.9</td><td>84.2</td><td>72.2</td><td>80.5</td><td>80.9</td></tr><tr><td>DeepSeek-VL-7B</td><td>85.3</td><td>87.2</td><td>81.0</td><td>77.8</td><td>83.9</td><td>73.5</td><td>81.1</td><td>82.8</td></tr><tr><td>ShareGPT4V-7B</td><td>86.1</td><td>87.1</td><td>80.5</td><td>79.7</td><td>86.2</td><td>71.3</td><td>82.4</td><td>82.9</td></tr><tr><td>LLaVA-7B</td><td>80.3</td><td>83.5</td><td>77.4</td><td>74.5</td><td>80.2</td><td>69.3</td><td>77.5</td><td>77.1</td></tr><tr><td>LLaVA-1.5-7B</td><td>86.5</td><td>89.8</td><td>80.2</td><td>80.1</td><td>86.3</td><td>71.9</td><td>82.3</td><td>83.0</td></tr><tr><td>LLaVA-13B</td><td>82.8</td><td>85.3</td><td>79.8</td><td>79.3</td><td>82.4</td><td>73.0</td><td>79.8</td><td>79.5</td></tr><tr><td>LLaVA-1.5-13B</td><td>87.2</td><td>90.0</td><td>83.3</td><td>82.7</td><td>88.5</td><td>74.0</td><td>84.3</td><td>85.5</td></tr></table>

## 6. Experiments

In this section, we verify whether the localization head discovered through our selection process ensures robust performance on well-known visual grounding benchmarks. Additionally, we conduct ablation studies to validate the settings of our method.

## 6.1. Experimental Setup

Models. We apply our approach across ten LVLMs to validate its broad applicability. The main experiments include DeepSeek-VL [38], Mini-Gemini [30], InternVL [8],

Table 2. Comparison of our method with existing fine-tuning based and training-free methods on the RES (Referring Expression Segmentation) task. All fine-tuning based methods, except for LISA [26] and GSVA [65], are trained on the training set of the corresponding datasets. Red and blue colors are used as in Tab. 1.

<table><tr><td rowspan="2">Method</td><td colspan="3">RefCOCO</td><td colspan="3">RefCOCO+</td><td colspan="2">RefCOCOg</td></tr><tr><td>val</td><td>testA</td><td>testB</td><td>val</td><td>testA</td><td>testB</td><td>val</td><td>test</td></tr><tr><td colspan="9">Fine-tuning based methods</td></tr><tr><td>LAVT [67]</td><td>72.7</td><td>75.8</td><td>68.8</td><td>62.1</td><td>68.4</td><td>55.1</td><td>61.2</td><td>62.1</td></tr><tr><td>ReLA [34]</td><td>73.8</td><td>76.5</td><td>70.2</td><td>66.0</td><td>71.0</td><td>57.7</td><td>65.0</td><td>66.0</td></tr><tr><td>UniRef++ [63]</td><td>79.1</td><td>82.1</td><td>77.5</td><td>68.4</td><td>74.0</td><td>61.5</td><td>71.4</td><td>72.8</td></tr><tr><td>UNINEXT [31]</td><td>82.2</td><td>83.4</td><td>81.3</td><td>72.5</td><td>76.4</td><td>66.2</td><td>74.4</td><td>76.4</td></tr><tr><td colspan="9">Fine-tuning based methods w/ LVLMs</td></tr><tr><td>LISA-7B [26]</td><td>74.1</td><td>76.5</td><td>71.1</td><td>62.4</td><td>67.4</td><td>56.5</td><td>66.4</td><td>68.5</td></tr><tr><td>GSVA-7B [65]</td><td>76.4</td><td>77.4</td><td>72.8</td><td>64.5</td><td>67.7</td><td>58.6</td><td>71.1</td><td>72.0</td></tr><tr><td>LISA-13B [65]</td><td>73.4</td><td>76.2</td><td>69.5</td><td>62.3</td><td>66.6</td><td>56.3</td><td>68.2</td><td>68.5</td></tr><tr><td>GSVA-13B [65]</td><td>77.7</td><td>79.9</td><td>74.2</td><td>68.0</td><td>71.5</td><td>61.5</td><td>73.2</td><td>73.9</td></tr><tr><td>GLaMM [45]</td><td>79.5</td><td>83.2</td><td>76.9</td><td>75.9</td><td>78.7</td><td>68.8</td><td>76.8</td><td>78.4</td></tr><tr><td>PSALM [74]</td><td>83.6</td><td>84.7</td><td>81.6</td><td>72.9</td><td>75.5</td><td>70.1</td><td>73.8</td><td>74.4</td></tr><tr><td colspan="9">Training-free methods</td></tr><tr><td>Yu et al. [71]</td><td>24.9</td><td>23.6</td><td>24.7</td><td>26.2</td><td>24.9</td><td>25.8</td><td>31.1</td><td>31.0</td></tr><tr><td>TAS [53]</td><td>29.5</td><td>30.3</td><td>28.2</td><td>33.2</td><td>38.8</td><td>28.0</td><td>35.8</td><td>36.2</td></tr><tr><td>Ref-Diff [40]</td><td>35.2</td><td>37.4</td><td>34.5</td><td>35.6</td><td>38.7</td><td>31.4</td><td>38.6</td><td>37.5</td></tr><tr><td colspan="9">Training-free methods w/ LVLMs (Ours)</td></tr><tr><td>DeepSeek-VL-1.3B</td><td>56.3</td><td>57.0</td><td>52.7</td><td>51.2</td><td>55.5</td><td>49.2</td><td>52.3</td><td>55.8</td></tr><tr><td>Mini-Gemini-2B</td><td>59.8</td><td>60.3</td><td>55.5</td><td>56.3</td><td>59.9</td><td>51.8</td><td>55.1</td><td>60.3</td></tr><tr><td>InternVL-6B</td><td>62.1</td><td>65.8</td><td>60.9</td><td>62.2</td><td>65.5</td><td>55.5</td><td>63.5</td><td>65.4</td></tr><tr><td>Yi-VL-6B</td><td>62.5</td><td>65.8</td><td>60.7</td><td>61.0</td><td>65.3</td><td>56.0</td><td>64.0</td><td>67.0</td></tr><tr><td>DeepSeek-VL-7B</td><td>73.9</td><td>76.6</td><td>70.7</td><td>63.1</td><td>66.1</td><td>56.5</td><td>64.0</td><td>68.9</td></tr><tr><td>ShareGPT4V-7B</td><td>73.5</td><td>76.7</td><td>70.1</td><td>59.4</td><td>63.8</td><td>55.9</td><td>60.7</td><td>65.1</td></tr><tr><td>LLaVA-7B</td><td>65.4</td><td>66.2</td><td>61.1</td><td>59.9</td><td>63.2</td><td>52.7</td><td>59.7</td><td>63.3</td></tr><tr><td>LLaVA-1.5-7B</td><td>74.2</td><td>76.5</td><td>70.4</td><td>62.5</td><td>65.2</td><td>56.0</td><td>64.2</td><td>68.1</td></tr><tr><td>LLaVA-13B</td><td>66.8</td><td>68.0</td><td>63.7</td><td>62.3</td><td>66.9</td><td>57.3</td><td>65.0</td><td>68.2</td></tr><tr><td>LLaVA-1.5-13B</td><td>76.1</td><td>78.9</td><td>72.8</td><td>64.1</td><td>67.1</td><td>57.3</td><td>67.7</td><td>69.0</td></tr></table>

Yi-VL [69], ShareGPT4V [7], LLaVA [36], and LLaVA-1.5 [35], with model sizes ranging from 1.3B to 13B. The number of localization heads is fixed to k = 3 for all models.

Benchmarks. To assess visual grounding capabilities, we conduct experiments on Referring Expression Comprehension (REC) and Referring Expression Segmentation (RES) tasks. REC requires the model to predict the bounding box of the referred object, while RES requires the segmentation mask. We use the RefCOCO, RefCOCO+ [22], and Ref-COCOg [18] datasets. We further evaluate the performance of our method on the more challenging scenario, Reasoning Segmentation (ReasonSeg) [26], which requires complex reasoning or world knowledge. For the REC task, we report the performance using Acc@0.5 metric, which is the standard detection metric for REC. For the RES and ReasonSeg task, cIoU is used as the evaluation metric.

Baselines. We compare our method with existing finetuning based and training-free approaches. The fine-tuning based methods include visual grounding specialist models [21, 31, 34, 37, 63, 67, 77], along with fine-tuned LVLMs for object localization [6, 61, 68] or segmentation tasks [26, 45, 65, 74]. The training-free methods include

![](images/13c9d9a15ccebaa518cba30173753ea8f146dcd77f996c31f4606acae940ca32.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
  subgraph Referring Expression Comprehension
  GT["GT"] --> FineTuning["Fine-tuning\nShikra-13B"]
  GT --> TrainingFree["Training-free\nReCLIP"]
  GT --> Ours["Ours"]
  GT --> LLaVA_1.5_7B["LLaVA-1.5-7B"]
  GT --> LLaVA_1.5_13B["LLaVA-1.5-13B"]
  end

  subgraph Referring Expression Segmentation
  GT --> FineTuning["Fine-tuning\nLISA-13B"]
  GT --> TrainingFree["Training-free\nZS-RS"]
  GT --> Ours["Ours"]
  GT --> LLaVA_1.5_7B["LLaVA-1.5-7B"]
  GT --> LLaVA_1.5_13B["LLaVA-1.5-13B"]
  end

  subgraph Bounding Boxes
  GT --> Box1["Expression: nut and carrot section to the right of the meat section."]
  GT --> Box2["Expression: one with finger in mouth."]
  GT --> Box3["Expression: the white chair on bottom."]
  GT --> Box4["Expression: fourth remote from left."]
  GT --> Box5["Expression: doughnut on left second from front."]
  end
```
</details>

Figure 8. Qualitative results of our framework with the baseline models. LVLMs successfully localize the referred objects in various challenging scenarios including multiple similar objects, non-salient objects, and complex spatial relations.

Table 3. Comparison of our framework with LISA [26] on the ReasonSeg (Reasoning Segmentation) benchmark.

<table><tr><td rowspan="2">Method</td><td>val</td><td colspan="3">test</td></tr><tr><td>overall</td><td>short</td><td>long</td><td>overall</td></tr><tr><td>LISA-7B [26]</td><td>52.3</td><td>48.5</td><td>48.9</td><td>48.8</td></tr><tr><td>LISA-13B [26]</td><td>60.3</td><td>50.0</td><td>50.9</td><td>50.8</td></tr><tr><td>LLaVA-1.5-7B (Ours)</td><td>52.4</td><td>48.0</td><td>49.1</td><td>48.7</td></tr><tr><td>LLaVA-1.5-13B (Ours)</td><td>60.5</td><td>48.7</td><td>51.0</td><td>49.9</td></tr></table>

CLIP-based methods [15, 48, 52, 53, 71] and DM-based method [40]. More details on the experimental setup are provided in the Appendix Sec. A.

## 6.2. Main Results

REC and RES. Tab. 1 and Tab. 2 present the results of our method and the baseline models on the REC and RES tasks, respectively. Our framework achieves substantial improvements over the existing training-free methods. Surprisingly, our method performs comparably to the fine-tuned LVLMs, even though our method does not require additional training. For example, in the REC task, the best performance of our approach achieves results on par with Shikra [6] and Ferret [68], which share the same base LLMs as LLaVA-1.5 [35], but are fine-tuned for localization tasks. A similar finding is observed with LISA [26] in the RES task. The results indicate that frozen LVLMs can effectively localize the referred object without any additional training, due to the presence of localization heads.

Notably, the visual grounding capability is enhanced as the model evolves. First, performance consistently improves as model size increases (1.3B to 13B). Second, updates in architecture and training data (e.g., LLaVA to LLaVA-1.5) also boost performance. This observation suggests that the grounding ability of LVLMs could be further enhanced with larger models and more diverse training data.

Fig. 8 compares the qualitative results of our method with those of the baseline models. The results demonstrate that LVLMs can accurately identify the correct object regions, even in challenging scenarios where multiple similar objects are present, or when the referred object is not prominently centered in the image. According to [52], CLIPbased methods struggle to interpret orientation descriptors (e.g., “left”). Therefore, they have to manually decompose the referring expression into multiple components [71] or rely on post-processing steps that use the object’s spatial information [53]. In contrast, our framework can directly predict the bounding box or segmentation mask of the referred object without carefully designed post-processing steps, with the help of the strong text comprehension capabilities of LVLMs. More qualitative results are provided in the Appendix Sec. E.

Reasoning Segmentation. Tab. 3 shows the results of our method and LISA [26] on the ReasonSeg. For a fair comparison, we compare both methods using the same backbone model, LLaVA-1.5 [35]. Our method performs comparably to LISA and sometimes outperforms it. The results suggest that the localization heads in LVLMs are generalizable to various visual grounding tasks, including those that require complex reasoning or world knowledge.

## 6.3. Ablation Studies

Number of Localization Heads. In our main experiments, we set the number of localization heads to k = 3. Here, we investigate the effect of varying k on visual grounding performance. Tab. 4 presents the results of our framework with different k values. We observe that the performance generally improves as k increases from 1 to 3, indicating that top-3 heads complement each other to provide more accurate localization. However, increasing k further does not guarantee better performance, implying that additional heads may introduce noise or redundancy. It is worth noting that the optimal k trend remains consistent across different LVLMs. The results suggest that similar numbers of attention heads are responsible for localization of referred objects in various LVLMs, even though the total number of heads and model architectures differ.

Table 4. Ablation study on the number of localization heads (k) on the RefCOCO validation set for the RES task.

<table><tr><td rowspan="2">Method</td><td colspan="5">k (# of Localization Heads)</td></tr><tr><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td></tr><tr><td>DeepSeek-VL-1.3B</td><td>55.1</td><td>56.3</td><td>56.3</td><td>55.3</td><td>51.2</td></tr><tr><td>MiniGemini-2B</td><td>58.0</td><td>58.5</td><td>59.8</td><td>59.1</td><td>54.2</td></tr><tr><td>InternVL-6B</td><td>61.3</td><td>61.8</td><td>62.1</td><td>61.0</td><td>55.7</td></tr><tr><td>Yi-VL-6B</td><td>61.8</td><td>62.1</td><td>62.5</td><td>62.6</td><td>55.4</td></tr><tr><td>DeepSeek-VL-7B</td><td>70.1</td><td>72.2</td><td>73.9</td><td>73.0</td><td>65.3</td></tr><tr><td>ShareGPT4V-7B</td><td>70.3</td><td>72.4</td><td>73.5</td><td>73.5</td><td>60.8</td></tr><tr><td>LLaVA-7B</td><td>62.7</td><td>63.1</td><td>65.4</td><td>65.3</td><td>57.7</td></tr><tr><td>LLaVA-1.5-7B</td><td>70.3</td><td>73.1</td><td>74.2</td><td>74.1</td><td>65.4</td></tr><tr><td>LLaVA-13B</td><td>63.5</td><td>64.7</td><td>66.8</td><td>66.4</td><td>57.8</td></tr><tr><td>LLaVA-1.5-13B</td><td>71.7</td><td>75.7</td><td>76.1</td><td>76.0</td><td>65.7</td></tr><tr><td>Average</td><td>64.5</td><td>66.0</td><td>67.1</td><td>65.4</td><td>58.9</td></tr></table>

Table 5. Ablation study on the validation of criteria and selection methods for localization heads. The results are reported on the RefCOCO validation set and LLaVA-1.5-13B.

<table><tr><td colspan="2">Criteria</td><td colspan="2">Selection</td><td rowspan="2">REC</td><td rowspan="2">RES</td></tr><tr><td> $S_{img}^{\ell,h}$ </td><td> $H(A^{\ell,h})$ </td><td>Fixed</td><td>Greedy</td></tr><tr><td>✓</td><td></td><td></td><td>✓</td><td>23.7</td><td>18.8</td></tr><tr><td></td><td>✓</td><td></td><td>✓</td><td>29.8</td><td>21.5</td></tr><tr><td>✓</td><td>✓</td><td></td><td>✓</td><td>67.4</td><td>63.8</td></tr><tr><td>✓</td><td></td><td>✓</td><td></td><td>23.9</td><td>19.3</td></tr><tr><td></td><td>✓</td><td>✓</td><td></td><td>31.3</td><td>25.7</td></tr><tr><td>✓</td><td>✓</td><td>✓</td><td></td><td>87.2</td><td>76.1</td></tr></table>

Validation of Criteria and Selection Methods for Localization Heads. In Sec. 4.1, we propose two criteria, attention sum $S _ { \mathrm { i m g } } ^ { \ell , h }$ and spatial entropy $H ( A ^ { \ell , h } )$ , to identify localization heads. Then, we select the fixed top-k heads based on the selection frequency, as described in Sec. 4.2. We ablate the effectiveness of each criterion and validate selection methods. For criterion ablation, we evaluate the performance of our method using each criterion individually: (1) selecting heads with either the highest $S _ { \mathrm { i m g } } ^ { \ell , h }$ or (2) the lowest $H ( A ^ { \ell , h } )$ only. For selection validation, we compare the performance of our method (denoted as the ‘fixed’ method for comparison) with ‘greedy’ selection, where the top-k heads are selected and aggregated per sample. Further details regarding the settings are provided in Appendix Sec. A.

Tab. 5 shows the results of these ablation studies. The performance drops significantly when only one criterion is used, indicating that both criteria are essential for identifying localization heads. Furthermore, the greedy selection method shows worse results than the fixed method. While our criteria identify attention maps exhibiting apparent clusters, they do not ensure that these clusters are formed around text semantics. As a result, the greedy method may select heads that are localized but not text-referred. In contrast, our method involves a statistical analysis (i.e., selection frequency). This ensures that the localization heads are genuinely text-referred, consistently focusing on text-related regions rather than arbitrarily clustered areas.

![](images/4451905e1e352414ccbb27437d7898ccebcb48f068232691fb57035e9b7f74ab.jpg)

<details>
<summary>text_image</summary>

Attention map
(Localization head)
Prediction
GT
</details>

Expression: third from right.  
Figure 9. Failure case of the LLaVA-1.5-13B [35] in visual grounding. The text-to-image attention map from a localization head (L15 H39) shows where the model focuses, helping to understand the model’s failure.

## 6.4. Understanding LVLMs When They Fail

Here, we briefly discuss how localization heads may also help us better understand LVLMs. Specifically, localization heads allow us to identify where LVLMs focus when they fail to ground the correct object. Fig. 9 illustrates an example where the model fails to predict the correct object, the third banana from the right. As shown in the first column of Fig. 9, the text-to-image attention map from a localization head focuses on both the third and fourth bananas from the right. This observation suggests that LVLMs struggle with pinpointing the exact location of objects. These findings show the localization head’s potential to provide a transparent understanding of where the LVLMs focus.

## 7. Conclusion

In this work, we identify localization heads within various LVLMs via criteria, which exhibit strong visual grounding capabilities in response to textual queries. We then propose a simple yet effective training-free framework that assembles the text-to-image attention maps from a few localization heads to predict bounding boxes and segmentation masks for text-relevant regions in the image. Our approach achieves competitive performance compared to fine-tuning based methods. Therefore, we conclude that LVLMs can act as text-referring localizers for visual grounding tasks with their inherent property under the attention mechanisms. We hope that our work opens up new possibilities for analyzing and utilizing the attention mechanisms of LVLMs.

## References

[1] Jinze Bai, Shuai Bai, Shusheng Yang, Shijie Wang, Sinan Tan, Peng Wang, Junyang Lin, Chang Zhou, and Jingren Zhou. Qwen-vl: A versatile vision-language model for understanding, localization, text reading, and beyond. 2023. 16  
[2] Michael Batty. Spatial entropy. Geographical Analysis, 6(1): 1–31, 1974. 2, 4, 13  
[3] Ryan Burgert, Kanchana Ranasinghe, Xiang Li, and Michael S Ryoo. Peekaboo: Text to image diffusion models are zero-shot segmentors. arXiv preprint arXiv:2211.13224, 2022. 3  
[4] Mingdeng Cao, Xintao Wang, Zhongang Qi, Ying Shan, Xiaohu Qie, and Yinqiang Zheng. Masactrl: Tuning-free mutual self-attention control for consistent image synthesis and editing. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 22560–22570, 2023. 2  
[5] Khyathi Raghavi Chandu, Yonatan Bisk, and Alan W Black. Grounding ‘grounding’ in NLP. In Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021, pages 4283–4305, Online, 2021. Association for Computational Linguistics. 2  
[6] Keqin Chen, Zhao Zhang, Weili Zeng, Richong Zhang, Feng Zhu, and Rui Zhao. Shikra: Unleashing multimodal llm’s referential dialogue magic. arXiv preprint arXiv:2306.15195, 2023. 1, 6, 7  
[7] Lin Chen, Jinsong Li, Xiaoyi Dong, Pan Zhang, Conghui He, Jiaqi Wang, Feng Zhao, and Dahua Lin. Sharegpt4v: Improving large multi-modal models with better captions. arXiv preprint arXiv:2311.12793, 2023. 3, 6, 14, 16  
[8] Zhe Chen, Jiannan Wu, Wenhai Wang, Weijie Su, Guo Chen, Sen Xing, Muyan Zhong, Qinglong Zhang, Xizhou Zhu, Lewei Lu, et al. Internvl: Scaling up vision foundation models and aligning for generic visual-linguistic tasks. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 24185–24198, 2024. 3, 6, 14, 16  
[9] Kevin Clark, Urvashi Khandelwal, Omer Levy, and Christopher D. Manning. What does BERT look at? an analysis of BERT’s attention. In Proceedings ofthe 2019 ACL Workshop BlackboxNLP: Analyzing and Interpreting Neural Networks for NLP, pages 276–286, Florence, Italy, 2019. Association for Computational Linguistics. 3  
[10] Explosion AI. spaCy: Industrial-strength Natural Language Processing in Python. 15  
[11] Wei Gao, Fang Wan, Xingjia Pan, Zhiliang Peng, Qi Tian, Zhenjun Han, Bolei Zhou, and Qixiang Ye. Ts-cam: Token semantic coupled attention map for weakly supervised object localization. In Proceedings of the IEEE/CVF international conference on computer vision, pages 2886–2895, 2021. 2  
[12] Cristina Gonzalez, Nicol´ as Ayobi, Isabela Hern´ andez, Jos´ e´ Hernandez, Jordi Pont-Tuset, and Pablo Arbel´ aez. Panoptic´ narrative grounding. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 1364–1373, 2021. 15  
[13] Ronald L. Graham. An efficient algorithm for determining the convex hull of a finite planar set. Info. Proc. Lett., 1: 132–133, 1972. 14  
[14] Costantino Grana, Daniele Borghesani, and Rita Cucchiara. Optimized block-based connected components labeling with decision trees. IEEE Transactions on Image Processing, 19 (6):1596–1609, 2010. 4  
[15] Zeyu Han, Fangrui Zhu, Qianru Lao, and Huaizu Jiang. Zero-shot referring expression comprehension via structural similarity between images and captions. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 14364–14374, 2024. 6, 7  
[16] Shuting He, Henghui Ding, Chang Liu, and Xudong Jiang. Grec: Generalized referring expression comprehension. arXiv preprint arXiv:2308.16182, 2023. 15  
[17] Amir Hertz, Ron Mokady, Jay Tenenbaum, Kfir Aberman, Yael Pritch, and Daniel Cohen-Or. Prompt-to-prompt image editing with cross attention control. arXiv preprint arXiv:2208.01626, 2022. 2  
[18] Ronghang Hu, Marcus Rohrbach, and Trevor Darrell. Segmentation from natural language expressions. In Computer Vision–ECCV2016: 14th European Conference, Amsterdam, The Netherlands, October 11–14, 2016, Proceedings, Part I 14, pages 108–124. Springer, 2016. 1, 2, 3, 6, 13  
[19] Andrew Jaegle, Felix Gimeno, Andy Brock, Oriol Vinyals, Andrew Zisserman, and Joao Carreira. Perceiver: General perception with iterative attention. In International conference on machine learning, pages 4651–4664. PMLR, 2021. 16  
[20] Nick Jiang, Anish Kachinthaya, Suzie Petryk, and Yossi Gandelsman. Interpreting and editing vision-language representations to mitigate hallucinations. arXiv preprint arXiv:2410.02762, 2024. 3  
[21] Aishwarya Kamath, Mannat Singh, Yann LeCun, Gabriel Synnaeve, Ishan Misra, and Nicolas Carion. Mdetrmodulated detection for end-to-end multi-modal understanding. In Proceedings of the IEEE/CVF international conference on computer vision, pages 1780–1790, 2021. 6  
[22] Sahar Kazemzadeh, Vicente Ordonez, Mark Matten, and Tamara Berg. Referitgame: Referring to objects in photographs of natural scenes. In Proceedings of the 2014 conference on empirical methods in natural language processing (EMNLP), pages 787–798, 2014. 3, 4, 5, 6, 13  
[23] Seoyeon Kim, Minguk Kang, Dongwon Kim, Jaesik Park, and Suha Kwak. Extending clip’s image-text alignment to referring image segmentation. In Proceedings of the 2024 Conference of the North American Chapter of the Associationfor Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), pages 4611–4628, 2024. 2  
[24] Alexander Kirillov, Eric Mintun, Nikhila Ravi, Hanzi Mao, Chloe Rolland, Laura Gustafson, Tete Xiao, Spencer Whitehead, Alexander C Berg, Wan-Yen Lo, et al. Segment anything. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 4015–4026, 2023. 3, 6  
[25] Vedang Lad, Wes Gurnee, and Max Tegmark. The remarkable robustness of llms: Stages of inference? arXiv preprint arXiv:2406.19384, 2024. 3  
[26] Xin Lai, Zhuotao Tian, Yukang Chen, Yanwei Li, Yuhui Yuan, Shu Liu, and Jiaya Jia. Lisa: Reasoning segmentation  
via large language model. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 9579–9589, 2024. 1, 2, 3, 6, 7, 13  
[27] Hugo Laurenc¸on, Lucile Saulnier, Leo Tronchon, Stas Bek-´ man, Amanpreet Singh, Anton Lozhkov, Thomas Wang, Siddharth Karamcheti, Alexander M. Rush, Douwe Kiela, Matthieu Cord, and Victor Sanh. Obelics: An open web-scale filtered dataset of interleaved image-text documents, 2023. 16  
[28] Junnan Li, Dongxu Li, Silvio Savarese, and Steven Hoi. Blip-2: Bootstrapping language-image pre-training with frozen image encoders and large language models. In International conference on machine learning, pages 19730– 19742. PMLR, 2023. 1, 16  
[29] Ruiyu Li, Kaican Li, Yi-Chun Kuo, Michelle Shu, Xiaojuan Qi, Xiaoyong Shen, and Jiaya Jia. Referring image segmentation via recurrent refinement networks. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, pages 5745–5753, 2018. 2  
[30] Yanwei Li, Yuechen Zhang, Chengyao Wang, Zhisheng Zhong, Yixin Chen, Ruihang Chu, Shaoteng Liu, and Jiaya Jia. Mini-gemini: Mining the potential of multi-modality vision language models. arXiv preprint arXiv:2403.18814, 2024. 3, 6, 14, 15, 16  
[31] Fangjian Lin, Jianlong Yuan, Sitong Wu, Fan Wang, and Zhibin Wang. Uninext: Exploring a unified architecture for vision recognition. In Proceedings of the 31st ACM International Conference on Multimedia, pages 3200–3208, 2023. 6  
[32] Tsung-Yi Lin, Michael Maire, Serge Belongie, James Hays, Pietro Perona, Deva Ramanan, Piotr Dollar, and C Lawrence´ Zitnick. Microsoft coco: Common objects in context. In Computer Vision–ECCV 2014: 13th European Conference, Zurich, Switzerland, September 6-12, 2014, Proceedings, Part V 13, pages 740–755. Springer, 2014. 13  
[33] Chenxi Liu, Zhe Lin, Xiaohui Shen, Jimei Yang, Xin Lu, and Alan Yuille. Recurrent multimodal interaction for referring image segmentation. In Proceedings of the IEEE international conference on computer vision, pages 1271–1280, 2017. 2  
[34] Chang Liu, Henghui Ding, and Xudong Jiang. Gres: Generalized referring expression segmentation. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages 23592–23601, 2023. 2, 6, 15  
[35] Haotian Liu, Chunyuan Li, Yuheng Li, and Yong Jae Lee. Improved baselines with visual instruction tuning. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 26296–26306, 2024. 1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 23, 24  
[36] Haotian Liu, Chunyuan Li, Qingyang Wu, and Yong Jae Lee. Visual instruction tuning. Advances in neural information processing systems, 36, 2024. 1, 3, 6, 14, 16  
[37] Shilong Liu, Zhaoyang Zeng, Tianhe Ren, Feng Li, Hao Zhang, Jie Yang, Qing Jiang, Chunyuan Li, Jianwei Yang, Hang Su, et al. Grounding dino: Marrying dino with grounded pre-training for open-set object detection. arXiv preprint arXiv:2303.05499, 2023. 6  
[38] Haoyu Lu, Wen Liu, Bo Zhang, Bingxuan Wang, Kai Dong, Bo Liu, Jingxiang Sun, Tongzheng Ren, Zhuoshu Li, Hao Yang, et al. Deepseek-vl: towards real-world visionlanguage understanding. arXiv preprint arXiv:2403.05525, 2024. 3, 6, 15, 16  
[39] Junhua Mao, Jonathan Huang, Alexander Toshev, Oana Camburu, Alan L Yuille, and Kevin Murphy. Generation and comprehension of unambiguous object descriptions. In Proceedings ofthe IEEE conference on computer vision and pattern recognition, pages 11–20, 2016. 1, 2  
[40] Minheng Ni, Yabo Zhang, Kailai Feng, Xiaoming Li, Yiwen Guo, and Wangmeng Zuo. Ref-diff: Zero-shot referring im age segmentation with generative models. arXiv preprint arXiv:2308.16777, 2023. 3, 6, 7  
[41] Elia Peruzzo, Enver Sangineto, Yahui Liu, Marco De Nadai, Wei Bi, Bruno Lepri, and Nicu Sebe. Spatial entropy as an inductive bias for vision transformers. Machine Learning, 113(9):6945–6975, 2024. 4, 13  
[42] Koutilya Pnvr, Bharat Singh, Pallabi Ghosh, Behjat Siddiquie, and David Jacobs. Ld-znet: A latent diffusion approach for text-based image segmentation. In Proceedings ofthe IEEE/CVF International Conference on Computer Vision, pages 4157–4168, 2023. 2  
[43] Dustin Podell, Zion English, Kyle Lacey, Andreas Blattmann, Tim Dockhorn, Jonas Muller, Joe Penna,¨ and Robin Rombach. Sdxl: Improving latent diffusion models for high-resolution image synthesis. In The Twelfth International Conference on Learning Representations. 16, 24  
[44] Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al. Learning transferable visual models from natural language supervision. In International conference on machine learning, pages 8748–8763. PMLR, 2021. 3  
[45] Hanoona Rasheed, Muhammad Maaz, Sahal Shaji, Abdelrahman Shaker, Salman Khan, Hisham Cholakkal, Rao M Anwer, Eric Xing, Ming-Hsuan Yang, and Fahad S Khan. Glamm: Pixel grounding large multimodal model. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 13009–13018, 2024. 1, 6, 15  
[46] Shaoqing Ren, Kaiming He, Ross Girshick, and Jian Sun. Faster r-cnn: Towards real-time object detection with region proposal networks. IEEE transactions on pattern analysis and machine intelligence, 39(6):1137–1149, 2016. 3  
[47] Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, and Bjorn Ommer. High-resolution image¨ synthesis with latent diffusion models. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages 10684–10695, 2022. 3  
[48] Haozhan Shen, Tiancheng Zhao, Mingwei Zhu, and Jianwei Yin. Groundvlp: Harnessing zero-shot visual grounding from vision-language pre-training and open-vocabulary object detection. In Proceedings of the AAAI Conference on Artificial Intelligence, pages 4766–4775, 2024. 6, 7  
[49] Hengcan Shi, Hongliang Li, Fanman Meng, and Qingbo Wu. Key-word-aware network for referring expression image seg-  
mentation. In Proceedings of the European Conference on Computer Vision (ECCV), pages 38–54, 2018. 2  
[50] Mohit Shridhar, Dixant Mittal, and David Hsu. Ingress: Interactive visual grounding of referring expressions. The International Journal ofRobotics Research, 39(2-3):217–232, 2020. 2  
[51] Oriane Simeoni, Gilles Puy, Huy V Vo, Simon Roburin,´ Spyros Gidaris, Andrei Bursuc, Patrick Perez, Renaud´ Marlet, and Jean Ponce. Localizing objects with selfsupervised transformers and no labels. arXiv preprint arXiv:2109.14279, 2021. 4  
[52] Sanjay Subramanian, William Merrill, Trevor Darrell, Matt Gardner, Sameer Singh, and Anna Rohrbach. ReCLIP: A strong zero-shot baseline for referring expression comprehension. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 5198–5215, Dublin, Ireland, 2022. Associa tion for Computational Linguistics. 3, 6, 7  
[53] Yucheng Suo, Linchao Zhu, and Yi Yang. Text augmented spatial aware zero-shot referring image segmentation. In Findings of the Association for Computational Linguistics: EMNLP 2023, pages 1032–1043, Singapore, 2023. Association for Computational Linguistics. 3, 6, 7  
[54] Raphael Tang, Linqing Liu, Akshat Pandey, Zhiying Jiang, Gefei Yang, Karun Kumar, Pontus Stenetorp, Jimmy Lin, and Ferhan Ture. What the daam: Interpreting stable diffusion using cross attention. arXiv preprint arXiv:2210.04885, 2022. 2  
[55] OpenGVLab Team. Internvl2, 2024. 16  
[56] Shengbang Tong, Ellis Brown, Penghao Wu, Sanghyun Woo, Manoj Middepogu, Sai Charitha Akula, Jihan Yang, Shusheng Yang, Adithya Iyer, Xichen Pan, et al. Cambrian-1: A fully open, vision-centric exploration of multimodal llms. arXiv preprint arXiv:2406.16860, 2024. 1  
[57] Elena Voita, David Talbot, Fedor Moiseev, Rico Sennrich, and Ivan Titov. Analyzing multi-head self-attention: Specialized heads do the heavy lifting, the rest can be pruned. In Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics, pages 5797–5808, Florence, Italy, 2019. Association for Computational Linguistics. 3  
[58] Feng Wang, Jieru Mei, and Alan Yuille. Sclip: Rethinking self-attention for dense vision-language inference. In European Conference on Computer Vision, pages 315–332. Springer, 2025. 4  
[59] Lean Wang, Lei Li, Damai Dai, Deli Chen, Hao Zhou, Fandong Meng, Jie Zhou, and Xu Sun. Label words are anchors: An information flow perspective for understanding incontext learning. In Proceedings ofthe 2023 Conference on Empirical Methods in Natural Language Processing, pages 9840–9855, Singapore, 2023. Association for Computational Linguistics. 3  
[60] Peng Wang, Shijie Wang, Junyang Lin, Shuai Bai, Xiaohuan Zhou, Jingren Zhou, Xinggang Wang, and Chang Zhou. One-peace: Exploring one general representation model toward unlimited modalities. arXiv preprint arXiv:2305.11172, 2023. 6  
[61] Weihan Wang, Qingsong Lv, Wenmeng Yu, Wenyi Hong, Ji Qi, Yan Wang, Junhui Ji, Zhuoyi Yang, Lei Zhao, Xixuan  
Song, et al. Cogvlm: Visual expert for pretrained language models. arXiv preprint arXiv:2311.03079, 2023. 1, 6  
[62] Zhaoqing Wang, Yu Lu, Qiang Li, Xunqiang Tao, Yandong Guo, Mingming Gong, and Tongliang Liu. Cris: Clipdriven referring image segmentation. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages 11686–11695, 2022. 2  
[63] Jiannan Wu, Yi Jiang, Bin Yan, Huchuan Lu, Zehuan Yuan, and Ping Luo. Uniref++: Segment every reference object in spatial and temporal spaces. arXiv preprint arXiv:2312.15715, 2023. 6  
[64] Size Wu, Sheng Jin, Wenwei Zhang, Lumin Xu, Wentao Liu, Wei Li, and Chen Change Loy. F-lmm: Grounding frozen large multimodal models. arXiv preprint arXiv:2406.05821, 2024. 3, 15  
[65] Zhuofan Xia, Dongchen Han, Yizeng Han, Xuran Pan, Shiji Song, and Gao Huang. Gsva: Generalized segmentation via multimodal large language models. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 3858–3869, 2024. 1, 6  
[66] Li Xu, Mark He Huang, Xindi Shang, Zehuan Yuan, Ying Sun, and Jun Liu. Meta compositional referring expression segmentation. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 19478– 19487, 2023. 2  
[67] Zhao Yang, Jiaqi Wang, Yansong Tang, Kai Chen, Hengshuang Zhao, and Philip HS Torr. Lavt: Language-aware vision transformer for referring image segmentation. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 18155–18165, 2022. 2, 6  
[68] Haoxuan You, Haotian Zhang, Zhe Gan, Xianzhi Du, Bowen Zhang, Zirui Wang, Liangliang Cao, Shih-Fu Chang, and Yinfei Yang. Ferret: Refer and ground anything anywhere at any granularity. arXiv preprint arXiv:2310.07704, 2023. 1, 6, 7  
[69] Alex Young, Bei Chen, Chao Li, Chengen Huang, Ge Zhang, Guanwei Zhang, Heng Li, Jiangcheng Zhu, Jianqun Chen, Jing Chang, et al. Yi: Open foundation models by 01. ai. arXiv preprint arXiv:2403.04652, 2024. 3, 6, 14, 16  
[70] Licheng Yu, Patrick Poirson, Shan Yang, Alexander C Berg, and Tamara L Berg. Modeling context in referring expressions. In Computer Vision–ECCV2016: 14th European Conference, Amsterdam, The Netherlands, October 11-14, 2016, Proceedings, Part II 14, pages 69–85. Springer, 2016. 1, 2  
[71] Seonghoon Yu, Paul Hongsuck Seo, and Jeany Son. Zeroshot referring image segmentation with global-local context features. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 19456– 19465, 2023. 3, 6, 7  
[72] Sukmin Yun, Hankook Lee, Jaehyung Kim, and Jinwoo Shin. Patch-level representation learning for self-supervised vision transformers. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages 8354– 8363, 2022. 4  
[73] Bowen Zhang, Zhi Tian, Quan Tang, Xiangxiang Chu, Xiaolin Wei, Chunhua Shen, et al. Segvit: Semantic segmentation with plain vision transformers. Advances in Neural Information Processing Systems, 35:4971–4982, 2022. 2  
[74] Zheng Zhang, Yeyao Ma, Enming Zhang, and Xiang Bai. Psalm: Pixelwise segmentation with large multi-modal model. arXiv preprint arXiv:2403.14598, 2024. 1, 6  
[75] Wenliang Zhao, Yongming Rao, Zuyan Liu, Benlin Liu, Jie Zhou, and Jiwen Lu. Unleashing text-to-image diffusion models for visual perception. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 5729–5739, 2023. 2  
[76] Zifan Zheng, Yezhaohui Wang, Yuxin Huang, Shichao Song, Bo Tang, Feiyu Xiong, and Zhiyu Li. Attention heads of large language models: A survey. arXiv preprint arXiv:2409.03752, 2024. 3  
[77] Chaoyang Zhu, Yiyi Zhou, Yunhang Shen, Gen Luo, Xingjia Pan, Mingbao Lin, Chao Chen, Liujuan Cao, Xiaoshuai Sun, and Rongrong Ji. Seqtr: A simple yet universal network for visual grounding. In European Conference on Computer Vi sion, pages 598–615. Springer, 2022. 6

## Appendix

## A. Experimental Details

Experimental Setting. All experiments and evaluations are conducted on a single NVIDIA GeForce RTX A6000 48GB GPU. We only use the inference stage of the models without any fine-tuning or training.

Analysis Setting. In Sec. 4, we identify and analyze localization heads in various LVLMs. We use the RefCOCO training set to prevent validation set leakage. To calculate the selection frequency of individual heads, we randomly select 1,000 image-text pair samples from the RefCOCO training set and average the results over five trials to validate consistency. When analyzing the selection frequency and IoU, we binarize the attention weights by assigning 1 above the mean value and 0 below it and calculate the IoU between the binarized attention weights and the ground-truth mask. We repeat this process for 1,000 image-text pairs and average the IoU scores.

Dataset Details. We evaluate our method on the following datasets:

• RefCOCO, RefCOCO+ [22], and RefCOCOg [18] datasets, sourced from MS-COCO [32], offer a collection of referring expressions and associated images. RefCOCO consists of 19,994 images paired with 142,210 expressions, while RefCOCO+ includes 19,992 images and 141,564 expressions. RefCOCOg, on the other hand, contains 26,771 images and 104,560 expressions. The expressions in RefCOCO and RefCOCO+ are generally concise, with an average of 1.6 nouns and 3.6 words per expression. In contrast, RefCOCOg features more descriptive expressions, averaging 2.8 nouns and 8.4 words.  
• ReasonSeg: The dataset and benchmark for reasoning segmentation were first introduced in LISA [26]. The resulting ReasonSeg benchmark consists of 1,218 imageinstruction-mask data samples, which are further divided into three splits: training (239 samples), validation (200 samples), and test (779 samples).

Main Experiments Setting. We evaluate our method on the following tasks:

• Referring Expression Comprehension (REC) and Referring Expression Segmentation (RES): The datasets evaluated for the main results in Sec.6.2 include RefCOCO (validation, test-A, test-B), RefCOCO+ (validation, test-A, test-B), and RefCOCOg (validation, test). All evaluations were conducted using the UNC split.

• Reasoning Segmentation (ReasonSeg): Reasoning Segmentation was first introduced in LISA [26]. This task shares a similar formulation with the referring expression segmentation task but is considerably more challenging. The key distinction lies in the complexity of the query text in reasoning segmentation. Rather than simple phrases (e.g., “the blue mug”), the queries involve more nuanced descriptions (e.g., “the container used for drinking, located next to the plate”) or longer sentences (e.g., “Find the item on the table that someone would use to hold liquid, often paired with a saucer”). These queries demand advanced reasoning and a deeper understanding of contextual and world knowledge. All reasoning segmentation results were evaluated using the ReasonSeg benchmark, which includes both the validation set and test set. Performance was measured across short queries, long queries, and overall, following the same experimental setup as LISA [26] to ensure consistency in comparisons.

Ablation Studies Setting. In Sec. 6.3, we ablate the effectiveness of each criterion and validate the selection methods. In this section, we provide details of the ablation studies.

For criterion ablation, we consider two approaches: (1) selecting heads based solely on the highest $S _ { \mathrm { i m g } } ^ { \dot { \ell } , h }$ values, or (2) selecting heads based solely on the lowest $H ( A ^ { \ell , h } )$ values. In approach (1), we select the 10 heads with the highest $S _ { \mathrm { i m g } } ^ { \ell , h }$ values and calculate their selection frequency. Similarly, in approach (2), we select the 10 heads with the lowest $H ( A ^ { \ell , h } )$ values and calculate their selection frequency.

For selection validation, we introduce the ‘greedy’ selection method, which selects the top-k heads per sample without considering the overall selection frequency. When applying the greedy selection method and criterion (1) simultaneously, we select the top-k heads with the highest $S _ { \mathrm { i m g } } ^ { \ell , h }$ values for each sample. Criterion (2) is applied in a similar manner, simultaneously selecting the top-k heads with the lowest $H ( A ^ { \ell , h } )$ values for each sample.

## B. Detailed Description of Algorithms

## B.1. Spatial Entropy

Spatial entropy [2] adjusts the probability of attention being focused in a region by factoring in the size of that region, ensuring fair comparison across areas of different sizes. Note that, our spatial entropy calculation is based on the previous work [41] which validated the effectiveness of spatial entropy in image attention maps within vision transformer. We begin by computing the image attention map $A ^ { \ell , h }$ as follows:

$$
\boldsymbol {A} ^ {\ell , h} = \operatorname{ReLU} \left(\operatorname{reshape} (\boldsymbol {a} ^ {\ell , h}) - m\right), \tag {4}
$$

where the ReLU function is applied after reshaping by $P \times P$ , and it retains only those values in $\mathbf { \Omega } _ { \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { \Omega } \mathbf { a } ^ { \ell , h } }$ that are greater than the mean m. Next, we identify the connected components $C _ { A ^ { \ell , h } } = \{ C _ { 1 } , C _ { 2 } , \ldots , C _ { n } \}$ from $A ^ { \ell , h }$

$$
C _ {\boldsymbol {A} ^ {\ell , h}} = \text {ConnectedComponents} (\boldsymbol {A} ^ {\ell , h}), \tag {5}
$$

where the connected components are determined by applying an 8-connectivity relation among the non-zero elements of $A ^ { \ell , h }$ . Each connected component $C _ { n }$ (with

$1 ~ \leq ~ n ~ \leq ~ N )$ in $C _ { A ^ { \ell , h } }$ is defined as the set of coordinates $C _ { n } = \{ ( x _ { 1 } , y _ { 1 } ) , ( x _ { 2 } , y _ { 2 } ) , \dots , ( x _ { k _ { n } } , y _ { k _ { n } } ) \}$ for the nth component, where $k _ { n } = | C _ { n } |$ represents the cardinality, or the number of elements, in $C _ { n }$ . Finally, we calculate the spatial entropy $H ( A ^ { \ell , h } )$ as follows:

$$
H (\boldsymbol {A} ^ {\ell , h}) = - \sum_ {n = 1} ^ {N} P (C _ {n}) \log P (C _ {n}), \tag {6}
$$

where this entropy is computed using Shannon’s entropy formula. Here, $P ( C _ { n } )$ represents the probability of observing each connected component $C _ { n }$ within $A ^ { \ell , h }$ . The probability $P ( C _ { n } )$ for each component $C _ { n }$ is defined as:

$$
P (C _ {n}) = \frac {| C _ {n} |}{\sum_ {n = 1} ^ {N} | C _ {n} |}, \tag {7}
$$

where $P ( C _ { n } )$ is calculated by dividing the area of $C _ { n }$ by the total area of all components in $A ^ { \bar { \ell } , h }$ . This provides a normalized measure of spatial focus. The resulting spatial entropy $H ( A ^ { \ell , h } )$ ranges from 0 to 1. A value of 0 indicates that attention is completely focused on a single region, while a value of 1 suggests that attention is evenly distributed across the image. This measure thus enables us to evaluate the dispersion of the model’s attention across different regions within the image.

## B.2. Details of Our Framework

In this section, we provide a detailed description of our framework, described in Sec. 5 of the main paper.

Binarization of the Attention Map. The attention map is binarized by setting values above the mean to 1. This approach effectively highlights the most significant regions of the attention map.

Gaussian Smoothing. Gaussian smoothing is applied using a kernel size of $k = 7$ and a standard deviation of $\sigma =$ 1.0. These parameters ensure a balance between smoothing effects and detail preservation.

Convex Hull Algorithm for Bounding Box. To determine the bounding box in an assembled attention map from the localization heads, we employ the convex hull algorithm [13]. In cases where multiple convex hulls are present within the same attention map, we retain only the largest convex hull. Subsequently, we calculate the smallest tight bounding box that encloses the retained convex hull and we use it as the final bounding box.

## C. More Analysis on Localization Heads

## C.1. Extended Analysis Across More LVLMs

In this section, we extend the analysis of localization heads in Sec. 4 of the main paper to more LVLMs, including InternVL [8], LLaVA [36], Mini-Gemini [30], ShareGPT4V [7], and Yi-VL [69].

Average Attention Sum in More LVLMs. We extend Fig. 3 in the main paper to demonstrate that relatively few attention heads significantly contribute to the model’s textimage interaction. As shown in Fig. 11, the trend of the average ${ \bf \bar { \mathbf { \Lambda } } } _ { S _ { \mathrm { i m g } } ^ { \ell , h } }$ values remains consistent across different LVLMs.

Selection Frequency and IoU in More LVLMs. Similar to the above, we extend Fig. 6 in the main paper to cover additional LVLMs. Fig. 12 presents the selection frequency and a scatter plot of selection frequency rank versus IoU for each attention head across various LVLMs. The results confirm that our observations hold consistently across different LVLMs.

## C.2. Robustness of Localization Head Selection

In this section, we validate the robustness of our localization head selection method across different threshold values (τ) and the number of selected heads (N). The experiments below indicate that localization head selection is not sensitive to the choice of τ or N.

Threshold τ. Fig. 3 in the main paper presents the average $S _ { \mathrm { i m g } }$ values for each attention head, setting the threshold τ at the point where the maximum curvature is observed. We select maximum curvature as the threshold to reduce the need for manual tuning; however, other τ values can also be considered. Therefore, we further validate that plausible τ values can give consistent results with the maximum curvature. To this end, we calculate the selection frequency of the heads based on different τ values and compare them with the results obtained using the maximum curvature. The results are presented in Fig. 13. We observe that the same localization heads are consistently selected across different τ values, indicating that our analysis results are robust to the choice of τ.

Number of Heads N. In Fig. 6(a) of the main paper, we select the 10 heads with the lowest $H ( A ^ { \ell , h } )$ values and repeat the process for 1,000 image-text pairs to calculate the selection frequency. We also investigate the effect of selecting different numbers of heads (N) on the selection frequency. We conduct experiments from N = 1 to N = 14 and compare the results with the selection frequency obtained using N = 10 (default setting). As shown in Fig. 14, we can obtain the same top-3 localization heads consistently across different N values, suggesting that the selection of localization heads is robust to the choice of N.

## D. More Experiments

## D.1. Comparison with Baseline Models

Most LVLMs, including the LLaVA [36] family, likely encode localization knowledge in their pretrained weights, possibly due to pretraining with bounding box coordinates or visual instruction prompts [36]. In Tab. 6, we compare baseline models and our proposed method, revealing the baseline models’ poor localization accuracy, likely due to their focus on describing objects rather than precise localization. Moreover, the localization head might provide only indirect support when text generation unfolds in its usual course. As a result, it becomes difficult for the model to directly output accurate object or region coordinates required for visual grounding, unless the information from this head is explicitly scrutinized. Thus, the localization head’s practical value can be realized as long as it is integrated with our proposed method.

Table 6. Comparison performance to baseline models

<table><tr><td>REC (RefCOCOg)</td><td>DeepSeekVL-1.3B</td><td>LLaVA-1.5-7B</td><td>LLaVA-1.5-13B</td></tr><tr><td>Baseline</td><td>1.5</td><td>2.92</td><td>5.28</td></tr><tr><td>Ours</td><td>65.2</td><td>82.3</td><td>84.3</td></tr></table>

Table 7. Performance comparison between F-LMM [64] and our method on the RES task. We note that F-LMM models are trained on the training set of Referring Expression Segmentation datasets.

<table><tr><td rowspan="2">Method</td><td colspan="3">RefCOCO</td><td colspan="3">RefCOCO+</td><td colspan="2">RefCOCOg</td></tr><tr><td>val</td><td>testA</td><td>testB</td><td>val</td><td>testA</td><td>testB</td><td>val</td><td>test</td></tr><tr><td colspan="9">F-LMM (Fine-tuning on RES)</td></tr><tr><td>DeepSeek-VL-1.3B</td><td>75.0</td><td>78.1</td><td>69.5</td><td>62.8</td><td>70.8</td><td>56.3</td><td>68.2</td><td>68.5</td></tr><tr><td>Mini-Gemini-2B</td><td>75.0</td><td>78.6</td><td>69.3</td><td>63.7</td><td>71.4</td><td>53.3</td><td>67.3</td><td>67.4</td></tr><tr><td>DeepSeek-VL-7B</td><td>76.1</td><td>78.8</td><td>72.0</td><td>66.4</td><td>73.2</td><td>57.6</td><td>70.1</td><td>70.4</td></tr><tr><td>LLaVA-1.5-7B</td><td>75.2</td><td>79.1</td><td>71.9</td><td>63.7</td><td>71.8</td><td>54.7</td><td>67.1</td><td>68.1</td></tr><tr><td colspan="9">Ours (Training-free)</td></tr><tr><td>DeepSeek-VL-1.3B</td><td>56.3</td><td>57.0</td><td>52.7</td><td>51.2</td><td>55.5</td><td>49.2</td><td>52.3</td><td>55.8</td></tr><tr><td>Mini-Gemini-2B</td><td>59.8</td><td>60.3</td><td>55.5</td><td>56.3</td><td>59.9</td><td>51.8</td><td>55.1</td><td>60.3</td></tr><tr><td>DeepSeek-VL-7B</td><td>73.9</td><td>76.6</td><td>70.7</td><td>63.1</td><td>67.1</td><td>56.5</td><td>64.0</td><td>68.9</td></tr><tr><td>LLaVA-1.5-7B</td><td>74.2</td><td>76.5</td><td>70.4</td><td>62.5</td><td>65.2</td><td>56.0</td><td>64.2</td><td>68.1</td></tr></table>

## D.2. Comparision with F-LMM

We compare our method with F-LMM [64], which also leverages the attention weights of frozen LVLMs for visual grounding. The differences between F-LMM and our method are as follows. First, F-LMM still requires finetuning its mask decoder modules on visual grounding datasets (i.e., referring expression segmentation datasets). Second, F-LMM uses all attention heads without considering the relative importance of each, leaving the decoder modules to interpret the entire set of attention weights. In contrast, our approach requires no fine-tuning and directly utilizes a few selected attention heads that are particularly useful for localizing objects in the image. Furthermore, our framework provides a transparent understanding of where the model focuses through localization heads, which is not available in F-LMM.

Tab. 7 presents the performance comparison between F-LMM and our method on the RES task. In smaller LVLMs (e.g., DeepSeek-VL-1.3B [38] and Mini-Gemini-2B [30]), F-LMM outperforms our method. However, in relatively larger LVLMs (e.g., DeepSeek-VL-7B [38] and LLaVA-1.5-7B [35]), our method demonstrates performance comparable to F-LMM, with only a slight gap. This result sug gests that the localization heads have competitive potential with the specialized mask decoder modules for visual grounding tasks, especially in relatively larger LVLMs.

Table 8. Ablation study on Gaussian smoothing parameters (σ and κ). The performance is evaluated using the RefCOCO validation set (UNC split) with the LLaVA-1.5-13B [35].

<table><tr><td rowspan="2">Task</td><td colspan="6">σ (standard deviation)</td></tr><tr><td>0.0</td><td>0.4</td><td>0.8</td><td>1.0</td><td>1.4</td><td>1.8</td></tr><tr><td>REC</td><td>85.5</td><td>86.8</td><td>87.2</td><td>87.2</td><td>86.8</td><td>84.3</td></tr><tr><td>RES</td><td>74.3</td><td>75.2</td><td>76.1</td><td>76.1</td><td>75.2</td><td>72.7</td></tr><tr><td rowspan="2">Task</td><td colspan="6">κ (kernel size)</td></tr><tr><td>1</td><td>3</td><td>5</td><td>7</td><td>9</td><td>11</td></tr><tr><td>REC</td><td>85.5</td><td>86.5</td><td>86.5</td><td>87.2</td><td>87.2</td><td>87.2</td></tr><tr><td>RES</td><td>74.3</td><td>75.2</td><td>75.2</td><td>76.1</td><td>76.1</td><td>76.1</td></tr></table>

Table 9. Performance comparison with F-LMM [64] on the PNG [12] benchmark.

<table><tr><td>PNG (all)</td><td>Ours</td><td>F-LMM</td></tr><tr><td>DeepSeekVL-7B</td><td>66.7</td><td>65.7</td></tr></table>

## D.3. Gaussian Smoothing Ablation

When assembling the attention map in the localization head (see Sec. 5 of the main paper), we apply Gaussian smoothing to the attention map to minimize potential random noise. In this section, we conduct an ablation study on the parameters of Gaussian smoothing to better understand the robustness of our framework across different values of standard deviation σ and kernel size κ. For the experiments, LLaVA-1.5-13B [35] was evaluated using the RefCOCO validation set (UNC split).

The results are presented in Tab. 8. Regardless of the selected σ and κ, Gaussian smoothing consistently enhances performance in almost all cases. The findings highlight that the framework is robust to varying choices of σ and κ. Furthermore, even when using the basic attention map of localization heads without Gaussian smoothing (σ = 0 or κ = 1), the performance remains competitive, with only a 1.9% drop compared to the best case. This demonstrates that Gaussian smoothing only serves as an auxiliary postprocessing step for refining the attention map from localization heads.

## D.4. Multi-Object Grounding Tasks

Beyond single-object tasks, our pipeline also suggests promise for multi-object grounding. We utilize spaCy [10] to extract noun tokens for generating attention maps (see Fig. 10), obtaining comparable results on the PNG benchmark [12], with improvements observed relative to F-LMM (see Tab. 9). Similarly, we believe this approach holds promise for extension to other various tasks [16, 34, 45].

## E. More Qualitative Results

We present more qualitative results of our framework, including the performance of 10 LVLMs [7, 8, 30, 35, 36, 38, 69], with parameter numbers ranging from 1.3B to 13B, on visual grounding tasks. Fig. 15, Fig. 16, and Fig. 17 present the qualitative results of our method on the Referring Expression Comprehension (REC), Referring Expression Segmentation (RES), and Reasoning Segmentation tasks, respectively. The results demonstrate that only a few selected localization heads are sufficient to accurately localize objects in the image based on the text query. Our method effectively localizes objects in various scenarios.

## F. Applications

## F.1. Real World Application

Fig. 18 illustrates that the localization heads effectively capture the region or object of interest in images from the real world, based on the provided expressions. This result demonstrates the robustness of the localization heads across various types of data.

## F.2. Image Editing

Fig. 19 presents the results of image inpainting performed by integrating Stable Diffusion XL (SDXL) [43]. The frozen LVLM generates a segmentation mask corresponding to the expression, and this mask, along with an additional text prompt, is used as input to the diffusion model to generate the desired image. These results demonstrate that the segmentation mask corresponding to the referred text, output by a small number of localization heads from the frozen LVLM, can serve as guidance for diffusion models. This compatibility enables its application in image editing tasks.

## G. Limitations

We propose a simple yet effective framework for trainingfree visual grounding, which leverages the localization heads of LVLMs. Our framework successfully localizes objects in images based on text queries without requiring any fine-tuning and achieves superior performance compared to existing training-free methods. However, our method still has some limitations that could be addressed in future work.

First, our work, as illustrated in Fig. 10, reveals the potential for multi-object grounding; however, the establishment of a formalized pipeline or the development of a more streamlined implementation remains limited. The task of rendering the identified localization head more practical, user-friendly, and adaptable across a diverse range of applications continues to pose a significant challenge. This presents a compelling avenue for future research.

![](images/8a2f5091c6112d4d79cbfdf73db52942d6e86229fc8a9bdd6981d02a154ea7ed.jpg)

<details>
<summary>text_image</summary>

Segmentation Results.
girl
boy
girl
boy
</details>

Figure 10. Multi-object segmentation results from the localization heads of DeepSeekVL-7B, along with the corresponding raw attention maps.

Second, our method is less suitable for LVLMs or methods that do not preserve spatial information in images (e.g., pooling) [1, 19, 27, 28, 55]. These methods make it challenging to explicitly obtain image attention maps. To collect the attention map, a reverse computation is required to determine the order in which image tokens were input during processing. We leave the application of our framework to these methods for future exploration.

![](images/61d5c2a67987d73e91a4c7c149f3da8d077bcf5a4fc38faf690b2ca80235de7b.jpg)  
Figure 11. Average $S _ { \mathrm { i m g } } ^ { \ell , h }$ values for each attention head in more LVLMs. τ is set at the point where the maximum curvature is observed.

![](images/44e43f699a15deb44f20b1497863beb127215fc16e0be32f71153240cfd3430e.jpg)  
Figure 12. Selection frequency of individual heads and scatter plot of selection frequency rank versus each head’s average IoU in more LVLMs. The Spearman correlation coefficient (ρ) between the selection frequency rank and the average IoU is displayed in the top-right corner of each plot. The observed Spearman correlation are statistically significant $( p < 0 . 0 0 1 )$ for all LVLMs.

![](images/7276b0f45ca7fb938896a690e26cdcf11cdfd2a24e971a5c049943aee7e3cd8b.jpg)  
Figure 13. Selection frequency of individual heads across different τ values. τ represents the threshold for the sum of each head’s attention map. Our analysis focuses on heads with attention map sums greater than τ, which are selected as targets for selection frequency evaluation. In the main paper, we select the threshold where the maximum curvature is observed. The top-3 localization heads remain consistent across different τ values, demonstrating the robustness of our analysis to variations in τ.

![](images/47fa4879b422f953f1ac6b57983bc234afdb77b123b9fa007cbc126a80b80833.jpg)  
Figure 14. Selection frequency of individual heads across different N values. N refers to the number of selected heads based on the lowest $H ( A ^ { \ell , h } )$ values. Default setting is N = 10. The top-3 localization heads are consistent across different N values, indicating the robustness of localization head selection to the choice of N.

Expression: pillow behind kid.  
Expression: red train middle right.  
Expression: laptop to the right of the other laptop.  
Expression: zebra on the left that is not grazing.  
Expression: the wonderful father in the middle he is glorious.  
Expression: left man standing in black.  
![](images/3f0c41649a65659af0d52bb7ae04f3da636e9042d43341dc18b7a050a86ca897.jpg)  
Figure 15. Qualitative results of Referring Expression Comprehension.

![](images/287112c629e892c1ffe45a12787856c87f54fe9f2f43366f23af41255370f84f.jpg)

<details>
<summary>text_image</summary>

Expression:
front row
second from
left.
GT
Expression:
zebra whos
full body is
shown.
Expression:
wood floor at
the bottom of
photo.
Expression:
top left sheep.
Expression:
top left
banana.
Expression:
giraffe on the
far right.
LLaVA-7B
LLaVA-13B
LLaVA-1.5-7B
LLaVA-1.5-7B
DeepSeek-1.3B
DeepSeek-7B
DeepSeek-7B
InternVL-6B
Mini-Gemini-2B
ShareGPT4V-7B
Yi-VL-6B
</details>

Figure 16. Qualitative results of Referring Expression Segmentation.

## LLaVA-1.5-13B with only three attention heads (L15 H39, L16 H30, L7 H2)

![](images/5366c3f4abe238c01d0e89e3d0c4d6453a0e421cf803927712f70e9816020242.jpg)

## Expression:

In gymnastics competitions, athletes perform a variety of acrobatic movements using different apparatus. Regarding the picture, what equipment could be utilized by athletes to accomplish challenging and impressive movements such as flips and vaults?

## Expression:

What item in the picture could be utilized as the accessory that people typically wear around their neck for elegant formal attire?

## Expression:

Something used for playing music.

## Expression:

During an air show, pilots perform various aerial maneuvers to entertain the audience. What spectacle in the picture indicates that a pilot is performing a spectacular and dazzling aerial stunt?

## Expression:

The frictional part used for igniting.

![](images/ed3bdf0755d48e7b4c875b13c90a515ac48ae099c4e8ed047702218212e6f6a4.jpg)  
Figure 17. Qualitative results of Reasoning Segmentation.

## Expression:

If we were attending a car show and desired to sit down and observe the displayed cars, where might we locate a suitable place to relax?

## Expression:

In modern cuisine, food decoration plays an important role in enhancing the dining experience. Based on the picture, which food item is most likely to be used for decoration purposes?

## Expression:

What is the item in this picture that could be utilized to hit the ball during a game of tennis?

## Expression:

In horse riding, it is crucial to have control and direction over the horse. What object in the picture is typically used for guiding and controlling the movements of a horse?

## Expression:

Please identify which object in the picture could serve as a toy for a dog, as dogs relish playing with a variety of different toys that are specifically designed for biting and chewing.

LLaVA-1.5-13B with only three attention heads (L15 H39, L16 H30, L7 H2)

![](images/a3a5d9b818de5c42e066e73d5a0453231248cb41815ab13cb9a40df8116b6b93.jpg)

<details>
<summary>natural_image</summary>

Cartoon illustration of a family of five characters including a man, a child, and two children with toys, standing together against a blue background (no text or symbols)
</details>

Original Image

![](images/1e5e29cef8942940347f611d5c4fd65132d54164c4ccc5e04873cffacdd52a47.jpg)

<details>
<summary>natural_image</summary>

Cartoon illustration of a family of five characters including a child, a woman, and two children (no text or symbols present)
</details>

Expression: a father and the youngest.

![](images/7dfceb6dfc732c577f17e1fbf189c563357030f8ec2e28ba8c0fe8c6616c5d13.jpg)

<details>
<summary>natural_image</summary>

Baseball player celebrating on court with crowd in background (no visible text or symbols)
</details>

Original Image

![](images/aeb8883775640a3d26bacfd85bb07364f6a578a7efc3fb4835352e65df3adf32.jpg)

<details>
<summary>natural_image</summary>

Baseball player in white uniform running on court with crowd in background (no visible text or symbols)
</details>

Expression: Ohtani Shohei.

![](images/91b2e6b4362fe369be75a39296fbbde311c339fdd31da3530c2c80e480bb03f6.jpg)

<details>
<summary>natural_image</summary>

Two musicians performing on electric guitar stands against a pink background (no text or symbols visible)
</details>

Original Image

![](images/17063900f4372f5135922669b2f7f34d65123926f3be0b7828951dfb58a376bb.jpg)

<details>
<summary>natural_image</summary>

Two musicians in front of electric guitar and electric guitar models on a pink background (no text or symbols visible)
</details>

Expression: Bruno Mars.

![](images/76c054a4f7cc325e90a97c70892a5a3c489168a469f8094c460f6daa430500be.jpg)

<details>
<summary>natural_image</summary>

Two musicians performing on electric guitar stands against a pink background (no text or symbols visible)
</details>

Expression: Blackpink Rose.

![](images/fd00305e58fbd482ba95a51cd37cff6f73459a7eb4d08523ecc5b84bd1d36467.jpg)

<details>
<summary>natural_image</summary>

Anime-style scene featuring a boy in a school uniform and a Pikachu character walking past a stone building (no text or symbols visible)
</details>

Original Image

![](images/e097072d0e4bb1e32afacbe370f906d2e8be8e5afff9fd3e0e45a5296549d4d5.jpg)

<details>
<summary>natural_image</summary>

Anime-style character walking with a Pikachu character in front of a building (no text or symbols visible)
</details>

Expression: an Electric-type Pokémon.

![](images/9de79990d074920b767df1e9c6325cd9838341a1daa1d1744af659ff60f16d73.jpg)

<details>
<summary>natural_image</summary>

Anime-style scene featuring a character of Pikachu standing beside a colorful Pikachu character in front of a brick building (no text or symbols visible)
</details>

Expression: a Pokémon Trainer.  
Figure 18. Qualitative results of real-world image segmentation. LLaVA-1.5-13B [35] uses only three attention heads (L15 H39, L16 H30, L7 H2) as localization heads to produce a precise segmentation masks related to the text expressions. The whitened regions in the images represent the segmentation mask output by the model.

![](images/8ec322328498baf813a72751bdf659be3b7b0d62bea43bb44f8c50978a379d5a.jpg)

<details>
<summary>natural_image</summary>

Wooden bowl containing fresh green fruits, accompanied by wooden chopsticks, placed on asphalt pavement (no text or symbols visible)
</details>

Original Image

![](images/00fb7269b0edfbdd67e88f9aed5a1b0e736247fad8faa19aa1029e84378159ff.jpg)

<details>
<summary>natural_image</summary>

Wooden bowl filled with fresh white round fruits, accompanied by wooden chopsticks, placed on asphalt pavement (no text or symbols visible)
</details>

Expression: apple inside a bowl.

![](images/72160aa680ab7ea5bf642f2ce432953409baaf36119ff4017f26efeeb6b40126.jpg)

<details>
<summary>natural_image</summary>

Wooden bowl containing fresh strawberries with chopsticks, placed on asphalt pavement (no text or symbols visible)
</details>

Prompt: strawberry

![](images/e6c43257bc8040ad763eca13dd71fa3e6fff342ac80289382cccaffee6de107d.jpg)

<details>
<summary>natural_image</summary>

Person roller skating in motion with green background and motion blur (no text or symbols visible)
</details>

Original Image

![](images/cfecca70b763f5bf9c37f409d8700500b55300ea6919bc13c17f1a8c76d86a4e.jpg)

<details>
<summary>natural_image</summary>

Person riding a roller skater in motion, with blurred greenery and motion blur background (no text or symbols visible)
</details>

Expression: guy skating.

![](images/24ca6e8ed7535fff6b09eedc9e72d4a169250f405c69d1278908fd787c0dc60e.jpg)

<details>
<summary>natural_image</summary>

Person in Spider-Man racing on a skateboard, motion blur background with greenery (no text or symbols visible)
</details>

Prompt: spider man  
Figure 19. Qualitative results of generating the desired image through integration with a diffusion model [43]. Given an original image, our method generates a mask from the LVLM based on the text describing the desired modifications. This mask is then used as guidance for a diffusion model to perform image editing. Using the segmentation mask obtained through the localization head of the frozen LVLM [35], it is possible to generate semantic objects that align with the prompt at the specified mask locations.