"""Shared priorities for research implementation instructions."""

DEFAULT_CODE_TEST_POLICY = (
    "默认不运行测试、构建、smoke 或 import/启动检查，也不新增测试 Run；仅用户明确要求时执行。"
    "仓库默认测试约定不是本轮授权，不得委派其他 Agent 绕过。"
    "未测试不阻断代码交付、审阅或提交；报告‘未测试’，不编造 test_evidence 或声称已验证。"
)

ALGORITHM_IMPLEMENTATION_GUIDANCE = (
    "实现优先：完成真实算法、数据流、梯度/干预逻辑与指标计算，不用占位文件代替实现。\n"
    + DEFAULT_CODE_TEST_POLICY + "\n"
    "代码位置以当前 Workspace 为准：本地修改前执行 code prepare，失败即停止；"
    "审阅后提交并 code publish。Git 状态、diff 和路径安全检查保留；"
    "不把代码审阅当作运行验证，不用 SSH patch、强推或部署 latest 绕过绑定与部署边界。"
)
