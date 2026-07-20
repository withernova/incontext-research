# E004-R-001-synthetic-double-instance-behavior-n4

- 状态：completed / behavioral gate failed
- 性质：synthetic causal-design sanity；不是自然图像机制证据。
- 远端目录：`/home/featurize/work/mechanism/explog/E-004/runs/E004-R-001-synthetic-double-instance-behavior-n4/`
- 数据：airplane、basketball、bear、bicycle，各用同类别不同 LaSOT sequences 的 context-padded object crops；独立 letterbox 到224×224 cell并合成灰色双面板；4 quartets/16 conditions。
- 设计：Reference A/B × Candidate A/B；matched期望Yes、mismatched期望No。
- score：forced assistant candidate+question 后 next-token `logit(Yes)-logit(No)`。
- 结果：accuracy=9/16=0.5625；0/4 quartets 四条件全对。各 quartet 的 matched−mismatched mean margin 分别为0.5625、0.125、0.71875、0.125，均为正但不足以通过离散行为 gate。
- 结论：prompt 对 identity relation 存在弱的方向性 margin信号，但模型未可靠解决 synthetic 2×2 verification；按预注册 gate，不应直接进行并解释大规模 causal-head scan。
- 替代解释：合成域偏移、crop/背景泄漏、A/B视觉难度、当前位置偏差、LoRA未见这种双面板格式，或模型本身缺乏稳定binding。
- 下一步：先做 hook correctness smoke；数据侧应增加真实同图双实例，或扩大/筛选仅用于寻找行为可解释 quartet，但筛选必须在独立 discovery/evaluation subsets 上，防止按 outcome cherry-pick。
- 审核：`config/run.md`、`logs/run.log`、`results/outputs.json`、`analysis/summary.json`、`manifests/manifest.json`。
