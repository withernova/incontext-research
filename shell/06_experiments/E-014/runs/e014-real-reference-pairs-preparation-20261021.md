# e014-real-reference-pairs-preparation-20261021 · 直接执行已讨论的Reference成对数据方案：基于真实TAO train标注及现有冻结候选，核实同Query换Reference对应不同答案的可用量并导出普通

- 父 Run：`e014-historical-three-source-train8367-generation-20261019`
- 来源版本：2026-10-19T20:25:15
- 状态：failed
- Workspace：03

## 本次任务
直接执行已讨论的Reference成对数据方案：基于真实TAO train标注及现有冻结候选，核实同Query换Reference对应不同答案的可用量并导出普通SFT/匹配预算控制输入。原始标注与图像/候选SHA核验、视频拆分、真实接受拒绝都记录，不追加GT；准备过程无GPU。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确运行配对方向。CPU读取已钉住SHA的TAO原始train标注和8367训练源中的499TAO视频，合并三组已有冻结候选（step200/SFT659/instances650）；仅重编号并保留source mapping，不改候选/顺序/目标或补GT。按同Query同类别异track选择Reference，优先原Reference帧，否则最早非Query帧；调用既有reference-pairs CLI核验身份/图像SHA/框/两不同答案/best>=.5/gap>.05/已有留出视频排除/seed20260901视频15%拆分。保存所有接受拒绝；非空后导出两行普通SFT、A-only等行数控制和双Reference验证输入。实际可用量决定后续轻量训练；零数据也保留真实不足结论。无GPU/模型推理/训练。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'1eb2fca8ee28409baf283656af8210836cfa3a50c56cdd7049c3b45ff43debfb'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-20261021/metrics.json

## 结果
尚无结果。

### Claim 边界
仅生成，绝不补GT/混组/选择SFT或测试集生成，不自动恢复任何旧训练。指标仅描述训练候选而非泛化。legacy evaluator不记录逐例EOS标记；EOS停止默认生效但不是显式终止审计，后续入库需声明限制。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
