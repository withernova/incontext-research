# E-015 · 实验结果

> 记录截至：2026-10-28T11:10:00。记录更新不等于实际运行完成；程序完成也不等于科研结论成立。

## 结果摘要（survey-tool 管理）
（Experiment 级摘要待登记；以下保留已登记 Run 的结果。）

## 对 Claims 的影响（survey-tool 管理）
（待人工判断；不会自动提升 Claim）

## 局限性（survey-tool 管理）
（待补充）

## 运行汇总（survey-tool 管理）

### 历史未分组 (`legacy`)

| Run / 名称 | Seed | 当前状态 | 最近记录更新 | 已登记数值 |
|---|---|---|---|---|
| [e015-multishot-data-preparation-20261021](runs/e015-multishot-data-preparation-20261021.md) · 构造同查询的多帧数据 | 20260901 | failed | 2026-10-21T19:05:15 | 尚无已登记数值；不表示没有产物 |
| [e015-multishot-data-preparation-r2-20261021](runs/e015-multishot-data-preparation-r2-20261021.md) · 仅修复TAO原始验证集标注文件名为validation.json；保持原数据准备定义和所有原始输入，不复用失败目录。用户本次已授权完成E015数据与pipeli | 20260901 | approved | 2026-10-21T19:09:52 | 尚无已登记数值；不表示没有产物 |
| [e015-multishot-data-preparation-r3-20261021](runs/e015-multishot-data-preparation-r3-20261021.md) · 前次仅预检因部署超时而未执行。部署完成后按完全相同的修正版输入进行一次数据准备。 | 20260901 | failed | 2026-10-21T19:11:38 | 尚无已登记数值；不表示没有产物 |
| [e015-multishot-data-preparation-r4-20261021](runs/e015-multishot-data-preparation-r4-20261021.md) · 只修正PIL尺寸读取属性，保持所有数据、采样、排除和哈希审计定义，继续完成已授权E015数据准备。 | 20260901 | failed | 2026-10-21T19:36:35 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-sft-selector-ddp4x2-capability-20261021](runs/e015-qwen2-sft-selector-ddp4x2-capability-20261021.md) · 双卡副本的多帧训练检查 | 11451 | failed | 2026-10-21T20:01:16 | 尚无已登记数值；不表示没有产物 |
| [e015-multishot-data-preparation-r5-20261021](runs/e015-multishot-data-preparation-r5-20261021.md) · 复用已完成六份清单（训练10175、测试1728），重核同Query/GT/索引和SHA；仅复核被排除记录并记录原因。GRPO中保留原始行与奖励，对无效中间参考 | 20260901 | analysis_pending | 2026-10-21T19:53:23 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-4shot-sft-grpo-vqa-20261021](runs/e015-qwen2-4shot-sft-grpo-vqa-20261021.md) · Qwen2四参考帧完整方法训练与同模型多shot评测 | 11451 | failed | 2026-10-23T20:18:56 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-selector-ddp4x2-capability-20261021](runs/e015-qwen2-selector-ddp4x2-capability-20261021.md) · 修正选择器配置并仅补跑选择训练/五图推理，复核父Run已通过SFT阶段；继续用户授权E015完整任务。 | 11451 | failed | 2026-10-21T20:16:36 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-vqa-ddp4x2-capability-20261021](runs/e015-qwen2-vqa-ddp4x2-capability-20261021.md) · 修正两卡副本早期同步的设备编号，只补跑五图VQA，所有已通过训练阶段不重复；继续E015。 | 11451 | failed | 2026-10-21T20:26:08 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-vqa-actual-budget4096-20261021](runs/e015-qwen2-vqa-actual-budget4096-20261021.md) · 修正Qwen2真实图像预算并补测输入grid；保留全部历史证据，继续独立E015正式pipeline。 | 11451 | failed | 2026-10-21T20:32:48 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-vqa-actual-budget4096-r2-20261021](runs/e015-qwen2-vqa-actual-budget4096-r2-20261021.md) · 使用实际Qwen3 processor配置修正回归测试导入，继续CPU和五图预算验证。 | 11451 | analysis_pending | 2026-10-21T20:40:04 | 尚无已登记数值；不表示没有产物 |
| [e015-iploc144-qwen2-4shot-restart-20261023](runs/e015-iploc144-qwen2-4shot-restart-20261023.md) · IPLoc官方144修正划分后Qwen2四参考帧重新训练 | 11451 | draft | 2026-10-23T20:50:22 | 尚无已登记数值；不表示没有产物 |
| [e015-iploc144-qwen2-4shot-restart-r2-20261023](runs/e015-iploc144-qwen2-4shot-restart-r2-20261023.md) · IPLoc官方144修正划分后Qwen2四参考帧重新训练 | 11451 | failed | 2026-10-23T20:53:40 | 尚无已登记数值；不表示没有产物 |
| [e015-iploc144-qwen2-4shot-restart-r3-20261023](runs/e015-iploc144-qwen2-4shot-restart-r3-20261023.md) · IPLoc官方144修正划分后Qwen2四参考帧重新训练 | 11451 | analysis_pending | 2026-10-26T01:10:11 | 关键结果：IPLoc144 1shot VQA mIoU=60.93249183877414 percent；关键结果：IPLoc144 1shot VQA Acc50=67.36111111111111 percent；关键结果：IPLoc144 1shot Proposal Oracle mIoU=60.93249183877414 percent；关键结果：IPLoc144 1shot Proposal Oracle Acc50=67.36111111111111 percent；关键结果：IPLoc144 1shot Oracle与实际mIoU差距=0.0 percentage_points；关键结果：IPLoc144 1shot 候选可命中但未选中数量=0 count；关键结果：IPLoc144 2shot VQA mIoU=61.162480906632446 percent；关键结果：IPLoc144 2shot VQA Acc50=65.97222222222221 percent；关键结果：IPLoc144 2shot Proposal Oracle mIoU=61.98003586156338 percent；关键结果：IPLoc144 2shot Proposal Oracle Acc50=66.66666666666666 percent；关键结果：IPLoc144 2shot Oracle与实际mIoU差距=0.8175549549309324 percentage_points；关键结果：IPLoc144 2shot 候选可命中但未选中数量=1 count；关键结果：IPLoc144 4shot VQA mIoU=65.23348855828748 percent；关键结果：IPLoc144 4shot VQA Acc50=72.91666666666666 percent；关键结果：IPLoc144 4shot Proposal Oracle mIoU=65.38908655975659 percent；关键结果：IPLoc144 4shot Proposal Oracle Acc50=72.91666666666666 percent；关键结果：IPLoc144 4shot Oracle与实际mIoU差距=0.15559800146911495 percentage_points；关键结果：IPLoc144 4shot 候选可命中但未选中数量=0 count；指标观测：IPLoc144 1shot VQA mIoU=60.93249183877414 percent；指标观测：IPLoc144 1shot VQA Acc50=67.36111111111111 percent；指标观测：IPLoc144 1shot Proposal Oracle mIoU=60.93249183877414 percent；指标观测：IPLoc144 1shot Proposal Oracle Acc50=67.36111111111111 percent；指标观测：IPLoc144 1shot Oracle与实际mIoU差距=0.0 percentage_points；指标观测：IPLoc144 1shot 候选可命中但未选中数量=0 count；指标观测：IPLoc144 2shot VQA mIoU=61.162480906632446 percent；指标观测：IPLoc144 2shot VQA Acc50=65.97222222222221 percent；指标观测：IPLoc144 2shot Proposal Oracle mIoU=61.98003586156338 percent；指标观测：IPLoc144 2shot Proposal Oracle Acc50=66.66666666666666 percent；指标观测：IPLoc144 2shot Oracle与实际mIoU差距=0.8175549549309324 percentage_points；指标观测：IPLoc144 2shot 候选可命中但未选中数量=1 count；指标观测：IPLoc144 4shot VQA mIoU=65.23348855828748 percent；指标观测：IPLoc144 4shot VQA Acc50=72.91666666666666 percent；指标观测：IPLoc144 4shot Proposal Oracle mIoU=65.38908655975659 percent；指标观测：IPLoc144 4shot Proposal Oracle Acc50=72.91666666666666 percent；指标观测：IPLoc144 4shot Oracle与实际mIoU差距=0.15559800146911495 percentage_points；指标观测：IPLoc144 4shot 候选可命中但未选中数量=0 count |
| [e015-three-dataset-eval-20261026](runs/e015-three-dataset-eval-20261026.md) · 用户授权使用已完成E015模型联合评测LaSOT/GOT10k/TAO的1/2/4shot。复用父GRPO与selector及LaSOT144预测；新增GOT1 | 20260901 | analysis_pending | 2026-10-26T15:15:01 | 关键结果：jointval_lasot_vqa_miou_1shot=60.93249183877414 percent；关键结果：jointval_lasot_score_miou_1shot=59.06520773132588 percent；关键结果：jointval_lasot_oracle_miou_1shot=60.93249183877414 percent；关键结果：jointval_lasot_vqa_acc50_1shot=67.36111111111111 percent；关键结果：jointval_lasot_score_acc50_1shot=65.27777777777779 percent；关键结果：jointval_lasot_oracle_acc50_1shot=67.36111111111111 percent；关键结果：jointval_got10k_vqa_miou_1shot=76.72734942773748 percent；关键结果：jointval_got10k_score_miou_1shot=77.31695533583304 percent；关键结果：jointval_got10k_oracle_miou_1shot=77.31695533583304 percent；关键结果：jointval_got10k_vqa_acc50_1shot=82.77777777777777 percent；关键结果：jointval_got10k_score_acc50_1shot=83.33333333333334 percent；关键结果：jointval_got10k_oracle_acc50_1shot=83.33333333333334 percent；关键结果：jointval_tao_vqa_miou_1shot=62.08848199525181 percent；关键结果：jointval_tao_score_miou_1shot=62.31441567475361 percent；关键结果：jointval_tao_oracle_miou_1shot=63.546319671871174 percent；关键结果：jointval_tao_vqa_acc50_1shot=67.15025906735751 percent；关键结果：jointval_tao_score_acc50_1shot=67.46113989637306 percent；关键结果：jointval_tao_oracle_acc50_1shot=68.9119170984456 percent；关键结果：jointval_pooled_vqa_miou_1shot=64.00355845399083 percent；关键结果：jointval_pooled_score_miou_1shot=64.0464336694322 percent；关键结果：jointval_pooled_oracle_miou_1shot=65.17729190736164 percent；关键结果：jointval_pooled_vqa_acc50_1shot=69.35608999224205 percent；关键结果：jointval_pooled_score_acc50_1shot=69.43366951124904 percent；关键结果：jointval_pooled_oracle_acc50_1shot=70.75252133436773 percent；关键结果：jointval_macro_vqa_miou_1shot=66.58277442058781 percent；关键结果：jointval_macro_score_miou_1shot=66.23219291397083 percent；关键结果：jointval_macro_oracle_miou_1shot=67.26525561549278 percent；关键结果：jointval_macro_vqa_acc50_1shot=72.42971598541547 percent；关键结果：jointval_macro_score_acc50_1shot=72.02408366916139 percent；关键结果：jointval_macro_oracle_acc50_1shot=73.20212051429668 percent；关键结果：jointval_lasot_vqa_miou_2shot=61.162480906632446 percent；关键结果：jointval_lasot_score_miou_2shot=60.78279528273303 percent；关键结果：jointval_lasot_oracle_miou_2shot=61.98003586156338 percent；关键结果：jointval_lasot_vqa_acc50_2shot=65.97222222222221 percent；关键结果：jointval_lasot_score_acc50_2shot=65.27777777777779 percent；关键结果：jointval_lasot_oracle_acc50_2shot=66.66666666666666 percent；关键结果：jointval_got10k_vqa_miou_2shot=78.93338946581325 percent；关键结果：jointval_got10k_score_miou_2shot=79.32342481529638 percent；关键结果：jointval_got10k_oracle_miou_2shot=79.32342481529638 percent；关键结果：jointval_got10k_vqa_acc50_2shot=85.55555555555556 percent；关键结果：jointval_got10k_score_acc50_2shot=86.11111111111111 percent；关键结果：jointval_got10k_oracle_acc50_2shot=86.11111111111111 percent；关键结果：jointval_tao_vqa_miou_2shot=69.38132026112342 percent；关键结果：jointval_tao_score_miou_2shot=69.6223584901695 percent；关键结果：jointval_tao_oracle_miou_2shot=70.63971067177198 percent；关键结果：jointval_tao_vqa_acc50_2shot=75.5440414507772 percent；关键结果：jointval_tao_score_acc50_2shot=75.75129533678756 percent；关键结果：jointval_tao_oracle_acc50_2shot=76.99481865284974 percent；关键结果：jointval_pooled_vqa_miou_2shot=69.79703755344111 percent；关键结果：jointval_pooled_score_miou_2shot=69.989538347929 percent；关键结果：jointval_pooled_oracle_miou_2shot=70.88492042597241 percent；关键结果：jointval_pooled_vqa_acc50_2shot=75.87276958882855 percent；关键结果：jointval_pooled_score_acc50_2shot=76.02792862684251 percent；关键结果：jointval_pooled_oracle_acc50_2shot=77.11404189294026 percent；关键结果：jointval_macro_vqa_miou_2shot=69.82573021118971 percent；关键结果：jointval_macro_score_miou_2shot=69.90952619606631 percent；关键结果：jointval_macro_oracle_miou_2shot=70.64772378287724 percent；关键结果：jointval_macro_vqa_acc50_2shot=75.69060640951832 percent；关键结果：jointval_macro_score_acc50_2shot=75.71339474189215 percent；关键结果：jointval_macro_oracle_acc50_2shot=76.59086547687583 percent；关键结果：jointval_lasot_vqa_miou_4shot=65.23348855828748 percent；关键结果：jointval_lasot_score_miou_4shot=65.38908655975659 percent；关键结果：jointval_lasot_oracle_miou_4shot=65.38908655975659 percent；关键结果：jointval_lasot_vqa_acc50_4shot=72.91666666666666 percent；关键结果：jointval_lasot_score_acc50_4shot=72.91666666666666 percent；关键结果：jointval_lasot_oracle_acc50_4shot=72.91666666666666 percent；关键结果：jointval_got10k_vqa_miou_4shot=82.19969489966476 percent；关键结果：jointval_got10k_score_miou_4shot=82.19969489966476 percent；关键结果：jointval_got10k_oracle_miou_4shot=82.19969489966476 percent；关键结果：jointval_got10k_vqa_acc50_4shot=90.0 percent；关键结果：jointval_got10k_score_acc50_4shot=90.0 percent；关键结果：jointval_got10k_oracle_acc50_4shot=90.0 percent；关键结果：jointval_tao_vqa_miou_4shot=73.05563864241168 percent；关键结果：jointval_tao_score_miou_4shot=73.53099737136853 percent；关键结果：jointval_tao_oracle_miou_4shot=74.01252082579934 percent；关键结果：jointval_tao_vqa_acc50_4shot=79.48186528497409 percent；关键结果：jointval_tao_score_acc50_4shot=79.89637305699482 percent；关键结果：jointval_tao_oracle_acc50_4shot=80.51813471502591 percent；关键结果：jointval_pooled_vqa_miou_4shot=73.45869567436793 percent；关键结果：jointval_pooled_score_miou_4shot=73.83195190839031 percent；关键结果：jointval_pooled_oracle_miou_4shot=74.19244076294869 percent；关键结果：jointval_pooled_vqa_acc50_4shot=80.21722265321955 percent；关键结果：jointval_pooled_score_acc50_4shot=80.52754072924748 percent；关键结果：jointval_pooled_oracle_acc50_4shot=80.99301784328937 percent；关键结果：jointval_macro_vqa_miou_4shot=73.49627403345464 percent；关键结果：jointval_macro_score_miou_4shot=73.70659294359663 percent；关键结果：jointval_macro_oracle_miou_4shot=73.86710076174023 percent；关键结果：jointval_macro_vqa_acc50_4shot=80.79951065054692 percent；关键结果：jointval_macro_score_acc50_4shot=80.93767990788714 percent；关键结果：jointval_macro_oracle_acc50_4shot=81.14493379389752 percent；指标观测：jointval_lasot_vqa_miou_1shot=60.93249183877414 percent；指标观测：jointval_lasot_score_miou_1shot=59.06520773132588 percent；指标观测：jointval_lasot_oracle_miou_1shot=60.93249183877414 percent；指标观测：jointval_lasot_vqa_acc50_1shot=67.36111111111111 percent；指标观测：jointval_lasot_score_acc50_1shot=65.27777777777779 percent；指标观测：jointval_lasot_oracle_acc50_1shot=67.36111111111111 percent；指标观测：jointval_got10k_vqa_miou_1shot=76.72734942773748 percent；指标观测：jointval_got10k_score_miou_1shot=77.31695533583304 percent；指标观测：jointval_got10k_oracle_miou_1shot=77.31695533583304 percent；指标观测：jointval_got10k_vqa_acc50_1shot=82.77777777777777 percent；指标观测：jointval_got10k_score_acc50_1shot=83.33333333333334 percent；指标观测：jointval_got10k_oracle_acc50_1shot=83.33333333333334 percent；指标观测：jointval_tao_vqa_miou_1shot=62.08848199525181 percent；指标观测：jointval_tao_score_miou_1shot=62.31441567475361 percent；指标观测：jointval_tao_oracle_miou_1shot=63.546319671871174 percent；指标观测：jointval_tao_vqa_acc50_1shot=67.15025906735751 percent；指标观测：jointval_tao_score_acc50_1shot=67.46113989637306 percent；指标观测：jointval_tao_oracle_acc50_1shot=68.9119170984456 percent；指标观测：jointval_pooled_vqa_miou_1shot=64.00355845399083 percent；指标观测：jointval_pooled_score_miou_1shot=64.0464336694322 percent；指标观测：jointval_pooled_oracle_miou_1shot=65.17729190736164 percent；指标观测：jointval_pooled_vqa_acc50_1shot=69.35608999224205 percent；指标观测：jointval_pooled_score_acc50_1shot=69.43366951124904 percent；指标观测：jointval_pooled_oracle_acc50_1shot=70.75252133436773 percent；指标观测：jointval_macro_vqa_miou_1shot=66.58277442058781 percent；指标观测：jointval_macro_score_miou_1shot=66.23219291397083 percent；指标观测：jointval_macro_oracle_miou_1shot=67.26525561549278 percent；指标观测：jointval_macro_vqa_acc50_1shot=72.42971598541547 percent；指标观测：jointval_macro_score_acc50_1shot=72.02408366916139 percent；指标观测：jointval_macro_oracle_acc50_1shot=73.20212051429668 percent；指标观测：jointval_lasot_vqa_miou_2shot=61.162480906632446 percent；指标观测：jointval_lasot_score_miou_2shot=60.78279528273303 percent；指标观测：jointval_lasot_oracle_miou_2shot=61.98003586156338 percent；指标观测：jointval_lasot_vqa_acc50_2shot=65.97222222222221 percent；指标观测：jointval_lasot_score_acc50_2shot=65.27777777777779 percent；指标观测：jointval_lasot_oracle_acc50_2shot=66.66666666666666 percent；指标观测：jointval_got10k_vqa_miou_2shot=78.93338946581325 percent；指标观测：jointval_got10k_score_miou_2shot=79.32342481529638 percent；指标观测：jointval_got10k_oracle_miou_2shot=79.32342481529638 percent；指标观测：jointval_got10k_vqa_acc50_2shot=85.55555555555556 percent；指标观测：jointval_got10k_score_acc50_2shot=86.11111111111111 percent；指标观测：jointval_got10k_oracle_acc50_2shot=86.11111111111111 percent；指标观测：jointval_tao_vqa_miou_2shot=69.38132026112342 percent；指标观测：jointval_tao_score_miou_2shot=69.6223584901695 percent；指标观测：jointval_tao_oracle_miou_2shot=70.63971067177198 percent；指标观测：jointval_tao_vqa_acc50_2shot=75.5440414507772 percent；指标观测：jointval_tao_score_acc50_2shot=75.75129533678756 percent；指标观测：jointval_tao_oracle_acc50_2shot=76.99481865284974 percent；指标观测：jointval_pooled_vqa_miou_2shot=69.79703755344111 percent；指标观测：jointval_pooled_score_miou_2shot=69.989538347929 percent；指标观测：jointval_pooled_oracle_miou_2shot=70.88492042597241 percent；指标观测：jointval_pooled_vqa_acc50_2shot=75.87276958882855 percent；指标观测：jointval_pooled_score_acc50_2shot=76.02792862684251 percent；指标观测：jointval_pooled_oracle_acc50_2shot=77.11404189294026 percent；指标观测：jointval_macro_vqa_miou_2shot=69.82573021118971 percent；指标观测：jointval_macro_score_miou_2shot=69.90952619606631 percent；指标观测：jointval_macro_oracle_miou_2shot=70.64772378287724 percent；指标观测：jointval_macro_vqa_acc50_2shot=75.69060640951832 percent；指标观测：jointval_macro_score_acc50_2shot=75.71339474189215 percent；指标观测：jointval_macro_oracle_acc50_2shot=76.59086547687583 percent；指标观测：jointval_lasot_vqa_miou_4shot=65.23348855828748 percent；指标观测：jointval_lasot_score_miou_4shot=65.38908655975659 percent；指标观测：jointval_lasot_oracle_miou_4shot=65.38908655975659 percent；指标观测：jointval_lasot_vqa_acc50_4shot=72.91666666666666 percent；指标观测：jointval_lasot_score_acc50_4shot=72.91666666666666 percent；指标观测：jointval_lasot_oracle_acc50_4shot=72.91666666666666 percent；指标观测：jointval_got10k_vqa_miou_4shot=82.19969489966476 percent；指标观测：jointval_got10k_score_miou_4shot=82.19969489966476 percent；指标观测：jointval_got10k_oracle_miou_4shot=82.19969489966476 percent；指标观测：jointval_got10k_vqa_acc50_4shot=90.0 percent；指标观测：jointval_got10k_score_acc50_4shot=90.0 percent；指标观测：jointval_got10k_oracle_acc50_4shot=90.0 percent；指标观测：jointval_tao_vqa_miou_4shot=73.05563864241168 percent；指标观测：jointval_tao_score_miou_4shot=73.53099737136853 percent；指标观测：jointval_tao_oracle_miou_4shot=74.01252082579934 percent；指标观测：jointval_tao_vqa_acc50_4shot=79.48186528497409 percent；指标观测：jointval_tao_score_acc50_4shot=79.89637305699482 percent；指标观测：jointval_tao_oracle_acc50_4shot=80.51813471502591 percent；指标观测：jointval_pooled_vqa_miou_4shot=73.45869567436793 percent；指标观测：jointval_pooled_score_miou_4shot=73.83195190839031 percent；指标观测：jointval_pooled_oracle_miou_4shot=74.19244076294869 percent；指标观测：jointval_pooled_vqa_acc50_4shot=80.21722265321955 percent；指标观测：jointval_pooled_score_acc50_4shot=80.52754072924748 percent；指标观测：jointval_pooled_oracle_acc50_4shot=80.99301784328937 percent；指标观测：jointval_macro_vqa_miou_4shot=73.49627403345464 percent；指标观测：jointval_macro_score_miou_4shot=73.70659294359663 percent；指标观测：jointval_macro_oracle_miou_4shot=73.86710076174023 percent；指标观测：jointval_macro_vqa_acc50_4shot=80.79951065054692 percent；指标观测：jointval_macro_score_acc50_4shot=80.93767990788714 percent；指标观测：jointval_macro_oracle_acc50_4shot=81.14493379389752 percent |
| [e015-qwen2-selector-e014data-20261026](runs/e015-qwen2-selector-e014data-20261026.md) · 用户明确要求先用E014丰富选择数据替换当前VQA阶段数据，诊断提升幅度，之后再解决数据来源。原样使用E014冻结21552行/8203 source_inde | 20260901 | failed | 2026-10-26T16:00:08 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-selector-e014clean-20261026](runs/e015-qwen2-selector-e014clean-20261026.md) · 用户纠正：去掉可能影响当前测试集的旧E014数据。排除当前作者LaSOT36测试类别（含TAO内LaSOT来源），排除三数据集1/2/4shot全部测试源视频（ | 20260901 | analysis_pending | 2026-10-27T10:39:10 | 关键结果：diag_e014clean_lasot_vqa_miou_1shot=60.24948934008074 percent；关键结果：diag_e014clean_lasot_vqa_acc50_1shot=66.66666666666666 percent；关键结果：diag_e014clean_lasot_delta_vqa_miou_1shot=-0.6830024986933978 percentage_points；关键结果：diag_e014clean_got10k_vqa_miou_1shot=77.31695533583304 percent；关键结果：diag_e014clean_got10k_vqa_acc50_1shot=83.33333333333334 percent；关键结果：diag_e014clean_got10k_delta_vqa_miou_1shot=0.5896059080955638 percentage_points；关键结果：diag_e014clean_tao_vqa_miou_1shot=63.31027965084585 percent；关键结果：diag_e014clean_tao_vqa_acc50_1shot=68.60103626943005 percent；关键结果：diag_e014clean_tao_delta_vqa_miou_1shot=1.2217976555940382 percentage_points；关键结果：diag_e014clean_pooled_vqa_miou_1shot=64.92428106166629 percent；关键结果：diag_e014clean_pooled_vqa_acc50_1shot=70.4422032583398 percent；关键结果：diag_e014clean_pooled_delta_vqa_miou_1shot=0.920722607675458 percentage_points；关键结果：diag_e014clean_macro_vqa_miou_1shot=66.95890810891987 percent；关键结果：diag_e014clean_macro_vqa_acc50_1shot=72.86701208981002 percent；关键结果：diag_e014clean_macro_delta_vqa_miou_1shot=0.37613368833206096 percentage_points；关键结果：diag_e014clean_lasot_vqa_miou_2shot=61.36961192652692 percent；关键结果：diag_e014clean_lasot_vqa_acc50_2shot=65.97222222222221 percent；关键结果：diag_e014clean_lasot_delta_vqa_miou_2shot=0.2071310198944758 percentage_points；关键结果：diag_e014clean_got10k_vqa_miou_2shot=79.13086819660238 percent；关键结果：diag_e014clean_got10k_vqa_acc50_2shot=86.11111111111111 percent；关键结果：diag_e014clean_got10k_delta_vqa_miou_2shot=0.19747873078912903 percentage_points；关键结果：diag_e014clean_tao_vqa_miou_2shot=69.97817606517961 percent；关键结果：diag_e014clean_tao_vqa_acc50_2shot=76.16580310880829 percent；关键结果：diag_e014clean_tao_delta_vqa_miou_2shot=0.5968558040561902 percentage_points；关键结果：diag_e014clean_pooled_vqa_miou_2shot=70.2945851789811 percent；关键结果：diag_e014clean_pooled_vqa_acc50_2shot=76.41582622187742 percent；关键结果：diag_e014clean_pooled_delta_vqa_miou_2shot=0.4975476255399798 percentage_points；关键结果：diag_e014clean_macro_vqa_miou_2shot=70.15955206276963 percent；关键结果：diag_e014clean_macro_vqa_acc50_2shot=76.08304548071388 percent；关键结果：diag_e014clean_macro_delta_vqa_miou_2shot=0.33382185157992694 percentage_points；关键结果：diag_e014clean_lasot_vqa_miou_4shot=65.23348855828748 percent；关键结果：diag_e014clean_lasot_vqa_acc50_4shot=72.91666666666666 percent；关键结果：diag_e014clean_lasot_delta_vqa_miou_4shot=0.0 percentage_points；关键结果：diag_e014clean_got10k_vqa_miou_4shot=81.56340126592931 percent；关键结果：diag_e014clean_got10k_vqa_acc50_4shot=88.88888888888889 percent；关键结果：diag_e014clean_got10k_delta_vqa_miou_4shot=-0.6362936337354483 percentage_points；关键结果：diag_e014clean_tao_vqa_miou_4shot=72.87637171041258 percent；关键结果：diag_e014clean_tao_vqa_acc50_4shot=79.17098445595855 percent；关键结果：diag_e014clean_tao_delta_vqa_miou_4shot=-0.17926693199909494 percentage_points；关键结果：diag_e014clean_pooled_vqa_miou_4shot=73.23563481831556 percent；关键结果：diag_e014clean_pooled_vqa_acc50_4shot=79.82932505818464 percent；关键结果：diag_e014clean_pooled_delta_vqa_miou_4shot=-0.22306085605237058 percentage_points；关键结果：diag_e014clean_macro_vqa_miou_4shot=73.22442051154313 percent；关键结果：diag_e014clean_macro_vqa_acc50_4shot=80.32551333717136 percent；关键结果：diag_e014clean_macro_delta_vqa_miou_4shot=-0.2718535219115097 percentage_points；指标观测：diag_e014clean_lasot_vqa_miou_1shot=60.24948934008074 percent；指标观测：diag_e014clean_lasot_vqa_acc50_1shot=66.66666666666666 percent；指标观测：diag_e014clean_lasot_delta_vqa_miou_1shot=-0.6830024986933978 percentage_points；指标观测：diag_e014clean_got10k_vqa_miou_1shot=77.31695533583304 percent；指标观测：diag_e014clean_got10k_vqa_acc50_1shot=83.33333333333334 percent；指标观测：diag_e014clean_got10k_delta_vqa_miou_1shot=0.5896059080955638 percentage_points；指标观测：diag_e014clean_tao_vqa_miou_1shot=63.31027965084585 percent；指标观测：diag_e014clean_tao_vqa_acc50_1shot=68.60103626943005 percent；指标观测：diag_e014clean_tao_delta_vqa_miou_1shot=1.2217976555940382 percentage_points；指标观测：diag_e014clean_pooled_vqa_miou_1shot=64.92428106166629 percent；指标观测：diag_e014clean_pooled_vqa_acc50_1shot=70.4422032583398 percent；指标观测：diag_e014clean_pooled_delta_vqa_miou_1shot=0.920722607675458 percentage_points；指标观测：diag_e014clean_macro_vqa_miou_1shot=66.95890810891987 percent；指标观测：diag_e014clean_macro_vqa_acc50_1shot=72.86701208981002 percent；指标观测：diag_e014clean_macro_delta_vqa_miou_1shot=0.37613368833206096 percentage_points；指标观测：diag_e014clean_lasot_vqa_miou_2shot=61.36961192652692 percent；指标观测：diag_e014clean_lasot_vqa_acc50_2shot=65.97222222222221 percent；指标观测：diag_e014clean_lasot_delta_vqa_miou_2shot=0.2071310198944758 percentage_points；指标观测：diag_e014clean_got10k_vqa_miou_2shot=79.13086819660238 percent；指标观测：diag_e014clean_got10k_vqa_acc50_2shot=86.11111111111111 percent；指标观测：diag_e014clean_got10k_delta_vqa_miou_2shot=0.19747873078912903 percentage_points；指标观测：diag_e014clean_tao_vqa_miou_2shot=69.97817606517961 percent；指标观测：diag_e014clean_tao_vqa_acc50_2shot=76.16580310880829 percent；指标观测：diag_e014clean_tao_delta_vqa_miou_2shot=0.5968558040561902 percentage_points；指标观测：diag_e014clean_pooled_vqa_miou_2shot=70.2945851789811 percent；指标观测：diag_e014clean_pooled_vqa_acc50_2shot=76.41582622187742 percent；指标观测：diag_e014clean_pooled_delta_vqa_miou_2shot=0.4975476255399798 percentage_points；指标观测：diag_e014clean_macro_vqa_miou_2shot=70.15955206276963 percent；指标观测：diag_e014clean_macro_vqa_acc50_2shot=76.08304548071388 percent；指标观测：diag_e014clean_macro_delta_vqa_miou_2shot=0.33382185157992694 percentage_points；指标观测：diag_e014clean_lasot_vqa_miou_4shot=65.23348855828748 percent；指标观测：diag_e014clean_lasot_vqa_acc50_4shot=72.91666666666666 percent；指标观测：diag_e014clean_lasot_delta_vqa_miou_4shot=0.0 percentage_points；指标观测：diag_e014clean_got10k_vqa_miou_4shot=81.56340126592931 percent；指标观测：diag_e014clean_got10k_vqa_acc50_4shot=88.88888888888889 percent；指标观测：diag_e014clean_got10k_delta_vqa_miou_4shot=-0.6362936337354483 percentage_points；指标观测：diag_e014clean_tao_vqa_miou_4shot=72.87637171041258 percent；指标观测：diag_e014clean_tao_vqa_acc50_4shot=79.17098445595855 percent；指标观测：diag_e014clean_tao_delta_vqa_miou_4shot=-0.17926693199909494 percentage_points；指标观测：diag_e014clean_pooled_vqa_miou_4shot=73.23563481831556 percent；指标观测：diag_e014clean_pooled_vqa_acc50_4shot=79.82932505818464 percent；指标观测：diag_e014clean_pooled_delta_vqa_miou_4shot=-0.22306085605237058 percentage_points；指标观测：diag_e014clean_macro_vqa_miou_4shot=73.22442051154313 percent；指标观测：diag_e014clean_macro_vqa_acc50_4shot=80.32551333717136 percent；指标观测：diag_e014clean_macro_delta_vqa_miou_4shot=-0.2718535219115097 percentage_points |
| [e015-qwen2-tier3-grpo-20261027](runs/e015-qwen2-tier3-grpo-20261027.md) · 用户授权修改奖励并重启GRPO，持续记录多框率等指标。复用e015-iploc144-qwen2-4shot-restart-r3-20261023的SFT63 | 11451 | failed | 2026-10-27T14:33:54 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-tier3-ddp8-probe-20261027](runs/e015-qwen2-tier3-ddp8-probe-20261027.md) · 用户明确要求试8卡单副本DDP能否运行，并授权直接停止当前4x2训练；父Run完成18步后终止、无checkpoint、日志保留。独立8步能力短测，从同SFT6 | 11451 | failed | 2026-10-27T14:56:36 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-tier3-ddp8-full-20261027](runs/e015-qwen2-tier3-ddp8-full-20261027.md) · 用户在8卡DDP短测完成4步并核验无OOM记录后，明确要求进行完整训练。新的独立Run从同一SFT636 adapter重新初始化GRPO，8进程×1GPU，4 | 11451 | failed | 2026-10-27T20:17:02 | 尚无已登记数值；不表示没有产物 |
| [e015-multibox-history-reward-audit-20261027](runs/e015-multibox-history-reward-audit-20261027.md) · 用户明确要求分析过去多框率较高的样本，解释当前单框收缩。独立CPU衍生分析：冻结同Qwen2/SFT636/4shot/数据的旧discovery400步128 | 11451 | analysis_pending | 2026-10-27T19:21:20 | 关键结果：history_audit_old_rollouts=12800 count；关键结果：history_audit_current_rollouts=5376 count；关键结果：history_audit_old_last100_original_multi=9.35960591133005 percent；关键结果：history_audit_old_last100_collage_multi=80.7741116751269 percent；关键结果：history_audit_current_last20_original_multi=0.5747126436781609 percent；关键结果：history_audit_current_last20_collage_multi=2.054794520547945 percent；指标观测：history_audit_old_rollouts=12800 count；指标观测：history_audit_current_rollouts=5376 count；指标观测：history_audit_old_last100_original_multi=9.35960591133005 percent；指标观测：history_audit_old_last100_collage_multi=80.7741116751269 percent；指标观测：history_audit_current_last20_original_multi=0.5747126436781609 percent；指标观测：history_audit_current_last20_collage_multi=2.054794520547945 percent |
| [e015-qwen2-cleanvqa-e014-proposals1766-20261027](runs/e015-qwen2-cleanvqa-e014-proposals1766-20261027.md) · 用户明确要求使用新的Qwen2 VQA评测E014原始proposal，固定1766条1shot/791多框，报告score/VQA/Oracle及旧VQA配对 | 20260901 | failed | 2026-10-27T19:50:50 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-cleanvqa-e014-124shot-20261027](runs/e015-qwen2-cleanvqa-e014-124shot-20261027.md) · 用户将新Qwen2 VQA评测E014原proposal改为1/2/4shot都评测，不单独做/报告多框子集。固定proposal与同一共同查询，只增加VQA参 | 20260901 | failed | 2026-10-27T20:17:08 | 尚无已登记数值；不表示没有产物 |
| [e015-qwen2-cleanvqa-e014-124shot-now-20261027](runs/e015-qwen2-cleanvqa-e014-124shot-now-20261027.md) · 用户明确取消当前GRPO并立即执行已准备的新Qwen2 VQA×E014固定proposal的1/2/4shot评测。只取消等待依赖，科学配置和已核验输入全部复 | 20260901 | analysis_pending | 2026-10-28T10:25:01 | 关键结果：旧候选1shot all vqa miou=70.98720046306559 percent；关键结果：旧候选1shot all vqa acc50=77.42120343839541 percent；关键结果：旧候选1shot all score miou=69.42985617220447 percent；关键结果：旧候选1shot all score acc50=75.81661891117479 percent；关键结果：旧候选1shot all oracle miou=75.95319130977694 percent；关键结果：旧候选1shot all oracle acc50=83.32378223495702 percent；关键结果：旧候选1shot all invalid=0 count；关键结果：旧候选1shot all delta_score_pp=1.557344290861118 percentage_point；关键结果：旧候选1shot lasot vqa miou=66.85139162399032 percent；关键结果：旧候选1shot lasot vqa acc50=75.0 percent；关键结果：旧候选1shot lasot score miou=65.37116103330052 percent；关键结果：旧候选1shot lasot score acc50=73.66666666666667 percent；关键结果：旧候选1shot lasot oracle miou=71.67223918508266 percent；关键结果：旧候选1shot lasot oracle acc50=80.83333333333333 percent；关键结果：旧候选1shot lasot invalid=0 count；关键结果：旧候选1shot lasot delta_score_pp=1.4802305906898017 percentage_point；关键结果：旧候选1shot got10k vqa miou=82.30688173062983 percent；关键结果：旧候选1shot got10k vqa acc50=89.44444444444444 percent；关键结果：旧候选1shot got10k score miou=79.59036041152275 percent；关键结果：旧候选1shot got10k score acc50=86.11111111111111 percent；关键结果：旧候选1shot got10k oracle miou=84.62972143842374 percent；关键结果：旧候选1shot got10k oracle acc50=92.22222222222223 percent；关键结果：旧候选1shot got10k invalid=0 count；关键结果：旧候选1shot got10k delta_score_pp=2.716521319107068 percentage_point；关键结果：旧候选1shot tao vqa miou=71.44724468615739 percent；关键结果：旧候选1shot tao vqa acc50=76.68393782383419 percent；关键结果：旧候选1shot tao score miou=70.05817360253094 percent；关键结果：旧候选1shot tao score acc50=75.23316062176167 percent；关键结果：旧候选1shot tao oracle miou=76.99650307315515 percent；关键结果：旧候选1shot tao oracle acc50=83.21243523316062 percent；关键结果：旧候选1shot tao invalid=0 count；关键结果：旧候选1shot tao delta_score_pp=1.3890710836264586 percentage_point；关键结果：旧候选1shot filtered_all vqa miou=71.09957077147594 percent；关键结果：旧候选1shot filtered_all vqa acc50=77.53329473074696 percent；关键结果：旧候选1shot filtered_all score miou=69.52599475088957 percent；关键结果：旧候选1shot filtered_all score acc50=75.91198610306891 percent；关键结果：旧候选1shot filtered_all oracle miou=76.11732064264632 percent；关键结果：旧候选1shot filtered_all oracle acc50=83.4973943254198 percent；关键结果：旧候选1shot filtered_all invalid=0 count；关键结果：旧候选1shot filtered_all delta_score_pp=1.5735760205863758 percentage_point；关键结果：旧候选1shot filtered_lasot vqa miou=67.05692248914723 percent；关键结果：旧候选1shot filtered_lasot vqa acc50=75.25773195876289 percent；关键结果：旧候选1shot filtered_lasot score miou=65.5309115709103 percent；关键结果：旧候选1shot filtered_lasot score acc50=73.8831615120275 percent；关键结果：旧候选1shot filtered_lasot oracle miou=72.02686842841769 percent；关键结果：旧候选1shot filtered_lasot oracle acc50=81.27147766323024 percent；关键结果：旧候选1shot filtered_lasot invalid=0 count；关键结果：旧候选1shot filtered_lasot delta_score_pp=1.5260109182369197 percentage_point；关键结果：旧候选1shot filtered_got10k vqa miou=82.30688173062983 percent；关键结果：旧候选1shot filtered_got10k vqa acc50=89.44444444444444 percent；关键结果：旧候选1shot filtered_got10k score miou=79.59036041152275 percent；关键结果：旧候选1shot filtered_got10k score acc50=86.11111111111111 percent；关键结果：旧候选1shot filtered_got10k oracle miou=84.62972143842374 percent；关键结果：旧候选1shot filtered_got10k oracle acc50=92.22222222222223 percent；关键结果：旧候选1shot filtered_got10k invalid=0 count；关键结果：旧候选1shot filtered_got10k delta_score_pp=2.716521319107068 percentage_point；关键结果：旧候选1shot filtered_tao vqa miou=71.44724468615739 percent；关键结果：旧候选1shot filtered_tao vqa acc50=76.68393782383419 percent；关键结果：旧候选1shot filtered_tao score miou=70.05817360253094 percent；关键结果：旧候选1shot filtered_tao score acc50=75.23316062176167 percent；关键结果：旧候选1shot filtered_tao oracle miou=76.99650307315515 percent；关键结果：旧候选1shot filtered_tao oracle acc50=83.21243523316062 percent；关键结果：旧候选1shot filtered_tao invalid=0 count；关键结果：旧候选1shot filtered_tao delta_score_pp=1.3890710836264586 percentage_point；关键结果：旧候选2shot all vqa miou=68.28444602803226 percent；关键结果：旧候选2shot all vqa acc50=74.32664756446992 percent；关键结果：旧候选2shot all score miou=69.42985617220447 percent；关键结果：旧候选2shot all score acc50=75.81661891117479 percent；关键结果：旧候选2shot all oracle miou=75.95319130977694 percent；关键结果：旧候选2shot all oracle acc50=83.32378223495702 percent；关键结果：旧候选2shot all invalid=13 count；关键结果：旧候选2shot all delta_score_pp=-1.1454101441722098 percentage_point；关键结果：旧候选2shot lasot vqa miou=64.16441792849078 percent；关键结果：旧候选2shot lasot vqa acc50=71.83333333333334 percent；关键结果：旧候选2shot lasot score miou=65.37116103330052 percent；关键结果：旧候选2shot lasot score acc50=73.66666666666667 percent；关键结果：旧候选2shot lasot oracle miou=71.67223918508266 percent；关键结果：旧候选2shot lasot oracle acc50=80.83333333333333 percent；关键结果：旧候选2shot lasot invalid=6 count；关键结果：旧候选2shot lasot delta_score_pp=-1.2067431048097377 percentage_point；关键结果：旧候选2shot got10k vqa miou=83.12890510394139 percent；关键结果：旧候选2shot got10k vqa acc50=90.55555555555556 percent；关键结果：旧候选2shot got10k score miou=79.59036041152275 percent；关键结果：旧候选2shot got10k score acc50=86.11111111111111 percent；关键结果：旧候选2shot got10k oracle miou=84.62972143842374 percent；关键结果：旧候选2shot got10k oracle acc50=92.22222222222223 percent；关键结果：旧候选2shot got10k invalid=0 count；关键结果：旧候选2shot got10k delta_score_pp=3.5385446924186326 percentage_point；关键结果：旧候选2shot tao vqa miou=68.07720688405429 percent；关键结果：旧候选2shot tao vqa acc50=72.84974093264248 percent；关键结果：旧候选2shot tao score miou=70.05817360253094 percent；关键结果：旧候选2shot tao score acc50=75.23316062176167 percent；关键结果：旧候选2shot tao oracle miou=76.99650307315515 percent；关键结果：旧候选2shot tao oracle acc50=83.21243523316062 percent；关键结果：旧候选2shot tao invalid=7 count；关键结果：旧候选2shot tao delta_score_pp=-1.980966718476651 percentage_point；关键结果：旧候选2shot filtered_all vqa miou=68.49978704719805 percent；关键结果：旧候选2shot filtered_all vqa acc50=74.5801968731905 percent；关键结果：旧候选2shot filtered_all score miou=69.52599475088957 percent；关键结果：旧候选2shot filtered_all score acc50=75.91198610306891 percent；关键结果：旧候选2shot filtered_all oracle miou=76.11732064264632 percent；关键结果：旧候选2shot filtered_all oracle acc50=83.4973943254198 percent；关键结果：旧候选2shot filtered_all invalid=13 count；关键结果：旧候选2shot filtered_all delta_score_pp=-1.0262077036915063 percentage_point；关键结果：旧候选2shot filtered_lasot vqa miou=64.67598740324607 percent；关键结果：旧候选2shot filtered_lasot vqa acc50=72.5085910652921 percent；关键结果：旧候选2shot filtered_lasot score miou=65.5309115709103 percent；关键结果：旧候选2shot filtered_lasot score acc50=73.8831615120275 percent；关键结果：旧候选2shot filtered_lasot oracle miou=72.02686842841769 percent；关键结果：旧候选2shot filtered_lasot oracle acc50=81.27147766323024 percent；关键结果：旧候选2shot filtered_lasot invalid=6 count；关键结果：旧候选2shot filtered_lasot delta_score_pp=-0.8549241676642283 percentage_point；关键结果：旧候选2shot filtered_got10k vqa miou=83.12890510394139 percent；关键结果：旧候选2shot filtered_got10k vqa acc50=90.55555555555556 percent；关键结果：旧候选2shot filtered_got10k score miou=79.59036041152275 percent；关键结果：旧候选2shot filtered_got10k score acc50=86.11111111111111 percent；关键结果：旧候选2shot filtered_got10k oracle miou=84.62972143842374 percent；关键结果：旧候选2shot filtered_got10k oracle acc50=92.22222222222223 percent；关键结果：旧候选2shot filtered_got10k invalid=0 count；关键结果：旧候选2shot filtered_got10k delta_score_pp=3.5385446924186326 percentage_point；关键结果：旧候选2shot filtered_tao vqa miou=68.07720688405429 percent；关键结果：旧候选2shot filtered_tao vqa acc50=72.84974093264248 percent；关键结果：旧候选2shot filtered_tao score miou=70.05817360253094 percent；关键结果：旧候选2shot filtered_tao score acc50=75.23316062176167 percent；关键结果：旧候选2shot filtered_tao oracle miou=76.99650307315515 percent；关键结果：旧候选2shot filtered_tao oracle acc50=83.21243523316062 percent；关键结果：旧候选2shot filtered_tao invalid=7 count；关键结果：旧候选2shot filtered_tao delta_score_pp=-1.980966718476651 percentage_point；关键结果：旧候选4shot all vqa miou=63.05745564259644 percent；关键结果：旧候选4shot all vqa acc50=68.59598853868195 percent；关键结果：旧候选4shot all score miou=69.42985617220447 percent；关键结果：旧候选4shot all score acc50=75.81661891117479 percent；关键结果：旧候选4shot all oracle miou=75.95319130977694 percent；关键结果：旧候选4shot all oracle acc50=83.32378223495702 percent；关键结果：旧候选4shot all invalid=154 count；关键结果：旧候选4shot all delta_score_pp=-6.3724005296080355 percentage_point；关键结果：旧候选4shot lasot vqa miou=59.0227832324664 percent；关键结果：旧候选4shot lasot vqa acc50=66.0 percent；关键结果：旧候选4shot lasot score miou=65.37116103330052 percent；关键结果：旧候选4shot lasot score acc50=73.66666666666667 percent；关键结果：旧候选4shot lasot oracle miou=71.67223918508266 percent；关键结果：旧候选4shot lasot oracle acc50=80.83333333333333 percent；关键结果：旧候选4shot lasot invalid=53 count；关键结果：旧候选4shot lasot delta_score_pp=-6.348377800834115 percentage_point；关键结果：旧候选4shot got10k vqa miou=75.21257071664161 percent；关键结果：旧候选4shot got10k vqa acc50=81.66666666666667 percent；关键结果：旧候选4shot got10k score miou=79.59036041152275 percent；关键结果：旧候选4shot got10k score acc50=86.11111111111111 percent；关键结果：旧候选4shot got10k oracle miou=84.62972143842374 percent；关键结果：旧候选4shot got10k oracle acc50=92.22222222222223 percent；关键结果：旧候选4shot got10k invalid=8 count；关键结果：旧候选4shot got10k delta_score_pp=-4.37778969488114 percentage_point；关键结果：旧候选4shot tao vqa miou=63.29878489933212 percent；关键结果：旧候选4shot tao vqa acc50=67.7720207253886 percent；关键结果：旧候选4shot tao score miou=70.05817360253094 percent；关键结果：旧候选4shot tao score acc50=75.23316062176167 percent；关键结果：旧候选4shot tao oracle miou=76.99650307315515 percent；关键结果：旧候选4shot tao oracle acc50=83.21243523316062 percent；关键结果：旧候选4shot tao invalid=93 count；关键结果：旧候选4shot tao delta_score_pp=-6.759388703198821 percentage_point；关键结果：旧候选4shot filtered_all vqa miou=63.17422638665753 percent；关键结果：旧候选4shot filtered_all vqa acc50=68.73190503763752 percent；关键结果：旧候选4shot filtered_all score miou=69.52599475088957 percent；关键结果：旧候选4shot filtered_all score acc50=75.91198610306891 percent；关键结果：旧候选4shot filtered_all oracle miou=76.11732064264632 percent；关键结果：旧候选4shot filtered_all oracle acc50=83.4973943254198 percent；关键结果：旧候选4shot filtered_all invalid=153 count；关键结果：旧候选4shot filtered_all delta_score_pp=-6.3517683642320355 percentage_point；关键结果：旧候选4shot filtered_lasot vqa miou=59.24449967853375 percent；关键结果：旧候选4shot filtered_lasot vqa acc50=66.32302405498281 percent；关键结果：旧候选4shot filtered_lasot score miou=65.5309115709103 percent；关键结果：旧候选4shot filtered_lasot score acc50=73.8831615120275 percent；关键结果：旧候选4shot filtered_lasot oracle miou=72.02686842841769 percent；关键结果：旧候选4shot filtered_lasot oracle acc50=81.27147766323024 percent；关键结果：旧候选4shot filtered_lasot invalid=52 count；关键结果：旧候选4shot filtered_lasot delta_score_pp=-6.286411892376553 percentage_point；关键结果：旧候选4shot filtered_got10k vqa miou=75.21257071664161 percent；关键结果：旧候选4shot filtered_got10k vqa acc50=81.66666666666667 percent；关键结果：旧候选4shot filtered_got10k score miou=79.59036041152275 percent；关键结果：旧候选4shot filtered_got10k score acc50=86.11111111111111 percent；关键结果：旧候选4shot filtered_got10k oracle miou=84.62972143842374 percent；关键结果：旧候选4shot filtered_got10k oracle acc50=92.22222222222223 percent；关键结果：旧候选4shot filtered_got10k invalid=8 count；关键结果：旧候选4shot filtered_got10k delta_score_pp=-4.37778969488114 percentage_point；关键结果：旧候选4shot filtered_tao vqa miou=63.29878489933212 percent；关键结果：旧候选4shot filtered_tao vqa acc50=67.7720207253886 percent；关键结果：旧候选4shot filtered_tao score miou=70.05817360253094 percent；关键结果：旧候选4shot filtered_tao score acc50=75.23316062176167 percent；关键结果：旧候选4shot filtered_tao oracle miou=76.99650307315515 percent；关键结果：旧候选4shot filtered_tao oracle acc50=83.21243523316062 percent；关键结果：旧候选4shot filtered_tao invalid=93 count；关键结果：旧候选4shot filtered_tao delta_score_pp=-6.759388703198821 percentage_point；指标观测：旧候选1shot all vqa miou=70.98720046306559 percent；指标观测：旧候选1shot all vqa acc50=77.42120343839541 percent；指标观测：旧候选1shot all score miou=69.42985617220447 percent；指标观测：旧候选1shot all score acc50=75.81661891117479 percent；指标观测：旧候选1shot all oracle miou=75.95319130977694 percent；指标观测：旧候选1shot all oracle acc50=83.32378223495702 percent；指标观测：旧候选1shot all invalid=0 count；指标观测：旧候选1shot all delta_score_pp=1.557344290861118 percentage_point；指标观测：旧候选1shot lasot vqa miou=66.85139162399032 percent；指标观测：旧候选1shot lasot vqa acc50=75.0 percent；指标观测：旧候选1shot lasot score miou=65.37116103330052 percent；指标观测：旧候选1shot lasot score acc50=73.66666666666667 percent；指标观测：旧候选1shot lasot oracle miou=71.67223918508266 percent；指标观测：旧候选1shot lasot oracle acc50=80.83333333333333 percent；指标观测：旧候选1shot lasot invalid=0 count；指标观测：旧候选1shot lasot delta_score_pp=1.4802305906898017 percentage_point；指标观测：旧候选1shot got10k vqa miou=82.30688173062983 percent；指标观测：旧候选1shot got10k vqa acc50=89.44444444444444 percent；指标观测：旧候选1shot got10k score miou=79.59036041152275 percent；指标观测：旧候选1shot got10k score acc50=86.11111111111111 percent；指标观测：旧候选1shot got10k oracle miou=84.62972143842374 percent；指标观测：旧候选1shot got10k oracle acc50=92.22222222222223 percent；指标观测：旧候选1shot got10k invalid=0 count；指标观测：旧候选1shot got10k delta_score_pp=2.716521319107068 percentage_point；指标观测：旧候选1shot tao vqa miou=71.44724468615739 percent；指标观测：旧候选1shot tao vqa acc50=76.68393782383419 percent；指标观测：旧候选1shot tao score miou=70.05817360253094 percent；指标观测：旧候选1shot tao score acc50=75.23316062176167 percent；指标观测：旧候选1shot tao oracle miou=76.99650307315515 percent；指标观测：旧候选1shot tao oracle acc50=83.21243523316062 percent；指标观测：旧候选1shot tao invalid=0 count；指标观测：旧候选1shot tao delta_score_pp=1.3890710836264586 percentage_point；指标观测：旧候选1shot filtered_all vqa miou=71.09957077147594 percent；指标观测：旧候选1shot filtered_all vqa acc50=77.53329473074696 percent；指标观测：旧候选1shot filtered_all score miou=69.52599475088957 percent；指标观测：旧候选1shot filtered_all score acc50=75.91198610306891 percent；指标观测：旧候选1shot filtered_all oracle miou=76.11732064264632 percent；指标观测：旧候选1shot filtered_all oracle acc50=83.4973943254198 percent；指标观测：旧候选1shot filtered_all invalid=0 count；指标观测：旧候选1shot filtered_all delta_score_pp=1.5735760205863758 percentage_point；指标观测：旧候选1shot filtered_lasot vqa miou=67.05692248914723 percent；指标观测：旧候选1shot filtered_lasot vqa acc50=75.25773195876289 percent；指标观测：旧候选1shot filtered_lasot score miou=65.5309115709103 percent；指标观测：旧候选1shot filtered_lasot score acc50=73.8831615120275 percent；指标观测：旧候选1shot filtered_lasot oracle miou=72.02686842841769 percent；指标观测：旧候选1shot filtered_lasot oracle acc50=81.27147766323024 percent；指标观测：旧候选1shot filtered_lasot invalid=0 count；指标观测：旧候选1shot filtered_lasot delta_score_pp=1.5260109182369197 percentage_point；指标观测：旧候选1shot filtered_got10k vqa miou=82.30688173062983 percent；指标观测：旧候选1shot filtered_got10k vqa acc50=89.44444444444444 percent；指标观测：旧候选1shot filtered_got10k score miou=79.59036041152275 percent；指标观测：旧候选1shot filtered_got10k score acc50=86.11111111111111 percent；指标观测：旧候选1shot filtered_got10k oracle miou=84.62972143842374 percent；指标观测：旧候选1shot filtered_got10k oracle acc50=92.22222222222223 percent；指标观测：旧候选1shot filtered_got10k invalid=0 count；指标观测：旧候选1shot filtered_got10k delta_score_pp=2.716521319107068 percentage_point；指标观测：旧候选1shot filtered_tao vqa miou=71.44724468615739 percent；指标观测：旧候选1shot filtered_tao vqa acc50=76.68393782383419 percent；指标观测：旧候选1shot filtered_tao score miou=70.05817360253094 percent；指标观测：旧候选1shot filtered_tao score acc50=75.23316062176167 percent；指标观测：旧候选1shot filtered_tao oracle miou=76.99650307315515 percent；指标观测：旧候选1shot filtered_tao oracle acc50=83.21243523316062 percent；指标观测：旧候选1shot filtered_tao invalid=0 count；指标观测：旧候选1shot filtered_tao delta_score_pp=1.3890710836264586 percentage_point；指标观测：旧候选2shot all vqa miou=68.28444602803226 percent；指标观测：旧候选2shot all vqa acc50=74.32664756446992 percent；指标观测：旧候选2shot all score miou=69.42985617220447 percent；指标观测：旧候选2shot all score acc50=75.81661891117479 percent；指标观测：旧候选2shot all oracle miou=75.95319130977694 percent；指标观测：旧候选2shot all oracle acc50=83.32378223495702 percent；指标观测：旧候选2shot all invalid=13 count；指标观测：旧候选2shot all delta_score_pp=-1.1454101441722098 percentage_point；指标观测：旧候选2shot lasot vqa miou=64.16441792849078 percent；指标观测：旧候选2shot lasot vqa acc50=71.83333333333334 percent；指标观测：旧候选2shot lasot score miou=65.37116103330052 percent；指标观测：旧候选2shot lasot score acc50=73.66666666666667 percent；指标观测：旧候选2shot lasot oracle miou=71.67223918508266 percent；指标观测：旧候选2shot lasot oracle acc50=80.83333333333333 percent；指标观测：旧候选2shot lasot invalid=6 count；指标观测：旧候选2shot lasot delta_score_pp=-1.2067431048097377 percentage_point；指标观测：旧候选2shot got10k vqa miou=83.12890510394139 percent；指标观测：旧候选2shot got10k vqa acc50=90.55555555555556 percent；指标观测：旧候选2shot got10k score miou=79.59036041152275 percent；指标观测：旧候选2shot got10k score acc50=86.11111111111111 percent；指标观测：旧候选2shot got10k oracle miou=84.62972143842374 percent；指标观测：旧候选2shot got10k oracle acc50=92.22222222222223 percent；指标观测：旧候选2shot got10k invalid=0 count；指标观测：旧候选2shot got10k delta_score_pp=3.5385446924186326 percentage_point；指标观测：旧候选2shot tao vqa miou=68.07720688405429 percent；指标观测：旧候选2shot tao vqa acc50=72.84974093264248 percent；指标观测：旧候选2shot tao score miou=70.05817360253094 percent；指标观测：旧候选2shot tao score acc50=75.23316062176167 percent；指标观测：旧候选2shot tao oracle miou=76.99650307315515 percent；指标观测：旧候选2shot tao oracle acc50=83.21243523316062 percent；指标观测：旧候选2shot tao invalid=7 count；指标观测：旧候选2shot tao delta_score_pp=-1.980966718476651 percentage_point；指标观测：旧候选2shot filtered_all vqa miou=68.49978704719805 percent；指标观测：旧候选2shot filtered_all vqa acc50=74.5801968731905 percent；指标观测：旧候选2shot filtered_all score miou=69.52599475088957 percent；指标观测：旧候选2shot filtered_all score acc50=75.91198610306891 percent；指标观测：旧候选2shot filtered_all oracle miou=76.11732064264632 percent；指标观测：旧候选2shot filtered_all oracle acc50=83.4973943254198 percent；指标观测：旧候选2shot filtered_all invalid=13 count；指标观测：旧候选2shot filtered_all delta_score_pp=-1.0262077036915063 percentage_point；指标观测：旧候选2shot filtered_lasot vqa miou=64.67598740324607 percent；指标观测：旧候选2shot filtered_lasot vqa acc50=72.5085910652921 percent；指标观测：旧候选2shot filtered_lasot score miou=65.5309115709103 percent；指标观测：旧候选2shot filtered_lasot score acc50=73.8831615120275 percent；指标观测：旧候选2shot filtered_lasot oracle miou=72.02686842841769 percent；指标观测：旧候选2shot filtered_lasot oracle acc50=81.27147766323024 percent；指标观测：旧候选2shot filtered_lasot invalid=6 count；指标观测：旧候选2shot filtered_lasot delta_score_pp=-0.8549241676642283 percentage_point；指标观测：旧候选2shot filtered_got10k vqa miou=83.12890510394139 percent；指标观测：旧候选2shot filtered_got10k vqa acc50=90.55555555555556 percent；指标观测：旧候选2shot filtered_got10k score miou=79.59036041152275 percent；指标观测：旧候选2shot filtered_got10k score acc50=86.11111111111111 percent；指标观测：旧候选2shot filtered_got10k oracle miou=84.62972143842374 percent；指标观测：旧候选2shot filtered_got10k oracle acc50=92.22222222222223 percent；指标观测：旧候选2shot filtered_got10k invalid=0 count；指标观测：旧候选2shot filtered_got10k delta_score_pp=3.5385446924186326 percentage_point；指标观测：旧候选2shot filtered_tao vqa miou=68.07720688405429 percent；指标观测：旧候选2shot filtered_tao vqa acc50=72.84974093264248 percent；指标观测：旧候选2shot filtered_tao score miou=70.05817360253094 percent；指标观测：旧候选2shot filtered_tao score acc50=75.23316062176167 percent；指标观测：旧候选2shot filtered_tao oracle miou=76.99650307315515 percent；指标观测：旧候选2shot filtered_tao oracle acc50=83.21243523316062 percent；指标观测：旧候选2shot filtered_tao invalid=7 count；指标观测：旧候选2shot filtered_tao delta_score_pp=-1.980966718476651 percentage_point；指标观测：旧候选4shot all vqa miou=63.05745564259644 percent；指标观测：旧候选4shot all vqa acc50=68.59598853868195 percent；指标观测：旧候选4shot all score miou=69.42985617220447 percent；指标观测：旧候选4shot all score acc50=75.81661891117479 percent；指标观测：旧候选4shot all oracle miou=75.95319130977694 percent；指标观测：旧候选4shot all oracle acc50=83.32378223495702 percent；指标观测：旧候选4shot all invalid=154 count；指标观测：旧候选4shot all delta_score_pp=-6.3724005296080355 percentage_point；指标观测：旧候选4shot lasot vqa miou=59.0227832324664 percent；指标观测：旧候选4shot lasot vqa acc50=66.0 percent；指标观测：旧候选4shot lasot score miou=65.37116103330052 percent；指标观测：旧候选4shot lasot score acc50=73.66666666666667 percent；指标观测：旧候选4shot lasot oracle miou=71.67223918508266 percent；指标观测：旧候选4shot lasot oracle acc50=80.83333333333333 percent；指标观测：旧候选4shot lasot invalid=53 count；指标观测：旧候选4shot lasot delta_score_pp=-6.348377800834115 percentage_point；指标观测：旧候选4shot got10k vqa miou=75.21257071664161 percent；指标观测：旧候选4shot got10k vqa acc50=81.66666666666667 percent；指标观测：旧候选4shot got10k score miou=79.59036041152275 percent；指标观测：旧候选4shot got10k score acc50=86.11111111111111 percent；指标观测：旧候选4shot got10k oracle miou=84.62972143842374 percent；指标观测：旧候选4shot got10k oracle acc50=92.22222222222223 percent；指标观测：旧候选4shot got10k invalid=8 count；指标观测：旧候选4shot got10k delta_score_pp=-4.37778969488114 percentage_point；指标观测：旧候选4shot tao vqa miou=63.29878489933212 percent；指标观测：旧候选4shot tao vqa acc50=67.7720207253886 percent；指标观测：旧候选4shot tao score miou=70.05817360253094 percent；指标观测：旧候选4shot tao score acc50=75.23316062176167 percent；指标观测：旧候选4shot tao oracle miou=76.99650307315515 percent；指标观测：旧候选4shot tao oracle acc50=83.21243523316062 percent；指标观测：旧候选4shot tao invalid=93 count；指标观测：旧候选4shot tao delta_score_pp=-6.759388703198821 percentage_point；指标观测：旧候选4shot filtered_all vqa miou=63.17422638665753 percent；指标观测：旧候选4shot filtered_all vqa acc50=68.73190503763752 percent；指标观测：旧候选4shot filtered_all score miou=69.52599475088957 percent；指标观测：旧候选4shot filtered_all score acc50=75.91198610306891 percent；指标观测：旧候选4shot filtered_all oracle miou=76.11732064264632 percent；指标观测：旧候选4shot filtered_all oracle acc50=83.4973943254198 percent；指标观测：旧候选4shot filtered_all invalid=153 count；指标观测：旧候选4shot filtered_all delta_score_pp=-6.3517683642320355 percentage_point；指标观测：旧候选4shot filtered_lasot vqa miou=59.24449967853375 percent；指标观测：旧候选4shot filtered_lasot vqa acc50=66.32302405498281 percent；指标观测：旧候选4shot filtered_lasot score miou=65.5309115709103 percent；指标观测：旧候选4shot filtered_lasot score acc50=73.8831615120275 percent；指标观测：旧候选4shot filtered_lasot oracle miou=72.02686842841769 percent；指标观测：旧候选4shot filtered_lasot oracle acc50=81.27147766323024 percent；指标观测：旧候选4shot filtered_lasot invalid=52 count；指标观测：旧候选4shot filtered_lasot delta_score_pp=-6.286411892376553 percentage_point；指标观测：旧候选4shot filtered_got10k vqa miou=75.21257071664161 percent；指标观测：旧候选4shot filtered_got10k vqa acc50=81.66666666666667 percent；指标观测：旧候选4shot filtered_got10k score miou=79.59036041152275 percent；指标观测：旧候选4shot filtered_got10k score acc50=86.11111111111111 percent；指标观测：旧候选4shot filtered_got10k oracle miou=84.62972143842374 percent；指标观测：旧候选4shot filtered_got10k oracle acc50=92.22222222222223 percent；指标观测：旧候选4shot filtered_got10k invalid=8 count；指标观测：旧候选4shot filtered_got10k delta_score_pp=-4.37778969488114 percentage_point；指标观测：旧候选4shot filtered_tao vqa miou=63.29878489933212 percent；指标观测：旧候选4shot filtered_tao vqa acc50=67.7720207253886 percent；指标观测：旧候选4shot filtered_tao score miou=70.05817360253094 percent；指标观测：旧候选4shot filtered_tao score acc50=75.23316062176167 percent；指标观测：旧候选4shot filtered_tao oracle miou=76.99650307315515 percent；指标观测：旧候选4shot filtered_tao oracle acc50=83.21243523316062 percent；指标观测：旧候选4shot filtered_tao invalid=93 count；指标观测：旧候选4shot filtered_tao delta_score_pp=-6.759388703198821 percentage_point |
| [e015-qwen2-selector-e014clean4shot-20261028](runs/e015-qwen2-selector-e014clean4shot-20261028.md) · 用户明确重新训练：E014清洗仅作数据来源，VQA参考数/提示/训练配置统一原E015四参考协议；沿原4epoch/global16设置，训练后固定E015和E | 20260901 | running | 2026-10-28T11:10:00 | 尚无已登记数值；不表示没有产物 |

