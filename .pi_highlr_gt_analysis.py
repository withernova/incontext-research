import json,csv,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path('/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009'); BR=ROOT/'E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches'
paths={'highlr_gtmask':BR/'20260903T162400978300Z--highlr-gt-mask-494-eval/evaluation/predictions.jsonl','gtmask247':BR/'20260903T084429173021Z--gt-mask-247-eval/evaluation/predictions.jsonl','step1729':BR/'baseline-nonft-eval/evaluation/predictions.jsonl','baseline':BR/'20260902T003556220809Z--focus-qwen3vl8b-1shot-nf4-ddp4-ft-459/evaluation/predictions.jsonl','dynamic':BR/'lr4时dynamic的valid/evaluation/predictions.jsonl'}
manifest=ROOT/'E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json'; M=json.loads(manifest.read_text())
out=BR/'20260903T162400978300Z--highlr-gt-mask-494-eval/diagnostics'; out.mkdir(parents=True,exist_ok=True)
p={k:{int((x:=json.loads(l))['dataset_index']):x for l in v.read_text().splitlines()} for k,v in paths.items()}
def box(s):
 n=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',s)];return n[-4:]
def mean(sub,k):return float(np.mean([x[k] for x in sub]))
rows=[]
for i,item in enumerate(M):
 r={'i':i,'dataset':item['dataset'],'sequence':item['sequence']}
 for k in p:r[k]=float(p[k][i]['iou']);r[k+'_box']=box(p[k][i]['prediction'])
 for k in ['step1729','baseline','dynamic','gtmask247']:r['delta_vs_'+k]=r['highlr_gtmask']-r[k]
 rows.append(r)
