# E-007：Query-stage reference-attention transplant

- 状态：R-000、R-001、R-002 已由用户批准并给予一次性执行授权；R-003–R-005 仍待审核，禁止执行。
- Primary intervention：softmax 后、dropout 前、`A@V` 前重写；保持 target row/head 原 `Q→R` mass，仅替换 reference span 内 shape；target head 保留自己的 V。
- 固定 source heads：`L15H13,L16H23,L18H15`。
- 固定 target heads：`L18H15,L19H03,L22H00,L20H08`。
- 执行链：R-000 correctness → R-001 n20 source/window gate → R-002 n20 teacher replay controls。任一 gate 失败，后续停止。
- 边界：R-002 是 teacher-forced、attention-level、分布外因果干预；不证明自然 bbox IoU 改善、identity understanding 或唯一电路。
