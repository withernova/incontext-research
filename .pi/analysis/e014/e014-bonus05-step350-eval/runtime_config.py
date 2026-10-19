"""Run-local parameter binding for the authorized bonus0.5 step350 evaluation."""
_base_ = '/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy/configs/experiments/E-014/evaluation/e014_structure_score_iou_explore_step150_eval1766.py'
_root = '/defaultShare/archive/songzhengyue/projects/IPLoc'
_checkpoint = _root + '/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/payload/grpo/checkpoints/step_000350'
_work = _root + '/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766/payload'
work_dir = _work
test_dataloader = dict(dataset=dict(ann_file=_work + '/manifest.json'))
evaluation = dict(checkpoint=_checkpoint, inputs_file=_work + '/inputs.json',
                  expected_inputs=dict(checkpoint=_checkpoint, step=350,
                                       training_reward=dict(exploration_penalty=.6,
                                                            multibox_bonus_weight=.5)))
del _root, _checkpoint, _work
