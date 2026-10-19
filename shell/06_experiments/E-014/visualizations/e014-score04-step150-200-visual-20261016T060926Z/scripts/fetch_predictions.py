import subprocess,json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parents[1];b=json.loads((p/'binding.json').read_text())
code="""import json
from pathlib import Path
base=Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014')
out={}
for step,rid in zip([150,200],IDS):
 p=base/rid
 out[str(step)]={'predictions':(p/'payload/evaluation/predictions.jsonl').read_text(),'metrics':(p/'payload/evaluation/metrics.json').read_text(),'manifest':(p/'inputs/manifest.json').read_text()}
print(json.dumps(out))
""".replace('IDS',repr(b['sources']))
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090','python3 -'],input=code,text=True,capture_output=True,check=True)
data=json.loads(r.stdout);(p/'sources').mkdir();hashes={}
for step,items in data.items():
 for kind,value in items.items():
  name=step+'-'+kind+('.jsonl' if kind=='predictions' else '.json');(p/'sources'/name).write_text(value);hashes[name]=hashlib.sha256(value.encode()).hexdigest()
(p/'source_hashes.json').write_text(json.dumps(hashes,indent=2))
print('Downloaded two predictions, metrics, and manifests.')
