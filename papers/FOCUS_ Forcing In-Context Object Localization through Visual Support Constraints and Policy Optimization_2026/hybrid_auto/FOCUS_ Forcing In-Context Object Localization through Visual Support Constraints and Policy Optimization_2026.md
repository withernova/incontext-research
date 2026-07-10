# FOCUS: Forcing In-Context Object Localization through Visual Support Constraints and Policy Optimization

Mohammed Asad Karim <sup>\*</sup> <sup>1</sup> Vinay Kumar Verma <sup>\*</sup> <sup>1</sup>

## Abstract

In-context localization (ICL) seeks to localize a target object specified by a small set of support examples in a query image, operating on the fly without training or parameter updates. Despite rapid advances in vision–language models (VLMs), achieving category-agnostic and visually grounded ICL remains an open problem, even though it is essential for applications such as image editing, personalized visual search, and retrieval. Existing methods are fragile and rely on explicit category supervision, which not only limits applicability in realistic settings with unnamed or instance-specific objects but also introduces category bias that steers predictions toward semantic priors rather than visual evidence. We introduce a two-stage training framework that explicitly optimizes in-context attention between support bounding boxes and query images without category supervision. We further refine localization via reinforcement learning using Group Relative Policy Optimization (GRPO) to directly minimize localization error. This formulation enforces visual correspondence over semantic priors, yielding robust instance-level localization. Empirically, a 7B-parameter model trained with our objectives outperforms models up to 72B parameters, demonstrating that context-aware localization objectives can surpass scaling alone. Comprehensive ablations validate the contribution of each component.

## 1. Introduction

Vision–language models (VLMs) (Wang et al., 2024; Li et al., 2024; Dai et al., 2023a; Li et al., 2023) have achieved remarkable success across a broad spectrum of vision and language tasks, yet they continue to struggle with in-context object localization. In-Context Object Localization (ICOL) focuses on localizing a user-specified object in a query image by relying solely on a small set of visual support examples available at inference time. In contrast to traditional object detection or grounding approaches that depend on fixed category vocabularies and extensive supervised training, ICOL enables models to infer the target concept on the fly, without parameter updates, by reasoning over visual correspondences between support and query images. This capability is critical for practical applications such as customized image editing, personalized visual search, and interactive object tracking, where the object of interest is user-defined, instance-specific, and often difficult or impossible to describe textually in advance. Achieving reliable in-context localization is therefore a key step toward flexible, user-driven visual understanding systems.

Despite the success of in-context learning in large language models (LLMs) (Alayrac et al., 2022; Brown et al., 2020b; OpenAI, 2023; Raffel et al., 2020), transferring this paradigm to vision–language models (VLMs) for object localization remains challenging. Recent work on in-context object localization shows that VLMs (Singh et al., 2022) can use support examples with bounding box annotations to localize novel objects at inference time; however, their predictions are still strongly shaped by category-level priors rather than instance-specific visual reasoning (Doveh et al., 2025). To address this, Doveh et al. introduce pseudolabels during training to reduce reliance on true category names and encourage visual grounding. In practice, inference continues to rely on original category labels, creating a train–test mismatch that reintroduces semantic priors at deployment. As a result, category bias is only partially mitigated, and localization decisions can still be driven by semantic cues instead of the visual evidence provided by support examples. Moreover, empirical findings suggest that even with pseudo-label training, models frequently underutilize fine-grained spatial cues such as bounding box geometry and relative position defaulting to coarse visual similarity or residual category correlations. These observations reveal a central gap: existing approaches fail to eliminate categorymediated reasoning and do not enforce strict reliance on visual support constraints for instance-level localization.

To address these limitations, we propose a category-agnostic, attention-based formulation of in-context object localization that removes category names entirely from both support and query prompts. Instead of relying on true labels or pseudo-labels, our method optimizes in-context attention using only visual support examples, ensuring that localization decisions are driven by visual correspondence and spatial reasoning. By removing textual identifiers, the model is no longer influenced by semantic category priors and must infer the target object from visual appearance and geometry. This attention-based design promotes direct use of bounding box information, encouraging consistent focus on object shape, relative position, and surrounding visual cues across support and query images. To further improve query alignment, we refine bounding box prediction using GRPO-based reward optimization, which directly minimizes alignment error. As a result, the model generalizes to arbitrary object instances, including unseen categories and visually defined concepts without stable names. Overall, our approach reframes in-context localization as a visual reasoning task, enabling robust and generalizable instance-level grounding. We summarize our key contributions as follows:

• We propose a category-independent, pure visual context–based in-context localization framework that overcomes category-induced bias in VLMs.

• We introduce an attention map optimization that encourages the model to focus on the most relevant regions in both support and query images for robust localization. In addition, a GRPO-based reward objective is used to reduce object bounding-box alignment error.

• Through extensive experiments, we demonstrate that the proposed model (FOCUS) enables effective in-context localization without relying on category labels or prior semantic information.

## 2. Related Work

In-context learning in language models. In-context learning (ICL) (Doveh et al., 2025) enables large language models (LLMs) to perform new tasks by conditioning on a small set of demonstrations at inference time, without parameter updates. Early work showed that few-shot performance scales with model and context size in autoregressive models (Brown et al., 2020a). Subsequent studies interpret ICL as implicit Bayesian inference (Xie et al., 2022) or gradient-descent-like computation emerging from transformer attention dynamics (Von Oswald et al., 2023). Empirically, ICL is sensitive to prompt composition (Min et al., 2022; Lu et al., 2022), motivating calibration (Zhao et al., 2021) and retrieval-augmented methods (Rubin et al., 2022). Instruction-tuned models further improve zero-shot generalization (Wei et al., 2022).

In-context learning in vision–language models. Compared to language models, in-context learning for vision– language models (VLMs) remains relatively underexplored (Alayrac et al., 2022; Zhang et al., 2024; OpenAI, 2023). Recent multimodal models demonstrate in-context capabilities for tasks such as visual question answering, reasoning, and visual grounding when examples are provided in the prompt (Alayrac et al., 2022; Brown et al., 2020b; Dai et al., 2023b). However, these demonstrations primarily focus on semantic understanding and rely on natural language to specify the task and the target object (Liu et al., 2024; Liao et al., 2025). As a result, in-context behavior in VLMs has largely been studied through language-conditioned interactions rather than through purely visual conditioning (Radford et al., 2021; Huang et al., 2023). A recent work IPLoc (Doveh et al., 2025) explores the ICL with the help of pseudo-label and visual grounding, however pseudo label reduce the generalization ability since for the novel category model have not learned the pseudo label.

Semantic grounding and localization in VLMs. Most vision–language models (VLMs) for grounding and localization rely on explicit semantic supervision, such as object names, attributes, or referring expressions. Early work formulates grounding as localizing regions described by natural language queries (Kazemzadeh et al., 2014; Yu et al., 2016), later extended to end-to-end multimodal transformers that condition detection on text (Kamath et al., 2021). Recent large-scale pretraining unifies open-vocabulary detection and phrase grounding by aligning visual regions with linguistic descriptions (Li et al., 2021; Zhang et al., 2022), while CLIP-based methods adapt contrastively trained models for grounding tasks (Xiao et al., 2023). Despite strong performance, these approaches assume targets can be specified unambiguously through language. This assumption limits applicability in settings with unnamed objects, visually similar instances, or domain-specific entities without canonical labels, motivating methods that relax or adapt text-conditioned grounding architectures (Shi et al., 2023).

