import copy, hashlib, json, unittest
import numpy as np
from iplocid.pipelines.e010_integrity import (T003_HEADS, T003_PARAMETERS, bootstrap_correct_minus_error, bootstrap_difference_in_differences, layer_matched_random_sets_without_replacement, load_and_validate_r006_t003_reference_heads, normalize_and_aggregate_heads, outcome_label, s30_metrics)
from iplocid.pipelines.outcome_stratified_core30 import core30_hit, largest4n, metrics

class E010R007Test(unittest.TestCase):
 def test_outcome_boundaries(self):
  self.assertEqual(outcome_label({'positive':True,'parse_status':'ok','natural_iou':.7}),'correct'); self.assertEqual(outcome_label({'positive':True,'parse_status':'ok','natural_iou':.1}),'middle'); self.assertEqual(outcome_label({'positive':True,'parse_status':'ok','natural_iou':.099}),'error'); self.assertEqual(outcome_label({'positive':False,'parse_status':'ok','natural_iou':.9}),'nonpositive'); self.assertEqual(outcome_label({'parse_status':'unparsed'}),'unparsed')
 def test_s30_tie_and_4neighborhood(self):
  q,k=core30_hit(np.ones((2,2)),np.array([[1.,0.],[0.,0.]])); self.assertEqual((q,k),(1,2)); m=np.array([[1,0,1],[0,1,0]],bool); self.assertTrue(np.array_equal(largest4n(m),np.array([[1,0,0],[0,0,0]],bool)))
 def test_spatial_auxiliary_fields(self):
  d,s,c=metrics(np.array([[9.,8.],[1.,0.]]),np.array([[1.,0.],[1.,0.]])); self.assertEqual(d['selected_token_count'],2); self.assertEqual(d['s30_intersection_tokens'],1); self.assertEqual(d['s30_union_tokens'],3); self.assertAlmostEqual(d['s30_iou'],1/3); self.assertEqual(d['largest4n_token_count'],2); self.assertTrue(c[0,0])
 def test_ensemble_normalizes_each_head(self):
  got=normalize_and_aggregate_heads([np.array([[9.,1.]]),np.array([[1.,0.]])]); self.assertTrue(np.allclose(got,[[.95,.05]]));
  for bad in ([np.zeros((1,2)),np.ones((1,2))],[np.array([[np.nan]]),np.ones((1,1))],[np.ones((1,2)),np.ones((2,1))]):
   with self.assertRaises(ValueError): normalize_and_aggregate_heads(bad)
 def test_random_repeated_layers_is_without_replacement(self):
  frozen=['L20H01','L20H02','L20H03','L18H05','L14H02']; a=layer_matched_random_sets_without_replacement(frozen,seed=7,repeats=100); self.assertEqual(a,layer_matched_random_sets_without_replacement(frozen,seed=7,repeats=100)); self.assertTrue(all(len(x)==5 and len(set(x))==5 and sorted(h//32 for h in x)==[14,18,20,20,20] for x in a))
 def test_bootstrap_and_did(self):
  rows=[{'outcome':'correct','x':3.,'methods':{'s':{'x':3},'c':{'x':1}}},{'outcome':'correct','x':5.,'methods':{'s':{'x':5},'c':{'x':2}}},{'outcome':'error','x':1.,'methods':{'s':{'x':1},'c':{'x':1}}}]; a=bootstrap_correct_minus_error(rows,'x',seed=3,repeats=20); self.assertEqual((a['n_correct'],a['n_error'],a['difference']),(2,1,3.)); self.assertEqual(a,bootstrap_correct_minus_error(rows,'x',seed=3,repeats=20)); self.assertEqual(bootstrap_difference_in_differences(rows,'s','c','x',seed=3,repeats=20)['difference'],2.5); self.assertIsNone(bootstrap_correct_minus_error([], 'x',seed=1,repeats=2)['difference'])
 def test_t003_authority_rejections(self):
  import tempfile
  base={'schema':'iplocid.e010.gt-iou-entropy-reward-trial/v1','trial_id':'T-003','status':'completed','parameters':T003_PARAMETERS,'integrity':{'records':140,'discovery':70,'evaluation':70,'sequence_overlap':0,'same_natural_query_bbox_rows':True,'gt_used_in_discovery':True,'heldout_reselection':False,'outcome_used_in_ranking':False,'failures':0},'discovery':{'fixed_heads':T003_HEADS}}
  with tempfile.TemporaryDirectory() as d:
   p=f'{d}/summary.json'; open(p,'w').write(json.dumps(base)); auth={'summary_path':p,'summary_sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'trial_id':'T-003','parameters':T003_PARAMETERS,'sets':T003_HEADS}; self.assertEqual(load_and_validate_r006_t003_reference_heads(auth)[0]['5'],tuple(T003_HEADS['5']))
   for mutate in (lambda x:x.update(schema='wrong'),lambda x:x['parameters'].update(iou_threshold=.2),lambda x:x['discovery'].update(fixed_heads={'3':[],'5':[]})):
    x=copy.deepcopy(base); mutate(x); open(p,'w').write(json.dumps(x));
    with self.assertRaises(RuntimeError): load_and_validate_r006_t003_reference_heads(auth)
if __name__=='__main__': unittest.main()