fields=['i','dataset','sequence','highlr_gtmask','gtmask247','step1729','baseline','dynamic','delta_vs_gtmask247','delta_vs_step1729','delta_vs_baseline','delta_vs_dynamic']
with (out/'per_sample.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{x:r[x] for x in fields} for r in rows])
def clusters(sub,key):
 # sequence-level bootstrap; note each combined entry has unique sequence often, retain exact protocol and report number
 g={}
 for r in sub:g.setdefault(r['sequence'],[]).append(r[key])
 vals=list(g.values()); rng=np.random.default_rng(20260903); z=[]
 for _ in range(10000):z.append(np.mean([v for j in rng.integers(0,len(vals),len(vals)) for v in vals[j]]))
 return [float(np.quantile(z,.025)),float(np.quantile(z,.975))],len(vals)
stats={}
for cmp in ['gtmask247','step1729','baseline','dynamic']:
 key='delta_vs_'+cmp;stats[cmp]={}
 for ds in ['ALL','LaSOT','GOT10k','TAO']:
  sub=rows if ds=='ALL' else [r for r in rows if r['dataset']==ds];d=np.array([r[key] for r in sub]);ci,n=clusters(sub,key);stats[cmp][ds]={'n':len(sub),'mean':float(d.mean()),'median':float(np.median(d)),'ci95':ci,'better':int((d>0).sum()),'worse':int((d<0).sum()),'same':int((d==0).sum()),'large_gain':int((d>=.25).sum()),'large_loss':int((d<=-.25).sum())}
strata={}
for cmp in ['gtmask247','step1729','baseline','dynamic']:
 strata[cmp]={}
 for lo,hi,label in [(0,0,'zero'),(0.000001,.25,'low'),(.25,.5,'mid'),(.5,.75,'upper_mid'),(.75,1.01,'high')]:
  sub=[r for r in rows if lo<=r[cmp]<hi]; d=np.array([r['delta_vs_'+cmp] for r in sub]);strata[cmp][label]={'n':len(sub),'base_mean':mean(sub,cmp) if sub else None,'highlr_mean':mean(sub,'highlr_gtmask') if sub else None,'delta_mean':float(d.mean()) if len(d) else None,'better':int((d>0).sum()),'worse':int((d<0).sum()),'same':int((d==0).sum())}
trans={}
for cmp in ['gtmask247','step1729','baseline','dynamic']:
 trans[cmp]={}
 for t in [.1,.25,.5,.75]:
  fail=[r for r in rows if r[cmp]<t];found=[r for r in rows if r[cmp]>=t];rec=[r for r in fail if r['highlr_gtmask']>=t];loss=[r for r in found if r['highlr_gtmask']<r[cmp]]
  trans[cmp][str(t)]={'initial_fail':len(fail),'recovered':len(rec),'recovery_rate':len(rec)/len(fail) if fail else None,'initial_found':len(found),'degraded':len(loss),'degrade_rate':len(loss)/len(found) if found else None,'mean_recovery_delta':float(np.mean([r['delta_vs_'+cmp] for r in rec])) if rec else None,'mean_found_delta':float(np.mean([r['delta_vs_'+cmp] for r in found])) if found else None}
res={'schema':'e009.highlr-gt-mask-step494-posthoc-analysis/v1','evaluation':{'n':len(rows),'mIoU':mean(rows,'highlr_gtmask'),'parse_rate':1.0,'vision_max_patch_tokens':4096},'paired_statistics':stats,'baseline_strata':strata,'threshold_transitions':trans,'limitations':['Natural-generation predictions only; no highlr attention maps in this directory.','Compared checkpoints use different training endpoints: highlr GT-mask step494 versus gtmask247 step247.','This is posthoc evaluation and does not replace fixed four-arm governance.']}
(out/'summary.json').write_text(json.dumps(res,indent=2)+'\n')
# select informative cases, excluding GT=0 and duplicates
def select(label,key,rev,pool=rows,n=8):
 for r in sorted(pool,key=lambda z:z[key],reverse=rev)[:n]:
  if not any(x[1]['i']==r['i'] for x in chosen):chosen.append((label,r))
chosen=[];valid=[r for r in rows if r['highlr_gtmask']>.25]
select('gain_vs_baseline','delta_vs_baseline',True,valid);select('loss_vs_baseline','delta_vs_baseline',False,valid);select('gain_vs_step1729','delta_vs_step1729',True,valid);select('loss_vs_step1729','delta_vs_step1729',False,valid)
with (out/'selected_cases.json').open('w') as f:json.dump([{'category':c,**{k:r[k] for k in fields}} for c,r in chosen[:24]],f,indent=2)
def render(cat,r):
 item=M[r['i']]; ref=Image.open(item['image_path'][0]).convert('RGB');q=Image.open(item['image_path'][1]).convert('RGB');d=ImageDraw.Draw(q);W,H=q.size;w=max(2,W//250);d.rectangle(item['bbox'][1],outline='lime',width=w)
 for k,c in [('step1729','cyan'),('baseline','yellow'),('dynamic','magenta'),('gtmask247','orange'),('highlr_gtmask','red')]:
  b=r[k+'_box']; x1,y1,x2,y2=[b[0]*W/1000,b[1]*H/1000,b[2]*W/1000,b[3]*H/1000];d.rectangle([min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)],outline=c,width=w)
 fig,ax=plt.subplots(1,2,figsize=(14,6));ax[0].imshow(ref);x1,y1,x2,y2=item['bbox'][0];ax[0].add_patch(plt.Rectangle((x1,y1),x2-x1,y2-y1,fill=False,color='lime',lw=3));ax[0].set_title('Reference | green=GT');ax[0].axis('off');ax[1].imshow(q);ax[1].set_title('Query | GT green, step cyan, baseline yellow, dynamic magenta, GT-mask247 orange, highlr GT-mask red',fontsize=8);ax[1].axis('off');fig.suptitle(f'{cat} idx={r["i"]} {r["dataset"]} {r["sequence"]}\nstep={r["step1729"]:.3f} baseline={r["baseline"]:.3f} dynamic={r["dynamic"]:.3f} GT247={r["gtmask247"]:.3f} highlr={r["highlr_gtmask"]:.3f}',fontsize=11);fig.tight_layout();fig.savefig(out/f'{cat}_idx{r["i"]:04d}.png',dpi=150);plt.close(fig)
for c,r in chosen[:24]:render(c,r)
fig,ax=plt.subplots(figsize=(9,5)); labs=['step1729','baseline','dynamic','gtmask247','highlr_gtmask']; vals=[mean(rows,x) for x in labs]; bars=ax.bar(labs,vals,color=['#4c78a8','#f2cf5b','#b279a2','#f28e2b','#e45756']);ax.set_ylim(.67,.705);ax.set_ylabel('mIoU');ax.set_title('Combined test mIoU');
for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.001,f'{v:.4f}',ha='center',fontsize=9)
fig.tight_layout();fig.savefig(out/'combined_miou_comparison.png',dpi=180);plt.close(fig)
print(json.dumps(res,ensure_ascii=False,indent=2))
