"""E-009：已有预测的只读、探索性配对曲线诊断；不启动模型或修改治理状态。"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SOURCES = {
    'parent1729': 'baseline-nonft-eval',
    'baseline494': '20260902T003556220809Z--focus-qwen3vl8b-1shot-nf4-ddp4-ft-459',
    'gt247': '20260903T084429173021Z--gt-mask-247-eval',
    'high494': '20260903T162400978300Z--highlr-gt-mask-494-eval',
}
REMOTE_ROOT = '/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches'

# 图中文字统一在这里修改；字典键对应数据列，不需要改。
CURVE_LABELS = {
    'high494': 'GT highlr 494 - baseline 494',
    'gt247': 'GT 247 - baseline 494 (unequal endpoint)',
}
PLOT_TITLE = 'Benefits by fixed parent-model performance'
X_LABEL = 'Parent step1729 IoU bin'
Y_LABEL = 'Paired mean IoU change (percentage points)'
PLOT_NOTE = '95% pointwise bootstrap intervals; training confounds unresolved'
COUNT_NOTE = 'Each cell: count (% of samples in that bin); changes relative to baseline 494'
CHANGE_LABELS = {'wins': 'Improved', 'losses': 'Worsened', 'ties': 'Unchanged'}
BIN_LABELS = {
    '0': '0', '(0,.1)': '(0,.1)', '[.1,.25)': '[.1,.25)',
    '[.25,.5)': '[.25,.5)', '[.5,.75)': '[.5,.75)', '[.75,1]': '[.75,1]',
}


def plot_parent_bins(conditional, output):
    """只绘制原四联图左上角；支持直接读取已保存的分箱统计。"""
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig = plt.figure(figsize=(10.5, 9), layout='constrained')
    grid = fig.add_gridspec(3, 1, height_ratios=[4, 1.05, 1.05])
    ax = fig.add_subplot(grid[0])
    colors = {'high494': '#b34e24', 'gt247': '#277da8'}
    bins = list(BIN_LABELS)
    for table_index, (arm, color) in enumerate(colors.items(), start=1):
        by_bin = {r['bin']: r for r in conditional if r['arm'] == arm}
        rows = [by_bin[b] for b in bins]
        if any(field not in r for r in rows for field in CHANGE_LABELS):
            raise ValueError('parent_bins.csv 缺少提升/下降/不变计数，请先带 --input 完整运行一次。')
        for r in rows:
            assert sum(int(r[field]) for field in CHANGE_LABELS) == int(r['n'])
        x = np.arange(len(rows)) + (-.07 if arm == 'high494' else .07)
        y = np.array([float(r['mean']) for r in rows]) * 100
        lo = np.array([float(r['lo']) for r in rows]) * 100
        hi = np.array([float(r['hi']) for r in rows]) * 100
        ax.errorbar(x, y, yerr=np.array([y-lo, hi-y]), fmt='o-',
                    color=color, capsize=3, label=CURVE_LABELS[arm])
        table_ax = fig.add_subplot(grid[table_index])
        table_ax.axis('off')
        table_ax.set_title(CURVE_LABELS[arm], fontsize=10, color=color, loc='left', pad=6)
        cells = [[label] + [f"{int(r[field])} ({100 * int(r[field]) / int(r['n']):.1f}%)"
                            if int(r['n']) else '0 (N/A)' for r in rows]
                 for field, label in CHANGE_LABELS.items()]
        table = table_ax.table(cellText=cells, colLabels=['Change'] + [BIN_LABELS[b] for b in bins],
                               cellLoc='center', bbox=[0, 0, 1, .96])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor('#dddddd')
            if row == 0:
                cell.set_facecolor('#f1f3f5')
                cell.set_text_props(weight='bold')
            elif col == 0:
                cell.set_text_props(color=color)
    ax.set_xticks(np.arange(len(bins)), [f"{BIN_LABELS[b]}\nn={int(by_bin[b]['n'])}" for b in bins])
    ax.set(title=PLOT_TITLE, xlabel=X_LABEL, ylabel=Y_LABEL)
    ax.legend(fontsize=9)
    ax.grid(alpha=.18)
    ax.axhline(0, color='.4', linestyle='--', linewidth=1)
    fig.suptitle(f'{PLOT_NOTE}\n{COUNT_NOTE}', fontsize=10)
    for ext in ['png', 'pdf', 'svg']:
        fig.savefig(output / f'gt_align_curves.{ext}', dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--output', type=Path, default=Path(__file__).parent)
    parser.add_argument('--bootstrap', type=int, default=4000)
    parser.add_argument('--plot-only', action='store_true', help='从输出目录的 parent_bins.csv 重画单图，不重复计算统计')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.plot_only:
        with (args.output / 'parent_bins.csv').open() as f:
            plot_parent_bins(list(csv.DictReader(f)), args.output)
        print(f'单图已输出：{args.output / "gt_align_curves.png"}（另有 PDF、SVG）')
        return
    if args.input is None:
        parser.error('完整分析需要 --input；仅修改图中文字可使用 --plot-only')
    records, provenance = {}, {}
    key = lambda r: (r['dataset'], r['sequence'], r['id'], r['dataset_index'])
    for arm, branch in SOURCES.items():
        path = args.input / f'{arm}.jsonl'
        raw = path.read_bytes()
        rows = [json.loads(line) for line in raw.splitlines()]
        records[arm] = {key(r): r for r in rows}
        assert len(rows) == len(records[arm]) == 1766, arm
        provenance[arm] = {'sha256': hashlib.sha256(raw).hexdigest(),
                           'source': f'{REMOTE_ROOT}/{branch}/evaluation/predictions.jsonl'}
    keys = sorted(records['parent1729'])
    for arm, rows in records.items():
        assert set(rows) == set(keys), arm
        assert all(rows[k]['target'] == records['parent1729'][k]['target'] for k in keys), arm
        assert all(rows[k]['parsed'] for k in keys), arm
    scores = {arm: np.array([rows[k]['iou'] for k in keys]) for arm, rows in records.items()}
    assert all(np.isfinite(v).all() and ((v >= 0) & (v <= 1)).all() for v in scores.values())
    n = len(keys)
    dataset = np.array([k[0] for k in keys])
    clusters = sorted(set((k[0], k[1]) for k in keys))
    cluster_index = {k: i for i, k in enumerate(clusters)}
    row_cluster = np.array([cluster_index[k[:2]] for k in keys])
    rng = np.random.default_rng(20260907)
    weights = np.zeros((args.bootstrap, len(clusters)), dtype=np.float64)
    for ds in sorted(set(dataset)):
        indices = [i for i, k in enumerate(clusters) if k[0] == ds]
        weights[:, indices] = rng.multinomial(len(indices), np.full(len(indices), 1 / len(indices)), size=args.bootstrap)

    def interval(values, mask):
        count = int(mask.sum())
        if not count:
            return {'n': 0, 'mean': None, 'lo': None, 'hi': None}
        num = np.bincount(row_cluster, weights=values * mask, minlength=len(clusters))
        den = np.bincount(row_cluster, weights=mask.astype(float), minlength=len(clusters))
        boot_den = weights @ den
        boot = (weights @ num)[boot_den > 0] / boot_den[boot_den > 0]
        lo, hi = np.quantile(boot, [.025, .975])
        return {'n': count, 'mean': float(values[mask].mean()), 'lo': float(lo), 'hi': float(hi)}

    parent = scores['parent1729']
    baseline = scores['baseline494']
    high = scores['high494']
    delta = high - baseline
    low = parent < .5
    all_rows = np.ones(n, dtype=bool)
    bins = [('0', parent == 0), ('(0,.1)', (parent > 0) & (parent < .1)),
            ('[.1,.25)', (parent >= .1) & (parent < .25)),
            ('[.25,.5)', (parent >= .25) & (parent < .5)),
            ('[.5,.75)', (parent >= .5) & (parent < .75)), ('[.75,1]', parent >= .75)]
    assert sum(int(mask.sum()) for _, mask in bins) == n
    groups = {}
    for label, mask in [('all', all_rows), ('parent_lt_0.5', low), ('parent_ge_0.75', parent >= .75)] + [(ds + '_parent_lt_0.5', low & (dataset == ds)) for ds in sorted(set(dataset))]:
        d = delta[mask]
        gains = np.sort(d[d > 0])[::-1]
        trim = int(len(d) * .05)
        trimmed = d[np.argsort(np.abs(d))[:len(d)-trim]]
        groups[label] = {**interval(delta, mask), 'median': float(np.median(d)),
                         'wins': int((d > 1e-12).sum()), 'losses': int((d < -1e-12).sum()),
                         'ties': int((np.abs(d) <= 1e-12).sum()),
                         'trim_largest_abs_5pct_mean': float(trimmed.mean()),
                         'top_5pct_samples_share_positive_gain': float(gains[:max(1, int(np.ceil(.05 * len(d))))].sum() / gains.sum()) if gains.size else None,
                         'parent_miou': float(parent[mask].mean()), 'baseline_miou': float(baseline[mask].mean()),
                         'high_miou': float(high[mask].mean())}
    transitions = []
    for label, mask in [('all', all_rows), ('parent_lt_0.5', low)] + [(ds, dataset == ds) for ds in sorted(set(dataset))]:
        for tau in [.1, .25, .5, .75]:
            rescued = int(((baseline < tau) & (high >= tau) & mask).sum())
            lost = int(((baseline >= tau) & (high < tau) & mask).sum())
            net = (high >= tau).astype(float) - (baseline >= tau).astype(float)
            transitions.append({'group': label, 'threshold': tau, 'rescued': rescued, 'lost': lost, **interval(net, mask)})
    curves = []
    conditional = []
    for arm in ['high494', 'gt247']:
        diff = scores[arm] - baseline
        for cutoff in [.05, .1, .15, .2, .25, .3, .4, .5, .6, .7, .75, .8, .9, 1.000001]:
            curves.append({'arm': arm, 'parent_cutoff_exclusive': cutoff, **interval(diff, parent < cutoff)})
        for label, mask in bins:
            d = diff[mask]
            counts = {'wins': int((d > 1e-12).sum()), 'losses': int((d < -1e-12).sum()),
                      'ties': int((np.abs(d) <= 1e-12).sum())}
            assert sum(counts.values()) == int(mask.sum())
            conditional.append({'arm': arm, 'bin': label, **interval(diff, mask), **counts})
    thresholds = np.linspace(0, 1, 101)
    success = []
    for tau in thresholds:
        diff = (high >= tau).astype(float) - (baseline >= tau).astype(float)
        success.append({'threshold': float(tau), **interval(diff, all_rows),
                        **{arm: float((v >= tau).mean()) for arm, v in scores.items()}})
    decomposition = []
    for label, mask in bins:
        d = delta[mask]
        decomposition.append({'parent_bin': label, 'n': int(mask.sum()), 'sum_delta_over_N': float(d.sum()/n),
                              'wins': int((d > 1e-12).sum()), 'losses': int((d < -1e-12).sum()), 'ties': int((np.abs(d) <= 1e-12).sum())})
    assert abs(sum(r['sum_delta_over_N'] for r in decomposition) - delta.mean()) < 1e-12
    # Identity check: the area under the exact empirical survival curve equals mean IoU.
    for values in scores.values():
        edges = np.unique(np.r_[0., values, 1.])
        area = sum((b-a) * np.mean(values >= b) for a, b in zip(edges[:-1], edges[1:]))
        assert abs(area - values.mean()) < 1e-12
    for filename, rows in [('cumulative_low_score.csv', curves), ('parent_bins.csv', conditional),
                            ('success_thresholds.csv', success), ('transitions.csv', transitions), ('decomposition.csv', decomposition)]:
        with (args.output / filename).open('w') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    summary = {'schema': 'e009.exploratory-gt-align-curves/v1', 'seed': 20260907, 'bootstrap_replicates': args.bootstrap,
               'bootstrap_unit': 'dataset-stratified (dataset, sequence) cluster; paired arms; pointwise percentile intervals',
               'n': n, 'clusters': len(clusters), 'gates': 'unique identities, equal targets, all parsed, finite [0,1], decomposition and exact survival integral PASS',
               'primary_contrast': 'high494 minus baseline494; not an isolated align effect',
               'grouping': 'fixed parent1729 IoU; low-performance = parent IoU < 0.5, posthoc diagnostic definition',
               'provenance': provenance, 'miou': {a: float(v.mean()) for a, v in scores.items()},
               'groups': groups, 'transitions': transitions,
               'limitations': ['No training config matching or seed replication; learning rate may confound contrast.',
                               'gt247 has a different training endpoint; sensitivity comparison only.',
                               'Parent scores anchor groups but are noisy and not independent repeated difficulty estimates.',
                               'Pointwise intervals are exploratory, not simultaneous confidence bands; no causal mechanism claim.',
                               'Dataset identities and targets match; original image hashes, preprocessing and split independence not audited here.']}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    plot_parent_bins(conditional, args.output)
    print(json.dumps({'gates': summary['gates'], 'groups': groups}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