Few-shot and instance-level visual conditioning. Fewshot object localization (Chen et al., 2022) has been studied via episodic and meta-learning across detection, segmentation, and tracking tasks (Bertinetto et al., 2016; Shaban et al., 2017; Yan et al., 2019). Recent work extends these paradigms to foundation and vision–language models using stronger visual and multimodal features (Madan et al., 2024; Han & Lim, 2024). However, most approaches rely on supervised adaptation or architectural updates rather than inference-time conditioning, and thus do not exhibit true in-context behavior (Xu et al., 2023; Liu et al., 2023).

Pure visual in-context localization. We introduce a pure visual in-context localization setting in which a single frozen model localizes objects using only support images and bounding box annotations, without any semantic labels or textual cues. To our knowledge, this is the first systematic study of in-context localization driven solely by visual evidence. By eliminating linguistic priors, this formulation enables open-set generalization to novel object instances and enforces robust instance-level reasoning through visual correspondence alone.

![](images/5c3d5ebdfb52691456943c84c1bfc833601175b893b0a57ae2af2a0a86b4ec33.jpg)  
Figure 1. The figure illustrates in-context localization across different models by visualizing the support, query, predicted bounding boxes, and the corresponding attention maps. The support image provides a bounding box specifying the target object. Attention heatmaps highlight regions the model relies on for prediction, while red boxes indicate the final localized output.

![](images/b63cbed04835e6235f24ec217ed4b14950b3bde77ab2efa12bc40fe5f3ea892d.jpg)  
Figure 2. Comparison of attention from answer tokens to inpu tokens. Our model places greater attention on query image tokens compared to the SFT baseline, indicating stronger visual grounding during localization. Here w/c and wo/c shows the model with and without category information respectively.

## 3. Why LVMs Require Explicit Supervision?

We conduct an extensive empirical study to analyze failure cases of in-context localization models and design targeted objectives to address the identified limitations. Our key findings are summarized as follows:

Prior Bias/ Category Name Biasness We observe that language bias, particularly the use of category names, plays a decisive role in predicting the query bounding box. As illustrated in Fig. 1, IPLoc fails to localize the correct instance and instead attends to an incorrect bowl when multiple objects from the same category appear in the scene. This failure mode exposes a fundamental limitation of categorydriven localization. When several instances share the same semantic label, category supervision biases the model toward visually salient or prototypical instances rather than the specific instance defined by the in-context example. Fig. 2 further supports this finding by examining attention from the answer token to the input tokens. We observe that category tokens receive comparable or even higher attention than the relevant visual context, indicating reliance on semantic shortcuts instead of grounded visual reasoning.

Attention Distribution to the Visual Context We further analyze attention from the answer token to the input tokens, as shown in Fig. 2, which reflects each token’s contribution during prediction. IPLoc and the vanilla w/c baseline assign limited attention to query and BBOX tokens while allocating relatively higher attention to category tokens, explaining their observed failure cases. The reduced attention to support and BBOX tokens indicates weak visual grounding. We then examine whether removing category names from the vanilla model (vanilla wo/c) resolves this issue. Although Fig. 2 suggests improved attention allocation across query, support, and BBOX tokens, this improvement is superficial. A closer inspection of Fig. 1 for Qwen2-VL-7B reveals that, without category information, the model exhibits high aggregated attention over the query image; however, this attention is diffusely distributed and fails to concentrate on regions corresponding to the support examples. Consequently, the predicted bounding boxes remain weakly grounded in the visual context.

Motivated by this analysis, we introduce an attention-based loss and a GRPO-based reward to correct these failure modes, explicitly enforcing support-aware visual attention and improving bounding box alignment for reliable incontext localization.

## 4. Preliminary

## 4.1. Problem Definition and Notation

This work study in-context localization, where a model localizes a target object in a query image by conditioning on a set of visual demonstrations (support images) provided within the same prompt. Let a sequence of images be:

$$
\mathcal {I} = (I _ {1}, I _ {2}, \dots , I _ {T}),\tag{1}
$$

where $\forall I _ { t } \in \mathbb { R } ^ { H \times W \times 3 }$ and $( I _ { 1 } , I _ { 2 } , \ldots , I _ { T - 1 } )$ are the support images that contain the target object annotated by the bounding box. For the support images, the bounding boxes are given as:

$$
\mathcal {B} _ {1: T - 1} = \{b _ {1}, b _ {2}, \dots , b _ {T - 1} \},\tag{2}
$$

![](images/55ec9576e319fc6cb6b4888d1e9cd00fb146ea5ac8e688a4d681910575c651ee.jpg)  
Figure 3. The block diagram of the proposed approach model (FOCUS): The model accepts the support set with the BBOX and predicts the final BBOX over the query image. Attention loss is applied to the attention map from the query to the input token, and GRPO helps generate a precise BBOX.

where each bounding box $\left( \boldsymbol { b } _ { t } \right)$ is parameterized as $b _ { t } \ =$ $[ x _ { \mathrm { m i n } } ^ { ( t ) } , y _ { \mathrm { m i n } } ^ { ( t ) } , x _ { \mathrm { m a x } } ^ { ( t ) } , y _ { \mathrm { m a x } } ^ { ( \overline { { t } } ) } ]$ . Given this context, the objective is to predict the bounding box $b _ { T }$ corresponding to the same object instance in the final query image $I _ { T }$ .

Let us assume that we have a multimodal autoregressive model $\mathbf { f } _ { \theta } ,$ where θ is the model parameters. The model accepts the support image data and the bounding boxes along with the query sample as input and predicts the query object output as BBOX, which is defined as:

$$
\hat {b} _ {T} = \mathbf {f} _ {\theta} (I _ {T} / (I _ {1}, I _ {2}, \dots , I _ {T - 1}), \mathcal {B} _ {1: T - 1})\tag{3}
$$

where $\hat { b } _ { T }$ is the predicted bounding box from the query image.

The model jointly encodes visual tokens extracted from images and textual tokens from the instruction prompt, enabling cross-modal reasoning over spatial relationships. Localization is performed by matching regions in the query image with the target object defined through bounding box demonstrations in the context. This formulation does not rely on temporal continuity, motion cues, or persistent object states. Each prediction is made independently based on incontext examples, framing localization as a demonstrationconditioned visual reasoning task.

## 5. Methodology

As outlined in Section 4, each training instance comprises multiple support images annotated with BBOXes, followed by a query image for which the model generates a BBOX prediction in text form. The proposed training framework consists of two stages. In the first stage, we optimize a category-agnostic, attention-based BBOX grounding objective using only visual context. This objective explicitly encourages attention concentration on relevant visual regions, while suppressing attention to irrelevant areas and categoryinduced biases. In the second stage, we refine BBOX alignment through reinforcement learning using Group Relative Policy Optimization (GRPO), guided by an IoU-based reward. The following section presents a detailed description of the proposed approach.

## 5.1. Prompt Specification

All experiments use a fixed natural language prompt that defines the in-context localization task and specifies the expected output format. The prompt is prepended once to each input sequence, followed by interleaved images and their corresponding BBOX annotations. The exact prompt text used in all experiments is provided below:

```txt
Prompt: Locate the same object across the sequence of frames shown below. Your goal is to identify the target object consistently using the visual context provided.
```

<div class="mineru-algorithm" style="white-space: pre-wrap; font-family:monospace;">
For the first $T-1$ frames, the bounding box of the object is already provided. Use this information and the visual context to predict where the same object appears in the final frame.
</div>

Output the predicted bounding box for the last frame in the following format:

$$
\langle \text {answer} \rangle [ x _ {\min}, y _ {\min}, x _ {\max}, y _ {\max} ] \langle / \text {answer} \rangle
$$

Following the task description, each image in the sequence is paired with a corresponding BBOX annotation. For frames 1 through T − 1, the input explicitly provides the bounding box of the target object associated with each image. For the final frame T, no bounding box is given, and the model is instructed to predict the corresponding BBOX for the query image.

