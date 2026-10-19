import json,subprocess,base64,hashlib
from pathlib import Path
p=Path(__file__).resolve().parents[1];cases=json.loads((p/'cases.json').read_text());paths=sorted({f for c in cases for f in [c['manifest']['image_path'][0],c['manifest']['image_path'][-1]]})
code="import json,base64\nfrom pathlib import Path\npaths="+repr(paths)+"\nprint(json.dumps({x:base64.b64encode(Path(x).read_bytes()).decode() for x in paths}))"
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090','python3 -'],input=code,text=True,capture_output=True,check=True,timeout=180)
(p/'images').mkdir();mapping={}
for i,(path,b64) in enumerate(json.loads(r.stdout).items()):
 raw=base64.b64decode(b64);name='images/'+str(i).zfill(3)+Path(path).suffix;(p/name).write_bytes(raw);mapping[path]=dict(local=name,sha256=hashlib.sha256(raw).hexdigest())
(p/'image_mapping.json').write_text(json.dumps(mapping,indent=2));print('Downloaded',len(mapping),'source images')
