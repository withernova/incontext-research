import unittest
from iplocid.pipelines.gt_iou_entropy_reward_trials import validate_rank_config

class E010R006IntegrityTest(unittest.TestCase):
 def test_t003_formula_contract(self):
  c={'reward_form':'thresholded_iou_bonus','iou_metric':'support50_fiou','entropy_weight':1,'iou_reward_weight':2,'iou_threshold':.1,'rank_score':'-normalized_entropy + iou_reward_weight * max(0, support50_fiou-iou_threshold)'}
  validate_rank_config(c)
  for key,value in [('iou_metric','other'),('rank_score','wrong'),('iou_threshold',.2)]:
   bad=dict(c); bad[key]=value
   with self.assertRaises(ValueError): validate_rank_config(bad)
if __name__=='__main__': unittest.main()