![](images/1dfdeae323dd85974d4b7c02faea1e5154a427c620ea243c97087297dc9189ce.jpg)  
Figure 4. BBOX Attention Optimization: The mask for the BBOX token are given as 1 and remaining are 0 which is used to compute the average attention for the BBOX and non-BBOX token using the Eq-7.

Formally, the complete input to the model is constructed as an interleaved sequence:

$$
\mathcal {C} = \langle \text {prompt}, (I _ {1}, b _ {1}), \dots , (I _ {T - 1}, b _ {T - 1}), (I _ {T}) \rangle\tag{4}
$$

Note that Eq. 4 contains no category information; only visual inputs are provided to the model. The task is framed as in-context localization, where the target object is specified exclusively through BBOX demonstrations contained within the prompt.

## 5.2. Bounding Box Attention Optimization

In the LVM failure analysis (Section 3), we observe that existing models exhibit weak attention to the visual context of both support and query images, failing to sufficiently emphasize the regions critical for accurate localization. As a result, predictions are often dominated by prior semantic knowledge rather than instance-specific visual evidence, leading to incorrect localization and persistent category bias. To address this limitation, we explicitly optimize the model’s latent attention maps to concentrate on the key spatial regions corresponding to the annotated support objects and the query image.

Let $\boldsymbol { x } = ( x _ { 1 } , \dots , x _ { T } )$ denote the input token sequence obtained from Eq. 4, consisting of the prompt and interleaved vision and text tokens from both the support set and the query example. The model $\mathbf { f } _ { \theta }$ consists of a set of transformer layers. For each transformer layer $\ell \in \{ 1 , \ldots , L \}$ and attention head $h \in \{ 1 , \ldots , H \}$ , the model produces an attention matrix $A ^ { ( \ell , h ) } \stackrel { \textstyle \setminus } { \in } \mathbb { R } ^ { T \times T }$ . We aggregate attentions across the layers and heads by averaging:

$$
A = \frac {1}{L H} \sum_ {\ell = 1} ^ {L} \sum_ {h = 1} ^ {H} A ^ {(\ell , h)}.\tag{5}
$$

Let $\mathcal { T } _ { \mathrm { q u e r y } } \subset \{ 1 , . . . , T \}$ denote the index set of tokens corresponding to the query image. We extract the rows of $A$ indexed by $\mathcal { T } _ { \mathrm { q u e r y } }$ , yielding

$$
P \in \mathbb {R} ^ {N \times T}\tag{6}
$$

where $N = | \mathcal { T } _ { \mathrm { q u e r y } } |$ is the number of query image tokens. Each row $P _ { i }$ represents the attention distribution from query image token i to all input tokens.

Bounding Box Token Mask During supervised finetuning, BBOX annotations for the support images are explicitly provided in the prompt as structured text (e.g., $[ x _ { m i n } , y _ { m i n } , x _ { m a x } , y _ { m a x } ] )$ . Since these annotations are serialized into text tokens by the tokenizer, the corresponding token indices are deterministically known. Based on this, we construct a binary mask $m \in \{ 0 , 1 \} ^ { T }$ , where $m _ { j } = 1$ if token $j$ corresponds to a BBOX annotation token from the support examples, and $m _ { j } = 0$ otherwise. A schematic illustration of the token mask and the associated loss computation is shown in Fig. 4.

Equation 6 denotes the attention map from query image tokens to all input prompt tokens. We then compute the average attention mass assigned to BBOX tokens and to non-bounding box tokens:

$$
p _ {i} ^ {+} = \frac {\sum_ {j} P _ {i j} m _ {j}}{\sum_ {j} m _ {j}}, \quad p _ {i} ^ {-} = \frac {\sum_ {j} P _ {i j} (1 - m _ {j})}{\sum_ {j} (1 - m _ {j})}.\tag{7}
$$

The attention preference margin for query image token i is defined as: − p+ (8)

$$
\Delta_ {i} = p _ {i} ^ {+} - p _ {i} ^ {-}\tag{8}
$$

The loss for the margin $\Delta _ { i }$ <sub>i</sub> is formulated to encourage query image tokens to preferentially attend to BBOX annotation tokens by minimizing a margin-based hinge loss.

$$
\mathcal {L} _ {\mathrm{bbox}} = \frac {1}{N} \sum_ {i = 1} ^ {N} \max (0, \mu - \Delta_ {i}) ^ {2},\tag{9}
$$

where $\mu > 0$ is a hyperparameter. This loss enforces a relative preference for bounding box tokens over unrelated context, without constraining absolute attention magnitudes.

## 5.3. Supervised Fine-Tuning Objective

Let $\mathcal { L } _ { \mathrm { L M } }$ denote the standard language modeling loss. Incorporating the BBOX attention optimization the supervised fine-tuning objective is defined as:

$$
\mathcal {L} _ {\mathrm{SFT}} = \mathcal {L} _ {\mathrm{LM}} + \beta \mathcal {L} _ {\mathrm{bbox}},\tag{10}
$$

where $\beta ,$ controls the strength of bounding box attention supervision which is optimized using the grid search over the validation data. This objective biases the model to ground its internal representations in spatial annotations provided by the support examples. Instead of training the model parameter θ we add the LoRA (Hu et al., 2021) weight ϕ and we only train the LoRA parameters.

While BBOX Attention Optimization emphasizes key regions in support and query images, it does not guarantee specific format and precise bounding box alignment. To address this limitation, we further optimize the model using Group Relative Policy Optimization (GRPO), encouraging accurate query bounding box prediction $b _ { \mathrm { p r e d } }$ . The reward consists of two components: (i) an IoU-based reward computed against the query ground truth, and (ii) a formatting reward that enforces syntactic validity of the predicted bounding box.

## 5.4. Reinforcement Learning with GRPO

Group Relative Policy Optimization (GRPO) is a reinforcement learning method that updates policies using relative comparisons among multiple sampled responses, rather than a learned critic. In contrast to PPO (Schulman et al., 2017), GRPO (Shao et al., 2024; DeepSeek-AI, 2024) may relies on rule-based rewards and therefore avoids value function estimation. Given a query q, GRPO samples G candidate outputs

$$
\{o _ {1}, o _ {2}, \dots , o _ {G} \} \sim \pi_ {\theta_ {\mathrm{old}}} (\cdot \mid q),
$$

each of which is assigned a scalar reward, producing

$$
\{r _ {1}, r _ {2}, \dots , r _ {G} \}.
$$

The policy parameters θ are optimized by maximizing

$$
\begin{array}{l} \mathcal {J} _ {\mathrm{GRPO}} (\theta) = \mathbb {E} \Bigg [ \frac {1}{G} \sum_ {i = 1} ^ {G} \min \left(\frac {\pi_ {\theta} (o _ {i} \mid q)}{\pi_ {\theta_ {\mathrm{old}}} (o _ {i} \mid q)} A _ {i}, \right. \\ \left. \quad \operatorname{clip} \left(\frac {\pi_ {\theta} (o _ {i} \mid q)}{\pi_ {\theta_ {\mathrm{old}}} (o _ {i} \mid q)}, 1 - \epsilon , 1 + \epsilon\right) A _ {i}\right) \Bigg ] \\ \quad - \beta \mathcal {D} _ {\mathrm{KL}} (\pi_ {\theta} \parallel \pi_ {\mathrm{ref}}) \end{array}\tag{11}
$$

where ϵ controls the clipping range and $\beta$ weights KL regularization against a fixed reference policy $\pi _ { \mathrm { r e f } } .$ . Advantages $A _ { i }$ are computed within each group using normalized rewards:

