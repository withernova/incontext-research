import json,csv,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path('/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009');BR=ROOT/'E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches'
probe=next(BR.glob('*headscreen-highlr-gtmask-step494/head_screening/screen_*/probe'),None)
if probe is None: raise SystemExit('probe not found')
art={int(p.stem.split('_')[-1]):p for p in probe.glob('rank_*/sample_*.npz')}; assert len(art)==96
M=json.loads((ROOT/'E009-real-focus-data/manifests/val_lasot_posthoc_valid96_1shot_focus.json').read_text())
E={'highlr':BR/'20260902T161705734308Z--E009-diagnostic-valid96-eval-dynamic-final/evaluation/predictions.jsonl','step1729':BR/'20260902T161428677289Z--E009-diagnostic-valid96-eval-step1729/evaluation/predictions.jsonl','gt247':BR/'20260903T093025528499Z--E009-diagnostic-valid96-eval-gt-mask-step247/evaluation/predictions.jsonl'}
# highlr valid96 eval may not exist; use step494 combined for aligned diagnostic only if present
E['highlr']=BR/'20260904T040731754696Z--E009-diagnostic-valid96-eval-highlr-gtmask-step494/evaluation/predictions.jsonl'
pred={k:{int((x:=json.loads(l))['dataset_index']):x for l in p.read_text().splitlines()} for k,p in E.items()}
out=BR/'20260904_attention_ensemble';out.mkdir(parents=True,exist_ok=True)
T=[(20,15),(20,20),(14,23)];S=[(21,10),(17,4),(17,7),(24,16),(18,15)]
def ens(a,heads):
 x=np.stack([a[l,h].astype(float) for l,h in heads]);m=x.reshape(len(heads),-1).sum(1);return x.mean(0),(x/m[:,None,None]).mean(0)
def b(s):return [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',s)][-4:]
rows=[]
for i in range(96):
 with np.load(art[i]) as z:
  a=z['q_to_r']; occ=z['reference_target']
 for role,heads in [('teacher',T),('student',S)]:
  raw,dist=ens(a,heads); 
  if role=='teacher': tm=float((raw*occ).sum())
  else: sm=float((raw*occ).sum())
 r={'i':i,'sequence':M[i]['sequence'],'step1729_iou':float(pred['step1729'][i]['iou']),'gt247_iou':float(pred['gt247'][i]['iou']),'highlr_iou':float(pred['highlr'][i]['iou']) if i in pred['highlr'] else None,'teacher_object_mass':tm,'student_object_mass':sm}
 r['highlr_delta_step']=None if r['highlr_iou'] is None else r['highlr_iou']-r['step1729_iou'];rows.append(r)
# categories based on gt247 versus step; highlr attention itself remains valid regardless of natural highlr eval availability.
chosen=[]
for label,key,rev in [('recovered_step','gt247_iou',True),('degraded_step','gt247_iou',False)]:
 pool=sorted(rows,key=lambda x:x[key]-x['step1729_iou'],reverse=rev)
 for r in pool:
  if not any(x['i']==r['i'] for x in chosen):chosen.append(r|{'category':label})
  if sum(x.get('category')==label for x in chosen)>=6:break
# add high attention extremes
for label,key,rev in [('high_student_mass','student_object_mass',True),('low_student_mass','student_object_mass',False)]:
 for r in sorted(rows,key=lambda x:x[key],reverse=rev)[:6]:
  if not any(x['i']==r['i'] for x in chosen):chosen.append(r|{'category':label})
(out/'summary.json').write_text(json.dumps({'probe':str(probe),'samples':96,'heads':{'teacher':T,'student':S},'selected_cases':chosen},indent=2)+'\n')
def overlay(ax,img,h,title,bbox):
 q=h/h.max() if h.max()>0 else h; q=np.asarray(Image.fromarray((q*255).astype('uint8')).resize(img.size,Image.Resampling.BILINEAR))/255.;ax.imshow(img);ax.imshow(q,cmap='magma',alpha=.55,vmin=0,vmax=1);x1,y1,x2,y2=bbox;ax.add_patch(plt.Rectangle((x1,y1),x2-x1,y2-y1,fill=False,color='lime',lw=2));ax.set_title(title,fontsize=8);ax.axis('off')
for r in chosen:
 i=r['i'];item=M[i];ref=Image.open(item['image_path'][0]).convert('RGB');fig,ax=plt.subplots(2,3,figsize=(15,9));ax[0,0].imshow(ref);x1,y1,x2,y2=item['bbox'][0];ax[0,0].add_patch(plt.Rectangle((x1,y1),x2-x1,y2-y1,fill=False,color='lime',lw=2));ax[0,0].set_title('Reference GT');ax[0,0].axis('off');q=Image.open(item['image_path'][1]).convert('RGB');d=ImageDraw.Draw(q);W,H=q.size
 for k,c in [('step1729','cyan'),('gt247','orange')]:
  if i in pred[k]:
   x=b(pred[k][i]['prediction']);d.rectangle([min(x[0]*W/1000,x[2]*W/1000),min(x[1]*H/1000,x[3]*H/1000),max(x[0]*W/1000,x[2]*W/1000),max(x[1]*H/1000,x[3]*H/1000)],outline=c,width=max(2,W//250))
 ax[1,0].imshow(q);ax[1,0].set_title(f'Query | GT green, step cyan, GT247 orange');ax[1,0].axis('off')
 with np.load(art[i]) as z:a=z['q_to_r'];occ=z['reference_target']
 for ri,(role,heads) in enumerate([('Reference Top-3',T),('Query Top-5',S)]):
  raw,dist=ens(a,heads); overlay(ax[ri,1],ref,dist,f'HighLR {role} avg\nobj={(raw*occ).sum():.4g}',item['bbox'][0])
  overlay(ax[ri,2],q,dist,f'HighLR {role} on Query coords\n(for spatial comparison)',item['bbox'][1])
 fig.suptitle(f"{r['category']} idx={i} {item['sequence']} | step1729={r['step1729_iou']:.3f}, GT247={r['gt247_iou']:.3f}, highLR combined-not-aligned={r['highlr_iou']}",fontsize=11);fig.tight_layout();fig.savefig(out/f'{r["category"]}_idx{i:03d}.png',dpi=150);plt.close(fig)
print(json.dumps({'out':str(out),'probe':str(probe),'n_images':len(chosen)},ensure_ascii=False))
