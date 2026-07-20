# E003-R-005-forced-candidate-verifier-local-lasot-n20

- 状态：failed_pre_inference
- 性质：forced-candidate pilot 的工程启动失败，非科学实验结果。
- 远端目录：`/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005-forced-candidate-verifier-local-lasot-n20/`
- 目的：运行 prefix-conditioned verifier n=20 pilot。
- 失败原因：launcher 从外部 script path 启动 Python；Python 将 script directory 放入 import path，而不是 shell 的 `cd` 目录，因此 `from loc_dataset import get_dataloader` 报 `ModuleNotFoundError: No module named 'loc_dataset'`。
- 有效输出：0；不得引用模型指标。
- 修复：后继 R-005b 显式设置 `PYTHONPATH=/home/featurize/work/mechanism/iplocid/iplocid`，并保留 exact new run ID，避免覆盖失败记录。
- 审核入口：`config/run.md`、`logs/run.log`。
