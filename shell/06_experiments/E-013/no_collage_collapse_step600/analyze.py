import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path('/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-013/focus-confidence-sft/branches/20260923T135503296295Z--multi3-instances-grpo-rank-lr8e5-3ep/grpo')
STEP_STOP = 600


def avg(values):
    return statistics.fmean(values) if values else None


def med(values):
    return statistics.median(values) if values else None


def first_argmax(values):
    return max(range(len(values)), key=values.__getitem__)


def group_stats(rows):
    if not rows:
        return {'n': 0}
    delta = [r['scores'][1] - r['scores'][0] for r in rows]
    return {
        'n': len(rows),
        'sample_ids': len({r['sample_id'] for r in rows}),
        'best2_selection_n': sum(r['selected'] == 1 for r in rows),
        'best2_selection_rate': avg([r['selected'] == 1 for r in rows]),
        'delta_score_mean': avg(delta),
        'delta_score_median': med(delta),
        'delta_score_positive_rate': avg([x > 0 for x in delta]),
        'delta_score_tie_rate': avg([x == 0 for x in delta]),
        'delta_iou_mean': avg([r['ious'][1] - r['ious'][0] for r in rows]),
        'first_iou_ge_05_rate': avg([r['ious'][0] >= 0.5 for r in rows]),
        'zero_advantage_rate': avg([r['advantage'] == 0 for r in rows]),
    }


def reward_stats(rows):
    if not rows:
        return {'n': 0}
    keys = ('total', 'iou', 'brier', 'duplicate_penalty', 'ranking_loss',
            'ranking_pairs')
    d = {'n': len(rows), 'sample_ids': len({r['sample_id'] for r in rows}),
         'advantage_mean': avg([r['advantage'] for r in rows]),
         'zero_advantage_rate': avg([r['advantage'] == 0 for r in rows]),
         'first_iou_mean': avg([r['ious'][0] for r in rows]),
         'second_iou_mean': avg([r['ious'][1] for r in rows]),
         'delta_iou_mean': avg([r['ious'][1]-r['ious'][0] for r in rows]),
         'selected_second_rate': avg([r['selected'] == 1 for r in rows])}
    for k in keys:
        d[k + '_mean'] = avg([r['reward'][k] for r in rows])
    return d


def recompute(scores, ious, duplicate_penalty):
    targets = [int(x >= 0.5) for x in ious]
    brier = sum((s-t)**2 for s,t in zip(scores, targets))/3
    terms = []
    for i in range(3):
        for j in range(i+1, 3):
            gap = ious[i]-ious[j]
            if abs(gap) >= 0.1:
                desired = 1 if gap > 0 else -1
                terms.append(max(0, 0.1-desired*(scores[i]-scores[j])))
    ranking_loss = avg(terms) or 0
    selected = first_argmax(scores)
    return ious[selected] - brier - duplicate_penalty - 0.5*ranking_loss


raw_count = 0
rows = []
grouped = defaultdict(list)
audit = defaultdict(int)
for rank in range(4):
    path = ROOT / f'rollouts-rank{rank}.jsonl'
    for line in path.open():
        if not line.strip():
            continue
        raw_count += 1
        d = json.loads(line)
        if d['step'] >= STEP_STOP or d.get('target_present') is not True:
            continue
        reward = d.get('reward') or {}
        scores = reward.get('scores')
        ious = reward.get('candidate_ious')
        if reward.get('valid') is not True or not isinstance(scores, list) or not isinstance(ious, list) or len(scores) != 3 or len(ious) != 3:
            continue
        if any(not isinstance(x, (int,float)) or not math.isfinite(x) for x in scores+ious):
            continue
        selected = first_argmax(scores)
        if selected != reward['selected_index']:
            raise RuntimeError('selected_index mismatch')
        item = {'rank': rank, 'step': d['step'], 'sample_id': d['sample_id'],
                'scores': scores, 'ious': ious, 'selected': selected,
                'reward': reward, 'advantage': d['advantage']}
        rows.append(item)
        grouped[(rank,d['step'],d['sample_id'])].append(item)

best2 = [r for r in rows if r['ious'][1] > max(r['ious'][0],r['ious'][2])]
position_bins = {}
for lo in range(0,600,100):
    subset = [r for r in rows if lo <= r['step'] < lo+100]
    unique = [r for r in subset if r['ious'].count(max(r['ious'])) == 1]
    position_bins[f'{lo}-{lo+99}'] = {
        'n': len(subset),
        'unique_best_counts': [sum(first_argmax(r['ious']) == i for r in unique) for i in range(3)],
        'tied_best_n': len(subset)-len(unique),
        'selected_nonfirst_n': sum(r['selected'] != 0 for r in subset),
    }
bins = {}
for lo in range(0,600,100):
    b = [r for r in best2 if lo <= r['step'] < lo+100]
    bins[f'{lo}-{lo+99}'] = group_stats(b)
    edges = [round(-1+i*.1, 10) for i in range(21)]
    edges[-1] = 1.00001  # Include the possible exact +1 score margin.
    bins[f'{lo}-{lo+99}']['hist_delta_score_edges'] = edges
    edges = bins[f'{lo}-{lo+99}']['hist_delta_score_edges']
    bins[f'{lo}-{lo+99}']['hist_delta_score_counts'] = [sum(edges[i] <= r['scores'][1]-r['scores'][0] < edges[i+1] for r in b) for i in range(len(edges)-1)]

