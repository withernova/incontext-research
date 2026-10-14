#!/usr/bin/env bash
# migrate-machine.sh — 把 survey-tool + 科研项目从"源机器"搬到"新机器"（默认按 macOS 目标设计）。
#
# 设计前提（见 docs/MULTI_MACHINE.md）：
#   * 工具仓库（含 .git）→ 拷到新机器，未 push 的提交随之过去
#   * 科研项目 canonical → 拷项目目录（.publish 镜像可从 GitHub 重新 clone，默认不拷）
#   * 每台机器本地：config.json / ~/.pi / SSH / Zotero 各自维护 —— 本脚本只生成新机器的
#     config.json 和 ssh 配置"建议文件"，绝不改新机器已有的 ~/.ssh/config
#
# 在"新机器"（Mac）上运行，通过 ssh 从源机器拉取：
#   ssh <源机器别名> 'cat ~/Tools/survey-tool/scripts/migrate-machine.sh' > ~/migrate-machine.sh
#   bash ~/migrate-machine.sh --source-host <源机器别名> --dry-run     # 先看会做什么
#   bash ~/migrate-machine.sh --source-host <源机器别名>               # 真正执行
# （也支持 `ssh <别名> 'cat ...' | bash -s -- --source-host <别名>`：内部 ssh 已用 -n/-T 保护 stdin）
#
# 兼容 macOS 自带 bash 3.2：不使用关联数组等 bash4 语法。
set -euo pipefail

SCRIPT_VERSION="2026-10-01.2"

SOURCE_HOST=""
LOCAL_SOURCE=0
SOURCE_TOOL=""
SOURCE_PROJECT=""
DEST_ROOT="$HOME"
DEST_TOOL=""
DEST_PROJECT=""
DEST_PI_HOME="${PI_AGENT_DIR:-$HOME/.pi/agent}"
PORT=""
DRY_RUN=0
ALLOW_RUNNING_SERVER=0
WITH_PUBLISH_MIRROR=0
WITH_RESEARCH_TMP=0
WITH_PI_STATE=1
WITH_PI_SESSIONS=0
SKIP_PI_COMPONENTS=0
SKIP_SMOKE_TEST=0
EMIT_SSH_CONFIG=0
TRANSPORT=auto
NO_VERIFY=0

usage() {
  cat <<'USAGE'
用法（在新机器上运行）：
  migrate-machine.sh --source-host <ssh别名> [选项]
  migrate-machine.sh --local-source [选项]        # 同机自检/预演（源=本地路径）

必填（二选一）：
  --source-host HOST        新机器上用于连接源机器的 ssh 别名（本机先 `ssh HOST true` 能通）
  --local-source            源就是本机（用于自检、预演、先打包再拷贝）

常用选项：
  --source-tool PATH        源上的 survey-tool 目录（默认 $SOURCE_HOME/Tools/survey-tool）
  --source-project PATH     源上的科研项目目录（默认读源 config.json 的 projects[0]）
  --dest-root PATH          新机器根目录（默认 ${HOME}）
  --dest-tool PATH          新机器工具目录（默认 $DEST_ROOT/Tools/survey-tool）
  --dest-project PATH       新机器项目目录（默认 $DEST_ROOT/Projects/<项目名>）
  --dest-pi-home PATH       pi 配置目录（默认 $HOME/.pi/agent）
  --port N                  新机器监听端口（默认沿用源 config.json 的 port）
  --with-publish-mirror     连 .publish 镜像一起拷（默认不拷，可从 GitHub 重新 clone）
  --with-research-tmp       连 shell/06_experiments/E-009/research_tmp 一起拷（默认不拷，约 400MB）
  --with-pi-sessions        连 ~/.pi/agent/sessions 一起拷（agent 历史，可能较大）
  --no-pi-state             不拷 pi 的 settings.json / multi-workspace.json
  --skip-pi-components      不在新机器上执行 scripts/install-pi-components.sh
  --skip-smoke-test         拷完不启动服务器做健康检查
  --emit-ssh-config         生成 <dest-root>/.ssh/config.survey-tool-suggested（只生成，不安装）
  --transport MODE          传输方式：auto（默认）/ rsync / tar。
                            auto：本机 rsync 是 openrsync（macOS 自带）时自动改用 tar 管道，
                            因为 openrsync 与远端 GNU rsync 3.x 握手会直接断流。
  --dry-run                 只打印将执行的动作（rsync -n），不写任何文件
  --allow-running-server    源机器仍在跑 survey-tool 时也继续（sqlite 可能不一致，不建议）
  --no-verify               跳过两侧文件数量/状态文件校验
  -h|--help                 显示本帮助

安全边界：
  * 不拷贝任何私钥、~/.pi/agent/auth.json、models-store.json 等凭据文件
  * 不修改新机器已有的 ~/.ssh/config，只生成建议文件
  * 默认不使用 rsync --delete（不删除新机器上的额外文件）
USAGE
}