## 指标观测（survey-tool 管理）

> 关键结果与指标观测分别保留，不混合计算。辅助指标不自动成为主指标；结论仍需人工判断。

<details><summary>e015-multishot-data-preparation-r5-20261021 · 结果、来源与解释</summary>

- Run 笔记：[e015-multishot-data-preparation-r5-20261021](runs/e015-multishot-data-preparation-r5-20261021.md)
- 最近记录更新：2026-10-21T19:53:23

### 本轮分析
完成10175训练与1728共同测试清单、2001支持身份和8269图像审计。发现原GRPO与冻结测试26个GOT原始视频重合；E015正式任务将用显式SHA排除清单整正负对/整ABBA四元组剔除，原输入不改。

### 本轮局限
仅数据审计，非模型结果；共同测试较原1766少38。缺失轨迹/越界标注及305训练源视频重合剔除记录完整保留；未做跨数据集像素去重。

</details>

<details><summary>e015-qwen2-4shot-sft-grpo-vqa-20261021 · 结果、来源与解释</summary>

- Run 笔记：[e015-qwen2-4shot-sft-grpo-vqa-20261021](runs/e015-qwen2-4shot-sft-grpo-vqa-20261021.md)
- 最近记录更新：2026-10-23T20:18:56

### 本轮分析
【已作废，不作为有效科学结果】用户2026-10-23明确要求当前实验作废。当前数据构造未充分核实FOCUS/IPLoc官方划分与support/query采样，不能据此作benchmark对比或score/shot收益结论。按授权向本Run四shot评测torchrun PID444727发送SIGTERM，保留实际退出码、全部历史数据/checkpoint/日志/结果。此为用户撤销本次实验，不是训练数值失败；禁止自动重试或复用这些数据/模型作为重建实验的有效基线。

