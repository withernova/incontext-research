# 配置与运行记录

E-009 分支入口与 E-011 训练、adapter 评测、原生推理现在共用 tools/launch.py。
E-012 R-004–R-010 的新双角色 head 分析同样使用该入口的单进程 `analyze` action：`tools/run/e012_dual_role_analysis.sh → Python config → tools/launch.py → tools/analyze.py → analysis.entrypoint`。该系列不得继续复制历史 head-screen 脚本中硬编码绝对日志路径和 `tee -a` 的模式；完整约定见治理项目 `shell/06_experiments/E-012/unified_execution_contract.md`。
对应 shell 仅接受可选 config 文件路径（E-012 公共 shell 另接受 `--inspect`），不再接受 checkpoint、数据集、GPU、生成长度等位置参数。
旧调用需要迁移；历史专用 suite 脚本尚未迁移，历史产物不追溯改写。

- 数据路径、checkpoint、prompt_text / prompt_version、evaluation 和 runner 参数在 config 中修改。
- 普通训练进程数由 launch.nproc_per_node 指定；分支由 branch.nproc_per_node 指定。
- 普通运行输出到 work_dir，已有目录拒绝复用。分支沿用 named_run 独立目录与恢复机制。
- `analyze` 由 `tools/launch.py` 创建 `logs/console-<uuid>.log`，由 `tools/analyze.py` 调用公共 config snapshot 并原子写 `status.json`；科学 entrypoint 只写 records/integrity/summary，不得另造日志根目录。
- 默认使用调度环境分配的 GPU。
- 原生推理 evaluation.limit=None 表示全量，max_new_tokens 控制生成上限。
- Python 旧 CLI 覆盖接口保留兼容，实际生效值记录到快照。

每次 train/evaluate/infer 启动，在 work_dir/logs/config_snapshots 下创建独立目录，包含：
原始入口与继承配置、resolved.json（最终合并配置）、provenance.json（Git HEAD 和源码哈希）、
prompt_implementation.py、构建数据后保存的 prompt_example.json。
模型加载失败仍保留配置快照；恢复运行创建新快照，不覆盖旧记录。
源码哈希可识别未提交改动，但不是完整代码备份，复现仍需保管相应提交或工作区补丁。
日志中 CONFIG_SNAPSHOT 指向本次快照。

E-011 的 prompt_text 保持修改前文本，显式命名为 qwen3-grounding-v1。
协议仍负责 reference/query 消息结构与答案格式，快照保存该实现和构建后的示例。
E-011 native base 与 adapter eval 从同一公共评测 base 继承数据范围和 prompt；训练 prompt 仍在训练 recipe 中显式保存。
本次不改变训练 1024 / adapter 评测 2048 的视觉 token 上限，只修正误导注释。

E-009 分支已恢复 qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py 父配置，与其 LoRA 评测入口对应。


## 冻结评测范围与来源

E-011 的 native base 与 adapter 评测共用 configs/_base_/e011_frozen_eval.py；E-009 focus eval 也指向同一份物理 manifest。
默认读取 experiments/_shared/manifests/iploc_1shot_frozen_eval_v1.json，共 1766 个 1-shot 样本：
LaSOT 600、GOT10k validation 180、TAO validation 986。文件 SHA-256 为
48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b。
E-011 只评估一个数据集时修改 SELECTED_DATASETS；E-009 修改 EVAL_DATASETS，例如 ("TAO",)。

Git 溯源：ac6d17a 是当前历史中最早引用该合并 manifest 的提交；
5d49890 中重组前的 E-011 adapter/native config 只使用 LaSOT 280；
d067688 将 E-011 配置重组为公共 recipe，同时把 adapter eval 扩大为
LaSOT testing 280、TAO train 499、GOT10k train 9335，共 10114。
该范围混入训练 split，且与 native base 不一致，现已由共享冻结评测配置替代。
训练入口 train_dataloader 仍使用训练 manifest，不受此修改影响。


共享 manifest 的 provenance sidecar 与 JSON 放在同一目录，记录原始 E-009 路径、
SHA-256、数据集计数和最早 Git 引用。原始文件继续保留，以保证历史 run 路径不失效；
新 run 统一读取共享路径，避免跨实验反向依赖。