log()  { printf '\033[1m==> %s\033[0m\n' "$*"; }
note() { printf '    %s\n' "$*"; }
warn() { printf '\033[33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[31m[error]\033[0m %s\n' "$*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --source-host)          SOURCE_HOST="${2:?--source-host 需要参数}"; shift 2;;
    --local-source)         LOCAL_SOURCE=1; shift;;
    --source-tool)          SOURCE_TOOL="${2:?}"; shift 2;;
    --source-project)       SOURCE_PROJECT="${2:?}"; shift 2;;
    --dest-root)            DEST_ROOT="${2:?}"; shift 2;;
    --dest-tool)            DEST_TOOL="${2:?}"; shift 2;;
    --dest-project)         DEST_PROJECT="${2:?}"; shift 2;;
    --dest-pi-home)         DEST_PI_HOME="${2:?}"; shift 2;;
    --port)                 PORT="${2:?}"; shift 2;;
    --with-publish-mirror)  WITH_PUBLISH_MIRROR=1; shift;;
    --with-research-tmp)    WITH_RESEARCH_TMP=1; shift;;
    --with-pi-sessions)     WITH_PI_SESSIONS=1; shift;;
    --no-pi-state)          WITH_PI_STATE=0; shift;;
    --skip-pi-components)   SKIP_PI_COMPONENTS=1; shift;;
    --skip-smoke-test)      SKIP_SMOKE_TEST=1; shift;;
    --emit-ssh-config)      EMIT_SSH_CONFIG=1; shift;;
    --transport)            TRANSPORT="${2:?--transport 需要参数: auto|rsync|tar}"; shift 2;;
    --dry-run)              DRY_RUN=1; shift;;
    --allow-running-server) ALLOW_RUNNING_SERVER=1; shift;;
    --no-verify)            NO_VERIFY=1; shift;;
    -h|--help)              usage; exit 0;;
    *) die "未知参数：$1（--help 查看用法）";;
  esac
done

[ "$LOCAL_SOURCE" = 1 ] || [ -n "$SOURCE_HOST" ] || { usage >&2; die "必须给 --source-host <ssh别名> 或 --local-source"; }

# 迁移只需要文件传输与远端命令执行，不需要端口转发。操作员的 ~/.ssh/config 里常带
# RemoteForward/LocalForward（如 7890 / 11451），端口被占时 ssh 会直接断开。
# ClearAllForwardings 只影响本次调用，不改也不删任何配置文件；SURVEY_TOOL_KEEP_FORWARDS=1 可保留。
# -n：ssh 默认会把本地 stdin 转发给远端；当本脚本自己是 `... | bash -s` 从管道执行时，
#     那会把脚本正文当作 stdin 吃掉，脚本会在第一个 ssh 调用后静默结束。
# -T：不分配 PTY，避免操作员 ssh 配置里 RequestTTY 之类导致输出被 CRLF 污染。
SSH_BASE=( -n -T -o BatchMode=yes -o ConnectTimeout=20 )
# rsync 的协议数据就走 ssh 的 stdin，绝不能加 -n（会把协议流接到 /dev/null → protocol incompatibility）
RSYNC_SSH_BASE=( -T -o BatchMode=yes -o ConnectTimeout=20 )
[ "${SURVEY_TOOL_KEEP_FORWARDS:-0}" = 1 ] || { SSH_BASE+=( -o ClearAllForwardings=yes ); RSYNC_SSH_BASE+=( -o ClearAllForwardings=yes ); }
if [ -n "${SURVEY_TOOL_SSH_OPTS:-}" ]; then
  # shellcheck disable=SC2206
  SSH_BASE+=( ${SURVEY_TOOL_SSH_OPTS} )
  # shellcheck disable=SC2206
  RSYNC_SSH_BASE+=( ${SURVEY_TOOL_SSH_OPTS} )
