#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""无第三方依赖：生成 E-001/E-002 token 干预结果的 SVG 图，便于组会展示。"""
from pathlib import Path
import html

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "Arial, 'Noto Sans CJK SC', 'PingFang SC', 'Microsoft YaHei', sans-serif"

def esc(s): return html.escape(str(s))

def svg_bar_chart(path, title, labels, values, colors, ylabel="数值", ylim=None, baseline_lines=None, line_series=None, note=None, width=1100, height=650):
    if ylim is None:
        ymin = min(0, min(values)); ymax = max(values) * 1.15 if max(values) > 0 else 1
    else:
        ymin, ymax = ylim
    left, right, top, bottom = 90, 35, 80, 155
    plot_w, plot_h = width-left-right, height-top-bottom
    def y(v): return top + (ymax-v)/(ymax-ymin)*plot_h
    def x(i): return left + (i+0.5)*plot_w/len(labels)
    bw = plot_w/len(labels)*0.62
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           f'<rect width="100%" height="100%" fill="white"/>',
           f'<text x="{width/2}" y="36" text-anchor="middle" font-family="{FONT}" font-size="26" font-weight="700">{esc(title)}</text>']
    # axes
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#333"/>')
    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#333"/>')
    # ticks
    for t in range(6):
        val = ymin + (ymax-ymin)*t/5
        yy=y(val)
        parts.append(f'<line x1="{left-5}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="#333"/>')
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+plot_w}" y2="{yy:.1f}" stroke="#eee"/>')
        parts.append(f'<text x="{left-10}" y="{yy+4:.1f}" text-anchor="end" font-family="{FONT}" font-size="14">{val:.2f}</text>')
    if baseline_lines:
        for val, lab, col in baseline_lines:
            yy=y(val)
            parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+plot_w}" y2="{yy:.1f}" stroke="{col}" stroke-dasharray="7,5"/>')
            parts.append(f'<text x="{left+plot_w-5}" y="{yy-6:.1f}" text-anchor="end" font-family="{FONT}" font-size="14" fill="{col}">{esc(lab)}</text>')
    # bars
    for i,(lab,v,c) in enumerate(zip(labels, values, colors)):
        xx=x(i)-bw/2
        yy=y(max(v,0)); y0=y(0); h=abs(y(v)-y(0))
        if v < 0: yy=y(0)
        parts.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{c}" rx="4"/>')
        parts.append(f'<text x="{x(i):.1f}" y="{(yy-8 if v>=0 else yy+h+18):.1f}" text-anchor="middle" font-family="{FONT}" font-size="15" font-weight="700">{v:.3f}</text>')
        # multiline labels
        for j,line in enumerate(str(lab).split('\n')):
            parts.append(f'<text x="{x(i):.1f}" y="{top+plot_h+28+j*18:.1f}" text-anchor="middle" font-family="{FONT}" font-size="14">{esc(line)}</text>')
    if line_series:
        for series_label, vals, col in line_series:
            pts = ' '.join(f'{x(i):.1f},{y(v):.1f}' for i,v in enumerate(vals))
            parts.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"/>')
            for i,v in enumerate(vals):
                parts.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="5" fill="{col}"/>')
                parts.append(f'<text x="{x(i):.1f}" y="{y(v)-12:.1f}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{col}">{v:.3f}</text>')
            parts.append(f'<text x="{left+plot_w-5}" y="{top+22}" text-anchor="end" font-family="{FONT}" font-size="15" fill="{col}">{esc(series_label)}</text>')
    parts.append(f'<text transform="translate(24,{top+plot_h/2}) rotate(-90)" text-anchor="middle" font-family="{FONT}" font-size="16">{esc(ylabel)}</text>')
    if note:
        parts.append(f'<text x="{left}" y="{height-24}" font-family="{FONT}" font-size="15" fill="#555">{esc(note)}</text>')
    parts.append('</svg>')
    Path(path).write_text('\n'.join(parts), encoding='utf-8')

# Figure 1
svg_bar_chart(
    OUT/'fig1_e001_container_expansion.svg',
    'E-001：向外复制 object tokens 会扩大预测框',
    ['面积比\n干预/基线', '面积增大\n比例', 'IoU\n变化'],
    [1.222, 0.591, -0.083],
    ['#4C78A8','#72B7B2','#E45756'],
    ylim=(-0.18,1.35),
    baseline_lines=[(1.0,'面积比=1','#777')],
    note='R-004c：60 个 COCO visual-prompt 样本；面积比 1.222，59.1% 样本预测框变大。',
    width=900, height=560)