### 本轮局限
所有本次数据派生的SFT/GRPO/选择器模型及1/2shot指标仅保留追溯；4shot评测中止。撤回此前方法收益与FOCUS数值优劣的解释，不抹除原始执行事实。

</details>

<details><summary>e015-qwen2-vqa-actual-budget4096-r2-20261021 · 结果、来源与解释</summary>

- Run 笔记：[e015-qwen2-vqa-actual-budget4096-r2-20261021](runs/e015-qwen2-vqa-actual-budget4096-r2-20261021.md)
- 最近记录更新：2026-10-21T20:40:04

### 本轮分析
9项相关CPU回归通过。GPU VQA实际8例、每例5图，全部4032rawpatch/图≤4096，8合法编号EOS；NCCL早期barrier问题已解决。复核既有SFT1/2/4shot、恢复和selector真实更新与副本哈希，但那些训练的size-only预算未生效，显存峰值不能解释为4096设置。正式SFT将依靠新增实际grid守卫及首步验证。

### 本轮局限
合成候选工程验证，不构成定位性能；先前SFT能力实际部分10764rawpatch。没有GRPO真实GPU结果，正式全链尚待执行。

</details>

<details><summary>e015-iploc144-qwen2-4shot-restart-r3-20261023 · 结果、来源与解释</summary>

