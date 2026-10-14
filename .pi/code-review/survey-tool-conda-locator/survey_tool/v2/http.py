"""HTTP dispatch for the Survey Tool v2 domain."""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import sqlite3
import sys
import urllib.parse

from survey_tool.v2 import V2Store

def _public_job(job):
    return {key:value for key,value in job.items() if key!="lease_token"}

def _public_pipeline(value):
    return {key:(_public_job(item) if key.endswith("_job") and isinstance(item,dict) else item) for key,item in value.items()}

_QUESTION_FIELDS={"title","question","current_judgement","investigation","status","papers","comparisons","findings","experiments"}
_QUESTION_STATUSES={"inbox","open","investigating","answered","blocked","archived"}
_QUESTION_LIST_FIELDS={"papers","comparisons","findings","experiments"}

def _validated_question_fields(value, *, creating=False):
    if not isinstance(value,dict): raise ValueError("question fields must be an object")
    unknown=set(value)-_QUESTION_FIELDS
    if unknown: raise ValueError("unsupported question fields: "+", ".join(sorted(unknown)))
    result={}
    for key,item in value.items():
        if key in _QUESTION_LIST_FIELDS:
            if not isinstance(item,list) or any(not isinstance(entry,str) or not entry.strip() or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}",entry.strip()) for entry in item): raise ValueError(f"{key} must be a list of safe object IDs")
            result[key]=list(dict.fromkeys(entry.strip() for entry in item))
        else:
            if not isinstance(item,str): raise ValueError(f"{key} must be a string")
            result[key]=item.strip() if key in {"title","status"} else item
    if "status" in result and result["status"] not in _QUESTION_STATUSES: raise ValueError("invalid question status")
    if creating and (not result.get("title") or not str(result.get("question") or "").strip()): raise ValueError("title and question are required")
    return result

def _question_target(root,target_id,deps):
    for row in deps["read_papers"](root):
        if str(row.get("citekey") or deps["citekey_for"](row))==target_id:
            path=deps["note_path"](root,target_id); return {"type":"paper","title":str(row.get("title") or target_id),"canonical_path":path.relative_to(root).as_posix() if path.is_relative_to(root) else "","field":"papers","relation_type":"discusses","authority":"question_frontmatter"}
    compares=deps["read_compares"](root)
    for comp in compares:
        if str(comp.get("id"))==target_id: return {"type":"comparison","title":str(comp.get("name") or target_id),"canonical_path":deps["_comparison_path"](root,target_id).relative_to(root).as_posix(),"field":"comparisons","relation_type":"discusses","authority":"question_frontmatter"}
        for finding in comp.get("findings",[]) or []:
            if str(finding.get("id"))==target_id: return {"type":"finding","title":str(finding.get("text") or target_id)[:200],"canonical_path":deps["_finding_path"](root,target_id).relative_to(root).as_posix(),"field":"findings","relation_type":"discusses","authority":"question_frontmatter"}
    for row in deps["experiment_data"](root).get("experiments",[]):
        if str(row.get("id"))==target_id: return {"type":"experiment","title":str(row.get("title") or target_id),"canonical_path":"","field":"experiments","relation_type":"tests","authority":"question_frontmatter"}
    for row in deps["read_ideas"](root):
        if str(row.get("id"))==target_id: return {"type":"idea","title":str(row.get("title") or target_id),"canonical_path":"shell/00_idea/idea.md","field":"","relation_type":"derived_from","authority":"v2_navigation_index"}
    for row in deps["read_claims"](root):
        if str(row.get("id"))==target_id: return {"type":"claim","title":str(row.get("text") or target_id)[:200],"canonical_path":"kernel/claims.md","field":"","relation_type":"discusses","authority":"v2_navigation_index"}
    raise KeyError("relation target not found or unsupported")

def _ensure_relation_object(store,root,object_id,object_type,title,canonical_path):
    try:
        current=store.get_object(object_id)
        if current["type"]!=object_type: raise ValueError("indexed target type conflict")
        return current
    except KeyError:
        project_id="PROJECT-"+hashlib.sha256(str(root).encode()).hexdigest()[:16]
        return store.create_object(object_id=object_id,object_type=object_type,project_id=project_id,title=title,lifecycle_status="reference",canonical_path=canonical_path,actor_kind="human",actor_id="web-v2")


