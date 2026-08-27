import json,tempfile,unittest
from pathlib import Path
import numpy as np
from iplocid.pipelines.head_reliability_controls import explanation_errors,invert_box,paired_identity,require_run1_manifest,transform_box

class ControlTests(unittest.TestCase):
    def test_box_roundtrip(self):
        box=[1,2,5,7]
        for mode in ("identity","horizontal_flip","vertical_flip"):
            self.assertEqual(invert_box(transform_box(box,10,12,mode),10,12,mode),box)
    def test_following_beats_fixed(self):
        original=np.array([[1.,0.],[0.,0.]])
        transformed=np.fliplr(original)
        score=explanation_errors(original,transformed,"horizontal_flip")
        self.assertEqual(score["object_following_mse"],0); self.assertGreater(score["fixed_position_mse"],0)
    def test_pair_failures_are_explicit(self):
        pairs,failures=paired_identity([{"pair_id":"a","condition":"correct_reference"}])
        self.assertFalse(pairs); self.assertEqual(len(failures),1)
    def test_manifest_hash_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"run1.json"; path.write_text(json.dumps({"schema":"iplocid.e010.fixed-head-validation/v1","selection_hash":"x","top3":[[1,1]],"top5":[[1,1]]}))
            self.assertEqual(require_run1_manifest(path,"x")["selection_hash"],"x")
            with self.assertRaises(ValueError): require_run1_manifest(path,"wrong")
if __name__=="__main__": unittest.main()
