"""兼容入口：所有可编辑参数统一在 qwen3vl_8b_focus_branch.py。"""
_base_ = "qwen3vl_8b_focus_branch.py"
branch = dict(action="attention_intervene")
