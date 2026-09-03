import json, tempfile, unittest
from pathlib import Path
from iplocid.pipelines.e010_integrity import ROW_CONTRACT, T003_HEADS, T003_PARAMETERS, load_and_validate_r006_t003_reference_heads, validate_repaired_r008_summary
from iplocid.pipelines.full_lasot_role_audit import READOUTS, deterministic_split, validate_natural_records

class E010R008Test(unittest.TestCase):
 def test_readout_contract(self):
  self.assertEqual(list(READOUTS),['q_to_q','q_to_r','rheads_t003_on_qbbox_to_reference'])
  rows={v['row_source'] for v in READOUTS.values()}; self.assertEqual(rows,{ROW_CONTRACT}); self.assertEqual(READOUTS['rheads_t003_on_qbbox_to_reference']['key_span'],'reference'); self.assertEqual(READOUTS['rheads_t003_on_qbbox_to_reference']['head_authority'],'r006_t003_reference')
 def test_t003_top3_top5_and_no_main_summary_authority(self):
  self.assertEqual(T003_HEADS['3'],['L18H05','L12H00','L20H12']); self.assertEqual(T003_HEADS['5'],['L18H05','L12H00','L20H12','L7H25','L20H15'])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'main-summary.json'; p.write_text(json.dumps({'discovery':{'fixed_heads':T003_HEADS}})); cfg={'summary_path':str(p),'summary_sha256':'0'*64,'trial_id':'T-003','parameters':T003_PARAMETERS,'sets':T003_HEADS}
   with self.assertRaises(RuntimeError): load_and_validate_r006_t003_reference_heads(cfg)
 def test_stale_v1_summary_rejected(self):
  with self.assertRaises(RuntimeError): validate_repaired_r008_summary({'schema':'iplocid.e010.full-lasot-frozen-query-top5/v1'})
 def test_per_class_split(self):
  rows=[{'source':{'category':f'c{i}','sequence_cluster':f'c{i}/{j}'}} for i in range(70) for j in range(20)]; groups={f'c{i}':list(range(i*20,i*20+20)) for i in range(70)}; e,d=deterministic_split(groups,rows,3); self.assertTrue(all(len(e[x])==len(d[x])==10 and not set(e[x])&set(d[x]) for x in groups))
 def test_natural_record_validation_rejects_missing_duplicate_and_mismatched_sequence(self):
  rows=[{'source':{'sequence_cluster':f'a/{i}'}} for i in range(1400)]
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'n.jsonl'; good=[{'index':i,'sequence':f'a/{i}','response':'[1]','response_token_ids':[1]} for i in range(1400)]; p.write_text(''.join(json.dumps(x)+'\n' for x in good)); self.assertEqual(len(validate_natural_records({'natural_records_path':str(p)},rows)),1400)
   good[-1]['index']=0; p.write_text(''.join(json.dumps(x)+'\n' for x in good));
   with self.assertRaises(RuntimeError): validate_natural_records({'natural_records_path':str(p)},rows)
if __name__=='__main__': unittest.main()
