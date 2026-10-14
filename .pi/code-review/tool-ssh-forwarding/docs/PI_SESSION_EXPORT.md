# 可复制的 Pi Session HTML

Pi 原生 `--export` 生成的 HTML 只提供“复制消息链接”。用本仓库的包装器导出，可为每条用户/助手消息添加“复制文本”按钮，并在选中文本时显示“复制所选内容”。

安装 Pi 扩展后，在任意已保存的 Pi 会话中可直接运行：

```text
/export-copyable
/export-copyable notes/current-session.html
```

前者将文件输出到当前工作目录，后者使用你指定的相对或绝对 `.html` 路径。

```bash
python3 scripts/pi_session_export.py \
  ~/.pi/agent/sessions/<项目目录>/<session>.jsonl \
  /tmp/session.copyable.html
```

已有原生导出文件时，可原地增强：

```bash
python3 scripts/pi_session_export.py --enhance /path/to/session.html
```

复制单条消息直接保留 session 中 user/assistant 的原始 Markdown text block；不会复制 Pi 的 thinking、工具调用、工具输出、token 或 managed-execution lease。“复制所选内容”按浏览器所见文本复制，适合摘取跨段片段。该增强完全离线，生成的 HTML 仍可单文件打开和分享。
