# Prompt and training protocol evidence

The training protocol is grounded in the locally ingested MinerU versions of:

- **IPLoc**: *Teaching VLMs to Localize Specific Objects from In-context
  Examples* (arXiv:2411.13317; local PDF SHA-256
  `0f9a9ad3a84da85172ae52335814b12683705dd066d368fde245d4041fdf78d3`).
- **FOCUS**: *Forcing In-Context Object Localization through Visual Support
  Constraints and Policy Optimization* (arXiv:2605.31145; citekey
  `focusfor2026`; local PDF SHA-256
  `2bc9af3713f20730b04d862bbb57d461774ad5521e4b7df0d1eaf10f7ab79391`).

## FOCUS protocol (default)

FOCUS prepends one fixed task instruction, interleaves support images with their
BBOX annotations, appends the query image without a box, and supervises the
final answer in this exact outer form:

```text
<answer>[x_min, y_min, x_max, y_max]</answer>
```

It intentionally contains no category or pseudo-name. The target is defined
only by visual support images and support boxes. See [[focusfor2026]] §5.1
Prompt Specification and Eq. 4. The paper's first stage combines language-model
loss with a query-image-token → support-BBOX-token attention margin loss; the
second stage uses GRPO with IoU and format rewards. See [[focusfor2026]]
§5.2–§5.4. The current code implements the prompt and standard LM-loss SFT
baseline only; attention loss and GRPO remain explicit future components.

## IPLoc protocol (optional ablation)

IPLoc builds semantically coherent 1–8-shot conversations from frames tracking
the same object within one video. Support inputs include images, a shared real
category or per-conversation pseudo-name, and support boxes; human/input turns
are masked and the assistant predicts query coordinates with next-token LM
loss. Pseudo-names regularize reliance on visual context. See the locally
fetched IPLoc paper §3.1 ICL Instruction Tuning Conversations, §3.2 Data Mixes,
and §3.3 Fine-tuning.

## Deliberate non-source

IPLoc-ID is not the primary source for these SFT prompt protocols. Its
candidate-then-identify and Yes/No extension is a separate task and must only be
added through an explicitly named protocol/evaluator.