$$
A _ {i} = \frac {r _ {i} - \mathrm{mean} (\{r _ {1} , \ldots , r _ {G} \})}{\mathrm{std} (\{r _ {1} , \ldots , r _ {G} \})}.
$$

This relative formulation promotes higher-quality responses within each sampled group and provides a stable alternative to critic-based optimization.

Query IoU reward. To ensure accurate localization with respect to the full query object, we additionally include the standard IoU between the predicted box and the query ground truth:

$$
r _ {\mathrm{iou}} = \mathrm{IoU} (b _ {\mathrm{pred}}, b _ {\mathrm{qry}}).\tag{12}
$$

Formatting reward. Because bounding boxes are generated as text, we include a formatting reward $r _ { \mathrm { f m t } }$ that encourages syntactically valid predictions. A prediction is considered valid if it follows the required structure

$$
\langle \text {answer} \rangle [ x _ {\min}, y _ {\min}, x _ {\max}, y _ {\max} ] \langle / \text {answer} \rangle .
$$

The formatting reward is defined as

$$
r _ {\mathrm{fmt}} (\hat {y}) = \left\{ \begin{array}{l l} 0. 5, & \text {if} \hat {y} \text {matches the specified format,} \\ 0, & \text {otherwise.} \end{array} \right.
$$

Combined reward. The final reward (R) used for GRPO is a weighted sum of the two above rewards:

$$
\mathcal {R} = r _ {\mathrm{iou}} + r _ {\mathrm{fmt}},\tag{13}
$$

The reward R are optimized w.r.t. the LoRA parameters ϕ. GRPO updates the policy by contrasting each trajectory’s reward against a group-wise baseline computed over sampled trajectories, yielding low-variance gradients and stable optimization in the few-shot localization setting. GRPO assigns a higher advantage to predicted BBOXes that outperform the average reward, which strongly encourages the model to concentrate on the most accurate alignment during in-context few-shot training scenarios

## 6. Results and Discussions

The following section evaluates the proposed model across various datasets and compares its results with recent stateof-the-art baselines. Further, we investigate the proposed components and present the results in the ablations.

## 7. Dataset Details

We evaluate FOCUS for the in-context localization on a diverse collection of video and image benchmarks, including LaSOT (Fan et al., 2019), GOT-10k (Huang et al., 2019), TAO (Dave et al., 2020), PerSeg (Zhang et al., 2023), and PerMIRS (Samuel et al., 2024), which together span a wide range of object diversity, scene complexity, and generalization regimes. All datasets provide frame-level spatial annotations that we use to construct prompt-based in-context localization tasks, where the target object is specified implicitly via bounding-box demonstrations rather than semantic labels or explicit identity cues.

LaSOT is a large-scale object video benchmark comprising long sequences with dense, high-quality bounding-box annotations across 85 object categories. The extended temporal duration of LaSOT videos introduces substantial appearance variation due to viewpoint changes, occlusions, and scale shifts, making it well-suited for evaluating localization robustness over time. GOT-10k emphasizes category-level generalization by enforcing a strict train–test split with zero overlap in object classes. As a result, models must localize objects from previously unseen categories at test time, which directly aligns with our in-context formulation, where object identity must be inferred solely from contextual visual and spatial cues. Both LaSOT and GOT-10k provide bounding box annotations for a single target object per sequence.

Table 1. In-Context Few-shot localization performance (%) across multiple benchmark datasets and model variants.

<table><tr><td rowspan="2">Model</td><td colspan="3">TAO</td><td colspan="3">GOT</td><td colspan="3">ICL-LASOT</td><td rowspan="2">Avg.</td></tr><tr><td>1-shot</td><td>2-shot</td><td>4-shot</td><td>1-shot</td><td>2-shot</td><td>4-shot</td><td>1-shot</td><td>2-shot</td><td>4-shot</td></tr><tr><td>Idefics3</td><td>6.8</td><td>15.0</td><td>25.5</td><td>9.3</td><td>21.2</td><td>32.3</td><td>3.6</td><td>8.7</td><td>14.7</td><td>15.2</td></tr><tr><td>Pixtral-12B</td><td>8.2</td><td>22.7</td><td>16.8</td><td>13.9</td><td>19.4</td><td>23.7</td><td>4.6</td><td>7.6</td><td>22.4</td><td>15.5</td></tr><tr><td>LLaVA-OV</td><td>22.5</td><td>29.5</td><td>33.5</td><td>18.6</td><td>26.4</td><td>33.7</td><td>10.8</td><td>14.1</td><td>17.7</td><td>23.0</td></tr><tr><td>Qwen2-VL-7B</td><td>26.0</td><td>31.6</td><td>36.1</td><td>36.2</td><td>37.0</td><td>39.3</td><td>26.2</td><td>22.3</td><td>25.0</td><td>31.1</td></tr><tr><td>IPLoc (7B)</td><td>51.7</td><td>54.3</td><td>56.1</td><td>64.2</td><td>68.1</td><td>68.7</td><td>49.7</td><td>57.1</td><td>59.4</td><td>58.8</td></tr><tr><td>Qwen2-VL-72B</td><td>46.2</td><td>52.8</td><td>55.6</td><td>62.7</td><td>60.1</td><td>59.9</td><td>51.9</td><td>50.7</td><td>55.4</td><td>55.0</td></tr><tr><td>InternVL2-76B</td><td>50.4</td><td>55.2</td><td>57.5</td><td>65.8</td><td>66.7</td><td>65.4</td><td>44.2</td><td>47.3</td><td>52.5</td><td>56.1</td></tr><tr><td>FOCUS (Ours)</td><td>55.8</td><td>63.0</td><td>68.5</td><td>77.1</td><td>80.6</td><td>82.6</td><td>56.1</td><td>59.9</td><td>65.6</td><td>67.7</td></tr></table>

TAO represents a more challenging, open-world setting, with high-resolution videos containing multiple annotated objects per frame and a large, diverse vocabulary of object categories. Unlike LaSOT and GOT-10k, TAO includes multiple object instances within the same scene, often under significant clutter and occlusion. To construct a consistent in-context localization benchmark, we select the most frequently occurring object track within each video sequence as the target instance and treat the remaining objects as distractors. This setting evaluates a model’s ability to resolve object identity from context alone in the presence of competing visual signals.

For all video datasets, we construct a fixed-shot in-context setting by uniformly sampling a set of support frames from each sequence. The first support frame is selected from the beginning of the video, the last from the end, and the remaining frames are sampled at equal temporal intervals in between. This strategy ensures that the in-context examples span the full temporal extent of the video and capture meaningful appearance variation of the target object. The final frame is used as the query, for which the model must predict the target object’s bounding box.

To further assess generalization beyond natural video benchmarks, we also evaluate on PerSeg and PerMIRS, which provide segmentation annotations that we convert to bounding boxes. PerSeg is a synthetic dataset containing a single object per image and serves as a controlled setting for evaluating basic in-context localization behavior. In contrast,

Table 2. In context localization results on domain shift datasets

<table><tr><td rowspan="2">Model</td><td colspan="2">PerMIRS</td><td colspan="3">PerSeg</td><td rowspan="2">Avg.</td></tr><tr><td>1-shot</td><td>2-shot</td><td>1-shot</td><td>2-shot</td><td>4-shot</td></tr><tr><td>Qwen2-VL-7B</td><td>24.5</td><td>50.2</td><td>64.0</td><td>65.7</td><td>63.4</td><td>53.6</td></tr><tr><td>IPLoc (7B)</td><td>41.2</td><td>53.3</td><td>84.1</td><td>83.1</td><td>79.4</td><td>68.2</td></tr><tr><td>Qwen2-VL-72B</td><td>43.9</td><td>54.3</td><td>91.5</td><td>92.6</td><td>95.8</td><td>75.6</td></tr><tr><td>FOCUS (Ours)</td><td>53.8</td><td>72.8</td><td>95.5</td><td>96.6</td><td>97.5</td><td>83.2</td></tr></table>

PerMIRS contains scenes with multiple objects, often including several instances from the same category, increasing ambiguity and requiring finer-grained instance-level reasoning. Together, these datasets span a wide spectrum of visual complexity, ranging from PerSeg, the simplest scenario, to TAO, the most challenging setting, with an average of 4.1 objects per image.

Overall, this collection of datasets enables a comprehensive evaluation of in-context localization across controlled, category-generalization, and open-world scenarios.

## 7.1. Implementation Details

We fine-tune our models using LoRA; the details of the LoRA configuration are provided in the appendix. All experiments are run using the DeepSpeed distributed library for efficient distributed training. For our main results, we use Qwen2-VL-7B as the base model and fine-tune all models under a four-shot setting. We find that models fine-tuned under this setting generalize reasonably well to other shot configurations, and we therefore adopt the four-shot setting for all our experiments. We conducted all the inference (1-shot, 2-shot, 4-shot) using the same four-shot training model, demonstrating the model’s generalization. We tuned the model’s hyperparameters using a validation set. The Additional details about the model hyperparameters and other experimental details are provided in the appendix.

## 7.2. Attention Heatmap Upsampling and Visualization

To visualize attention distributions over the input image, we convert the model’s 1D attention vector into a spatial heatmap aligned with the image’s resolution. Given a 1D attention tensor of length N, we first infer its underlying 2D grid resolution $( H _ { \mathrm { g r i d } } , W _ { \mathrm { g r i d } } )$ based on the target image dimensions (H, W). The attention vector is then reshaped into a 2D map of size $H _ { \mathrm { g r i d } } \times W _ { \mathrm { g r i d } }$ . To obtain a dense attention heatmap at the image resolution, we upsample this grid using bilinear interpolation to size $H \times W$ , ensuring spatial alignment with the original image. This upsampled heatmap is subsequently normalized and overlaid on the image for visualization and analysis.

![](images/8ad92628e38588c299f67342d5b7fe57601a0220d64247f32047c908de60c91f.jpg)  
Figure 5. We share attention-based localization heatmaps across models and compare Qwen2-VL-7B under different training regimes. The vanilla model fails to localize the person riding the camel, while fine-tuning improves localization but remains incomplete. In contrast, our attention-based loss improves visual grounding and accurately localizes the target, with further gains from reinforcement learning.

## 7.3. Evaluation Metrics

Similar to the IPLoc (Doveh et al., 2025) we use mIoU as the primary evaluation metric, reporting the IoU on the query image for the test set. We evaluate our model under different in-context few-shot settings. To demonstrate robustness across datasets, we fine-tune on multiple datasets and report performance on their respective test sets. In addition, we evaluate generalization by reporting performance on datasets outside the training distribution.

## 7.4. Results

We evaluate in-context localization performance across multiple datasets and compare our method against strong vision–language baselines, including Idefics3 (Laurenc¸on et al., 2023), Pixtral-12B (Agrawal et al., 2024), LLaVA-OV (Li et al., 2024), Qwen2-VL-72B (Wang et al., 2024), InternVL2-76B (Chen et al., 2024), and IPLoc (). Results are reported on TAO (Dave et al., 2020), GOT (Huang et al., 2019), ICL-LaSOT (Fan et al., 2019), PerSeg (Zhang et al., 2023), and PerMIRS (Samuel et al., 2024) datasets. For each dataset, model hyperparameters are tuned using 10% of the training samples. On these datasets, the proposed model is evaluated under the following scenarios:

In-Context Localization Generalization Capabilities: To assess generalization beyond the training distribution, we evaluate FOCUS on two held-out datasets, PerMIRS and PerSeg. PerMIRS contains videos with multiple instances from the same semantic category, while PerSeg is a synthetic dataset generated using a diffusion model. We report mean IoU (mIoU) across shot settings. The model is trained on the joint TAO, GOT, and ICL-LaSOT data under the four-shot setting and evaluated on PerMIRS and PerSeg. The results are reported in Table 2.

PerSeg is a synthetic dataset with relatively simple scenes containing a single object per sample. Nevertheless, IPLoc (Doveh et al., 2025) underperforms on this benchmark, as shown in Table 2. The performance gap widens further on PerMIRS, where each sample contains multiple instances from the same semantic category. In this setting, IPLoc struggles to correctly disambiguate the target instance, highlighting a limitation of category-conditioned localization in the presence of instance ambiguity. In contrast, FOCUS maintains strong performance by relying exclusively on visual context from in-context support images rather than semantic category names. As summarized in Table 2, FOCUS achieves absolute improvements of 19.1% on PerMIRS and 13.5% on PerSeg over IPLoc in the 2-shot setting.

In Context Localization on Seen/Unseen Classes: We have evaluated the model on the TAO dataset, and the results are shown in Table 1. TAO is highly challenging, contains the open word category, and each image contains multiple objects. For the multi-object scenario, where other models suffer, FOCUS outperforms recent baselines by a significant margin. Further, to evaluate generalization to unseen classes, we report results on the ICL-LaSOT and GOT datasets. La-SOT contains 70 object categories; we train on 35 categories and evaluate on the remaining 35 unseen categories. Similarly, GOT enforces a strict category-disjoint split between training and testing. Results are summarized in Table 1. We observe that FOCUS generalizes substantially better to unseen classes than IPLoc, achieving absolute gains of 13.9% on GOT and 6.2% on ICL-LaSOT in the four-shot setting. These results indicate that FOCUS learns categoryagnostic visual grounding from in-context examples rather than relying on category-specific cues.

Table 3. Ablations over the various components of the TAO Dataset

<table><tr><td>Model</td><td>1-shot</td><td>2-shot</td><td>4-shot</td></tr><tr><td>Qwen2-VL-7B</td><td>26.0</td><td>31.6</td><td>36.1</td></tr><tr><td>Qwen2-VL-7B (sft)</td><td>22.1</td><td>28.9</td><td>34.3</td></tr><tr><td>Qwen2-VL-7B (grpo)</td><td>19.4</td><td>26.4</td><td>32.1</td></tr><tr><td>Qwen2-VL-7B (grpo+sft)</td><td>24.3</td><td>27.2</td><td>33.7</td></tr><tr><td>Qwen2-VL-7B (sft + attn loss) (ours)</td><td>51.7</td><td>54.0</td><td>57.1</td></tr><tr><td>Qwen2-VL-7B (sft + attn loss + grpo) (Ours)</td><td>55.8</td><td>63.0</td><td>68.5</td></tr></table>

## 8. Ablations

We conduct extensive ablation studies to analyze the contributions of individual components in the proposed model. Specifically, we examine the attention distribution of answer tokens across different groups of input tokens, including query image tokens, support image tokens, and bounding box annotation tokens. We find the TAO dataset to be most suitable for these ablations, as it features open-vocabulary categories and multiple objects per frame. Compared to a na¨ıve SFT baseline, our model assigns substantially higher attention to query image tokens while reducing reliance on bounding box annotation tokens. Although our training objective explicitly encourages query image tokens to attend to bounding box annotations, this behavior reflects representation learning induced by the attention loss rather than a failure of the objective. Quantitatively, as shown in Table 3, incorporating the attention loss alongside SFT yields significant performance gains. Further refining bounding box prediction using the GRPO loss improves boundary alignment, resulting in an additional 11.4% gain in the 4-shot setting over SFT with attention loss. Qualitative results in Fig. 5 further demonstrate that attention loss improves focus on relevant regions, while the combination of attention loss and GRPO enables accurate bounding box prediction in multi-object scenarios.

## FOCUS with a different base model

We evaluate the generality of our approach on an additional architecture, LLaVA-OV, using the TAO dataset. The results are shown in Table 4. FOCUS consistently improves over the LLaVA-OV baseline across all shot settings, increasing performance from 22.5 to 52.2 in the 1-shot setting, 29.5 to 59.7 in the 2-shot setting, and 33.5 to 65.7 in the 4-shot setting. These results show that our method is not limited to a single base VLM and can provide consistent gains across different architectures.

## Performance Across Different Layers of Attention

We ablate the effect of applying the attention loss at different layer groups: the first five layers, the last five layers, and the mean attention across all layers. We evaluate Qwen2 VL 7B on TAO in the 4-shot setting, as shown in Table 5. Applying the attention loss to the first five layers achieves the best performance, with a score of 62.8, compared to 42.12 for the last five layers and 57.1 for all layers. This suggests that early-layer attention is more effective for grounding the model in the relevant visual region, while later layers primarily refine semantic features after the attended region has already been identified. This finding is interesting and could be a potential direction for future exploration. We conducted this study for completeness.

Table 4. Performance comparison with LLaVA-OV architecture on the TAO dataset: FOCUS shows consistently better results for the 1, 2, and 4-shot settings.

<table><tr><td>Model</td><td>1-shot</td><td>2-shot</td><td>4-shot</td></tr><tr><td>LLaVA-OV</td><td>22.5</td><td>29.5</td><td>33.5</td></tr><tr><td>FOCUS (on LLaVA-OV)</td><td>52.2</td><td>59.7</td><td>65.7</td></tr></table>

Table 5. Ablation on attention loss placement across layers on the TAO dataset in the 4-shot setting.

<table><tr><td>Model</td><td>First 5</td><td>Last 5</td><td>All</td></tr><tr><td>Qwen2-VL-7B (sft + attn loss)</td><td>62.8</td><td>42.12</td><td>57.1</td></tr></table>

## 9. Memory Analysis with Attention Loss

During training, attention loss introduces a small memory overhead because attention maps must be retained for supervision. In our setting, SFT without attention loss requires 57.2 GB of VRAM, while adding the attention loss requires 64.1 GB. This corresponds to approximately 12% additional VRAM with a reasonable training batch size.

Importantly, this overhead is only incurred during training. At inference time, the attention loss is not used, so both memory usage and FLOPs remain the same as the base SFT model. Thus, our method improves grounding performance without adding any inference time computational cost.

## 10. Conclusions

In this work, we investigated in-context object localization under a category-agnostic, purely visual conditioning setting and identified key limitations of existing vision–language models, including reliance on semantic priors and weak spatial grounding. To address these issues, we proposed FOCUS, a two-stage framework that optimizes in-context attention over support bounding boxes and refines localization using Group Relative Policy Optimization. By enforcing reliance on visual correspondence rather than category supervision, our approach achieves robust instance-level localization. Extensive experiments demonstrate consistent improvements over strong baselines, including models an order of magnitude larger, highlighting the importance of context-aware localization objectives over model scale.

## Impact Statement

This work advances in-context visual understanding and may positively impact applications such as image editing, accessibility tools, and visual search. We expect its broader societal effects to align with established, beneficial uses of vision–language models, without introducing new ethical concerns.

## References

Agrawal, P., Antoniak, S., Hanna, E. B., Bout, B., Chaplot, D., Chudnovsky, J., Costa, D., De Monicault, B., Garg, S., Gervet, T., et al. Pixtral 12b. arXiv preprint arXiv:2410.07073, 2024.

Alayrac, J.-B., Donahue, J., Luc, P., Miech, A., Barr, I., Hasson, Y., Lenc, K., Mensch, A., Millican, K., Reynolds, M., Ring, R., Rutherford, E., Cabi, S., Han, T., Gong, Z., Samangooei, S., Monteiro, M., Menick, J., Borgeaud, S., Brock, A., Nematzadeh, A., Sharifzadeh, S., Binkowski, M., Barreira, R., Vinyals, O., Zisserman, A., and Simonyan, K. Flamingo: a Visual Language Model for Few-Shot Learning. In NeurIPS, 2022.

Bertinetto, L., Valmadre, J., Henriques, J. F., Vedaldi, A., and Torr, P. H. S. Learning feed-forward oneshot learners. In Advances in Neural Information Processing Systems, volume 29, 2016. URL https: //proceedings.neurips.cc/paper/2016/hash/ 90e1357833654983612fb05e3ec9148c-Abstract. html.

Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A., Agarwal, S., Herbert-Voss, A., Krueger, G., Henighan, T., Child, R., Ramesh, A., Ziegler, D., Wu, J., Winter, C., Hesse, C., Chen, M., Sigler, E., Litwin, M., Gray, S., Chess, B., Clark, J., Berner, C., McCandlish, S., Radford, A., Sutskever, I., and Amodei, D. Language models are few-shot learners. In Advances in Neural Information Processing Systems, volume 33, 2020a.

Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A., Agarwal, S., Herbert-Voss, A., Krueger, G., Henighan, T., Child, R., Ramesh, A., Ziegler, D. M., Wu, J., Winter, C., Hesse, C., Chen, M., Sigler, E., Litwin, M., Gray, S., Chess, B., Clark, J., Berner, C., McCandlish, S., Radford, A., Sutskever, I., and Amodei, D. Language Models are Few-Shot Learners. In NeurIPS, 2020b.

Chen, M., Du, J., Pasunuru, R., Mihaylov, T., Iyer, S., Stoyanov, V., and Kozareva, Z. Improving In-Context Few-Shot Learning via Self-Supervised Training. In Proc. NAACL, 2022.

Chen, Z., Wang, W., Tian, H., Ye, S., Gao, Z., Cui, E., Tong, W., Hu, K., Luo, J., Ma, Z., et al. How far are we to gpt-4v? closing the gap to commercial multimodal models with open-source suites. arXiv preprint arXiv:2404.16821, 2024.

Dai, W., Li, J., Li, D., Tiong, A., Zhao, J., Wang, W., Li, B., Fung, P., and Hoi, S. InstructBLIP: Towards General-purpose Vision-Language Models with Instruction Tuning. In NeurIPS, 2023a.

Dai, W., Li, J., Li, D., Tiong, A., Zhao, J., Wang, W., Li, B., Fung, P. N., and Hoi, S. Instructblip: Towards general-purpose visionlanguage models with instruction tuning. Advances in neural information processing systems, 36:49250–49267, 2023b.

Dave, A., Khurana, T., Tokmakov, P., Schmid, C., and Ramanan, D. Tao: A large-scale benchmark for tracking any object. In Computer Vision–ECCV 2020: 16th European Conference, Glasgow, UK, August 23–28, 2020, Proceedings, Part V 16, pp. 436–454. Springer, 2020.

DeepSeek-AI. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv preprint arXiv:2401.06066, 2024.

Doveh, S., Shabtay, N., Schwartz, E., Kuehne, H., Giryes, R., Feris, R., Karlinsky, L., Glass, J., Arbelle, A., Ullman, S., et al. Teaching vlms to localize specific objects from in-context examples. In Proceedings ofthe IEEE/CVF International Conference on Computer Vision, pp. 9572–9582, 2025.

Fan, H., Lin, L., Yang, F., Chu, P., Deng, G., Yu, S., Bai, H., Xu, Y., Liao, C., and Ling, H. Lasot: A high-quality benchmark for large-scale single object tracking. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 5374–5383, 2019.

Han, G. and Lim, S.-N. Few-shot object detection with foundation models. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pp. 28608–28618, 2024. URL https: //openaccess.thecvf.com/content/CVPR2024/ html/Han\_Few-Shot\_Object\_Detection\_with\_ Foundation\_Models\_CVPR\_2024\_paper.html.

Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., and Chen, W. Lora: Low-rank adaptation of large language models. arXiv preprint arXiv:2106.09685, 2021.

Huang, L., Zhao, X., and Huang, K. Got-10k: A large highdiversity benchmark for generic object tracking in the wild. IEEE transactions on pattern analysis and machine intelligence, 43(5):1562–1577, 2019.

Huang, S., Dong, L., Wang, W., Hao, Y., Singhal, S., Ma, S., Lv, T., Cui, L., Mohammed, O. K., Patra, B., et al. Language is not all you need: Aligning perception with language models. Advances in Neural Information Processing Systems, 36:72096–72109, 2023.

Kamath, A., Singh, M., LeCun, Y., Synnaeve, G., Misra, I., and Carion, N. Mdetr: Modulated detection for end-to-end multimodal understanding. arXiv preprint arXiv:2104.12763, 2021. URL https://arxiv.org/abs/2104.12763.

Kazemzadeh, S., Ordonez, V., Matten, M., and Berg, T. L. Referitgame: Referring to objects in photographs of natural scenes. In Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2014. URL https://aclanthology.org/D14-1086/.

Laurenc¸on, H., Saulnier, L., Tronchon, L., Bekman, S., Singh, A., Lozhkov, A., Wang, T., Karamcheti, S., Rush, A. M., Kiela, D., Cord, M., and Sanh, V. Obelics: An open web-scale filtered dataset of interleaved image-text documents, 2023.

Li, B., Zhang, Y., Guo, D., Zhang, R., Li, F., Zhang, H., Zhang, K., Li, Y., Liu, Z., and Li, C. LLaVA-OneVision: Easy Visual Task Transfer. arXiv preprint arXiv:2408.03326, 2024.

Li, J., Li, D., Savarese, S., and Hoi, S. BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models. In Proc. ICML, 2023.

Li, L. H., Zhang, P., Zhang, H., Yang, J., Li, C., Zhong, Y., Wang, L., Yuan, L., Chang, K.-W., and Gao, J. Grounded languageimage pre-training. arXiv preprint arXiv:2112.03857, 2021. URL https://arxiv.org/abs/2112.03857.

Liao, Y.-H., Mahmood, R., Fidler, S., and Acuna, D. Can large vision-language models correct semantic grounding errors by themselves? In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pp. 14667– 14678, June 2025.

Liu, S., Zeng, Z., Ren, T., Li, F., Zhang, H., Yang, J., Jiang, Q., Li, C., Yang, J., Su, H., et al. Grounding dino: Marrying dino with grounded pre-training for open-set object detection. In European conference on computer vision, pp. 38–55. Springer, 2024.

Liu, Y., Zhu, M., Li, H., Chen, H., Wang, X., and Shen, C. Matcher: Segment anything with one shot using all-purpose feature matching. arXiv preprint arXiv:2305.13310, 2023. URL https://arxiv.org/abs/2305.13310.

Lu, Y., Bartolo, M., Moore, A., and Riedel, S. Fantastically ordered prompts and where to find them: Overcoming fewshot prompt order sensitivity. In Proceedings of the 60th Annual Meeting ofthe Associationfor Computational Linguistics (ACL), 2022. URL https://aclanthology.org/2022. acl-long.556/.

Madan, A., Peri, N., Kong, S., and Ramanan, D. Revisiting few-shot object detection with vision-language models. In Advances in Neural Information Processing Systems (NeurIPS), 2024. URL https://proceedings. neurips.cc/paper\_files/paper/2024/file/ 22b2067b8f680812624032025864c5a1-Paper-Abs html. Datasets and Benchmarks Track.

Min, S., Lyu, X., Holtzman, A., Artetxe, M., Lewis, M., Hajishirzi, H., and Zettlemoyer, L. Rethinking the role of demonstrations: What makes in-context learning work? In Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2022. URL https: //aclanthology.org/2022.emnlp-main.759/.

OpenAI. GPT-4 Technical Report. arXiv preprint arXiv:2303.08774, 2023.

Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Askell, A., Mishkin, P., Clark, J., et al. Learning transferable visual models from natural language supervision. In International conference on machine learning, pp. 8748–8763. PmLR, 2021.

Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., Zhou, Y., Li, W., and Liu, P. J. Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer. JMLR, 2020.

Rubin, O., Herzig, J., and Berant, J. Learning to retrieve prompts for in-context learning. In Proceedings of the 2022 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL), 2022. URL https://aclanthology.org/ 2022.naacl-main.191/.

