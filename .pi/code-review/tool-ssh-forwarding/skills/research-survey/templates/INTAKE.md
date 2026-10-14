# 项目输入（PROJECT INTAKE） — 逐行填写，完成后告诉 agent “intake done / 填好了”

> 把每个 `<...>` 替换为你的取值，**不要留下任何 `<...>`**。
> 多值字段（seed_papers、constraints）：每行一项，以 `- ` 开头。
> 填完后对 agent 说 “intake done” / “填好了”，它会运行 materialize.py 并继续后续阶段。

repo_path: <代码仓库的绝对路径；若为纯新颖性/调研研究，写 none-yet>
project_slug: <短 slug，小写连字符，例如 gdino-vlod-novelty>
project_name: <可读项目名，例如 GDINO+IVLOD 新颖性研究>

seed_papers:
- <arXiv id / DOI / 本地 PDF 绝对路径 — 每行一项>
- <例如 2401.04000  或  10.1109/CVPR.2024.0001  或  E:/path/to/paper.pdf>
- <尽量≥1 篇；越多越好。若同名目录下已有 MinerU 抽取产物，会优先读取其中的 .md>

idea: <你的想法，2–6 句。说清“机制”（为何会 work），而非只说目标。草稿即可，后续会迭代。>

domain: <例如 open-vocabulary detection / incremental learning / IVLOD>
target_venue: <例如 CVPR 2027 / ICCV / arXiv preprint>
polite_email: <你的真实邮箱 — OpenAlex / Unpaywall / CrossRef API 必需>
constraints: <每行一项；若没有写 none>
- <例如 单机训练，无分布式>
- <例如 backbone 固定为 Swin-T>

## 备注（可选）
<其它需要 agent 知道的事项。例如：种子论文来自 Zotero 某集合；某篇无本地 PDF 需联网抓取；是否需要英文输出等。>