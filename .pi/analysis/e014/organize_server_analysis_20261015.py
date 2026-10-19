"""一次性整理：只迁移明确列出的13个已结束E-014分析Run，保留原文件。"""
import json, pathlib, subprocess
plan_path=pathlib.Path('.pi/analysis/e014/server_directory_migration_plan_20261015.json')
plan=json.loads(plan_path.read_text())
remote_script='PLAN='+repr(plan)+'\n'+r'''
import pathlib,hashlib,json,os,stat,datetime
base=pathlib.Path(PLAN['base'])
target=base/'analysis'
receipt_path=target/'directory_migration_20261015.json'
assert not receipt_path.exists(), '迁移记录已存在，拒绝重复执行'
assert not (target/'README.md').exists(), '目标索引已存在，拒绝覆盖'
ids={r['id'] for r in PLAN['runs']}
# 只比较进程命令，不读取环境；不输出进程或终端标识。
active=0
for item in pathlib.Path('/proc').iterdir():
    if not item.name.isdigit(): continue
    try: args=(item/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
    except (FileNotFoundError,PermissionError,ProcessLookupError): continue
    if any(rid in args for rid in ids): active+=1
assert active==0, '分析目录仍被进程使用，停止整理'
def inventory(folder):
    out={}
    for p in sorted(folder.rglob('*')):
        rel=p.relative_to(folder).as_posix();s=p.lstat()
        item={'mode':s.st_mode,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'device':s.st_dev,'inode':s.st_ino}
        if stat.S_ISLNK(s.st_mode): item['link_target']=os.readlink(p)
        elif stat.S_ISREG(s.st_mode):
            if not any(x.startswith('.survey-tool') for x in p.relative_to(folder).parts):
                h=hashlib.sha256()
                with p.open('rb') as f:
                    for block in iter(lambda:f.read(1048576),b''):h.update(block)
                item['sha256']=h.hexdigest()
            else: item['content_check']='opaque_control_file_inode_size_mtime_preserved'
        elif not stat.S_ISDIR(s.st_mode): raise ValueError('不支持的文件类型')
        out[rel]=item
    return out
before={}
for r in PLAN['runs']:
    src=pathlib.Path(r['old']);dst=pathlib.Path(r['new'])
    assert src.is_dir() and not src.is_symlink() and not dst.exists()
    assert (src/'.survey-tool-complete').is_file(), '尚未结束的Run不可移动'
    before[r['id']]=inventory(src)
target.mkdir(exist_ok=True)
assert not target.is_symlink() and target.stat().st_dev==base.stat().st_dev
moved=[]
try:
    for r in PLAN['runs']:
        pathlib.Path(r['old']).rename(r['new']);moved.append(r)
        assert inventory(pathlib.Path(r['new']))==before[r['id']], '迁移完整性不一致'
except BaseException:
    for r in reversed(moved): pathlib.Path(r['new']).rename(r['old'])
    raise
receipt={'experiment_id':'E-014','completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'moves':[{'id':r['id'],'old':r['old'],'new':r['new'],'status_at_migration':r['status'],'inventory':before[r['id']]} for r in PLAN['runs']],'checks':{'all_original_files_unchanged':True,'atomic_same_filesystem_rename':True,'old_top_level_analysis_directories_absent':all(not pathlib.Path(r['old']).exists() for r in PLAN['runs']),'archived_analysis_process_count':active,'historical_sources_commands_logs_preserved':True,'managed_control_files_not_read':True},'files_hashed':sum('sha256' in f for v in before.values() for f in v.values()),'opaque_control_files_preserved':sum(f.get('content_check') is not None for v in before.values() for f in v.values())}
with receipt_path.open('x') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
lines=['# E-014 分析目录索引','','这里保存已结束的分析/诊断 Run；训练、checkpoint 和评测 Run 仍位于 E-014 一级目录。','','原文件完整保留，Run ID 未改变。2026-10-15 迁移采用同一文件系统目录重命名；结果、日志、快照、执行脚本不改写。','','旧路径 `E-014/<Run ID>` 的当前位置为 `E-014/analysis/<Run ID>`；历史脚本/命令中的旧地址仅保留执行时事实，不能直接作为重跑入口。','','详见 [迁移与完整性记录](directory_migration_20261015.json)。','','| Run ID | 迁移时状态 |','| --- | --- |']
for r in PLAN['runs']:lines.append('| ['+r['id']+']('+r['id']+'/) | '+r['status']+' |')
with (target/'README.md').open('x') as f:f.write('\n'.join(lines)+'\n')
print(json.dumps({'moved':len(moved),'files_hashed':receipt['files_hashed'],'opaque_control_files_preserved':receipt['opaque_control_files_preserved'],'integrity':'passed','target':str(target),'receipt':str(receipt_path)},ensure_ascii=False))
'''
result=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090','python3 -'],input=remote_script,text=True,capture_output=True)
print(result.stdout,end='')
if result.returncode:
    print(result.stderr[-3000:])
    raise SystemExit(result.returncode)
receipt_remote=plan['base']+'/analysis/directory_migration_20261015.json'
fetch=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090','cat '+receipt_remote],text=True,capture_output=True)
if fetch.returncode:raise SystemExit('服务器已完成迁移，本地回执获取失败')
receipt=json.loads(fetch.stdout)
assert len(receipt['moves'])==13 and receipt['checks']['all_original_files_unchanged']
local=pathlib.Path('.pi/analysis/e014/server_directory_migration_20261015.json')
with local.open('x') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'local_receipt':str(local)},ensure_ascii=False))