Samuel, D., Ben-Ari, R., Levy, M., Darshan, N., and Chechik, G. Where’s waldo: Diffusion features for personalized segmentation and retrieval. NeurIPS, 2024.

Schulman, J., Wolski, F., Dhariwal, P., Radford, A., and Klimov, O. Proximal policy optimization algorithms. arXiv preprint arXiv:1707.06347, 2017.

Shaban, A., Bansal, S., Liu, Z., Essa, I., and Boots, B. One-shot learning for semantic segmentation. In Kim, T.-K., Zafeiriou, S., Brostow, G., and Mikolajczyk, K. (eds.), Proceedings of the British Machine Vision Conference (BMVC), pp. 167.1– 167.13. BMVA Press, September 2017. ISBN 1-901725-60-X. doi: 10.5244/C.31.167. URL https://dx.doi.org/10. 5244/C.31.167.

Shao, Z., Wang, P., Zhu, Y., Xu, R., Song, J., et al. Deepseekmath: Pushing the limits of mathematical reasoning in open language models. arXiv preprint arXiv:2402.03300, 2024.

Shi, F., Gao, R., Huang, W., and Wang, L. Dynamic mdetr: A dynamic multimodal transformer decoder for visual grounding. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2023. doi: 10.1109/TPAMI.2023.3328185.

