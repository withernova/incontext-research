"""Summarize paired held-out first-score interventions."""

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).parent
rows = [json.loads(line) for line in (ROOT / 'first_score_validation_results.jsonl').open()]
if len(rows) != 115 or len({r['id'] for r in rows}) != 115:
    raise ValueError(f'Expected 115 unique complete cases, got {len(rows)}')


def summary(items):
    valid = [r for r in items if all(r['conditions'][k]['second_score'] is not None
              for k in ('original', 'low_001', 'high_099'))]
    out = {'n': len(items), 'valid_all_conditions': len(valid)}
    for key in ('original', 'low_001', 'high_099'):
        v = [r['conditions'][key] for r in valid]
        out[key] = {
            'mean_second_score': statistics.mean(x['second_score'] for x in v) if v else None,
            'mean_second_iou': statistics.mean(x['second_iou'] for x in v) if v else None,
            'second_exceeds_forced_first': sum(x['second_score'] >
                (r['baseline_scores'][0] if key == 'original' else
                 0.01 if key == 'low_001' else 0.99)
                for r, x in zip(valid, v)),
        }
    for key in ('low_001', 'high_099'):
        deltas = [r['conditions'][key]['second_score'] -
                  r['conditions']['original']['second_score'] for r in valid]
        iou_deltas = [r['conditions'][key]['second_iou'] -
                      r['conditions']['original']['second_iou'] for r in valid]
        out[key].update(
            score_up=sum(x > 0 for x in deltas),
            score_same=sum(x == 0 for x in deltas),
            score_down=sum(x < 0 for x in deltas),
            mean_score_delta=statistics.mean(deltas) if deltas else None,
            box_changed=sum(r['conditions'][key]['second_box'] !=
                            r['conditions']['original']['second_box'] for r in valid),
            mean_iou_delta=statistics.mean(iou_deltas) if iou_deltas else None,
        )
    out['original_reproduction'] = {
        'second_score': sum(r['conditions']['original']['second_score'] ==
                            r['baseline_scores'][1] for r in valid),
        'second_iou_exact': sum(abs(r['conditions']['original']['second_iou'] -
            r['baseline_ious'][1]) < 1e-12 for r in valid),
    }
    return out


result = {
    'all_eligible': summary(rows),
    'effective_downshift': summary([r for r in rows if r['baseline_scores'][0] > 0.01]),
    'clear_second_effective_downshift': summary([r for r in rows
        if r['baseline_scores'][0] > 0.01 and r['baseline_ious'][1] >= 0.5
        and r['baseline_ious'][1] - r['baseline_ious'][0] >= 0.1]),
}
(ROOT / 'first_score_validation_summary.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
