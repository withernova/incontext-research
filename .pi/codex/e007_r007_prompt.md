你是本项目按 experiment_code_edit 路由委派的实现 Agent。请直接实现已由人类批准并授权的 Run：E007-R-007-natural-query-head-reference-correspondence-chain-audit-n140。

必须先完整阅读并遵守：
1. AGENTS.md
2. shell/06_experiments/E-007/runs/E007-R-007-natural-query-head-reference-correspondence-chain-audit-n140.md
3. shell/06_experiments/E-007/mission.md
4. shell/06_experiments/E-007/plan.md
5. shell/06_experiments/E-002/ledger_filling_skill.md
6. 参考实现 codespace/e007/runner_006c.py，以及通过 ssh featurize 读取远程只读参考：/home/featurize/work/mechanism/scripts/e005/e005_r029c_original140_binding_640.py

任务边界：
- 在本地 codespace/e007/ 新建 R-007 runner 与 launcher；不要修改 approved Run 规范，不改变head/样本/指标/controls。
- 可通过 ssh featurize 只读审计模型模块、旧脚本、manifest和既有产物；可以做语法检查与不加载模型的静态测试。
- 不得激活/消费 survey-tool 执行授权，不得启动正式run，不得创建正式远程run产物；正式部署和执行由协调pi在审核你的实现后完成。
- 不删除数据，不做破坏性git，不使用/tmp作为源码或持久产物，不覆盖已有科学产物。
- 实现必须覆盖批准规范中的：n140 exact replay；自然bbox p-1 rows；main4和GQA KV映射；pre-RoPE K hook；matched/background/same-class donor；fractional occupancy；H1/H2/H3 metrics；sequence bootstrap；固定hash CV；12套图；原子records/checkpoint；no-silent-zero gates；summary.json/metrics.json/manifest/exit code。
- 如果批准规范内部存在无法可靠实现或数据不满足的点，必须 fail closed 并在最终报告明确指出，不得静默改变设计。
- 运行 python compile/static self-tests。不要假装做过GPU smoke。

最终回复必须列出：修改文件、设计要点、静态测试结果、远程只读审计证据、尚存风险、建议正式命令。
