#!/usr/bin/env python3
"""Stable CLI bridge between a terminal pi agent and survey-tool state."""
import argparse, datetime, json, pathlib, subprocess, sys

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import server

def now(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")
def root_for(value):
    server.CFG=server.load_config(); server.SKILL=pathlib.Path(server.CFG["skill_dir"]); server.SKILL_SCRIPTS=server.SKILL/"scripts"
    p=pathlib.Path(value).expanduser()
    return p.resolve() if p.exists() else server.resolve_project(value)
def data(root): return server.experiment_data(root)
def find(rows,key):
    x=next((r for r in rows if r.get("id")==key),None)
    if not x: raise SystemExit(f"not found: {key}")
    return x
def emit(x): print(json.dumps(x,ensure_ascii=False,indent=2))
def json_arg(value,label):
    try: return json.loads(value)
    except json.JSONDecodeError as exc: raise SystemExit(f"{label} 不是合法 JSON：{exc.msg}")
def append_event(root,eid,kind,message,rid="",details=""):
    """Append a one-line event summary; the detail payload stays in the jsonl store."""
    with server.tool_state_transaction(root):
        return server._append_experiment_event(root,eid,kind,message,rid,details)

def main():
    ap=argparse.ArgumentParser(description="终端 Agent 与研究实验工作台之间的同步接口")
    ap.add_argument("--project",required=True,help="项目名或绝对路径")
    sub=ap.add_subparsers(dest="object",required=True)
    code=sub.add_parser("code",help="本地 Git 开发：远端 checkpoint/push、改后发布与指定 commit 部署（不启动 Run）")
    codes=code.add_subparsers(dest="action",required=True)
    for name in ("prepare","publish","deploy"):
        cp=codes.add_parser(name); cp.add_argument("--workspace-id",required=True)
        if name in {"publish","deploy"}:
            cp.add_argument("--commit",required=True)
        if name=="deploy":
            cp.add_argument("--confirmation",required=True)
    e=sub.add_parser("experiment"); es=e.add_subparsers(dest="action",required=True)
    en=es.add_parser("create",help="创建 Experiment 初稿及 canonical Markdown")
    en.add_argument("id",nargs="?",default="",help="可选显式 ID，如 E-003；省略则自动分配")
    en.add_argument("--title",required=True); en.add_argument("--workspace-id",required=True); en.add_argument("--objective",required=True)
    en.add_argument("--constraints",default=""); en.add_argument("--source-ref",default=""); en.add_argument("--evidence-ref",action="append",default=[])
    en.add_argument("--claim-ref",action="append",default=[]); en.add_argument("--kind",default="standalone"); en.add_argument("--agent-level",default="2",choices=["0","1","2","3"])
    en.add_argument("--run-groups-json",default="",help="Run group 对象数组 JSON"); en.add_argument("--metric-definitions-json",default="",help="指标定义对象数组 JSON")
    ec=es.add_parser("context",help="只读查询执行约束、注册表、解析路径与 gate（默认精简）"); ec.add_argument("id"); ec.add_argument("--run",default="",help="额外返回该 Run 的完整字段与解析路径"); ec.add_argument("--full",action="store_true",help="返回整个 Experiment 的全量 registry（旧行为）")
    ex=es.add_parser("constraints",help="context 的只读别名"); ex.add_argument("id")
    el=es.add_parser("events",help="列出事件摘要（单行索引）"); el.add_argument("id"); el.add_argument("--full",action="store_true",help="包含完整 details")
    ed=es.add_parser("event-detail",help="按 EVENT-ID 展开一条事件的完整 payload"); ed.add_argument("id"); ed.add_argument("event_id")
    ece=es.add_parser("compact-events",help="把 events.md 重写为单行摘要（details 仍在 jsonl）"); ece.add_argument("id")
    edoc=es.add_parser("docs",help="仅刷新该实验的阅读入口、文档目录和结果页，不修改注册表或研究正文"); edoc.add_argument("id"); edoc.add_argument("--dry-run",action="store_true",help="只输出预览，不写文件")
    eh=es.add_parser("handoff"); eh.add_argument("id"); eh.add_argument("--file",required=True,help="experiment-handoff/v1 JSON")
    eg=es.add_parser("governance",help="安全更新 Experiment 分组与指标注册表"); eg.add_argument("id"); eg.add_argument("--run-groups-json"); eg.add_argument("--metric-definitions-json")
    eag=es.add_parser("agent-grouping",help="Agent 部分成功地直接整理 Run Folder"); eag.add_argument("id"); eag.add_argument("--proposal-json"); eag.add_argument("--file")
    ea=es.add_parser("auto-review",help="显式批量按 Experiment 预授权策略评估"); ea.add_argument("id")
    r=sub.add_parser("run"); rs=r.add_subparsers(dest="action",required=True)
    rc=rs.add_parser("create"); rc.add_argument("experiment_id"); rc.add_argument("--id",required=True,help="canonical/descriptive Run ID；同时作为 registry ID、note 文件名和默认产物目录名"); rc.add_argument("--variant",required=True); rc.add_argument("--run-type",default=""); rc.add_argument("--purpose",default=""); rc.add_argument("--necessity",default=""); rc.add_argument("--evidence-basis",default=""); rc.add_argument("--implementation-summary",default=""); rc.add_argument("--implementation-details",default=""); rc.add_argument("--data-definition",default=""); rc.add_argument("--data-scale",default=""); rc.add_argument("--model-config",default=""); rc.add_argument("--variables-controls",default=""); rc.add_argument("--metric-definition",default=""); rc.add_argument("--integrity-gates",default=""); rc.add_argument("--expected-outcome",default=""); rc.add_argument("--acceptance-criteria",default=""); rc.add_argument("--dependencies",default=""); rc.add_argument("--limitations",default=""); rc.add_argument("--claim-boundary",default=""); rc.add_argument("--audit-paths",default=""); rc.add_argument("--status",default="draft"); rc.add_argument("--workspace-id",default=""); rc.add_argument("--git-commit",default=""); rc.add_argument("--config",default=""); rc.add_argument("--command",default=""); rc.add_argument("--log-path",default=""); rc.add_argument("--output-dir",default=""); rc.add_argument("--artifact-dir",default="",help="真实产物根目录；默认由 canonical Run ID 解析"); rc.add_argument("--artifacts",default=""); rc.add_argument("--tmux-session",default=""); rc.add_argument("--seed",default="")
    rc.add_argument("--group-id",default="",help="已声明的责任分组；默认首个分组")
    rc.add_argument("--metric-observations",default="",help="结构化指标观测对象数组 JSON")
    for flag in ("research-question","purpose","method-plan","hypothesis","metric-plan","architecture-plan","implementation-details"):
        if "--"+flag in rc._option_string_actions: continue
        rc.add_argument("--"+flag,default="")
    rc.add_argument("--implementation-ref",default="",help="survey-tool.run-implementation/v1 JSON")
    rk=rs.add_parser("rekey",help="把历史自动编号迁移为 canonical/descriptive Run ID"); rk.add_argument("id",help="旧 registry ID"); rk.add_argument("new_id",help="真实 canonical Run ID"); rk.add_argument("--adopt-existing-note",action="store_true",help="目标 descriptive note 已核对且应保留时使用")
    rr=rs.add_parser("submit-review",help="Agent 将 Run 初稿/完善稿提交给用户审核"); rr.add_argument("id"); rr.add_argument("--message",default="Run 初稿已完成，等待用户审核")
    rauto=rs.add_parser("auto-review",help="按 Experiment 策略把就绪的 Run 提交人工审核（不会自动批准或授权）"); rauto.add_argument("id")
    ru=rs.add_parser("update"); ru.add_argument("id"); ru.add_argument("--status"); ru.add_argument("--run-type"); ru.add_argument("--purpose"); ru.add_argument("--necessity"); ru.add_argument("--evidence-basis"); ru.add_argument("--implementation-summary"); ru.add_argument("--implementation-details"); ru.add_argument("--data-definition"); ru.add_argument("--data-scale"); ru.add_argument("--model-config"); ru.add_argument("--variables-controls"); ru.add_argument("--metric-definition"); ru.add_argument("--integrity-gates"); ru.add_argument("--expected-outcome"); ru.add_argument("--acceptance-criteria"); ru.add_argument("--dependencies"); ru.add_argument("--result-summary"); ru.add_argument("--limitations"); ru.add_argument("--conclusion-scope"); ru.add_argument("--claim-boundary"); ru.add_argument("--audit-paths"); ru.add_argument("--command"); ru.add_argument("--config"); ru.add_argument("--log-path"); ru.add_argument("--output-dir"); ru.add_argument("--artifact-dir"); ru.add_argument("--artifacts"); ru.add_argument("--tmux-session"); ru.add_argument("--git-commit"); ru.add_argument("--metrics"); ru.add_argument("--notes"); ru.add_argument("--agent-review-summary"); ru.add_argument("--agent-review-questions"); ru.add_argument("--message")
    ru.add_argument("--metric-observations",help="结构化指标观测对象数组 JSON")
    for flag in ("research-question","purpose","method-plan","hypothesis","metric-plan","architecture-plan","implementation-details","result-analysis"):
        if "--"+flag in ru._option_string_actions: continue
        ru.add_argument("--"+flag)
    ru.add_argument("--implementation-ref"); ru.add_argument("--key-results")
    rw=rs.add_parser("workflow",help="推进 Run 科研生命周期 v2"); rw.add_argument("id"); rw.add_argument("--action",dest="workflow_action",required=True,choices=["confirm-design","implementation-ready","reopen-design","begin-analysis","finalize-results","mark-failed"]); rw.add_argument("--result-analysis"); rw.add_argument("--key-results"); rw.add_argument("--limitations"); rw.add_argument("--artifacts")
    ev=sub.add_parser("event"); ev.add_argument("experiment_id"); ev.add_argument("--run",default=""); ev.add_argument("--type",default="progress"); ev.add_argument("--message",required=True); ev.add_argument("--details",default="")
    ob=sub.add_parser("outbox",help="Execution Outbox 显式协调接口"); obs=ob.add_subparsers(dest="action",required=True)
    obs.add_parser("list",help="列出公开 dispatch（不含 lease token/hash）"); ost=obs.add_parser("status",help="按 dispatch_id 查看公开状态"); ost.add_argument("dispatch_id")
    oq=obs.add_parser("enqueue",help="为 Run 当前授权幂等入队或解除已修复的 blocked"); oq.add_argument("run_id")
    oc=obs.add_parser("claim-next",help="原子领取下一个 dispatch 并取得 lease token"); oc.add_argument("--consumer",required=True); oc.add_argument("--experiment-id",default=""); oc.add_argument("--run-id",default="")
    for name in ("ack","running","complete","fail","release"):
        p=obs.add_parser(name,help={"ack":"确认实际执行路由","running":"确认真正开始并消费 Run 授权","complete":"以非空证据完成","fail":"记录分类失败","release":"执行开始前释放租约"}[name]); p.add_argument("dispatch_id"); p.add_argument("--lease-token",required=True); p.add_argument("--consumer",required=True)
        if name=="ack": p.add_argument("--actual-agent",required=True); p.add_argument("--actual-model",default=""); p.add_argument("--fallback-reason",default="")
        if name=="complete": p.add_argument("--log",default=""); p.add_argument("--artifact",default=""); p.add_argument("--result-message",default="")
        if name=="fail": p.add_argument("--failure-class",required=True); p.add_argument("--reason",required=True); p.add_argument("--retryable",action="store_true")
        if name=="release": p.add_argument("--reason",default="released")
    ort=obs.add_parser("retry",help="仅将 retryable failed 按变化依据重新排队"); ort.add_argument("dispatch_id"); ort.add_argument("--reason",required=True); ort.add_argument("--evidence",required=True)
    ore=obs.add_parser("reconcile",help="幂等修复缺失 dispatch 并报告历史异常"); ore.add_argument("--experiment-id",default=""); ore.add_argument("--dry-run",action="store_true")
    mr=sub.add_parser("managed-run",help="bubblewrap+tmux managed execution consumer"); mrs=mr.add_subparsers(dest="action",required=True)
    mprep=mrs.add_parser("prepare"); mprep.add_argument("run_id"); mprep.add_argument("--consumer",required=True); mprep.add_argument("--runtime-command",required=True); mprep.add_argument("--trial-manifest-json",default="")
    mtp=mrs.add_parser("trial-plan",help="read or validate a structured Trial manifest without execution"); mtp.add_argument("run_id"); mtp.add_argument("--trial-manifest-json",default="")
    mtc=mrs.add_parser("trial-campaign",help="create a parameter campaign under an existing Run"); mtc.add_argument("run_id"); mtc.add_argument("--request",required=True); mtc.add_argument("--trial-manifest-json",required=True); mtc.add_argument("--concurrency",type=int,default=1); mtc.add_argument("--max-retries",type=int,default=1); mtc.add_argument("--consumer",required=True)
    for name in ("preflight","start","status","complete","fail","repair","reattach"):
        mp=mrs.add_parser(name); mp.add_argument("dispatch_id"); mp.add_argument("--consumer",required=True)
        if name!="reattach": mp.add_argument("--lease-token",required=True)
        if name=="status": mp.add_argument("--heartbeat",action="store_true")
        if name=="fail": mp.add_argument("--failure-class",required=True); mp.add_argument("--reason",required=True); mp.add_argument("--retryable",action="store_true")
        if name=="repair": mp.add_argument("--failure-class",required=True); mp.add_argument("--reason",required=True)
    ag=sub.add_parser("agent",help="查询人类配置的 Agent 路由"); ags=ag.add_subparsers(dest="action",required=True); ags.add_parser("routing",help="只读输出 local_tool_edit 与 experiment_code_edit 路由")
    are=ags.add_parser("route-event"); are.add_argument("--route",required=True); are.add_argument("--subject",default="requested",choices=["requested","actual"]); are.add_argument("--requested-agent",default=""); are.add_argument("--requested-model",default=""); are.add_argument("--actual-agent",default=""); are.add_argument("--actual-model",default=""); are.add_argument("--fallback-reason",default=""); are.add_argument("--result",required=True,choices=["success","unsupported","unavailable","quota","error"]); are.add_argument("--error-code",default=""); are.add_argument("--message",default=""); are.add_argument("--run-id",default="")
    gt=sub.add_parser("governance-task"); gts=gt.add_subparsers(dest="action",required=True); gts.add_parser("list"); gpmt=gts.add_parser("prompt"); gpmt.add_argument("task_id"); gc=gts.add_parser("claim-next"); gc.add_argument("--consumer",required=True)
    for name in ("complete","fail"):
        gp=gts.add_parser(name); gp.add_argument("task_id"); gp.add_argument("--lease-token",required=True); gp.add_argument("--consumer",required=True); gp.add_argument("--reason",required=True)
        if name=="complete": gp.add_argument("--group-id",default="")
    xp=sub.add_parser("exploration",help="Research Explorer canonical 桥接"); xps=xp.add_subparsers(dest="action",required=True)
    xi=xps.add_parser("inspect-target"); xi.add_argument("--target-type",required=True,choices=["experiment","idea","question","comparison"]); xi.add_argument("--target-id",required=True)
    xn=xps.add_parser("init"); xn.add_argument("--target-type",required=True,choices=["experiment","idea","question","comparison"]); xn.add_argument("--target-id",required=True); xn.add_argument("--exploration-id",required=True); xn.add_argument("--budget-json",required=True)
    xc=xps.add_parser("context"); xc.add_argument("id")
    xr=xps.add_parser("record-round"); xr.add_argument("id"); xr.add_argument("--round",required=True,type=int); xr.add_argument("--payload-file",required=True)
    xt=xps.add_parser("transition"); xt.add_argument("id"); xt.add_argument("--status",required=True,choices=sorted(server.EXPLORATION_STATUSES)); xt.add_argument("--reason",default=""); xt.add_argument("--expected-status",default="")
    xf=xps.add_parser("finalize"); xf.add_argument("id"); xf.add_argument("--proposal-file",required=True); xf.add_argument("--final-report-file",required=True)
    a=ap.parse_args(); root=root_for(a.project); d=data(root)
    if a.object=="managed-run":
        from survey_tool.managed_execution import managed_execution_complete,managed_execution_fail,managed_execution_preflight,managed_execution_repair,managed_execution_start,managed_execution_status
        try:
            if a.action=="prepare": result=server.prepare_managed_run_command(root,a.run_id,a.runtime_command,a.consumer,a.trial_manifest_json or None)
            elif a.action=="trial-plan": result=server.run_trial_plan_status(root,a.run_id,json_arg(a.trial_manifest_json,"--trial-manifest-json") if a.trial_manifest_json else None)
            elif a.action=="trial-campaign": result=server.prepare_run_trial_campaign_for_steward(root,a.run_id,a.request,json_arg(a.trial_manifest_json,"--trial-manifest-json"),a.concurrency,a.max_retries,a.consumer)
            elif a.action=="reattach": result=server.reattach_managed_execution(root,a.dispatch_id,a.consumer)
            elif a.action=="preflight": result=managed_execution_preflight(root,a.dispatch_id,a.lease_token,a.consumer)
            elif a.action=="start": result=managed_execution_start(root,a.dispatch_id,a.lease_token,a.consumer)
            elif a.action=="status": result=managed_execution_status(root,a.dispatch_id,a.lease_token,a.consumer,heartbeat=a.heartbeat)
            elif a.action=="complete": result=managed_execution_complete(root,a.dispatch_id,a.lease_token,a.consumer)
            elif a.action=="repair": result=managed_execution_repair(root,a.dispatch_id,a.lease_token,a.consumer,a.failure_class,a.reason)
            else: result=managed_execution_fail(root,a.dispatch_id,a.lease_token,a.consumer,a.failure_class,a.reason,a.retryable)
            return emit(result)
        except (ValueError,OSError,subprocess.SubprocessError) as e: raise SystemExit(str(e))
    if a.object=="code":
        from survey_tool.code_workflow import prepare_code, publish_code, deploy_code
        try:
            if a.action=="prepare": return emit(prepare_code(root,a.workspace_id))
            if a.action=="publish": return emit(publish_code(root,a.workspace_id,a.commit))
            return emit(deploy_code(root,a.workspace_id,a.commit,a.confirmation))
        except (ValueError,OSError,subprocess.SubprocessError) as e: raise SystemExit(str(e))
    if a.object=="exploration":
        try:
            if a.action=="inspect-target": return emit(server.exploration_inspect_target(root,a.target_type,a.target_id))
            if a.action=="init": return emit(server.exploration_init(root,a.target_type,a.target_id,a.exploration_id,json_arg(a.budget_json,"--budget-json")))
            if a.action=="context": return emit(server.exploration_context(root,a.id))
            if a.action=="record-round": return emit(server.exploration_record_round(root,a.id,a.round,json.loads(pathlib.Path(a.payload_file).read_text(encoding="utf-8"))))
            if a.action=="transition": return emit(server.exploration_transition(root,a.id,a.status,a.reason,a.expected_status))
            if a.action=="finalize": return emit(server.exploration_finalize(root,a.id,pathlib.Path(a.final_report_file).read_text(encoding="utf-8"),json.loads(pathlib.Path(a.proposal_file).read_text(encoding="utf-8"))))
        except (ValueError,OSError,json.JSONDecodeError) as e: raise SystemExit(str(e))
    if a.object=="outbox":
        if a.action=="list": return emit(server.execution_outbox_public(root)["execution_outbox"])
        if a.action=="status":
            item=next((x for x in server.execution_outbox_public(root)["execution_outbox"]["items"] if x.get("dispatch_id")==a.dispatch_id),None)
            if not item: raise SystemExit("dispatch 不存在")
            return emit(item)
        if a.action=="enqueue": return emit(server.enqueue_execution(root,a.run_id,"cli"))
        if a.action=="claim-next": return emit(server.claim_next_execution(root,a.consumer,a.experiment_id,a.run_id))
        if a.action=="retry": return emit(server.retry_execution(root,a.dispatch_id,a.reason,a.evidence))
        if a.action=="reconcile": return emit(server.reconcile_execution_outbox(root,a.experiment_id,a.dry_run))
        if a.action=="ack": return emit(server._leased_transition(root,a.dispatch_id,a.lease_token,a.consumer,"acknowledge",{"actual_agent":a.actual_agent,"actual_model":a.actual_model,"fallback_reason":a.fallback_reason}))
        if a.action=="running": return emit(server._leased_transition(root,a.dispatch_id,a.lease_token,a.consumer,"running"))
        if a.action=="complete": return emit(server._leased_transition(root,a.dispatch_id,a.lease_token,a.consumer,"complete",{"log":a.log,"artifact":a.artifact,"result_message":a.result_message}))
        if a.action=="fail": return emit(server._leased_transition(root,a.dispatch_id,a.lease_token,a.consumer,"fail",{"failure_class":a.failure_class,"reason":a.reason,"retryable":a.retryable}))
        if a.action=="release": return emit(server.release_execution(root,a.dispatch_id,a.lease_token,a.consumer,a.reason))
    if a.object=="agent":
        if a.action=="routing": return emit(server.agent_routing_policy(root))
        return emit(server.record_agent_route_event(root,{"route":a.route,"subject":a.subject,"requested_agent":a.requested_agent,"requested_model":a.requested_model,"actual_agent":a.actual_agent,"actual_model":a.actual_model,"fallback_reason":a.fallback_reason,"result":a.result,"error_code":a.error_code,"message":a.message,"run_id":a.run_id}))
    if a.object=="governance-task":
        if a.action=="list": return emit(server.governance_task_public(root))
        if a.action=="prompt": return emit(server.governance_task_prompt(root,a.task_id))
        if a.action=="claim-next": return emit(server.claim_governance_task(root,a.consumer))
        if a.action=="complete": return emit(server.complete_governance_task(root,a.task_id,a.lease_token,a.consumer,a.group_id,a.reason))
        return emit(server.fail_governance_task(root,a.task_id,a.lease_token,a.consumer,a.reason))
    if a.object=="experiment":
        if a.action=="create":
            fields={"title":a.title,"workspace_id":a.workspace_id,"objective":a.objective,"constraints":a.constraints,
                    "source_ref":a.source_ref,"evidence_refs":a.evidence_ref,"claim_refs":a.claim_ref,"kind":a.kind,
                    "agent_level":a.agent_level,"workflow_stage":"draft","created_by":"terminal_pi"}
            if a.run_groups_json: fields["run_groups"]=json_arg(a.run_groups_json,"--run-groups-json")
            if a.metric_definitions_json: fields["metric_definitions"]=json_arg(a.metric_definitions_json,"--metric-definitions-json")
            try: exp=server.create_experiment(root,fields,a.id)
            except ValueError as e: raise SystemExit(str(e))
            append_event(root,exp["id"],"experiment_created",f'Agent 创建实验初稿 {exp["id"]} · {exp["title"]}')
            return emit({"experiment":exp,"canonical":{"index":str(root/"shell"/"06_experiments"/exp["id"]/f'{exp["id"]}.md'),"brief":str(root/"shell"/"06_experiments"/exp["id"] / "brief.md"),"plan":str(root/"shell"/"06_experiments"/exp["id"] / "plan.md"),"mission":str(root/"shell"/"06_experiments"/exp["id"] / "mission.md")}})
        exp=find(d["experiments"],a.id); runs=[x for x in d["runs"] if x.get("experiment_id")==a.id]
        if a.action=="events":
            rows=[x for x in server.read_tool_json(root,"experiment-events.jsonl",[]) if x.get("experiment_id")==a.id]
            return emit(rows if a.full else [server._event_summary(x,i) for i,x in enumerate(rows)])
        if a.action=="event-detail":
            try: return emit(server.event_detail(root,a.event_id))
            except ValueError as e: raise SystemExit(str(e))
        if a.action=="compact-events": return emit(server.compact_event_log(root,a.id))
        if a.action=="docs":
            from survey_tool.experiment_docs import refresh_experiment_docs
            try: return emit(refresh_experiment_docs(root,a.id,a.dry_run))
            except (ValueError,OSError) as e: raise SystemExit(str(e))
        if a.action=="auto-review": return emit(server.auto_review_experiment(root,a.id))
        if a.action=="agent-grouping":
            if bool(a.proposal_json)==bool(a.file): raise SystemExit("必须且只能提供 --proposal-json 或 --file")
            try: proposal=json.loads(a.proposal_json) if a.proposal_json else json.loads(pathlib.Path(a.file).read_text(encoding="utf-8"))
            except (json.JSONDecodeError,OSError) as e: raise SystemExit(f"无法读取 grouping proposal：{e}")
            if not isinstance(proposal,dict) or (proposal.get("experiment_id") and proposal["experiment_id"]!=a.id): raise SystemExit("proposal 必须是匹配 Experiment 的对象")
            try: return emit(server.apply_agent_run_grouping(root,a.id,proposal.get("groups"),proposal.get("assignments")))
            except ValueError as e: raise SystemExit(str(e))
        if a.action=="governance":
            fields={}
            if a.run_groups_json is not None: fields["run_groups"]=json_arg(a.run_groups_json,"--run-groups-json")
            if a.metric_definitions_json is not None: fields["metric_definitions"]=json_arg(a.metric_definitions_json,"--metric-definitions-json")
            if not fields: raise SystemExit("至少提供 --run-groups-json 或 --metric-definitions-json")
            try: return emit(server.update_experiment(root,a.id,fields))
            except ValueError as e: raise SystemExit(str(e))
        if a.action=="handoff":
            payload=json.loads(pathlib.Path(a.file).read_text(encoding="utf-8"))
            if payload.get("contract")!="survey-tool.experiment-handoff/v1" or payload.get("experiment_id")!=a.id: raise SystemExit("invalid contract or experiment_id")
            exp=server.update_experiment(root,a.id,{"agent_handoff":payload,"workflow_stage":"awaiting_confirmation"})
            append_event(root,a.id,"handoff","Agent 已提交勘察结果与待确认表单")
            return emit(exp)
        return emit(server.experiment_constraints(root,a.id,getattr(a,"run","") or "",full=bool(getattr(a,"full",False))))
    if a.object=="event": return emit(append_event(root,a.experiment_id,a.type,a.message,a.run,a.details))
    if a.action=="auto-review": return emit(server.auto_review_run(root,a.id))
    if a.action=="create":
        fields={key:getattr(a,key) for key in ["variant","run_type","purpose","necessity","evidence_basis","implementation_summary","implementation_details","data_definition","data_scale","model_config","variables_controls","metric_definition","integrity_gates","expected_outcome","acceptance_criteria","dependencies","limitations","claim_boundary","audit_paths","status","workspace_id","git_commit","config","command","log_path","output_dir","artifact_dir","artifacts","tmux_session","seed"]}
        fields["group_id"]=a.group_id
        fields.update({"research_question":a.research_question,"purpose":a.purpose or fields.get("purpose",""),"method_plan":a.method_plan,"hypothesis":a.hypothesis,"metric_plan":a.metric_plan,"architecture_plan":a.architecture_plan,"implementation_details":a.implementation_details or fields.get("implementation_details","")})
        if a.implementation_ref: fields["implementation_ref"]=json_arg(a.implementation_ref,"--implementation-ref")
        if a.metric_observations: fields["metric_observations"]=json_arg(a.metric_observations,"--metric-observations")
        fields["created_by"]="terminal_pi"; fields["workflow_version"]=2
        try: run=server.create_run(root,a.experiment_id,fields,a.id)
        except ValueError as e: raise SystemExit(str(e))
        append_event(root,a.experiment_id,"run_created",f'Agent 创建 canonical Run {run["id"]} · {run["variant"]}',run["id"]); return emit(run)
    if a.action=="rekey":
        old=find(d["runs"],a.id); eid=old.get("experiment_id","")
        try: run=server.rekey_run(root,a.id,a.new_id,a.adopt_existing_note)
        except ValueError as e: raise SystemExit(str(e))
        append_event(root,eid,"run_rekey",f'Run registry 已从 {a.id} 迁移为 canonical ID {a.new_id}',a.new_id,details=f"legacy_registry_id={a.id}")
        return emit(run)
    if a.action=="submit-review":
        old=find(d["runs"],a.id)
        try: run=server.review_run(root,a.id,"submit",actor="terminal_pi")
        except ValueError as e: raise SystemExit(str(e))
        append_event(root,old["experiment_id"],"run_review_submitted",a.message,a.id)
        return emit(run)
    if a.action=="workflow":
        result_fields={}
        for key in ("result_analysis","limitations","artifacts"):
            value=getattr(a,key,None)
            if value is not None: result_fields[key]=value
        if a.key_results is not None: result_fields["key_results"]=json_arg(a.key_results,"--key-results")
        try: return emit(server.advance_run_workflow(root,a.id,a.workflow_action,actor="terminal_pi",result_fields=result_fields))
        except ValueError as e: raise SystemExit(str(e))
    run=find(d["runs"],a.id); fields={}
    for key in ["status","run_type","purpose","method_plan","necessity","evidence_basis","implementation_summary","implementation_details","data_definition","data_scale","model_config","variables_controls","metric_definition","integrity_gates","expected_outcome","acceptance_criteria","dependencies","result_summary","limitations","conclusion_scope","claim_boundary","audit_paths","command","config","log_path","output_dir","artifact_dir","artifacts","tmux_session","git_commit","metrics","notes","agent_review_summary","agent_review_questions"]:
        value=getattr(a,key.replace("-","_"),None)
        if value is not None: fields[key]=value
    for key in ("research_question","hypothesis","metric_plan","architecture_plan","result_analysis"):
        value=getattr(a,key,None)
        if value is not None: fields[key]=value
    if getattr(a,"implementation_ref",None) is not None: fields["implementation_ref"]=json_arg(a.implementation_ref,"--implementation-ref")
    if getattr(a,"key_results",None) is not None: fields["key_results"]=json_arg(a.key_results,"--key-results")
    if a.metric_observations is not None: fields["metric_observations"]=json_arg(a.metric_observations,"--metric-observations")
    try: run=server.update_run(root,a.id,fields)
    except ValueError as e: raise SystemExit(str(e))
    if a.message: append_event(root,run["experiment_id"],"run_update",a.message,run["id"])
    emit(run)
if __name__=="__main__": main()
