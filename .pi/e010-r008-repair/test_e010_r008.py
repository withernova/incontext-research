import unittest
from iplocid.pipelines.full_lasot_role_audit import QUERY_TOP5, REFERENCE_TOP5, READOUTS, deterministic_split, layer_matched_random_heads

class E010R008Test(unittest.TestCase):
 def test_query_head_authority(self): self.assertEqual(QUERY_TOP5, ("L20H15","L24H16","L25H10","L15H13","L21H10"))
 def test_reference_head_authority_and_row_contract(self):
  self.assertEqual(REFERENCE_TOP5, ("L18H05","L20H12","L20H15","L20H08","L14H02")); self.assertEqual([x[0] for x in READOUTS],["q_to_q","q_to_r","r_to_r"]); self.assertEqual(READOUTS[2][1],"reference")
 def test_per_class_split_is_deterministic_and_disjoint(self):
  rows=[{"source":{"category":f"c{i}","sequence_cluster":f"c{i}/{j}"}} for i in range(70) for j in range(20)]; groups={f"c{i}":list(range(i*20,i*20+20)) for i in range(70)}
  e,d=deterministic_split(groups,rows,20260830); self.assertTrue(all(len(e[x])==len(d[x])==10 and not set(e[x])&set(d[x]) for x in groups))
 def test_layer_matched_random_has_frozen_layers_and_is_deterministic(self):
  a=layer_matched_random_heads(7,20260830,QUERY_TOP5,"q_to_r"); self.assertEqual(a,layer_matched_random_heads(7,20260830,QUERY_TOP5,"q_to_r")); self.assertEqual([v[0] for v in a.values()],[20,24,25,15,21])
if __name__ == '__main__': unittest.main()
