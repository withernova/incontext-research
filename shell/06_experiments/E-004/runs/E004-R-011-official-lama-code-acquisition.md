# E004-R-011 · 官方 LaMa 代码获取

- status: `completed_passed`
- remote: `/home/featurize/work/mechanism/explog/E-004/runs/E004-R-011-official-lama-code-acquisition`
- tmux: `e004_lama_acquire`（正常退出 status 0）

## 目的

在用论文指定的LaMa替换neutral-fill object-removal proxy前，固定并审计官方源码版本。

## 结果

```text
repository=https://github.com/advimman/lama.git
commit=786f5936b27fb3dacd2b1ad799e4de968ea697e7
dirty=0
```

服务器代码目录：

```text
/home/featurize/work/mechanism/third_party/lama
```

## 审核入口

- `results/repository_identity.txt`
- `manifests/entrypoint_inventory.txt`
- `logs/run.log`
- `config/run.md`

## 结论边界

该run只证明论文引用对应的官方LaMa代码已获取并固定。尚未获取或校验Big-LaMa checkpoint，也尚未完成inpainting smoke和LaMa source/base行为gate。