- Run 笔记：[e015-iploc144-qwen2-4shot-restart-r3-20261023](runs/e015-iploc144-qwen2-4shot-restart-r3-20261023.md)
- 最近记录更新：2026-10-26T01:10:11

### 关键结果 · IPLoc144 1shot VQA mIoU
- 值：60.93249183877414 percent
- 指标含义：VQA mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 1shot VQA Acc50
- 值：67.36111111111111 percent
- 指标含义：VQA Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 1shot Proposal Oracle mIoU
- 值：60.93249183877414 percent
- 指标含义：Proposal Oracle mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 1shot Proposal Oracle Acc50
- 值：67.36111111111111 percent
- 指标含义：Proposal Oracle Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 1shot Oracle与实际mIoU差距
- 值：0.0 percentage_points
- 指标含义：Oracle与实际mIoU差距
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 1shot 候选可命中但未选中数量
- 值：0 count
- 指标含义：候选可命中但未选中数量
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 2shot VQA mIoU
- 值：61.162480906632446 percent
- 指标含义：VQA mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 2shot VQA Acc50
- 值：65.97222222222221 percent
- 指标含义：VQA Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 2shot Proposal Oracle mIoU
- 值：61.98003586156338 percent
- 指标含义：Proposal Oracle mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 2shot Proposal Oracle Acc50
- 值：66.66666666666666 percent
- 指标含义：Proposal Oracle Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 2shot Oracle与实际mIoU差距
- 值：0.8175549549309324 percentage_points
- 指标含义：Oracle与实际mIoU差距
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 2shot 候选可命中但未选中数量
- 值：1 count
- 指标含义：候选可命中但未选中数量
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 4shot VQA mIoU
- 值：65.23348855828748 percent
- 指标含义：VQA mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 4shot VQA Acc50
- 值：72.91666666666666 percent
- 指标含义：VQA Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 4shot Proposal Oracle mIoU
- 值：65.38908655975659 percent
- 指标含义：Proposal Oracle mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 4shot Proposal Oracle Acc50
- 值：72.91666666666666 percent
- 指标含义：Proposal Oracle Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 4shot Oracle与实际mIoU差距
- 值：0.15559800146911495 percentage_points
- 指标含义：Oracle与实际mIoU差距
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 关键结果 · IPLoc144 4shot 候选可命中但未选中数量
- 值：0 count
- 指标含义：候选可命中但未选中数量
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 1shot VQA mIoU
- 值：60.93249183877414 percent
- 指标含义：VQA mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 1shot VQA Acc50
- 值：67.36111111111111 percent
- 指标含义：VQA Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 1shot Proposal Oracle mIoU
- 值：60.93249183877414 percent
- 指标含义：Proposal Oracle mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 1shot Proposal Oracle Acc50
- 值：67.36111111111111 percent
- 指标含义：Proposal Oracle Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 1shot Oracle与实际mIoU差距
- 值：0.0 percentage_points
- 指标含义：Oracle与实际mIoU差距
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 1shot 候选可命中但未选中数量
- 值：0 count
- 指标含义：候选可命中但未选中数量
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 2shot VQA mIoU
- 值：61.162480906632446 percent
- 指标含义：VQA mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 2shot VQA Acc50
- 值：65.97222222222221 percent
- 指标含义：VQA Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 2shot Proposal Oracle mIoU
- 值：61.98003586156338 percent
- 指标含义：Proposal Oracle mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 2shot Proposal Oracle Acc50
- 值：66.66666666666666 percent
- 指标含义：Proposal Oracle Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 2shot Oracle与实际mIoU差距
- 值：0.8175549549309324 percentage_points
- 指标含义：Oracle与实际mIoU差距
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 2shot 候选可命中但未选中数量
- 值：1 count
- 指标含义：候选可命中但未选中数量
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 4shot VQA mIoU
- 值：65.23348855828748 percent
- 指标含义：VQA mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 4shot VQA Acc50
- 值：72.91666666666666 percent
- 指标含义：VQA Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 4shot Proposal Oracle mIoU
- 值：65.38908655975659 percent
- 指标含义：Proposal Oracle mIoU
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 4shot Proposal Oracle Acc50
- 值：72.91666666666666 percent
- 指标含义：Proposal Oracle Acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 4shot Oracle与实际mIoU差距
- 值：0.15559800146911495 percentage_points
- 指标含义：Oracle与实际mIoU差距
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 指标观测 · IPLoc144 4shot 候选可命中但未选中数量
- 值：0 count
- 指标含义：候选可命中但未选中数量
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 本轮解释：待解释

