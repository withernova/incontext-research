# 后续实验构想：集合相同、身份不同的 candidate 对照

目标：更直接检验 container hypothesis / 内部对应是否有价值。

构造两个 candidate：

\[
C^{+} \quad\text{和}\quad C^{-}
\]

让二者尽可能保持相似的全局 feature distribution：

\[
\operatorname{Pool}(C^{+}) \approx \operatorname{Pool}(C^{-})
\]

但内部对应不同：

- \(C^{+}\) 是正确实例；
- \(C^{-}\) 是同类实例；
- 或者 \(C^{-}\) 由正确实例的部件重新排列而成；
- 或者将 identity marker 替换为另一个实例的局部区域。

然后测试：

\[
s_{\mathrm{global}}(C^{+}) \approx s_{\mathrm{global}}(C^{-})
\]

但希望：

\[
s_{\mathrm{struct}}(C^{+}) > s_{\mathrm{struct}}(C^{-})
\]

如果结构分支能在 pooled semantics 几乎相同的情况下区分二者，才是真正证明内部对应有价值。

## 建议的训练变体

下一阶段比较以下五组，保持参数量和训练预算一致：

\[
M_0: \text{FOCUS coordinate-text attention}
\]

\[
M_1: \text{support-object token attention}
\]

\[
M_2: \text{support-object token attention + global pooling}
\]

\[
M_3: \text{token correspondence without geometry}
\]

\[
M_4: \text{token correspondence + relative geometry + cycle consistency}
\]

关键比较：

- \(M_1 > M_0\)：说明直接使用 support visual tokens 比 coordinate-text proxy 更有效；
- \(M_3 > M_2\)：说明 token-level correspondence 比全局集合语义更有效；
- \(M_4 > M_3\)：说明内部几何关系确实提供额外价值。

若只有 \(M_1 > M_0\)，而 \(M_3, M_4\) 没有提高，那么正确结论应是：

> 强调 object visual evidence 有用，但没有证据表明内部结构建模有用。

## 与当前 E-001 的关系

- 当前 E-001 只验证行为层面的 containerization 迹象；
- 原 R-004 support padding 不再作为有效证据；
- 后续 query-side padding / candidate over-box sensitivity 应单独实现；
- 上述 candidate-pair 实验更适合作为下一阶段主实验，用来区分 global pooled semantics 与 structural correspondence。