fi
RSYNC_SSH="ssh ${RSYNC_SSH_BASE[*]}"

# 在源机器上执行一条命令；--local-source 时就是本机执行。
run_src() {
  if [ "$LOCAL_SOURCE" = 1 ]; then
    bash -c "$1"
  else
    ssh "${SSH_BASE[@]}" -- "$SOURCE_HOST" "$1"
  fi
}

RSYNC_FLAGS=( -a )
[ "$DRY_RUN" = 1 ] && RSYNC_FLAGS+=( -n -i )
# macOS 自带 openrsync 对一些 GNU 选项支持不一；需要时用环境变量追加（如 --protocol=29）
if [ -n "${SURVEY_TOOL_RSYNC_ARGS:-}" ]; then
  # shellcheck disable=SC2206
  RSYNC_FLAGS+=( ${SURVEY_TOOL_RSYNC_ARGS} )
fi

# 排除模式（不带 --exclude 前缀，两种传输各自翻译）：
# 以 / 开头的表示"仅传输根目录下该路径"。
EXCLUDES_COMMON=( '__pycache__' '.pytest_cache' '*.pyc' '.DS_Store' )
EXCLUDES_TOOL=( "${EXCLUDES_COMMON[@]}" '/config.json' 'web/node_modules' 'node_modules' '.mypy_cache' '.ruff_cache' )
EXCLUDES_PROJECT=( "${EXCLUDES_COMMON[@]}" 'codespace' )
[ "${WITH_PUBLISH_MIRROR}" = 0 ] && EXCLUDES_PROJECT+=( '.publish' )
[ "${WITH_RESEARCH_TMP}" = 0 ] && EXCLUDES_PROJECT+=( 'shell/06_experiments/E-009/research_tmp' )
CURRENT_EXCLUDES=()

# 本机 rsync 是 openrsync 时改走 tar 管道：openrsync 与 GNU rsync 3.x 协商会失败
# （表现为 "connection unexpectedly closed (0 bytes received)" / "unexpected end of file"）。
TRANSPORT_REASON=""
if [ "$TRANSPORT" = auto ]; then
  if rsync --version 2>/dev/null | head -1 | grep -qi openrsync; then
    TRANSPORT=tar; TRANSPORT_REASON="本机 rsync 是 openrsync，与远端 rsync 3.x 不兼容 → 改用 tar"
  else
    TRANSPORT=rsync; TRANSPORT_REASON="本机 rsync 可用"
  fi
fi
case "$TRANSPORT" in
  rsync|tar) [ -n "$TRANSPORT_REASON" ] || TRANSPORT_REASON="由 --transport 指定";;
  *) die "--transport 只支持 auto|rsync|tar";;
esac

trace() { [ "$DRY_RUN" = 1 ] && printf '    [dry-run] %s\n' "$*"; return 0; }