### 本轮分析
Managed execution exited successfully with 18 declared and 0 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence and declared metrics only; it does not validate causal or Claim conclusions.

</details>

<details><summary>e015-three-dataset-eval-20261026 · 结果、来源与解释</summary>

- Run 笔记：[e015-three-dataset-eval-20261026](runs/e015-three-dataset-eval-20261026.md)
- 最近记录更新：2026-10-26T15:15:01

### 关键结果 · jointval_lasot_vqa_miou_1shot
- 值：60.93249183877414 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_score_miou_1shot
- 值：59.06520773132588 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_oracle_miou_1shot
- 值：60.93249183877414 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_vqa_acc50_1shot
- 值：67.36111111111111 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_score_acc50_1shot
- 值：65.27777777777779 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_oracle_acc50_1shot
- 值：67.36111111111111 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_vqa_miou_1shot
- 值：76.72734942773748 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_score_miou_1shot
- 值：77.31695533583304 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_oracle_miou_1shot
- 值：77.31695533583304 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_vqa_acc50_1shot
- 值：82.77777777777777 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_score_acc50_1shot
- 值：83.33333333333334 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_oracle_acc50_1shot
- 值：83.33333333333334 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_vqa_miou_1shot
- 值：62.08848199525181 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_score_miou_1shot
- 值：62.31441567475361 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_oracle_miou_1shot
- 值：63.546319671871174 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_vqa_acc50_1shot
- 值：67.15025906735751 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_score_acc50_1shot
- 值：67.46113989637306 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_oracle_acc50_1shot
- 值：68.9119170984456 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_vqa_miou_1shot
- 值：64.00355845399083 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_score_miou_1shot
- 值：64.0464336694322 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_oracle_miou_1shot
- 值：65.17729190736164 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_vqa_acc50_1shot
- 值：69.35608999224205 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_score_acc50_1shot
- 值：69.43366951124904 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_oracle_acc50_1shot
- 值：70.75252133436773 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_vqa_miou_1shot
- 值：66.58277442058781 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_score_miou_1shot
- 值：66.23219291397083 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_oracle_miou_1shot
- 值：67.26525561549278 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_vqa_acc50_1shot
- 值：72.42971598541547 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_score_acc50_1shot
- 值：72.02408366916139 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_oracle_acc50_1shot
- 值：73.20212051429668 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_vqa_miou_2shot
- 值：61.162480906632446 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_score_miou_2shot
- 值：60.78279528273303 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_oracle_miou_2shot
- 值：61.98003586156338 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_vqa_acc50_2shot
- 值：65.97222222222221 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_score_acc50_2shot
- 值：65.27777777777779 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_oracle_acc50_2shot
- 值：66.66666666666666 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_vqa_miou_2shot
- 值：78.93338946581325 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_score_miou_2shot
- 值：79.32342481529638 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_oracle_miou_2shot
- 值：79.32342481529638 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_vqa_acc50_2shot
- 值：85.55555555555556 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_score_acc50_2shot
- 值：86.11111111111111 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_oracle_acc50_2shot
- 值：86.11111111111111 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_vqa_miou_2shot
- 值：69.38132026112342 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_score_miou_2shot
- 值：69.6223584901695 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_oracle_miou_2shot
- 值：70.63971067177198 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_vqa_acc50_2shot
- 值：75.5440414507772 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_score_acc50_2shot
- 值：75.75129533678756 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_oracle_acc50_2shot
- 值：76.99481865284974 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_vqa_miou_2shot
- 值：69.79703755344111 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_score_miou_2shot
- 值：69.989538347929 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_oracle_miou_2shot
- 值：70.88492042597241 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_vqa_acc50_2shot
- 值：75.87276958882855 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_score_acc50_2shot
- 值：76.02792862684251 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_oracle_acc50_2shot
- 值：77.11404189294026 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_vqa_miou_2shot
- 值：69.82573021118971 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_score_miou_2shot
- 值：69.90952619606631 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_oracle_miou_2shot
- 值：70.64772378287724 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_vqa_acc50_2shot
- 值：75.69060640951832 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_score_acc50_2shot
- 值：75.71339474189215 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_oracle_acc50_2shot
- 值：76.59086547687583 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_vqa_miou_4shot
- 值：65.23348855828748 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_score_miou_4shot
- 值：65.38908655975659 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_oracle_miou_4shot
- 值：65.38908655975659 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_vqa_acc50_4shot
- 值：72.91666666666666 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_score_acc50_4shot
- 值：72.91666666666666 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_lasot_oracle_acc50_4shot
- 值：72.91666666666666 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_vqa_miou_4shot
- 值：82.19969489966476 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_score_miou_4shot
- 值：82.19969489966476 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_oracle_miou_4shot
- 值：82.19969489966476 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_vqa_acc50_4shot
- 值：90.0 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_score_acc50_4shot
- 值：90.0 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_got10k_oracle_acc50_4shot
- 值：90.0 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_vqa_miou_4shot
- 值：73.05563864241168 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_score_miou_4shot
- 值：73.53099737136853 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_oracle_miou_4shot
- 值：74.01252082579934 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_vqa_acc50_4shot
- 值：79.48186528497409 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_score_acc50_4shot
- 值：79.89637305699482 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_tao_oracle_acc50_4shot
- 值：80.51813471502591 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_vqa_miou_4shot
- 值：73.45869567436793 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_score_miou_4shot
- 值：73.83195190839031 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_oracle_miou_4shot
- 值：74.19244076294869 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_vqa_acc50_4shot
- 值：80.21722265321955 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_score_acc50_4shot
- 值：80.52754072924748 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_pooled_oracle_acc50_4shot
- 值：80.99301784328937 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_vqa_miou_4shot
- 值：73.49627403345464 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_score_miou_4shot
- 值：73.70659294359663 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_oracle_miou_4shot
- 值：73.86710076174023 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_vqa_acc50_4shot
- 值：80.79951065054692 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_score_acc50_4shot
- 值：80.93767990788714 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · jointval_macro_oracle_acc50_4shot
- 值：81.14493379389752 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_vqa_miou_1shot
- 值：60.93249183877414 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_score_miou_1shot
- 值：59.06520773132588 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_oracle_miou_1shot
- 值：60.93249183877414 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_vqa_acc50_1shot
- 值：67.36111111111111 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_score_acc50_1shot
- 值：65.27777777777779 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_oracle_acc50_1shot
- 值：67.36111111111111 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_vqa_miou_1shot
- 值：76.72734942773748 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_score_miou_1shot
- 值：77.31695533583304 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_oracle_miou_1shot
- 值：77.31695533583304 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_vqa_acc50_1shot
- 值：82.77777777777777 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_score_acc50_1shot
- 值：83.33333333333334 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_oracle_acc50_1shot
- 值：83.33333333333334 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_vqa_miou_1shot
- 值：62.08848199525181 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_score_miou_1shot
- 值：62.31441567475361 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_oracle_miou_1shot
- 值：63.546319671871174 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_vqa_acc50_1shot
- 值：67.15025906735751 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_score_acc50_1shot
- 值：67.46113989637306 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_oracle_acc50_1shot
- 值：68.9119170984456 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_vqa_miou_1shot
- 值：64.00355845399083 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_score_miou_1shot
- 值：64.0464336694322 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_oracle_miou_1shot
- 值：65.17729190736164 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_vqa_acc50_1shot
- 值：69.35608999224205 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_score_acc50_1shot
- 值：69.43366951124904 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_oracle_acc50_1shot
- 值：70.75252133436773 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_vqa_miou_1shot
- 值：66.58277442058781 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_score_miou_1shot
- 值：66.23219291397083 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_oracle_miou_1shot
- 值：67.26525561549278 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_vqa_acc50_1shot
- 值：72.42971598541547 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_score_acc50_1shot
- 值：72.02408366916139 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_oracle_acc50_1shot
- 值：73.20212051429668 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_vqa_miou_2shot
- 值：61.162480906632446 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_score_miou_2shot
- 值：60.78279528273303 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_oracle_miou_2shot
- 值：61.98003586156338 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_vqa_acc50_2shot
- 值：65.97222222222221 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_score_acc50_2shot
- 值：65.27777777777779 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_oracle_acc50_2shot
- 值：66.66666666666666 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_vqa_miou_2shot
- 值：78.93338946581325 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_score_miou_2shot
- 值：79.32342481529638 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_oracle_miou_2shot
- 值：79.32342481529638 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_vqa_acc50_2shot
- 值：85.55555555555556 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_score_acc50_2shot
- 值：86.11111111111111 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_oracle_acc50_2shot
- 值：86.11111111111111 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_vqa_miou_2shot
- 值：69.38132026112342 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_score_miou_2shot
- 值：69.6223584901695 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_oracle_miou_2shot
- 值：70.63971067177198 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_vqa_acc50_2shot
- 值：75.5440414507772 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_score_acc50_2shot
- 值：75.75129533678756 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_oracle_acc50_2shot
- 值：76.99481865284974 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_vqa_miou_2shot
- 值：69.79703755344111 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_score_miou_2shot
- 值：69.989538347929 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_oracle_miou_2shot
- 值：70.88492042597241 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_vqa_acc50_2shot
- 值：75.87276958882855 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_score_acc50_2shot
- 值：76.02792862684251 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_oracle_acc50_2shot
- 值：77.11404189294026 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_vqa_miou_2shot
- 值：69.82573021118971 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_score_miou_2shot
- 值：69.90952619606631 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_oracle_miou_2shot
- 值：70.64772378287724 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_vqa_acc50_2shot
- 值：75.69060640951832 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_score_acc50_2shot
- 值：75.71339474189215 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_oracle_acc50_2shot
- 值：76.59086547687583 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_vqa_miou_4shot
- 值：65.23348855828748 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_score_miou_4shot
- 值：65.38908655975659 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_oracle_miou_4shot
- 值：65.38908655975659 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_vqa_acc50_4shot
- 值：72.91666666666666 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_score_acc50_4shot
- 值：72.91666666666666 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_lasot_oracle_acc50_4shot
- 值：72.91666666666666 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_vqa_miou_4shot
- 值：82.19969489966476 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_score_miou_4shot
- 值：82.19969489966476 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_oracle_miou_4shot
- 值：82.19969489966476 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_vqa_acc50_4shot
- 值：90.0 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_score_acc50_4shot
- 值：90.0 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_got10k_oracle_acc50_4shot
- 值：90.0 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_vqa_miou_4shot
- 值：73.05563864241168 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_score_miou_4shot
- 值：73.53099737136853 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_oracle_miou_4shot
- 值：74.01252082579934 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_vqa_acc50_4shot
- 值：79.48186528497409 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_score_acc50_4shot
- 值：79.89637305699482 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_tao_oracle_acc50_4shot
- 值：80.51813471502591 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_vqa_miou_4shot
- 值：73.45869567436793 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_score_miou_4shot
- 值：73.83195190839031 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_oracle_miou_4shot
- 值：74.19244076294869 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_vqa_acc50_4shot
- 值：80.21722265321955 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_score_acc50_4shot
- 值：80.52754072924748 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_pooled_oracle_acc50_4shot
- 值：80.99301784328937 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_vqa_miou_4shot
- 值：73.49627403345464 percent
- 指标含义：vqa miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_score_miou_4shot
- 值：73.70659294359663 percent
- 指标含义：score miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_oracle_miou_4shot
- 值：73.86710076174023 percent
- 指标含义：oracle miou
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_vqa_acc50_4shot
- 值：80.79951065054692 percent
- 指标含义：vqa acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_score_acc50_4shot
- 值：80.93767990788714 percent
- 指标含义：score acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · jointval_macro_oracle_acc50_4shot
- 值：81.14493379389752 percent
- 指标含义：oracle acc50
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
- 本轮解释：待解释

