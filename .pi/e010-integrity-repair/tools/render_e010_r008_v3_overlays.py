#!/usr/bin/env python3
"""Render-only R-008 v3 original-image attention overlays.

Replays selected immutable natural responses, verifies their saved row/span
contract, and renders only; it never rewrites v3 metrics, heads, or summaries.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from iplocid.attention.spans import locate_image_spans
from iplocid.inference.images import load_and_resize_image
from iplocid.inference.replay import prediction_rows
from iplocid.models.qwen import load_qwen3vl_with_lora
from iplocid.pipelines.e010_integrity import load_and_validate_r003_query_heads, load_and_validate_r006_t003_reference_heads, normalize_and_aggregate_heads
from iplocid.pipelines.full_lasot_role_audit import _inputs, head_tuple
from iplocid.pipelines.role_audit_pipeline import token_ids_with_offsets, unique_subsequence

READOUTS=(("q_to_q","Query Top5 → Query","query","query"),("q_to_r","Query Top5 → Reference","reference","query"),("rheads_t003_on_qbbox_to_reference","T-003 Reference Top5 → Reference","reference","reference"))
def load(p): return json.loads(Path(p).read_text())
def rgba(a):
 a=np.asarray(a,float); x=(a-a.min())/(a.max()-a.min()+1e-15); z=plt.get_cmap("turbo")(x); z[...,3]=.72*np.sqrt(x); return z
def draw(ax,img,m,title,box,score):
 layer=Image.fromarray(np.uint8(rgba(m)*255),"RGBA").resize(img.size,Image.Resampling.BILINEAR)
 ax.imshow(img); ax.imshow(layer); x1,y1,x2,y2=box; ax.add_patch(plt.Rectangle((x1,y1),x2-x1,y2-y1,fill=False,edgecolor="lime",linewidth=2.4)); y,x=np.unravel_index(int(np.argmax(m)),m.shape); ax.plot((x+.5)/m.shape[1]*img.width,(y+.5)/m.shape[0]*img.height,"wx",ms=7,mew=1.8); ax.set_title(f"{title}\npoint={score['pointing']} S30={score['s30_iou']:.3f} L4={score['largest4n_iou']:.3f}",fontsize=9); ax.axis("off")
def map_for(result, layer, head, rows, span): return result.attentions[layer][0,head,rows,span.start:span.end].float().mean(0).cpu().numpy().reshape(span.merged_h,span.merged_w)
def replay_maps(model,processor,row,record,c,heads):
 ref,query,rs,qs,messages,_=_inputs(model,processor,row,c); text=record['natural']['response']; close=text.find(']'); rendered=processor.apply_chat_template(messages+[{"role":"assistant","content":[{"type":"text","text":text}]}],tokenize=False,add_generation_prompt=False); inputs=processor(text=[rendered],images=[ref,query],videos=None,padding=True,return_tensors="pt").to(next(model.parameters()).device); tok=processor.tokenizer; spans=locate_image_spans(inputs.input_ids,inputs.image_grid_thw,int(tok.convert_tokens_to_ids("<|image_pad|>")),int(model.config.vision_config.spatial_merge_size)); ids=inputs.input_ids[0].tolist(); start=rendered.rfind(text); pos=unique_subsequence(ids,token_ids_with_offsets(tok,rendered,start,start+close+1),spans[1].end,len(ids)); rows=prediction_rows(pos); saved=record['row_span_contract']
 if rows!=saved['prediction_rows'] or len(rows)!=saved['row_count'] or [spans[0].start,spans[0].end]!=saved['reference_span'] or [spans[1].start,spans[1].end]!=saved['query_span']: raise RuntimeError(f"row/span mismatch index={record['index']}")
 if hashlib.sha256(text.encode()).hexdigest()!=saved['response_text_sha256']: raise RuntimeError("response hash mismatch")
 with torch.inference_mode(): result=model(**inputs,output_attentions=True,return_dict=True)
 output=[]
 for key,title,span_name,family in READOUTS:
  span=spans[1] if span_name=='query' else spans[0]; maps=[map_for(result,*head_tuple(n),rows,span) for n in heads[family]['5']]; output.append((key,title,query if span_name=='query' else ref,normalize_and_aggregate_heads(maps),[x*qs for x in row['bbox'][1]] if span_name=='query' else [x*rs for x in row['bbox'][0]]))
 return output
def main():
 p=argparse.ArgumentParser(); p.add_argument('--config',required=True); p.add_argument('--count-per-outcome',type=int,default=6); a=p.parse_args(); c=load(a.config); stage=Path(c['run_dir'])/'staging'/'iplocid.e010.full-lasot-frozen-query-and-reference-top5_v3'; records=[load_line for load_line in map(json.loads,(stage/'per_image.jsonl').read_text().splitlines())]; manifest=load(Path(c['run_dir'])/'manifests/full_manifest.json'); q=load_and_validate_r003_query_heads(c['query_head_authority']); r,_=load_and_validate_r006_t003_reference_heads(c['reference_head_authority']); heads={'query':q,'reference':r}; selected=[x for outcome in ('correct','error') for x in [z for z in records if z['cohort']=='evaluation' and z['outcome']==outcome][:a.count_per_outcome]]; out=stage/'visualizations'/'original_attention_overlays'; out.mkdir(parents=True,exist_ok=True); model,processor=load_qwen3vl_with_lora(c['model_path'],c['lora_path'],max_memory={0:'22GiB',1:'22GiB'}); rendered=[]
 for rec in selected:
  panels=replay_maps(model,processor,manifest[rec['index']],rec,c,heads); fig,axes=plt.subplots(1,3,figsize=(15,5),constrained_layout=True)
  for ax,(key,title,img,m,box) in zip(axes,panels): draw(ax,img,m,title,box,rec['scores'][key]['top5'])
  fig.suptitle(f"R-008 v3 | {rec['outcome']} | evaluation | {rec['sequence']} | natural Query-bbox p−1 rows; green=GT, white x=argmax; per-panel visual normalization",fontsize=11); path=out/f"{rec['outcome']}_{rec['index']:04d}_{rec['sequence'].replace('/','_')}.png"; fig.savefig(path,dpi=170); plt.close(fig); rendered.append({'index':rec['index'],'sequence':rec['sequence'],'outcome':rec['outcome'],'file':str(path),'readouts':[x[0] for x in panels],'row_contract_verified':True})
 (out/'manifest.json').write_text(json.dumps({'schema':'iplocid.e010.r008.v3.original-overlay/v1','source_stage':str(stage),'count_per_outcome':a.count_per_outcome,'records':rendered,'metrics_or_heads_changed':False,'normalization':'per-panel min-max only for display'},indent=2)+'\n'); print(json.dumps({'rendered':len(rendered),'dir':str(out)}))
if __name__=='__main__': main()
