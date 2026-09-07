import csv,numpy as np
from pathlib import Path
p=Path('/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches/20260903T084429173021Z--gt-mask-247-eval/diagnostics/case_visualizations/per_sample.csv')
r=list(csv.DictReader(p.open()))
for x in r:
 for k in ['gt_mask_iou','step1729_iou','baseline_iou','dynamic_iou']:x[k]=float(x[k])
def stat(name,sub,base):
 d=np.array([x['gt_mask_iou']-x[base] for x in sub]);g=np.array([x['gt_mask_iou'] for x in sub]);b=np.array([x[base] for x in sub])
 print(name,'n',len(sub),'base',round(b.mean(),4),'gt',round(g.mean(),4),'delta',round(d.mean(),4),'median',round(np.median(d),4),'better',sum(d>0),'worse',sum(d<0),'same',sum(d==0),'large_loss',sum(d<=-0.25),'rel_drop',round(np.mean(d[b>.5]/b[b>.5]),4) if any(b>.5) else None)
for base in ['baseline_iou','step1729_iou','dynamic_iou']:
 print('\nBASE',base)
 for label,sub in [('base=0',[x for x in r if x[base]==0]),('0<base<.25',[x for x in r if 0<x[base]<.25]),('base .25-.5',[x for x in r if .25<=x[base]<.5]),('base .5-.75',[x for x in r if .5<=x[base]<.75]),('base>=.75',[x for x in r if x[base]>=.75])]:stat(label,sub,base)
for base in ['baseline_iou','step1729_iou','dynamic_iou']:
 print('\nTRANS',base)
 for t in [.1,.25,.5,.75]:
  fail=[x for x in r if x[base]<t];rec=[x for x in fail if x['gt_mask_iou']>=t];found=[x for x in r if x[base]>=t];loss=[x for x in found if x['gt_mask_iou']<x[base]]
  print(t,'fail',len(fail),'recovered',len(rec),'rate',round(len(rec)/len(fail),3) if fail else None,'found',len(found),'degraded',len(loss),'rate',round(len(loss)/len(found),3) if found else None,'rec_delta',round(np.mean([x['gt_mask_iou']-x[base] for x in rec]),3) if rec else None,'found_delta',round(np.mean([x['gt_mask_iou']-x[base] for x in found]),3) if found else None)
print('\nTOP REL LOSSES baseline>=.5')
for x in sorted([x for x in r if x['baseline_iou']>=.5],key=lambda x:(x['gt_mask_iou']-x['baseline_iou'])/x['baseline_iou'])[:15]:print(x['dataset_index'],x['sequence'],round(x['baseline_iou'],3),round(x['gt_mask_iou'],3),round(x['gt_mask_iou']-x['baseline_iou'],3),round((x['gt_mask_iou']-x['baseline_iou'])/x['baseline_iou'],3))
