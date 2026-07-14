# E-002 · IPLoc-ID 数据集构建脚本阅读笔记

> 来源：GitHub `kensuke-nakamura/iplocid` raw files。服务器已关闭时离线整理。  
> 目标：判断是否必须下载 train/test 全量，还是只准备 test 即可。

## 结论先行

如果 E-002 当前目标是“发现现象 / 小规模评估”，**不需要准备训练集**。优先只准备官方 `data/*_test.json` 或 `data/*T2.json` 涉及的 test/val 图像即可。

最省力路线：

1. 不重新 build JSON；直接使用仓库自带官方 manifest。
2. 不运行原版 `extract_dataset.sh`，因为它会遍历 `./data/*.json`，包括 LASOT train JSON。
3. 写一个 test-only extract 脚本，只处理：
   - `LASOT_1shot_T2_classwise-split_test.json`
   - `VastTrack_test_1shot_T2.json`
   - 可选：`got10k-val_1shot_T2.json`
   - 可选：`pdm_1shot_T2.json`
4. E-002 第一阶段优先 LaSOT/VastTrack，因为它们是 in-class negative，更能诊断 instance-level rejection。

## 官方脚本总览

`iplocid/shell_build_data-json.sh`：

```bash
bash shell_build_dataset_LASOT.sh
bash shell_build_dataset_pdm.sh
bash shell_build_dataset_got10k.sh
bash shell_build_dataset_VastTrack.sh
```

它是全量重建入口，不建议第一阶段直接跑。

## 1. LASOT

入口：

```bash
bash shell_build_dataset_LASOT.sh "1,2,4,8" "1,2,3,9,18" 0.2
```

内部调用：

```bash
python3 tool_build_dataset_json_lasot.py \
  --lasot_root /ssd1/dataset/ICL_tracking/video/LASOT \
  --output_dir ./data \
  --export_root /ssd1/dataset/ICL_tracking_minimized/video/LASOT \
  --test_sample_ratio 0.2 \
  --N_set ... \
  --T_set ...
```

### LASOT build 逻辑

`tool_build_dataset_json_lasot.py`：

- 列出 LaSOT root 下所有 class；
- 按 class 名排序后，一半 class 做 test，一半 class 做 train；
- 对 test classes：
  - 每个 class 抽 `test_sample_ratio` 比例的 target sequences；
  - in-class negative 从同 class 的其他 sequence 抽；
  - out-class negative 从其他 class 抽；
- 对 train classes：
  - 为 train split 构造 train JSON；
- 输出：
  - `LASOT_{N}shot_T{T}_classwise-split_test.json`
  - `LASOT_{N}shot_T{T}_classwise-split_train.json`

### 对我们意味着什么

如果重新 build LASOT，它会需要完整 LaSOT class/sequence 结构，因为要做 class split 和 negative sampling。

但如果只做评估，**不需要重新 build**。仓库已经有：

```text
LASOT_1shot_T2_classwise-split_test.json
LASOT_2shot_T2_classwise-split_test.json
LASOT_4shot_T2_classwise-split_test.json
LASOT_8shot_T2_classwise-split_test.json
```

E-002 可以只用这些 test manifest。理论上只需要这些 manifest 引用到的图像，不需要 LASOT train JSON 引用的图像。

### 注意

原版 `extract_dataset.sh` 会处理 `./data/*.json`，因此会连 LASOT train JSON 一起处理，导致你必须有 train classes/images。不要直接全量跑。

## 2. PDM / BURST

入口：

```bash
python3 tool_build_dataset_json_pdm.py \
  --original_iploc_json ./data/iploc/2_shots_pdm.json \
  --burst_annotations_json /ssd1/dataset/ICL_tracking/video/burst/annotations/test/all_classes.json \
  --burst_frames_base_dir /ssd1/dataset/ICL_tracking/video/burst/frames \
  --out_dir ./data \
  --out_prefix pdm \
  --export_root /ssd1/dataset/ICL_tracking_minimized/video/burst/frames
```

### PDM build 逻辑

- 只使用 BURST `annotations/test/all_classes.json`；
- frame path 来自 `burst/frames/test/...`；
- 构造：
  - `pdm_1shot_T2.json`
  - `pdm_2shot_T2.json`
- negative 是 out-class image。

### 对我们意味着什么

PDM 不需要 BURST train，**只需要 BURST test annotations + test frames**。

