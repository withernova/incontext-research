import json,glob,os
from collections import defaultdict

def seq(p):
 z=p.replace('\\','/').split('/')
 for key in ('img','imgs','images','frames'):
  if key in z:
   i=len(z)-1-z[::-1].index(key);return '/'.join(z[:i])
 return '/'.join(z[:-1])
for f in sorted(glob.glob('/home/featurize/work/mechanism/iplocid/iplocid/data/*T2*.json')):
 x=json.load(open(f)); edges=[]; ownpos=set(); records=[]
 for ri,r in enumerate(x):
  refs=[i for i,v in enumerate(r['role']) if v=='reference']; negs=[i for i,v in enumerate(r['role']) if v in ('inclass-image','outclass-image')]; poss=[i for i,v in enumerate(r['role']) if v=='positive-image']
  refids=set(seq(r['image_path'][i]) for i in refs)
  if len(refids)!=1: continue
  A=next(iter(refids))
  for i in poss: ownpos.add((A,seq(r['image_path'][i])))
  for i in negs: edges.append((A,seq(r['image_path'][i]),ri,r['role'][i],r.get('element')))
 eset={(a,b) for a,b,*_ in edges}; reciprocal_unordered=set(); reciprocal_details=[]
 for a,b,ri,role,el in edges:
  if a!=b and (b,a) in eset:
   key=tuple(sorted((a,b)))
   reciprocal_unordered.add(key)
 # all edges where negative identity has own positive/reference record in manifest
 ids_as_ref={a for a,b,*_ in edges}; switchable=[e for e in edges if e[1] in ids_as_ref]
 print(os.path.basename(f),json.dumps({'records':len(x),'negative_edges':len(edges),'distinct_edges':len(eset),'negative_target_is_also_reference_identity':len(switchable),'reciprocal_identity_pairs':len(reciprocal_unordered)},ensure_ascii=False))
 for pair in list(sorted(reciprocal_unordered))[:2]:
  print(' RECIP',pair)
