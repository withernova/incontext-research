
## Prompt protocol correction

`prompting/messages.py` and `datasets/iploc.py` now expose two explicit
protocols. The default `focus` protocol follows FOCUS §5.1: one fixed prompt,
interleaved support image/BBOX inputs, a box-free query image, and one
`<answer>[xyxy]</answer>` target without category text. The optional `iploc`
protocol follows IPLoc §3.1–§3.3: same-sequence shots conditioned on a shared
real or pseudo category name with input/human turns masked. IPLoc-ID is not a
source for either base SFT protocol.
