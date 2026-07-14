#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import html
OUT=Path(__file__).resolve().parent/'figures'
OUT.mkdir(parents=True,exist_ok=True)
FONT="Arial, 'Noto Sans CJK SC', 'PingFang SC', 'Microsoft YaHei', sans-serif"
def esc(s): return html.escape(str(s))
def chart(path,title,labels,bars,colors,ylabel,ylim,line=None,line_label='',note='',w=1150,h=650):
 left,right,top,bottom=90,40,78,150; pw=w-left-right; ph=h-top-bottom; ymin,ymax=ylim
 def y(v): return top+(ymax-v)/(ymax-ymin)*ph
 def x(i): return left+(i+.5)*pw/len(labels)
 bw=pw/len(labels)*.58
 p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>',f'<text x="{w/2}" y="38" text-anchor="middle" font-family="{FONT}" font-size="26" font-weight="700">{esc(title)}</text>']
 p += [f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+ph}" stroke="#333"/>',f'<line x1="{left}" y1="{top+ph}" x2="{left+pw}" y2="{top+ph}" stroke="#333"/>']
 for t in range(6):
  v=ymin+(ymax-ymin)*t/5; yy=y(v)
  p.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+pw}" y2="{yy:.1f}" stroke="#eee"/>')
  p.append(f'<text x="{left-10}" y="{yy+4:.1f}" text-anchor="end" font-family="{FONT}" font-size="14">{v:.2f}</text>')
 for i,(lab,v,c) in enumerate(zip(labels,bars,colors)):
  xx=x(i)-bw/2; yy=y(v); p.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{(y(0)-yy):.1f}" fill="{c}" rx="4"/>')
  p.append(f'<text x="{x(i):.1f}" y="{yy-8:.1f}" text-anchor="middle" font-family="{FONT}" font-size="15" font-weight="700">{v:.3f}</text>')
  for j,line2 in enumerate(lab.split('\n')): p.append(f'<text x="{x(i):.1f}" y="{top+ph+28+j*18:.1f}" text-anchor="middle" font-family="{FONT}" font-size="14">{esc(line2)}</text>')
 if line:
  pts=' '.join(f'{x(i):.1f},{y(v):.1f}' for i,v in enumerate(line))
  p.append(f'<polyline points="{pts}" fill="none" stroke="#2E7D32" stroke-width="3"/>')
  for i,v in enumerate(line):
   p.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="5" fill="#2E7D32"/>')
   p.append(f'<text x="{x(i):.1f}" y="{y(v)-12:.1f}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#2E7D32">{v:.3f}</text>')
  p.append(f'<text x="{left+pw-5}" y="{top+20}" text-anchor="end" font-family="{FONT}" font-size="15" fill="#2E7D32">{esc(line_label)}</text>')
 p.append(f'<text transform="translate(26,{top+ph/2}) rotate(-90)" text-anchor="middle" font-family="{FONT}" font-size="16">{esc(ylabel)}</text>')
 if note: p.append(f'<text x="{left}" y="{h-24}" font-family="{FONT}" font-size="15" fill="#555">{esc(note)}</text>')
 p.append('</svg>'); Path(path).write_text('\n'.join(p),encoding='utf-8')
labels=['baseline','p25\ncenter-out','p50\ncenter-out','p75\ncenter-out','p100\nno-repeat','p100\nrepeat','query\nshuffle']
colors=['#999','#FFCC80','#FFB74D','#FF8A65','#E57373','#BA68C8','#64B5F6']
chart(OUT/'fig6_r014b_centerout_interference_fpr.svg','R-014b：query 内部 support-token 污染的 center-out 剂量效应',labels,[0.037,0.148,0.296,0.296,0.333,0.444,0.037],colors,'neg_FPR（柱） / F1（绿线）',(0,1.08),line=[0.982,0.931,0.871,0.871,0.857,0.818,0.982],line_label='F1',note='p25/p50/p75 表示在 query object footprint 内从中心向外替换 support/reference tokens；query shuffle 为内部顺序打乱控制。')
chart(OUT/'fig7_r014b_box_size_change.svg','R-014b：support-token 污染后预测框面积变化',labels[1:],[1.142,1.319,1.419,1.516,1.440,1.095],colors[1:],'mean area ratio: intervention / baseline',(0,1.75),line=[0.667,0.667,0.704,0.704,0.741,0.556],line_label='fraction area increased',note='统计对象：same-class negative query images；面积来自模型输出框。面积比 > 1 表示预测框变大。')
# export via Chrome if available
print('wrote',OUT/'fig6_r014b_centerout_interference_fpr.svg')
print('wrote',OUT/'fig7_r014b_box_size_change.svg')