但 PDM negative 是 out-of-class，不如 LaSOT/VastTrack 对 instance-level false positive 诊断强。

## 3. GOT-10k

入口：

```bash
python3 tool_build_dataset_json_got10k.py \
  --got_root /ssd1/dataset/ICL_tracking/video/got10k \
  --split val \
  --out_dir ./data \
  --seed 1234 \
  --export_root /ssd1/dataset/ICL_tracking_minimized/video/got10k
```

### GOT-10k build 逻辑

- 明确只用 `--split val`；
- 默认 val=180 sequences；
- 从每个 sequence 取 8 refs + positive；
- outclass 从另一个 sequence 取；
- 输出 `got10k-val_{N}shot_T2.json`。

### 对我们意味着什么

GOT-10k 只需要 **val split**，不需要 train/test split。

但 GOT-10k negative 是 out-of-class，也不是第一优先级。

## 4. VastTrack

入口：

```bash
python3 tool_build_dataset_json_VastTrack.py \
  --vasttrack_root /ssd1/dataset/ICL_tracking/video/VastTrack \
  --output_dir ./data \
  --export_root /ssd1/dataset/ICL_tracking_minimized/video/VastTrack \
  --seed 1234
```

### VastTrack build 逻辑

- 没有 train/test split；
- 每个 class 至少需要 2 个 subclasses；
- subA 取 refs + positive；
- subB 取 in-class negative；
- 每个 eligible class 最多 1 个 sample；
- 输出：
  - `VastTrack_test_1shot_T2.json`
  - `VastTrack_test_2shot_T2.json`
  - `VastTrack_test_4shot_T2.json`
  - `VastTrack_test_8shot_T2.json`

### 对我们意味着什么

VastTrack 不涉及 train。它直接就是 test-style in-class negative 数据，很适合 E-002。

## 5. extract_dataset.sh 的坑

官方 `extract_dataset.sh`：

```bash
for JSON_PATH in "${DATA_DIR}"/*.json; do
  python3 tool_extract_dataset_from_json.py \
    "${JSON_PATH}" \
    "${DST_ROOT}" \
    --src_root "${SRC_ROOT}" \
    --write_json
done
```

问题：它会处理全部 JSON，包括：

```text
LASOT_*_train.json
```

如果只准备 test 数据，原版 extract 会报大量 missing。E-002 应该改成 test-only：

```bash
for JSON_PATH in \
  ./data/LASOT_1shot_T2_classwise-split_test.json \
  ./data/VastTrack_test_1shot_T2.json \
  ./data/got10k-val_1shot_T2.json \
  ./data/pdm_1shot_T2.json; do
  python3 ./tool_extract_dataset_from_json.py \
    "$JSON_PATH" \
    /home/featurize/data/ICL_tracking_minimized \
    --src_root /home/featurize/data/ICL_tracking \
    --write_json
done
```

## 6. E-002 最小下载建议

### 第一优先级：LaSOT test manifest 所需图像

原因：in-class negative，样本数 140，最贴近“同类不同 instance 是否 FP”的问题。

理论上只需：

```text
LASOT_1shot_T2_classwise-split_test.json
```

引用到的 420 张图像。

但实际下载时 LaSOT 官方通常按 class/sequence 包组织，可能无法只下 420 张。仍然可以只解压/保留 manifest 涉及的 sequences。

### 第二优先级：VastTrack 1-shot T2

原因：也是 in-class negative，样本更多约 391。

```text
VastTrack_test_1shot_T2.json
```

### 第三优先级：GOT-10k val / PDM-BURST test

它们主要是 out-of-class negative，适合补充验证，但不是最关键。

## 7. 是否需要 train？

当前不需要。

- 不训练 LoRA；
- 不重新 build full JSON；
- 不跑 official train split；
- 只做现象发现/评估。

只有在后续决定训练 verifier / adapter / LoRA 时，才需要考虑 train JSON 和对应源数据。

## 8. 推荐 next action

1. 不跑 `shell_build_data-json.sh`；
2. 不跑原版 `extract_dataset.sh`；
3. 写/使用 test-only extract；
4. 第一阶段只处理：
   ```text
   LASOT_1shot_T2_classwise-split_test.json
   VastTrack_test_1shot_T2.json
   ```
5. 先得到 minimized image set；
6. 再跑 2-sample smoke 和小规模评估。