### 本轮分析
Managed execution exited successfully with 90 declared and 0 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence and declared metrics only; it does not validate causal or Claim conclusions.

</details>

<details><summary>e015-qwen2-selector-e014clean-20261026 · 结果、来源与解释</summary>

- Run 笔记：[e015-qwen2-selector-e014clean-20261026](runs/e015-qwen2-selector-e014clean-20261026.md)
- 最近记录更新：2026-10-27T10:39:10

### 关键结果 · diag_e014clean_lasot_vqa_miou_1shot
- 值：60.24948934008074 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_lasot_vqa_acc50_1shot
- 值：66.66666666666666 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_lasot_delta_vqa_miou_1shot
- 值：-0.6830024986933978 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_got10k_vqa_miou_1shot
- 值：77.31695533583304 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_got10k_vqa_acc50_1shot
- 值：83.33333333333334 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_got10k_delta_vqa_miou_1shot
- 值：0.5896059080955638 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_tao_vqa_miou_1shot
- 值：63.31027965084585 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_tao_vqa_acc50_1shot
- 值：68.60103626943005 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_tao_delta_vqa_miou_1shot
- 值：1.2217976555940382 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_pooled_vqa_miou_1shot
- 值：64.92428106166629 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_pooled_vqa_acc50_1shot
- 值：70.4422032583398 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_pooled_delta_vqa_miou_1shot
- 值：0.920722607675458 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_macro_vqa_miou_1shot
- 值：66.95890810891987 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_macro_vqa_acc50_1shot
- 值：72.86701208981002 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_macro_delta_vqa_miou_1shot
- 值：0.37613368833206096 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_lasot_vqa_miou_2shot
- 值：61.36961192652692 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_lasot_vqa_acc50_2shot
- 值：65.97222222222221 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_lasot_delta_vqa_miou_2shot
- 值：0.2071310198944758 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_got10k_vqa_miou_2shot
- 值：79.13086819660238 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_got10k_vqa_acc50_2shot
- 值：86.11111111111111 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_got10k_delta_vqa_miou_2shot
- 值：0.19747873078912903 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_tao_vqa_miou_2shot
- 值：69.97817606517961 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_tao_vqa_acc50_2shot
- 值：76.16580310880829 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_tao_delta_vqa_miou_2shot
- 值：0.5968558040561902 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_pooled_vqa_miou_2shot
- 值：70.2945851789811 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_pooled_vqa_acc50_2shot
- 值：76.41582622187742 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_pooled_delta_vqa_miou_2shot
- 值：0.4975476255399798 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_macro_vqa_miou_2shot
- 值：70.15955206276963 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_macro_vqa_acc50_2shot
- 值：76.08304548071388 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_macro_delta_vqa_miou_2shot
- 值：0.33382185157992694 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_lasot_vqa_miou_4shot
- 值：65.23348855828748 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_lasot_vqa_acc50_4shot
- 值：72.91666666666666 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_lasot_delta_vqa_miou_4shot
- 值：0.0 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_got10k_vqa_miou_4shot
- 值：81.56340126592931 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_got10k_vqa_acc50_4shot
- 值：88.88888888888889 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_got10k_delta_vqa_miou_4shot
- 值：-0.6362936337354483 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_tao_vqa_miou_4shot
- 值：72.87637171041258 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_tao_vqa_acc50_4shot
- 值：79.17098445595855 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_tao_delta_vqa_miou_4shot
- 值：-0.17926693199909494 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_pooled_vqa_miou_4shot
- 值：73.23563481831556 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_pooled_vqa_acc50_4shot
- 值：79.82932505818464 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_pooled_delta_vqa_miou_4shot
- 值：-0.22306085605237058 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_macro_vqa_miou_4shot
- 值：73.22442051154313 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_macro_vqa_acc50_4shot
- 值：80.32551333717136 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 关键结果 · diag_e014clean_macro_delta_vqa_miou_4shot
- 值：-0.2718535219115097 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_lasot_vqa_miou_1shot
- 值：60.24948934008074 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_lasot_vqa_acc50_1shot
- 值：66.66666666666666 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_lasot_delta_vqa_miou_1shot
- 值：-0.6830024986933978 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_got10k_vqa_miou_1shot
- 值：77.31695533583304 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_got10k_vqa_acc50_1shot
- 值：83.33333333333334 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_got10k_delta_vqa_miou_1shot
- 值：0.5896059080955638 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_tao_vqa_miou_1shot
- 值：63.31027965084585 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_tao_vqa_acc50_1shot
- 值：68.60103626943005 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_tao_delta_vqa_miou_1shot
- 值：1.2217976555940382 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_pooled_vqa_miou_1shot
- 值：64.92428106166629 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_pooled_vqa_acc50_1shot
- 值：70.4422032583398 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_pooled_delta_vqa_miou_1shot
- 值：0.920722607675458 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_macro_vqa_miou_1shot
- 值：66.95890810891987 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_macro_vqa_acc50_1shot
- 值：72.86701208981002 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_macro_delta_vqa_miou_1shot
- 值：0.37613368833206096 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_lasot_vqa_miou_2shot
- 值：61.36961192652692 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_lasot_vqa_acc50_2shot
- 值：65.97222222222221 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_lasot_delta_vqa_miou_2shot
- 值：0.2071310198944758 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_got10k_vqa_miou_2shot
- 值：79.13086819660238 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_got10k_vqa_acc50_2shot
- 值：86.11111111111111 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_got10k_delta_vqa_miou_2shot
- 值：0.19747873078912903 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_tao_vqa_miou_2shot
- 值：69.97817606517961 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_tao_vqa_acc50_2shot
- 值：76.16580310880829 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_tao_delta_vqa_miou_2shot
- 值：0.5968558040561902 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_pooled_vqa_miou_2shot
- 值：70.2945851789811 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_pooled_vqa_acc50_2shot
- 值：76.41582622187742 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_pooled_delta_vqa_miou_2shot
- 值：0.4975476255399798 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_macro_vqa_miou_2shot
- 值：70.15955206276963 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_macro_vqa_acc50_2shot
- 值：76.08304548071388 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_macro_delta_vqa_miou_2shot
- 值：0.33382185157992694 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_lasot_vqa_miou_4shot
- 值：65.23348855828748 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_lasot_vqa_acc50_4shot
- 值：72.91666666666666 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_lasot_delta_vqa_miou_4shot
- 值：0.0 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_got10k_vqa_miou_4shot
- 值：81.56340126592931 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_got10k_vqa_acc50_4shot
- 值：88.88888888888889 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_got10k_delta_vqa_miou_4shot
- 值：-0.6362936337354483 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_tao_vqa_miou_4shot
- 值：72.87637171041258 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_tao_vqa_acc50_4shot
- 值：79.17098445595855 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_tao_delta_vqa_miou_4shot
- 值：-0.17926693199909494 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_pooled_vqa_miou_4shot
- 值：73.23563481831556 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_pooled_vqa_acc50_4shot
- 值：79.82932505818464 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_pooled_delta_vqa_miou_4shot
- 值：-0.22306085605237058 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_macro_vqa_miou_4shot
- 值：73.22442051154313 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_macro_vqa_acc50_4shot
- 值：80.32551333717136 percent
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 指标观测 · diag_e014clean_macro_delta_vqa_miou_4shot
- 值：-0.2718535219115097 percentage_points
- 指标含义：E014数据诊断选择器结果，非干净泛化结论
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
- 本轮解释：待解释

