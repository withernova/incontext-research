"""读取同一评测预测，核对生成序号、横向位置和GT位置的关系。"""
import json,pathlib,subprocess
remote=r'''
import json,math,hashlib
from pathlib import Path
p=Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/payload/evaluation/predictions.jsonl')
raw=p.read_bytes();rows=[json.loads(x) for x in raw.splitlines() if x.strip()]
def box(value):
    if isinstance(value,str):
        try:value=json.loads(value)
        except (ValueError,TypeError):return None
    if not isinstance(value,list) or len(value)!=4:return None
    if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in value):return None
    if not (0<=value[0]<value[2]<=1000 and 0<=value[1]<value[3]<=1000):return None
    return value
cx=lambda b:(b[0]+b[2])/2
valid=[(r,box(r.get('target'))) for r in rows if box(r.get('target')) is not None]
groups={}
for name,items in [('gt_center_x_lt_500',[(r,t) for r,t in valid if cx(t)<500]),('gt_center_x_ge_500',[(r,t) for r,t in valid if cx(t)>=500])]:
    n=len(items)
    groups[name]={'samples':n,'first_miou':sum(float(r.get('first_candidate_iou') or 0) for r,t in items)/n,'selected_miou':sum(float(r.get('iou') or 0) for r,t in items)/n,'oracle_miou':sum(float(r.get('oracle_iou') or 0) for r,t in items)/n,'first_iou_ge_05_count':sum(float(r.get('first_candidate_iou') or 0)>=.5 for r,t in items),'second_iou_ge_05_count':sum(len(r.get('candidates') or [])>=2 and r['candidates'][1]['iou']>=.5 for r,t in items)}
centers=[[cx(r['candidates'][i]['box']) for r in rows if len(r.get('candidates') or [])>i] for i in range(2)]
positions={}
for i,v in enumerate(centers):
    ordered=sorted(v)
    positions['candidate_'+str(i+1)]={'samples':len(v),'mean_center_x':sum(v)/len(v),'median_center_x':ordered[len(v)//2],'center_x_ge_500_count':sum(x>=500 for x in v),'center_x_ge_850_count':sum(x>=850 for x in v),'center_x_ge_900_count':sum(x>=900 for x in v)}
pairs=[r['candidates'] for r in rows if len(r.get('candidates') or [])==2]
audit={'source_predictions_sha256':hashlib.sha256(raw).hexdigest(),'coordinate_scale':1000,'samples':len(rows),'valid_gt_count':len(valid),'invalid_gt_count':len(rows)-len(valid),'by_gt_image_half':groups,'prediction_positions':positions,'pairs_in_left_to_right_order':sum(cx(c[0]['box'])<=cx(c[1]['box']) for c in pairs),'pair_count':len(pairs),'interpretation_limit':'GT图像左/右半区不等于多实例空间排名。当前1766原测试集不能替代AB/BA拼图专项评测。'}
print(json.dumps(audit,ensure_ascii=False,indent=2))
'''
result=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090','python3 -'],input=remote,text=True,capture_output=True)
if result.returncode:print(result.stderr[-1500:]);raise SystemExit(result.returncode)
audit=json.loads(result.stdout)
expected=json.loads(pathlib.Path('.pi/analysis/e014/e014-bonus05-step350-eval-r2/final_integrity_audit.json').read_text())['predictions_sha256']
assert audit['source_predictions_sha256']==expected
p=pathlib.Path('.pi/analysis/e014/e014-bonus05-step350-eval-r2/spatial_candidate_audit.json')
with p.open('x') as f:json.dump(audit,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(audit,ensure_ascii=False,indent=2))