Singh, A., Hu, R., Goswami, V., Couairon, G., Galuba, W., Rohrbach, M., and Kiela, D. FLAVA: A Foundational Language And Vision Alignment Model. In Proc. CVPR, 2022.

Von Oswald, J., Niklasson, E., Randazzo, E., Sacramento, J., Mordvintsev, A., Zhmoginov, A., and Vladymyrov, M. Transformers learn in-context by gradient descent. In Proceedings ofthe 40th International Conference on Machine Learning (ICML), volume 202 of Proceedings of Machine Learning Research, 2023. URL https://proceedings.mlr. act.press/v202/von-oswald23a.html.

Wang, P., Bai, S., Tan, S., Wang, S., Fan, Z., Bai, J., Chen, K., Liu, X., Wang, J., Ge, W., et al. Qwen2-vl: Enhancing visionlanguage model’s perception of the world at any resolution. arXiv preprint arXiv:2409.12191, 2024.

Wei, J., Bosma, M., Zhao, V. Y., Guu, K., Yu, A. W., Lester, B., Du, N., Dai, A. M., and Le, Q. V. Finetuned language models are zero-shot learners. In International Conference on Learning Representations (ICLR), 2022. URL https:// openreview.net/forum?id=gEZrGCozdqR.

Xiao, L., Yang, X., Peng, F., Yan, M., Wang, Y., and Xu, C. Clip-vg: Self-paced curriculum adapting of clip for visual grounding. arXiv preprint arXiv:2305.08685, 2023. URL https://arxiv.org/abs/2305.08685.

