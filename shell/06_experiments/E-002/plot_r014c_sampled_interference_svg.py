#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import html
OUT=Path(__file__).resolve().parent/'figures'
OUT.mkdir(parents=True,exist_ok=True)
FONT="Arial, 'Noto Sans CJK SC', 'PingFang SC', 'Microsoft YaHei', sans-serif"
def esc(s): return html.escape(str(s))
def chart(path,title,labels,bars,colors,ylabel,ylim,line=None,line_label='',note='',w=1180,h=650):
    left,right,top,bottom=92,42,78,158; pw=w-left-right; ph=h-top-bottom; ymin,ymax=ylim
    def y(v): return top+(ymax-v)/(ymax-ymin)*ph
    def x(i): return left+(i+.5)*pw/len(labels)
    bw=pw/len(labels)*.58
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>',f'<text x="{w/2}" y="38" text-anchor="middle" font-family="{FONT}" font-size="26" font-weight="700">{esc(title)}</text>']
    parts += [f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+ph}" stroke="#333"/>',f'<line x1="{left}" y1="{top+ph}" x2="{left+pw}" y2="{top+ph}" stroke="#333"/>']
    for t in range(6):
        v=ymin+(ymax-ymin)*t/5; yy=y(v)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+pw}" y2="{yy:.1f}" stroke="#eee"/>')
        parts.append(f'<text x="{left-10}" y="{yy+4:.1f}" text-anchor="end" font-family="{FONT}" font-size="14">{v:.2f}</text>')
    for i,(lab,v,c) in enumerate(zip(labels,bars,colors)):
        yy=y(v); xx=x(i)-bw/2
        parts.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{y(0)-yy:.1f}" fill="{c}" rx="4"/>')
        parts.append(f'<text x="{x(i):.1f}" y="{yy-8:.1f}" text-anchor="middle" font-family="{FONT}" font-size="15" font-weight="700">{v:.3f}</text>')
        for j,line2 in enumerate(lab.split('\n')):
            parts.append(f'<text x="{x(i):.1f}" y="{top+ph+28+j*18:.1f}" text-anchor="middle" font-family="{FONT}" font-size="14">{esc(line2)}</text>')
    if line:
        pts=' '.join(f'{x(i):.1f},{y(v):.1f}' for i,v in enumerate(line))
        parts.append(f'<polyline points="{pts}" fill="none" stroke="#2E7D32" stroke-width="3"/>')
        for i,v in enumerate(line):
            parts.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="5" fill="#2E7D32"/>')
            parts.append(f'<text x="{x(i):.1f}" y="{y(v)-12:.1f}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#2E7D32">{v:.3f}</text>')
        parts.append(f'<text x="{left+pw-5}" y="{top+20}" text-anchor="end" font-family="{FONT}" font-size="15" fill="#2E7D32">{esc(line_label)}</text>')
    parts.append(f'<text transform="translate(26,{top+ph/2}) rotate(-90)" text-anchor="middle" font-family="{FONT}" font-size="16">{esc(ylabel)}</text>')
    if note:
        parts.append(f'<text x="{left}" y="{h-24}" font-family="{FONT}" font-size="15" fill="#555">{esc(note)}</text>')
    parts.append('</svg>')
    Path(path).write_text('\n'.join(parts),encoding='utf-8')

labels=['baseline','p25\nsampled','p50\nsampled','p75\nsampled','p100\nsampled\nno-repeat','p100\nsampled\nrepeat','query\nshuffle']
colors=['#999999','#FFE0A3','#FFB74D','#FF7043','#E45756','#B279A2','#64B5F6']
chart(
    OUT/'fig8_r014c_sampled_interference_fpr.svg',
    'R-014c：随机采样式 query support-token 污染仍提高 negative FP',
    labels,
    [0.074,0.222,0.259,0.259,0.444,0.296,0.074],
    colors,
    'neg_FPR（柱） / F1（绿线）',
    (0,1.08),
    line=[0.964,0.900,0.885,0.885,0.818,0.871,0.964],
    line_label='F1',
    note='R-014c：在 center-out ratio bin 内随机采样 query object slots 替换为 support/reference tokens；query shuffle 为顺序打乱控制。'
)
chart(
    OUT/'fig9_r014c_sampled_box_size_change.svg',
    'R-014c：随机 support-token 污染后预测框面积变化',
    labels[1:],
    [1.108,1.303,1.480,1.634,1.405,1.149],
    colors[1:],
    'mean area ratio: intervention / baseline',
    (0,1.85),
    line=[0.593,0.593,0.741,0.704,0.519,0.481],
    line_label='fraction area increased',
    note='统计对象：same-class negative query images；面积比 > 1 表示干预后预测框平均变大。'
)
chart(
    OUT/'fig10_r014c_sampled_box_follow.svg',
    'R-014c：预测框向 support-token 污染区域靠近的 proxy 指标',
    labels[1:5],
    [0.017,0.053,0.102,0.128],
    colors[1:5],
    'ΔIoU to contaminated region（柱）',
    (-0.02,0.16),
    line=None,
    note='ΔIoU>0 表示干预框比 baseline 更重叠污染区域；R-014c 未保存 exact pairs，此处用 actual count + center-out ranking 近似 contaminated region。',
    w=1050,h=600
)
for p in ['fig8_r014c_sampled_interference_fpr.svg','fig9_r014c_sampled_box_size_change.svg','fig10_r014c_sampled_box_follow.svg']:
    print('wrote', OUT/p)