iou_edges = [0,0.05,0.1,0.2,1.00001]
iou_gap = {}
for label, subset in [('all',best2),('early_0_199',[r for r in best2 if r['step'] < 200]),('late_400_599',[r for r in best2 if r['step'] >= 400]),('last_500_599',[r for r in best2 if r['step'] >= 500])]:
    iou_gap[label] = {}
    for i in range(len(iou_edges)-1):
        lo,hi = iou_edges[i:i+2]
        b = [r for r in subset if lo <= r['ious'][1]-r['ious'][0] < hi]
        iou_gap[label][f'{lo:g}-{hi:g}'] = group_stats(b)

reward_comparison = {}
for label,subset in [('all',best2),('early_0_199',[r for r in best2 if r['step']<200]),('late_400_599',[r for r in best2 if r['step']>=400]),('last_500_599',[r for r in best2 if r['step']>=500])]:
    reward_comparison[label] = {
        'A_s2_gt_s1': reward_stats([r for r in subset if r['scores'][1] > r['scores'][0]]),
        'B_s1_gt_s2': reward_stats([r for r in subset if r['scores'][0] > r['scores'][1]]),
        'tie': reward_stats([r for r in subset if r['scores'][0] == r['scores'][1]]),
    }

paired = []
for key,group in grouped.items():
    a=[r for r in group if r in best2 and r['scores'][1]>r['scores'][0]]
    b=[r for r in group if r in best2 and r['scores'][0]>r['scores'][1]]
    if a and b:
        paired.append({'step':key[1], 'reward_diff':avg([r['reward']['total'] for r in a])-avg([r['reward']['total'] for r in b]),
                       'advantage_diff':avg([r['advantage'] for r in a])-avg([r['advantage'] for r in b]),
                       'iou_gap_diff':avg([r['ious'][1]-r['ious'][0] for r in a])-avg([r['ious'][1]-r['ious'][0] for r in b])})

residuals = [abs(recompute(r['scores'],r['ious'],r['reward']['duplicate_penalty'])-r['reward']['total']) for r in best2]
wrong = [r for r in best2 if r['scores'][0]>r['scores'][1]]
counterfactual = []
for r in wrong:
    swapped = [r['scores'][1],r['scores'][0],r['scores'][2]]
    counterfactual.append(recompute(swapped,r['ious'],r['reward']['duplicate_penalty'])-r['reward']['total'])

early_by_id = defaultdict(list)
late_by_id = defaultdict(list)
for r in best2:
    if r['step'] < 200:
        early_by_id[r['sample_id']].append(r)
    elif r['step'] >= 400:
        late_by_id[r['sample_id']].append(r)
matched_ids = sorted(early_by_id.keys() & late_by_id.keys())
matched_score_changes = [
    avg([r['scores'][1]-r['scores'][0] for r in late_by_id[id_]])
    - avg([r['scores'][1]-r['scores'][0] for r in early_by_id[id_]])
    for id_ in matched_ids]
matched_select_changes = [
    avg([r['selected']==1 for r in late_by_id[id_]])
    - avg([r['selected']==1 for r in early_by_id[id_]])
    for id_ in matched_ids]

output = {
    'source':str(ROOT), 'raw_records':raw_count,'included_positive_valid_three_before_step600':len(rows),
    'best2_unique':group_stats(best2), 'bins_100':bins, 'position_bins_100':position_bins,
    'iou_gap':iou_gap,
    'reward_comparison':reward_comparison,
    'same_prompt_group_A_and_B':{'n':len(paired),'reward_difference_mean':avg([p['reward_diff'] for p in paired]),
        'reward_difference_median':med([p['reward_diff'] for p in paired]),
        'advantage_difference_mean':avg([p['advantage_diff'] for p in paired]),
        'iou_gap_difference_mean':avg([p['iou_gap_diff'] for p in paired]),
        'positive_reward_difference_rate':avg([p['reward_diff']>0 for p in paired])},
    'objective_recompute_max_abs_error':max(residuals) if residuals else None,
    'swap_s1_s2_in_B':{'n':len(counterfactual),'mean_delta_reward':avg(counterfactual),
       'median_delta_reward':med(counterfactual),
       'positive_fraction':avg([x>0 for x in counterfactual])},
    'all_groups':len(grouped),
    'best2_groups':len({(r['rank'],r['step'],r['sample_id']) for r in best2}),
    'best2_zero_advantage_rate':avg([r['advantage']==0 for r in best2]),
    'best2_early_late_sample_id_overlap':len({r['sample_id'] for r in best2 if r['step']<200}
                                              & {r['sample_id'] for r in best2 if r['step']>=400}),
    'matched_early_late_best2': {
        'sample_ids': len(matched_ids),
        'delta_score_change_mean': avg(matched_score_changes),
        'delta_score_change_median': med(matched_score_changes),
        'fraction_delta_score_decreased': avg([x<0 for x in matched_score_changes]),
        'selection_rate_change_mean': avg(matched_select_changes),
        'early_selection_rate_sample_equal': avg([
            avg([r['selected']==1 for r in early_by_id[id_]]) for id_ in matched_ids]),
        'late_selection_rate_sample_equal': avg([
            avg([r['selected']==1 for r in late_by_id[id_]]) for id_ in matched_ids]),
    },
}
print(json.dumps(output,allow_nan=False,sort_keys=True))
