# Evidence-RL: Towards Evidence-intensive Visual Reasoning

Haojie Huang<sup>1,2,\*</sup> Xinlei Yu<sup>1,\*</sup> Chengming Xu<sup>3,\*</sup> Zhangquan Chen<sup>4</sup> Cheng Yang<sup>5</sup> Qingdong He<sup>5</sup> Yu Yang<sup>2</sup> Jiangning Zhang<sup>2</sup> Xiaobin Hu<sup>1,†</sup>

greatesthhj@zju.edu.cn ben0xiaobin0hu1@nus.edu.sg

<sup>1</sup>National University of Singapore <sup>2</sup>Zhejiang University

<sup>3</sup>Fudan University <sup>4</sup>Tsinghua University <sup>5</sup>Tencent

<sup>\*</sup>Equal contribution. <sup>†</sup>Corresponding author.

## Abstract

Vision-Language Models (VLMs) should answer from concrete image evidence rather than language priors, dataset shortcuts, or irrelevant visual context. Existing perception-aware post-training methods encourage image use through global perturbations or attention proxies, but they do not test whether a sampled answer causally depends on the local evidence that supports it. We propose Counterfactual Evidence Disentanglement (CED), a training-time evidence audit for VLM grounding. For each response, CED neutralizes an object-centric Evidence Region and compares the resulting support drop against matched non-evidence Regions. We combine this signal with answer correctness inside GRPO, rewarding correct answers that rely on the evidence path rather than shortcut or nuisance paths. CED uses weak object-level proposals, requires no question-specific evidence annotations, and adds no inference-time overhead. Across nine public benchmarks and four backbones, CED outperforms prior RL-based post-training methods, with targeted analyses verifying its object-centric signal. Project page including code and checkpoint is available at https://evidencerl.github.io.

## 1 Introduction

Vision-Language Models (VLMs) are increasingly used as general-purpose visual reasoners [Bai et al., 2025b,a, Wang et al., 2025b, Li et al., 2024], but correct-looking answers need not be visually grounded. A model may answer a counting or spatial question by inspecting the relevant evidence, or by relying on language priors, dataset regularities, and scene-level common sense, a failure pattern documented in hallucination, counting, spatial, and shortcut-reasoning evaluations [Li et al., 2023, Paiss et al., 2023, Wang et al., 2024, Guan et al., 2024, Rahmanzadehgervi et al., 2024, Yin et al., 2026]. Post-training can amplify either behavior depending on what the training signal can observe.

Recent perception-aware methods attempt to reintroduce the image into the post-training loop. PAPO [Wang et al., 2025d] compares model behavior under the original image and a corrupted image, while VPPO [Huang et al., 2025] uses attention-derived visual dependency to adjust the training signal. These methods are important because they move beyond text-only supervision. However, they still target coarse visual dependence as a weaker visual anchor rather than causal evidence dependence. In general, the image is not a single cause. It contains the target evidence that supports the answer, irrelevant context, visually salient distractors, and artifacts introduced by masking, zeroing, or noise. A global image perturbation can show that the model is sensitive to the image, but it cannot tell whether the current answer specifically depends on the local evidence that would falsify it if removed. Attention-based dependency is also an internal routing proxy, not a direct test of whether the answer is supported by the relevant evidence.

![](images/61fbde905d9ca54f6ab62681095079f413e6aa22952286b87f7b836c1fff7d4c.jpg)  
Figure 1: Left: Task setup with a counting query over two views of the same scene. Upper right: A pretrained VLM gives the same prior-based answer for both views; EVIDENCE-RL inspects the visual evidence and adjusts its answer when the scene changes. Lower right: Causal path decomposition: a candidate answer can be supported by the target visual evidence, by irrelevant context, or by language priors, which motivates CED to test whether the response depends specifically on the evidence path.

The path decomposition in Figure 1 causally formalizes this interference, following the structuralcausal view that interventions should isolate the path being tested [Pearl, 2009]. A candidate answer can be produced by language and world priors, by irrelevant visual context or distractors, or by the target evidence that actually supports the answer. The shortcut problem arises because these paths meet at the same observed output: the same correct answer may be caused by the evidence path or by a non-evidence path. This suggests a more general requirement for grounded VLM post-training. Instead of asking only whether the model uses the image, we should ask whether the answer depends on the particular visual evidence that supports it, while discounting nuisance sensitivity to other regions and to the intervention itself. Without an image-conditional probe, a training signal computed on the model’s text output alone cannot distinguish answers that traverse the target-evidence path from those that traverse a shortcut path; we make this consequence precise as evidence-closed self-evolution in Section 5 where grounding becomes formally unidentifiable.

Based on this causal view, we propose Counterfactual Evidence Disentanglement (CED), a novel post-training framework that trains VLMs to rely on evidence-specific counterfactual dependence rather than coarse image sensitivity. The core idea is to turn the causal graph into a training-time counterfactual test: for each sampled response, CED asks whether the model’s support for that response decreases more when the object-centric Evidence Region is neutralized than when matched non-evidence Regions are neutralized. A response is therefore favored only when its correctness is tied to the evidence path, rather than preserved through language priors, irrelevant context, or generic sensitivity to visual perturbations. We implement this test by intervening on visual tokens with mean replacement, which removes region-specific information while preserving the local feature baseline, making the intervention a structured local removal of evidence rather than zeroing, random noise, or global corruption. The resulting evidence signal is combined with answer correctness inside GRPO [Shao et al., 2024], encouraging correct answers that are causally grounded in the image without requiring question-specific region annotations or adding inference-time overhead.

We evaluate CED on public VLM benchmarks spanning VQA, hallucination detection, counting, spatial reasoning, and perception-heavy visual reasoning, in which CED outperforms prior RL-based post-training methods, with clear gains on evaluations that require resisting language priors and grounding answers in visual evidence. Targeted analyses confirm that CED captures evidencespecific dependence, that mean replacement provides a cleaner counterfactual intervention than common alternatives, and that the signal follows plausible target evidence rather than arbitrary regions. Throughout the paper we use CED for the counterfactual evidence diagnostic itself (the reward signal) and EVIDENCE-RL for the full post-training pipeline that combines CED with GRPO (Section 3). Our contributions can be summarized as follows:

• We articulate the gap between coarse visual dependence and counterfactual evidence dependence, and formalize visual grounding as a structural causal graph in which the same observed answer can arise from the target-evidence path or from shortcut and nuisance paths. We further characterize why text-only self-evolution can remain evidence-closed.

• We propose CED, a counterfactual evidence audit that tests whether a candidate answer depends on a proposed Evidence Region relative to matched non-evidence Regions. The audit is defined on the causal graph rather than tied to a specific evidence type; we instantiate it for spatial-region evidence and outline how the same recipe extends to attribute-level and relational evidence by varying the intervention.

• We integrate CED into GRPO and validate it through signal diagnostics, controlled ablations (correctness-only, matched baselines, intervention type, proposal robustness), and nine public benchmarks across four backbones. The results show that targeting counterfactual evidence dependence transfers across backbones, recovers gains on perception-heavy benchmarks, and adds no inference-time overhead.

## 2 Related Work

VLM reasoning. Vision-language models built on instruction-tuned LLM backbones [Li et al., 2024, Bai et al., 2025b,a, Wang et al., 2025b] have evolved from task-specific perception systems into general-purpose multimodal reasoners, supporting visual QA, counting, spatial reasoning, diagrammatic reasoning, and scientific problem solving [Paiss et al., 2023, Wang et al., 2024, Lu et al., 2022, 2023, Yue et al., 2024]. This progress exposes a persistent gap between answer correctness and visual grounding: a model can produce a plausible answer without relying on the evidence that should justify it. Benchmarks such as HallusionBench [Guan et al., 2024], VLMsAreBlind [Rahmanzadehgervi et al., 2024], and FREAK [Yin et al., 2026] make this failure measurable through hallucination, shortcut reasoning, and fine-grained visual errors. We address this from the post-training side, rewarding answers whose likelihood depends on relevant visual evidence.

Post-training VLMs. Reinforcement learning has become a central post-training mechanism for improving reasoning, from PPO-style optimization [Schulman et al., 2017, Shao et al., 2024] to verifiable-reward and self-evolution recipes [Guo et al., 2025, Acikgoz et al., 2026]. Recent VLM methods, including VLM-R1 [Shen et al., 2025], ViCrit [Wang et al., 2025c], Perception-R1 [Xiao et al., 2025], SophiaVL-R1 [Fan et al., 2025], and VAPO [Yue et al., 2025], bring this paradigm to multimodal reasoning. The key difficulty is that visual tasks lack cheap per-sample verifiers analogous to code execution or arithmetic checking. Text-only judges can score the plausibility of an answer or rationale but cannot tell whether it was caused by the image, so grounding-oriented RL needs rewards that observe visual evidence.

Grounded Rewards. Existing attempts move in this direction but remain limited. Imageconditional rewards compare rollouts under original and perturbed images [Wang et al., 2025d, Huang et al., 2025, Du et al., 2026] or distill from crop-conditioned teachers [Yuan et al., 2026], yet neither tests whether the decisive region supports the answer. Process-level and self-evolving rewards [Fan et al., 2025, Zhang et al., 2025b, Acikgoz et al., 2026, Zhao et al., 2026] audit the reasoning trace, but remain text-closed and can reward language-prior shortcuts with consistent explanations; we formalize this as evidence-closed self-evolution in Section 5. Counterfactual visual interventions expose grounding failures at inference time [Leng et al., 2024, Liu et al., 2025, Li et al., 2025a, Wu et al., 2026], but usually do not update the model. Our intervention is related to perturbation-based visual explanations [Zeiler and Fergus, 2014, Fong and Vedaldi, 2017, Petsiuk et al., 2018], but we use the score as a training reward. Closest training-time methods require region annotations in reasoning traces [Sun et al., 2026], process/checklist supervision [Li et al., 2026, Zhang et al., 2025a, Wang et al., 2025a, Qin et al., 2025], or adversarial text/preference pairs [Chen et al., 2025, Yang et al., 2026]. In contrast, CED brings region-level counterfactual intervention into RL as a reward, using off-the-shelf object proposals instead of question-specific annotations.

![](images/156ca4a824b2604900da7763ad96b2fe42cc2bbf68135635a10023f775daf76a.jpg)  
Counterfactual Evidence Disentanglement (CED)

Figure 2: Overview of EVIDENCE-RL during post-training. A policy samples candidate answers, and CED scores each answer by applying the same feature-space intervention to the proposed Evidence Region and to matched non-evidence Regions. The contrastive support drop yields an evidence margin, which is combined with correctness to form the GRPO reward. The counterfactual audit is used only during training; inference uses the trained VLM normally.

## 3 Method

Figure 2 summarizes EVIDENCE-RL as a training-time pipeline: sample a candidate answer, contrast the proposed Evidence Region with matched non-evidence Regions, intervene in feature space, compute an answer-conditioned evidence margin, and use the resulting reward in GRPO. We now define the counterfactual probe and its integration into post-training.

## 3.1 CED: Counterfactual Evidence Margin

Correctness alone leaves open whether an answer is supported by the image or by language priors. We therefore use “grounding” in a narrow sense: an answer is grounded when its support depends on a specific locus of visual evidence. CED turns this evidence sensitivity into a training signal complementary to answer correctness.

Given image I, question q, and candidate answer $y ,$ we identify an Evidence Region $\Omega ^ { \mathrm { e v } }$ hypothesized to contain answer-relevant evidence and $K$ non-evidence Regions $\{ \Omega _ { k } ^ { \mathrm { n o n } } \} _ { k = 1 } ^ { K ^ { - } }$ . For a region Ω, we intervene after spatial merging by replacing its visual tokens with the mean $\pmb { \mu } _ { T }$ of neighboring tokens:

$$
\tilde { \mathbf { h } } _ { i } = \left\{ \begin{array} { l l } { \mu _ { T } } & { \mathrm { i f } i \in \mathcal { T } ( \Omega ) , } \\ { \mathbf { h } _ { i } } & { \mathrm { o t h e r w i s e } , } \end{array} \right.\tag{1}
$$

where $\mathcal { T } ( \Omega )$ maps a spatial region to visual-token indices. Feature-space mean replacement removes region-specific information while keeping the local representation manifold largely intact, reducing artifacts compared with zeroing or noise injection. We evaluate these alternatives in Section 4.3.3 and give a mechanistic account in Section A.5.

The evidence sensitivity of y to region Ω is defined as the counterfactual log-likelihood drop:

$$
s ( \Omega ) = \log \pi _ { \theta } ( y \mid I , q ) - \log \pi _ { \theta } ( y \mid \tilde { I } _ { \setminus \Omega } , q ) .\tag{2}
$$

If the model can support y without inspecting Ω, then $s ( \Omega )$ remains close to zero. To obtain a bounded and contrastive score, we compare the evidence-region sensitivity with reference-region

sensitivities:

$$
m ( I , q , y ) = \mathrm { t a n h } \Bigg ( \frac { s ( \Omega ^ { \mathrm { e v } } ) - \mu ( s ^ { \mathrm { n o n } } ) } { \sigma ( s ^ { \mathrm { n o n } } ) + \epsilon } \Bigg ) ,\tag{3}
$$

where $s ^ { \mathrm { n o n } } = \{ s ( \Omega _ { k } ^ { \mathrm { n o n } } ) \} _ { k = 1 } ^ { K }$ , and $\mu ( s ^ { \mathrm { n o n } } )$ and $\sigma ( s ^ { \mathrm { n o n } } )$ are the mean and standard deviation over non-evidence Regions. A positive margin indicates that the candidate answer depends more on the proposed Evidence Region than on area-matched non-evidence Regions.

Non-evidence Regions as a local null. Non-evidence Regions are not treated as annotated negatives. They define a sample-local null distribution for how much the candidate answer changes under the same feature-space intervention applied to regions that are area-matched and spatially separated from the proposed Evidence Region. Thus, if a response is sensitive mainly to generic masking artifacts or irrelevant visual context, the Evidence and non-evidence interventions should induce comparable support drops. A high margin is obtained only when the Evidence Region produces a larger drop than this non-evidence distribution. In implementation, the K non-evidence Regions jointly estimate this baseline rather than forming one-to-one evidence–non-evidence pairs.

Response-conditioned local interventions. CED is designed to isolate the target-evidence path in Figure 1. It scores the sampled answer y itself, measuring the likelihood drop of that response rather than a distribution-level shift. It also intervenes locally, targeting the region that should carry the relevant evidence instead of perturbing the whole image. Finally, the intervention is applied in feature space after spatial merging, which preserves the representation outside the intervened region and reduces pixel-level encoder artifacts. These choices make the score answer-specific, evidence-localized, and less confounded by intervention noise.

Weakly-supervised evidence proposals. The Evidence Region $\Omega ^ { \mathrm { e v } }$ is a weak spatial proposal resolved from dataset metadata, using object-level COCO annotations [Lin et al., 2014] in our experiments. Such boxes provide spatial priors: the same object box may or may not contain evidence depending on the question. Reference Regions are sampled to match the intervention scale while avoiding the proposed Evidence Region. CED resolves this proposal ambiguity by comparing the counterfactual sensitivity of $\Omega ^ { \mathrm { e v } }$ against matched Reference Regions, so the evidence signal is determined by model behavior which are expected to transfer to various downstream tasks. Proposal-layer reliability is evaluated in Section 4.3.3.

## 3.2 EVIDENCE-RL: CED-Guided GRPO

Having defined the evidence margin $m ,$ , we integrate it into GRPO as a correctness-anchored reward. The resulting pipeline, including CED reward shaping and binary-action routing, is denoted by EVIDENCE-RL.

Correctness-anchored reward. The training reward is:

$$
\begin{array} { r } { R _ { \mathrm { t r a i n } } = R _ { \mathrm { a n s } } \cdot g ( m ) + \varepsilon _ { \mathrm { t i e } } m , \qquad g ( m ) = \frac { 1 } { 2 } \Big ( 1 + \operatorname { t a n h } \Big ( \frac { m } { \tau _ { g } } \Big ) \Big ) , } \end{array}\tag{4}
$$

where $\tau _ { g } { = } 0 . 2 0 , \varepsilon _ { \mathrm { t i e } } { = } 0 . 1 0 .$ , and $R _ { \mathrm { a n s } }$ is the answer-correctness score defined in Appendix A.1. When the answer is correct, g(m) favors responses with stronger Evidence Region support. When the answer is wrong and $R _ { \mathrm { a n s } } \stackrel { \cdot } {  } 0$ , the evidence term becomes a bounded tiebreaker, with $| \varepsilon _ { \mathrm { t i e } } m | \leq \varepsilon _ { \mathrm { t i e } } .$ Thus, after within-group normalization $A _ { i } = ( R _ { \mathrm { t r a i n } , i } - \mu ) / \sigma$ , correctness remains the dominant gradient driver, while CED ranks equally correct rollouts by evidence support.

## 4 Experiments

The experiments are designed to validate four properties of our method:(1)the counterfactual reward provides a usable evidence-dependence signal;(2)RL with this signal improves benchmark performance against matched-backbone baselines;(3)the gains transfer across backbones,;(4)the signal remains stable under intervention and proposal perturbations. Unless explicitly stated, ours denotes the Answer-CED variant. The main head-to-head comparison uses Qwen2.5-VL-7B [Bai et al., 2025b] as the base model for ours; cross-backbone validation further covers Qwen2.5-VL-3B/7B [Bai et al., 2025b], Qwen3-VL-8B [Bai et al., 2025a], and Qwen3.5-9B [Team, 2026]. For reference, the backbone rows also include LLaVA-v1.6-7B [Li et al., 2024] and InternVL3.5-8B [Wang et al., 2025b]. Matched baselines include recent RL-based VLM post-training methods [Yue et al., 2025, Huang et al., 2025, Xiao et al., 2025, Wang et al., 2025d, Shen et al., 2025, Fan et al., 2025]. Signal validation diagnostics use Qwen3-VL-8B-Instruct as a frozen probe. Evaluation covers nine public benchmarks spanning grounding, faithfulness, and general reasoning: CountBench [Paiss et al., 2023], SpatialEval [Wang et al., 2024], HallusionBench [Guan et al., 2024], VLMsAreBlind [Rahmanzadehgervi et al., 2024], FREAK [Yin et al., 2026], MathVista [Lu et al., 2023], MMBench [Liu et al., 2024], MMMU [Yue et al., 2024], and ScienceQA [Lu et al., 2022], with no overlap between training images and evaluation benchmarks.

Table 1: Signal-validation statistics on counting and presence tasks.
<table><tr><td>Task</td><td>Non-constant raw reward</td><td>Zero variance</td><td>Mean reward std</td><td>Same answer, different reward</td><td>Mean negation</td></tr><tr><td>Counting</td><td>99.5%</td><td>24.0%</td><td>0.1299</td><td>90.0%</td><td>0.003</td></tr><tr><td>Presence</td><td>21.1%</td><td>79.0%</td><td>0.0497</td><td>5.0%</td><td>0.777</td></tr></table>

Table 2: Nine-benchmark evaluation using Qwen2.5-VL-7B as the base model for Ours. Backbone, baseline, and benchmark sources are cited in the setup paragraph. Best bold; second-best underlined. Each ∆ row reports absolute gain over the corresponding base.
<table><tr><td rowspan="2">Model</td><td colspan="5">Grounding</td><td colspan="4">General Reasoning</td><td rowspan="2">Avg</td></tr><tr><td>CountBench</td><td>SpatialEval</td><td>Hallusion</td><td>VLMs AreBlind</td><td>FREAK</td><td>MathVista</td><td>MMBench</td><td>MMMU</td><td>ScienceQA</td></tr><tr><td colspan="10">VLM backbones</td></tr><tr><td>LLaVA-v1.6-7B</td><td>55.60</td><td>23.60</td><td>51.00</td><td>28.23</td><td>9.50</td><td>22.80</td><td>71.30</td><td>29.00</td><td>57.20</td><td>38.69</td></tr><tr><td>InternVL3.5-8B</td><td>86.90</td><td>24.00</td><td>69.60</td><td>54.92</td><td>12.80</td><td>51.90</td><td>83.40</td><td>50.80</td><td>89.90</td><td>58.25</td></tr><tr><td>Qwen2.5-VL-3B</td><td>70.71</td><td>53.94</td><td>65.37</td><td>42.46</td><td>11.14</td><td>52.10</td><td>80.40</td><td>50.29</td><td>74.93</td><td>55.70</td></tr><tr><td>Qwen2.5-VL-7B</td><td>81.82</td><td>59.21</td><td>68.64</td><td>46.44</td><td>12.18</td><td>63.10</td><td>84.73</td><td>50.63</td><td>83.98</td><td>61.19</td></tr><tr><td colspan="10">RL-based methods</td></tr><tr><td>VAPO-Thinker-7B</td><td>86.90</td><td>60.80</td><td>71.20</td><td>48.62</td><td>13.10</td><td>51.10</td><td>81.80</td><td>44.60</td><td>82.30</td><td>60.05</td></tr><tr><td>∆</td><td>+5.10</td><td>+1.59</td><td>+2.60</td><td>+2.18</td><td>+0.92</td><td>-12.00</td><td>-2.90</td><td>-6.00</td><td>-1.70</td><td>-1.14</td></tr><tr><td>VPPO-7B</td><td>85.90</td><td>61.80</td><td>68.20</td><td>49.35</td><td>12.70</td><td>67.90</td><td>84.90</td><td>52.10</td><td>88.40</td><td>63.47</td></tr><tr><td>∆</td><td>+4.10</td><td>+2.59</td><td>-0.40</td><td>+2.91</td><td>+0.52</td><td>+4.80</td><td>+0.20</td><td>+1.50</td><td>+4.40</td><td>+2.28</td></tr><tr><td>Perception-R1-7B</td><td>84.90</td><td>59.70</td><td>66.70</td><td>45.22</td><td>12.20</td><td>67.10</td><td>81.70</td><td>48.10</td><td>82.30</td><td>60.88</td></tr><tr><td>∆</td><td>+3.10</td><td>+0.49</td><td>-1.90</td><td>-1.22</td><td>+0.02</td><td>+4.00</td><td>-3.00</td><td>-2.50</td><td>-1.70</td><td>-0.31</td></tr><tr><td>PAPO-G-H</td><td>90.90</td><td>64.80</td><td>69.50</td><td>47.92</td><td>12.80</td><td>69.40</td><td>82.80</td><td>50.50</td><td>85.60</td><td>63.80</td></tr><tr><td>∆</td><td>+9.10</td><td>+5.59</td><td>+0.90</td><td>+1.48</td><td>+0.62</td><td>+6.30</td><td>-1.90</td><td>-0.10</td><td>+1.60</td><td>+2.61</td></tr><tr><td>VLM-R1</td><td>74.80</td><td>56.40</td><td>66.60</td><td>44.15</td><td>11.00</td><td>60.30</td><td>79.90</td><td>48.60</td><td>73.60</td><td>57.26</td></tr><tr><td>∆ vs. Qwen2.5-VL-3B</td><td>+4.10</td><td>+2.50</td><td>+1.20</td><td>+1.69</td><td>-0.14</td><td>+8.20</td><td>-0.50</td><td>-1.70</td><td>-1.30</td><td>+1.56</td></tr><tr><td>SophiaVL-R1</td><td>82.83</td><td>61.38</td><td>66.87</td><td>47.09</td><td>24.18</td><td>66.30</td><td>87.41</td><td>52.18</td><td>87.64</td><td>63.99</td></tr><tr><td>Δ</td><td>+1.01</td><td>+2.17</td><td>-1.77</td><td>+0.65</td><td>+12.00</td><td>+3.20</td><td>+2.68</td><td>+1.55</td><td>+3.66</td><td>+2.80</td></tr><tr><td colspan="10">Ours</td></tr><tr><td>∆</td><td>88.89 +7.07</td><td>63.34 +4.13</td><td>70.08 +1.44</td><td>54.02 +7.58</td><td>26.40 +14.22</td><td>69.40 +6.30</td><td>87.53 +2.80</td><td>57.47 +6.84</td><td>87.08 +3.10</td><td>67.13 +5.94</td></tr></table>

## 4.1 Validating the Evidence-Dependence Signal

We first check whether the reward separates evidence dependence from correctness-only. On counting tasks, 99.5% of groups have non-constant rewards and 90.0% contain same-answer trajectories with different rewards, showing that the signal preserves within-group discrimination beyond answer-string matching. Presence tasks show higher zero variance, consistent with their two-action yes/no structure discussed in Section 3.2. Cross-model validation and blindfold tests are reported in Appendix A.4.

## 4.2 Main Results on Nine Benchmarks

Table 2 compares ours with VLM backbones and RL-based baselines on nine benchmarks. Benchmarks are grouped into Grounding and General Reasoning. Each ∆ reports the absolute gain over the corresponding base model, which is Qwen2.5-VL-7B unless the row label specifies another base.

Ours obtains the highest average score and the largest mean improvement in the matched-backbone comparison. It is also the only RL method with non-negative ∆ on all nine benchmarks. The largest gains appear on perception-heavy benchmarks, including VLMsAreBlind, FREAK, and MMMU, while MathVista, MMBench, and ScienceQA remain positive. This pattern supports the intended role of the reward: increasing reliance on visual evidence without sacrificing general transfer.

Table 3: Controlled comparison on Qwen3.5-9B with matched data, router, and compute. ∆ is the mean gain over the frozen base; $\Delta _ { \mathrm { C E D } }$ is Answer-CED minus correctness-only.
<table><tr><td rowspan="2">Method</td><td colspan="5">Grounding</td><td colspan="4">General Reasoning</td><td rowspan="2"></td><td rowspan="2">∆</td></tr><tr><td>CountBench</td><td></td><td>SpatialEval Hallusion</td><td>VLMs AreBlind</td><td></td><td>FREAK MathVista</td><td>MMBench</td><td>MMMU</td><td>ScienceQA</td></tr><tr><td>λ=0 (corr.-only)</td><td>89.90</td><td>40.45</td><td>57.93</td><td>72.90</td><td>18.73</td><td>73.40</td><td>79.44</td><td>36.00</td><td>82.24</td><td>61.22</td><td>-1.24</td></tr><tr><td>VPPO (retrained)</td><td>86.87</td><td>38.32</td><td>58.37</td><td>72.97</td><td>19.07</td><td>72.50</td><td>79.62</td><td>37.33</td><td>81.09</td><td>60.68</td><td>-1.78</td></tr><tr><td>PAPO (retrained)†</td><td>86.87</td><td>8.59</td><td>58.46</td><td>69.96</td><td>19.40</td><td>14.00</td><td>44.87</td><td>33.22</td><td>34.24</td><td>41.07</td><td>-21.39</td></tr><tr><td>Answer-CED</td><td>93.90</td><td>54.35</td><td>78.10</td><td>73.10</td><td>23.12</td><td>83.75</td><td>88.58</td><td>75.67</td><td>93.61</td><td>73.80</td><td>+11.34</td></tr><tr><td>∆CED</td><td>+4.00</td><td>+13.90</td><td>+20.17</td><td>+0.20</td><td>+4.39</td><td>+10.35</td><td>+9.14</td><td>+39.67</td><td>+11.37</td><td>+12.58</td><td></td></tr></table>

<sup>†</sup> PAPO’s global-perturbation KL reward induces repetitive reasoning loops on Qwen3.5-9B (25% repeated-segment rate, 58% budget exhaustion at 24k tokens).

![](images/09f6fffc99105406afd67ebf607e8bb7102ef3587b78af041067e052a6e1b776.jpg)  
Figure 3: A case showing why correctness-only reward is insufficient. Two rollouts from the same GRPO group both answer $\mathit { \Omega } ^ {  6 } 4 ^ {  3  }$ correctly, but the CED gate g(m) creates a $7 \times$ reward gap between a prior-based rollout (g(m)=0.18, R=0.11) and an evidence-grounded rollout (g(m)=1.00, R=0.78), enabling GRPO to select the grounded trajectory.

## 4.3 Ablations and Diagnostics

Having established the aggregate gains, we now diagnose their source. We first isolate the CED contribution under strictly controlled conditions (Section 4.3.1), then examine cross-backbone generalization and the Answer-vs-CoT design choice (Section 4.3.2), and finally stress-test the reward signal against proposal and intervention perturbations (Section 4.3.3).

## 4.3.1 Isolating the CED Contribution

Is the CED reward necessary? Table 3 compares correctness-only, retrained VPPO, retrained PAPO, and Answer-CED under matched conditions: the same Qwen3.5-9B backbone, 15,314-sample training set, router, 2,000-step schedule, and LoRA configuration. Without CED, the same data and compute do not produce transferable improvements. Correctness-only and VPPO produce gains on several grounding benchmarks but substantial negative transfer to general reasoning, yielding net-negative average deltas. PAPO becomes unstable under its global-perturbation KL objective, with 25% repeated-segment rate and 58% budget exhaustion at 24k tokens. Answer-CED improves all nine benchmarks over correctness-only (+12.58 average) and exceeds matched VPPO by +13.12. CED uniquely converts the same data and compute into transferable improvements by restoring evidence-specific within-group discrimination among equally correct rollouts.

Figure 3 illustrates this mechanism. Two rollouts from the same GRPO group both answer “4” correctly: one relies on the prior sedan = 2+2 without inspecting the image, while the other detects the unusual wheel configuration (1 front +2 rear +1 spare) through visual evidence. Correctness-only reward produces no ranking signal while the CED gate $g ( m )$ multiplies R<sub>ans</sub> $R _ { \mathrm { a n s } }$ by the evidence margin, creating a 7× reward gap that GRPO uses to select the grounded trajectory.

## 4.3.2 Generalization and Variant Analysis

Does CED transfer across backbones? We apply the same recipe to four from two model families. Table 4 reports frozen-base scores, ours, and per-benchmark gains. Our method yields positive mean improvement on every backbone and non-negative gains on all 36 benchmark–backbone cells.

Table 4: Cross-backbone validation of Ours. Each block reports the frozen base, Ours, and absolute ∆ against that block’s base. The Qwen3.5-9B block additionally reports 3-seed mean±std, with its mean ∆ in the last column.
<table><tr><td></td><td colspan="5">Grounding</td><td colspan="4">General Reasoning</td><td></td></tr><tr><td>Model</td><td>CountBench</td><td>SpatialEval</td><td>Hallusion</td><td>VLMs AreBlind</td><td>FREAK</td><td>MathVista</td><td>MMBench</td><td>MMMU</td><td>ScienceQA</td><td>Avg. ∆</td></tr><tr><td colspan="9">Backbone: Qwen2.5-VL-3B</td><td></td></tr><tr><td>Qwen2.5-VL-3B</td><td>70.71</td><td>53.94</td><td>65.37</td><td>42.46</td><td>11.14</td><td>52.10</td><td>80.40</td><td>50.29</td><td>74.93</td><td></td></tr><tr><td>Ours</td><td>70.71</td><td>55.56</td><td>67.40</td><td>49.51</td><td>25.51</td><td>60.40</td><td>82.55</td><td>50.57</td><td>80.43</td><td></td></tr><tr><td>△</td><td>+0.00</td><td>+1.62</td><td>+2.03</td><td>+7.05</td><td>+14.37</td><td>+8.30</td><td>+2.15</td><td>+0.28</td><td>+5.50</td><td>+4.59</td></tr><tr><td colspan="9">Backbone: Qwen2.5-VL-7B</td><td></td></tr><tr><td>Qwen2.5-VL-7B</td><td>81.82</td><td>59.21</td><td>68.64</td><td>46.44</td><td>12.18</td><td>63.10</td><td>84.73</td><td>50.63</td><td>83.98</td><td></td></tr><tr><td>Ours</td><td>88.89</td><td>63.34</td><td>70.08</td><td>54.02</td><td>26.40</td><td>69.40</td><td>87.53</td><td>57.47</td><td>87.08</td><td></td></tr><tr><td>△</td><td>+7.07</td><td>+4.13</td><td>+1.44</td><td>+7.58</td><td>+14.22</td><td>+6.30</td><td>+2.80</td><td>+6.84</td><td>+3.10</td><td>+5.94</td></tr><tr><td colspan="9">Backbone: Qwen3-VL-8B-Instruct</td><td></td><td></td></tr><tr><td>Qwen3-VL-8B</td><td>94.90</td><td>65.26</td><td>72.86</td><td>67.01</td><td>28.85</td><td>67.54</td><td>89.15</td><td>57.82</td><td>91.99</td><td></td></tr><tr><td>Ours</td><td>95.92</td><td>67.75</td><td>74.30</td><td>68.88</td><td>31.18</td><td>68.04</td><td>89.58</td><td>58.85</td><td>92.82</td><td></td></tr><tr><td>∆</td><td>+1.02</td><td>+2.49</td><td>+1.44</td><td>+1.87</td><td>+2.33</td><td>+0.50</td><td>+0.43</td><td>+1.03</td><td>+0.83</td><td>+1.33</td></tr><tr><td colspan="9">Backbone: Qwen3.5-9B</td><td></td></tr><tr><td>Qwen3.5-9B</td><td>80.80</td><td>52.73</td><td>47.20</td><td>46.44</td><td>9.95</td><td>80.00</td><td>88.03</td><td>66.21</td><td>90.78</td><td></td></tr><tr><td>Òurs</td><td>93.90</td><td>54.35</td><td>78.10</td><td>73.10</td><td>23.12</td><td>83.75</td><td>88.58</td><td>75.67</td><td>93.61</td><td></td></tr><tr><td>∆</td><td>+13.10</td><td>+1.62</td><td>+30.90</td><td>+26.66</td><td>+13.17</td><td>+3.75</td><td>+0.55 89.87</td><td>+9.46</td><td>+2.83</td><td>+11.34</td></tr><tr><td>Ours (3 seeds)</td><td>93.60</td><td>56.04 ±0.27</td><td>78.35 ±0.21</td><td>73.37 ±0.17</td><td>23.11 ±0.40</td><td>84.40 ±0.50</td><td>±0.04</td><td>75.39 ±0.22</td><td>94.46 ±0.13</td><td>+11.83</td></tr><tr><td></td><td>±0.48</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>

Table 5: Answer vs. CoT variants on Qwen3.5-9B; Avg. ∆ is the mean gain over the base.
<table><tr><td></td><td colspan="5">Grounding</td><td colspan="4">General Reasoning</td><td></td></tr><tr><td>Variant</td><td>CountBench</td><td>SpatialEval</td><td>Hallusion</td><td>VLMs AreBlind</td><td>FREAK</td><td>MathVista</td><td>MMBench</td><td>MMMU</td><td>ScienceQA</td><td>Avg. ∆</td></tr><tr><td>Answer</td><td>93.90</td><td>54.35</td><td>78.10</td><td>73.10</td><td>23.12</td><td>83.75</td><td>88.58</td><td>75.67</td><td>93.61</td><td>+11.34</td></tr><tr><td>CoT</td><td>92.90</td><td>53.80</td><td>78.10</td><td>69.09</td><td>30.35</td><td>81.88</td><td>88.53</td><td>68.23</td><td>94.66</td><td>+10.60</td></tr></table>

Which CED variant should be used: Answer or CoT? The default Answer variant directly rewards image-to-answer dependence. To isolate the effect of where the counterfactual margin is applied, Table 5 compares Answer and CoT variants on the same Qwen3.5-9B base. Answer obtains a slightly higher mean gain with stronger general transfer on downstream tasks like MMMU even though CoT obtains larger reward. This discrepancy reflects a structural mismatch between dense per-token rewards and GRPO’s group-relative optimization. CoT-CED averages evidence margins over the full reasoning trace, and because trace length is policy-controlled, the model can raise the per-token average by truncating low-margin connective tokens rather than by strengthening visual grounding which is a reward-hacking pathway also documented in the process-reward literature Guo et al. [2025], Shao et al. [2024]. Tables A.13–A.14 confirm this collapse: CoT-CED’s mean chain shrinks to 3.6 tokens on counting, degenerating to object-cue shorthand. Answer-CED avoids this by scoring only the final-answer span, a fixed-length outcome interface that eliminates the chain-length degree of freedom. Full length and generation diagnostics are in Appendix A.11.

Figure 4 shows why the default remains Answer-CED despite CoT-CED’s stronger training-side signal. CoT-CED reaches higher reward and a denser positive margin during training, but this margin advantage does not yield stronger average transfer in Table 5. The likely failure mode is that CoT-CED can raise a per-token margin by shortening the chain around visually salient object cues, whereas Answer-CED applies the counterfactual directly to the final answer. We therefore use Answer-CED as the default variant; additional length and generation diagnostics are in Section A.11.

## 4.3.3 Reward Signal Robustness

Is the reward signal robust to proposal quality? Figure 5 evaluates whether CED’s signal depends on proposal relevance or simply on masking magnitude. Panel (a) compares the original COCO-based proposal with a random object box as $\Omega ^ { \mathrm { e v } }$ across seven task types. The evidence margin drops from m¯ =0.268 (COCO) to m¯ =0.015 (random box), and the relevant-beats-random rate drops from 0.636 to 0.487 (chance level). Panel (b) shows IoU-graded degradation on the count-exclusion diagnostic: m¯ decreases monotonically from 0.501 at high IoU to 0.219 at low IoU, approaching the random floor at 0.147. Scale and shift perturbations are reported in Section A.7. These results confirm two properties: CED does not reward masking magnitude, and the COCO-based proposal, despite being a weak spatial prior without question-specific annotation, provides sufficient evidence localization for a discriminative signal.

![](images/d576cc0cf412349b28a3c6318d25c30b4182412abc47f040eb8367db6f4aea9c.jpg)  
(a) Training reward

![](images/b0aa4e9fd73b1b1b4adb330cff1c868f19e41d1527164fb494b17518f77b28e2.jpg)  
(b) Training correctness

Figure 4: Training dynamics for Answer-CED and CoT-CED on Qwen3.5-9B. CoT-CED produces larger training-side rewards, but the downstream comparison in Table 5 favors Answer-CED on average; we therefore use Answer-CED as the default variant.  
![](images/3e1ce704959be729edd794d81374e449b49497b6d16c963526b8274b2459499d.jpg)

(b) IoU-graded degradation (n = 41, count-excl.)  
![](images/abc8da5364929ce845437310c7c064ff49f6fa0d5fb27f97b57969ce0ea268a0.jpg)  
Figure 5: CED probe robustness under proposal perturbation. (a) Replacing the COCO proposal with a random object box as $\Omega ^ { \mathrm { e v } }$ collapses the evidence margin to near zero across all seven task types, confirming that the signal tracks proposal relevance rather than masking magnitude. (b) IoU-graded degradation on the count-exclusion diagnostic: m¯ decreases monotonically as spatial overlap with the original proposal drops, approaching the random-region floor at lowest IoU.

Which intervention type produces the strongest discrimination? Within local interventions, mean replacement gives the strongest discrimination, followed by zero replacement and Gaussiannoise replacement $( \mathrm { A U C 0 . 6 6 9 > 0 . 6 4 1 > 0 . 6 2 9 }$ averaged across keying modes). Global random masking performs below chance, with an above-baseline rate of 0.490, showing that ours depends on structured local counterfactuals rather than corruption magnitude alone. With the frozen pre-RL checkpoint, the Evidence Region signal is 1.534, compared with 0.520 for shifted regions, 0.319 for wrong-category regions, and 0.566 for random regions, consistent with the proposal-robustness results in Section 4.3.3. Full perturbation results and mechanistic analysis are in Section A.5.

## 5 Discussion

Visual evidence over language priors on FREAK. The FREAK gains make the same mechanism visible at the trajectory level. The representative cases in Figure 6 contain images whose visual evidence contradicts a common language prior. PAPO and LLaVA-v1.6-7B follow the prior-consistent answer, whereas the CED-trained model recovers the image-grounded answer. Thus, the qualitative rollouts instantiate the rerouting predicted by Figure 1: answers that would otherwise be driven by shortcut priors are redirected toward visual evidence. The selected cases are typical members of this failure regime rather than engineered edge cases.

Behavior in the absence of visual evidence. Blank-image ScienceQA items provide the complementary test. In examples whose image is only a blank 448×448 placeholder, such as “What is the mass of a cement truck?” with options 20 tons / 20 pounds / 20 ounces, the frozen base selects the prior-consistent answer and is scored correct, while CED responds “Cannot determine from image” and is scored incorrect. This is precisely the downstream tasks’ behavior targeted by the reward: when no answer is grounded in image evidence, the model should avoid substituting language priors. This also explains part of the modest ScienceQA gains in Table 4: CED improves the visual-reasoning portion as in other benchmarks, while the blank-image subset rewards the prior-following behavior that CED suppresses. The net effect remains positive on every backbone.

![](images/b5886851bf27db0ef2565fb2845739a3ce76551a5bc9182151e9d022262a6fce.jpg)  
Figure 6: Five prior-conflict FREAK cases. Each card reports the ground truth, the outputs of PAPO, LLaVA-v1.6-7B, and the Qwen2.5-VL-7B base model in that order, and the output of ours. The non-CED models follow a plausible object prior, whereas ours follows the local visual evidence.

No text-only degradation. A potential concern is that rewarding evidence dependence may harm general text reasoning. We evaluate the Qwen3.5-9B Answer-CED checkpoint on eight text-only benchmarks (ARC-Easy, ARC-Challenge, OpenBookQA, CommonsenseQA, WinoGrande, PIQA, BoolQ, TruthfulQA-MC2) spanning commonsense, science, and factual reasoning. The mean accuracy change is −0.27 pp, with no single benchmark dropping more than 1.5 pp. CED improves visual grounding without degrading the language backbone.

Evidence-closed text-only self-evolution. The following analysis makes this intuition precise: an image-conditional signal is structurally necessary to distinguish grounded from shortcut trajectories. In VLM RL, model-judged or self-evolving audits often collapse back to text because the cheap verifiable targets used in LLM self-evolution, such as executable code or checkable arithmetic, have no per-sample-cheap visual analogue. Let $S _ { t }$ be the reward, $I _ { t }$ the image, $\hat { Y } _ { t }$ the answer, and $G _ { t } \in \{ 0 , 1 \}$ the latent grounding indicator. This conditional independence is a direct consequence of the path structure in Figure 1: the evidence path and the shortcut path both terminate at the answer node, so a reward that observes only the answer cannot determine which upstream path produced it.A text-only reward satisfies $S _ { t } \perp \perp I _ { t } \mid ( \hat { Y } _ { t } , Q _ { t } )$ , and therefore ${ \cal I } ( S _ { t } ; G _ { t } \ | \ \hat { Y } _ { t } , Q _ { t } ) = 0 \colon$ two trajectories that reach the same correct answer through grounding versus a language-prior shortcut induce identical reward distributions. We call this regime evidence-closed self-evolution. As long as the audit observes only text, judge capacity, annealing, or trustworthiness reweighting cannot resolve the ambiguity, since the limitation comes from the conditional independence structure. CED breaks this closure by injecting an image-conditional signal. The evidence margin $m ( I , q , y )$ in Equation (3) cannot be computed from $( \hat { Y } _ { t } , Q _ { t } )$ alone, and the strict inequality $H ( G _ { t } \mid \mathcal { B } _ { t } , A _ { t } ) < H ( G _ { t } \mid \mathcal { B } _ { t } )$ formalizes the empirical fact that CED reorders trajectories that correctness rewards cannot. The formal argument is developed in Section A.12. This yields a unified diagnosis of recent self-evolving multimodal RL pipelines: stable shortcut correction depends less on judge capacity than on whether the reward can observe the visual evidence path.

## 6 Conclusion

We introduced EVIDENCE-RL, a post-training framework for VLMs built around CED, a counterfactual evidence diagnostic motivated by a causal view of visual grounding. CED moves beyond rewarding answer correctness alone by asking whether a sampled response depends on the Evidence Region causally. With spatial-region interventions, this diagnostic can be directly integrated into GRPO as an evidence-aware reward, producing grounded reasoning behavior with no additional inference cost. Across four backbones and nine benchmarks, EVIDENCE-RL consistently improves performance, with the largest gains on benchmarks where shortcut behavior is most exposed.

Post-training should reward correct answers for depending on the visual evidence relevant to the question, rather than for matching the answer distribution alone. Though our experiments use objectcentric interventions, gains generalize to various downstream tasks: the CED signal supervises the reasoning process and instills faithful evidence dependence, the capability most absent from current VLMs. Achieving high accuracy without depending on the relevant evidence is not visual reasoning; making that dependence a prioritized training objective is what evidence-intensive reasoning requires.

## References

Emre Can Acikgoz, Cheng Qian, Jonas Hübotter, Heng Ji, Dilek Hakkani-Tür, and Gokhan Tur. Toolr0: Self-evolving llm agents for tool-learning from zero data. arXiv preprint arXiv:2602.21320, 2026.

Shuai Bai, Yuxuan Cai, Ruizhe Chen, Keqin Chen, Xionghui Chen, Zesen Cheng, Lianghao Deng, Wei Ding, Chang Gao, Chunjiang Ge, et al. Qwen3-vl technical report. arXiv preprint arXiv:2511.21631, 2025a.

Shuai Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin Ge, Sibo Song, Kai Dang, Peng Wang, Shijie Wang, Jun Tang, Humen Zhong, Yuanzhi Zhu, Mingkun Yang, Zhaohai Li, Jianqiang Wan, Pengfei Wang, Wei Ding, Zheren Fu, Yiheng Xu, Jiabo Ye, Xi Zhang, Tianbao Xie, Zesen Cheng, Hang Zhang, Zhibo Yang, Haiyang Xu, and Junyang Lin. Qwen2.5-vl technical report. arXiv preprint arXiv:2502.13923, 2025b.

Cong Chen, Mingyu Liu, Chenchen Jing, Yizhou Zhou, Fengyun Rao, Hao Chen, Bo Zhang, and Chunhua Shen. Perturbollava: Reducing multimodal hallucinations with perturbative visual training. arXiv preprint arXiv:2503.06486, 2025.

Yuetian Du, Yucheng Wang, Rongyu Zhang, Zhijie Xu, Boyu Yang, Ming Kong, Jie Liu, and Qiang Zhu. Linking perception, confidence and accuracy in mllms. arXiv preprint arXiv:2603.12149, 2026.

Kaixuan Fan, Kaituo Feng, Haoming Lyu, Dongzhan Zhou, and Xiangyu Yue. Sophiavl-r1: Reinforcing mllms reasoning with thinking reward. arXiv preprint arXiv:2505.17018, 2025.

Ruth C. Fong and Andrea Vedaldi. Interpretable explanations of black boxes by meaningful perturbation. In IEEE International Conference on Computer Vision, pages 3449–3457, 2017.

Tianrui Guan, Fuxiao Liu, Xiyang Wu, Ruiqi Xian, Zongxia Li, Xiaoyu Liu, Xijun Wang, Lichang Chen, Furong Huang, Yaser Yacoob, et al. Hallusionbench: an advanced diagnostic suite for entangled language hallucination and visual illusion in large vision-language models. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages 14375–14385, 2024.

Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Peiyi Wang, Qihao Zhu, Runxin Xu, Ruoyu Zhang, Shirong Ma, Xiao Bi, et al. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv preprint arXiv:2501.12948, 2025.

Siyuan Huang, Xiaoye Qu, Yafu Li, Yun Luo, Zefeng He, Daizong Liu, and Yu Cheng. Spotlight on token perception for multimodal reinforcement learning. arXiv preprint arXiv:2510.09285, 2025.

Sicong Leng, Hang Zhang, Guanzheng Chen, Xin Li, Shijian Lu, Chunyan Miao, and Lidong Bing. Mitigating object hallucinations in large vision-language models through visual contrastive decoding. In Proceedings ofthe IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 13872–13882, 2024.

Feng Li, Renrui Zhang, Hao Zhang, Yuanhan Zhang, Bo Li, Wei Li, Zejun Ma, and Chunyuan Li. Llava-next-interleave: Tackling multi-image, video, and 3d in large multimodal models. arXiv preprint arXiv:2407.07895, 2024.

Shawn Li, Jiashu Qu, Yuxiao Zhou, Yuehan Qin, Tiankai Yang, and Yue Zhao. Treble counterfactual vlms: A causal approach to hallucination. arXiv preprint arXiv:2503.06169, 2025a.

Yantao Li, Qiang Hui, Chenyang Yan, Kanzhi Cheng, Fang Zhao, Chao Tan, Huanling Gao, Jianbing Zhang, Kai Wang, Xinyu Dai, et al. Palmr: Towards faithful visual reasoning via multimodal process alignment. arXiv preprint arXiv:2603.06652, 2026.

Yifan Li, Yifan Du, Kun Zhou, Jinpeng Wang, Xin Zhao, and Ji-Rong Wen. Evaluating object hallucination in large vision-language models. In Proceedings of the 2023 conference on empirical methods in natural language processing, pages 292–305, 2023.

Zongxia Li, Wenhao Yu, Chengsong Huang, Rui Liu, Zhenwen Liang, Fuxiao Liu, Jingxi Che, Dian Yu, Jordan Boyd-Graber, Haitao Mi, et al. Self-rewarding vision-language model via reasoning decomposition. arXiv preprint arXiv:2508.19652, 2025b.

Tsung-Yi Lin, Michael Maire, Serge Belongie, James Hays, Pietro Perona, Deva Ramanan, Piotr Dollár, and C Lawrence Zitnick. Microsoft coco: Common objects in context. In European conference on computer vision, pages 740–755. Springer, 2014.

Sheng Liu, Haotian Ye, and James Zou. Reducing hallucinations in large vision-language models via latent space steering. In The Thirteenth International Conference on Learning Representations, 2025.

Yuan Liu, Haodong Duan, Yuanhan Zhang, Bo Li, Songyang Zhang, Wangbo Zhao, Yike Yuan, Jiaqi Wang, Conghui He, Ziwei Liu, et al. Mmbench: Is your multi-modal model an all-around player? In European conference on computer vision, pages 216–233. Springer, 2024.

Pan Lu, Swaroop Mishra, Tanglin Xia, Liang Qiu, Kai-Wei Chang, Song-Chun Zhu, Oyvind Tafjord, Peter Clark, and Ashwin Kalyan. Learn to explain: Multimodal reasoning via thought chains for science question answering. Advances in neural information processing systems, 35:2507–2521, 2022.

Pan Lu, Hritik Bansal, Tony Xia, Jiacheng Liu, Chunyuan Li, Hannaneh Hajishirzi, Hao Cheng, Kai-Wei Chang, Michel Galley, and Jianfeng Gao. Mathvista: Evaluating mathematical reasoning of foundation models in visual contexts. arXiv preprint arXiv:2310.02255, 2023.

Roni Paiss, Ariel Ephrat, Omer Tov, Shiran Zada, Inbar Mosseri, Michal Irani, and Tali Dekel. Teaching clip to count to ten. In Proceedings of the IEEE/CVF international conference on computer vision, pages 3170–3180, 2023.

Judea Pearl. Causality: Models, Reasoning, and Inference. Cambridge University Press, 2 edition, 2009.

Vitali Petsiuk, Abir Das, and Kate Saenko. RISE: Randomized input sampling for explanation of black-box models. In British Machine Vision Conference, 2018.

Yiming Qin, Bomin Wei, Jiaxin Ge, Konstantinos Kallidromitis, Stephanie Fu, Trevor Darrell, and XuDong Wang. Chain-of-visual-thought: Teaching vlms to see and think better with continuous visual tokens. arXiv preprint arXiv:2511.19418, 2025.

Pooyan Rahmanzadehgervi, Logan Bolton, Mohammad Reza Taesiri, and Anh Totti Nguyen. Vision language models are blind: Failing to translate detailed visual features into words. arXiv preprint arXiv:2407.06581, 2024.

John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, and Oleg Klimov. Proximal policy optimization algorithms. arXiv preprint arXiv:1707.06347, 2017.

Zhihong Shao, Peiyi Wang, Qihao Zhu, Runxin Xu, Junxiao Song, Xiao Bi, Haowei Zhang, Mingchuan Zhang, YK Li, Yang Wu, et al. Deepseekmath: Pushing the limits of mathematical reasoning in open language models. arXiv preprint arXiv:2402.03300, 2024.

Haozhan Shen, Peng Liu, Jingcheng Li, Chunxin Fang, Yibo Ma, Jiajia Liao, Qiaoli Shen, Zilun Zhang, Kangjia Zhao, Qianqian Zhang, et al. Vlm-r1: A stable and generalizable r1-style large vision-language model. arXiv preprint arXiv:2504.07615, 2025.

Wenfang Sun, Hao Chen, Yingjun Du, Yefeng Zheng, and Cees GM Snoek. Regionreasoner: Region-grounded multi-round visual reasoning. arXiv preprint arXiv:2602.03733, 2026.

Qwen Team. Qwen3.5: Accelerating productivity with native multimodal agents, February 2026. URL https://qwen.ai/blog?id=qwen3.5.

Jiacong Wang, Zijian Kang, Haochen Wang, Haiyong Jiang, Jiawen Li, Bohong Wu, Ya Wang, Jiao Ran, Xiao Liang, Chao Feng, et al. Vgr: Visual grounded reasoning. arXiv preprint arXiv:2506.11991, 2025a.

Jiayu Wang, Yifei Ming, Zhenmei Shi, Vibhav Vineet, Xin Wang, Yixuan Li, and Neel Joshi. Is a picture worth a thousand words? delving into spatial reasoning for vision language models. Advances in Neural Information Processing Systems, 37:75392–75421, 2024.

Weiyun Wang, Zhangwei Gao, Lixin Gu, Hengjun Pu, Long Cui, Xingguang Wei, Zhaoyang Liu, Linglin Jing, Shenglong Ye, Jie Shao, et al. Internvl3. 5: Advancing open-source multimodal models in versatility, reasoning, and efficiency. arXiv preprint arXiv:2508.18265, 2025b.

Xiyao Wang, Zhengyuan Yang, Chao Feng, Yongyuan Liang, Yuhang Zhou, Xiaoyu Liu, Ziyi Zang, Ming Li, Chung-Ching Lin, Kevin Lin, et al. Vicrit: A verifiable reinforcement learning proxy task for visual perception in vlms. arXiv preprint arXiv:2506.10128, 2025c.

Zhenhailong Wang, Xuehang Guo, Sofia Stoica, Haiyang Xu, Hongru Wang, Hyeonjeong Ha, Xiusi Chen, Yangyi Chen, Ming Yan, Fei Huang, et al. Perception-aware policy optimization for multimodal reasoning. arXiv preprint arXiv:2507.06448, 2025d.

Jialin Wu, Wei Shi, Han Shen, Peigui Qi, Kunsheng Tang, Zhicong Huang, Binghao Wang, and Zhou Yang. Revis: Sparse latent steering to mitigate object hallucination in large vision-language models. arXiv preprint arXiv:2602.11824, 2026.

Tong Xiao, Xin Xu, Zhenya Huang, Hongyu Gao, Quan Liu, Qi Liu, and Enhong Chen. Perception-r1: Advancing multimodal reasoning capabilities of mllms via visual perception reward. arXiv preprint arXiv:2506.07218, 2025.

Yilin Yang, Zhenghui Guo, Yuke Wang, Omprakash Gnawali, Sheng Di, and Chengming Zhang. Hii-dpo: Eliminate hallucination via accurate hallucination-inducing counterfactual images. arXiv preprint arXiv:2602.10425, 2026.

Zhihan Yin, Jianxin Liang, Yueqian Wang, Yifeng Yao, Huishuai Zhang, and Dongyan Zhao. Freak: A fine-grained hallucination evaluation benchmark for advanced mllms. arXiv preprint arXiv:2603.19765, 2026.

Qianhao Yuan, Jie Lou, Xing Yu, Hongyu Lin, Le Sun, Xianpei Han, and Yaojie Lu. Vision-opd: Learning to see fine details for multimodal llms via on-policy self-distillation. arXiv preprint arXiv:2605.18740, 2026.

Xiang Yue, Yuansheng Ni, Kai Zhang, Tianyu Zheng, Ruoqi Liu, Ge Zhang, Samuel Stevens, Dongfu Jiang, Weiming Ren, Yuxuan Sun, et al. Mmmu: A massive multi-discipline multimodal understanding and reasoning benchmark for expert agi. In Proceedings ofthe IEEE/CVF conference on computer vision and pattern recognition, pages 9556–9567, 2024.

Yu Yue, Yufeng Yuan, Qiying Yu, Xiaochen Zuo, Ruofei Zhu, Wenyuan Xu, Jiaze Chen, Chengyi Wang, TianTian Fan, Zhengyin Du, et al. Vapo: Efficient and reliable reinforcement learning for advanced reasoning tasks. arXiv preprint arXiv:2504.05118, 2025.

Matthew D. Zeiler and Rob Fergus. Visualizing and understanding convolutional networks. In European Conference on Computer Vision, pages 818–833. Springer, 2014.

Chi Zhang, Haibo Qiu, Qiming Zhang, Yufei Xu, Zhixiong Zeng, Siqi Yang, Peng Shi, Lin Ma, and Jing Zhang. Perceptual-evidence anchored reinforced learning for multimodal reasoning. arXiv preprint arXiv:2511.18437, 2025a.

Juntian Zhang, Song Jin, Chuanqi Cheng, Yuhan Liu, Yankai Lin, Xun Zhang, Yufei Zhang, Fei Jiang, Guojun Yin, Wei Lin, et al. Viper: Empowering the self-evolution of visual perception abilities in vision-language model. arXiv preprint arXiv:2510.24285, 2025b.

Rosie Zhao, Anshul Shah, Xiaoyu Zhu, Xinke Deng, Zhongyu Jiang, Yang Yang, Joerg Liebelt, and Arnab Mondal. On robustness and chain-of-thought consistency of rl-finetuned vlms. arXiv preprint arXiv:2602.12506, 2026.

Table A.1: Complete hyperparameter listing. “Paper notation” gives the corresponding symbol in the main text when applicable.
<table><tr><td>Category</td><td>Parameter</td><td>Value</td><td>Paper notation</td></tr><tr><td colspan="4">RL &amp; optimization</td></tr><tr><td>Learning rate</td><td>lr</td><td> $1 \times 1 0 ^ { - 5 }$ </td><td></td></tr><tr><td>KL penalty coefficient</td><td>kl_coeff</td><td>0.01</td><td></td></tr><tr><td>GRPO group size</td><td>group_size</td><td>32</td><td></td></tr><tr><td>Training steps</td><td>n_steps</td><td>2,000</td><td></td></tr><tr><td>Trainable layers</td><td>n_trainable_layers</td><td>4 (last)</td><td></td></tr><tr><td>Precision</td><td>dtype</td><td>bfloat16</td><td></td></tr><tr><td colspan="4">Generation &amp; sampling</td></tr><tr><td>Temperature</td><td>temperature</td><td>1.0</td><td></td></tr><tr><td>Top-p</td><td>top-p</td><td>0.95</td><td></td></tr><tr><td>Max new tokens (evidence)</td><td>max_new_tokens</td><td>32</td><td></td></tr><tr><td>Max response tokens (full)</td><td>max_response_tokens</td><td>64</td><td></td></tr><tr><td>Prompt format</td><td>short_evidence_v1</td><td></td><td></td></tr><tr><td colspan="4">Reward function (Equation (4))</td></tr><tr><td>Response reward weight</td><td>alpha_resp</td><td>0.70</td><td>see note†</td></tr><tr><td>Answer reward weight</td><td>alpha_ans</td><td>0.30</td><td>see note†</td></tr><tr><td>Response logprob temp.</td><td>tau_resp</td><td>0.20</td><td></td></tr><tr><td>Answer logprob temp.</td><td>tau_ans</td><td>1.00</td><td></td></tr><tr><td>Gate temperature</td><td>tau_resp (shared)</td><td>0.20</td><td>Tg</td></tr><tr><td>Gate baseline at m=0</td><td>(derived)</td><td>0.50</td><td>g(0)</td></tr><tr><td>Evidence tie-breaker</td><td>evidence_eps</td><td>0.10</td><td>Etie</td></tr><tr><td>Additive evidence weight</td><td>evidence_eps (shared)</td><td>0.10</td><td>λ</td></tr><tr><td>Reward clipping</td><td>[min, max]</td><td>[−1.25, 1.00]</td><td></td></tr><tr><td>Format penalty</td><td></td><td>-0.75</td><td></td></tr><tr><td colspan="4">Data &amp; evaluation</td></tr><tr><td>Rerank candidates</td><td>rerank_num_candidates</td><td>6</td><td></td></tr><tr><td>non-evidence Regions per sample</td><td>K</td><td>3</td><td>K</td></tr></table>

<sup>†</sup> In Equation (4), $R _ { \mathrm { a n s } }$ is a composite: R<sub>ans</sub> = alpha\_ans · answer\_score + alpha\_resp · response\_score, where each score is computed from log probabilities scaled by its temperature.

## A Supplementary Experiments and Implementation Details

## A.1 Reproducibility Details

Dataset split and task-family distribution. The training data are derived from COCO val2017 [Lin et al., 2014] after quality filtering and format normalization. This yields 21,758 raw samples, split into train (17,502 valid), validation (2,352 valid), and probe (1,904 valid) subsets. After RL-specific filtering, 15,314 samples are loaded for online training. The loaded training set contains three task families: attribute (6,562), counting (2,188), and spatial (6,564). Training images are drawn from COCO val2017 [Lin et al., 2014]. CountBench [Paiss et al., 2023], SpatialEval [Wang et al., 2024], and MathVista [Lu et al., 2023] use independently sourced evaluation images and share no image-level overlap with the training set; the remaining benchmarks are cited in Section 4 and likewise contain no COCO val2017 images.

Training configuration. Training uses balanced\_no\_replacement sampling for uniform coverage across task families, GRPO group size 32, and 2,000 optimization steps. The trainable part of the model is restricted to the last four layers. Full training and reward hyperparameters are listed in Table A.1.

Broader impacts. CED is a training-time diagnostic and reward component for improving visual grounding in VLMs. It does not directly interact with end users or generate user-facing content. Improved grounding may reduce shortcut-driven errors in safety-relevant visual reasoning tasks. The main risk is that counterfactual probing can also reveal model vulnerabilities, although CED exposes only a scalar evidence margin rather than a detailed attack surface.

Table A.2: Methodological comparison with perception-aware VLM RL methods. The Causal audit column indicates whether the method tests causal evidence dependence for a candidate answer.
<table><tr><td>Method</td><td>Signal source</td><td>Granularity</td><td>Causal audit</td><td>Stage</td></tr><tr><td>PAPO [Wang et al., 2025d]</td><td>Global mask KL</td><td>Global</td><td>No</td><td>Training</td></tr><tr><td>VPPO [Huang et al., 2025]</td><td>Attention weights</td><td>Token-level</td><td>No</td><td>Training</td></tr><tr><td>Vision-SR1†</td><td>Text self-verification</td><td>Description-level</td><td>No</td><td>Training</td></tr><tr><td>PaLMR</td><td>LLM-as-Judge</td><td>Trajectory-level</td><td>No</td><td>Training</td></tr><tr><td>SophiaVL-R1 [Fan et al., 2025]</td><td>Thinking-reward RM</td><td>Trajectory-level</td><td>No</td><td>Training</td></tr><tr><td> $\mathrm { P E A R L } ^ { \bar { \aleph } }$ </td><td>Perception checklist</td><td>Sample-level</td><td>No</td><td>Training</td></tr><tr><td>VAPOπ</td><td>Trajectory anchoring</td><td>Token-level</td><td>No</td><td>Training</td></tr><tr><td> ${ \mathbf { V L M - R 1 } } ^ { * }$ </td><td>Self-verification</td><td>Response-level</td><td>No</td><td>Training</td></tr><tr><td>Perception-  $. \mathbf { R } 1 ^ { \dagger \dagger }$ </td><td>Proxy localization</td><td>Region-levelª</td><td>No</td><td>Training</td></tr><tr><td>CED (Ours)</td><td>Counterfactual intervention</td><td>Region-level</td><td>Yes</td><td>Training</td></tr></table>

<sup>†</sup>Li et al. [2025b]; <sup>‡</sup>Li et al. [2026]; <sup>§</sup>Zhang et al. [2025a]; <sup>¶</sup>Yue et al. [2025]; <sup>\*</sup>Shen et al. [2025]; <sup>††</sup>Xiao et al. [2025].  
<sup>a</sup>Perception-R1 reaches region-level granularity through proxy localization and requires additional supervision.

## A.2 Intervention Implementation Details

Replacement strategies. We evaluate three replacement strategies: mean replacement (default), zero replacement, and Gaussian-noise replacement. All interventions are applied to the last-layer vision-encoder output after spatial merging. Mean replacement substitutes Evidence Region visual tokens with the mean of neighboring visual tokens outside $\mathcal T ( \Omega )$ ; zero replacement sets selected tokens to 0; Gaussian-noise replacement substitutes zero-mean Gaussian samples.

Spatial-merge-aware token mapping. Modern vision encoders apply a 2×2 spatial merge before feeding visual tokens to the LLM. Given merge dimensions $( s _ { w } , s _ { h } ) = ( 2 , 2 )$ , an original grid coordinate $( g _ { x } , g _ { y } )$ maps to the merged-token index

$$
( g _ { y } / / s _ { h } ) \times w _ { \mathrm { m e r g e d } } + ( g _ { x } / / s _ { w } ) .
$$

For non-evidence Region construction, the mapping module supports Chebyshev-distance ring expansion on the merged feature map.

Proposal construction pipeline. Positive proposals are sourced from COCO instance annotations [Lin et al., 2014]. They are object-level bounding boxes, not question-specific region annotations. The Evidence Region $\Omega ^ { \mathrm { e v } }$ is resolved from sample metadata using the priority proposal\_bbox > target\_bbox > argument\_bbox > metadata.bbox > center-box fallback. non-evidence Regions $\{ \Omega _ { k } ^ { \mathrm { n o n } } \}$ are sampled as area-matched random boxes with IoU $\leq 0 . 0 5 \mathrm { t o } \Omega ^ { \mathrm { e v } }$ . If box sampling fails, random visual-token subsets of matching size are used as fallback. Quality diagnostics filter proposals with extreme area fractions or insufficient token coverage before training.

## A.3 Comparison with Perception-Aware RL Methods

Table A.2 compares CED with representative perception-aware VLM RL methods. The key distinction is whether the training signal tests candidate-answer dependence on local visual evidence, rather than coarse image dependence or text-only consistency.

## A.4 Additional Evidence-Signal Diagnostics

Relevant-vs-random intervention. On a held-out set of 500 samples per task family, we compare Evidence Region sensitivity $s ( \Omega ^ { \mathrm { e v } } )$ with mean non-evidence Region sensitivity $\mu ( s ^ { \mathrm { n o n } } )$ . On counting tasks, the Evidence Region elicits higher sensitivity in 63.4% of samples, with mean Evidence Region $s = 2 . 5 6 6$ versus mean non-evidence Region $s = 0 . 6 3 8 .$ . On presence tasks, the rate drops to 55.0%, with mean Evidence Region $s = 1 . 0 8 2$ versus mean non-evidence Region $s = 0 . 3 0 2$ . This supports the regime separation used by the routing rule in Section 3.2.

Table A.3: Cross-model evidence sensitivity validation (N=50 per task per model).
<table><tr><td>Model</td><td>Task</td><td>Relevant &gt; Random rate</td><td>Mean margin</td></tr><tr><td rowspan="2">InternVL3.5-8B</td><td>Counting</td><td>0.68</td><td>0.0070</td></tr><tr><td>Presence</td><td>0.62</td><td>0.0737</td></tr><tr><td rowspan="2">LLaVA-v1.6-7B</td><td>Counting</td><td>0.78</td><td>0.0074</td></tr><tr><td>Presence</td><td>0.60</td><td>0.1625</td></tr></table>

Table A.4: Blindfold test results (N=500 per task family).

<table><tr><td>Condition</td><td>Task</td><td>Rel. &gt; Rand. rate</td><td>Mean Delta</td></tr><tr><td>Normal</td><td>Counting</td><td>0.634</td><td>+1.928</td></tr><tr><td>Normal</td><td>Presence</td><td>0.550</td><td>+0.780</td></tr><tr><td>Blindfold</td><td>Counting</td><td>0.404</td><td>-0.114</td></tr><tr><td>Blindfold</td><td>Presence</td><td>0.448</td><td>+0.070</td></tr></table>

Cross-model validation. We also validate the signal on InternVL3.5-8B [Wang et al., 2025b] and LLaVA-v1.6-Mistral-7B [Li et al., 2024] using pixel-level intervention. Table A.3 shows that counting tasks maintain higher relevant-vs-random rates across both models, while presence tasks remain weaker.

Blindfold test. After replacing the image with a blank input, the relevant-vs-random rate drops to 0.404 on counting and 0.448 on presence, both below the 0.50 chance level. Mean delta collapses from $+ 1 . 9 2 8 / + \bar { 0 . 7 } 8 0 \mathrm { t o } - 0 . 1 1 \bar { 4 } / + 0 . 0 7 0$ , confirming that the signal originates from real image content.

## A.5 Intervention-Type Ablations

Why mean replacement reduces intervention artifacts. The perturbation ablation shows that mean replacement gives the strongest discrimination within the local intervention family: AUC 0.669 for mean replacement, compared with 0.641 for zero replacement and 0.629 for Gaussian-noise replacement. This ordering follows from the role of the replacement as a structural baseline. Write the Evidence Region token representation as

$$
h _ { T } = b _ { T } + e _ { T } ,\tag{5}
$$

where $b _ { T }$ is a context-consistent baseline component and $e _ { T }$ is the answer-relevant evidence component. The ideal counterfactual removes $e _ { T }$ while preserving $b _ { T } .$ . Replacement strategies differ in how much they perturb this baseline:

$$
h _ { T } ^ { \mathrm { m e a n } } = \mu _ { T } = b _ { T } + \delta _ { T } , ~ h _ { T } ^ { \mathrm { z e r o } } = 0 , ~ h _ { T } ^ { \mathrm { n o i s e } } = b _ { T } + \xi _ { T } .\tag{6}
$$

Let F be the downstream logit assigned to the candidate answer and $J _ { T }$ its local Jacobian with respect to $h _ { T } . \mathrm { A }$ first-order expansion gives

$$
\Delta F ^ { \mathrm { m e a n } } \approx J _ { T } ( \delta _ { T } - e _ { T } ) , \Delta F ^ { \mathrm { z e r o } } \approx - J _ { T } ( b _ { T } + e _ { T } ) , \Delta F ^ { \mathrm { n o i s e } } \approx J _ { T } ( \xi _ { T } - e _ { T } ) .\tag{7}
$$

All three contain the desired signal term $- J _ { T } e _ { T }$ . Mean replacement adds only the neighborhoodoffset artifact $J _ { T } \delta _ { T } ,$ zero replacement adds the systematic baseline-removal artifact $- J _ { T } b _ { T }$ , and Gaussian replacement adds sample-specific noise. Since context mixing makes the neighborhood offset smaller than the full baseline norm at the intervention layer, mean replacement preserves the non-evidence part of the representation more faithfully.

AUC ablation and global masking. Table A.5 reports the local perturbation-family ablation. Global masking performs worse: it does not support stable answer-conditioned discrimination, with above-baseline rate 0.490 below chance. Local counterfactual intervention retains discriminative utility with AUC 0.620.

## A.6 Reward Hyperparameter Sensitivity

Tables A.7 and A.8 show that the default reward hyperparameters lie in stable regions. Across $\lambda \in [ 0 . 0 5 , 0 . 2 0 ]$ , the non-constant reward rate remains 96–100%. For $\tau _ { g } ,$ values around 0.15–0.30 yield balanced selection behavior; we use $\tau _ { g } = 0 . 2 0$ by default.

Table A.5: Perturbation-family ablation within the local intervention family, evaluated by logits-JS AUC.
<table><tr><td>Key mode</td><td>Mean repl.</td><td>Zero repl.</td><td>Gaussian-noise repl.</td></tr><tr><td>prompt_last</td><td>0.6780</td><td>0.6602</td><td>0.6299</td></tr><tr><td>answer_first</td><td>0.6592</td><td>0.6215</td><td>0.6273</td></tr><tr><td>Average</td><td>0.6686</td><td>0.6409</td><td>0.6286</td></tr></table>

Table A.6: Gaussian-noise profile under prompt\_last. Stability drops under logits\_only.
<table><tr><td>Config</td><td>Fixed metric</td><td>Best metric</td><td>Best paired AUC</td></tr><tr><td>logits24</td><td>0.6299</td><td>0.6299</td><td>0.7108</td></tr><tr><td>logits_only</td><td>0.5753</td><td>0.5920</td><td>0.6407</td></tr></table>

Table A.7: Evidence weight (λ) sensitivity. $\lambda = 0 . 0 0$ is correctness-only.
<table><tr><td>λ</td><td>Non-const. rate</td><td>Reward std</td><td>Zero-var. rate</td></tr><tr><td>0.00</td><td>100%</td><td>0.0528</td><td>0%</td></tr><tr><td>0.05</td><td>100%</td><td>0.0508</td><td>0%</td></tr><tr><td>0.10</td><td>96%</td><td>0.0597</td><td>4%</td></tr><tr><td>0.15</td><td>100%</td><td>0.0415</td><td>4%</td></tr><tr><td>0.20</td><td>100%</td><td>0.0491</td><td>0%</td></tr></table>

Table A.8: Gate temperature $( \tau _ { g } )$ sensitivity.
<table><tr><td> $\tau _ { g }$ </td><td>Non-const. rate</td><td>Reward std</td><td>Zero-var. rate</td></tr><tr><td>0.10</td><td>100%</td><td>0.0568</td><td>4%</td></tr><tr><td>0.20</td><td>96%</td><td>0.0597</td><td>4%</td></tr><tr><td>0.30</td><td>96%</td><td>0.0469</td><td>4%</td></tr><tr><td>0.50</td><td>100%</td><td>0.0378</td><td>0%</td></tr></table>

## A.7 Proposal Robustness to Spatial Perturbations

This experiment tests whether the CED probe remains useful when the target proposal is imperfect. It is orthogonal to Section A.5: that subsection varies the intervention type while holding the region fixed; here we hold the intervention type fixed as mean replacement and vary the region.

Protocol. Starting from the true Evidence Region box of each sample, we generate perturbed proposals and re-run the full CED pipeline with K=3 non-evidence Regions. We test three perturbation axes: IoU stratification with the original box, scale changes around the box center, and translations by a fixed fraction of the image short side. A random region baseline gives the expected floor without spatial targeting. We report mean evidence margin m¯ , evidence-non-evidence gap $\Delta = \mu ( s ^ { \mathrm { e v } } ) - \mu ( s ^ { \mathrm { n o n } } )$ , and evidence-beats-random rate $\mathrm { P r } ( s ^ { \mathrm { \bar { e v } } } > s ^ { \mathrm { r a n d } } )$ . All numbers use the Qwen3.5-9B CoT-CED checkpoint on n=41 count-exclusion samples.

Interpreting the results. IoU gives the cleanest trend: m¯ and ∆ both decrease as overlap with the original proposal drops. The lowest IoU bin approaches the random floor, indicating that CED does not merely reward masking magnitude. Scale and shift perturbations do not show systematic degradation within the tested ranges. Their evidence-reference gaps stay well above the random baseline, suggesting that moderate detector imprecision is a second-order effect for this diagnostic. All measurements here are probe diagnostics rather than downstream accuracy estimates.

## A.8 Shared-Candidate Baselines and Reward Diagnostics

Unified-condition protocol. Recent perception-aware methods differ in backbone and data. We therefore separate checkpoint transfer from signal design by evaluating lightweight method variants under a shared-candidate protocol with the same backbone, candidate pool, and benchmark manifest.

Table A.9: Proposal-perturbation results on count-exclusion (n=41). Higher values indicate stronger evidence dependence; the random row gives the floor without spatial targeting.
<table><tr><td>Axis</td><td>Condition</td><td>m</td><td>∆</td><td>Rel. rate</td></tr><tr><td rowspan="4">IoU stratification</td><td>[0.7, 1.0]</td><td>0.501</td><td>2.032</td><td>0.732</td></tr><tr><td>[0.5, 0.7)</td><td>0.379</td><td>1.282</td><td>0.683</td></tr><tr><td>[0.3, 0.5)</td><td>0.341</td><td>1.386</td><td>0.683</td></tr><tr><td>[0.0, 0.3)</td><td>0.219</td><td>0.555</td><td>0.561</td></tr><tr><td rowspan="4">Scale</td><td>0.50×</td><td>0.377</td><td>1.113</td><td>0.732</td></tr><tr><td>0.75×</td><td>0.481</td><td>1.750</td><td>0.732</td></tr><tr><td>1.25×</td><td>0.433</td><td>2.230</td><td>0.683</td></tr><tr><td>1.50× 2.00×</td><td>0.295</td><td>2.003</td><td>0.634</td></tr><tr><td rowspan="3">Shift</td><td></td><td>0.382</td><td>1.880</td><td>0.707</td></tr><tr><td>5% 10%</td><td>0.304 0.428</td><td>1.602 1.457</td><td>0.634 0.707</td></tr><tr><td>20%</td><td>0.532</td><td>1.899</td><td>0.732</td></tr><tr><td colspan="2">original proposal (reference)</td><td>0.386</td><td>1.852</td><td>0.683</td></tr><tr><td colspan="2">random region (floor)</td><td>0.147</td><td>0.277</td><td>0.537</td></tr></table>

![](images/efc1826bda018ed9b940439201fccf4accbfc190148f308eab168eaf2141bded.jpg)  
Figure A.1: CED probe robustness under proposal perturbation on the count-exclusion diagnostic. (a) Mean evidence margin m¯ across IoU bins, with the random-region baseline as a grey dashed reference. (b,c) m¯ under scale and translation perturbations, with the original ±1 SE band in red. Error bars are ±1 SE.

Table A.10: Unified-condition baseline comparison on the offline rerank dataset (N=1,353).
<table><tr><td>Method</td><td>Reward mean</td><td>Signal strength</td><td>Signal-corr</td></tr><tr><td>Vanilla GRPO</td><td>-0.149</td><td>N/A</td><td>N/A</td></tr><tr><td>PAPO-Lite</td><td>-0.156</td><td> $\mathrm { K L = 0 . 0 2 4 }$ </td><td>0.034</td></tr><tr><td>CED (Ours)</td><td>+0.448</td><td> $\mathrm { M a r g i n } = - 0 . 0 0 7$ </td><td>Selective</td></tr></table>

Shared-candidate comparison. Table A.11 reports Lite versions of representative methods on the counting shared-candidate slice. The key readout is not final accuracy alone, which is saturated on this slice, but whether the reward can produce non-constant within-group signal and flip candidate preference beyond log-probability ranking.

Within-group variance telemetry. Correctness-only has within-group zero-variance rate 0.949, non-constant rate 0.051, and same-answer-different-reward discrimination 0.0. Additive and ours reduce the zero-variance rate to 0.035 and restore the non-constant rate to 0.965. Ours gives slightly higher discrimination, 0.555 versus 0.535. Re-scoring the pre-RL checkpoint gives a yes/no shortcut bias gap of 0.077 for Correctness-only, 0.075 for Additive, and 0.015 for ours. The intervention area-reward Pearson correlation is 0.080, ruling out area-driven reward hacking. Reward-length correlations are consistent across methods: −0.226, −0.222, and −0.230.

Table A.11: Unified-condition method comparison on the counting shared-candidate slice: 94 samples with at least two distinct candidates.
<table><tr><td>Method</td><td>Acc.</td><td>Strong inf.</td><td> $r _ { \mathrm { n c } } \uparrow$ </td><td>flip ↑</td></tr><tr><td>LogProb</td><td>94.7</td><td>75.0</td><td></td><td>一</td></tr><tr><td>Correctness-only</td><td>97.9</td><td>100.0</td><td>12.8</td><td>4.3</td></tr><tr><td>CED (Ours)</td><td>97.9</td><td>100.0</td><td>100.0</td><td>76.6</td></tr><tr><td>Perception-R1-Lite</td><td>97.9</td><td>100.0</td><td>13.8</td><td>5.3</td></tr><tr><td>VLM-R1-Lite*</td><td>94.7</td><td>75.0</td><td>0.0</td><td>0.0</td></tr><tr><td>VPPO-Lite*</td><td>94.7</td><td>75.0</td><td>0.0</td><td>0.0</td></tr><tr><td>PAPO-Lite*</td><td>94.7</td><td>75.0</td><td>0.0</td><td>0.0</td></tr></table>

<sup>∗</sup> No reward-based reranking recovered; falls back to log probability.

## A.9 Reward Discrimination and Failure Modes

The same-answer-different-reward statistic in Table 1 is visualized in Figure A.2. Rollouts with the same final answer receive different rewards once the evidence margin enters the signal, reflecting differences in the visual evidence each rollout uses.

Under Correctness-only, evidence-intensive tasks exhibit low within-group discrimination, with nonconstant raw reward rate $r _ { \mathrm { n c } } \approx 0 . 0 5$ and zero-variance rate ≈ 0.95. Additive and Routed rewards restore discrimination, with $r _ { \mathrm { n c } } \approx 0 . 9 7$ and zero-variance rate ≈ 0.04. On the presence probe, all formulations remain limited by the binary-task variance bound, supporting the routing of presence tasks to the audit pathway.

## A.10 Scope and Extensions of the Evidence Interface

Behavioral target. CED is designed to reward a model behavior: a candidate answer should be supported by the visual evidence that justifies it. In the causal view of grounding, this means that the model’s support for an answer should decrease more under intervention on the target-evidence path than under matched interventions on non-evidence paths. This requirement is not specific to bounding boxes or object regions.

Region-level instantiation. In this paper, we instantiate the audit with object-centric region interventions because regions provide a scalable interface for constructing Evidence Regions and matched non-evidence Regions without question-specific evidence annotations. This choice aligns with the benchmark families studied in our experiments, including counting, spatial reasoning, hallucination detection, and object-centric visual reasoning, where many failures arise when the model answers from language priors, scene context, or salient distractors rather than the relevant local evidence.

Beyond object boxes. In the causal graph of Figure 1, CED rewards a path-level property: the answer should depend more on the target-evidence path than on shortcut or nuisance paths. Objectregion interventions query this property by probing one spatial locus of the evidence path without question-specific evidence annotations, making the audit scalable to open-ended VQA training. The behavioral target itself is defined on the graph structure, not on the intervention format. Richer evidence interfaces such as attribute-preserving interventions, multi-region proposals, or text-span units query the same path at finer granularity or for different evidence types; they refine how the evidence path is probed, not what behavior is rewarded.

## A.11 Answer-CED vs. CoT-CED Details

The two variants differ in where the evidence sensitivity is computed: CoT-CED applies the counterfactual to the full reasoning trace, while Answer-CED applies it only to the final answer. Both variants are trained for 2,000 steps on Qwen3.5-9B with LoRA (r=16, α=32). The main paper reports the training trajectories in Figure 4; here, Table A.12 summarizes the final training state and Tables A.13 and A.14 provide the behavior-level diagnostics.

CoT-CED achieves higher training reward (Table A.12, Figure 4), yet transfers worse on average (Table 5). This reflects a structural mismatch between dense per-token rewards and GRPO’s grouprelative optimization. CoT-CED averages evidence rewards over the full reasoning trace, and because

[2] raw=Evidence: orange and green on sticker Final answer: 2 [31 reward=0.2567final='2 [31 reward=0.2567final='2'

![](images/52c3cbe97b77d657aa70e39859270f58deb0de18ed1dcb1cba2281492d0f4af2.jpg)

Routed | family=counting   
Q: How many distinct colored elements on the sticker of the   
fruit at [199, 51, 126, 132] are not blue?   
Shared final answer: '2   
Reward span: 0.6674   
Routed | family=counting   
Q: How many framed pictures on the table at [122, 340, 437,   
419] do not have a yellow border?   
Shared final answer: '1'   
Reward span: 0.5097   
[1] reward=0.6797 final='1 raw=Evidence: one picture with blue and white frame Final   
answer: 1   
[2] reward=0.3289final='1 raw=Evidence: one framed picture with blue patterned   
border Final answer: 1   
[3] reward=0.2209 final='1 raw=Evidence: one picture with blue patterned border Final   
answer: 1   
Routed | family=counting   
Q: How many poles within the slope area at [0, 126, 500, 203]   
are not black?   
Shared final answer: '1'   
Reward span: 0.5032

raw=Evidence: one yellow and one green Final answer: 2

![](images/81e8f892c3389c8c1a1dd922bba21be41d5fb0b7e10b06248890cd9eee95e590.jpg)

![](images/7aa7c422d423c40bca7d024e154b5d28323f1e604b2b5c66f02acac327a864b0.jpg)

Figure A.2: Qualitative examples of same-answer-different-reward under the CED method. All rollouts share the same answer, while CED produces reward spans of 0.50–0.67 according to visual evidence quality.  
Table A.12: CoT-CED vs. Answer-CED: training-end summary over 2,000 steps.
<table><tr><td>Metric</td><td>CoT-CED</td><td>Answer-CED</td></tr><tr><td>Mean training reward</td><td>+0.259</td><td>-0.009</td></tr><tr><td>Final training correctness</td><td>43.4%</td><td>34.2%</td></tr></table>

trace length is policy-controlled, the model can raise the per-token average by truncating low-reward tokens rather than by improving visual grounding. Tables A.13–A.14 confirm this collapse: CoT-CED’s mean chain shrinks to 3.6 tokens on counting (vs. 49.3 for Answer-CED), degenerating to object-cue shorthand. This parallels the process-reward hacking reported by Guo et al. [2025], who abandon dense process rewards in favor of outcome-level signals for the same reason. Answer-CED removes this degree of freedom by scoring only the final-answer span, a fixed-length interface whose reward cannot be manipulated through generation length.

All No | Pre-RL   
Q: Is there a remote in the image   
[1] ans='no' reward=1.0000 raw=Evidence: no remote visible in image Final answer: no   
[2] ans='no' reward=1.0000 raw=Evidence: no remote visible Final answer: no

![](images/834f0aa0324ac19fcd5f5531795814bdfc005e92a9a21262dde858487590bda1.jpg)  
Figure A.3: Within-group zero-variance rate across task families. Evidence-intensive tasks show a large reduction from correctness-only reward to our reward; binary-dominated groups remain near high zero-variance because of their two-action structure.  
Existence failure cases

![](images/03778a62cf507a77c32092ed4167aa10fe13db878ea147f6d43f4310e0201451.jpg)

![](images/cbbd1355aab5a70b58a7cc879450beef29697bacf34df82b04ee74c4ab070955.jpg)  
Reward Tie | Pre-RL  
Q: Is there a remote in the image?  
[1] ans='no' reward=1.0000 raw=Evidence: no remote visible in image Final answer: no [2] ans='no' reward=1.0000 raw=Evidence: no remote visible Final answer: no  
Figure A.4: Failure cases on presence tasks: identical negation answers with identical rewards yield zero within-group variance.

## A.12 Formalizing Evidence-Closed Self-Evolution

This appendix provides the complete formalization of the evidence-closed self-evolution regime introduced in Section 5.

Notation. Let $O _ { t } = ( I _ { t } , Q _ { t } )$ denote the image-question pair, $\hat { Y } _ { t }$ the prediction, $V _ { t } = \nu ( I _ { t } )$ the task-relevant visual evidence, $G _ { t } \in \{ 0 , 1 \}$ the grounding indicator, and $S _ { t }$ the endogenous reward.

Table A.13: End-of-training CoT behavior on held-out prompts. CoT-CED collapses toward an object-cue answer format, while Answer-CED preserves natural multi-sentence reasoning.
<table><tr><td>Metric</td><td>Benchmark</td><td>CoT-CED</td><td>Answer-CED</td></tr><tr><td>Mean CoT length (tokens)</td><td>Counting</td><td>3.6</td><td>49.3</td></tr><tr><td>Median CoT length (tokens)</td><td>Counting</td><td>3</td><td>47</td></tr><tr><td>p90 CoT length (tokens)</td><td>Counting</td><td>6</td><td>78</td></tr><tr><td>Mean CoT length (tokens)</td><td>HallusionBench</td><td>3.8</td><td>82.1</td></tr><tr><td>Median CoT length (tokens)</td><td>HallusionBench</td><td>3</td><td>61</td></tr><tr><td>p90 CoT length (tokens)</td><td>HallusionBench</td><td>6</td><td>173</td></tr><tr><td>Image-referential opener rate</td><td>Counting</td><td>1.0%</td><td>79.8%</td></tr><tr><td>Image-referential opener rate</td><td>HallusionBench</td><td>5.2%</td><td>64.2%</td></tr><tr><td>Unique-token ratio</td><td>Counting</td><td>99.1%</td><td>75.8%</td></tr><tr><td>Unique-token ratio</td><td>HallusionBench</td><td>96.8%</td><td>68.1%</td></tr></table>

Table A.14: Representative side-by-side generations. Both variants produce the correct final answer, but CoT-CED reduces the chain to an object cue, while Answer-CED keeps an explicit visual check.
<table><tr><td>Prompt</td><td>CoT-CED</td><td>Answer-CED</td></tr><tr><td>How many beds are there in the image?</td><td>The beds  $^ { \prime 2 }$ </td><td>Got it, let&#x27;s look at the image. There&#x27;s a loft bed with a lower bed. The upper bunk is one, the lower bed is another. So that&#x27;s two beds.</td></tr><tr><td>How many weights are there in the image?</td><td>The weights/Two</td><td>Got it, let&#x27;s look at the image. The man is holding two dumbbells, one in each hand. There&#x27;s one in the left hand and one in the right hand. So that&#x27;s two weights.</td></tr></table>

Definition 1 (Evidence-closed self-evolution). A training step is evidence-closed if its signal $T _ { t } ^ { \mathrm { c l } }$ is measurable with respect to $\boldsymbol { { B } } _ { t } = \sigma ( \mathcal { F } _ { t } , I _ { t } , Q _ { t } , \hat { Y } _ { t } , S _ { t } )$

Lemma 1 (Endogenous reward bottleneck). $I f S _ { t } \perp \perp I _ { t } \mid ( \hat { Y } _ { t } , Q _ { t } , \mathcal { F } _ { t } )$ , then $I ( S _ { t } ; V _ { t } \mid \hat { Y } _ { t } , Q _ { t } , \mathcal { F } _ { t } ) =$ 0.

Proof. Since $V _ { t } = \nu ( I _ { t } )$ , the conditional independence implies $S _ { t } \perp \perp V _ { t } \mid ( \hat { Y } _ { t } , Q _ { t } , \mathcal { F } _ { t } )$ , which gives the result. □

Proposition 1 (No incremental grounding information). $I f T _ { t } ^ { \mathrm { c l } }$ is evidence-closed, then $I ( T _ { t } ^ { \mathrm { c l } } ; G _ { t } \ |$ $B _ { t } ) \bar { = } 0 .$

Proof. $T _ { t } ^ { \mathrm { c l } }$ is $B _ { t }$ -measurable, so conditioning on $B _ { t }$ leaves no remaining uncertainty in $T _ { t } ^ { \mathrm { c l } }$ that can carry additional information about $G _ { t }$ □

Proposition 2 (Closed-loop reward does not identify grounding). If two predictors induce the same distribution over $( I _ { t } , Q _ { t } , \hat { Y } _ { t } , S _ { t } )$ but differ in grounding, then any objective of the form $J ( h ) =$ $\mathbb { E } _ { h } [ \phi ( I _ { t } , Q _ { t } , \hat { Y } _ { t } , S _ { t } ) ]$ cannot distinguish them.

Proof. The objective depends only on the joint distribution of $( I _ { t } , Q _ { t } , \hat { Y } _ { t } , S _ { t } )$ . If two predictors have the same joint distribution over these variables, they have the same value of $J ( h )$ regardless of their grounding behavior. □

Assumption 1 (Audit informativeness). On evidence-intensive tasks, $I ( A _ { t } ; G _ { t } \mid B _ { t } ) > 0 ,$ , where $A _ { t }$ denotes the evidence audit signal.

Proposition 3 (Information increment from evidence auditing). Under Assumption 1, $H ( G _ { t } \mid$ $B _ { t } , { \bf \dot { A } } _ { t } ) < H ( G _ { t } \mid B _ { t } )$ .

Proof. By the definition of conditional mutual information, ${ \cal { I } } ( A _ { t } ; G _ { t } \ | \ B _ { t } ) \ = \ { \cal { H } } ( G _ { t } \ | \ B _ { t } ) \ -$ $H ( \boldsymbol { \dot { G } } _ { t } \mid \boldsymbol { \dot { B } } _ { t } , \boldsymbol { A } _ { t } )$ . The assumption makes the left-hand side strictly positive, giving the stated strict inequality. □