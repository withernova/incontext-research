"""E010-R-008 full-LaSOT replay scorer. Natural records are immutable inputs."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from types import SimpleNamespace
import numpy as np, torch
from iplocid.attention.metrics import area_normalized_enrichment, fractional_mass, fractional_token_iou, pointing_hit, retained_mass_support
from iplocid.attention.spans import locate_image_spans
from iplocid.inference.images import load_and_resize_image
from iplocid.inference.replay import prediction_rows
from iplocid.models.qwen import load_qwen3vl_with_lora
from iplocid.pipelines.e010_integrity import (ROW_CONTRACT, bootstrap_correct_minus_error, bootstrap_difference_in_differences, hindex, hname, layer_matched_random_sets_without_replacement, load_and_validate_r003_query_heads, load_and_validate_r006_t003_reference_heads, normalize_and_aggregate_heads, outcome_label, s30_metrics, sha256)
from iplocid.pipelines.role_audit_pipeline import occupancy, token_ids_with_offsets, unique_subsequence
from iplocid.prompts.coordinates import pixel_to_vlm_format
from iplocid.prompts.messages import build_messages
SCHEMA="iplocid.e010.full-lasot-frozen-query-and-reference-top5/v3"
READOUTS={"q_to_q":{"row_source":ROW_CONTRACT,"key_span":"query","target":"query","head_authority":"r003_query"},"q_to_r":{"row_source":ROW_CONTRACT,"key_span":"reference","target":"reference","head_authority":"r003_query"},"rheads_t003_on_qbbox_to_reference":{"row_source":ROW_CONTRACT,"key_span":"reference","target":"reference","head_authority":"r006_t003_reference","compatibility_alias":"r_to_r"}}
def sequence(row): return row['source']['sequence_cluster']
def category(row): return row['source']['category']
def load(p): return json.loads(Path(p).read_text())
def head_tuple(name): return int(name[1:].split('H')[0]),int(name.split('H')[1])
def xywh(line):
 v=[float(x) for x in re.split(r'[ ,\t]+',line.strip()) if x]; return None if len(v)<4 or v[2]<=0 or v[3]<=0 else [v[0],v[1],v[0]+v[2],v[1]+v[3]]
def deterministic_split(groups,rows,seed):
 e={};d={}
 for cls,inds in sorted(groups.items()):
  order=sorted(inds,key=lambda i:hashlib.sha256(f'{seed}:{cls}:{sequence(rows[i])}'.encode()).hexdigest()); e[cls],d[cls]=order[:10],order[10:]
 if any(len(e[x])!=10 or len(d[x])!=10 or set(e[x])&set(d[x]) for x in groups): raise RuntimeError('10/10 split contract')
 return e,d
def build_manifest(c):
 root=Path(c['dataset_root']); pairs=[(a,b) for a in sorted(root.iterdir()) if a.is_dir() for b in sorted(a.iterdir()) if b.is_dir()]; ids=[f'{a.name}/{b.name}' for a,b in pairs]
 if len(pairs)!=1400 or len({a.name for a,b in pairs})!=70 or hashlib.sha256('\n'.join(ids).encode()).hexdigest()!=c['sequence_ids_sha256']: raise RuntimeError('LaSOT 70x20 contract')
 rows=[]
 for a,b in pairs:
  valid=[(i,xywh(x)) for i,x in enumerate((b/'groundtruth.txt').read_text().splitlines()) if xywh(x)]
  (ri,rb),(qi,qb)=valid[0],valid[-1]; rows.append({'element':a.name,'image_path':[str(b/'img'/f'{ri+1:08d}.jpg'),str(b/'img'/f'{qi+1:08d}.jpg')],'bbox':[rb,qb],'source':{'category':a.name,'sequence_cluster':f'{a.name}/{b.name}','reference_line':ri+1,'query_line':qi+1}})
 return rows
def prepare(c):
 rows=build_manifest(c); groups={x:[i for i,r in enumerate(rows) if category(r)==x] for x in sorted({category(r) for r in rows})}; e,d=deterministic_split(groups,rows,c['seed']); return rows,{i for x in e.values() for i in x}
def validate_natural_records(c,rows):
 records=[json.loads(x) for x in Path(c['natural_records_path']).read_text().splitlines() if x.strip()]; by={x.get('index'):x for x in records}
 if len(records)!=1400 or len(by)!=1400 or set(by)!=set(range(1400)): raise RuntimeError('natural records require exactly unique indices 0..1399')
 for i,row in enumerate(rows):
  n=by[i]
  if n.get('sequence')!=sequence(row) or not isinstance(n.get('response'),str) or not isinstance(n.get('response_token_ids'),list): raise RuntimeError(f'natural record contract {i}')
 return by
def spatial(a,t):
 a=normalize_and_aggregate_heads([a]); support=retained_mass_support(a,.5); return {'pointing':int(pointing_hit(a,t)),'fractional_mass':fractional_mass(a,t),'enrichment':area_normalized_enrichment(a,t),'s50_fiou':fractional_token_iou(support,t),'selected_token_count_s50':int(support.sum()),**s30_metrics(a,t)}
def _inputs(model,processor,row,c):
 rp,qp=row['image_path']; ref,_,rs=load_and_resize_image(rp,c['max_side']); query,_,qs=load_and_resize_image(qp,c['max_side']); adapter=SimpleNamespace(data_path=str(Path(c['run_dir'])/'manifests/full_manifest.json')); text=str(pixel_to_vlm_format(adapter,str([x*rs for x in row['bbox'][0]]),ref.size,'NotGT',model_id=c['model_id'])); messages,_=build_messages(element=row['element'],reference_img_path=rp,ref_box_text=text,query_img_path=qp); return ref,query,rs,qs,messages,adapter
def replay_record(model,processor,row,natural,c,authorities,controls):
 ref,query,rs,qs,messages,_=_inputs(model,processor,row,c); text=natural['response']; close=text.find(']')
 if close<0: raise ValueError('natural response has no bbox close')
 rendered=processor.apply_chat_template(messages+[{'role':'assistant','content':[{'type':'text','text':text}]}],tokenize=False,add_generation_prompt=False); inputs=processor(text=[rendered],images=[ref,query],videos=None,padding=True,return_tensors='pt').to(next(model.parameters()).device); tok=processor.tokenizer; spans=locate_image_spans(inputs.input_ids,inputs.image_grid_thw,int(tok.convert_tokens_to_ids('<|image_pad|>')),int(model.config.vision_config.spatial_merge_size))
 if len(spans)!=2: raise ValueError('two image spans required')
 ids=inputs.input_ids[0].tolist(); start=rendered.rfind(text); positions=unique_subsequence(ids,token_ids_with_offsets(tok,rendered,start,start+close+1),spans[1].end,len(ids)); rows=prediction_rows(positions)
 with torch.inference_mode(): result=model(**inputs,output_attentions=True,return_dict=True)
 targets={'query':occupancy([x*qs for x in row['bbox'][1]],query.width,query.height,spans[1].merged_h,spans[1].merged_w),'reference':occupancy([x*rs for x in row['bbox'][0]],ref.width,ref.height,spans[0].merged_h,spans[0].merged_w)}; all_maps={}
 for name,spec in READOUTS.items():
  span=spans[1] if spec['key_span']=='query' else spans[0]; target=targets[spec['target']]; family='query' if spec['head_authority']=='r003_query' else 'reference'; allhead=[]; methods={}
  for layer in range(len(result.attentions)):
   for head in range(result.attentions[layer].shape[1]): allhead.append(result.attentions[layer][0,head,rows,span.start:span.end].float().mean(0).cpu().numpy().reshape(span.merged_h,span.merged_w))
  for k,names in authorities[family].items():
   maps=[result.attentions[l][0,h,rows,span.start:span.end].float().mean(0).cpu().numpy().reshape(span.merged_h,span.merged_w) for l,h in map(head_tuple,names)]; methods[f'top{k}']=spatial(normalize_and_aggregate_heads(maps),target)
   for n,m in zip(names,maps): methods[n]=spatial(m,target)
   random_scores=[spatial(normalize_and_aggregate_heads([allhead[h] for h in draw]),target) for draw in controls[name][k]]; methods[f'top{k}_random']={m:float(np.mean([x[m] for x in random_scores])) for m in random_scores[0]}
  methods['all_head_mean']=spatial(normalize_and_aggregate_heads(allhead),target); all_maps[name]=methods
 contract={'version':ROW_CONTRACT,'response_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'response_token_ids_sha256':hashlib.sha256(json.dumps(natural['response_token_ids']).encode()).hexdigest(),'bbox_token_positions':positions,'prediction_rows':rows,'row_count':len(rows),'reference_span':[spans[0].start,spans[0].end],'query_span':[spans[1].start,spans[1].end],'reference_grid':[spans[0].merged_h,spans[0].merged_w],'query_grid':[spans[1].merged_h,spans[1].merged_w]}
 return all_maps,contract
def run(c):
 rows,evaluation=prepare(c); natural=validate_natural_records(c,rows); q=load_and_validate_r003_query_heads(c['query_head_authority']); r,rauth=load_and_validate_r006_t003_reference_heads(c['reference_head_authority']); auth={'query':q,'reference':r}; controls={name:{k:layer_matched_random_sets_without_replacement(v,seed=c['seed']+ri*10000+int(k),repeats=c['random_repeats']) for k,v in auth['query' if spec['head_authority']=='r003_query' else 'reference'].items()} for ri,(name,spec) in enumerate(READOUTS.items())}
 # Explicitly stage, never overwrite v1 or an existing repaired publication.
 stage=Path(c['run_dir'])/'staging'/SCHEMA.replace('/','_'); stage.mkdir(parents=True,exist_ok=True); model,processor=load_qwen3vl_with_lora(c['model_path'],c['lora_path'],max_memory={0:'22GiB',1:'22GiB'}); per=[]; failures=[]
 for i,row in enumerate(rows):
  n=natural[i]
  try: scores,contract=replay_record(model,processor,row,n,c,auth,controls); per.append({'index':i,'sequence':sequence(row),'category':category(row),'cohort':'evaluation' if i in evaluation else 'discovery','outcome':outcome_label(n),'natural':n,'row_span_contract':contract,'scores':scores})
  except Exception as ex: failures.append({'index':i,'error':f'{type(ex).__name__}: {ex}'})
  if torch.cuda.is_available(): torch.cuda.empty_cache()
 if failures or len(per)!=1400: raise RuntimeError(f'replay integrity failure: {failures[:3]}')
 summary={'schema':SCHEMA,'status':'completed','readouts':{**READOUTS,'r_to_r':'rheads_t003_on_qbbox_to_reference'},'authority':{'query':c['query_head_authority'],'reference_t003':rauth},'integrity':{'natural_records':1400,'exact_replay_records':len(per),'replay_failures':failures,'row_contract':ROW_CONTRACT,'evaluation_records':700,'random_repeats':c['random_repeats']}}
 for cohort,ids in [('evaluation',evaluation),('all',set(range(1400)))]:
  summary[cohort]={}
  for role in READOUTS:
   rr=[x for x in per if x['index'] in ids]; block={}
   for method in rr[0]['scores'][role]:
    vals=[{'outcome':x['outcome'],**x['scores'][role][method]} for x in rr]; block[method]={'correct_minus_error':{m:bootstrap_correct_minus_error(vals,m,seed=c['seed'],repeats=c['bootstrap_repeats']) for m in ('pointing','fractional_mass','enrichment','s50_fiou','core30_hit','s30_iou','largest4n_hit','largest4n_iou')}}
   for k in ('3','5'):
    paired=[{'outcome':x['outcome'],'methods':x['scores'][role]} for x in rr]
    block[f'top{k}']['vs_random_difference_in_differences']={m:bootstrap_difference_in_differences(paired,f'top{k}',f'top{k}_random',m,seed=c['seed']+int(k),repeats=c['bootstrap_repeats']) for m in ('pointing','fractional_mass','enrichment','s50_fiou','core30_hit','s30_iou','largest4n_hit','largest4n_iou')}
   summary[cohort][role]=block
 (stage/'per_image.jsonl').write_text(''.join(json.dumps(x,allow_nan=False)+'\n' for x in per)); (stage/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n'); print('E010_R008_STAGED',stage)
def main():
 p=argparse.ArgumentParser(); p.add_argument('--config',required=True); p.add_argument('--prepare-only',action='store_true'); a=p.parse_args(); c=load(a.config)
 if a.prepare_only: rows,e=prepare(c); validate_natural_records(c,rows); load_and_validate_r003_query_heads(c['query_head_authority']); load_and_validate_r006_t003_reference_heads(c['reference_head_authority']); print('E010_R008_PREPARE_OK',len(rows),len(e),1400-len(e))
 else: run(c)
if __name__=='__main__': main()