Xie, S. M., Raghunathan, A., Liang, P., and Ma, T. An explanation of in-context learning as implicit bayesian inference. In International Conference on Learning Representations (ICLR), 2022. URL https://openreview.net/forum?id= RdJVFCHjUMI.

Xu, Y., Zhang, M., Fu, C., Chen, P., Yang, X., Li, K., and Xu, C. Multi-modal queried object detection in the wild. arXiv preprint arXiv:2305.18980, 2023. URL https://arxiv. org/abs/2305.18980.

Yan, X., Chen, Z., Xu, A., Wang, X., Liang, X., and Lin, L. Meta rcnn: Towards general solver for instance-level low-shot learning. In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), October 2019.

Yu, L., Poirson, P., Yang, S., Berg, A. C., and Berg, T. L. Modeling context in referring expressions. In European Conference on Computer Vision (ECCV), 2016. URL https: //arxiv.org/abs/1608.00272.

Zhang, H., Zhang, P., Hu, X., Chen, Y.-C., Li, L. H., Dai, X., Wang, L., and Gao, J. Glipv2: Unifying localization and visionlanguage understanding. arXiv preprint arXiv:2206.05836, 2022. URL https://arxiv.org/abs/2206.05836.

Zhang, J., Huang, J., Jin, S., and Lu, S. Vision-language models for vision tasks: A survey. IEEE transactions on pattern analysis and machine intelligence, 46(8):5625–5644, 2024.

