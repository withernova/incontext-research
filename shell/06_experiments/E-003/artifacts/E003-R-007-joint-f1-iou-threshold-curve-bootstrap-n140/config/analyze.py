#!/usr/bin/env python3
import argparse,csv,hashlib,json,math,shutil
from pathlib import Path
import numpy as np

def f1(tp,fp,fn):
    d=2*tp+fp+fn
    return np.divide(2*tp,d,out=np.zeros_like(np.asarray(d,dtype=float)),where=np.asarray(d)!=0)

def q(a):
    return np.percentile(a,[2.5,50,97.5],axis=0)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--source-summary',required=True);ap.add_argument('--out',required=True);ap.add_argument('--seed',type=int,default=20260721);ap.add_argument('--replicates',type=int,default=10000);a=ap.parse_args()
    out=Path(a.out)
    for d in ['config','logs','analysis','results','visualizations','manifests']: (out/d).mkdir(parents=True,exist_ok=True)
    raw=json.load(open(a.source)); records=raw['outputs']
    assert len(records)==280
    by={}
    for r in records:
        sid=int(r['sample']); by.setdefault(sid,{})
        role='positive' if r['role']=='positive-image' else 'negative' if r['role'] in ('inclass-image','outclass-image') else None
        assert role and role not in by[sid],(sid,role)
        by[sid][role]=r
    ids=sorted(by);assert len(ids)==140 and all(set(by[i])=={'positive','negative'} for i in ids)
    pos_yes=np.array([by[i]['positive']['confusion']=='TP' for i in ids],bool)
    neg_yes=np.array([by[i]['negative']['confusion']=='FP' for i in ids],bool)
    iou=np.array([float(by[i]['positive']['iou_raw']) for i in ids],float);assert np.isfinite(iou).all() and ((iou>=0)&(iou<=1+1e-6)).all()
    thresholds=np.round(np.arange(101)/100,2)
    qual=pos_yes[:,None] & (iou[:,None]>=thresholds[None,:])
    tp=qual.sum(0);fn=140-tp;fp=np.repeat(neg_yes.sum(),101);tn=140-fp
    jf=f1(tp,fp,fn);rec=tp/140
    accepted_below=(pos_yes[:,None] & (iou[:,None]<thresholds[None,:])).sum(0)
    id_tp=int(pos_yes.sum());id_fn=140-id_tp;id_fp=int(neg_yes.sum());id_tn=140-id_fp;id_f1=float(f1(np.array(id_tp),np.array(id_fp),np.array(id_fn)))
    # clustered bootstrap via multinomial counts over 140 clusters; batches keep memory bounded
    rng=np.random.default_rng(a.seed);B=a.replicates
    b_id=np.empty(B);b_joint=np.empty((B,101),np.float32);b_rec=np.empty((B,101),np.float32);b_gap=np.empty((B,101),np.float32);b_accbelow=np.empty((B,101),np.float32)
    batch=250
    for st in range(0,B,batch):
        en=min(B,st+batch);idx=rng.integers(0,140,size=(en-st,140))
        py=pos_yes[idx].sum(1);ny=neg_yes[idx].sum(1)
        qq=qual[idx,:].sum(1)
        bid=f1(py,ny,140-py);bj=f1(qq,ny[:,None],140-qq)
        b_id[st:en]=bid;b_joint[st:en]=bj;b_rec[st:en]=qq/140;b_gap[st:en]=bid[:,None]-bj
        b_accbelow[st:en]=(pos_yes[idx,None] & (iou[idx,None]<thresholds[None,None,:])).sum(1)/140
    id_ci=q(b_id);jci=q(b_joint);rci=q(b_rec);gci=q(b_gap);aci=q(b_accbelow)
    rows=[]
    for k,t in enumerate(thresholds):
        rows.append({'threshold':float(t),'TP':int(tp[k]),'TN':int(tn[k]),'FP':int(fp[k]),'FN':int(fn[k]),'joint_f1':float(jf[k]),'joint_f1_ci_low':float(jci[0,k]),'joint_f1_ci_median':float(jci[1,k]),'joint_f1_ci_high':float(jci[2,k]),'positive_joint_recall':float(rec[k]),'positive_joint_recall_ci_low':float(rci[0,k]),'positive_joint_recall_ci_high':float(rci[2,k]),'accepted_below_n':int(accepted_below[k]),'accepted_below_rate_all_positive':float(accepted_below[k]/140),'accepted_below_rate_ci_low':float(aci[0,k]),'accepted_below_rate_ci_high':float(aci[2,k]),'f1_gap_vs_identification':float(id_f1-jf[k]),'f1_gap_ci_low':float(gci[0,k]),'f1_gap_ci_high':float(gci[2,k])})
    with open(out/'results'/'threshold_curve.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    json.dump(rows,open(out/'results'/'threshold_curve.json','w'),indent=2)
    np.savez_compressed(out/'results'/'bootstrap_replicates.npz',thresholds=thresholds,identification_f1=b_id,joint_f1=b_joint,positive_joint_recall=b_rec,gap=b_gap,accepted_below_rate=b_accbelow,seed=a.seed)
    h=hashlib.sha256((out/'results'/'bootstrap_replicates.npz').read_bytes()).hexdigest()
    official=json.load(open(a.source_summary))
    gates={'records_280':len(records)==280,'clusters_140':len(ids)==140,'one_positive_one_negative':all(set(by[i])=={'positive','negative'} for i in ids),'finite_iou':bool(np.isfinite(iou).all()),'tau0_equals_identification':bool(tp[0]==id_tp and fn[0]==id_fn and fp[0]==id_fp and abs(jf[0]-id_f1)<1e-12),'replicates_10000':B==10000,'registered_points_reproduced':{}}
    for t in [0.3,0.5,0.7]:
        k=int(round(t*100)); ref=official['joint_by_iou'][str(t)];ok=tp[k]==ref['TP'] and fn[k]==ref['FN'] and fp[k]==ref['FP'] and tn[k]==ref['TN'] and abs(jf[k]-ref['F1'])<1e-12;gates['registered_points_reproduced'][str(t)]=bool(ok)
    assert all(v for k,v in gates.items() if k!='registered_points_reproduced') and all(gates['registered_points_reproduced'].values())
    key={str(t):rows[int(round(t*100))] for t in [0,0.1,0.3,0.5,0.7,0.9,1.0]}
    summary={'status':'completed','run_id':out.name,'source_run':'E003-R-004b-joint-f1-iou-local-lasot-n140-t128','offline_no_model_rerun':True,'integrity_gates':gates,'data':{'clusters':140,'records':280,'positive':140,'negative':140,'split':'local deterministic LaSOT reconstruction; not official'},'identification':{'TP':id_tp,'TN':id_tn,'FP':id_fp,'FN':id_fn,'F1':id_f1,'bootstrap95':[float(id_ci[0]),float(id_ci[2])]},'curve':{'threshold_start':0.0,'threshold_end':1.0,'step':0.01,'points':101,'bootstrap_replicates':B,'seed':a.seed,'bootstrap_npz_sha256':h,'key_points':key},'interpretation':'Identification F1 is threshold-independent; Joint F1 decreases as stricter localization correctness is required. This is a local evaluation-coverage result, not a mechanism or wrong-instance estimate.','boundaries':['Local deterministic reconstruction, not official IPLoc-ID split.','Pointwise percentile bootstrap intervals over 140 paired sample clusters.','Do not subtract F1 and mIoU.','Low IoU does not by itself establish wrong-instance selection.']}
    json.dump(summary,open(out/'analysis'/'summary.json','w'),indent=2)
    # plots
    import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    plt.style.use('seaborn-v0_8-whitegrid')
    fig,ax=plt.subplots(figsize=(8,5));ax.plot(thresholds,jf,label='Joint F1@IoU',lw=2,color='#b2182b');ax.fill_between(thresholds,jci[0],jci[2],alpha=.2,color='#b2182b',label='95% clustered bootstrap CI');ax.axhline(id_f1,color='#2166ac',ls='--',lw=2,label=f'Identification F1 = {id_f1:.3f}');
    for t in [.3,.5,.7]: k=int(t*100);ax.scatter([t],[jf[k]],color='#b2182b');ax.annotate(f'{jf[k]:.3f}',(t,jf[k]),xytext=(3,-14),textcoords='offset points',fontsize=9)
    ax.set(xlabel='IoU correctness threshold',ylabel='F1',xlim=(0,1),ylim=(0,1.02),title='Identification-only vs joint identification–localization F1');ax.legend(loc='lower left');fig.tight_layout();fig.savefig(out/'visualizations'/'joint_f1_iou_threshold_curve.png',dpi=220);fig.savefig(out/'visualizations'/'joint_f1_iou_threshold_curve.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5));ax.plot(thresholds,rec,label='Positive joint recall',lw=2,color='#1b7837');ax.fill_between(thresholds,rci[0],rci[2],alpha=.2,color='#1b7837');ax.plot(thresholds,accepted_below/140,label='Yes but IoU below threshold / all positives',lw=2,color='#762a83');ax.fill_between(thresholds,aci[0],aci[2],alpha=.15,color='#762a83');ax.axhline(id_fn/140,color='#d95f02',ls='--',label='Positive decision FN rate');ax.set(xlabel='IoU correctness threshold',ylabel='Rate',xlim=(0,1),ylim=(0,1.02),title='Positive joint success and failure composition');ax.legend();fig.tight_layout();fig.savefig(out/'visualizations'/'positive_joint_failure_curve.png',dpi=220);plt.close(fig)
    pos_sorted=np.sort(iou);ecdf=np.arange(1,141)/140;fig,ax=plt.subplots(figsize=(7,5));ax.step(pos_sorted,ecdf,where='post',color='#2166ac',lw=2,label='All positive queries');tp_iou=np.sort(iou[pos_yes]);ax.step(tp_iou,np.arange(1,len(tp_iou)+1)/len(tp_iou),where='post',color='#b2182b',lw=2,label='Positive identification TP');ax.set(xlabel='Predicted/GT IoU',ylabel='Empirical CDF',xlim=(0,1),ylim=(0,1.02),title='Positive-query localization IoU distribution');ax.legend();fig.tight_layout();fig.savefig(out/'visualizations'/'positive_iou_ecdf.png',dpi=220);plt.close(fig)
    vis={'files':['joint_f1_iou_threshold_curve.png','joint_f1_iou_threshold_curve.pdf','positive_joint_failure_curve.png','positive_iou_ecdf.png'],'source':'E003-R-004b outputs','offline_no_model_rerun':True}
    json.dump(vis,open(out/'visualizations'/'manifest.json','w'),indent=2)
    shutil.copy2(a.source,out/'manifests'/'source_outputs.json');shutil.copy2(a.source_summary,out/'manifests'/'source_summary.json')
    md=f'''# E003-R-007 summary\n\nOffline analysis; no model rerun. 140 paired clusters / 280 records; 10,000 clustered bootstrap replicates, seed {a.seed}.\n\n- Identification F1: **{id_f1:.4f}**, 95% CI [{id_ci[0]:.4f}, {id_ci[2]:.4f}]\n- Joint F1@0.3: **{key['0.3']['joint_f1']:.4f}**, 95% CI [{key['0.3']['joint_f1_ci_low']:.4f}, {key['0.3']['joint_f1_ci_high']:.4f}]\n- Joint F1@0.5: **{key['0.5']['joint_f1']:.4f}**, 95% CI [{key['0.5']['joint_f1_ci_low']:.4f}, {key['0.5']['joint_f1_ci_high']:.4f}]\n- Joint F1@0.7: **{key['0.7']['joint_f1']:.4f}**, 95% CI [{key['0.7']['joint_f1_ci_low']:.4f}, {key['0.7']['joint_f1_ci_high']:.4f}]\n\nCurve points: IoU threshold 0.00–1.00 in steps of 0.01. All integrity gates passed and registered 0.3/0.5/0.7 values exactly reproduce R-004b.\n\nBoundary: local deterministic LaSOT reconstruction, not official IPLoc-ID split; evaluation-coverage evidence only.\n'''
    (out/'analysis'/'summary.md').write_text(md)
    print(json.dumps(summary))
if __name__=='__main__':main()
