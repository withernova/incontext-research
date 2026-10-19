import pathlib,os,json,hashlib
root=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014')
old=root/'e014-discovery-priority-score04-beta0-sft659-200step-seed11451'
new=root/'20261015-172638__discovery-priority__score0.4-selected0.2-coverage0.5__kl0__sft659__200step__seed11451'
assert old.is_dir() and not old.is_symlink() and not new.exists() and not new.is_symlink()
assert (old/'.survey-tool-exit-code').read_text().strip()=='0'
assert json.loads((old/'payload/grpo/completed.json').read_text())['steps']==200
# Metadata only: do not open managed control files or historical log content.
def fingerprint(base):
 rows=[]
 for d,dirs,files in os.walk(base,followlinks=False):
  for name in dirs+files:
   p=pathlib.Path(d)/name;s=p.lstat()
   rows.append((str(p.relative_to(base)),s.st_ino,s.st_size,s.st_mtime_ns,s.st_mode))
 return len(rows),hashlib.sha256(json.dumps(sorted(rows),separators=(',',':')).encode()).hexdigest()
before=fingerprint(old)
old.rename(new)
after=fingerprint(new);assert before==after,'rename changed tree metadata'
old.symlink_to(new.name,target_is_directory=True)
assert old.resolve()==new.resolve()
print(json.dumps({'old':str(old),'new':str(new),'timestamp_source':'canonical execution_authorization_consumed_at 2026-10-15T17:26:38','entries_preserved':before[0],'tree_metadata_sha256':before[1],'old_path_is_compatibility_symlink':old.is_symlink(),'new_path_is_real_directory':new.is_dir() and not new.is_symlink()}))
