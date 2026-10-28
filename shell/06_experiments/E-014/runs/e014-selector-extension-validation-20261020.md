# e014-selector-extension-validation-20261020 · 用户在四项代码交付后明确授权“可以部署运行”。部署7caae090351c9c71ce65fd8c98a0bbbbb1825bc6后，先执行一次有限验证：候选换

- 父 Run：`e014-historical-balanced-vqa-step4041-test1766-20261020`
- 来源版本：2026-10-20T11:19:55
- 状态：failed
- Workspace：03

## 本次任务
用户在四项代码交付后明确授权“可以部署运行”。部署7caae090351c9c71ce65fd8c98a0bbbbb1825bc6后，先执行一次有限验证：候选换序映射/无效回答统计、裁剪像素与角色顺序、LR端点和二次恢复、少量真实输入的train/eval processor编码；原始TAO配对证据可用性只作核验，不训练、不改变历史产物。通过后另登记step4041固定1766换序P1诊断。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：一次性验收输入脚本SHA=e090ef64786aa5e64fbfa0cc9c69c90b1a61fedae80d6b6126e84aa51a89bd8f。已部署7caae09；合成候选排列、无效统计、裁剪像素/顺序、真实AdamW小参数的LR端点与二次恢复；三数据集各一个真实图片processor编码train/eval一致性。生成模型为明确标记的编码stub，模型推理0、训练更新0；不作为真实TAO配对规模或训练收益证据。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import hashlib,pathlib; assert hashlib.sha256(pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-20261020/inputs/validate_extensions.py'"'"').read_bytes()).hexdigest()=='"'"'e090ef64786aa5e64fbfa0cc9c69c90b1a61fedae80d6b6126e84aa51a89bd8f'"'"'' && env PYTHONPATH=. OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-20261020/inputs/validate_extensions.py /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-20261020
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-20261020/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-20261020/payload
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-20261020/metrics.json

## 结果
尚无结果。

### Claim 边界
暂停训练不自动恢复，不宣称完成4epoch。较旧模型数据、采样、预算同时变化，测试集又已反复探索，不是单因果或无偏泛化。只评测最新完整step4041，不选其它checkpoint。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
