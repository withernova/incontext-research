# Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models

Kensuke Nakamura<sup>a</sup>, Byung-Woo Hong<sup>a,∗</sup>

<sup>a</sup>Artificial Intelligence Department, Chung-Ang University, Seoul, 06974, Korea

## Abstract

Personalized object localization (POL) localizes an object instance in a query image based on a few reference images with bounding-box annotations and a target object label. The pioneering method, IPLoc, solves this task through in-context inference with vision-language models (VLMs). However, it assumes that the query image always contains the target object. This assumption severely limits its applicability to real-world scenarios with many irrelevant images. To address this issue, we formulate a new task, personalized object identification and localization (POIL), by positioning POL within the broader few-shot object detection framework. POIL aims to localize the target object instance while rejecting query images that do not contain the reference object instance. We also present POIL datasets constructed from public sources. We further propose an in-context algorithm named IPLoc-ID for solving POIL with VLMs. IPLoc-ID first predicts a candidate bounding box and then determines whether it corresponds to the reference object instance. We introduce a self-posed query to connect these two steps within a single autoregressive generation framework. Through ablation studies and comprehensive experiments, we show that IPLoc-ID substantially suppresses false-positive detections on negative query images while maintaining localization performance comparable to IPLoc. Overall, IPLoc-ID efectively addresses the practical instance-level POIL task, which cannot be suficiently solved by conventional object detection, few-shot object detection, or the localization-only IPLoc method.

Keywords: object detection, object identification, bounding-box localization, vision-language models, in-context learning

## 1. Introduction

Object detection (OD) is a fundamental visual recognition task that aims to find objects in an image and estimate their locations as bounding boxes. Recent advances in open-vocabulary object detection and few-shot object detection (FSOD) have made it possible to detect objects specified not only by predefined categories but also by text labels or a small number of support examples [1– 5]. However, most of these methods are essentially designed for category-level detection and do not aim to identify a specific object instance indicated by reference data. For example, even when a reference image specifies a particular cat, conventional OD or FSOD methods may regard detecting another cat from the same category as a successful result. In contrast, reference-conditioned instance-level localization aims to detect a specific object instance indicated by reference data in a query image. Such a capability is expected to be useful for future applications such as user-specified image retrieval, video grounding, object re-identification, and personalized object tracking.

In this line of research, IPLoc (in-context personalized object localization) [6] is pioneering work on reference-conditioned instance-level localization. It exploits the contextual understanding ability of transformer-based vision-language models (VLMs) to localize the corresponding object region in a query image based on reference data. IPLoc takes a small number of images with bounding-box (BBOX) annotations and the target label as reference data, and generates the BBOX coordinates for the query image through next-token prediction. This formulation enables reference-conditioned inference with VLMs without fine-tuning to the reference data. However, IPLoc assumes that the target object is present in the query image, i.e., the query image is positive. Therefore, even when the target object is absent from a negative query image, IPLoc still generates a bounding box. As a result, in practical scenarios such as image retrieval and video grounding, where most candidate images may not contain the object of interest, users must either preselect positive query images before inference or manually remove false-positive detections after inference. This severely limits the practical applicability of the IPLoc framework.

To further unlock the object detection capability of VLMs for practical applications, we revisit the localization setting of IPLoc and introduce a more general task, termed personalized object identification and localization (POIL). In this task, the model is required to output a bounding box when the same object instance specified by the reference data exists in the query image, and to reject the query image otherwise. Figure 1 illustrates the characteristic behavior of existing methods under the POIL setting. Conventional OD and FSOD methods operate mainly at the category level and may therefore produce falsepositive detections on negative examples containing object instances diferent from the reference object. Similarly, IPLoc has no explicit mechanism for rejecting negative query images and exhibits the same failure mode. We also construct customized datasets based on public video object tracking datasets. The constructed datasets consist of instance-level positive and negative examples and are suitable for fine-tuning and evaluating models under the POIL task.

![](images/451e316405297cb1b3e5208513665a118ab35e7e4ed9caac8d3842802e1f0982.jpg)  
Figure 1: [In-context inference for personalized object identification and localization task] (Left) Examples of reference data, (Right) positive and negative query images, and inference results using Florence-2, No-Time-To-Train (NT3), Qwen2-VL with prompting, IPLoc, and the proposed IPLoc-ID, respectively: Red boxes indicate reference annotations, green boxes indicate correct detections, and magenta boxes indicate false-positive detections. More detail is shown in Section 4.

We further propose an in-context algorithm, IPLoc-ID, for solving the POIL task with VLMs. IPLoc-ID reinterprets the BBOX, which is treated as the final output in IPLoc, as a reference-conditioned candidate, and then determines whether this candidate actually corresponds to the reference object instance through a subsequent identification component. Specifically, based on the autoregressive generation process of VLMs, IPLoc-ID generates the BBOX, a self-posed query, and an identification answer as a single continuous text sequence. The self-posed query connects the input reference data, the query image, and the previously generated BBOX into a single token sequence, naturally eliciting the final Yes/No identification response. By fine-tuning with both positive and negative examples, IPLoc-ID jointly learns reference-conditioned candidate localization and instance-level identification. Through ablation studies and comprehensive experiments on four datasets, we show that IPLoc-ID substantially suppresses false-positive detections on negative query images while maintaining the localization performance of IPLoc. As a result, the proposed method shows a clear advantage in instance-level identification and localization, which cannot be suficiently addressed by conventional OD, FSOD methods, or the previous localization-only IPLoc framework.

The remainder of this paper is organized as follows. Section 2 summarizes related works. Section 3 describes the proposed framework. Section 4 reports empirical results. Section 5 concludes this paper.

## 2. Related Works

Few-shot object detection (FSOD) aims to detect novel object categories from a few annotated examples [3, 4]. Representative approaches include finetuning-based methods such as TFA [5], FSCE [7], and DeFRCN [8], meta-learning or support-query interaction methods such as Meta R-CNN [9] and fully crosstransformer-based methods [10], and recent transformer- or foundation-modelbased methods such as DE-ViT [11]. More recent FSOD methods exploit vision foundation models: FT-FSOD [12] fine-tunes Grounding-DINO [2] with support data, FSOD-VFM (VFM) [13] constructs class-wise prototypes using UPN, SAM2, and DINOv2, and No-Time-To-Train [14] performs training-free matching between support features and SAM-generated masks. The key diference from our POIL task is that FSOD is category-level, whereas POIL is instance-level. In FSOD, detecting any object of the target category is suficient. In contrast, POIL requires localizing the specific reference-conditioned instance and rejecting other instances, including in-class distractors. Moreover, while recent FSOD pipelines often rely on task-specific modules such as SAM, IPLoc variants aim to exploit the general-purpose visual reasoning ability of VLMs. In our experiments, we compare with VFM and No-Time-To-Train to highlight this diference between category-level FSOD and instance-level POIL.

Instance-level retrieval and localization. Recent studies have extended retrieval and localization toward instance-level matching. i-CIR [15] retrieves a specific instance using a visual query and textual modification, but does not perform spatial localization. REIR [16] retrieves and localizes instances using finegrained natural language expressions, whereas POIL specifies the target through reference images, labels, and bounding boxes. Few-Shot Object Localization (FSOL) [17] localizes objects from limited support examples, but does not explicitly address negative query rejection. These studies show the importance of instance-level retrieval and localization. In contrast to them, POIL focuses on VLM-based in-context inference, where the reference-conditioned instance must be localized when present and rejected when absent.

Vision-language models. Vision foundation models have become central to computer vision. Contrastive vision-language models such as CLIP [18] and Open-CLIP [19] learn joint image-text representations, while BLIP variants [20, 21] combine visual understanding with language generation. Task-specific foundation models such as SAM [22] and DINOv2 [23] provide visual modules for downstream pipelines. VLMs, including LLaVA [24], Gemma [25], and Qwen-VL [26, 27], integrate visual perception and language generation, enabling instruction-based visual reasoning, detection, and grounding [24, 26–29]. For localization tasks, an important challenge is to design prompts and input contexts that make VLMs produce reliable structured outputs such as bounding boxes. IPLoc [6] addresses this direction by formulating personalized object localization as sequence generation. Our work extends IPLoc by adding an identification component based on a self-posed query, enabling the model to decide whether the localized candidate matches the reference instance.

Self-posed query. Question generation and self-questioning have been studied as mechanisms for improving model reasoning in language tasks [30, 31] and vision-language tasks [32, 33]. Our self-posed query is inspired by this idea but difers in purpose and formulation. Rather than generating diverse or recursive questions for general reasoning, IPLoc-ID uses a fixed intermediate query to connect the generated BBOX candidate with the final identification answer. This design induces a simple sequence from context, to localization, to identification, and enables instance-level rejection within VLM-based inference.

In-context learning and personalized object localization. In-context learning allows a model to solve a task using examples and context provided in the input, without updating model parameters at test time [34]. Although originally studied in language models, it has also been extended to VLM settings [35–37]. Here, the model may be trained beforehand to acquire the task format, but the reference data is used only as input context in inference. IPLoc [6] is a representative in-context approach for personalized object localization. Our work follows this paradigm and extends it to a more practical setting where query images may or may not contain the intended object instance.

## 3. Method

This section defines POIL and formulates IPLoc and its limitation under this setting. We then present IPLoc-ID as a VLM-based in-context solution and describe the customized POIL datasets.

## 3.1. Preliminary

## 3.1.1. Personalized object identification and localization

We first introduce personalized object identification and localization (POIL). Here, a “personalized object” [6] denotes a specific object instance specified by reference data, such as reference images, labels, or annotations. Given such reference data and a target image, POIL aims to identify and localize the same object instance in the target image.

Conceptually, POIL extends POL by introducing negative-query rejection and can also be viewed as an instance-level counterpart of conventional FSOD. While FSOD detects objects at the category level from support data, POIL requires detecting a specific object instance. Although the original IPLoc also localizes a specific object from the same input data, its formulation can produce false positives for objects other than the intended instance. In POIL, the model must localize the target object only when the same instance as the reference object appears in the target image; otherwise, it must reject the image. This property is essential for instance-level applications such as image retrieval, video grounding, and object identification.

Formally, we define the POIL task as follows. Let the input be defined as

$$
x = \{(I _ {k} ^ {\mathrm{r}}, \ell , B _ {k} ^ {\mathrm{r}}) \} _ {k = 1} ^ {N}, I ^ {\mathrm{t}}, \ell ,\tag{1}
$$

where $I _ { k } ^ { \mathrm { r } }$ denotes the k-th reference image, $B _ { k } ^ { \mathrm { r } }$ denotes its annotated bounding box, and ℓ denotes the corresponding class label. $I ^ { \mathrm { t } }$ and ℓ denote the target query image and its query label, respectively. This input format follows the original IPLoc formulation. The input x is converted into a sequence of tokens and fed into a transformer-based VLM.

