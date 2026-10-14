# 引用表（Citations，kernel 真相层）

每条记录：citekey -> 书目信息 + 溯源。content_hash 一旦设定即不可变。
用 ingest.py 添加条目（它会自动对 PDF 计算 SHA-256）。
绝不手工臆造条目；若论文无法抓取，标记为 [UNVERIFIED] 并附说明、不填 hash。
若同名目录下存在 MinerU 抽取产物，ingest.py 会在对应笔记骨架记录 mineru_md / mineru_images 字段（见 SKILL.md C2）。