import json,glob,os,re
from collections import defaultdict,Counter

def seq(path):
 p=path.replace('\\','/').split('/')
 # frame parent: .../<sequence>/img/file or PDM variants; use parent before img/images
 for key in ('img','imgs','images','frame','frames'):
  if key in p:
   i=len(p)-1-p[::-1].index(key)
   if i>0:return '/'.join(p[:i])
 return '/'.join(p[:-1])
def identity(rec, idx): return seq(rec['image_path'][idx])
for f in sorted(glob.glob('/home/featurize/work/mechanism/iplocid/iplocid/data/*T2*.json')):
 x=json.load(open(f)); assert isinstance(x,list)
 qmap=defaultdict(list); tuples=[]; malformed=0
 for ri,r in enumerate(x):
  paths=r.get('image_path',[]); roles=r.get('role',[])
  if len(paths)!=len(roles):malformed+=1;continue
  refs=[i for i,z in enumerate(roles) if z=='reference']
  qs=[i for i,z in enumerate(roles) if z!='reference']
  refids=tuple(sorted(set(identity(r,i) for i in refs)))
  for qi in qs:
   qmap[paths[qi]].append((ri,roles[qi],refids,identity(r,qi)))
   tuples.append((paths[qi],roles[qi],refids,identity(r,qi)))
 repeated={q:v for q,v in qmap.items() if len(v)>1}
 diffref={q:v for q,v in repeated.items() if len(set(z[2] for z in v))>1}
 # candidate explicit bidirectional requires same query path with >=2 ref identities and each reference identity corresponds to a labeled query identity/candidate.
 # Manifest has only one bbox per image path, so at minimum detect same query reused under two refs with opposite/positive roles.
 reciprocal=[]
 for q,v in diffref.items():
  for a in v:
   for b in v:
    if a>=b:continue
    if a[2]!=b[2]:reciprocal.append((q,a,b))
 print(json.dumps({'file':os.path.basename(f),'records':len(x),'malformed':malformed,'query_entries':len(tuples),'unique_query_paths':len(qmap),'repeated_query_paths':len(repeated),'query_paths_with_distinct_reference_sets':len(diffref),'potential_reference_switch_pairs':len(reciprocal),'max_annotations_per_query_path':max(map(len,qmap.values()),default=0)},ensure_ascii=False))
 if diffref:
  for q,v in list(diffref.items())[:2]: print(' EXAMPLE',q,v)
