"""本次授权的一次性日志快照和离线诊断；不重试、不修改训练。"""
import collections
import datetime
import json
from pathlib import Path
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
B = json.loads((HERE / 'binding.json').read_text())
def save(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2))
def mean(values):
    return sum(values) / len(values) if values else None

def main():
    # 标记先于网络读取落盘；即使失败也不会自动再次读取。
    try:
        with (HERE / 'attempted.json').open('x') as f:
            json.dump({'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}, f)
    except FileExistsError:
        return
    remote = '''import json,os
from pathlib import Path
base=Path(BASE)/'payload/grpo'
result=[]
for rank in range(8):
 p=base/('rollouts-rank%d.jsonl'%rank)
 if not p.is_file():
  result.append(dict(rank=rank,missing=True,records=[]));continue
 with p.open('rb') as f:
  size=os.fstat(f.fileno()).st_size
  # 单次有限快照；忽略末尾尚未写完的行。
  raw=f.read(size)
 rows=[]
 for line in raw.splitlines(keepends=True):
  if not line.endswith(b'\\n'):continue
  x=json.loads(line)
  rows.append({k:x.get(k) for k in ['step','sample_id','training_source','target_present','terminated','reward','advantage','completion_tokens']})
 result.append(dict(rank=rank,missing=False,snapshot_bytes=size,records=rows))
root=Path(BASE)
cfg=json.loads((root/'payload/trainer_config.json').read_text())
exitpath=root/'.survey-tool-exit-code'
meta=dict(trainer={k:cfg.get(k) for k in ['reward_scheme','reward','group_size','beta','max_steps']},saved_checkpoints=sorted(x.name for x in (root/'payload/grpo/checkpoints').glob('step_*')),exit_code=exitpath.read_text().strip() if exitpath.exists() else None)
metrics=root/'payload/grpo/evaluations/step_000300/metrics.json'
meta['step300_metrics']=json.loads(metrics.read_text()) if metrics.exists() else None
print(json.dumps(dict(ranks=result,meta=meta)))
'''.replace('BASE', repr(B['run_dir']))
    try:
        proc = subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090', '/songzhengyue/miniconda3/envs/IPLoc/bin/python -'], input=remote, text=True, capture_output=True, timeout=180)
        if proc.returncode:
            raise RuntimeError('SSH snapshot failed, exit code '+str(proc.returncode))
        payload = json.loads(proc.stdout)
        save('runtime.json', payload['meta'])
        ranks = payload['ranks']
        save('snapshot.json', ranks)
        counts = [collections.Counter(x['step'] for x in rank['records']) for rank in ranks]
        complete = sorted(set.intersection(*[{s for s,n in c.items() if n==16} for c in counts]))
        steps = complete[-20:]
        rows = [dict(x,rank=r['rank']) for r in ranks for x in r['records'] if x['step'] in steps]
        def stats(xs):
            valid=[x for x in xs if x['reward'].get('valid')]
            pos=[x for x in valid if x['target_present']]
            multi=[x for x in valid if x['reward'].get('candidate_count',0)>1]
            pm=[x for x in pos if x['reward'].get('candidate_count',0)>1]
            def gap(x):
                us=x['reward'].get('candidate_ious')
                selected=x['reward'].get('selected_iou')
                return max(us)-selected if us and selected is not None else None
            return dict(total=len(xs),valid=len(valid),valid_rate=len(valid)/len(xs) if xs else None,
              valid_multibox=len(multi),multibox_per_all=len(multi)/len(xs) if xs else None,
              multibox_per_valid=len(multi)/len(valid) if valid else None,
              valid_positive=len(pos),valid_positive_multibox=len(pm),
              selected_iou=mean([x['reward']['selected_iou'] for x in pos if x['reward'].get('selected_iou') is not None]),
              oracle_selected_gap=mean([gap(x) for x in pos if gap(x) is not None]),
              unterminated=sum(not x['terminated'] for x in xs),
              tiers=dict(collections.Counter(str(x['reward'].get('behavioral_tier')) for x in pos)))
        overall=stats(rows)
        report=dict(run_id=B['run_id'],observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          complete_step_count=len(complete),window_steps=steps,overall=overall,
          by_source={s:stats([x for x in rows if x['training_source']==s]) for s in sorted({x['training_source'] for x in rows})})
        groups=collections.defaultdict(list)
        for x in rows:groups[(x['rank'],x['step'],x['sample_id'])].append(x)
        comparisons=[]
        for xs in groups.values():
            if len(xs)!=8:continue
            a=[x['advantage'] for x in xs if x['reward'].get('valid') and x['reward'].get('candidate_count',0)>1]
            b=[x['advantage'] for x in xs if x['reward'].get('valid') and x['reward'].get('candidate_count')==1]
            if a and b:comparisons.append(mean(a)-mean(b))
        report['mixed_groups']=len(comparisons)
        report['within_group_multi_minus_single_advantage']=mean(comparisons)
        enough=len(steps)>=10 and overall['valid_positive']>=100
        collapsed=enough and overall['valid_rate']>=.95 and overall['valid_positive_multibox']==0
        report['multibox_disappeared']=collapsed if enough else None
        notes=['仅一次训练采样快照，不能代替固定验证集评测；未自动重试或修改训练。']
        if not enough:notes.append('完整训练步或合法正样本不足，不判断坍缩。')
        elif overall['valid_rate']<.95:notes.append('先分析协议非法和截断占比；不要把解析失败当成候选数减少。必要时仅调整生成预算后独立验证。')
        elif collapsed:notes.append('最近至少10个完整步的合法正样本未出现多框。当前为发现优先奖励；优先检查同输入混合组的候选收益与优势，检查已有拼图覆盖信号和有效新增候选收益，不盲目添加背景补框奖励。')
        else:notes.append('窗口内仍存在合法正样本多框，不判定已消失；按原图/拼图分开查看比例。')
        if (overall['oracle_selected_gap'] or 0)>.1:notes.append('存在较大选框差距；优先离线检查正确候选低分与错误候选高分，针对评分目标优化，不仅提高框数收益。')
        report['diagnosis']=notes
        save('report.json',report)
        (HERE/'report.md').write_text('# E-014 一次性检查\n\n'+'\n\n'.join(notes)+'\n\n```json\n'+json.dumps(report,ensure_ascii=False,indent=2)+'\n```\n')
        sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
        import surveyctl
        from survey_tool import experiments as ex
        ex.update_run(surveyctl.root_for(str(HERE.parents[3])),B['analysis_run'],{'result_analysis':'本地一次性只读分析完成；'+ '；'.join(notes)+'；完整报告 '+str(HERE/'report.json')})
    except Exception as exc:
        save('error.json',{'error_type':type(exc).__name__,'message':str(exc),'retried':False})
        raise
if __name__=='__main__':main()
