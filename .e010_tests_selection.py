import unittest
import numpy as np
from iplocid.attention.selection import chord_threshold, fixed_top, layer_matched_random, select_fixed_heads, spatial_component_entropy

class SelectionTests(unittest.TestCase):
    def test_entropy_prefers_one_component(self):
        focused=np.array([[2.,2.,0.],[2.,2.,0.],[0.,0.,0.]])
        split=np.array([[2.,0.,0.],[0.,0.,0.],[0.,0.,2.]])
        self.assertLess(spatial_component_entropy(focused),spatial_component_entropy(split))
    def test_fixed_selection_is_deterministic(self):
        samples=[]
        for shift in (0.,.1,.2):
            samples.append({(2,0):np.array([[3+shift,2],[0,0]]),(2,1):np.array([[2,0],[0,2+shift]]),(3,0):np.ones((2,2))})
        first=select_fixed_heads(samples,per_sample=2); second=select_fixed_heads(samples,per_sample=2)
        self.assertEqual(first.ranked_heads,second.ranked_heads); self.assertEqual(first.frequency,second.frequency)
        self.assertEqual(len(fixed_top(first,2)),2)
    def test_layer_matched_control(self):
        control=layer_matched_random([(2,0),(3,0)],[(2,0),(2,1),(3,0),(3,1)],7)
        self.assertEqual([x[0] for x in control],[2,3]); self.assertEqual(len(set(control)),2)
    def test_no_silent_zero(self):
        with self.assertRaises(ValueError): select_fixed_heads([])
        with self.assertRaises(ValueError): chord_threshold([])
if __name__=="__main__": unittest.main()
