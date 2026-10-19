import json,base64,struct,html,xml.etree.ElementTree as ET
from pathlib import Path
p=Path(__file__).resolve().parents[1];cases=json.loads((p/'cases.json').read_text());mapping=json.loads((p/'image_mapping.json').read_text());summary=json.loads((p/'summary.json').read_text());(p/'figures').mkdir(exist_ok=True)
def size(path):
 data=path.read_bytes()
 if data[:8]==b'\x89PNG\r\n\x1a\n':return struct.unpack('>II',data[16:24])
 assert data[:2]==b'\xff\xd8';i=2
 while i<len(data):
  while data[i]==255:i+=1
  m=data[i];i+=1
  if m in (216,217):continue
  n=struct.unpack('>H',data[i:i+2])[0]
  if m in (192,193,194,195,197,198,199,201,202,203,205,206,207):
   h,w=struct.unpack('>HH',data[i+3:i+7]);return w,h
  i+=n
 raise ValueError('Unsupported image')
def text(x,y,s,size=20,color='#dce6f2'):return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-family="DejaVu Sans, sans-serif">{html.escape(str(s))}</text>'
def image(path,x,y,w,h):
 raw=path.read_bytes();mime='image/png' if raw[:4]==b'\x89PNG' else 'image/jpeg'
 return f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:{mime};base64,{base64.b64encode(raw).decode()}"/>'
def rect(box,color,width=3,dash=''):
 x1,y1,x2,y2=box
 return f'<rect x="{x1}" y="{y1}" width="{max(0,x2-x1)}" height="{max(0,y2-y1)}" fill="none" stroke="{color}" stroke-width="{width}" '+(f'stroke-dasharray="{dash}" ' if dash else '')+'/>'
colors=['#ffae42','#52baff','#f37bc7','#b39aff','#ffe866','#ffffff']
titles={'rescue':'Later candidate rescues localization','selection_failure':'Correct candidate exists, score selects wrong','ineffective_extra':'Extra candidates do not rescue localization','improved':'Selected IoU improves from step150 to step200','regressed':'Selected IoU regresses from step150 to step200'}
files=[]
for num,c in enumerate(cases,1):
 ref=p/mapping[c['manifest']['image_path'][0]]['local'];q=p/mapping[c['manifest']['image_path'][-1]]['local'];rw,rh=size(ref);qw,qh=size(q)
 parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="900" viewBox="0 0 1800 900">','<rect width="1800" height="900" fill="#101b2c"/>',text(25,36,f"{num:02} | {titles[c['category']]}",26),text(25,70,f"{c['step200']['dataset']} / {c['step200']['sequence']} / id={c['step200']['id']} | green dashed=GT; thick colored box=SELECTED",19)]
 parts.append(text(25,115,'Reference (annotated target)',22));scale=min(390/rw,270/rh);ox=25;oy=135
 parts.append(image(ref,ox,oy,rw*scale,rh*scale));box=c['manifest']['bbox'][0];parts.append(rect([ox+box[0]*scale,oy+box[1]*scale,ox+box[2]*scale,oy+box[3]*scale],'#50ed99',4))
 # Reference crop is context only, based on provided reference GT.
 x1,y1,x2,y2=box;pad=max(x2-x1,y2-y1)*.4;cx=max(0,x1-pad);cy=max(0,y1-pad);cw=min(rw,x2+pad)-cx;ch=min(rh,y2+pad)-cy
 parts.append(text(25,450,'Reference target crop',20));parts.append(f'<svg x="25" y="470" width="390" height="310" viewBox="{cx} {cy} {cw} {ch}">');parts.append(image(ref,0,0,rw,rh));parts.append('</svg>')
 for step,ox in [(150,445),(200,1125)]:
  row=c['step'+str(step)];scale=min(640/qw,430/qh);oy=145
  parts.append(text(ox,115,f"Step {step} | {row['candidate_count']} candidates",24));parts.append(image(q,ox,oy,qw*scale,qh*scale))
  gt=json.loads(row['target']);parts.append(rect([ox+gt[0]/1000*qw*scale,oy+gt[1]/1000*qh*scale,ox+gt[2]/1000*qw*scale,oy+gt[3]/1000*qh*scale],'#50ed99',3,'8 5'))
  for j,v in enumerate(row['candidates']):
   box=v['box'];bb=[ox+box[0]/1000*qw*scale,oy+box[1]/1000*qh*scale,ox+box[2]/1000*qw*scale,oy+box[3]/1000*qh*scale];col=colors[j%len(colors)];selected=j==row['selected_candidate_index']
   parts.append(rect(bb,col,6 if selected else 2));parts.append(text(max(ox,bb[0]),max(oy+17,bb[1]-5),f'#{j+1}'+(' SELECTED' if selected else ''),18,col))
   parts.append(text(ox,635+j*28,f"#{j+1}   score={v['score']:.2f}   IoU={v['iou']:.3f}"+('  SELECTED' if selected else ''),20,col))
  parts.append(text(ox,595,f"Selected={row['iou']:.3f}   Oracle={row['oracle_iou']:.3f}   Gap={row['oracle_iou']-row['iou']:.3f}",20))
  if not row['variable_candidate_format_valid']:parts.append(text(ox,845,'INVALID OUTPUT: candidate fields are diagnostic only',16,'#ff7777'))
 parts.append(text(25,875,'Cases deliberately selected by magnitude; not a random or representative sample. Same Query and Reference for both checkpoints.',17,'#98adc6'));parts.append('</svg>')
 name=f'figures/{num:02}-{c["category"]}-{c["index"]}.svg';svg=''.join(parts);ET.fromstring(svg);(p/name).write_text(svg);files.append((c,name))
