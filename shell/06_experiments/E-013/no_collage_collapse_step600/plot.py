"""Render the saved E-013 no-collage rollout diagnostics without remote access."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
d = json.loads((HERE / 'summary.json').read_text())
names = [f'{i}-{i+99}' for i in range(0, 600, 100)]
bins = [d['bins_100'][name] for name in names]
x = np.arange(len(names))

fig, ax = plt.subplots(3, 1, figsize=(9, 10), sharex=True, constrained_layout=True)
ax[0].plot(x, [b['best2_selection_rate'] * 100 for b in bins], marker='o', label='selected #2')
for i, b in enumerate(bins):
    ax[0].annotate(f"{b['best2_selection_n']}/{b['n']}",
                   (i, b['best2_selection_rate'] * 100), xytext=(0, 8),
                   textcoords='offset points', ha='center', fontsize=9)
ax[0].set_ylabel('Best-2 selected (%)')
ax[0].set_ylim(0, 23)
ax[0].grid(alpha=.25)

ax[1].plot(x, [b['delta_score_mean'] for b in bins], marker='o', label='mean')
ax[1].plot(x, [b['delta_score_median'] for b in bins], marker='s', label='median')
ax[1].axhline(0, color='black', lw=.8)
ax[1].set_ylabel('score #2 - score #1')
ax[1].legend()
ax[1].grid(alpha=.25)

ax[2].plot(x, [b['delta_score_positive_rate'] * 100 for b in bins],
           marker='o', label='score #2 > score #1')
ax[2].plot(x, [b['delta_score_tie_rate'] * 100 for b in bins],
           marker='s', label='tie')
ax[2].set_ylabel('Rollouts (%)')
ax[2].set_xticks(x, names)
ax[2].set_xlabel('Training step')
ax[2].legend()
ax[2].grid(alpha=.25)
fig.suptitle('No-collage GRPO: unique GT-best #2, valid positive rollouts')
fig.savefig(HERE / 'training_curve.png', dpi=180)
plt.close(fig)

fig, axes = plt.subplots(2, 3, figsize=(12, 6.5), sharex=True, sharey=True,
                         constrained_layout=True)
for name, b, a in zip(names, bins, axes.flat):
    edges = np.array(b['hist_delta_score_edges'])
    counts = np.array(b['hist_delta_score_counts'])
    a.bar(edges[:-1], counts / b['n'], width=np.diff(edges), align='edge',
          color='#4169a8', alpha=.85, edgecolor='white')
    a.axvline(0, color='#cf562f', lw=1.3)
    a.set_title(f'{name}: n={b["n"]}')
    a.grid(axis='y', alpha=.2)
for a in axes[-1]:
    a.set_xlabel('score #2 - score #1')
for a in axes[:, 0]:
    a.set_ylabel('Fraction')
fig.suptitle('Score margin distribution by training step')
fig.savefig(HERE / 'score_margin_hist.png', dpi=180)
plt.close(fig)

gap_names = ['0-.05', '.05-.1', '.1-.2', '>.2']
keys = ['0-0.05', '0.05-0.1', '0.1-0.2', '0.2-1.00001']
early = [d['iou_gap']['early_0_199'][k] for k in keys]
late = [d['iou_gap']['late_400_599'][k] for k in keys]
fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
w = .37
ax.bar(np.arange(4)-w/2, [v['delta_score_positive_rate']*100 for v in early],
       width=w, label='steps 0-199', color='#4169a8')
ax.bar(np.arange(4)+w/2, [v['delta_score_positive_rate']*100 for v in late],
       width=w, label='steps 400-599', color='#cf562f')
for i, (e, l) in enumerate(zip(early, late)):
    ax.text(i-w/2, e['delta_score_positive_rate']*100+1, f"n={e['n']}",
            ha='center', fontsize=8)
    ax.text(i+w/2, l['delta_score_positive_rate']*100+1, f"n={l['n']}",
            ha='center', fontsize=8)
ax.set_xticks(np.arange(4), gap_names)
ax.set_xlabel('IoU #2 - IoU #1')
ax.set_ylabel('P(score #2 > score #1) (%)')
ax.set_ylim(0, 27)
ax.legend()
ax.grid(axis='y', alpha=.2)
ax.set_title('Unique GT-best #2: ranking still fails for large IoU gaps')
fig.savefig(HERE / 'iou_gap_ranking.png', dpi=180)
plt.close(fig)

comp = d['reward_comparison']['all']
a = comp['A_s2_gt_s1']
b = comp['B_s1_gt_s2']
labels = ['Total reward', 'Selected IoU', '-Brier', '-0.5 ranking loss', 'Advantage']
value = lambda v: [v['total_mean'], v['iou_mean'], -v['brier_mean'],
                   -.5*v['ranking_loss_mean'], v['advantage_mean']]
fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
ax.bar(np.arange(5)-w/2, value(a), width=w, label=f'A: s2 > s1 (n={a["n"]})',
       color='#2d8b65')
ax.bar(np.arange(5)+w/2, value(b), width=w, label=f'B: s1 > s2 (n={b["n"]})',
       color='#ba5555')
ax.axhline(0, color='black', lw=.8)
ax.set_xticks(np.arange(5), labels, rotation=15, ha='right')
ax.set_ylabel('Mean value')
ax.legend()
ax.grid(axis='y', alpha=.2)
ax.set_title('Observed reward signal, unique GT-best #2 (descriptive)')
fig.savefig(HERE / 'reward_comparison.png', dpi=180)
plt.close(fig)
