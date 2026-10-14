# 公共配置、构造、启动与Run生命周期审查

基线：`1622e5f64a70239d02145f017cfd991cf8318e47`。本报告补充config_shell_review入口清单之外的公共生命周期；SFT/GRPO/评测数学另见相应报告。仅源码核对，非运行验证。

## Config / Registry / Builder

- Config.fromfile使用runpy执行Python；当前129维护配置的顶层已核对为无import、只dict及有限sum/list表达式，不代表任意外部配置安全。
- _base_按顺序深合并，child字典递归合并；_delete_=True替换子树，删除控制键不留给constructor。列表不是按元素递归合并。
- config_alias只允许单一alias字段；递归栈防cycle。source_files保留invocation alias和canonical配置文本，canonical_path用于相对branch parent解析。不能凭旧路径名称推断旧Run内容。
- CLI用literal_eval，否则保留字符串；dotted key只穿mapping，允许新增未知key，不是完整schema校验。程序支持的mapping字段必须由消费者落实/拒绝，A012/A014/A018是相关例子。
- Registry拒绝重复注册名，build(None)=None、非dict对象原样返回；dict配置deepcopy并pop(type)，defaults只setdefault。不是通用依赖注入安全边界。
- Builder先model再dataset/collator再runner，将model-owned processor传入collator；work_dir及dataloader.batch_size由Builder覆盖到Runner。旧Registry名称的显式alias仍指向同一实现，不独立复制科学算法。
- SyntheticLocalizationDataset构造时创建/重写四张PNG，明确只用于能力smoke。它不是只读manifest dataset，也不是IPLoc科学证据。image_size/root等变体的几何与输出覆盖边界仍需单独验证，未执行。
- compat仅声明缺失torchvision::nms schema并保持library引用，不提供NMS kernel；不能将它当成torchvision ABI或所有视觉算子已修复证明。

## Branch与动作优先级

- ordinary配置先inherit/CLI，再由output(root/run_name)解析work_dir；output与named_run互斥，显式work_dir CLI与output控制冲突则拒绝。
- branch CLI修改template；父可执行字段必须在runtime下。top-level model/runner/work_dir/dataloaders/evaluator/checkpoint_suite被明确拒绝，避免默默丢失。允许的template section再覆盖父section。
- branch.source profile解析named_run来源；profile只允许kind/checkpoint/experiment_id，冲突的named_run来源CLI会拒绝，手填来源需source=None。base_model与checkpoint来源门禁不同。
- train/new注入initialize_from；train/resume注入resume_from；evaluation/head actions清resume_from并要求new named child，不恢复optimizer。GRPO普通branch只支持new与2/4rank；symmetric_grpo coordinator是独立冻结8rank入口，不机械统一。
- settings优先branch再launch；worker_command仅nproc>1包装torchrun，single DDP前提缺口A001；infer/analyze限定单process，允许model sharding，不等于DDP。
- ordinary attention_intervene worker只读branch动作的缺口A004，以及普通named非train默认train的缺口A005，已经跨launch/summary/preparation/worker核对。
- input_artifacts只核对显式文件SHA、config path binding和可选head binding；未声明的输入没有自动身份保证。inspect只计划、artifact检查延迟到execute。
- symmetric_grpo由coordinator拥有fresh payload和内部worker启动，外层不能二次torchrun或先分配payload。其他固定output/named_run各自目录所有权不同。

## Named Run身份、保存与来源

- new分支validated names、UTC timestamp、目录排重，路径resolve后必须位于experiment_dir。checkpoint源要在同experiment；普通train要求trainer_state，read-only action只要求adapter文件。
- 来源布局：root在experiment_dir下；checkpoint branch在root/branches；explicit scientific parent在parent/children。scientific lineage可以和initialization checkpoint来源不同，manifest分列两者，不应把parent_run_id自动等同于加载权重来源。
- legacy parent只作为index observation，不反写旧Run manifest。最终adapter-only work_dir靠metrics.json识别legacy布局；这只是路径分类，不读取指标判passed。
- new manifest记录entry/parent config SHA及CLI，实际可执行effective config另由snapshot保存。只有配置路径SHA不是所有输入/权重身份保证。
- resume核对run_dir/experiment/schema、checkpoint属于该Run/checkpoints、resolved identity与runner来源；未绑定有效训练条件（A017）。prepared/started不等于完成，不恢复科学收益标签。
- run_index/events采用flock追加、flush+fsync；manifest/status是当前视图，通过rename替换，不是不可变真相日志。锁保护的是追加写入，不是整个训练execution lease；正式任务互斥还依赖外部managed流程。
- mark_run_event的失败记录不保证所有异常路径都能写出；需要保留worker退出码和原始日志。路径/文件存在检查不读取权重，不证明adapter完整性（A002）。

## Snapshot与完成性

- save_snapshot每次invoke创建独占UUID目录，包含resolved config、每个源config文本/SHA、prompt implementation、Git HEAD和iploc_szy/tools的Python/Shell字节SHA。resume不会覆盖旧snapshot。
- Git HEAD不是dirty工作区全部内容证明；code_sha256记录相应当前源码字节，但不包括全部依赖、环境、模型/data或历史Run产物。来源身份需各执行期协议另补。
- save_prompt_example只存构造后的messages，不打开图像。例子只证明这一sample的conversation构造，不证明所有图片/所有prompt/GT边界。
- snapshot存在不证明worker完成；保存是多文件顺序写入，没有事务完成marker。它不自动核验此前Run的snapshot兼容性。
- fixed output拒绝已有目录，named new独占目录，resume追加log/history。不得把所有任务强改成同一payload/metrics位置；managed scaffold、named lifecycle与准备型coordinator边界需按真实入口记录。

## 范围与余项

公共Config/Registry/Builder/branching/launching/run_management/snapshot源码与主要worker指向已核对。worker内部head screening、干预、数据构造/统计与完整测试/依赖/文档仍未全完。以上没有授予执行、部署、自动修复或Claim promotion权限。
