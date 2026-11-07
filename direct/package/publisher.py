"""Build a content-addressed code update for publication by the assistant.
This tool never contacts GitHub or edits the local installation.
"""
import argparse,json,sys
from pathlib import Path
from agent import digest,writable_path,write_json,SUFFIXES,MAX_FILE,MAX_TOTAL

def build(baseline,candidate,revision,update_id,tests,output,allow_protected=False):
 baseline=Path(baseline);candidate=Path(candidate);output=Path(output);blobs=output/'jarvis-updates/blobs';blobs.mkdir(parents=True,exist_ok=True);entries=[];total=0
 names={p.relative_to(root).as_posix() for root in (baseline,candidate) for p in root.rglob('*') if p.is_file() and p.suffix.lower() in SUFFIXES}
 for name in sorted(names):
  old=baseline/name;new=candidate/name;before=old.read_bytes() if old.exists() else None;after=new.read_bytes() if new.exists() else None
  if before==after:continue
  writable_path(candidate,name,allow_protected)
  if after is not None:
   total+=len(after)
   if len(after)>MAX_FILE or total>MAX_TOTAL:raise ValueError('Correctif trop volumineux')
   if new.suffix=='.py':compile(after,name,'exec')
   (blobs/digest(after)).write_bytes(after)
  entries.append({'path':name,'before':digest(before) if before is not None else None,'after':digest(after) if after is not None else None})
 if not entries:raise ValueError('Aucun changement')
 checks=[]
 for path in tests:
  path=Path(path);code=path.read_bytes();compile(code,str(path),'exec');key=digest(code);(blobs/key).write_bytes(code);checks.append({'name':path.name,'sha256':key,'timeout':180})
 if not checks:raise ValueError('Au moins un test obligatoire')
 release={'revision':revision,'id':update_id,'title':update_id,'files':entries,'checks':checks,'restart':True,'allow_protected_data':bool(allow_protected)}
 # A preview is not the active channel: publish only after review and passing tests.
 write_json(output/'release_preview.json',release);return release
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--candidate',required=True);p.add_argument('--revision',type=int,required=True);p.add_argument('--id',required=True);p.add_argument('--test',action='append',required=True);p.add_argument('--output',required=True);p.add_argument('--allow-protected-data',action='store_true');a=p.parse_args()
 print(json.dumps(build(a.baseline,a.candidate,a.revision,a.id,a.test,a.output,a.allow_protected_data),indent=2))