Zhang, R., Jiang, Z., Guo, Z., Yan, S., Pan, J., Ma, X., Dong, H., Gao, P., and Li, H. Personalize segment anything model with one shot. arXiv preprint arXiv:2305.03048, 2023.

Zhao, T. Z., Wallace, E., Feng, S., Klein, D., and Singh, S. Calibrate before use: Improving few-shot performance of language models. In Proceedings ofthe 38th International Conference on Machine Learning (ICML), volume 139 of Proceedings ofMachine Learning Research, 2021. URL https: //proceedings.mlr.press/v139/zhao21c.html.

## A. BBOX Notations

Following the standard convention adopted by recent vision–language models, bounding box coordinates are represented in a normalized coordinate space. Specifically, bounding boxes are scaled relative to the image dimensions and mapped to a fixed 0–1000 range. To remain consistent with this convention, we apply the same normalization to all bounding box annotations during preprocessing.

## B. Failure Cases:

![](images/1e4b0ff8787472c061ace9b90cf89d4abb5e0926c17d17c50c137bd7caad1527.jpg)  
Figure 6. The figure shows representative 2-shot in-context localization failure cases on GOT. These examples illustrate the intrinsic difficulty of the task, where large viewpoint and scale changes between support and query images, heavy occlusion, and background clutter make reliable localization from a small number of support examples highly challenging.

## C. Hyperparameter Tuning for $\mu$ and $\beta$

During training with the attention loss, we perform a grid search over the margin parameter µ and the weighting factor $\beta$ on the TAO dataset under the 4-shot setting. As shown in Table 1, performance is sensitive to the choice of these hyperparameters, with intermediate values yielding substantially better localization accuracy. Based on this analysis, we select $\dot { \mu } = 0 . 0 2 5$ and $\beta = 0 . 2 5$ for the TAO dataset. Similar hyperparameter searches are conducted independently for each dataset.

Table 6. Grid search over $\mu$ and $\beta$ on TAO in the 4-shot setting.

<table><tr><td> $\mu \downarrow$ </td><td> $I$ </td><td> $\beta \rightarrow$ </td><td>0.0</td><td>0.01</td><td>0.15</td><td>0.20</td><td>0.25</td><td>0.30</td><td>0.35</td><td>1.0</td></tr><tr><td></td><td>0.025</td><td></td><td>34.3</td><td>37.2</td><td>53.2</td><td>55.9</td><td>57.1</td><td>56.4</td><td>52.5</td><td>28.1</td></tr><tr><td></td><td>0.05</td><td></td><td>34.3</td><td>40.8</td><td>48.6</td><td>49.7</td><td>50.2</td><td>51.3</td><td>50.7</td><td>24.2</td></tr><tr><td></td><td>0.075</td><td></td><td>34.3</td><td>38.7</td><td>46.1</td><td>47.3</td><td>47.5</td><td>45.5</td><td>44.7</td><td>23.4</td></tr></table>

## D. Attention Heatmap Upsampling and Visualization.

To visualize attention distributions over the input image, we convert the model’s 1D attention vector into a spatial heatmap aligned with the image’s resolution. Given a 1D attention tensor of length $N _ { \ast }$ we first infer its underlying 2D grid resolution $( H _ { \mathrm { g r i d } } , W _ { \mathrm { g r i d } } )$ based on the target image dimensions $( H , W )$ . The attention vector is then reshaped into a 2D map of size $H _ { \mathrm { g n i d } } \times W _ { \mathrm { g r i d } } .$ To obtain a dense attention heatmap at the image resolution, we upsample this grid using bilinear interpolation to size $H \times W$ , ensuring spatial alignment with the original image. This upsampled heatmap is subsequently normalized and overlaid on the image for visualization and analysis.

Table 7. Training configuration for supervised fine-tuning (SFT), GRPO, and LoRA.

<table><tr><td>Setting</td><td>Value</td></tr><tr><td colspan="2">Supervised Fine-Tuning (SFT) Configuration</td></tr><tr><td>Base model</td><td>Qwen2-VL-7B-Instruct</td></tr><tr><td>Learning rate</td><td> $2 \times 10^{-4}$ </td></tr><tr><td>Gradient accumulation steps</td><td>16</td></tr><tr><td>Warmup ratio</td><td>0.03</td></tr><tr><td>Max gradient norm</td><td>0.3</td></tr><tr><td>Precision</td><td>bfloat16</td></tr><tr><td colspan="2">GRPO Training Configuration</td></tr><tr><td>Base model</td><td>Qwen2-VL-7B-Instruct</td></tr><tr><td>Optimization method</td><td>Group Relative Policy Optimization (GRPO)</td></tr><tr><td>Number of generations</td><td>4</td></tr><tr><td>Max prompt length</td><td>8192</td></tr><tr><td>Learning rate</td><td> $1 \times 10^{-5}$ </td></tr><tr><td>Warmup ratio</td><td>0.01</td></tr><tr><td>Max gradient norm</td><td>1.0</td></tr><tr><td>Precision</td><td>bfloat16</td></tr><tr><td>Attention implementation</td><td>FlashAttention-2</td></tr><tr><td>Reward functions</td><td>Accuracy, Format correctness</td></tr><tr><td colspan="2">LoRA Fine-Tuning Configuration</td></tr><tr><td>LoRA rank (r)</td><td>8</td></tr><tr><td>LoRA scaling (α)</td><td>16</td></tr><tr><td>LoRA dropout</td><td>0.0</td></tr><tr><td>Target modules</td><td>q_proj, k_proj, v_proj, o_proj,up_proj, down_proj, gate_proj</td></tr><tr><td>Task type</td><td>Causal language modeling</td></tr><tr><td>Model quantization</td><td>4-bit</td></tr></table>

## E. FOCUS with 72B model

We further evaluate FOCUS on the 72B model setting to compare with the strongest reported IPLoc baseline. IPLoc reports results using Qwen2-VL-72B with real and pseudo examples. Since our original experiments were conducted under a more limited compute setting, we trained FOCUS primarily with Qwen2-VL-7B. To assess scalability to larger models, we additionally train FOCUS using Qwen3-VL-72B on 8 A100 80GB GPUs and evaluate on the ICL-LASOT dataset. The results are reported in Table 8.

Table 8. Comparison with IPLoc on TAO.

<table><tr><td>Model</td><td>2-shot</td><td>4-shot</td></tr><tr><td>IPLoc (72B) (Real + Pseudo)</td><td>65.71</td><td>67.63</td></tr><tr><td>FOCUS (on Qwen2-VL-72B)</td><td>70.72</td><td>72.35</td></tr></table>