### 本轮分析
Managed execution exited successfully with 45 declared and 0 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence and declared metrics only; it does not validate causal or Claim conclusions.

</details>

<details><summary>e015-multibox-history-reward-audit-20261027 · 结果、来源与解释</summary>

- Run 笔记：[e015-multibox-history-reward-audit-20261027](runs/e015-multibox-history-reward-audit-20261027.md)
- 最近记录更新：2026-10-27T19:21:20

### 关键结果 · history_audit_old_rollouts
- 值：12800 count
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · history_audit_current_rollouts
- 值：5376 count
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · history_audit_old_last100_original_multi
- 值：9.35960591133005 percent
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · history_audit_old_last100_collage_multi
- 值：80.7741116751269 percent
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · history_audit_current_last20_original_multi
- 值：0.5747126436781609 percent
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · history_audit_current_last20_collage_multi
- 值：2.054794520547945 percent
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · history_audit_old_rollouts
- 值：12800 count
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · history_audit_current_rollouts
- 值：5376 count
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · history_audit_old_last100_original_multi
- 值：9.35960591133005 percent
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · history_audit_old_last100_collage_multi
- 值：80.7741116751269 percent
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · history_audit_current_last20_original_multi
- 值：0.5747126436781609 percent
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · history_audit_current_last20_collage_multi
- 值：2.054794520547945 percent
- 指标含义：历史多框奖励CPU分析诊断
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
- 本轮解释：待解释

### 本轮分析
Managed execution exited successfully with 6 declared and 0 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence and declared metrics only; it does not validate causal or Claim conclusions.

</details>

<details><summary>e015-qwen2-cleanvqa-e014-124shot-now-20261027 · 结果、来源与解释</summary>

- Run 笔记：[e015-qwen2-cleanvqa-e014-124shot-now-20261027](runs/e015-qwen2-cleanvqa-e014-124shot-now-20261027.md)
- 最近记录更新：2026-10-28T10:25:01