# Standalone summary chart from all 1766 aligned samples.
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="590"><rect width="1200" height="590" fill="#101b2c"/>',text(30,45,'Discovery reward score=0.4 | step150 vs step200',28),text(30,80,'All 1766 aligned evaluation samples; multi-box = valid outputs with >1 candidate',18)]
for j,(key,label) in enumerate([('multibox_rate','Valid multi-box / all'),('selected_miou','Selected mIoU'),('oracle_miou','Oracle mIoU')]):
 y=145+j*120;parts.append(text(30,y,label,22))
 for off,step,col in [(15,'150','#52baff'),(50,'200','#ffae42')]:
  val=summary['metrics'][step][key];parts.append(f'<rect x="320" y="{y+off-20}" width="{val*700}" height="26" fill="{col}"/>');parts.append(text(330+val*700,y+off,f'{step}: {val:.4f}',18,col))
parts.append(text(30,550,'More candidates and higher Oracle IoU did not improve overall Selected IoU.',22));parts.append('</svg>');(p/'summary.svg').write_text(''.join(parts))
intro='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>E-014 多框评测对比</title><style>body{background:#101b2c;color:#e7eef8;font:17px system-ui;margin:30px auto;max-width:1600px}img{width:100%;margin:12px 0}a{color:#74caff}button{padding:10px;margin:5px;cursor:pointer}article{border-top:1px solid #40546a;padding-top:20px}p{line-height:1.65}</style><h1>E-014：step150 / step200 多框可视化</h1><p>来源：发现优先奖励 score=0.4。全部1766个样本按 dataset_index、id、target 对齐，两次清单相同。左侧为 Reference 和目标裁剪，中间/右侧为同一 Query 的两次预测。绿虚线为 GT，粗彩框为最终选框；#编号为原始候选顺序。GT 仅用于离线展示，未参与选框。</p><img src="summary.svg"><p>多框率 14.89% → 44.79%；Selected mIoU 0.6933 → 0.6917；Oracle mIoU 0.7263 → 0.7574。候选增多并未转化为整体最终定位提升。多框子集随checkpoint变化，不能当成同一批样本直接做因果比较。</p><p>案例按对应指标差值从大到小挑选，每类最多3个、不同视频序列且全局不重复，共15个。属于用于解释行为的极端案例，不代表总体分布。类别池可重叠，图中每个案例只展示一次。</p>'''
labels={'rescue':'后框成功补救','selection_failure':'找到但选错','ineffective_extra':'无效补框','improved':'训练后改善','regressed':'训练后退化'}
intro+='<nav><button onclick="filterCases(\'all\')">全部</button>'+''.join(f'<button onclick="filterCases(\'{k}\')">{v}</button>' for k,v in labels.items())+'</nav>'
for c,name in files:intro+=f'<article data-category="{c["category"]}"><h2>{labels[c["category"]]} · {html.escape(c["step200"]["sequence"])}</h2><a href="{name}" target="_blank">打开原尺寸矢量图</a><img loading="lazy" src="{name}"></article>'
intro+='''<script>function filterCases(k){document.querySelectorAll('article').forEach(x=>x.hidden=k!=='all'&&x.dataset.category!==k)}</script><p>分析与图像均由既有产物生成，未重新运行模型。完整来源、哈希及选择规则见同目录 JSON 文件。</p></html>''';(p/'index.html').write_text(intro)
print('Rendered 15 self-contained SVG case figures, summary.svg and filterable index.html')
