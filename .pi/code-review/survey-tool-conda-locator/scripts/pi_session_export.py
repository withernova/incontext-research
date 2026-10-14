#!/usr/bin/env python3
"""Export a Pi JSONL session to a copy-friendly standalone HTML file.

Pi's native export contains a deep-link button, but not a convenient way to
copy a single user/assistant turn.  This wrapper preserves Pi's generated
document and appends an idempotent, offline-only enhancement: per-message copy
buttons and a copy-selected-text control.  It deliberately excludes thinking
blocks, tool calls and tool results from message copying.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys


MARKER = "<!-- survey-tool:pi-copyable-export/v1 -->"

STYLE = r"""
<style id="survey-tool-pi-copy-style">
  .pi-copy-text-btn { position:absolute; top:8px; right:44px; z-index:11; padding:5px 8px; border:1px solid var(--dim,#666); border-radius:4px; background:var(--container-bg,#222); color:var(--muted,#bbb); font:11px inherit; cursor:pointer; opacity:0; transition:opacity .15s,background .15s,color .15s; }
  .user-message:hover .pi-copy-text-btn, .assistant-message:hover .pi-copy-text-btn, .skill-user-entry:hover .pi-copy-text-btn, .pi-copy-text-btn:focus { opacity:1; }
  .pi-copy-text-btn:hover, .pi-copy-text-btn.copied { background:var(--accent,#4f8cff); color:var(--body-bg,#fff); border-color:var(--accent,#4f8cff); }
  #pi-copy-selection { position:fixed; right:20px; bottom:20px; z-index:100; display:none; padding:8px 12px; border:1px solid var(--dim,#666); border-radius:5px; background:var(--container-bg,#222); color:var(--text,#fff); font:12px ui-monospace,monospace; cursor:pointer; box-shadow:0 3px 14px rgba(0,0,0,.35); }
  #pi-copy-selection.visible { display:block; }
  @media (max-width:600px) { .pi-copy-text-btn { opacity:1; right:40px; } }
</style>
"""

SCRIPT = r"""
<script id="survey-tool-pi-copy-script">
(() => {
  "use strict";
  const copiedLabel = "已复制";
  let entriesById;

  function sessionEntries() {
    if (entriesById) return entriesById;
    try {
      const raw = document.getElementById("session-data").textContent.trim();
      const binary = atob(raw); const bytes = Uint8Array.from(binary, char => char.charCodeAt(0));
      const session = JSON.parse(new TextDecoder("utf-8").decode(bytes));
      entriesById = new Map((session.entries || []).map(entry => [String(entry.id), entry]));
    } catch (_) { entriesById = new Map(); }
    return entriesById;
  }

  function entryText(entry) {
    const message = entry && entry.type === "message" ? entry.message : null;
    if (!message || !["user", "assistant"].includes(message.role)) return "";
    const blocks = Array.isArray(message.content) ? message.content : [{type:"text", text:message.content}];
    return blocks.filter(block => block && block.type === "text" && typeof block.text === "string")
      .map(block => block.text).join("\n\n").trim();
  }

  async function copy(text, button) {
    if (!text) return;
    let done = false;
    try { await navigator.clipboard.writeText(text); done = true; } catch (_) {}
    if (!done) {
      const area = document.createElement("textarea"); area.value = text;
      area.style.cssText = "position:fixed;opacity:0;pointer-events:none"; document.body.appendChild(area);
      area.select(); done = document.execCommand("copy"); area.remove();
    }
    if (done && button) {
      const label = button.textContent; button.textContent = copiedLabel; button.classList.add("copied");
      setTimeout(() => { button.textContent = label; button.classList.remove("copied"); }, 1200);
    }
  }

  function addButtons() {
    document.querySelectorAll(".user-message[id^='entry-'],.assistant-message[id^='entry-'],.skill-user-entry[id^='entry-']").forEach(node => {
      if (node.querySelector(":scope > .pi-copy-text-btn")) return;
      const id = node.id.slice("entry-".length); const text = entryText(sessionEntries().get(id));
      if (!text) return;
      const button = document.createElement("button"); button.type = "button"; button.className = "pi-copy-text-btn";
      button.textContent = "复制文本"; button.title = "复制此条对话文本（不含思考和工具输出）";
      button.addEventListener("click", event => { event.preventDefault(); event.stopPropagation(); void copy(text, button); });
      node.appendChild(button);
    });
  }

  function selectedConversationText() {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0 || !selection.toString().trim()) return "";
    const fragment = selection.getRangeAt(0).cloneContents();
    fragment.querySelectorAll(".thinking-block,.tool-execution,.tool-call,.tool-item,.tool-result").forEach(node => node.remove());
    return fragment.textContent.trim();
  }

  const selected = document.createElement("button"); selected.id = "pi-copy-selection"; selected.type = "button"; selected.textContent = "复制所选内容";
  selected.addEventListener("click", () => { void copy(selectedConversationText(), selected); });
  document.body.appendChild(selected);
  document.addEventListener("selectionchange", () => {
    const range = window.getSelection(); const anchor = range && range.anchorNode;
    const inMessages = anchor && anchor.parentElement && anchor.parentElement.closest("#messages");
    selected.classList.toggle("visible", Boolean(inMessages && selectedConversationText()));
  });
  addButtons(); new MutationObserver(addButtons).observe(document.getElementById("messages"), {childList:true, subtree:true});
})();
</script>
"""


def enhance_html(path: pathlib.Path) -> bool:
    """Append copy controls once; return whether the document changed."""
    content = path.read_text(encoding="utf-8")
    if MARKER in content:
        return False
    if "</head>" not in content or "</body>" not in content:
        raise ValueError("not a complete Pi HTML export (missing head/body closing tag)")
    content = content.replace("</head>", f"{MARKER}\n{STYLE}</head>", 1)
    content = content.replace("</body>", f"{SCRIPT}</body>", 1)
    path.write_text(content, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a Pi session HTML with per-message copy controls")
    parser.add_argument("session", nargs="?", type=pathlib.Path, help="Pi session .jsonl; omit with --enhance")
    parser.add_argument("output", nargs="?", type=pathlib.Path, help="output .html (default: <session>.copyable.html)")
    parser.add_argument("--enhance", type=pathlib.Path, help="enhance an existing Pi-exported .html in place")
    parser.add_argument("--pi-bin", default="pi", help="Pi executable used for export (default: pi)")
    args = parser.parse_args()
    if bool(args.session) == bool(args.enhance):
        parser.error("provide SESSION OUTPUT, or --enhance EXISTING.html")
    if args.enhance and args.output:
        parser.error("OUTPUT is only valid when exporting a SESSION")
    return args


def main() -> int:
    args = parse_args()
    if args.enhance:
        if not args.enhance.is_file(): raise FileNotFoundError(args.enhance)
        changed = enhance_html(args.enhance)
        print(f"{'Enhanced' if changed else 'Already enhanced'}: {args.enhance}")
        return 0
    if not args.session.is_file(): raise FileNotFoundError(args.session)
    pi_bin = shutil.which(args.pi_bin) if not pathlib.Path(args.pi_bin).is_file() else args.pi_bin
    if not pi_bin: raise FileNotFoundError(f"Pi executable not found: {args.pi_bin}")
    output = args.output or args.session.with_suffix(".copyable.html")
    subprocess.run([str(pi_bin), "--export", str(args.session), str(output)], check=True)
    enhance_html(output)
    print(f"Copy-friendly Pi session export: {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"pi_session_export: {error}", file=sys.stderr)
        raise SystemExit(1)