### 关键结果 · 旧候选1shot all vqa miou
- 值：70.98720046306559 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot all vqa acc50
- 值：77.42120343839541 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot all score miou
- 值：69.42985617220447 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot all score acc50
- 值：75.81661891117479 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot all oracle miou
- 值：75.95319130977694 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot all oracle acc50
- 值：83.32378223495702 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot all invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot all delta_score_pp
- 值：1.557344290861118 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot lasot vqa miou
- 值：66.85139162399032 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot lasot vqa acc50
- 值：75.0 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot lasot score miou
- 值：65.37116103330052 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot lasot score acc50
- 值：73.66666666666667 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot lasot oracle miou
- 值：71.67223918508266 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot lasot oracle acc50
- 值：80.83333333333333 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot lasot invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot lasot delta_score_pp
- 值：1.4802305906898017 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot got10k vqa miou
- 值：82.30688173062983 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot got10k vqa acc50
- 值：89.44444444444444 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot got10k invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot got10k delta_score_pp
- 值：2.716521319107068 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot tao vqa miou
- 值：71.44724468615739 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot tao vqa acc50
- 值：76.68393782383419 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot tao invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot tao delta_score_pp
- 值：1.3890710836264586 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_all vqa miou
- 值：71.09957077147594 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_all vqa acc50
- 值：77.53329473074696 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_all score miou
- 值：69.52599475088957 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_all score acc50
- 值：75.91198610306891 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_all oracle miou
- 值：76.11732064264632 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_all oracle acc50
- 值：83.4973943254198 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_all invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_all delta_score_pp
- 值：1.5735760205863758 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_lasot vqa miou
- 值：67.05692248914723 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_lasot vqa acc50
- 值：75.25773195876289 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_lasot score miou
- 值：65.5309115709103 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_lasot score acc50
- 值：73.8831615120275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_lasot oracle miou
- 值：72.02686842841769 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_lasot oracle acc50
- 值：81.27147766323024 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_lasot invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_lasot delta_score_pp
- 值：1.5260109182369197 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_got10k vqa miou
- 值：82.30688173062983 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_got10k vqa acc50
- 值：89.44444444444444 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_got10k invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_got10k delta_score_pp
- 值：2.716521319107068 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_tao vqa miou
- 值：71.44724468615739 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_tao vqa acc50
- 值：76.68393782383419 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_tao invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选1shot filtered_tao delta_score_pp
- 值：1.3890710836264586 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot all vqa miou
- 值：68.28444602803226 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot all vqa acc50
- 值：74.32664756446992 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot all score miou
- 值：69.42985617220447 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot all score acc50
- 值：75.81661891117479 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot all oracle miou
- 值：75.95319130977694 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot all oracle acc50
- 值：83.32378223495702 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot all invalid
- 值：13 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot all delta_score_pp
- 值：-1.1454101441722098 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot lasot vqa miou
- 值：64.16441792849078 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot lasot vqa acc50
- 值：71.83333333333334 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot lasot score miou
- 值：65.37116103330052 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot lasot score acc50
- 值：73.66666666666667 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot lasot oracle miou
- 值：71.67223918508266 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot lasot oracle acc50
- 值：80.83333333333333 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot lasot invalid
- 值：6 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot lasot delta_score_pp
- 值：-1.2067431048097377 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot got10k vqa miou
- 值：83.12890510394139 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot got10k vqa acc50
- 值：90.55555555555556 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot got10k invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot got10k delta_score_pp
- 值：3.5385446924186326 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot tao vqa miou
- 值：68.07720688405429 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot tao vqa acc50
- 值：72.84974093264248 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot tao invalid
- 值：7 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot tao delta_score_pp
- 值：-1.980966718476651 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_all vqa miou
- 值：68.49978704719805 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_all vqa acc50
- 值：74.5801968731905 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_all score miou
- 值：69.52599475088957 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_all score acc50
- 值：75.91198610306891 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_all oracle miou
- 值：76.11732064264632 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_all oracle acc50
- 值：83.4973943254198 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_all invalid
- 值：13 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_all delta_score_pp
- 值：-1.0262077036915063 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_lasot vqa miou
- 值：64.67598740324607 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_lasot vqa acc50
- 值：72.5085910652921 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_lasot score miou
- 值：65.5309115709103 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_lasot score acc50
- 值：73.8831615120275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_lasot oracle miou
- 值：72.02686842841769 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_lasot oracle acc50
- 值：81.27147766323024 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_lasot invalid
- 值：6 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_lasot delta_score_pp
- 值：-0.8549241676642283 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_got10k vqa miou
- 值：83.12890510394139 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_got10k vqa acc50
- 值：90.55555555555556 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_got10k invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_got10k delta_score_pp
- 值：3.5385446924186326 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_tao vqa miou
- 值：68.07720688405429 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_tao vqa acc50
- 值：72.84974093264248 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_tao invalid
- 值：7 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选2shot filtered_tao delta_score_pp
- 值：-1.980966718476651 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot all vqa miou
- 值：63.05745564259644 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot all vqa acc50
- 值：68.59598853868195 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot all score miou
- 值：69.42985617220447 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot all score acc50
- 值：75.81661891117479 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot all oracle miou
- 值：75.95319130977694 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot all oracle acc50
- 值：83.32378223495702 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot all invalid
- 值：154 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot all delta_score_pp
- 值：-6.3724005296080355 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot lasot vqa miou
- 值：59.0227832324664 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot lasot vqa acc50
- 值：66.0 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot lasot score miou
- 值：65.37116103330052 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot lasot score acc50
- 值：73.66666666666667 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot lasot oracle miou
- 值：71.67223918508266 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot lasot oracle acc50
- 值：80.83333333333333 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot lasot invalid
- 值：53 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot lasot delta_score_pp
- 值：-6.348377800834115 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot got10k vqa miou
- 值：75.21257071664161 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot got10k vqa acc50
- 值：81.66666666666667 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot got10k invalid
- 值：8 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot got10k delta_score_pp
- 值：-4.37778969488114 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot tao vqa miou
- 值：63.29878489933212 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot tao vqa acc50
- 值：67.7720207253886 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot tao invalid
- 值：93 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot tao delta_score_pp
- 值：-6.759388703198821 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_all vqa miou
- 值：63.17422638665753 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_all vqa acc50
- 值：68.73190503763752 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_all score miou
- 值：69.52599475088957 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_all score acc50
- 值：75.91198610306891 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_all oracle miou
- 值：76.11732064264632 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_all oracle acc50
- 值：83.4973943254198 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_all invalid
- 值：153 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_all delta_score_pp
- 值：-6.3517683642320355 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_lasot vqa miou
- 值：59.24449967853375 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_lasot vqa acc50
- 值：66.32302405498281 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_lasot score miou
- 值：65.5309115709103 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_lasot score acc50
- 值：73.8831615120275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_lasot oracle miou
- 值：72.02686842841769 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_lasot oracle acc50
- 值：81.27147766323024 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_lasot invalid
- 值：52 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_lasot delta_score_pp
- 值：-6.286411892376553 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_got10k vqa miou
- 值：75.21257071664161 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_got10k vqa acc50
- 值：81.66666666666667 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_got10k invalid
- 值：8 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_got10k delta_score_pp
- 值：-4.37778969488114 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_tao vqa miou
- 值：63.29878489933212 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_tao vqa acc50
- 值：67.7720207253886 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_tao invalid
- 值：93 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 关键结果 · 旧候选4shot filtered_tao delta_score_pp
- 值：-6.759388703198821 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot all vqa miou
- 值：70.98720046306559 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot all vqa acc50
- 值：77.42120343839541 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot all score miou
- 值：69.42985617220447 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot all score acc50
- 值：75.81661891117479 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot all oracle miou
- 值：75.95319130977694 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot all oracle acc50
- 值：83.32378223495702 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot all invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot all delta_score_pp
- 值：1.557344290861118 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot lasot vqa miou
- 值：66.85139162399032 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot lasot vqa acc50
- 值：75.0 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot lasot score miou
- 值：65.37116103330052 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot lasot score acc50
- 值：73.66666666666667 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot lasot oracle miou
- 值：71.67223918508266 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot lasot oracle acc50
- 值：80.83333333333333 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot lasot invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot lasot delta_score_pp
- 值：1.4802305906898017 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot got10k vqa miou
- 值：82.30688173062983 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot got10k vqa acc50
- 值：89.44444444444444 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot got10k invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot got10k delta_score_pp
- 值：2.716521319107068 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot tao vqa miou
- 值：71.44724468615739 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot tao vqa acc50
- 值：76.68393782383419 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot tao invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot tao delta_score_pp
- 值：1.3890710836264586 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_all vqa miou
- 值：71.09957077147594 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_all vqa acc50
- 值：77.53329473074696 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_all score miou
- 值：69.52599475088957 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_all score acc50
- 值：75.91198610306891 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_all oracle miou
- 值：76.11732064264632 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_all oracle acc50
- 值：83.4973943254198 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_all invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_all delta_score_pp
- 值：1.5735760205863758 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_lasot vqa miou
- 值：67.05692248914723 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_lasot vqa acc50
- 值：75.25773195876289 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_lasot score miou
- 值：65.5309115709103 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_lasot score acc50
- 值：73.8831615120275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_lasot oracle miou
- 值：72.02686842841769 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_lasot oracle acc50
- 值：81.27147766323024 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_lasot invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_lasot delta_score_pp
- 值：1.5260109182369197 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_got10k vqa miou
- 值：82.30688173062983 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_got10k vqa acc50
- 值：89.44444444444444 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_got10k invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_got10k delta_score_pp
- 值：2.716521319107068 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_tao vqa miou
- 值：71.44724468615739 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_tao vqa acc50
- 值：76.68393782383419 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_tao invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选1shot filtered_tao delta_score_pp
- 值：1.3890710836264586 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot all vqa miou
- 值：68.28444602803226 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot all vqa acc50
- 值：74.32664756446992 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot all score miou
- 值：69.42985617220447 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot all score acc50
- 值：75.81661891117479 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot all oracle miou
- 值：75.95319130977694 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot all oracle acc50
- 值：83.32378223495702 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot all invalid
- 值：13 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot all delta_score_pp
- 值：-1.1454101441722098 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot lasot vqa miou
- 值：64.16441792849078 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot lasot vqa acc50
- 值：71.83333333333334 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot lasot score miou
- 值：65.37116103330052 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot lasot score acc50
- 值：73.66666666666667 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot lasot oracle miou
- 值：71.67223918508266 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot lasot oracle acc50
- 值：80.83333333333333 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot lasot invalid
- 值：6 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot lasot delta_score_pp
- 值：-1.2067431048097377 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot got10k vqa miou
- 值：83.12890510394139 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot got10k vqa acc50
- 值：90.55555555555556 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot got10k invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot got10k delta_score_pp
- 值：3.5385446924186326 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot tao vqa miou
- 值：68.07720688405429 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot tao vqa acc50
- 值：72.84974093264248 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot tao invalid
- 值：7 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot tao delta_score_pp
- 值：-1.980966718476651 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_all vqa miou
- 值：68.49978704719805 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_all vqa acc50
- 值：74.5801968731905 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_all score miou
- 值：69.52599475088957 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_all score acc50
- 值：75.91198610306891 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_all oracle miou
- 值：76.11732064264632 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_all oracle acc50
- 值：83.4973943254198 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_all invalid
- 值：13 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_all delta_score_pp
- 值：-1.0262077036915063 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_lasot vqa miou
- 值：64.67598740324607 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_lasot vqa acc50
- 值：72.5085910652921 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_lasot score miou
- 值：65.5309115709103 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_lasot score acc50
- 值：73.8831615120275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_lasot oracle miou
- 值：72.02686842841769 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_lasot oracle acc50
- 值：81.27147766323024 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_lasot invalid
- 值：6 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_lasot delta_score_pp
- 值：-0.8549241676642283 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_got10k vqa miou
- 值：83.12890510394139 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_got10k vqa acc50
- 值：90.55555555555556 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_got10k invalid
- 值：0 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_got10k delta_score_pp
- 值：3.5385446924186326 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_tao vqa miou
- 值：68.07720688405429 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_tao vqa acc50
- 值：72.84974093264248 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_tao invalid
- 值：7 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选2shot filtered_tao delta_score_pp
- 值：-1.980966718476651 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot all vqa miou
- 值：63.05745564259644 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot all vqa acc50
- 值：68.59598853868195 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot all score miou
- 值：69.42985617220447 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot all score acc50
- 值：75.81661891117479 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot all oracle miou
- 值：75.95319130977694 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot all oracle acc50
- 值：83.32378223495702 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot all invalid
- 值：154 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot all delta_score_pp
- 值：-6.3724005296080355 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot lasot vqa miou
- 值：59.0227832324664 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot lasot vqa acc50
- 值：66.0 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot lasot score miou
- 值：65.37116103330052 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot lasot score acc50
- 值：73.66666666666667 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot lasot oracle miou
- 值：71.67223918508266 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot lasot oracle acc50
- 值：80.83333333333333 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot lasot invalid
- 值：53 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot lasot delta_score_pp
- 值：-6.348377800834115 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot got10k vqa miou
- 值：75.21257071664161 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot got10k vqa acc50
- 值：81.66666666666667 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot got10k invalid
- 值：8 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot got10k delta_score_pp
- 值：-4.37778969488114 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot tao vqa miou
- 值：63.29878489933212 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot tao vqa acc50
- 值：67.7720207253886 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot tao invalid
- 值：93 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot tao delta_score_pp
- 值：-6.759388703198821 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_all vqa miou
- 值：63.17422638665753 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_all vqa acc50
- 值：68.73190503763752 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_all score miou
- 值：69.52599475088957 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_all score acc50
- 值：75.91198610306891 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_all oracle miou
- 值：76.11732064264632 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_all oracle acc50
- 值：83.4973943254198 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_all invalid
- 值：153 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_all delta_score_pp
- 值：-6.3517683642320355 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_lasot vqa miou
- 值：59.24449967853375 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_lasot vqa acc50
- 值：66.32302405498281 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_lasot score miou
- 值：65.5309115709103 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_lasot score acc50
- 值：73.8831615120275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_lasot oracle miou
- 值：72.02686842841769 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_lasot oracle acc50
- 值：81.27147766323024 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_lasot invalid
- 值：52 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_lasot delta_score_pp
- 值：-6.286411892376553 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_got10k vqa miou
- 值：75.21257071664161 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_got10k vqa acc50
- 值：81.66666666666667 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_got10k score miou
- 值：79.59036041152275 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_got10k score acc50
- 值：86.11111111111111 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_got10k oracle miou
- 值：84.62972143842374 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_got10k oracle acc50
- 值：92.22222222222223 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_got10k invalid
- 值：8 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_got10k delta_score_pp
- 值：-4.37778969488114 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_tao vqa miou
- 值：63.29878489933212 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_tao vqa acc50
- 值：67.7720207253886 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_tao score miou
- 值：70.05817360253094 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_tao score acc50
- 值：75.23316062176167 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_tao oracle miou
- 值：76.99650307315515 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_tao oracle acc50
- 值：83.21243523316062 percent
- 指标含义：共同查询上的定位指标
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_tao invalid
- 值：93 count
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 指标观测 · 旧候选4shot filtered_tao delta_score_pp
- 值：-6.759388703198821 percentage_point
- 指标含义：非法选择数或同查询score收益
- 不确定性：未记录
- 来源/产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json
- 本轮解释：待解释

### 本轮分析
三档评测均exit0，逐条候选/ID/IoU及总体统计核验通过。以下为排除18已知训练原视频重合后的共同1727查询，mIoU（%）：

| 范围 | score | VQA 1shot | VQA 2shot | VQA 4shot | Oracle |
|---|---:|---:|---:|---:|---:|
| 总体（1727） | 69.53 | 71.10 | 68.50 | 63.17 | 76.12 |
| LaSOT（582） | 65.53 | 67.06 | 64.68 | 59.24 | 72.03 |
| GOT10k（180） | 79.59 | 82.31 | 83.13 | 75.21 | 84.63 |
| TAO（965） | 70.06 | 71.45 | 68.08 | 63.30 | 77.00 |

完整共同1745查询VQA mIoU为70.987200/68.284446/63.057456%；相应score69.429856、Oracle75.953191。排除重合后1shot相对score+1.573576pp，2shot−1.026208pp，4shot−6.351768pp；同1727查询旧Qwen3 VQA（1shot）72.220238%，新Qwen2 1shot低1.120668pp，模型、数据规模与训练预算同时变化，非模型版本单因素对照。

排除重合后的无效选择数1/2/4shot为0/13/153。2shot十三条均输出Reference 1或Reference 2；4shot148条输出候选范围外的3/4（88/60），另5条输出Reference X，均EOS结束，不是生成截断。提示多参考输入/编号适配异常；没有因此修改parser、回退score或重训。仅用于诊断的计算：若4shot无效项回退原score，总体可增加5.089593pp至68.2638%，仍低于原score69.525995%；这一数值不是正式VQA指标。有效回答上的错误选择也存在，不能把全部下降归因格式。

三个shot共享冻结E014原1shot proposal，只改变VQA参考帧数；原1766中21条TAO不足5标注帧排除，1745中18视频重合另报1727。报告不单列多框子集。GRPO保持取消（115步，最近checkpoint100），无新训练、推理或Claim升级。

### 本轮局限
共同1745查询排除了21条参考不足TAO；18训练原视频重合另报1727。冻结E014原1shot proposal，仅改VQA参考数，旧探索集非E015当前作者划分。模型/数据/预算非单因素。诊断回退分数不是正式结果；不单列多框子集。

</details>

## 详细审计正文（canonical）
这里保存指标定义、证据链、逐层结论边界与审核入口；后续 Run 更新不会覆盖本节。