# Figure 2 R014 dose
svg_bar_chart(
    OUT/'fig2_r014_contamination_dose.svg',
    'R-014：support-token contamination 的剂量效应',
    ['baseline','p25\nno-repeat','p50\nno-repeat','p75\nno-repeat','p100\nno-repeat','p100\nrepeat','query\nshuffle'],
    [0.148,0.259,0.259,0.407,0.444,0.444,0.000],
    ['#9E9E9E','#FFCC80','#FFB74D','#FF8A65','#E57373','#BA68C8','#64B5F6'],
    ylabel='neg_FPR（柱） / F1（绿线）', ylim=(0,1.08),
    line_series=[('F1',[0.931,0.885,0.885,0.831,0.818,0.818,0.981],'#2E7D32')],
    note='no-repeat：support tokens 不重复使用；其余 query object tokens 保留。',
    width=1150, height=630)

# Figure 3 comparison
svg_bar_chart(
    OUT/'fig3_e002_fpr_comparison.svg',
    'E-002：reference-like token contamination 远强于 object-order shuffle',
    ['R-012\nreplace full','R-014\np100 no-repeat','R-014\np100 repeat','R-014\nquery shuffle','R-015\nsupport shuffle','R-015\nquery shuffle','R-015\nsupport+query','R-015\nfull visual'],
    [0.481,0.444,0.444,0.000,0.037,0.037,0.037,1.000],
    ['#D62728','#E45756','#B279A2','#4C78A8','#F58518','#54A24B','#72B7B2','#000000'],
    ylabel='negative false positive rate', ylim=(0,1.12),
    baseline_lines=[(0.074,'R-015 baseline=0.074','#777')],
    width=1250, height=660)

# Figure 4 R015 grouped as two charts simplified
svg_bar_chart(
    OUT/'fig4_r015_support_query_shuffle.svg',
    'R-015：support-only / query-only shuffle 均未破坏 POIL',
    ['baseline','support\nshuffle','query\nshuffle','support+query\nshuffle','full visual\nshuffle'],
    [0.074,0.037,0.037,0.037,1.000],
    ['#9E9E9E','#F58518','#54A24B','#72B7B2','#000000'],
    ylabel='neg_FPR（柱） / F1（蓝线）', ylim=(0,1.12),
    line_series=[('F1',[0.964,0.982,0.982,0.982,0.667],'#4C78A8')],
    width=1000, height=610)

# Figure 5 synthesis slide
w,h=1250,560
items=[
    ('Container expansion','E-001 R-004c：外圈复制 token → 面积比 1.222，59.1% 样本预测框变大','#4C78A8'),
    ('Order shuffle','R-015：support/query/support+query shuffle 的 neg_FPR 均为 0.037；不是主导机制','#72B7B2'),
    ('Reference-like contamination','R-014：no-repeat contamination 将 neg_FPR 从 0.148 提高到 0.444','#E45756'),
    ('Global structure','R-011/R-015：full visual shuffle 的 neg_FPR = 1.000，negative rejection 崩溃','#000000'),
]
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="{w/2}" y="44" text-anchor="middle" font-family="{FONT}" font-size="28" font-weight="700">当前证据链：containerized reference-matching</text>']
y=105
for title,text,col in items:
    parts.append(f'<rect x="45" y="{y}" width="300" height="62" rx="8" fill="{col}"/>')
    parts.append(f'<text x="195" y="{y+39}" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="700" fill="white">{esc(title)}</text>')
    parts.append(f'<text x="380" y="{y+39}" font-family="{FONT}" font-size="20" fill="#111">{esc(text)}</text>')
    y += 88
parts.append(f'<text x="55" y="505" font-family="{FONT}" font-size="22" font-weight="700">结论：POIL 对 object-internal token order shuffle 相对鲁棒；但对全局视觉结构和 query object container 中的 support/reference-like evidence 高度敏感。</text>')
parts.append('</svg>')
(OUT/'fig5_synthesis_slide.svg').write_text('\n'.join(parts), encoding='utf-8')

# Index HTML for quick preview
html_index=['<html><head><meta charset="utf-8"><title>E-002 figures</title></head><body style="font-family:sans-serif">','<h1>E-001/E-002 token intervention figures</h1>']
for p in sorted(OUT.glob('fig*.svg')):
    html_index.append(f'<h2>{p.name}</h2><img src="{p.name}" style="max-width:100%;border:1px solid #ddd">')
html_index.append('</body></html>')
(OUT/'index.html').write_text('\n'.join(html_index), encoding='utf-8')
print('Wrote SVG figures to:', OUT)
for p in sorted(OUT.glob('fig*.svg')):
    print(p)
print('Preview:', OUT/'index.html')