# 传输一个目录（读 CURRENT_EXCLUDES）；源可以是本机或远端
transport_copy() {
  _src="$1"; _dest="$2"
  [ "$DRY_RUN" = 1 ] || mkdir -p "$_dest"
  if [ "$TRANSPORT" = rsync ]; then
    _ex=()
    for _p in "${CURRENT_EXCLUDES[@]}"; do _ex+=( --exclude "${_p%/}" ); done
    if [ "$LOCAL_SOURCE" = 1 ]; then
      rsync "${RSYNC_FLAGS[@]}" "${_ex[@]}" "$_src/" "$_dest/"
    else
      rsync "${RSYNC_FLAGS[@]}" -e "$RSYNC_SSH" "${_ex[@]}" "$SOURCE_HOST:$_src/" "$_dest/"
    fi
    return
  fi
  # tar 模式：在源端打包（排除项由源端 tar 应用），本地解包
  _tex=()
  for _p in "${CURRENT_EXCLUDES[@]}"; do
    case "$_p" in
      /*) _tex+=( "--exclude=.${_p}" );;            # /config.json → ./config.json（锚定）
      *)  _tex+=( "--exclude=${_p%/}" "--exclude=./${_p%/}" );;
    esac
  done
  if [ "$DRY_RUN" = 1 ]; then
    trace "tar: ${_src} → ${_dest}（排除 ${CURRENT_EXCLUDES[*]}）"
    return
  fi
  if [ "$LOCAL_SOURCE" = 1 ]; then
    tar -C "$_src" -cf - "${_tex[@]}" . | tar -C "$_dest" -xf -
  else
    _cmd="tar -C $(_q "$_src") -cf -"
    for _p in "${_tex[@]}"; do _cmd="$_cmd $(_q "$_p")"; done
    _cmd="$_cmd ."
    ssh "${SSH_BASE[@]}" -- "$SOURCE_HOST" "$_cmd" | tar -C "$_dest" -xf -
  fi
}

_q() { printf '%q' "$1"; }

log "阶段 0/7 · 预检（migrate-machine.sh ${SCRIPT_VERSION}，bash3.2 安全版）"
for bin in rsync python3; do command -v "$bin" >/dev/null 2>&1 || die "新机器缺少 $bin"; done
if [ "$LOCAL_SOURCE" = 0 ]; then
  command -v ssh >/dev/null 2>&1 || die "新机器缺少 ssh"
  ssh "${SSH_BASE[@]}" -- "$SOURCE_HOST" true >/dev/null 2>&1 \
    || die "无法免密 ssh 到源机器 '$SOURCE_HOST'：先自己跑 \`ssh $SOURCE_HOST true\` 排查（若报 'Address already in use / Could not request local forwarding'，说明该别名带端口转发；脚本默认已加 ClearAllForwardings=yes 屏蔽）"
  if [ ! -t 0 ]; then note "脚本正从 stdin 管道执行；已用 ssh -n/-T 保护 stdin，建议直接 \`bash migrate-machine.sh ...\`"; fi
  SOURCE_HOME="$(run_src 'printf %s "$HOME"')"
  note "源机器：${SOURCE_HOST}（${SOURCE_HOME}）"
else
  SOURCE_HOME="$HOME"
  note "源机器：本机（--local-source）"
fi
[ -n "$SOURCE_HOME" ] || die "无法确定源机器 HOME"
[ -n "$SOURCE_TOOL" ] || SOURCE_TOOL="$SOURCE_HOME/Tools/survey-tool"
run_src "test -f '$SOURCE_TOOL/server.py'" || die "源机器上找不到 survey-tool：$SOURCE_TOOL"
[ -n "$SOURCE_PROJECT" ] || SOURCE_PROJECT="$(run_src "python3 -c \"import json,sys;print(json.load(open('$SOURCE_TOOL/config.json'))['projects'][0])\"" )" \
  || die "无法从源 config.json 读取 projects[0]，请显式给 --source-project"
[ -n "$SOURCE_PROJECT" ] || die "无法确定源项目路径，请显式给 --source-project"
run_src "test -d '$SOURCE_PROJECT'" || die "源机器上找不到项目目录：$SOURCE_PROJECT"
[ -n "$PORT" ] || PORT="$(run_src "python3 -c \"import json;print(json.load(open('$SOURCE_TOOL/config.json')).get('port',7421))\"" )"
[ -n "$PORT" ] || PORT=7421
[ -n "$DEST_TOOL" ] || DEST_TOOL="$DEST_ROOT/Tools/survey-tool"
PROJECT_NAME="$(basename "$SOURCE_PROJECT")"
[ -n "$DEST_PROJECT" ] || DEST_PROJECT="$DEST_ROOT/Projects/$PROJECT_NAME"

# 判定源侧是否还在跑 survey-tool：
#   1) 端口探测（最贴近事实：服务占用 $PORT 时说明它还在写 .survey-tool/）
#   2) 进程名兜底，但要求 python 前缀 + [s]erver 括号写法：
#      裸 'server.py' 会匹配到承载 pgrep 的 `bash -c` 自身，也会匹配任何命令行里提到 server.py 的进程。
SRC_PORT_BUSY=0
if run_src "python3 -c \"import socket,sys;s=socket.socket();s.settimeout(1);sys.exit(0 if s.connect_ex(('127.0.0.1',$PORT))==0 else 1)\"" >/dev/null 2>&1; then
  SRC_PORT_BUSY=1; SRC_BUSY_WHY="端口 $PORT 有进程在监听"
fi
if [ "$SRC_PORT_BUSY" = 0 ] && run_src "pgrep -f '[p]ython[0-9.]* .*[s]erver\.py' >/dev/null 2>&1"; then
  SRC_PORT_BUSY=1; SRC_BUSY_WHY="检测到 python 运行 server.py"
fi
if [ "$SRC_PORT_BUSY" = 1 ]; then
  if [ "$ALLOW_RUNNING_SERVER" = 1 ]; then
    warn "源机器上 survey-tool 可能仍在运行（${SRC_BUSY_WHY}）；--allow-running-server 已指定，继续（sqlite -wal 可能不一致）"
  else
    die "源机器上 survey-tool 仍在运行（${SRC_BUSY_WHY}）：请先停掉它再迁移（避免 .survey-tool/*.sqlite3 半写），或加 --allow-running-server 自行承担风险"
  fi
fi

note "源工具：$SOURCE_TOOL"
note "源项目：$SOURCE_PROJECT"
note "新工具：$DEST_TOOL"
note "新项目：$DEST_PROJECT"
note "pi 配置：${DEST_PI_HOME}（$( [ "$WITH_PI_STATE" = 1 ] && echo '拷 settings/multi-workspace' || echo '跳过' )）"
note "传输方式：${TRANSPORT}（${TRANSPORT_REASON}）"
note "端口：$PORT$( [ "$DRY_RUN" = 1 ] && echo '（dry-run：不写任何文件）' )"

log "阶段 1/7 · 工具仓库（含 .git，未 push 的提交随之过去）"
# config.json 是每台机器私有的绝对路径配置，绝不从源机器带过来（见 docs/MULTI_MACHINE.md）
CURRENT_EXCLUDES=( "${EXCLUDES_TOOL[@]}" )
transport_copy "$SOURCE_TOOL" "$DEST_TOOL"
note "工具文件数：$(find "$DEST_TOOL" -type f 2>/dev/null | wc -l | tr -d ' ')（dry-run 时目标可能还是空的）"

log "阶段 2/7 · 新机器 config.json"
# github_repo / github_branch / freeze_legacy_writes 不是机器专属路径，从源 config.json 继承；
# projects_root / projects / skill_dir / port 必须指向新机器，绝不继承。
SRC_CONFIG_EXTRAS="$(run_src "python3 - '$SOURCE_TOOL/config.json' <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print(json.dumps({k: d[k] for k in ('github_repo','github_branch','freeze_legacy_writes') if k in d}))
PY" 2>/dev/null || true)"
[ -n "$SRC_CONFIG_EXTRAS" ] || SRC_CONFIG_EXTRAS='{}'
if [ -f "$DEST_TOOL/config.json" ]; then
  note "已存在，保留不动。请人工确认这四个键指向新机器路径："
  python3 -c "import json;d=json.load(open('$DEST_TOOL/config.json'));print('  projects_root =',d.get('projects_root'));print('  projects      =',d.get('projects'));print('  skill_dir     =',d.get('skill_dir'));print('  port          =',d.get('port'))"
  note "期望值：projects_root=$(dirname "$DEST_PROJECT") / projects=[$DEST_PROJECT] / skill_dir=$DEST_TOOL/skills/research-survey / port=$PORT"
  if python3 -c "import json,pathlib,sys;d=json.load(open('$DEST_TOOL/config.json'));sys.exit(0 if all(pathlib.Path(p).is_dir() for p in d.get('projects') or []) else 1)"; then
    note "config.json 里的项目路径在本机存在 ✓"
  else
    warn "config.json 的 projects 指向本机不存在的目录（很可能直接拷了源机器的 config.json）——请手动改成 $DEST_PROJECT"
  fi
elif [ "$DRY_RUN" = 1 ]; then
  note "dry-run：会从 config.example.json 生成 $DEST_TOOL/config.json"
else
  python3 - "$DEST_TOOL/config.example.json" "$DEST_TOOL/config.json" "$(dirname "$DEST_PROJECT")" "$DEST_PROJECT" "$DEST_TOOL/skills/research-survey" "$PORT" "$SRC_CONFIG_EXTRAS" <<'PY'
import json, pathlib, sys
example, out, projects_root, project, skill_dir, port, extras_json = sys.argv[1:8]
data = json.loads(pathlib.Path(example).read_text(encoding="utf-8"))
try:
    data.update(json.loads(extras_json or "{}"))
except ValueError:
    pass
data["projects_root"] = projects_root
data["projects"] = [project]
data["skill_dir"] = skill_dir
data["port"] = int(port)
pathlib.Path(out).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("已生成", out)
PY
fi

log "阶段 3/7 · 科研项目"
CURRENT_EXCLUDES=( "${EXCLUDES_PROJECT[@]}" )
transport_copy "$SOURCE_PROJECT" "$DEST_PROJECT"
if [ "$WITH_PUBLISH_MIRROR" = 0 ]; then
  note "未拷 .publish 镜像；需要时在新机器上：git clone <你配置的 snapshot remote> $DEST_PROJECT/.publish"
fi

log "阶段 4/7 · pi 组件与本机状态"
if [ "$WITH_PI_STATE" = 1 ]; then
  [ "$DRY_RUN" = 1 ] || mkdir -p "$DEST_PI_HOME"
  for f in settings.json multi-workspace.json; do
    if run_src "test -f '$SOURCE_HOME/.pi/agent/$f'"; then
      if [ "$DRY_RUN" = 1 ]; then note "dry-run：会拷 ~/.pi/agent/$f"; else
        if [ "$LOCAL_SOURCE" = 1 ]; then cp -p "$SOURCE_HOME/.pi/agent/$f" "$DEST_PI_HOME/$f"
        else ssh "${SSH_BASE[@]}" -- "$SOURCE_HOST" "cat '$SOURCE_HOME/.pi/agent/$f'" > "$DEST_PI_HOME/$f"; fi
        note "已拷 ~/.pi/agent/$f"
      fi
    fi
  done
  MW="$DEST_PI_HOME/multi-workspace.json"
  if [ -f "$MW" ] && grep -q '"/mnt/' "$MW" 2>/dev/null; then
    if [ "$DRY_RUN" = 1 ]; then note "dry-run：会清空 multi-workspace.json 里指向 /mnt/ 的路径（Windows 专属）"
    else
      python3 - "$MW" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]); d = json.loads(p.read_text(encoding="utf-8"))
changed = []
for name, ws in (d.get("workspaces") or {}).items():
    if isinstance(ws, dict) and str(ws.get("path") or "").startswith("/mnt/"):
        changed.append(name); ws["path"] = ""
if changed:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("已清空 Windows 专属路径：", ", ".join(changed), "→ 请在新机器上填 Zotero 数据目录")
PY
    fi
  fi
  note "未拷贝凭据（auth.json / models-store.json / 私钥）；在新机器上重新登录 pi 与 gh"
else
  note "--no-pi-state：跳过 pi settings/multi-workspace"
fi
if [ "$WITH_PI_SESSIONS" = 1 ]; then
  CURRENT_EXCLUDES=( "${EXCLUDES_COMMON[@]}" )
  transport_copy "$SOURCE_HOME/.pi/agent/sessions" "$DEST_PI_HOME/sessions"
else
  note "未拷 agent 会话历史（要拷加 --with-pi-sessions）"
fi
if [ "$SKIP_PI_COMPONENTS" = 1 ]; then
  note "--skip-pi-components：跳过；请自行执行 $DEST_TOOL/scripts/install-pi-components.sh"
elif [ "$DRY_RUN" = 1 ]; then
  note "dry-run：会执行 PI_AGENT_DIR=$DEST_PI_HOME $DEST_TOOL/scripts/install-pi-components.sh"
elif [ -x "$DEST_TOOL/scripts/install-pi-components.sh" ]; then
  # 安装器可能因为新机器上已有真实（非软链）的旧扩展而拒绝执行并 exit 1；
  # 这不该中断迁移（校验与健康检查更重要），因此只告警并给出可照抄的修复命令。
  if PI_AGENT_DIR="$DEST_PI_HOME" "$DEST_TOOL/scripts/install-pi-components.sh"; then
    :
  else
    warn "install-pi-components.sh 未成功（常见原因：$DEST_PI_HOME/extensions 里已有真实文件/目录而非软链）"
    warn "  → 先移开旧的：mv \"$DEST_PI_HOME/extensions/experiment-watchdog\" \"$DEST_PI_HOME/extensions/experiment-watchdog.old-\$(date +%Y%m%d)\""
    warn "  → 再单独执行：PI_AGENT_DIR=\"$DEST_PI_HOME\" \"$DEST_TOOL/scripts/install-pi-components.sh\""
    warn "继续后续阶段（两侧校验 / 健康检查不受影响）"
  fi
else
  warn "找不到 $DEST_TOOL/scripts/install-pi-components.sh，跳过"
fi

log "阶段 5/7 · 新机器 ssh 配置建议（只生成文件，不改你的 ~/.ssh/config）"
if [ "$EMIT_SSH_CONFIG" = 1 ]; then
  SUGGEST="$DEST_ROOT/.ssh/config.survey-tool-suggested"
  if [ "$DRY_RUN" = 1 ]; then
    note "dry-run：会生成 $SUGGEST"
  else
    mkdir -p "$DEST_ROOT/.ssh"
    : > "$SUGGEST"
    for h in $(run_src "python3 -c \"import json;print(' '.join(sorted({str(s.get('ssh_host') or '') for s in json.load(open('$SOURCE_PROJECT/.survey-tool/servers.json')) if s.get('ssh_host')})))\" 2>/dev/null"); do
      hostname="$(run_src "ssh -G '$h' 2>/dev/null | awk '\$1==\"hostname\"{print \$2; exit}'")"
      user="$(run_src "ssh -G '$h' 2>/dev/null | awk '\$1==\"user\"{print \$2; exit}'")"
      port="$(run_src "ssh -G '$h' 2>/dev/null | awk '\$1==\"port\"{print \$2; exit}'")"
      ident="$(run_src "ssh -G '$h' 2>/dev/null | awk '\$1==\"identityfile\"{print \$2; exit}'")"
      if [ -z "$hostname" ] || [ "$hostname" = "$h" ]; then
        warn "$h 在源机器上无法解析出 HostName（源 ~/.ssh/config 可能需要修），已跳过"
        continue
      fi
      {
        printf 'Host %s\n' "$h"
        printf '    HostName %s\n' "$hostname"
        [ -n "$user" ] && printf '    User %s\n' "$user"
        [ -n "$port" ] && [ "$port" != "22" ] && printf '    Port %s\n' "$port"
        printf '    IdentityFile %s\n' "${ident:-~/.ssh/id_ed25519}"
        printf '    IdentitiesOnly yes\n\n'
      } >> "$SUGGEST"
    done
    chmod 600 "$SUGGEST"
    note "已生成 ${SUGGEST}（请人工检查后合并进 ~/.ssh/config；私钥需在新机器上另行准备）"
  fi
else
  note "未生成 ssh 建议（要的话加 --emit-ssh-config）"
fi

log "阶段 6/7 · 校验"
if [ "$NO_VERIFY" = 1 ] || [ "$DRY_RUN" = 1 ]; then
  note "跳过校验"
else
  FAILED=0
  PY_HASH='import hashlib,pathlib,sys;p=pathlib.Path(sys.argv[1]);print(hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "")'
  PY_SIZE='import pathlib,sys;p=pathlib.Path(sys.argv[1]);print(p.stat().st_size if p.is_file() else "")'
  src_files="$(run_src "find '$SOURCE_PROJECT' -type f | wc -l")"
  dst_files="$(find "$DEST_PROJECT" -type f | wc -l)"
  note "项目文件数：源 $src_files / 新机器 ${dst_files}（新机器默认少 .publish 与 research_tmp 的文件）"
  for f in runs.json experiments.json workspaces.json servers.json; do
    s="$(run_src "python3 -c '$PY_HASH' '$SOURCE_PROJECT/.survey-tool/$f'")"
    d="$(python3 -c "$PY_HASH" "$DEST_PROJECT/.survey-tool/$f")"
    if [ -n "$s" ] && [ "$s" = "$d" ]; then note "  ok   .survey-tool/$f"; else warn "  DIFF .survey-tool/${f}（源 ${s:-缺失} / 新机器 ${d:-缺失}）"; FAILED=1; fi
  done
  for f in survey-tool-v2.sqlite3; do
    s="$(run_src "python3 -c '$PY_SIZE' '$SOURCE_PROJECT/.survey-tool/$f'")"
    d="$(python3 -c "$PY_SIZE" "$DEST_PROJECT/.survey-tool/$f")"
    if [ -n "$s" ] && [ "$s" = "$d" ]; then note "  ok   .survey-tool/${f}（$s bytes）"; else warn "  DIFF .survey-tool/$f 大小（源 ${s:-缺失} / 新机器 ${d:-缺失}）"; FAILED=1; fi
  done
  [ "$FAILED" = 0 ] || die "校验不通过：先别删除源机器数据"
fi

log "阶段 7/7 · 健康检查"
if [ "$SKIP_SMOKE_TEST" = 1 ] || [ "$DRY_RUN" = 1 ]; then
  note "跳过（--skip-smoke-test / --dry-run）"
else
  command -v curl >/dev/null 2>&1 || warn "新机器没有 curl，跳过健康检查"
  if command -v curl >/dev/null 2>&1; then
    SMOKE_LOG=/tmp/survey-tool-migrate-smoke.log
    SMOKE_HEALTH=/tmp/survey-tool-migrate-health.json
    : > "$SMOKE_LOG"
    # 用 exec 让子 shell 变成 python 进程：这样 $! 才是真正的服务器 PID。
    # （之前 nohup ... & echo $! 记到的是子 shell，kill 打空 → 留下占端口的孤儿进程。）
    ( cd "$DEST_TOOL" && exec python3 server.py --port "$PORT" >>"$SMOKE_LOG" 2>&1 </dev/null ) &
    SMOKE_PID=$!
    trap 'kill "${SMOKE_PID:-0}" 2>/dev/null || true' EXIT INT TERM
    ok=0
    i=0
    while [ "$i" -lt 20 ]; do
      if curl -fsS "http://127.0.0.1:$PORT/api/v2/health" > "$SMOKE_HEALTH" 2>/dev/null; then ok=1; break; fi
      i=$((i+1)); sleep 1
    done
    if [ "$ok" = 1 ]; then
      note "健康检查通过：$(head -c 400 "$SMOKE_HEALTH")"
    else
      warn "健康检查失败，日志尾巴："; tail -20 "$SMOKE_LOG" >&2 || true
    fi
    kill "$SMOKE_PID" 2>/dev/null || true
    wait "$SMOKE_PID" 2>/dev/null || true
    trap - EXIT INT TERM
    if kill -0 "$SMOKE_PID" 2>/dev/null; then warn "健康检查服务器未退出（PID ${SMOKE_PID}），请手动 kill"; fi
    [ "$ok" = 1 ] || die "新机器上服务器启动失败，请查看 $SMOKE_LOG"
  fi
fi

cat <<EOF

$(log "完成")
工具：$DEST_TOOL
项目：$DEST_PROJECT
启动：cd $DEST_TOOL && ./start.sh          # 或 caffeinate -i python3 server.py --port $PORT

在新机器上还需要人工做（脚本故意不代做）：
  1. SSH 私钥：新机器自己的密钥要能被远端服务器接受（authorized_keys），脚本不拷私钥
  2. GitHub：git/gh 认证（发布 snapshot 需要），脚本不拷凭据
  3. Zotero：如用论文库，把 multi-workspace.json 的 workspaces.zotero.path 指向新机器数据目录
  4. 远端路径与 policy：进入 UI 的 Workspace 页面确认 remote_repo / dataset 路径仍然正确
  5. 两机纪律：同一 canonical Markdown 不要两台机器同时改；切换前 push，开工前 git pull --ff-only
EOF