Let X be the input space, where each input $x \in \mathcal { X }$ consists of reference data and a query image. Importantly, diferent from the original IPLoc, we do not restrict X to inputs in which the query image necessarily contains the object specified by the reference data. This allows practical scenarios where the query image $I ^ { \mathrm { t } }$ does not contain the same object instance as the reference data. We refer to such inputs as “negative examples”, in contrast to “positive examples” whose query image contains the object of interest. To handle both positive and negative data, we define the identification condition

$$
\delta (x) \in \{0, 1 \},\tag{2}
$$

where $\delta ( x ) = 1$ if the query image in x contains the same object instance as specified by the reference data, and $\delta ( x ) = 0$ otherwise.

Let B denote the bounding-box space and ∅ denote rejection. We then define the ideal task of POIL as a mapping

$$
f ^ {*}: \mathcal {X} \to \mathcal {B} \cup \{\varnothing \},\tag{3}
$$

such that

$$
f ^ {*} (x) = \left\{ \begin{array}{l l} B ^ {\mathrm{t}}, & \text {if} \delta (x) = 1, \\ \varnothing , & \text {if} \delta (x) = 0. \end{array} \right.\tag{4}
$$

where $B ^ { \mathrm { t } } \in B$ denotes the ground-truth bounding box of the reference object instance in the query image when it exists. Our main objective is to develop an algorithm that accurately approximates the ideal mapping in Eq. (4).

## 3.1.2. Evaluation metric for POIL

Following common OD and FSOD evaluation metrics, we use mIoU [38, 39] to measure BBOX localization accuracy and F1-score [40] to evaluate instance-level identification, including false-positive suppression on negative query images.

## 3.2. The baseline IPLoc

## 3.2.1. Formulation of IPLoc

IPLoc [6] is an in-context algorithm for personalized object localization (POL). Following the input format x defined in Eq. (1), POL aims to generate the bounding-box coordinates of the object category or instance specified by the reference data. Since IPLoc is trained with the standard next-token-prediction objective to generate localization coordinates, its VLM-based output can be formulated as conditional generation of the target bounding box. Specifically, given an input $x ,$ the output sequence of IPLoc can be written as

$$
y = \langle B \rangle ,\tag{5}
$$

where $B \in B$ denotes the estimated bounding-box coordinates in the query image, and $\langle \cdot \rangle$ denotes a generated text component in the output sequence. Equivalently, IPLoc parameterized by θ models the conditional probability

$$
p _ {\theta} (B ^ {\mathrm{t}} \mid x),\tag{6}
$$

and generates the BBOX component as

$$
B = \arg \max _ {b \in \mathcal {B}} p _ {\theta} (b \mid x).\tag{7}
$$

During fine-tuning, IPLoc constructs multi-modal conversations from image sequences. Each conversation consists of the input x and the ground-truth BBOX for the query image as the target output. Accordingly, IPLoc is trained by minimizing the negative log-likelihood of the target bounding box:

$$
\min _ {\theta} \mathbb {E} _ {(x, B ^ {\mathrm{t}}) \sim \tilde {P}} \left[ - \log p _ {\theta} (B ^ {\mathrm{t}} \mid x) \right],\tag{8}
$$

where $\tilde { P }$ denotes the POL training distribution, in which the query image contains the object specified by the reference data. The original IPLoc also introduces pseudo-label-based label noise. Specifically, the class label ℓ in the input sequence is randomly replaced with a pseudo label during training. This reduces overfitting to specific class names and encourages localization based on visual examples and bounding-box annotations.

A key insight of IPLoc is to exploit the contextual understanding ability of transformer-based VLMs by formulating localization as sequence generation. In this formulation, the personalized examples establish a repeated order of image, label, and bounding-box coordinates. Given a query with only an image and label, this format induces the model to complete the sequence by predicting the missing bounding box.

## 3.2.2. Limitation of IPLoc

However, IPLoc assumes that the object of interest is always present in the query image. This limitation follows from its output-space constraint: IPLoc maps any input $x \in \mathcal { X }$ to a bounding box in B. In contrast, for a negative query image satisfying $\delta ( x ) = 0$ , the ideal POIL mapping in Eq. (4) requires the rejection output $f ^ { * } ( x ) = \alpha$ . Since $\emptyset \notin B$ , IPLoc cannot represent the ideal output for negative query images. Equivalently, even when the query image does not contain the reference object instance, IPLoc still returns a bounding box:

$$
f _ {\mathrm{IPLoc}} (x) \in \mathcal {B} \quad \text {even when} \quad f ^ {*} (x) = \varnothing .\tag{9}
$$

This mismatch between the IPLoc formulation in Eq. (9) and the ideal POIL mapping in Eq. (4) leads to false-positive detections on negative query images.

This false-positive behavior, as discussed in Section 1, limits the applicability of IPLoc under the POIL setting, where target images may or may not contain the reference object. Thus, the model must localize true-positive cases while also identifying true-negative cases and rejecting query images without the reference object. To address this requirement, we extend IPLoc to IPLoc-ID, which incorporates identification into personalized object localization.

## 3.3. The Proposed IPLoc-ID

We now propose IPLoc-ID as an in-context algorithm for solving POIL. IPLoc-ID leverages the strong generalization ability of VLMs to localize the object of interest in positive query images while rejecting negative query images that do not contain the reference object instance. To this end, we decompose Eq. (4) into BBOX localization and identification, and generate them sequentially as text using a VLM. The BBOX component first produces a candidate bounding box in the query image, following the sequence-generation principle of IPLoc. The identification component then verifies whether the generated BBOX corresponds to the object instance specified by the reference data. To connect these components, we introduce a self-posed query, which preserves the natural sequence from input data to generated text. Finally, an interpreter function converts the generated text into the structured output required by POIL. Figure 2 illustrates the overall framework of IPLoc-ID.

![](images/4d6bbf3839a25151337027a6abd942fd7b2b343b1153d2dfa480d7eefab18450.jpg)  
Figure 2: [The proposed IPLoc-ID framework] (Top) We introduce personalized object identification and localization (POIL) and construct datasets by augmenting video object tracking data with negative query images. (Bottom) IPLoc-ID extends the sequence-generation formulation of IPLoc by generating a BBOX candidate, a self-posed query, and an identification answer in an autoregressive process, enabling the model to reject negative query images.

## 3.3.1. Sequential generation of localization and identification

IPLoc-ID generates the following text sequence:

$$
y = \langle B \rangle \langle Q \rangle \langle A \rangle ,\tag{10}
$$

where $B \in B$ denotes the generated bounding box, $Q$ denotes the fixed self-posed query, and $A \in { \mathcal { A } }$ denotes the identification answer, with $\mathcal { A } = \{ \mathrm { Y e s } , \mathrm { N o } \}$ . The answer A is designed to approximate the identification condition $\delta ( x )$ :

$$
A ^ {*} (x) = \left\{ \begin{array}{l l} \text {Yes,} & \text {if} \delta (x) = 1, \\ \text {No,} & \text {if} \delta (x) = 0. \end{array} \right.\tag{11}
$$

Thus, the BBOX component provides a candidate localization, while the answer component determines whether the candidate should be accepted or rejected.

The autoregressive generation process of IPLoc-ID using a VLM parameterized by $\theta$ can be factorized as

$$
p _ {\theta} (y \mid x) = p _ {\theta} (B \mid x) \cdot p _ {\theta} (Q \mid x, B) \cdot p _ {\theta} (A \mid x, B, Q).\tag{12}
$$

Since $Q$ is fixed by the output format, $p _ { \theta } ( Q \mid x , B ) = 1$ . Thus, IPLoc-ID efec tively decomposes output generation into BBOX generation and identification:

$$
p _ {\theta} (y \mid x) = p _ {\theta} (B \mid x) \cdot p _ {\theta} (A \mid x, B, Q).\tag{13}
$$

During inference, IPLoc-ID first generates the BBOX component:

$$
y _ {1} = \langle B \rangle , \qquad B = \arg \max _ {b \in \mathcal {B}} p _ {\theta} (b \mid x).\tag{14}
$$

This follows the same BBOX-generation process as IPLoc, but produces a reference-conditioned candidate bounding box in the query image. Second, IPLoc-ID appends the fixed self-posed query:

$$
y _ {2} = \langle Q \rangle .\tag{15}
$$

Unlike prior self-questioning methods [30–32], our fixed self-posed query does not introduce an additional stochastic decision, but bridges the generated BBOX candidate and the final identification answer. The efect of this design is analyzed in Section 4.3.

Third, IPLoc-ID generates the identification answer:

$$
y _ {3} = \langle A \rangle , \qquad A = \arg \max _ {a \in \mathcal {A}} p _ {\theta} (a \mid x, B, Q),\tag{16}
$$

where $\mathcal { A } = \{ \mathrm { Y e s } , \mathrm { N o } \}$ denotes the answer space. The final output in Eq. (10) is then formed by the sequential generation of $y _ { 1 } , y _ { 2 }$ , and $y _ { 3 }$ .

## 3.3.2. Fine-tuning with positive and negative examples

In-context learning allows a model to solve a task using reference examples and contextual information in the input, without updating model parameters at test time [34]. Following this principle, IPLoc-ID performs inference without updating the model on test data. To acquire the required task format and contextual reasoning ability, we fine-tune the VLM for POIL using both positive and negative examples.

The fine-tuning objective of IPLoc-ID is formulated as min $F ( \theta )$ , where θ denotes the model parameters and $F ( \theta )$ maximizes the likelihood of the entire target output sequence. Specifically, $F ( \theta )$ is defined as

$$
F (\theta) := \mathbb {E} _ {(x, y ^ {*}) \sim P} \left[ - \log p _ {\theta} (B ^ {\mathrm{t}} \mid x) - \log p _ {\theta} (Q \mid x, B ^ {\mathrm{t}}) - \log p _ {\theta} (A ^ {*} (x) \mid x, B ^ {\mathrm{t}}, Q) \right],\tag{17}
$$

where $P$ denotes the POIL training distribution, including both positive and negative examples. The target output sequence $y ^ { * }$ is defined as

$$
y ^ {*} = \langle B ^ {\mathrm{t}} \rangle \langle Q \rangle \langle A ^ {*} (x) \rangle ,\tag{18}
$$

where $B ^ { \mathrm { t } }$ denotes the target BBOX, Q denotes the fixed self-posed query, and $A ^ { * } ( x )$ denotes the ground-truth identification answer determined by whether the query image contains the reference object instance.

Positive examples contain the same object instance as specified by the reference data, and their target answer is Yes. Negative examples use query images that do not contain the reference object instance, and their target answer is $\mathrm { N o }$ . To learn reference-conditioned instance-level discrimination, we construct negative examples from diferent object instances, including instances from the same category as the positive examples. More details of dataset construction are provided in Section 3.5.

For positive examples, $B ^ { \mathrm { t } }$ is the ground-truth bounding box of the reference object instance in the query image. For negative examples, $B ^ { \mathrm { t } }$ is the BBOX of the most plausible candidate object in the query image. Thus, even for negative examples, the model first generates a candidate BBOX following the same sequence-generation process. However, this BBOX is treated only as a reference-conditioned candidate region, and the subsequent identification answer determines whether it corresponds to the reference object instance. This enables the model to learn both candidate localization and instance-level rejection.

## 3.3.3. Interpretation of generated results

We employ an interpreter $\gamma ( y )$ to extract the generated BBOX text $\langle B \rangle$ and answer text $\langle A \rangle$ from the generated text. The implementation of the interpreter $\gamma$ is described in Section 3.4. We define the interpreter output as

$$
\gamma (y) = \left\{ \begin{array}{l l} 1, & \text {if} \langle A \rangle \text {is interpreted as positive}, \\ 0, & \text {if} \langle A \rangle \text {is interpreted as negative}. \end{array} \right.\tag{19}
$$

Based on this interpreter output, we define the final prediction as

$$
f (x) = \left\{ \begin{array}{l l} B, & \text {if} \gamma (y) = 1, \\ \varnothing , & \text {if} \gamma (y) = 0, \end{array} \right.\tag{20}
$$

where $B$ denotes the generated BBOX coordinates. This IPLoc-ID formulation approximates the ideal mapping in Eq. (4) by returning a BBOX for positive query images and rejecting negative query images.

Table 1: Examples of generated texts and their interpreted model response.

<table><tr><td>Generated text</td><td>Response</td></tr><tr><td>“[175.9, 411.1, 656.3, 866.7]”</td><td>positive</td></tr><tr><td>“Not found.”</td><td>negative</td></tr><tr><td>“bbox=[197.0, 388.0, 640.0, 843.0]\n same_object=NO”</td><td>negative</td></tr><tr><td>“[382.1, 233.3, 595.8, 605.6], Do all these boxes have the same object? Yes.”</td><td>positive</td></tr><tr><td>“[187.5, 405.6, 656.3, 855.6], Do all these boxes have the same object? No.”</td><td>negative</td></tr></table>

## 3.4. Implementation of IPLoc-ID

Interpreter function. Since VLMs generate free-form text, an interpreter is required to convert generated text into structured outputs. In this study, the interpreter extracts bounding-box coordinates (⟨BBOX⟩) and the identification response (⟨Ans⟩). If the generated text contains an explicit negative expression such as No, Not found, different, or not the same, or contains no valid bounding box, it is classified as a negative response. Otherwise, it is treated as a positive response, allowing methods without an identification component, such as the original IPLoc, to be consistently interpreted as positive. Table 1 shows examples of model outputs and their interpreted responses.

LoRA fine-tuning. For fine-tuning, we employ LoRA [41], a standard parameter-eficient fine-tuning method. Let $\theta _ { 0 }$ denote the frozen parameters, and let $\phi$ denote the trainable LoRA parameters. The efective model parameters are written as $\theta ( \phi ) = \theta _ { 0 } + \Delta _ { \mathrm { L o R A } } ( \phi )$ , where $\Delta _ { \mathrm { L o R A } } ( \phi )$ denotes the low-rank update. Accordingly, we optimize Eq. (17) with respect to ϕ as ${ \mathrm { m i n } } _ { \phi } F \left( \theta ( \phi ) \right)$ ).

## 3.5. Datasets for the POIL task

We construct datasets for fine-tuning and evaluating the POIL task. We use four public sources: LaSOT [42], PDM (Burst) [43], GOT-10K [44], and VastTrack [45]. These datasets are selected because they (i) consist of image sequences, (ii) provide annotations suitable for BBOX localization, and (iii) include class labels. Among them, LaSOT provides high data volume and class diversity, with multiple sub-classes per class corresponding to diferent object instances or video sequences. We therefore use a subset of LaSOT for fine-tuning, and use the LaSOT test split and the other datasets for evaluation.

Table 2 summarizes the customized datasets. Each data sample contains one positive and one negative query image that share the same reference data. Thus, the actual number of examples is twice the number of data samples. For example, the LaSOT training set contains 700 data samples, corresponding to 700 positive and 700 negative examples. For simplicity, we refer to each customized dataset by its source name.

## 3.5.1. Sampling procedure

The sampling procedure is illustrated in the top part of Figure 2. Reference data and positive query images are sampled following the original IPLoc, while negative query images are newly introduced for POIL. From each video sequence, we uniformly sample N + 1 frames: the first N frames are used as reference data, and the last frame is used as the positive query image with its ground-truth BBOX. We then sample one negative query image from a diferent instance, either from a diferent class or from a diferent sub-class within the same class. The positive and negative query images share the same reference data but are treated as independent query cases during training and evaluation.

## 3.5.2. Training set

We construct the training set from LaSOT. The public LaSOT dataset contains approximately 70 classes, and each class contains multiple sub-classes corresponding to diferent object instances or video sequences.

We split the classes into training and test splits and apply the above sampling procedure to the training split. Negative query images are sampled from diferent sub-classes within the same class, providing in-class adversarial examples. As a result, we obtain 700 training samples, each consisting of N reference images, one positive query image, and one negative query image.

## 3.5.3. Test set

We construct 140 LaSOT test samples from the held-out class split, using in-class negative query images. This test set evaluates generalization to unseen classes within the same domain.

For unseen-domain evaluation, we use PDM, GOT-10K, and VastTrack without fine-tuning on these datasets. For PDM and GOT-10K, which do not provide explicit sub-class structures, negative query images are sampled from diferent classes. For VastTrack, we select approximately 400 classes with at least two sub-classes and sample in-class negative query images from diferent sub classes within the same class. Thus, VastTrack provides a larger unseen-domain test set with more challenging in-class negative examples.

## 3.5.4. N-shot settings

We evaluate four N-shot settings: N = 1, 2, 4, 8. To isolate the efect of N, datasets with smaller N are constructed as subsets of the N = 8 set, sharing the same positive and negative query images. Because IPLoc-ID is sensitive to the number of reference images used during fine-tuning, we fine-tune separate models for each N and evaluate them on the corresponding N-shot test sets.

Table 2: Summary of customized datasets.

<table><tr><td>Dataset</td><td>#Training</td><td>#Test</td><td>N-shot</td><td>Negative data</td></tr><tr><td>LaSOT [42]</td><td>700</td><td>140</td><td>1, 2, 4, 8</td><td>in-class</td></tr><tr><td>PDM [43]</td><td>-</td><td>745</td><td>1, 2</td><td>out-of-class</td></tr><tr><td>GOT-10K [44]</td><td>-</td><td>180</td><td>1, 2, 4, 8</td><td>out-of-class</td></tr><tr><td>VastTrack [45]</td><td>-</td><td>400</td><td>1, 2, 4, 8</td><td>in-class</td></tr></table>

## 4. Experimental Results

In this section, we first present the experimental setup and discuss the selection of backbone models. Then, we conduct ablation studies. Finally, we report the main results.

## 4.1. Experimental Setup

## 4.1.1. Training procedure

Using LoRA, we fine-tune each backbone model on the customized training set. For each backbone, we train two variants: IPLoc using Eq. (8) and IPLoc-ID using Eq. (17). During training, positive and in-class negative pairs are sequentially fed in a randomized order, enabling IPLoc-ID to learn instance-level decision boundaries. The same pairs are also used to train IPLoc, ensuring that IPLoc and IPLoc-ID are trained on identical data. This does not change the formulation of IPLoc, which performs only BBOX localization for each target image. We also observe that using negative examples improves IPLoc mIoU, suggesting their role as data augmentation even for localization-only training.

Our reproduced IPLoc may not be strictly identical to the original IPLoc, as its complete training configuration and scripts are not publicly available. Moreover, the original IPLoc does not consider negative examples and was trained using three datasets [6]. Nevertheless, our reproduced IPLoc shows the expected localization-only behavior under standard training settings. We also include the partially released oficial Qwen2-VL-7B IPLoc model, denoted by “IPLoc 7B (oficial)”, as a reference in the final comparison.

## 4.1.2. Evaluation procedure

The final model is further evaluated on the test datasets using mIoU and F1-score. mIoU measures BBOX localization accuracy, while F1-score assesses identification performance. Since positive and negative query images are balanced in our setting, methods that always return positive responses, such as localization only detectors and IPLoc, yield an F1-score of $2 / 3 \ ( \simeq 0 . 6 6 7 )$ . Thus, this value serves as the theoretical baseline for methods without an explicit negative-query rejection mechanism. Unless otherwise specified, we report the average metrics over three independent training/evaluation runs.

## 4.1.3. Other experimental details

Our implementation is based on Hugging Face, and all backbone models are publicly available on the same platform. We use LoRA with rank r = 8 and scaling factor $\alpha = 1 6$ , following common LoRA fine-tuning settings and the publicly disclosed details of the original IPLoc configuration. The remaining hyperparameters follow standard Hugging Face LoRA fine-tuning examples. Model training and inference were primarily conducted on four NVIDIA A100 GPUs. For Qwen3-VL-235B, we used eight NVIDIA B200 GPUs.

![](images/83c7ff8219085aa35b48fdce09d0c5073e554aa606730ffa1fd245b66f46a075.jpg)  
(1) Qwen2-VL-7B

![](images/9e302ebe94ad1ecb0c32bbb174711a629d400189e608f6f547d9acb01978c0d8.jpg)  
(2) Qwen3-VL-8B

![](images/0a0f00f6eaf71742e3a462c0e337dc0fdfd226abfba3e01935eb0eb19e9a21f6.jpg)  
(3) Qwen3-VL-32B  
Figure 3: [Training curves] The mIoU (solid line) and F1-score (dotted line) curves for the LaSOT test set during training based on diferent backbones trained using (blue) only BBOX loss (IPLoc), (green) two-stage training, and (magenta) the proposed unified loss.

## 4.2. Backbone Model Selection

The proposed method assumes a transformer-based VLM with autoregressive text generation. We empirically select the backbone architecture and model size based on performance as follows.

## 4.2.1. Model architecture

We first compare the following VLMs: LLaVA1.5-7B, Gemma3-12B, Qwen2- VL-7B, and Qwen3-VL-8B, as shown in Table 3. These models are representative open-source pretrained VLMs. LLaVA1.5-7B is one of the early instructiontuned models. Gemma3-12B is a recent VLM with strong conversational ability. Qwen2-VL-7B is one of the backbones used in the previous IPLoc study. Qwen3- VL-8B represents the next generation of the Qwen series, and we further examine its larger variants.

Table 3 shows that the Qwen models outperform Gemma3 and LLaVA1.5 in mIoU. One possible explanation is that the Qwen series is more efective for visual localization and structured coordinate generation in our setting. In addition, Qwen3-VL-8B outperforms Qwen2-VL-7B in both mIoU and F1-score under similar model sizes. Based on these results, we adopt Qwen3-VL-8B as the main backbone of our method, while Qwen2-VL-7B is also included in the basic analyses for consistency with the previous IPLoc study.

## 4.2.2. Model-size scalability

We compare three Qwen3-VL variants: 8B, 32B, and 235B, as shown in Table 3. Qwen3-VL-8B and Qwen3-VL-32B are dense models, whereas Qwen3- VL-235B adopts a Mixture-of-Experts (MoE) architecture, where tokens are dynamically routed to a subset of experts. As shown in Table 3, performance improves with model scale, and the result with Qwen3-VL-235B suggests that IPLoc-ID can also benefit from the known scalability of sparse MoE models [46].

In the following ablation studies, we mainly use Qwen3-VL-8B and Qwen3-VL 32B as representative dense backbones for controlled experiments, and include Qwen3-VL-235B in the final comprehensive evaluation.

Table 3: [Backbone model selection] mIoU and F1-score on the LaSOT test set for backbones under diferent N-shot settings.

<table><tr><td rowspan="3">Backbone</td><td colspan="8">mIoU (↑)</td></tr><tr><td colspan="4">IPLoc</td><td colspan="4">IPLoc-ID</td></tr><tr><td>N=1</td><td>N=2</td><td>N=4</td><td>N=8</td><td>N=1</td><td>N=2</td><td>N=4</td><td>N=8</td></tr><tr><td>LLaVA1.5-7B</td><td>0.345</td><td>0.375</td><td>0.397</td><td>0.065</td><td>0.348</td><td>0.379</td><td>0.369</td><td>0.064</td></tr><tr><td>Gemma3-12B</td><td>0.377</td><td>0.395</td><td>0.406</td><td>0.444</td><td>0.382</td><td>0.442</td><td>0.422</td><td>0.450</td></tr><tr><td>Qwen2-VL-7B</td><td>0.501</td><td>0.536</td><td>0.561</td><td>0.580</td><td>0.503</td><td>0.535</td><td>0.571</td><td>0.580</td></tr><tr><td>Qwen3-VL-8B</td><td>0.632</td><td>0.675</td><td>0.694</td><td>0.711</td><td>0.637</td><td>0.673</td><td>0.698</td><td>0.714</td></tr><tr><td>Qwen3-VL-32B</td><td>0.650</td><td>0.702</td><td>0.716</td><td>0.728</td><td>0.639</td><td>0.701</td><td>0.723</td><td>0.729</td></tr><tr><td>Qwen3-VL-235B</td><td>0.646</td><td>0.691</td><td>0.704</td><td>0.742</td><td>0.652</td><td>0.686</td><td>0.718</td><td>0.753</td></tr><tr><td colspan="9"></td></tr><tr><td rowspan="3">Backbone</td><td colspan="8">F1-score (↑)</td></tr><tr><td colspan="4">IPLoc</td><td colspan="4">IPLoc-ID</td></tr><tr><td>N=1</td><td>N=2</td><td>N=4</td><td>N=8</td><td>N=1</td><td>N=2</td><td>N=4</td><td>N=8</td></tr><tr><td>LLaVA1.5-7B</td><td>0.664</td><td>0.667</td><td>0.667</td><td>0.650</td><td>0.570</td><td>0.453</td><td>0.523</td><td>0.611</td></tr><tr><td>Gemma3-12B</td><td>0.667</td><td>0.666</td><td>0.666</td><td>0.666</td><td>0.929</td><td>0.939</td><td>0.920</td><td>0.946</td></tr><tr><td>Qwen2-VL-7B</td><td>0.667</td><td>0.666</td><td>0.667</td><td>0.667</td><td>0.943</td><td>0.963</td><td>0.973</td><td>0.985</td></tr><tr><td>Qwen3-VL-8B</td><td>0.667</td><td>0.667</td><td>0.667</td><td>0.667</td><td>0.924</td><td>0.973</td><td>0.982</td><td>0.993</td></tr><tr><td>Qwen3-VL-32B</td><td>0.668</td><td>0.667</td><td>0.667</td><td>0.667</td><td>0.950</td><td>0.968</td><td>0.985</td><td>0.996</td></tr><tr><td>Qwen3-VL-235B</td><td>0.665</td><td>0.667</td><td>0.667</td><td>0.667</td><td>0.956</td><td>0.967</td><td>0.982</td><td>0.986</td></tr></table>

## 4.3. Ablation Studies

## 4.3.1. Unified objective vs. two-stage training

The proposed IPLoc-ID uses the unified objective in Eq. (17) to generate the complete output sequence in Eq. (10), $y = \langle B \rangle \langle Q \rangle \langle A \rangle$ . A natural question is whether this framework is merely an additional identification stage built upon a pretrained IPLoc model. To answer this question, we compare IPLoc, IPLoc-ID, and a two-stage training strategy in Figure 3. Two-stage training first trains the model for BBOX localization and then re-trains it only for identification, with the second-stage target sequence $\langle Q \rangle \langle A ^ { * } ( x ) \rangle$ ⟩.

Figure 3 shows the mIoU and F1-score curves during training. For the Twostage model, only the second-stage training process starting from the pretrained IPLoc model is shown. IPLoc improves mIoU but not F1-score, because it has no identification objective. The Two-stage model improves F1-score, but its mIoU rapidly decreases, indicating catastrophic forgetting [47, 48] of localization ability. In contrast, IPLoc-ID improves both mIoU and F1-score simultaneously. These results show that IPLoc-ID is not merely an additional identification stage, but a unified framework for jointly learning localization and identification.

Table 4: [Unified objective vs. conditional branching] mIoU and F1-score on the 1-shot LaSOT test set for backbones under diferent training frameworks.

<table><tr><td rowspan="2">Backbone</td><td colspan="3">mIoU (↑)</td><td colspan="3">F1-score (↑)</td></tr><tr><td>IPLoc</td><td>IPLoc-ID</td><td>Branch</td><td>IPLoc</td><td>IPLoc-ID</td><td>Branch</td></tr><tr><td>Qwen2-VL-7B</td><td>0.501</td><td>0.503</td><td>0.446</td><td>0.667</td><td>0.943</td><td>0.937</td></tr><tr><td>Qwen3-VL-8B</td><td>0.632</td><td>0.637</td><td>0.595</td><td>0.667</td><td>0.924</td><td>0.955</td></tr><tr><td>Qwen3-VL-32B</td><td>0.644</td><td>0.639</td><td>0.620</td><td>0.670</td><td>0.950</td><td>0.952</td></tr></table>

Table 5: [Self-posed queries used in ablation] Query texts used for the self-posed query ablation study.

<table><tr><td>Self-posed query</td><td>Prompt texts</td></tr><tr><td>Query #1</td><td>Do all these boxes have the same object?</td></tr><tr><td>Query #2</td><td>Do all these boxes contain the same object instance?</td></tr><tr><td>Query #3</td><td>Is there a single shared object across all these boxes?</td></tr><tr><td>Query #4</td><td>Do all these boxes enclose the same object?</td></tr></table>

Table 6: [Ablation on self-posed query] mIoU and F1-score on the LaSOT test set for IPLoc-ID with diferent self-posed queries.

<table><tr><td rowspan="2">Self-posed query</td><td colspan="4">mIoU (↑)</td><td colspan="4">F1-score (↑)</td></tr><tr><td>#1</td><td>#2</td><td>#3</td><td>#4</td><td>#1</td><td>#2</td><td>#3</td><td>#4</td></tr><tr><td>Qwen2-VL-7B + IPLoc-ID</td><td>0.503</td><td>0.489</td><td>0.489</td><td>0.490</td><td>0.943</td><td>0.944</td><td>0.944</td><td>0.940</td></tr><tr><td>Qwen3-VL-8B + IPLoc-ID</td><td>0.637</td><td>0.623</td><td>0.623</td><td>0.639</td><td>0.924</td><td>0.898</td><td>0.944</td><td>0.942</td></tr><tr><td>Qwen3-VL-32B + IPLoc-ID</td><td>0.639</td><td>0.668</td><td>0.657</td><td>0.645</td><td>0.950</td><td>0.966</td><td>0.965</td><td>0.952</td></tr></table>

## 4.3.2. Unified objective vs. conditional branching

We compare IPLoc-ID with another training strategy that directly generates diferent responses for positive and negative query images. Given the same input sequence x, this baseline learns a conditionally branched response:

$$
y _ {\mathrm{branch}} = \left\{ \begin{array}{l l} \langle B \rangle , & \text {if} \delta (x) = 1, \\ \langle A \rangle , & \text {if} \delta (x) = 0, \end{array} \right.\tag{21}
$$

where $\delta ( x ) = 1$ indicates that the query image contains the reference object instance, and $\delta ( x ) ~ = ~ 0$ otherwise. In our implementation, we use $\langle A \rangle =$ “Not found.” as the negative response and refer to this variant as the Conditional Branching baseline.

This formulation collapses bounding-box prediction and identification into a single conditional generation step. Although straightforward, it requires the model to decide whether to localize or reject the query image before generating the output. Moreover, generating a fixed negative response is easier than generating continuous-valued bounding-box coordinates, which tends to bias the model toward negative responses. As shown in Table 4, this results in degraded mIoU despite high F1-scores. In contrast, IPLoc-ID first generates a reference-conditioned candidate BBOX, then performs identification through the self-posed query. This sequential decomposition enables identification without sacrificing box localization accuracy, as shown in Table 4.

## 4.3.3. Ablation on self-posed query

We ablate the concrete wording of the self-posed query introduced in Sec tion 3.3. The four query texts compared in this experiment are listed in Table 5. They cover generic object consistency, instance-level identity, global set consistency, and spatial enclosure.

Table 6 reports the mIoU and F1-score obtained with these four self-posed queries. The results show that IPLoc-ID is robust to the specific wording of ⟨Q⟩. This suggests that, during fine-tuning, the model learns both to generate the self-posed query and to use it as a cue for the subsequent answer component ⟨A⟩.

Table 7: [Ablation on loss terms with label noise] mIoU and F1-score on the LaSOT test set for diferent backbones. The four columns in each metric block correspond to diferent combinations of loss components.

<table><tr><td></td><td colspan="4">mIoU (↑)</td><td colspan="4">F1-score (↑)</td></tr><tr><td>box localization</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td></tr><tr><td>+ label noise</td><td></td><td>✓</td><td></td><td>✓</td><td></td><td>✓</td><td></td><td>✓</td></tr><tr><td>+ identification</td><td></td><td></td><td>✓</td><td>✓</td><td></td><td></td><td>✓</td><td>✓</td></tr><tr><td>Qwen2-VL-7B</td><td>0.495</td><td>0.501</td><td>0.491</td><td>0.503</td><td>0.666</td><td>0.667</td><td>0.939</td><td>0.943</td></tr><tr><td>Qwen3-VL-8B</td><td>0.595</td><td>0.632</td><td>0.601</td><td>0.637</td><td>0.667</td><td>0.667</td><td>0.933</td><td>0.924</td></tr><tr><td>Qwen3-VL-32B</td><td>0.631</td><td>0.650</td><td>0.637</td><td>0.639</td><td>0.667</td><td>0.668</td><td>0.964</td><td>0.950</td></tr><tr><td></td><td colspan="2">(IPLoc)</td><td colspan="2">(Ours)</td><td colspan="2">(IPLoc)</td><td colspan="2">(Ours)</td></tr></table>

In this paper, we use Query #1 as the recommended implementation because it is the most basic formulation and shows stable performance.

## 4.3.4. Ablation on loss terms with label noise

The proposed IPLoc-ID consists of three components: the box localization term, pseudo-label-based label noise inherited from IPLoc, and the identification term. Table 7 analyzes diferent combinations of these components. The first and second columns correspond to IPLoc without and with label noise, respectively. The third column removes label noise from IPLoc-ID, and the fourth column shows the full IPLoc-ID. The results reconfirm that label noise improves mIoU not only for Qwen2 but also for the Qwen3 series, and we therefore use pseudo-labeling in our final models. More importantly, the identification term consistently improves F1-score, regardless of the use of label noise.

## 4.4. Comprehensive Comparison with State-of-the-Art Methods

We now present the main experimental results on LaSOT, PDM, GOT-10K, and VastTrack in Tables 8–11. In these tables, the best value for each N-shot setting within each block is highlighted in bold, while the best value within each block is underlined. We compare three variants for each backbone: the VLM with instruction prompting, IPLoc, and IPLoc-ID. For LLaVA1.5-7B and Gemma3-12B, the instruction-prompting baseline is denoted by adding “+ prompt”. For brevity, we omit “+ prompt” for the Qwen series and denote the prompted backbone simply by the model name. For Qwen3-VL-235B, we report a single independent trial due to its high computational cost. For externally prompted VLM baselines, we use a structured two-step instruction prompt selected from a preliminary prompt pretest. The details of this pretest are provided in Appendix A.1.

We also include the following related algorithms. Grounding-DINO [2] is used as a general-purpose object detector. Florence-2 [49] is used as a multi-task VLM with OD prompting. Both use only the target image and label, so we report them only under the 1-shot setting. VFM [13] is used as a state-of-the-art FSOD baseline with all N-shot reference data as support data. No-Time-To-Train [14] constructs a memory bank from the reference data for each test case and applies it to the target image. LLaVA1.5-7B [24] with instruction prompting is included as an early conversational VLM baseline. IPLoc 7B (oficial) [6] is the oficial Qwen2-VL-7B-based IPLoc model.

The results on the LaSOT test set in Table 8 evaluate generalization to unseen classes within the same domain, as described in Section 3.5. In this setting, IPLoc-ID maintains BBOX localization accuracy comparable to IPLoc in terms of mIoU, while substantially improving F1-score. Recall that an F1- score of approximately 0.667 corresponds to an all-positive response under a balanced positive/negative test set. Thus, the F1-scores of IPLoc and several localization-only baselines indicate limited instance-level identification capability. In contrast, IPLoc-ID consistently achieves high F1-scores, demonstrating that it efectively rejects negative query images.

The results on PDM and GOT-10K in Tables 9 and 10 evaluate generalization to unseen domains. In terms of mIoU, IPLoc and IPLoc-ID achieve satisfactory localization performance, although No-Time-To-Train shows particularly strong mIoU on PDM. This indicates that IPLoc-based methods can benefit from the general visual reasoning ability of large-scale pretrained VLMs. For F1-score, VFM achieves high values on GOT-10K, likely because the negative examples are out-of-class images, making the task closer to category-level FSOD. The F1-scores of IPLoc remain close to the all-positive baseline, indicating that IPLoc tends to return positive detections even for out-of-class negative examples. In contrast, IPLoc-ID achieves the highest F1-scores on these two sets, demonstrating strong identification ability under unseen-domain settings.

The VastTrack results in Table 11 are particularly important because the negative examples are in-class distractors. This setting requires instance-level identification and evaluates unseen-domain generalization without fine-tuning on that domain. Even under this challenging setting, IPLoc-ID shows consistent improvements in F1-score while maintaining competitive mIoU.

Regarding the reference algorithms, LLaVA1.5-7B with instruction prompting shows substantially lower mIoU than the other algorithms. This is because early VLMs such as LLaVA1.5-7B often ignore localization-oriented instructions and generate image captions or free-form descriptions, as also reported in the original IPLoc study [6]. The oficial IPLoc 7B model shows behavior similar to our reproduced Qwen2-VL-7B + IPLoc model across the tested datasets. This illustrates that the original IPLoc tends to produce false-positive detections on negative query images and supports the validity of our reproduced IPLoc implementation. VLMs with instruction prompting can solve the POIL task to some extent, especially with stronger backbone models. However, IPLoc-ID achieves better overall performance in both mIoU and F1-score.

Importantly, these results across datasets and backbone models empirically support the formulations in Section 3. The localization-only IPLoc variants remain close to the all-positive F1-score baseline, consistent with Eq. (9): IPLoc tends to return an element of B even for negative query images, whereas the ideal POIL mapping in Eq. (4) requires rejection. In contrast, IPLoc-ID substantially improves F1-score while preserving mIoU, showing that the interpreted prediction in Eq. (20) better approximates the ideal mapping in Eq. (4). Thus, the results support the intended transition from localization-only prediction to identificationaware personalized object localization.

Table 8: [Quantitative comparison on the LaSOT test set] mIoU and F1-score under diferent N-shot settings for various algorithms.

<table><tr><td rowspan="2">Algorithms</td><td colspan="4">mIoU (↑)</td><td colspan="4">F1-score (↑)</td></tr><tr><td>N=1</td><td>N=2</td><td>N=4</td><td>N=8</td><td>N=1</td><td>N=2</td><td>N=4</td><td>N=8</td></tr><tr><td>(OD) Grounding-DINO</td><td>0.222</td><td>-</td><td>-</td><td>-</td><td>0.416</td><td>-</td><td>-</td><td>-</td></tr><tr><td>(OD) Florence-2</td><td>0.306</td><td>-</td><td>-</td><td>-</td><td>0.511</td><td>-</td><td>-</td><td>-</td></tr><tr><td>(FSOD) VFM</td><td>0.605</td><td>0.593</td><td>0.617</td><td>0.601</td><td>0.656</td><td>0.665</td><td>0.662</td><td>0.665</td></tr><tr><td>(FSOD) No-Time-To-Train</td><td>0.644</td><td>0.627</td><td>0.618</td><td>0.617</td><td>0.663</td><td>0.657</td><td>0.660</td><td>0.657</td></tr><tr><td>LLaVA1.5-7B + prompt</td><td>0.005</td><td>0.159</td><td>0.111</td><td>0.000</td><td>0.065</td><td>0.624</td><td>0.524</td><td>0.014</td></tr><tr><td>IPLoc 7B (official)</td><td>0.515</td><td>0.529</td><td>0.541</td><td>0.527</td><td>0.652</td><td>0.663</td><td>0.663</td><td>0.659</td></tr><tr><td>Gemma3-12B (+ prompt)</td><td>0.139</td><td>0.185</td><td>0.209</td><td>0.140</td><td>0.869</td><td>0.843</td><td>0.795</td><td>0.535</td></tr><tr><td>Gemma3-12B + IPLoc</td><td>0.377</td><td>0.395</td><td>0.406</td><td>0.444</td><td>0.667</td><td>0.666</td><td>0.666</td><td>0.666</td></tr><tr><td>Gemma3-12B + IPLoc-ID</td><td>0.382</td><td>0.442</td><td>0.422</td><td>0.450</td><td>0.929</td><td>0.939</td><td>0.920</td><td>0.946</td></tr><tr><td>Qwen2-VL-7B</td><td>0.247</td><td>0.306</td><td>0.297</td><td>0.319</td><td>0.584</td><td>0.489</td><td>0.426</td><td>0.488</td></tr><tr><td>Qwen2-VL-7B + IPLoc</td><td>0.501</td><td>0.536</td><td>0.561</td><td>0.580</td><td>0.667</td><td>0.666</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen2-VL-7B + IPLoc-ID</td><td>0.503</td><td>0.535</td><td>0.571</td><td>0.580</td><td>0.943</td><td>0.963</td><td>0.973</td><td>0.985</td></tr><tr><td>Qwen3-VL-8B</td><td>0.511</td><td>0.558</td><td>0.552</td><td>0.559</td><td>0.746</td><td>0.779</td><td>0.810</td><td>0.771</td></tr><tr><td>Qwen3-VL-8B + IPLoc</td><td>0.632</td><td>0.675</td><td>0.694</td><td>0.711</td><td>0.667</td><td>0.667</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen3-VL-8B + IPLoc-ID</td><td>0.637</td><td>0.673</td><td>0.698</td><td>0.714</td><td>0.924</td><td>0.973</td><td>0.982</td><td>0.993</td></tr><tr><td>Qwen3-VL-32B</td><td>0.541</td><td>0.561</td><td>0.572</td><td>0.585</td><td>0.835</td><td>0.889</td><td>0.883</td><td>0.927</td></tr><tr><td>Qwen3-VL-32B + IPLoc</td><td>0.650</td><td>0.702</td><td>0.716</td><td>0.728</td><td>0.668</td><td>0.667</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen3-VL-32B + IPLoc-ID</td><td>0.639</td><td>0.701</td><td>0.723</td><td>0.729</td><td>0.950</td><td>0.968</td><td>0.985</td><td>0.996</td></tr><tr><td>Qwen3-VL-235B</td><td>0.430</td><td>0.561</td><td>0.584</td><td>0.588</td><td>0.866</td><td>0.840</td><td>0.884</td><td>0.935</td></tr><tr><td>Qwen3-VL-235B + IPLoc</td><td>0.646</td><td>0.691</td><td>0.704</td><td>0.742</td><td>0.665</td><td>0.667</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen3-VL-235B + IPLoc-ID</td><td>0.652</td><td>0.686</td><td>0.718</td><td>0.753</td><td>0.956</td><td>0.967</td><td>0.982</td><td>0.986</td></tr></table>

Table 9: [Quantitative comparison on PDM] mIoU and F1-score under diferent N-shot settings for various algorithms.

<table><tr><td rowspan="2">Algorithms</td><td colspan="2">mIoU (↑)</td><td colspan="2">F1-score (↑)</td></tr><tr><td>N=1</td><td>N=2</td><td>N=1</td><td>N=2</td></tr><tr><td>(OD) Grounding-DINO</td><td>0.213</td><td>-</td><td>0.498</td><td>-</td></tr><tr><td>(OD) Florence-2</td><td>0.174</td><td>-</td><td>0.467</td><td>-</td></tr><tr><td>(FSOD) VFM</td><td>0.264</td><td>0.287</td><td>0.658</td><td>0.681</td></tr><tr><td>(FSOD) No-Time-To-Train</td><td>0.556</td><td>0.621</td><td>0.636</td><td>0.655</td></tr><tr><td>LLaVA1.5-7B + prompt</td><td>0.009</td><td>0.122</td><td>0.100</td><td>0.644</td></tr><tr><td>IPLoc 7B (official)</td><td>0.315</td><td>0.343</td><td>0.722</td><td>0.713</td></tr><tr><td>Gemma3-12B (+ prompt)</td><td>0.117</td><td>0.142</td><td>0.760</td><td>0.663</td></tr><tr><td>Gemma3-12B + IPLoc</td><td>0.134</td><td>0.177</td><td>0.667</td><td>0.666</td></tr><tr><td>Gemma3-12B + IPLoc-ID</td><td>0.134</td><td>0.201</td><td>0.932</td><td>0.959</td></tr><tr><td>Qwen2-VL-7B</td><td>0.204</td><td>0.229</td><td>0.380</td><td>0.455</td></tr><tr><td>Qwen2-VL-7B + IPLoc</td><td>0.318</td><td>0.367</td><td>0.666</td><td>0.667</td></tr><tr><td>Qwen2-VL-7B + IPLoc-ID</td><td>0.316</td><td>0.351</td><td>0.976</td><td>0.988</td></tr><tr><td>Qwen3-VL-8B</td><td>0.363</td><td>0.398</td><td>0.861</td><td>0.914</td></tr><tr><td>Qwen3-VL-8B + IPLoc</td><td>0.436</td><td>0.487</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen3-VL-8B + IPLoc-ID</td><td>0.439</td><td>0.487</td><td>0.941</td><td>0.987</td></tr><tr><td>Qwen3-VL-32B</td><td>0.391</td><td>0.440</td><td>0.699</td><td>0.654</td></tr><tr><td>Qwen3-VL-32B + IPLoc</td><td>0.437</td><td>0.473</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen3-VL-32B + IPLoc-ID</td><td>0.455</td><td>0.507</td><td>0.986</td><td>0.995</td></tr><tr><td>Qwen3-VL-235B</td><td>0.368</td><td>0.387</td><td>0.778</td><td>0.633</td></tr><tr><td>Qwen3-VL-235B + IPLoc</td><td>0.445</td><td>0.481</td><td>0.668</td><td>0.666</td></tr><tr><td>Qwen3-VL-235B + IPLoc-ID</td><td>0.445</td><td>0.536</td><td>0.970</td><td>0.976</td></tr></table>

Table 10: [Quantitative comparison on GOT-10K] mIoU and F1-score under diferent N-shot settings for various algorithms.

<table><tr><td rowspan="2">Algorithms</td><td colspan="4">mIoU (↑)</td><td colspan="4">F1-score (↑)</td></tr><tr><td>N=1</td><td>N=2</td><td>N=4</td><td>N=8</td><td>N=1</td><td>N=2</td><td>N=4</td><td>N=8</td></tr><tr><td>(OD) Grounding-DINO</td><td>0.012</td><td>-</td><td>-</td><td>-</td><td>0.054</td><td>-</td><td>-</td><td>-</td></tr><tr><td>(OD) Florence-2</td><td>0.039</td><td>-</td><td>-</td><td>-</td><td>0.115</td><td>-</td><td>-</td><td>-</td></tr><tr><td>(FSOD) VFM</td><td>0.680</td><td>0.717</td><td>0.736</td><td>0.764</td><td>0.942</td><td>0.946</td><td>0.946</td><td>0.960</td></tr><tr><td>(FSOD) No-Time-To-Train</td><td>0.762</td><td>0.768</td><td>0.769</td><td>0.769</td><td>0.672</td><td>0.670</td><td>0.672</td><td>0.670</td></tr><tr><td>LLaVA1.5-7B + prompt</td><td>0.000</td><td>0.139</td><td>0.082</td><td>0.000</td><td>0.000</td><td>0.529</td><td>0.410</td><td>0.043</td></tr><tr><td>IPLoc 7B (official)</td><td>0.481</td><td>0.501</td><td>0.516</td><td>0.587</td><td>0.675</td><td>0.677</td><td>0.668</td><td>0.668</td></tr><tr><td>Gemma3-12B (+ prompt)</td><td>0.201</td><td>0.198</td><td>0.234</td><td>0.295</td><td>0.966</td><td>0.922</td><td>0.899</td><td>0.751</td></tr><tr><td>Gemma3-12B + IPLoc</td><td>0.504</td><td>0.485</td><td>0.511</td><td>0.572</td><td>0.667</td><td>0.667</td><td>0.666</td><td>0.667</td></tr><tr><td>Gemma3-12B + IPLoc-ID</td><td>0.504</td><td>0.534</td><td>0.504</td><td>0.607</td><td>0.942</td><td>0.940</td><td>0.910</td><td>0.972</td></tr><tr><td>Qwen2-VL-7B</td><td>0.231</td><td>0.235</td><td>0.274</td><td>0.434</td><td>0.731</td><td>0.602</td><td>0.414</td><td>0.669</td></tr><tr><td>Qwen2-VL-7B + IPLoc</td><td>0.497</td><td>0.527</td><td>0.558</td><td>0.634</td><td>0.667</td><td>0.667</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen2-VL-7B + IPLoc-ID</td><td>0.496</td><td>0.532</td><td>0.570</td><td>0.643</td><td>0.970</td><td>0.949</td><td>0.944</td><td>0.997</td></tr><tr><td>Qwen3-VL-8B</td><td>0.667</td><td>0.690</td><td>0.649</td><td>0.676</td><td>0.967</td><td>0.983</td><td>0.989</td><td>0.985</td></tr><tr><td>Qwen3-VL-8B + IPLoc</td><td>0.763</td><td>0.771</td><td>0.786</td><td>0.836</td><td>0.667</td><td>0.667</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen3-VL-8B + IPLoc-ID</td><td>0.747</td><td>0.772</td><td>0.785</td><td>0.828</td><td>0.943</td><td>0.967</td><td>0.973</td><td>0.997</td></tr><tr><td>Qwen3-VL-32B</td><td>0.686</td><td>0.693</td><td>0.671</td><td>0.668</td><td>0.947</td><td>0.949</td><td>0.956</td><td>0.983</td></tr><tr><td>Qwen3-VL-32B + IPLoc</td><td>0.738</td><td>0.756</td><td>0.796</td><td>0.842</td><td>0.668</td><td>0.664</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen3-VL-32B + IPLoc-ID</td><td>0.738</td><td>0.742</td><td>0.777</td><td>0.854</td><td>0.993</td><td>0.986</td><td>0.982</td><td>0.997</td></tr><tr><td>Qwen3-VL-235B</td><td>0.616</td><td>0.671</td><td>0.625</td><td>0.737</td><td>0.951</td><td>0.916</td><td>0.915</td><td>0.929</td></tr><tr><td>Qwen3-VL-235B + IPLoc</td><td>0.736</td><td>0.785</td><td>0.806</td><td>0.860</td><td>0.667</td><td>0.667</td><td>0.668</td><td>0.667</td></tr><tr><td>Qwen3-VL-235B + IPLoc-ID</td><td>0.764</td><td>0.795</td><td>0.795</td><td>0.869</td><td>1.000</td><td>0.974</td><td>0.935</td><td>1.000</td></tr></table>

Table 11: [Quantitative comparison on VastTrack] mIoU and F1-score under diferent N-shot settings for various algorithms.

<table><tr><td rowspan="2">Algorithms</td><td colspan="4">mIoU (↑)</td><td colspan="4">F1-score (↑)</td></tr><tr><td>N=1</td><td>N=2</td><td>N=4</td><td>N=8</td><td>N=1</td><td>N=2</td><td>N=4</td><td>N=8</td></tr><tr><td>(OD) Grounding-DINO</td><td>0.003</td><td>-</td><td>-</td><td>-</td><td>0.030</td><td>-</td><td>-</td><td>-</td></tr><tr><td>(OD) Florence-2</td><td>0.026</td><td>-</td><td>-</td><td>-</td><td>0.101</td><td>-</td><td>-</td><td>-</td></tr><tr><td>(FSOD) VFM</td><td>0.400</td><td>0.413</td><td>0.440</td><td>0.473</td><td>0.690</td><td>0.694</td><td>0.712</td><td>0.723</td></tr><tr><td>(FSOD) No-Time-To-Train</td><td>0.500</td><td>0.512</td><td>0.524</td><td>0.530</td><td>0.646</td><td>0.648</td><td>0.650</td><td>0.650</td></tr><tr><td>LLaVA1.5-7B + prompt</td><td>0.000</td><td>0.108</td><td>0.100</td><td>0.000</td><td>0.010</td><td>0.554</td><td>0.474</td><td>0.005</td></tr><tr><td>IPLoc 7B (official)</td><td>0.284</td><td>0.316</td><td>0.333</td><td>0.427</td><td>0.660</td><td>0.664</td><td>0.662</td><td>0.663</td></tr><tr><td>Gemma3-12B (+ prompt)</td><td>0.154</td><td>0.161</td><td>0.216</td><td>0.289</td><td>0.784</td><td>0.785</td><td>0.755</td><td>0.629</td></tr><tr><td>Gemma3-12B + IPLoc</td><td>0.227</td><td>0.243</td><td>0.287</td><td>0.413</td><td>0.666</td><td>0.666</td><td>0.667</td><td>0.667</td></tr><tr><td>Gemma3-12B + IPLoc-ID</td><td>0.223</td><td>0.267</td><td>0.291</td><td>0.415</td><td>0.884</td><td>0.907</td><td>0.888</td><td>0.913</td></tr><tr><td>Qwen2-VL-7B</td><td>0.180</td><td>0.192</td><td>0.234</td><td>0.380</td><td>0.565</td><td>0.509</td><td>0.416</td><td>0.500</td></tr><tr><td>Qwen2-VL-7B + IPLoc</td><td>0.335</td><td>0.357</td><td>0.382</td><td>0.472</td><td>0.667</td><td>0.667</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen2-VL-7B + IPLoc-ID</td><td>0.329</td><td>0.349</td><td>0.378</td><td>0.471</td><td>0.906</td><td>0.937</td><td>0.953</td><td>0.975</td></tr><tr><td>Qwen3-VL-8B</td><td>0.359</td><td>0.378</td><td>0.387</td><td>0.465</td><td>0.706</td><td>0.745</td><td>0.761</td><td>0.741</td></tr><tr><td>Qwen3-VL-8B + IPLoc</td><td>0.429</td><td>0.451</td><td>0.477</td><td>0.578</td><td>0.667</td><td>0.667</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen3-VL-8B + IPLoc-ID</td><td>0.424</td><td>0.447</td><td>0.482</td><td>0.574</td><td>0.884</td><td>0.951</td><td>0.959</td><td>0.965</td></tr><tr><td>Qwen3-VL-32B</td><td>0.188</td><td>0.413</td><td>0.382</td><td>0.465</td><td>0.379</td><td>0.838</td><td>0.869</td><td>0.918</td></tr><tr><td>Qwen3-VL-32B + IPLoc</td><td>0.443</td><td>0.472</td><td>0.507</td><td>0.596</td><td>0.667</td><td>0.668</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen3-VL-32B + IPLoc-ID</td><td>0.437</td><td>0.465</td><td>0.508</td><td>0.615</td><td>0.928</td><td>0.958</td><td>0.951</td><td>0.973</td></tr><tr><td>Qwen3-VL-235B</td><td>0.326</td><td>0.358</td><td>0.378</td><td>0.502</td><td>0.802</td><td>0.783</td><td>0.725</td><td>0.726</td></tr><tr><td>Qwen3-VL-235B + IPLoc</td><td>0.427</td><td>0.456</td><td>0.506</td><td>0.618</td><td>0.667</td><td>0.667</td><td>0.667</td><td>0.667</td></tr><tr><td>Qwen3-VL-235B + IPLoc-ID</td><td>0.431</td><td>0.462</td><td>0.510</td><td>0.621</td><td>0.930</td><td>0.954</td><td>0.963</td><td>0.982</td></tr></table>

For qualitative comparison, Figure 1 visualizes representative examples on the LaSOT test set. The examples show that conventional OD/FSOD methods and localization-only IPLoc tend to produce false-positive detections on negative query images, whereas IPLoc-ID suppresses such false positives while preserving correct localization on positive query images. Additional qualitative comparisons between the baseline IPLoc and the proposed IPLoc-ID on all test datasets are provided in Appendix A.2.

## 5. Conclusion

In this paper, we generalized personalized object localization (POL) to personalized object identification and localization (POIL). Unlike localizationonly settings, POIL requires localizing the reference-conditioned object instance when it appears in the query image and rejecting the image otherwise. Thus, POIL combines reference-conditioned instance-level localization with negativequery rejection. For this task, we constructed POIL datasets from four public sources, including both positive and negative query images.

We proposed IPLoc-ID as an in-context algorithm for POIL. IPLoc-ID treats the BBOX generated by IPLoc as a candidate and verifies whether it corresponds to the reference object instance through a self-posed query and identification answer. This design connects the input context, BBOX candidate, self-posed query, and final identification response as a single autoregressive sequence. Through experiments, we demonstrated that IPLoc-ID substantially suppresses false-positive detections on negative query images while maintaining the localization performance of IPLoc. In particular, the results on in-class negative examples show that IPLoc-ID is more efective for instance-level identification than conventional OD, FSOD, and localization-only IPLoc.

The limitations of this study are as follows. First, similar to IPLoc, our setting focuses on a single object in each query image and does not address simultaneous localization and identification of multiple target objects. Second, inference is performed on individual images, and temporal consistency in videos or image sequences is not explicitly used. Thus, the current framework does not fully exploit temporal information and motion consistency, which are important for applications such as video grounding and object tracking.

For the broader research community, we expect the POIL formulation, customized datasets, evaluation protocol, and baseline comparisons introduced in this study to provide a useful foundation for future research on various personal ized vision tasks, including personalized recognition, retrieval, grounding, and tracking under realistic query settings.

As VLMs continue to advance rapidly, future work will extend IPLoc-ID to multi-object and video-level POIL tasks by further exploiting the multi object localization and temporal reasoning abilities of increasingly capable VLMs through the proposed reference-conditioned identification framework.

## Acknowledgment

This work was supported by the Korea government (MSIT): IITP-RS-2021- II211341, Artificial Intelligence Graduate School, Chung-Ang University and NRF-RS-2025-25462275.

## Data and code availability

This study uses publicly available source datasets, including LaSOT, PDM/BURST, GOT-10K, and VastTrack. We provide the inference code, dataset construction scripts, and minimal trained models at https: //github.com/kensuke-nakamura/iplocid. The training code and additional trained models will be made publicly available upon acceptance.

## References

[1] M. Minderer, A. Gritsenko, A. Stone, M. Neumann, D. Weissenborn, A. Dosovitskiy, A. Mahendran, A. Arnab, M. Dehghani, Z. Shen, et al., Sim ple open-vocabulary object detection, in: European conference on computer vision, Springer, 2022, pp. 728–755.

[2] S. Liu, Z. Zeng, T. Ren, F. Li, H. Zhang, J. Yang, Q. Jiang, C. Li, J. Yang, H. Su, et al., Grounding dino: Marrying dino with grounded pre-training for open-set object detection, in: European conference on computer vision, Springer, 2024, pp. 38–55.

[3] M. Köhler, M. Eisenbach, H.-M. Gross, Few-shot object detection: A comprehensive survey, IEEE transactions on neural networks and learning systems 35 (9) (2023) 11958–11978.

[4] Z. Xin, S. Chen, T. Wu, Y. Shao, W. Ding, X. You, Few-shot object detection: Research advances and challenges, Information Fusion 107 (2024) 102307.

[5] X. Wang, T. Huang, J. Gonzalez, T. Darrell, F. Yu, Frustratingly simple few-shot object detection, in: H. D. III, A. Singh (Eds.), Proceedings of the 37th International Conference on Machine Learning, Vol. 119 of Proceedings of Machine Learning Research, PMLR, 2020, pp. 9919–9928. URL https://proceedings.mlr.press/v119/wang20j.html

[6] S. Doveh, N. Shabtay, E. Schwartz, H. Kuehne, R. Giryes, R. Feris, L. Karlinsky, J. Glass, A. Arbelle, S. Ullman, et al., Teaching vlms to localize specific objects from in-context examples, in: Proceedings of the IEEE/CVF International Conference on Computer Vision, 2025, pp. 9572–9582.

[7] B. Sun, B. Li, S. Cai, Y. Yuan, C. Zhang, Fsce: Few-shot object detection via contrastive proposal encoding, in: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, 2021, pp. 7352–7362.

[8] L. Qiao, Y. Zhao, Z. Li, X. Qiu, J. Wu, C. Zhang, Defrcn: Decoupled faster r-cnn for few-shot object detection, in: Proceedings of the IEEE/CVF international conference on computer vision, 2021, pp. 8681–8690.

[9] X. Yan, Z. Chen, A. Xu, X. Wang, X. Liang, L. Lin, Meta r-cnn: Towards general solver for instance-level low-shot learning, in: Proceedings of the IEEE/CVF international conference on computer vision, 2019, pp. 9577– 9586.

[10] G. Han, J. Ma, S. Huang, L. Chen, S.-F. Chang, Few-shot object detection with fully cross-transformer, in: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, 2022, pp. 5321–5330.

[11] X. Zhang, Y. Liu, Y. Wang, A. Boularias, Detect everything with few examples, in: Proceedings of The 8th Conference on Robot Learning, Vol. 270 of Proceedings of Machine Learning Research, PMLR, 2024, pp. 3986– 4004.

[12] X. Yu, Y. Sha, L. Liu, X. Shen, D. Yang, A closer look at cross-domain few-shot object detection: Fine-tuning matters and parallel decoder helps, in: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2026.

[13] C.-B. Feng, Y. Sha, L. Liu, Y. Yu, C. M. Vong, X. Yu, X. Shen, Few-shot object detection with vision foundation models and graph difusion, in: The Fourteenth International Conference on Learning Representations, 2026.

[14] M. Espinosa, C. Yang, L. Ericsson, S. McDonagh, E. J. Crowley, No time to train! training-free reference-based instance segmentation, arXiv preprint arXiv:2507.02798 (2025).

[15] B. Psomas, G. Retsinas, N. Efthymiadis, P. Filntisis, Y. Avrithis, P. Maragos, O. Chum, G. Tolias, Instance-level composed image retrieval, in: The Thirtyninth Annual Conference on Neural Information Processing Systems, 2025.

[16] X. Hao, K. Zhu, H. Guo, H. Guo, N. Jiang, Q. Lu, M. Tang, J. Wang, Referring expression instance retrieval and a strong end-to-end baseline, in: Proceedings of the 33rd ACM International Conference on Multimedia, 2025, pp. 4464–4473.

[17] Y. Ren, B. Li, C. Zhang, Y. Zhang, B. Yin, Few-shot object localization, arXiv preprint arXiv:2403.12466 (2024).

[18] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal, G. Sastry, A. Askell, P. Mishkin, J. Clark, et al., Learning transferable visual models from natural language supervision, in: International conference on machine learning, PmLR, 2021, pp. 8748–8763.

[19] M. Cherti, R. Beaumont, R. Wightman, M. Wortsman, G. Ilharco, C. Gordon, C. Schuhmann, L. Schmidt, J. Jitsev, Reproducible scaling laws for contrastive language-image learning, in: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, 2023, pp. 2818–2829.

[20] J. Li, D. Li, C. Xiong, S. Hoi, Blip: Bootstrapping language-image pretraining for unified vision-language understanding and generation, in: International conference on machine learning, PMLR, 2022, pp. 12888–12900.

[21] J. Li, D. Li, S. Savarese, S. Hoi, Blip-2: Bootstrapping language-image pre-training with frozen image encoders and large language models, in: International conference on machine learning, PMLR, 2023, pp. 19730– 19742.

[22] N. Ravi, V. Gabeur, Y.-T. Hu, R. Hu, C. Ryali, T. Ma, H. Khedr, R. Rädle, C. Rolland, L. Gustafson, et al., Sam 2: Segment anything in images and videos, in: International Conference on Learning Representations, Vol. 2025, 2025, pp. 28085–28128.

[23] M. Oquab, T. Darcet, T. Moutakanni, H. Vo, M. Szafraniec, V. Khalidov, P. Fernandez, D. Haziza, F. Massa, A. El-Nouby, et al., Dinov2: Learning robust visual features without supervision, arXiv preprint arXiv:2304.07193 (2023).

[24] H. Liu, C. Li, Q. Wu, Y. J. Lee, Visual instruction tuning, Advances in neural information processing systems 36 (2023) 34892–34916.

[25] G. Team, A. Kamath, J. Ferret, S. Pathak, N. Vieillard, R. Merhej, S. Perrin, T. Matejovicova, A. Ramé, M. Rivière, et al., Gemma 3 technical report, arXiv preprint arXiv:2503.19786 (2025).

[26] P. Wang, S. Bai, S. Tan, S. Wang, Z. Fan, J. Bai, K. Chen, X. Liu, J. Wang, W. Ge, et al., Qwen2-vl: Enhancing vision-language model’s perception of the world at any resolution, arXiv preprint arXiv:2409.12191 (2024).

[27] S. Bai, Y. Cai, R. Chen, K. Chen, X. Chen, Z. Cheng, L. Deng, W. Ding, C. Gao, C. Ge, et al., Qwen3-vl technical report, arXiv preprint arXiv:2511.21631 (2025).

[28] H. Zhang, H. Li, F. Li, T. Ren, X. Zou, S. Liu, S. Huang, J. Gao, Leizhang, C. Li, et al., Llava-grounding: Grounded visual chat with large multimodal models, in: European Conference on Computer Vision, Springer, 2024, pp. 19–35.

[29] Y. Yao, Q. Yang, H. Zhong, J. Wei, Y. Men, S. Bai, M. Cui, Z. Yang, Qwen3- vl-seg: Unlocking open-world referring segmentation with vision-language grounding, arXiv preprint arXiv:2605.07141 (2026).

[30] O. Press, M. Zhang, S. Min, L. Schmidt, N. A. Smith, M. Lewis, Measuring and narrowing the compositionality gap in language models, in: Findings of the Association for Computational Linguistics: EMNLP 2023, 2023, pp. 5687–5711.

[31] J. Qi, Z. Xu, Y. Shen, M. Liu, D. Jin, Q. Wang, L. Huang, The art of socratic questioning: Recursive thinking with large language models, in: Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, 2023, pp. 4177–4199.

[32] G. Sun, C. Qin, J. Wang, Z. Chen, R. Xu, Z. Tao, Sq-llava: Self-questioning for large vision-language assistant, in: European Conference on Computer Vision, Springer, 2024, pp. 156–172.

[33] A. Prasad, E. Stengel-Eskin, M. Bansal, Rephrase, augment, reason: Visual grounding of questions for vision-language models, in: International Conference on Learning Representations, 2024.

[34] S. Min, M. Lewis, L. Zettlemoyer, H. Hajishirzi, Metaicl: Learning to learn in context, in: Proceedings of the 2022 conference of the North American chapter of the Association for Computational Linguistics: Human Language Technologies, 2022, pp. 2791–2809.

[35] M. Monajatipoor, L. H. Li, M. Rouhsedaghat, L. Yang, K.-W. Chang, Metavl: Transferring in-context learning ability from language models to vision-language models, in: Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers), 2023, pp. 495–508.

[36] K. P. Yu, Z. Zhang, F. Hu, S. Storks, J. Chai, Eliciting in-context learning in vision-language models for videos through curated data distributional properties, in: Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, 2024, pp. 20416–20431.

[37] D. Sheng, D. Chen, Z. Tan, Q. Liu, Q. Chu, J. Bao, T. Gong, B. Liu, S. Xu, N. Yu, Towards more unified in-context visual understanding, in: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 13362–13372.

[38] M. Everingham, L. Van Gool, C. K. Williams, J. Winn, A. Zisserman, The pascal visual object classes (voc) challenge, International journal of computer vision 88 (2) (2010) 303–338.

[39] T.-Y. Lin, M. Maire, S. Belongie, J. Hays, P. Perona, D. Ramanan, P. Dollár, C. L. Zitnick, Microsoft coco: Common objects in context, in: European conference on computer vision, Springer, 2014, pp. 740–755.

[40] D. M. W. Powers, Evaluation: From precision, recall and f-measure to roc, informedness, markedness and correlation, Journal of Machine Learning Technologies 2 (1) (2011) 37–63.

[41] E. J. Hu, Y. Shen, P. Wallis, Z. Allen-Zhu, Y. Li, S. Wang, L. Wang, W. Chen, LoRA: Low-rank adaptation of large language models, in: International Conference on Learning Representations, 2022.

[42] H. Fan, L. Lin, F. Yang, P. Chu, G. Deng, S. Yu, H. Bai, Y. Xu, C. Liao, H. Ling, Lasot: A high-quality benchmark for large-scale single object tracking, in: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, 2019, pp. 5374–5383.

[43] D. Samuel, R. Ben-Ari, M. Levy, N. Darshan, G. Chechik, Where’s waldo: Difusion features for personalized segmentation and retrieval, Advances in Neural Information Processing Systems 37 (2024) 128160–128181.

[44] L. Huang, X. Zhao, K. Huang, Got-10k: A large high-diversity benchmark for generic object tracking in the wild, IEEE transactions on pattern analysis and machine intelligence 43 (5) (2019) 1562–1577.

[45] L. Peng, J. Gao, X. Liu, W. Li, S. Dong, Z. Zhang, H. Fan, L. Zhang, Vasttrack: Vast category visual object tracking, Advances in Neural Information Processing Systems 37 (2024) 130797–130818.

[46] C. Riquelme, J. Puigcerver, B. Mustafa, M. Neumann, R. Jenatton, A. Su sano Pinto, D. Keysers, N. Houlsby, Scaling vision with sparse mixture of experts, Advances in Neural Information Processing Systems 34 (2021) 8583–8595.

[47] M. McCloskey, N. J. Cohen, Catastrophic interference in connectionist networks: The sequential learning problem, Psychology of Learning and Motivation 24 (1989) 109–165. doi:10.1016/S0079-7421(08)60536-8.

[48] J. Kirkpatrick, R. Pascanu, N. Rabinowitz, J. Veness, G. Desjardins, A. A. Rusu, K. Milan, J. Quan, T. Ramalho, A. Grabska-Barwinska, et al., Overcoming catastrophic forgetting in neural networks, Proceed ings of the National Academy of Sciences 114 (13) (2017) 3521–3526. doi:10.1073/pnas.1611835114.

[49] B. Xiao, H. Wu, W. Xu, X. Dai, H. Hu, Y. Lu, M. Zeng, C. Liu, L. Yuan, Florence-2: Advancing a unified representation for a variety of vision tasks, in: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 4818–4829.

## Appendix A. Additional Experimental Results

## Appendix A.1. Pretest on instruction prompts

The proposed IPLoc-ID is designed for in-context inference without updating the model on test data. As an auxiliary analysis, we conducted a pretest on instruction prompt design for externally prompted VLMs. We compared four prompts, whose concrete texts are shown in Figure A.1. Prompt #1 is a two-line explicit format that specifies both the bounding box and identity response; Prompt #2 is a compact one-line format of the form [x1,y1,x2,y2], YES/NO; Prompt #3 is a structured two-step reasoning format that guides localization and identity verification; and Prompt #4 is a minimal-constraint format. Table A.1 reports the results on the 1-shot LaSOT test set. Based on these results, we adopt Prompt #3 for externally prompted VLMs in the comprehensive comparison.

Table A.1: [Pretest on instruction prompts] mIoU and F1-score on the 1-shot LaSOT test set for VLMs with diferent instruction prompts (#1–#4).

<table><tr><td rowspan="2">Instruction prompt</td><td colspan="4">mIoU (↑)</td><td colspan="4">F1-score (↑)</td></tr><tr><td>#1</td><td>#2</td><td>#3</td><td>#4</td><td>#1</td><td>#2</td><td>#3</td><td>#4</td></tr><tr><td>Gemma-3-12B + prompt</td><td>0.146</td><td>0.135</td><td>0.139</td><td>0.154</td><td>0.675</td><td>0.661</td><td>0.869</td><td>0.667</td></tr><tr><td>Qwen2-VL-7B + prompt</td><td>0.226</td><td>0.167</td><td>0.247</td><td>0.211</td><td>0.650</td><td>0.655</td><td>0.584</td><td>0.667</td></tr><tr><td>Qwen3-VL-8B + prompt</td><td>0.503</td><td>0.492</td><td>0.511</td><td>0.456</td><td>0.800</td><td>0.777</td><td>0.746</td><td>0.669</td></tr><tr><td>Qwen3-VL-32B + prompt</td><td>0.534</td><td>0.529</td><td>0.541</td><td>0.535</td><td>0.875</td><td>0.839</td><td>0.835</td><td>0.639</td></tr></table>

## Appendix A.2. Additional qualitative examples

Figures A.2, A.3, A.4, and A.5 show additional qualitative comparisons between IPLoc and IPLoc-ID using the Qwen3-VL-32B backbone. Each 1-shot example consists of a reference image, a positive query image, and a negative query image. The red BBOX denotes the reference annotation; in positive queries, blue and green BBOXes denote the ground truth and prediction, respectively; in negative queries, magenta denotes a false-positive detection. These examples further illustrate that IPLoc-ID localizes the target object in positive queries while suppressing false positives in negative queries.

![](images/3adaefdfba994d4aa9b2ec16d6da12984b3b1baaa9c21caeb46d331465155b99.jpg)  
Figure A.1: [Instruction prompts for general VLMs] Concrete instruction prompts (#1–#4) used for joint box localization and identity verification in the prompt pretest.

reference  
positive image  
![](images/126b8506c6f9e713442fef4a1a2139eff0d93d2a06c5d3d9985b65eedcdffd92.jpg)  
negative image  
(1) IPLoc

reference  
positive image  
negative image  
![](images/4db604212dc87349793318f633d7ad43e91edeffe8db63aa9ce153f0defa719a.jpg)  
(2) IPLoc-ID  
Figure A.2: [Qualitative comparison on the LaSOT test set] Reference (red), true positive (green) and false-positive (magenta) boxes using IPLoc and IPLoc-ID.

reference  
positive image  
negative image  
![](images/d93aaa0de9290f23e7e67280add97526945c3618b70251b451508160343e220e.jpg)  
(1) IPLoc

reference  
positive image  
negative image  
![](images/5e484584b828897c18b8d464333fbb4fd4457dc0816cbeb1ad3603bb8495ff7a.jpg)  
(2) IPLoc-ID  
Figure A.3: [Qualitative comparison on PDM] Reference (red), true-positive (green) and false-positive (magenta) boxes using IPLoc and IPLoc-ID.

reference  
positive image  
![](images/4a60dd848de24966d68a06e80b12ef964f15c37a7693c62e365591af336bd7c6.jpg)  
negative image  
(1) IPLoc

reference  
positive image  
negative image  
![](images/0f5d520fad13205b3cd8abae2aca52e2d3564a4d2ed1833e5bd83bac585558d8.jpg)  
(2) IPLoc-ID  
Figure A.4: [Qualitative comparison on GOT-10K] Reference (red), true-positive (green) and false-positive (magenta) boxes using IPLoc and IPLoc-ID.

reference  
positive image  
negative image  
![](images/245443d851108600eb0af4f01c92ba32c22c478d62fa3e2c8254f8f40f1f408d.jpg)  
(1) IPLoc

reference  
positive image  
negative image  
![](images/2184b617248d651206cdf3f0eeaedd3c586390af6e899ff33f1aa098442d0888.jpg)  
(2) IPLoc-ID  
Figure A.5: [Qualitative comparison on VastTrack] Reference (red), true-positive (green) and false-positive (magenta) boxes using IPLoc and IPLoc-ID.