def dispatch(method: str, path: str, body: dict | None, deps: dict) -> tuple[int, object] | None:
    """处理 /api/v2/* 路由。命中返回 (status, payload)，未命中返回 None。"""
    if not path.startswith("/api/v2/"):
        return None
    b = body or {}
    resolve_project=deps["resolve_project"]

    if method == "GET":
        if path == "/api/v2/health": return (200,deps["v2_capabilities"]())
        m = re.match(r"^/api/v2/p/([^/]+)/experiments/([^/]+)/documents(?:/(content))?$", path)
        if m:
            from survey_tool.experiment_document_api import ExperimentDirectoryError, list_documents, read_document
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=urllib.parse.unquote(m.group(2))
            params=urllib.parse.parse_qs(urllib.parse.urlparse(deps["request_path"]).query)
            def param(key,default=""): return (params.get(key) or [default])[0]
            try:
                if m.group(3): return (200,read_document(root,eid,param("path")))
                return (200,list_documents(root,eid,param("q"),param("directory"),param("kind","all"),param("sort","path"),param("status","all")))
            except ExperimentDirectoryError as exc: return (409,{"error":str(exc),"reason":"experiment_directory_unavailable","experiment_id":eid,"read_only":True})
            except (KeyError,FileNotFoundError) as exc: return (404,{"error":str(exc)})
            except ValueError as exc: return (400,{"error":str(exc)})
        m = re.match(r"^/api/v2/p/([^/]+)/papers/arxiv-search$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); params=urllib.parse.parse_qs(urllib.parse.urlparse(deps["request_path"]).query); query=(params.get("q") or [""])[0].strip()
            if not query or len(query)>500: return (400,{"error":"arXiv query must be nonempty and at most 500 characters","hits":[]})
            result=deps["arxiv_paper_search"](root,query,10)
            return (502 if result.get("error") and not result.get("hits") else 200,result)
        m = re.match(r"^/api/v2/p/([^/]+)/publish$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return (200,deps["read_publish"](root))
        m = re.match(r"^/api/v2/p/([^/]+)/agent-routing$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return (200,{"routing":deps["agent_routing_policy"](root),"authority":"project_tool_state","known_codex_models":["gpt-5.6-sol","gpt-5.6-terra","gpt-5.6-luna","gpt-5.5"],"applies_to":"future_dispatches_only"})
        m = re.match(r"^/api/v2/p/([^/]+)/environment-bindings$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); result=deps["environment_bindings"](root); intake=deps["read_intake"](root); publish=deps["read_publish"](root)
            result.update({"intake_repo_path":intake.get("repo_path","") or "none-yet","publish":{key:publish.get(key) for key in ("githubUrl","commitSha","publishedAt")},"binding_note":"Intake repo_path 是待研究源码；Workspace remote_repo 是 Experiment 远程执行仓库；Publish 是外部 AI 只读 snapshot，三者不会自动互相覆盖。"})
            return (200,result)
        m = re.match(r"^/api/v2/p/([^/]+)/stewards$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return (200,deps["list_steward_statuses"](root))
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/steward/console$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            try: return (200,deps["steward_console"](root,rid))
            except KeyError as exc: return (404,{"error":str(exc)})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/steward$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            try: return (200,deps["steward_status"](root,rid))
            except KeyError: return (404,{"error":"run not found"})
            except ValueError as e: return (400,{"error":str(e)})
        m = re.match(r"^/api/v2/p/([^/]+)/zotero/collections$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); result=deps["zotero_collections"](root)
            return (200 if result.get("ok") else 503,result)
        m = re.match(r"^/api/v2/p/([^/]+)/zotero/collections/(\d+)/items$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); result=deps["zotero_collection_items"](root,int(m.group(2)),recursive=True)
            if result.get("ok"): result={"ok":True,"items":[{key:item.get(key) for key in ("id","title","authors","date","venue","doi","has_pdf","already_in")} for item in result.get("items",[])]}
            return (200 if result.get("ok") else 503,result)
        m = re.match(r"^/api/v2/p/([^/]+)/capabilities$", path)
        if m:
            root = resolve_project(urllib.parse.unquote(m.group(1)))
            return (200,deps["v2_capabilities"](root))
        m = re.match(r"^/api/v2/p/([^/]+)/paper-candidates$", path)
        if m:
            root = resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            return (200,{"initialized":store.exists(),"candidates":store.list_paper_candidates() if store.exists() else []})
        m = re.match(r"^/api/v2/p/([^/]+)/objects$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (200,{"initialized":False,"objects":[],"relations":[],"summary":{}})
            objects=store.list_objects(); relations=store.list_relations()
            summary: dict[str,int] = {}
            for item in objects: summary[item["type"]] = summary.get(item["type"],0)+1
            return (200,{"initialized":True,"objects":objects,"relations":relations,"summary":summary})
        m = re.match(r"^/api/v2/p/([^/]+)/objects/archive$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (200,{"initialized":False,"objects":[]})
            objects=store.list_objects(); native=[item for item in objects if item["type"] in {"paper_candidate","automation"}]
            impacts={item["id"]:item for item in store.archive_impact([item["id"] for item in native])} if native else {}
            return (200,{"initialized":True,"objects":[{**item,"impact":impacts[item["id"]]} for item in native],"hard_delete_available":False})
        m = re.match(r"^/api/v2/p/([^/]+)/automations$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            automations=store.list_automations() if store.exists() else []
            events=store.list_events() if store.exists() else []
            event_map={item["id"]:[] for item in automations}
            for event in events:
                if event.get("object_id") in event_map: event_map[event["object_id"]].append(event)
            for item in automations: item["events"]=event_map[item["id"]]
            return (200,{"initialized":store.exists(),"automations":automations})
        m = re.match(r"^/api/v2/p/([^/]+)/herdr-launch-requests$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (200,{"initialized":False,"launch_requests":[]})
            requests=[deps["public_herdr_launch_request"](item) for item in store.list_herdr_launch_requests()]; events=store.list_events()
            event_map={item["id"]:[] for item in requests}
            for event in events:
                if event.get("object_id") in event_map: event_map[event["object_id"]].append(event)
            for item in requests: item["events"]=event_map[item["id"]]
            return (200,{"initialized":True,"launch_requests":requests,"execution_available":False})
        m = re.match(r"^/api/v2/p/([^/]+)/herdr-executions$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (200,{"initialized":False,"executions":[]})
            executions=[deps["public_herdr_execution"](item) for item in store.list_herdr_executions()]; events=store.list_events()
            event_map={item["id"]:[] for item in executions}
            for event in events:
                if event.get("object_id") in event_map: event_map[event["object_id"]].append(deps["public_herdr_execution_event"](event))
            for item in executions: item["events"]=event_map[item["id"]]
            return (200,{"initialized":True,"executions":executions,"execution_started":False})
        m = re.match(r"^/api/v2/p/([^/]+)/agent-sessions$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            return (200,{"initialized":store.exists(),"sessions":[deps["public_agent_session"](item) for item in store.list_agent_sessions()] if store.exists() else [],"current_pi":deps["current_pi_binding_summary"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/migration/dry-run$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            result=deps["build_migration_inventory"](root); result["identity_index_plan"]=deps["build_identity_index_plan"](root); result["identity_index_history"]=deps["identity_index_history"](root); result["content_index_plan"]=deps["build_content_index_plan"](root); result["content_index_history"]=deps["content_index_history"](root)
            return (200,result)
        m = re.match(r"^/api/v2/p/([^/]+)/jobs$", path)
        if m:
            root = resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (200,{"initialized":False,"jobs":[]})
            params=urllib.parse.parse_qs(urllib.parse.urlparse(deps["request_path"]).query)
            return (200,{"initialized":True,"jobs":[_public_job(job) for job in store.list_jobs(status=(params.get("status") or [""])[0],target_object_id=(params.get("target_object_id") or [""])[0])]})

    if method == "POST":
        m = re.match(r"^/api/v2/p/([^/]+)/experiments/([^/]+)/documents/refresh$", path)
        if m:
            from survey_tool.experiment_docs import refresh_experiment_docs
            from survey_tool.experiment_document_api import ExperimentDirectoryError
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=urllib.parse.unquote(m.group(2))
            if set(b)-{"confirmation"} or b.get("confirmation")!=f"REFRESH EXPERIMENT DOCUMENTS {eid}":
                return (400,{"error":"需要确认只刷新该 Experiment 的文档导航与结果页"})
            if not any(row.get("id")==eid for row in deps["experiment_data"](root)["experiments"]): return (404,{"error":"Experiment 不存在"})
            try: return (200,refresh_experiment_docs(root,eid))
            except ExperimentDirectoryError as exc: return (409,{"error":str(exc),"reason":"experiment_directory_unavailable","experiment_id":eid})
            except ValueError as exc: return (400,{"error":str(exc)})
        m = re.match(r"^/api/v2/p/([^/]+)/rule-drafts/external-prompt$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); draft=b.get("draft",b.get("workspace"))
            if set(b)-{"request","draft","workspace"} or ("draft" in b and "workspace" in b): return (400,{"error":"invalid external rule prompt payload"})
            try: return (200,{"prompt":deps["workspace_external_prompt"](b.get("request"),draft),"read_only":True,"contract":"survey-tool.workspace-rule-external/v1"})
            except ValueError as e: return (400,{"error":str(e)})
        m = re.match(r"^/api/v2/p/([^/]+)/rule-drafts/external-preview$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); draft=b.get("draft",b.get("workspace"))
            if set(b)-{"request","preset","draft","workspace","response"} or ("draft" in b and "workspace" in b): return (400,{"error":"invalid external rule preview payload"})
            context={"available_server_ids":[item.get("id") for item in deps["experiment_data"](root)["servers"]]}
            try: return (200,deps["external_intent_preview"](b.get("request"),b.get("preset"),draft,b.get("response"),context))
            except ValueError as e: return (400,{"error":str(e)})
        m = re.match(r"^/api/v2/p/([^/]+)/rule-drafts/preview$", path)
        if m:
            resolve_project(urllib.parse.unquote(m.group(1)))
            unknown=set(b)-{"scope","preset","request","draft","workspace","organizer"}
            if unknown: return (400,{"error":"payload contains unsupported fields: "+", ".join(sorted(unknown))})
            if "draft" in b and "workspace" in b: return (400,{"error":"provide draft only"})
            root=resolve_project(urllib.parse.unquote(m.group(1))); draft=b.get("draft",b.get("workspace"))
            context={"available_server_ids":[item.get("id") for item in deps["experiment_data"](root)["servers"]]}
            organizer=str(b.get("organizer") or "basic"); bridge=deps["bridge_for"](root) if organizer=="ai_auto" else None
            try: return (200,deps["organize_rule_draft"](b.get("scope"),b.get("request"),b.get("preset"),draft,context,organizer,bridge,90))
            except ValueError as e: return (400,{"error":str(e)})
        m = re.match(r"^/api/v2/p/([^/]+)/experiments/(E-\d+)/handoff/confirm$", path)
        if m:
            from survey_tool.experiments import confirm_experiment_handoff
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=m.group(2)
            if b.get("confirmation")!="CONFIRM EXPERIMENT HANDOFF": return (400,{"error":"confirmation phrase mismatch"})
            try: exp=confirm_experiment_handoff(root,eid,b.get("expected_updated"),b.get("expected_handoff"),b.get("proposal"),b.get("answers"))
            except RuntimeError as e: return (409,{"error":str(e),"reason":"registry_version_conflict"})
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{"experiment":exp,"dashboard":deps["experiment_dashboard_data"](root),"execution_started":False})
        m = re.match(r"^/api/v2/p/([^/]+)/zotero/items/(\d+)/(?:stage|preview-stage)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); key=m.group(2); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            if b.get("confirmation") != "STAGE ZOTERO PAPER CANDIDATE": return (400,{"error":"confirmation phrase mismatch"})
            library=deps["zotero_collection_items"](root,0,item_id=int(key))
            if not library.get("ok"): return (503,{"error":library.get("error") or "Zotero unavailable"})
            item=next((row for row in library.get("items",[]) if int(row.get("id") or -1)==int(key)),None)
            if not item: return (404,{"error":"Zotero item not found"})
            if item.get("already_in"): return (409,{"error":"该论文已在项目论文库中，无需重复添加"})
            source_url=f"https://www.zotero.org/items/{int(key)}"; year=(re.search(r"(?:19|20)\d{2}",str(item.get("date") or "")) or [""])[0]
            try: row=store.create_paper_candidate(object_id=f"PC-{secrets.token_hex(8)}",project_id=f"PROJECT-{hashlib.sha256(str(root).encode()).hexdigest()[:16]}",citekey=deps["citekey_for"]({"title":item.get("title","") ,"date":year}),title=str(item.get("title") or key),source_url=source_url,authors=list(item.get("authors") or []),year=year,doi=str(item.get("doi") or ""),oa_url="",source="zotero-local",recommendation_reason="由用户从 Zotero 本地库显式登记；PDF 尚未写入 canonical",actor_kind="human",actor_id="web-v2")
            except (ValueError,sqlite3.IntegrityError) as e: return (400,{"error":str(e)})
            public_candidate={key:value for key,value in row.items() if key not in {"canonical_path","canonical_paper_path"}}
            return (201,{"candidate":public_candidate,"preview":{k:item.get(k) for k in ("id","title","authors","date","venue","doi","has_pdf","already_in")},"canonical_write":False,"local_path_exposed":False})
        m = re.match(r"^/api/v2/p/([^/]+)/publish/sync$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "SYNC V2 PROJECT TO GITHUB": return (400,{"error":"confirmation phrase mismatch"})
            pub=deps["read_publish"](root); setup=b.get("setup") or {}
            if not isinstance(setup,dict): return (400,{"error":"setup must be an object"})
            repo_name=str(setup.get("repo_name") or "").strip(); visibility=str(setup.get("visibility") or "private")
            if not pub.get("githubUrl") and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}",repo_name): return (400,{"error":"repo_name must be a safe GitHub repository name"})
            if visibility not in {"private","public"}: return (400,{"error":"visibility must be private or public"})
            option_types={"include_pdfs","include_mineru","include_tool_state"}
            if any(key in setup and not isinstance(setup[key],bool) for key in option_types): return (400,{"error":"publish include options must be boolean"})
            opts={"includePdfs":True if pub.get("githubUrl") else setup.get("include_pdfs",True),"includeMinerU":True if pub.get("githubUrl") else setup.get("include_mineru",True),"includeToolState":True if pub.get("githubUrl") else setup.get("include_tool_state",True),"initGit":True,"pushGithub":True,"repoName":pub.get("name") or repo_name,"visibility":visibility if not pub.get("githubUrl") else "private"}
            try: result=deps["export_repo"](root,deps["publish_path"](root),opts)
            except Exception as e: return (502,{"error":str(e)[:300],"publish":deps["read_publish"](root)})
            result={key:value for key,value in result.items() if "token" not in key.lower()}
            result["publish"]=deps["read_publish"](root)
            status=200 if result.get("ok") and not result.get("pushSkipped") else 502
            return (status,result)
        m = re.match(r"^/api/v2/p/([^/]+)/experiments/(E-\d+)/run-grouping/ai-prompt-preview$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=m.group(2)
            try: preview=deps["ai_run_grouping_prompt"](root,eid)
            except ValueError as e: return (404, {"error":str(e)})
            bridge=deps["bridge_for"](root); live=bool(bridge.proc and bridge.proc.poll() is None)
            return (200,{**preview,"bridge":{"live_bound":live,"isStreaming":bridge.is_streaming if live else False}})
        m = re.match(r"^/api/v2/p/([^/]+)/ai/discussion-prompt-preview$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); target_type=str(b.get("target_type") or ""); target_id=str(b.get("target_id") or "").strip(); mode=str(b.get("mode") or ""); task=str(b.get("task") or "question"); request=b.get("request",""); focus_name=str(b.get("focus") or "whole"); reference_ids=b.get("reference_ids") or []; discussion_summary=b.get("discussion_summary") or ""; code_repository_id=str(b.get("code_repository_id") or "").strip()
            if target_type not in {"experiment","run","question","paper","paper_candidate"} or not target_id: return (400,{"error":"invalid discussion target"})
            if not isinstance(request,str) or len(request.encode("utf-8"))>256*1024: return (400,{"error":"request must be a string no larger than 256KB"})
            if focus_name not in {"whole","seven","method","evidence","limitations","relevance","question","original","judgement","investigation","relations"}: return (400,{"error":"unsupported discussion focus"})
            if task not in {"question","review","counter","compare","rewrite","experiment","code_edit","run_implementation"}: return (400,{"error":"unsupported discussion task"})
            if task=="code_edit" and (mode!="terminal_pi" or target_type not in {"experiment","run"}): return (400,{"error":"code_edit is available only for local Pi on Experiment/Run"})
            if task=="run_implementation" and (mode!="terminal_pi" or target_type!="run"): return (400,{"error":"run_implementation is available only for local Pi on a Run"})
            if not isinstance(reference_ids,list) or not isinstance(discussion_summary,str): return (400,{"error":"invalid discussion context"})
            data=deps["experiment_data"](root) if target_type in {"experiment","run"} else {"experiments":[],"runs":[]}; exp=next((item for item in data["experiments"] if item.get("id")==target_id),None) if target_type=="experiment" else None; run=next((item for item in data["runs"] if item.get("id")==target_id),None) if target_type=="run" else None
            if target_type=="experiment" and not exp: return (404,{"error":"experiment not found"})
            if target_type=="run":
                if not run: return (404,{"error":"run not found"})
                exp=next((item for item in data["experiments"] if item.get("id")==run.get("experiment_id")),None)
                if not exp: return (400,{"error":"run does not belong to an existing experiment"})
            if target_type=="paper":
                if not re.fullmatch(r"[A-Za-z0-9._-]+",target_id) or ".." in target_id: return (400,{"error":"invalid paper citekey"})
                if not any(str(item.get("citekey") or deps["citekey_for"](item))==target_id for item in deps["read_papers"](root)): return (404,{"error":"paper not found"})
            if target_type=="question":
                if not re.fullmatch(r"Q-\d+",target_id): return (400,{"error":"invalid question id"})
                if not any(item.get("id")==target_id for item in deps["read_questions"](root)): return (404,{"error":"question not found"})
            if target_type=="paper_candidate":
                if not re.fullmatch(r"PC-[A-Za-z0-9_-]+",target_id): return (400,{"error":"invalid paper candidate id"})
                store=V2Store(root)
                if not store.exists(): return (404,{"error":"paper candidate not found"})
                try: store.get_paper_candidate(target_id)
                except KeyError: return (404,{"error":"paper candidate not found"})
            if mode=="terminal_pi":
                try: preview=deps["ai_discussion_prompt"](root,target_type,target_id,request,task,focus_name,reference_ids,discussion_summary) if target_type in {"experiment","run"} else deps["research_object_discussion_prompt"](root,target_type,target_id,task,request,focus_name)
                except KeyError as e: return (404,{"error":str(e).strip("'")})
                except ValueError as e: return (400,{"error":str(e)})
                live_bridge=deps["bridge_for"](root); live=bool(live_bridge.proc and live_bridge.proc.poll() is None); persisted=bool(deps["read_pi_binding"](root)); bridge={"bound":live,"live_bound":live,"persisted_bound":persisted,"isStreaming":bool(live_bridge.is_streaming) if live else False}
                return (200,{**preview,"bridge":bridge})
            if mode=="external_gpt":
                if target_type=="paper_candidate": return (409,{"error":"候选论文尚未发布；请先核验、纳入 canonical 并同步 GitHub snapshot","reason":"candidate_not_published"})
                code_repository=None
                if code_repository_id:
                    if target_type not in {"experiment","run"} or not exp: return (400,{"error":"代码仓库引用只适用于 Experiment 或 Run"})
                    expected_id=str(exp.get("code_repository_workspace_id") or exp.get("workspace_id") or "")
                    if code_repository_id not in {"associated",expected_id}: return (400,{"error":"只能引用当前 Experiment 关联的代码仓库"})
                    workspace=next((item for item in data["workspaces"] if item.get("id")==expected_id),None)
                    if not workspace: return (409,{"error":"Experiment 关联的代码仓库 Workspace 不存在","reason":"code_repository_missing"})
                    code_repository={"workspace_id":expected_id,"url":workspace.get("external_code_url","") ,"ref":workspace.get("external_code_ref","")}
                    result=deps["gpt_assistant_instruction"](root,[f"{target_type}:{target_id}"],task,request,{"address":f"{target_type}:{target_id}"},code_repository)
                    if not result.get("ok"): return (409,{**result,"reason":"code_repository_not_ready"})
                    return (200,{**result,"prompt":result.get("instruction",""),"read_only":True})
                pub=deps["read_publish"](root)
                if not pub.get("githubUrl"): return (409,{"error":"项目尚未绑定 GitHub 仓库","reason":"publish_required","publish":pub})
                address=f"{target_type}:{target_id}"
                if target_type=="experiment" and task=="experiment": focus={"address":address,"index":"document:plan","label":"Plan · 实验方案","locator":f"只读取 shell/06_experiments/{target_id}/plan.md；只使用固定 commit 中的内容"}
                elif target_type=="run" and task in {"review","counter"}: focus={"address":address,"index":"field:result","label":"Result 与 Metrics","locator":"只定位 Result summary、Metrics 和 conclusion boundary；只使用固定 commit 中的内容"}
                elif target_type=="paper":
                    indexes={"whole":"whole","seven":"seven:all","method":"field:method","evidence":"field:evidence","limitations":"field:limitations","relevance":"field:relevance"}; labels={"whole":"整篇论文","seven":"七问","method":"方法","evidence":"证据","limitations":"局限","relevance":"与当前研究关系"}
                    focus={"address":address,"index":indexes[focus_name],"label":labels[focus_name],"locator":f"只读取固定 commit 中 paper:{target_id} 的 canonical note/MinerU；引用使用 [[{target_id}]] §小节"}
                elif target_type=="question":
                    indexes={"whole":"whole","question":"whole","original":"field:question","judgement":"field:current_judgement","investigation":"field:investigation","relations":"field:relations"}; labels={"whole":"整个 Question","question":"整个 Question","original":"原始疑问","judgement":"当前判断","investigation":"深究记录","relations":"关联对象"}
                    if focus_name not in indexes: return (400,{"error":"unsupported Question focus"})
                    focus={"address":address,"index":indexes[focus_name],"label":labels[focus_name],"locator":f"只读取固定 commit 中 question:{target_id} 的 canonical Markdown 对应字段"}
                else: focus={"address":address,"index":"whole","label":"整个 Experiment" if target_type=="experiment" else "整个 Run","locator":"阅读该对象的 canonical Markdown；只使用固定 commit 中的内容"}
                addresses=[address]
                if target_type=="question" and focus_name=="relations": addresses.extend(deps["linked_context_addresses"](root,target_type,target_id))
                result=deps["gpt_assistant_instruction"](root,list(dict.fromkeys(addresses)),task,request,focus)
                if not result.get("ok"): return (400,result)
                return (200,{**result,"prompt":result.get("instruction",""),"read_only":True})
            return (400,{"error":"mode must be terminal_pi or external_gpt"})
        m = re.match(r"^/api/v2/p/([^/]+)/experiments/(E-\d+)/archive$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=m.group(2); restore=b.get("restore") is True
            expected=f"RESTORE V2 EXPERIMENT {eid}" if restore else f"ARCHIVE V2 EXPERIMENT {eid}"
            if b.get("confirmation")!=expected: return (400,{"error":"confirmation phrase mismatch"})
            try: updated=deps["archive_experiment"](root,eid,b.get("expected_updated",""),b.get("reason",""),"human:web-v2",restore)
            except RuntimeError as e:
                if str(e)=="registry_version_conflict": return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
                if str(e).startswith("active_execution"): return (409,{"error":"Experiment 仍有活动 execution，需先结束或失败该 attempt","reason":"active_execution"})
                return (409,{"error":str(e)})
            except ValueError as e: return (404 if "不存在" in str(e) else 400,{"error":str(e)})
            return (200,{"experiment":updated,"dashboard":deps["experiment_dashboard_data"](root),"archived":bool(updated.get("archived_at")),"authority":"legacy_json_markdown"})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/archive$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2)); restore=b.get("restore") is True
            expected=f"RESTORE V2 RUN {rid}" if restore else f"ARCHIVE V2 RUN {rid}"
            if b.get("confirmation")!=expected: return (400,{"error":"confirmation phrase mismatch"})
            try: updated=deps["archive_run"](root,rid,b.get("expected_updated",""),b.get("reason",""),"human:web-v2",restore)
            except RuntimeError as e:
                if str(e)=="registry_version_conflict": return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
                if str(e)=="active_execution": return (409,{"error":"Run 仍有活动 execution，需先结束或失败该 attempt","reason":"active_execution"})
                return (409,{"error":str(e)})
            except ValueError as e: return (404 if "不存在" in str(e) else 400,{"error":str(e)})
            return (200,{"run":updated,"dashboard":deps["experiment_dashboard_data"](root),"archived":bool(updated.get("archived_at")),"authority":"legacy_json_markdown"})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/evidence-label$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2)); label=str(b.get("label") or "")
            if b.get("confirmation")!=f"SET V2 RUN EVIDENCE LABEL {rid}": return (400,{"error":"confirmation phrase mismatch"})
            try: updated=deps["set_run_evidence_label"](root,rid,b.get("expected_updated",""),label,b.get("note",""),"human:web-v2")
            except RuntimeError as e:
                if str(e)=="registry_version_conflict": return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
                return (409,{"error":str(e)})
            except ValueError as e: return (404 if "不存在" in str(e) else 400,{"error":str(e)})
            return (200,{"run":updated,"dashboard":deps["experiment_dashboard_data"](root),"evidence_label":updated.get("evidence_label",""),"authority":"legacy_json_markdown","claim_verdict_changed":False})
        m = re.match(r"^/api/v2/p/([^/]+)/experiments$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "CREATE V2 EXPERIMENT": return (400,{"error":"confirmation phrase mismatch"})
            if not isinstance(b.get("experiment"),dict): return (400,{"error":"experiment must be an object"})
            try: created=deps["create_experiment"](root,b["experiment"])
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{"experiment":created,"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/experiments/(E-\d+)/runs$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=m.group(2)
            if b.get("confirmation") != "CREATE V2 RUN": return (400,{"error":"confirmation phrase mismatch"})
            if not isinstance(b.get("run"),dict): return (400,{"error":"run must be an object"})
            spec=dict(b["run"]); rid=str(spec.pop("id","")).strip(); spec["workflow_version"]=2
            try: created=deps["create_run"](root,eid,spec,rid)
            except ValueError as e: return (404 if "Experiment 不存在" in str(e) else 400,{"error":str(e)})
            return (200,{"run":created,"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/trials/prepare-steward$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "PREPARE V2 RUN TRIALS": return (400,{"error":"confirmation phrase mismatch"})
            try:
                prepared=deps["prepare_run_trials_for_steward"](root,rid,b.get("expected_updated",""),b.get("request",""),b.get("axes"),b.get("concurrency",1),b.get("max_retries",1),"human:web-v2",b.get("planning_mode","matrix"),b.get("trial_budget"))
                handoff=deps["prepare_steward_handoff"](root,rid,prepared["run"].get("updated",""))
            except RuntimeError as e:
                if str(e)=="registry_version_conflict": return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
                return (409,{"error":str(e)})
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{**handoff,**prepared,"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/review$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2)); action=str(b.get("action") or "")
            confirmations={"submit":"SUBMIT V2 RUN REVIEW","request_changes":"REQUEST V2 RUN CHANGES","approve":"APPROVE V2 RUN","authorize_execution":"AUTHORIZE V2 RUN EXECUTION"}
            if action not in confirmations: return (400,{"error":"unsupported review action"})
            if b.get("confirmation") != confirmations[action]: return (400,{"error":"confirmation phrase mismatch"})
            current=next((item for item in deps["experiment_data"](root)["runs"] if item.get("id")==rid),None)
            if not current: return (404,{"error":"run not found"})
            if str(b.get("expected_updated") or "") != str(current.get("updated") or ""): return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
            if action=="authorize_execution" and (deps["run_review_status"](current)!="approved" or current.get("workflow_stage")!="ready_to_run"):
                try: direct=deps["prepare_direct_steward_run"](root,rid,current.get("updated", ""),"human:web-v2")
                except RuntimeError: return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
                except ValueError as e: return (400,{"error":str(e)})
                dashboard=deps["experiment_dashboard_data"](root); updated=next(item for item in dashboard["runs"] if item.get("id")==rid)
                return (200,{"run":updated,"dashboard":dashboard,"dispatch":direct["dispatch"],"direct_steward":True})
            try: deps["review_run"](root,rid,action,b.get("requirements",""),b.get("questions",""),"human:web-v2",b.get("authorization_note",""))
            except ValueError as e: return (400,{"error":str(e)})
            dashboard=deps["experiment_dashboard_data"](root)
            updated=next(item for item in dashboard["runs"] if item.get("id")==rid)
            return (200,{"run":updated,"dashboard":dashboard})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/steward/start$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "PREPARE V2 RUN STEWARD": return (400,{"error":"confirmation phrase mismatch"})
            try: result=deps["prepare_steward_handoff"](root,rid,b.get("expected_updated",""))
            except KeyError: return (404,{"error":"run not found"})
            except RuntimeError as e:
                if str(e)=="registry_version_conflict": return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
                return (409,{"error":str(e)})
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{**result,"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/steward/restart$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "RESTART V2 FAILED RUN": return (400,{"error":"confirmation phrase mismatch"})
            try:
                restarted=deps["restart_failed_run_execution"](root,rid,b.get("expected_updated",""),"human:web-v2",str(b.get("execution_mode") or "single"))
                result=deps["prepare_steward_handoff"](root,rid,restarted["run"].get("updated",""))
            except KeyError: return (404,{"error":"run not found"})
            except RuntimeError as e:
                if str(e)=="registry_version_conflict": return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
                return (409,{"error":str(e)})
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{**result,"run":restarted["run"],"dispatch":restarted["dispatch"],"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/steward/force-restart$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "FORCE RESTART V2 RUN STEWARD": return (400,{"error":"confirmation phrase mismatch"})
            try: result=deps["force_restart_steward_handoff"](root,rid,b.get("expected_updated",""),"human:web-v2")
            except KeyError: return (404,{"error":"run not found"})
            except RuntimeError as e:
                if str(e)=="registry_version_conflict": return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
                return (409,{"error":str(e)})
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{**result,"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/steward/mark-failed$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "MARK V2 STEWARD ATTEMPT FAILED": return (400,{"error":"confirmation phrase mismatch"})
            try: result=deps["mark_steward_attempt_failed"](root,rid,b.get("expected_updated",""),b.get("reason",""),"human:web-v2")
            except KeyError: return (404,{"error":"run not found"})
            except RuntimeError as e:
                if str(e)=="registry_version_conflict": return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
                return (409,{"error":str(e)})
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{**result,"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/steward/correct-failed$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "CORRECT V2 FAILED RUN STATUS": return (400,{"error":"confirmation phrase mismatch"})
            try: result=deps["correct_failed_run_state"](root,rid,b.get("expected_updated",""),b.get("target_stage",""),b.get("reason",""),b.get("evidence",""),"human:web-v2")
            except KeyError: return (404,{"error":"run not found"})
            except RuntimeError as e:
                if str(e)=="registry_version_conflict": return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
                return (409,{"error":str(e)})
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{**result,"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)/workflow$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2)); action=str(b.get("action") or "")
            confirmations={"confirm-design":"CONFIRM V2 RUN DESIGN","implementation-ready":"MARK V2 RUN IMPLEMENTATION READY","reopen-design":"REOPEN V2 RUN DESIGN","begin-analysis":"BEGIN V2 RUN ANALYSIS","finalize-results":"FINALIZE V2 RUN RESULTS","mark-failed":"MARK V2 RUN FAILED"}
            if action not in confirmations: return (400,{"error":"unsupported workflow action"})
            if b.get("confirmation") != confirmations[action]: return (400,{"error":"confirmation phrase mismatch"})
            current=next((item for item in deps["experiment_data"](root)["runs"] if item.get("id")==rid),None)
            if not current: return (404,{"error":"run not found"})
            if str(b.get("expected_updated") or "") != str(current.get("updated") or ""): return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
            result_fields=b.get("result_fields") or {}
            if not isinstance(result_fields,dict): return (400,{"error":"result_fields must be an object"})
            allowed_results={"result_analysis","key_results","metric_observations","limitations","artifacts"}
            result_fields={key:value for key,value in result_fields.items() if key in allowed_results}
            try: result=deps["advance_run_workflow"](root,rid,action,"human:web-v2",result_fields)
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{"run":result["run"],"dashboard":result})
        m = re.match(r"^/api/v2/p/([^/]+)/papers/([^/]+)/seven/import-preview$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); citekey=urllib.parse.unquote(m.group(2))
            try: deps["note_path"](root,citekey)
            except ValueError as e: return (400,{"error":str(e)})
            text=b.get("text")
            if not isinstance(text,str) or not text.strip(): return (400,{"error":"text must be a non-empty string"})
            if len(text.encode("utf-8")) > 256*1024: return (400,{"error":"text exceeds 256KB limit"})
            parsed=deps["parse_gpt_response"](text); meta=parsed.get("meta") or {}; labels=deps["SEVENQ"]
            answers={label:str((parsed.get("seven_answers") or {}).get(f"q{index+1}") or "") for index,label in enumerate(labels)}
            warnings=[]
            if meta.get("target_type") and meta.get("target_type")!="paper": warnings.append("AI 输出的 target_type 不是 paper，请人工核对")
            if meta.get("target_id") and meta.get("target_id")!=citekey: warnings.append("AI 输出指向另一篇论文，请人工核对 target_id")
            if meta.get("target_address") and meta.get("target_address") not in {citekey,f"paper:{citekey}"}: warnings.append("AI 输出指向另一篇论文，请人工核对 target_address")
            missing=[label for label in labels if not answers[label]]
            return (200,{"answers":answers,"meta":meta,"parsed_count":len(labels)-len(missing),"missing":missing,"warnings":warnings})
        m = re.match(r"^/api/v2/p/([^/]+)/intake/materialize$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "MATERIALIZE V2 INTAKE": return (400,{"error":"confirmation phrase mismatch"})
            if b.get("expected_hash") != deps["intake_canonical_hash"](root): return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
            result=deps["materialize"](root)
            return (200,{"materialize":result,"state":deps["read_state"](root),"authority":"markdown"})
        m = re.match(r"^/api/v2/p/([^/]+)/initialize$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "INITIALIZE SURVEY TOOL 2.0": return (400,{"error":"confirmation phrase mismatch"})
            store=V2Store(root); existed=store.exists(); version=store.initialize()
            return (200,{"initialized":True,"already_initialized":existed,"schema_version":version,"relative_path":str(store.path.relative_to(root))})
        m = re.match(r"^/api/v2/p/([^/]+)/questions$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "CREATE V2 QUESTION": return (400,{"error":"confirmation phrase mismatch"})
            try: fields=_validated_question_fields(b.get("question"),creating=True)
            except ValueError as e: return (400,{"error":str(e)})
            q=deps["create_question"](root,fields)
            deps["refresh_v2_index"](root,actor_id="web-v2",content=False)
            q=next((item for item in deps["read_questions"](root) if item.get("id")==q.get("id")),q)
            return (200,{"question":q,"authority":"markdown","indexed":True})
        m = re.match(r"^/api/v2/p/([^/]+)/questions/(Q-\d+)/relations$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); qid=m.group(2)
            if b.get("confirmation")!="ADD V2 QUESTION RELATION": return (400,{"error":"confirmation phrase mismatch"})
            target_id=b.get("target_id")
            if not isinstance(target_id,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}",target_id): return (400,{"error":"target_id must be a safe object ID"})
            store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 store is not initialized","reason":"store_not_initialized"})
            question=next((item for item in deps["read_questions"](root) if item.get("id")==qid),None)
            if not question: return (404,{"error":"question not found"})
            if b.get("expected_hash")!=question.get("_canonical_rev"): return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
            try: target=_question_target(root,target_id,deps)
            except KeyError as e: return (404,{"error":str(e).strip("'")})
            _ensure_relation_object(store,root,qid,"question",question.get("title",qid),question.get("path",f"shell/01_questions/{qid}.md"))
            existing=next((rel for rel in store.list_relations(from_object_id=qid) if rel["relation_type"]==target["relation_type"] and rel["to_object_id"]==target_id),None)
            canonical_modified=False
            if target["field"] and target_id not in (question.get(target["field"],[]) or []):
                updated={**question,target["field"]:[*(question.get(target["field"],[]) or []),target_id],"updated":deps["now_iso"]()}
                deps["save_question"](root,updated,question); canonical_modified=True
                question=next(item for item in deps["read_questions"](root) if item.get("id")==qid)
            if existing: relation=existing
            else:
                try: relation=store.ensure_reference_relation(from_object_id=qid,relation_type=target["relation_type"],to_object_id=target_id,target_type=target["type"],project_id="PROJECT-"+hashlib.sha256(str(root).encode()).hexdigest()[:16],target_title=target["title"],target_canonical_path=target["canonical_path"],metadata={"authority":target["authority"],"inferred":False},actor_kind="human",actor_id="web-v2")
                except sqlite3.IntegrityError:
                    relation=next((rel for rel in store.list_relations(from_object_id=qid) if rel["relation_type"]==target["relation_type"] and rel["to_object_id"]==target_id),None)
                    if relation is None: return (500,{"error":"question canonical saved but relation index sync failed","reason":"index_sync_error","partial":canonical_modified,"canonical_question_modified":canonical_modified,"question":question})
                except Exception as e: return (500,{"error":"question canonical saved but relation index sync failed","reason":"index_sync_error","partial":canonical_modified,"canonical_question_modified":canonical_modified,"question":question,"detail":str(e)[:200]})
            return (200,{"question":question,"relation":relation,"authority":target["authority"],"canonical_question_modified":canonical_modified,"indexed":True})
        m = re.match(r"^/api/v2/p/([^/]+)/ideas$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "CREATE V2 IDEA": return (400,{"error":"confirmation phrase mismatch"})
            idea=b.get("idea")
            if not isinstance(idea,dict): return (400,{"error":"idea must be an object"})
            if not isinstance(idea.get("title"),str) or not idea["title"].strip(): return (400,{"error":"title is required"})
            fields={k:v for k,v in idea.items() if k in deps["IDEA_KEYS"] and k not in ("created","updated")}
            fields["title"]=fields["title"].strip(); iid=deps["append_idea"](root,fields)
            deps["refresh_v2_index"](root,actor_id="web-v2",identity=False)
            created=next(x for x in deps["read_ideas"](root) if x.get("id")==iid)
            return (200,{"idea":created,"authority":"markdown","indexed":True})
        m = re.match(r"^/api/v2/p/([^/]+)/comparisons$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "CREATE V2 COMPARISON": return (400,{"error":"confirmation phrase mismatch"})
            spec=b["comparison"]; name=str(spec.get("name") or "").strip()
            if not name: return (400,{"error":"comparison name is required"})
            data=deps["read_compares"](root); base=f"cmp-{deps['_stable_slug'](name,str(len(data)+1))}"; cid=base; n=2
            used={str(item.get("id") or "") for item in data}
            while cid in used: cid=f"{base}-{n}"; n+=1
            c={"id":cid,"name":name,"papers":spec.get("papers") or [],"axes":spec.get("axes") or [],"customAxes":[],"cells":{},"findings":[],"discussion":[],"mode":spec.get("mode") or "structured","analysis":spec.get("analysis") or ""}
            data.append(c); deps["save_compares"](root,data)
            return (200,{"comparison":c,"authority":"markdown","indexed":True})
        m = re.match(r"^/api/v2/p/([^/]+)/comparisons/(cmp-[^/]+)/findings$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); cid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "CREATE V2 FINDING": return (400,{"error":"confirmation phrase mismatch"})
            data=deps["read_compares"](root); comp=next((item for item in data if item.get("id")==cid),None)
            if not comp: return (404,{"error":"comparison not found"})
            spec=b["finding"]; text=str(spec.get("text") or "").strip()
            if not text: return (400,{"error":"finding text is required"})
            comp.setdefault("findings",[]).append({"text":text,"source":spec.get("source","")})
            data=deps["ensure_finding_ids"](data); deps["save_compares"](root,data)
            saved=next(item for item in data if item.get("id")==cid)["findings"][-1]
            return (200,{"finding":saved,"comparison_id":cid,"authority":"markdown","indexed":True})
        m = re.match(r"^/api/v2/p/([^/]+)/paper-candidates$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            hit=b.get("candidate") or {}; source_url=str(hit.get("url") or hit.get("source_url") or "")
            try:
                row=store.create_paper_candidate(object_id=str(hit.get("object_id") or f"PC-{secrets.token_hex(8)}"),project_id=str(hit.get("project_id") or f"PROJECT-{hashlib.sha256(str(root).encode()).hexdigest()[:16]}"),citekey=str(hit.get("citekey") or deps["citekey_for"]({"title":hit.get("title",""),"date":hit.get("year","")})),title=str(hit.get("title") or "Untitled candidate"),source_url=source_url,authors=list(hit.get("authors") or []),year=str(hit.get("year") or ""),doi=str(hit.get("doi") or ""),oa_url=str(hit.get("oa_url") or ""),source=str(hit.get("source") or "openalex"),recommendation_reason=str(b.get("recommendation_reason") or ""),actor_kind="human",actor_id="web-v2")
            except (ValueError,sqlite3.IntegrityError) as e: return (400,{"error":str(e)})
            return (201,{"candidate":row})
        m = re.match(r"^/api/v2/p/([^/]+)/paper-candidates/([^/]+)/acquisition$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            if b.get("confirmation") != "STAGE PAPER ACQUISITION": return (400,{"error":"confirmation phrase mismatch"})
            try: pipeline=store.create_candidate_acquisition_pipeline(urllib.parse.unquote(m.group(2)),expected_revision=int(b.get("expected_revision") or 0),actor_id="web-v2")
            except (ValueError,KeyError) as e: return (409 if "revision conflict" in str(e) else 400,{"error":str(e)})
            return (202,_public_pipeline(pipeline))
        m = re.match(r"^/api/v2/p/([^/]+)/jobs/run-local$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            if b.get("confirmation") != "RUN LOCAL PAPER WORKER": return (400,{"error":"confirmation phrase mismatch"})
            target=str(b.get("target_object_id") or ""); max_jobs=b.get("max_jobs",2)
            try: result=deps["start_local_worker"](root,target_object_id=target,max_jobs=int(max_jobs))
            except (ValueError,TypeError) as e: return (400,{"error":str(e)})
            return (202,result)
        m = re.match(r"^/api/v2/p/([^/]+)/migration/identity-index/apply$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "APPLY IDENTITY INDEX MIGRATION": return (400,{"error":"confirmation phrase mismatch"})
            try: result=deps["apply_identity_index_migration"](root,actor_id="web-v2")
            except ValueError as e: return (409,{"error":str(e)})
            return (200,result)
        m = re.match(r"^/api/v2/p/([^/]+)/migration/content-index/apply$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "APPLY CONTENT INDEX MIGRATION": return (400,{"error":"confirmation phrase mismatch"})
            try: result=deps["apply_content_index_migration"](root,actor_id="web-v2")
            except ValueError as e: return (409,{"error":str(e)})
            return (200,result)
        m = re.match(r"^/api/v2/p/([^/]+)/jobs/([^/]+)/(retry|cancel)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            action=m.group(3); confirmation="RETRY FAILED JOB" if action=="retry" else "CANCEL QUEUED JOB"
            if b.get("confirmation") != confirmation: return (400,{"error":"confirmation phrase mismatch"})
            try:
                if action=="retry": jobs=[store.retry_failed_job(urllib.parse.unquote(m.group(2)),expected_revision=int(b.get("expected_revision") or 0),reason=str(b.get("reason") or ""),actor_id="web-v2")]
                else: jobs=store.cancel_queued_job(urllib.parse.unquote(m.group(2)),expected_revision=int(b.get("expected_revision") or 0),reason=str(b.get("reason") or ""),actor_id="web-v2")
            except KeyError as e: return (404,{"error":str(e)})
            except ValueError as e: return (409 if "revision conflict" in str(e) else 400,{"error":str(e)})
            return (200,{"jobs":[_public_job(job) for job in jobs],"worker_started":False,"running_process_stopped":False})
        m = re.match(r"^/api/v2/p/([^/]+)/objects/archive$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            restore=bool(b.get("restore")); confirmation="RESTORE V2 OBJECTS" if restore else "ARCHIVE V2 OBJECTS"
            if b.get("confirmation") != confirmation: return (400,{"error":"confirmation phrase mismatch"})
            try: objects=store.archive_objects(list(b.get("items") or []),reason=str(b.get("reason") or ""),actor_id="web-v2",restore=restore)
            except KeyError as e: return (404,{"error":str(e)})
            except ValueError as e: return (409 if "revision conflict" in str(e) else 400,{"error":str(e)})
            return (200,{"objects":objects,"hard_delete":False,"canonical_files_deleted":False})
        m = re.match(r"^/api/v2/p/([^/]+)/automations$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            if b.get("confirmation") != "CREATE AUTOMATION DRAFT": return (400,{"error":"confirmation phrase mismatch"})
            spec=b.get("automation") or {}
            try: automation=store.create_automation(object_id=str(spec.get("id") or f"AUTO-{secrets.token_hex(8)}"),project_id=f"PROJECT-{hashlib.sha256(str(root).encode()).hexdigest()[:16]}",title=str(spec.get("title") or "Bounded automation"),automation_type=str(spec.get("automation_type") or "research"),target_type=str(spec.get("target_type") or "question"),target_id=str(spec.get("target_id") or ""),budget=dict(spec.get("budget") or {}),actor_id="web-v2")
            except (ValueError,sqlite3.IntegrityError) as e: return (400,{"error":str(e)})
            return (201,{"automation":automation,"started":False})
        m = re.match(r"^/api/v2/p/([^/]+)/herdr-launch-requests$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            if b.get("confirmation") != "CREATE HERDR LAUNCH REQUEST DRAFT": return (400,{"error":"confirmation phrase mismatch"})
            spec=b.get("launch_request") or {}
            try:
                target_id=str(spec.get("target_object_id") or "")
                # Launch Requests target verified v2 identities. If a real legacy
                # Experiment/Question exists but its identity projection is
                # missing, create only that reference identity; never alter its
                # canonical authority.
                deps["ensure_v2_binding_target"](root,store,target_id)
                request=store.create_herdr_launch_request(object_id=str(spec.get("id") or f"HLR-{secrets.token_hex(8)}"),project_id=f"PROJECT-{hashlib.sha256(str(root).encode()).hexdigest()[:16]}",target_object_id=target_id,agent_kind=str(spec.get("agent_kind") or "codex"),task_type=str(spec.get("task_type") or "discussion"),task_summary=str(spec.get("task_summary") or ""),safe_config=dict(spec.get("safe_config") or {}),actor_id="web-v2")
            except KeyError as e: return (404,{"error":str(e)})
            except (ValueError,sqlite3.IntegrityError) as e: return (400,{"error":str(e)})
            return (201,{"launch_request":deps["public_herdr_launch_request"](request),"execution_started":False,"prompt_stored":False,"command_stored":False})
        m = re.match(r"^/api/v2/p/([^/]+)/herdr-launch-requests/([^/]+)/transition$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            status=str(b.get("status") or ""); expected_confirmation={"awaiting_approval":"SUBMIT HERDR LAUNCH REQUEST FOR APPROVAL","approved":"APPROVE HERDR LAUNCH REQUEST","cancelled":"CANCEL HERDR LAUNCH REQUEST"}.get(status)
            if not expected_confirmation or b.get("confirmation") != expected_confirmation: return (400,{"error":"confirmation phrase mismatch"})
            try: request=store.transition_herdr_launch_request(urllib.parse.unquote(m.group(2)),expected_revision=int(b.get("expected_revision") or 0),status=status,actor_id="web-v2")
            except KeyError as e: return (404,{"error":str(e)})
            except ValueError as e: return (409 if "revision conflict" in str(e) else 400,{"error":str(e)})
            return (200,{"launch_request":deps["public_herdr_launch_request"](request),"execution_started":False,"herdr_invoked":False})
        m = re.match(r"^/api/v2/p/([^/]+)/herdr-launch-requests/([^/]+)/authorize$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root); request_id=urllib.parse.unquote(m.group(2))
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            if b.get("confirmation") != f"AUTHORIZE HERDR EXECUTION {request_id}": return (400,{"error":"confirmation phrase mismatch"})
            capability=deps["v2_capabilities"](root).get("herdr") or {}
            try: execution=store.authorize_herdr_execution(execution_id=f"HEX-{secrets.token_hex(8)}",project_id=f"PROJECT-{hashlib.sha256(str(root).encode()).hexdigest()[:16]}",launch_request_id=request_id,expected_request_revision=int(b.get("expected_request_revision") or 0),capability=capability,ttl_seconds=int(b.get("ttl_seconds") or 300),actor_id="web-v2")
            except KeyError as e: return (404,{"error":str(e)})
            except (ValueError,sqlite3.IntegrityError) as e: return (409,{"error":str(e)})
            return (201,{"execution":deps["public_herdr_execution"](execution),"execution_started":False,"herdr_invoked":False})
        m = re.match(r"^/api/v2/p/([^/]+)/herdr-executions/([^/]+)/revoke$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root); execution_id=urllib.parse.unquote(m.group(2))
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            if b.get("confirmation") != f"REVOKE HERDR EXECUTION {execution_id}": return (400,{"error":"confirmation phrase mismatch"})
            try: execution=store.revoke_herdr_execution(execution_id,expected_revision=int(b.get("expected_execution_revision") or 0),actor_id="web-v2")
            except KeyError as e: return (404,{"error":str(e)})
            except ValueError as e: return (409,{"error":str(e)})
            return (200,{"execution":deps["public_herdr_execution"](execution),"execution_started":False,"herdr_invoked":False})
        m = re.match(r"^/api/v2/p/([^/]+)/automations/([^/]+)/transition$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            status=str(b.get("status") or ""); expected_confirmation={"awaiting_approval":"SUBMIT AUTOMATION FOR APPROVAL","active":"APPROVE AUTOMATION","checkpoint":"CHECKPOINT AUTOMATION","paused":"PAUSE AUTOMATION","completed":"COMPLETE AUTOMATION","completed_with_warnings":"COMPLETE AUTOMATION WITH WARNINGS","failed":"FAIL AUTOMATION","cancelled":"CANCEL AUTOMATION"}.get(status)
            if not expected_confirmation or b.get("confirmation") != expected_confirmation: return (400,{"error":"confirmation phrase mismatch"})
            approval={}
            if status=="active":
                approval["approved_by"]="human:web-v2"
                if b.get("approve_experiment_phase"): approval["experiment_phase_approved_by"]="human:web-v2"
            try: automation=store.transition_automation(urllib.parse.unquote(m.group(2)),expected_revision=int(b.get("expected_revision") or 0),status=status,phase=b.get("phase"),approval=approval,actor_id="web-v2")
            except (ValueError,KeyError) as e: return (409 if "revision conflict" in str(e) else 400,{"error":str(e)})
            return (200,{"automation":automation,"execution_started":False})
        m = re.match(r"^/api/v2/p/([^/]+)/agent-sessions/bind-current-pi$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root)
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            if b.get("confirmation") != "BIND CURRENT PI SESSION": return (400,{"error":"confirmation phrase mismatch"})
            snapshot=deps["read_pi_binding"](root); stable_id=str(snapshot.get("session_id") or "")
            if not stable_id: return (409,{"error":"no verified pi session binding is available"})
            try:
                target=deps["ensure_v2_binding_target"](root,store,str(b.get("object_id") or "")); bridges=deps["BRIDGES"]
                session=store.bind_agent_session(session_id=f"AS-{hashlib.sha256(stable_id.encode()).hexdigest()[:24]}",provider="pi",object_id=str(b.get("object_id") or ""),task_type=str(b.get("task_type") or "discussion"),external_ref=f"session-id:{stable_id}",status="live" if (bridges.get(str(root.resolve())) and bridges[str(root.resolve())].proc and bridges[str(root.resolve())].proc.poll() is None) else "stale",agent="pi",model="")
            except KeyError as e: return (404,{"error":str(e)})
            except (ValueError,sqlite3.IntegrityError) as e: return (400,{"error":str(e)})
            return (201,{"session":deps["public_agent_session"](session),"target":{"id":target["id"],"type":target["type"],"authority":"legacy_json" if target["type"]=="experiment" else "markdown" if target["type"]=="question" else "sqlite","reference_identity_only":target["lifecycle_status"]=="reference"},"messages_copied":False,"prompt_copied":False,"session_path_copied":False})
        m = re.match(r"^/api/v2/p/([^/]+)/paper-candidates/([^/]+)/ingest$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); store=V2Store(root); object_id=urllib.parse.unquote(m.group(2))
            if not store.exists(): return (409,{"error":"v2 project store is not initialized"})
            try: candidate=store.get_paper_candidate(object_id)
            except KeyError as e: return (404,{"error":str(e)})
            expected_confirmation=f"INGEST {candidate['citekey']}"
            if b.get("confirmation") != expected_confirmation: return (400,{"error":f"confirmation must be: {expected_confirmation}"})
            def canonical_runner(pdf,candidate_row):
                args=[sys.executable,str(deps["paper_skill_script"]("ingest.py")),"--project",str(root),"--pdf",str(pdf),"--citekey",candidate_row["citekey"],"--title",candidate_row["title"],"--authors",", ".join(candidate_row.get("authors") or []),"--year",candidate_row.get("year") or "","--url",candidate_row.get("source_url") or "","--doi",candidate_row.get("doi") or ""]
                result=deps["run_script"](args,cwd=str(root),timeout=120)
                try: payload=json.loads(result.get("stdout") or "{}")
                except Exception: payload={}
                return {"ok":result.get("returncode")==0,"error":result.get("stderr") or payload.get("error"),**payload}
            try: ingested=deps["ingest_staged_candidate"](root,store,object_id,expected_revision=int(b.get("expected_revision") or 0),actor_id="web-v2",ingest_runner=canonical_runner)
            except FileExistsError as e: return (409,{"error":str(e)})
            except (ValueError,RuntimeError) as e: return (400,{"error":str(e)})
            return (200,{"candidate":ingested,"canonical_write":True})

    if method == "PUT":
        m = re.match(r"^/api/v2/p/([^/]+)/agent-routing$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "UPDATE V2 AGENT ROUTING": return (400,{"error":"confirmation phrase mismatch"})
            if set(b)-{"confirmation","routing"}: return (400,{"error":"unsupported agent routing payload"})
            try: routing=deps["write_agent_routing"](root,b.get("routing"))
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{"routing":routing,"authority":"project_tool_state","known_codex_models":["gpt-5.6-sol","gpt-5.6-terra","gpt-5.6-luna","gpt-5.5"],"applies_to":"future_dispatches_only"})
        m = re.match(r"^/api/v2/p/([^/]+)/servers/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); sid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "UPDATE V2 SERVER": return (400,{"error":"confirmation phrase mismatch"})
            try: return (200,deps["update_server_binding"](root,sid,str(b.get("expected_hash") or ""),b.get("fields")))
            except RuntimeError as e:
                if str(e)=="content_hash_conflict": return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
                return (500,{"error":str(e)})
            except ValueError as e: return (400,{"error":str(e)})
        m = re.match(r"^/api/v2/p/([^/]+)/workspaces/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); wid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "UPDATE V2 WORKSPACE": return (400,{"error":"confirmation phrase mismatch"})
            try: return (200,deps["update_workspace_binding"](root,wid,str(b.get("expected_hash") or ""),b.get("fields")))
            except RuntimeError as e:
                if str(e)=="content_hash_conflict": return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
                return (500,{"error":str(e)})
            except ValueError as e: return (400,{"error":str(e)})
        m = re.match(r"^/api/v2/p/([^/]+)/experiments/(E-\d+)/run-grouping/ai-apply$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=m.group(2)
            if b.get("confirmation") != "APPLY V2 AI RUN GROUPING": return (400,{"error":"confirmation phrase mismatch"})
            current=next((item for item in deps["experiment_data"](root)["experiments"] if item.get("id")==eid),None)
            if not current: return (404,{"error":"experiment not found"})
            if str(b.get("expected_updated") or "") != str(current.get("updated") or ""): return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
            try: result=deps["apply_agent_run_grouping"](root,eid,b.get("groups",[]),b.get("assignments",{}))
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{"experiment":next(item for item in result["experiments"] if item.get("id")==eid),"dashboard":result,"grouping_result":result.get("grouping_result",{})})
        m = re.match(r"^/api/v2/p/([^/]+)/experiments/(E-\d+)/run-grouping$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=m.group(2)
            if b.get("confirmation") != "UPDATE V2 RUN GROUPING": return (400,{"error":"confirmation phrase mismatch"})
            current=next((item for item in deps["experiment_data"](root)["experiments"] if item.get("id")==eid),None)
            if not current: return (404,{"error":"experiment not found"})
            if str(b.get("expected_updated") or "") != str(current.get("updated") or ""): return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
            try: deps["apply_run_grouping"](root,eid,b.get("groups",[]),b.get("assignments",{}))
            except ValueError as e: return (409 if "审核" in str(e) or "锁" in str(e) else 400,{"error":str(e)})
            return (200,{"experiment":next(item for item in deps["experiment_data"](root)["experiments"] if item.get("id")==eid),"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/experiments/(E-\d+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=m.group(2)
            if b.get("confirmation") != "UPDATE V2 EXPERIMENT": return (400,{"error":"confirmation phrase mismatch"})
            current=next((item for item in deps["experiment_data"](root)["experiments"] if item.get("id")==eid),None)
            if not current: return (404,{"error":"experiment not found"})
            if str(b.get("expected_updated") or "") != str(current.get("updated") or ""): return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
            if not isinstance(b.get("fields"),dict): return (400,{"error":"fields must be an object"})
            allowed={"title","objective","workspace_id","constraints","evidence_refs","hypothesis","success_criteria","failure_criteria","schedule","variables","minimum_test","baseline","treatments","metrics","confounders","risks","open_questions","budget","run_groups","metric_definitions"}
            fields={key:value for key,value in b["fields"].items() if key in allowed}
            try: updated=deps["update_experiment"](root,eid,fields)
            except ValueError as e: return (400,{"error":str(e)})
            return (200,{"experiment":updated,"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/runs/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "UPDATE V2 RUN": return (400,{"error":"confirmation phrase mismatch"})
            current=next((item for item in deps["experiment_data"](root)["runs"] if item.get("id")==rid),None)
            if not current: return (404,{"error":"run not found"})
            if str(b.get("expected_updated") or "") != str(current.get("updated") or ""): return (409,{"error":"concurrent modification","reason":"registry_version_conflict"})
            if not isinstance(b.get("fields"),dict): return (400,{"error":"fields must be an object"})
            forbidden={"status","created_by","agent_review_summary","agent_review_questions","steward_summary"}
            fields={key:value for key,value in b["fields"].items() if key in deps["RUN_MUTABLE_FIELDS"] and key not in forbidden and not any(token in key for token in ("review","execution","dispatch","lease","authorization","approved","history"))}
            try: updated=deps["update_run"](root,rid,fields)
            except ValueError as e: return (409 if "审核" in str(e) else 400,{"error":str(e)})
            return (200,{"run":updated,"dashboard":deps["experiment_dashboard_data"](root)})
        m = re.match(r"^/api/v2/p/([^/]+)/intake$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if b.get("confirmation") != "UPDATE V2 INTAKE": return (400,{"error":"confirmation phrase mismatch"})
            if b.get("expected_hash") != deps["intake_canonical_hash"](root): return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
            data=b.get("data")
            if not isinstance(data,dict): return (400,{"error":"data must be an object"})
            current=deps["read_intake"](root)
            clean={key:current.get(key,[]) if key in deps["INTAKE_LIST_FIELDS"] else current.get(key,"") for key in [*deps["INTAKE_FIELDS"],*deps["INTAKE_LIST_FIELDS"]]}
            clean["notes"]=current.get("notes","")
            for key in deps["INTAKE_FIELDS"]:
                if key in data:
                    if not isinstance(data[key],str): return (400,{"error":f"{key} must be a string"})
                    clean[key]=data[key]
            for key in deps["INTAKE_LIST_FIELDS"]:
                if key in data:
                    if not isinstance(data[key],list) or not all(isinstance(item,str) for item in data[key]): return (400,{"error":f"{key} must be a list of strings"})
                    clean[key]=data[key]
            if "notes" in data:
                if not isinstance(data["notes"],str): return (400,{"error":"notes must be a string"})
                clean["notes"]=data["notes"]
            deps["write_intake"](root,clean)
            return (200,{"intake":deps["read_intake"](root),"authority":"markdown"})
        m = re.match(r"^/api/v2/p/([^/]+)/ideas/(I-\d+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); iid=m.group(2)
            if b.get("confirmation") != "UPDATE V2 IDEA": return (400,{"error":"confirmation phrase mismatch"})
            current=next((item for item in deps["read_ideas"](root) if item.get("id")==iid),None)
            if not current: return (404,{"error":"idea not found"})
            if b.get("expected_hash") != deps["idea_canonical_hash"](root): return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
            fields=b.get("fields")
            if not isinstance(fields,dict): return (400,{"error":"fields must be an object"})
            allowed={"title","hypothesis","motivation","method","key_experiments","risks","related_diff","falsification","status","novelty","novelty_note","support_claims","contra_claims","sources"}
            update={k:v for k,v in fields.items() if k in allowed and k in deps["IDEA_KEYS"]}
            if "title" in update and (not isinstance(update["title"],str) or not update["title"].strip()): return (400,{"error":"title is required"})
            if "title" in update: update["title"]=update["title"].strip()
            deps["update_idea"](root,iid,update); deps["refresh_v2_index"](root,actor_id="web-v2",identity=False)
            updated=next(x for x in deps["read_ideas"](root) if x.get("id")==iid)
            return (200,{"idea":updated,"authority":"markdown","indexed":True})
        m = re.match(r"^/api/v2/p/([^/]+)/papers/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); citekey=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "UPDATE V2 PAPER": return (400,{"error":"confirmation phrase mismatch"})
            try: canonical=deps["note_path"](root,citekey)
            except ValueError as e: return (400,{"error":str(e)})
            text=canonical.read_text(encoding="utf-8") if canonical.exists() else ""
            current_hash="sha256:"+hashlib.sha256(text.encode()).hexdigest()
            if b.get("expected_hash") != current_hash: return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
            deps["update_paper_canonical"](root,citekey,b)
            deps["refresh_v2_index"](root,actor_id="web-v2",identity=False)
            return (200,{"paper":deps["paper_bundle"](root,citekey),"authority":"markdown","indexed":True})
        m = re.match(r"^/api/v2/p/([^/]+)/comparisons/(cmp-[^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); cid=urllib.parse.unquote(m.group(2))
            if b.get("confirmation") != "UPDATE V2 COMPARISON": return (400,{"error":"confirmation phrase mismatch"})
            data=deps["read_compares"](root); c=next((item for item in data if item.get("id")==cid),None)
            if not c: return (404,{"error":"comparison not found"})
            if c.get("_canonical_rev") != b.get("expected_hash"): return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
            c.update({k:v for k,v in b["fields"].items() if k in ("name","papers","axes","analysis")}); deps["save_compares"](root,data)
            return (200,{"comparison":c,"authority":"markdown","indexed":True})
        m = re.match(r"^/api/v2/p/([^/]+)/findings/(F-\d+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); fid=m.group(2)
            if b.get("confirmation") != "UPDATE V2 FINDING": return (400,{"error":"confirmation phrase mismatch"})
            data=deps["read_compares"](root); f=next((finding for comp in data for finding in (comp.get("findings",[]) or []) if finding.get("id")==fid),None)
            if not f: return (404,{"error":"finding not found"})
            if f.get("_canonical_rev") != b.get("expected_hash"): return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
            f.update({k:v for k,v in b["fields"].items() if k in ("text","source")}); deps["save_compares"](root,data)
            return (200,{"finding":f,"authority":"markdown","indexed":True})
        m = re.match(r"^/api/v2/p/([^/]+)/questions/(Q-\d+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); qid=m.group(2)
            if b.get("confirmation") != "UPDATE V2 QUESTION": return (400,{"error":"confirmation phrase mismatch"})
            canonical=deps["questions_dir"](root)/f"{qid}.md"; text=canonical.read_text(encoding="utf-8") if canonical.exists() else ""
            current_hash="sha256:"+hashlib.sha256(text.encode()).hexdigest()
            if b.get("expected_hash") != current_hash: return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
            old=next((x for x in deps["read_questions"](root) if x.get("id")==qid),None)
            if not old: return (404,{"error":"question not found"})
            try: fields=_validated_question_fields(b.get("fields"))
            except ValueError as e: return (400,{"error":str(e)})
            q={**old,**fields}; q["id"]=qid; q["updated"]=deps["now_iso"]()
            if not str(q.get("title") or "").strip() or not str(q.get("question") or "").strip(): return (400,{"error":"title and question are required"})
            deps["save_question"](root,q,old); deps["generate_obsidian_indexes"](root); deps["refresh_v2_index"](root,actor_id="web-v2",content=False)
            q=next(item for item in deps["read_questions"](root) if item.get("id")==qid)
            return (200,{"question":q,"authority":"markdown","indexed":True})

    if method == "DELETE":
        m = re.match(r"^/api/v2/p/([^/]+)/questions/(Q-\d+)/relations/(REL-[A-Za-z0-9_-]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); qid=m.group(2); relation_id=m.group(3)
            if b.get("confirmation")!="REMOVE V2 QUESTION RELATION": return (400,{"error":"confirmation phrase mismatch"})
            store=V2Store(root)
            if not store.exists(): return (404,{"error":"relation not found"})
            relation=next((item for item in store.list_relations(from_object_id=qid) if item.get("id")==relation_id),None)
            if not relation: return (404,{"error":"relation not found for question"})
            question=next((item for item in deps["read_questions"](root) if item.get("id")==qid),None)
            if not question: return (404,{"error":"question not found"})
            if b.get("expected_hash") and b.get("expected_hash")!=question.get("_canonical_rev"): return (409,{"error":"concurrent modification","reason":"content_hash_conflict"})
            target=store.get_object(relation["to_object_id"]); field={"paper":"papers","comparison":"comparisons","finding":"findings","experiment":"experiments"}.get(target["type"],"")
            canonical_modified=False
            if field and relation["to_object_id"] in (question.get(field,[]) or []):
                updated={**question,field:[item for item in question.get(field,[]) if item!=relation["to_object_id"]],"updated":deps["now_iso"]()}
                deps["save_question"](root,updated,question); canonical_modified=True
                question=next(item for item in deps["read_questions"](root) if item.get("id")==qid)
            try: removed=store.delete_relation(relation_id,expected_from_object_id=qid,actor_kind="human",actor_id="web-v2")
            except Exception as e: return (500,{"error":"question canonical saved but relation index removal failed","reason":"index_sync_error","partial":canonical_modified,"question":question,"detail":str(e)[:200]})
            return (200,{"question":question,"removed_relation":removed,"authority":"question_frontmatter" if field else "v2_navigation_index","canonical_question_modified":canonical_modified,"indexed":True})

    return None
