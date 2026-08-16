# Reference→Query correspondence 假设定向检索（2026-08-11）

## 待检验假设
在 ICOL 自然 bbox 生成阶段，query-localization heads 若不能从 reference object 建立可靠的对象条件/对应关系，则其在 query image 上的空间 attention 更容易错配，最终导致 bbox 错误。

> 本文是 GATHER 工作笔记，不是 validated synthesis；所有结论均限于已抓取 PDF。

## 检索覆盖与退化情况
- 已实际检索：OpenAlex、Semantic Scholar、arXiv；查询记录见 `shell/02_search/search_log.md`。
- Semantic Scholar 随后触发 HTTP 429；arXiv出现 timeout/429。相关失败已由脚本写入 search log，故本轮为 **degraded search**，不能声称穷尽文献。
- OpenAlex对长自然语言MLLM查询噪声很大；改用方法名/任务名（tracking、visual in-context、personalized segmentation）后获得有效候选。
- 已抓取并hash：[[ostrack2022]]、[[mixformer2022]]、[[seggpt2023]]、[[painter2023]]、[[persam2023]]。

## 最相关论文及与假设的关系

### 1. PerSAM：最接近具体机制
PerSAM从 reference mask 内抽取多个局部视觉特征，与 test/query image 每个位置计算 cosine similarity，聚合成 location confidence map，再用该 map 引导 decoder token-to-image cross-attention。它直接采用“reference内部视觉表征 → 跨图对应图 → query目标聚焦”的链条。[[persam2023]] §3.2

**对我们的启发：**
- 假设应从“query head是否理解reference”精化为可测量的：
  1. reference-object-conditioned correspondence 是否正确；
  2. correspondence 是否预测 query GT；
  3. 下游 query heads 是否采用该 correspondence。
- 比 residual stream 注入更贴近假设的干预，是对 reference-object→query-token correspondence 做局部、预算保持的 knockout/替换。

### 2. OSTrack：target awareness 与query/search判别力
OSTrack明确指出，分离 template/search 特征抽取和后续relation modeling会使特征缺少target awareness、限制target-background discriminability；它用早期拼接和堆叠attention进行迭代feature matching，使search feature被template动态条件化。[[ostrack2022]] §1 Introduction, §3.1

**与假设关系：**结构性支持“reference没有参与query feature形成会造成定位判别不足”。但它没有证明MLLM某个head的Q→R差会导致同head Q→Q差。

### 3. MixFormer：方向上更贴近Q→R
MixFormer迭代执行template/search mixed attention；尤其指出template-query→search方向可能受distractors影响而可裁剪，核心是search/query表征读取template/reference并形成target-specific search features。[[mixformer2022]] §3.1

**与假设关系：**支持重点考察自然bbox rows 的 search/query→template/reference 信息流；同时提示成功机制是多层coupled feature learning，而非单次人工注入。

### 4. SegGPT：reference dependence通常需要训练目标强制
SegGPT用随机颜色映射消除固定颜色捷径，迫使模型依赖context；feature ensemble在每个attention layer后让query聚合reference examples。[[seggpt2023]] §3.1, §3.2

**与假设关系：**支持“有reference token不等于模型自然会正确使用”；如果现有SFT没有显式reference-counterfactual约束，query-only捷径很合理。

### 5. Painter：context应进入自然联合forward
Painter通过MIM训练使预测conditioned on visible example patches，并将示例与query共同参与forward。[[painter2023]] §Abstract, §3.2

**与假设关系：**广义支持自然context-conditioned computation；不直接覆盖实例身份对应。

## 当前最安全结论
1. **存在很强的相邻文献支持**：reference/template信息若未充分进入query/search feature形成，target-specific定位会受损。[[ostrack2022]] §1 Introduction [[mixformer2022]] §Abstract
2. **存在与我们机制非常接近的方法先例**：PerSAM显式构造reference-object local features到query/test locations的correspondence map，并用它引导cross-attention。[[persam2023]] §3.2
3. **尚未找到直接论文**证明：在autoregressive MLLM中，同一组bbox query heads的Q→R GT alignment下降，因而导致Q→Q GT alignment下降并造成bbox错误。该具体链条仍可能是我们的实验gap，但本轮搜索退化，不能宣称novel。
4. 现有文献更支持**迭代联合表征/显式correspondence/训练期context dependence**，不支持把固定source residual加到后层作为核心机制验证。

## 建议的新实验表述
将原假设改写为三层：

- H1（reference read）：自然bbox rows的冻结query heads能否在reference span内对准reference object？
- H2（correspondence）：其reference-object-conditioned attention/similarity分布能否预测query GT，而非仅有总Q→R mass？
- H3（behavioral mediation）：H1/H2较差是否中介Q→Q GT alignment下降及bbox错误？

优先先做无干预同row链式审计；若H1→H2→H3成立，再做head-local Q→R object contribution knockout，而不是whole-residual injection。

## 边界
- tracking/segmentation论文是架构邻近证据，不是MLLM机制证据。
- attention map不是“理解”的充分指标；需要spatial quality、counterfactual specificity和行为关联共同成立。
- 所有上述声明保持 `supported/partial` 级别，尚未经R2和人工Claim gate，不进入validated synthesis。
