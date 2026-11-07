import copy,hashlib,importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
MODULE=Path(__file__).resolve().parents[1]/'package/agent.py'
sp=importlib.util.spec_from_file_location('direct_agent',MODULE);a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
TARGET='SYSTEME_JARVIS/MOTEUR_V196/ENGINE/logic.py'
class Source:
 def __init__(self):self.objects={};self.updates=[];self.calls=[]
 def add(self,data):key=a.digest(data);self.objects[key]=data;return key
 def blob(self,key):self.calls.append(key);return self.objects[key]
 def channel(self):return {'protocol':1,'updates':self.updates}
class Processes:
 def __init__(self):
  self.active=[{'role':'engine','marker':'voice_v195/live_voice_session_v195.py','pid':3},{'role':'mfd','marker':'background_mfd_v194/JARVIS_V194.exe','pid':4}];self.calls=[];self.health=[]
 def snapshot(self):return copy.deepcopy(self.active)
 def stop(self,snapshot):
  self.calls.append(('stop',[p['role'] for p in snapshot]));names={p['marker'] for p in snapshot};self.active=[p for p in self.active if p['marker'] not in names]
 def restart(self,snapshot):self.calls.append(('restart',[p['role'] for p in snapshot]));self.active.extend(copy.deepcopy(snapshot))
 def healthy(self,snapshot):return self.health.pop(0) if self.health else True
class Case(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.root=self.base/'JARVIS_LMU';self.file=self.root/TARGET;self.file.parent.mkdir(parents=True);self.file.write_text('VALUE=1\n')
  self.storage=self.root/'SYSTEME_JARVIS/DIRECT_GITHUB';self.source=Source();self.processes=Processes();self.agent=a.Agent(self.root,self.storage,self.source,self.processes)
 def tearDown(self):self.tmp.cleanup()
 def release(self,after=b'VALUE=2\n',revision=1,before=None):
  old=a.digest(self.file.read_bytes()) if before is None else before;new=self.source.add(after) if after is not None else None
  check=("import os,runpy\nfrom pathlib import Path\np=Path(os.environ['JARVIS_CANDIDATE_ROOT'])/"+repr(TARGET)+"\n"+("assert not p.exists()\n" if after is None else "assert runpy.run_path(str(p))['VALUE']=="+str(int(after.decode().split('=')[1].strip()))+"\n")).encode()
  return {'revision':revision,'id':'test-'+str(revision),'title':'test','files':[{'path':TARGET,'before':old,'after':new}],'checks':[{'name':'test_logic.py','sha256':self.source.add(check),'timeout':10}],'restart':True}
 def test_success_real_test_execution_and_cache(self):
  r=self.release();self.source.updates=[r];status=self.agent.poll();self.assertEqual(status['revision'],1);self.assertEqual(self.file.read_text(),'VALUE=2\n');self.assertFalse(self.agent.pending.exists())
  self.assertEqual(self.source.calls.count(r['files'][0]['after']),1);self.assertTrue((self.storage/'ANCIENNES_VERSIONS/revision_000000_avant_test-1/manifest.json').exists())
  self.assertEqual(self.processes.calls[0],('stop',['engine']));self.assertTrue(any(p['role']=='mfd' for p in self.processes.active))
 def test_failed_check_never_stops_live_app(self):
  r=self.release();r['checks'][0]['sha256']=self.source.add(b'raise RuntimeError("bad test")\n')
  with self.assertRaises(a.UpdateError):self.agent.apply(r)
  self.assertEqual(self.file.read_text(),'VALUE=1\n');self.assertEqual(self.processes.calls,[]);self.assertFalse(self.agent.pending.exists())
 def test_base_mismatch(self):
  r=self.release(before='0'*64)
  with self.assertRaises(a.UpdateError):self.agent.apply(r)
  self.assertEqual(self.processes.calls,[])
 def test_bad_hash(self):
  r=self.release();self.source.objects[r['files'][0]['after']]=b'VALUE=999\n'
  with self.assertRaises(a.UpdateError):self.agent.apply(r)
  self.assertEqual(self.file.read_text(),'VALUE=1\n')
 def test_syntax_error(self):
  r=self.release();r['files'][0]['after']=self.source.add(b'def !bad\n')
  with self.assertRaises(SyntaxError):self.agent.apply(r)
  self.assertEqual(self.processes.calls,[])
 def test_runtime_failure_restores_old_app_and_mfd_untouched(self):
  self.processes.health=[False,True];r=self.release();status=self.agent.apply(r)
  self.assertEqual(status['state'],'ANNULE');self.assertEqual(self.file.read_text(),'VALUE=1\n');self.assertEqual(self.agent.state['revision'],0);self.assertIn(r['id'],self.agent.state['blocked'])
  self.assertTrue(all('mfd' not in call[1] for call in self.processes.calls))
 def test_blocked_update_not_retried(self):
  r=self.release();self.agent.state['blocked']=[r['id']];self.assertEqual(self.agent.apply(r)['state'],'BLOQUE');self.assertEqual(self.processes.calls,[])
 def test_delete_and_rollback(self):
  r=self.release(after=None);self.processes.health=[False,True];status=self.agent.apply(r);self.assertEqual(status['state'],'ANNULE');self.assertEqual(self.file.read_text(),'VALUE=1\n')
 def test_create_new_file_and_rollback(self):
  r=self.release();path='SYSTEME_JARVIS/new.py';r['files'].append({'path':path,'before':None,'after':self.source.add(b'NEW=True\n')});self.processes.health=[False,True]
  self.agent.apply(r);self.assertFalse((self.root/path).exists());self.assertEqual(self.file.read_text(),'VALUE=1\n')
 def test_interrupted_transaction_recovered(self):
  r=self.release();path='SYSTEME_JARVIS/new.py';r['files'].append({'path':path,'before':None,'after':self.source.add(b'NEW=True\n')});original=a.atomic
  def fail(p,data):
   if Path(p)==self.root/path:raise KeyboardInterrupt
   return original(p,data)
  with patch.object(a,'atomic',fail):
   with self.assertRaises(KeyboardInterrupt):self.agent.apply(r)
  self.assertEqual(self.file.read_text(),'VALUE=2\n');self.assertTrue(self.agent.pending.exists())
  other=a.Agent(self.root,self.storage,self.source,self.processes);other.recover();self.assertEqual(self.file.read_text(),'VALUE=1\n');self.assertFalse((self.root/path).exists());self.assertFalse(other.pending.exists())
 def test_chain_of_two(self):
  r1=self.release();r2=self.release(after=b'VALUE=3\n',revision=2,before=a.digest(b'VALUE=2\n'));self.source.updates=[r1,r2];self.agent.poll();self.assertEqual(self.agent.state['revision'],2);self.assertEqual(self.file.read_text(),'VALUE=3\n')
 def test_missing_revision(self):
  r=self.release(revision=2)
  with self.assertRaises(a.UpdateError):self.agent.apply(r)
 def test_duplicate_paths(self):
  r=self.release();r['files']*=2
  with self.assertRaises(a.UpdateError):self.agent.apply(r)
 def test_protected_data_denied(self):
  r=self.release();r['files'][0]['path']='SYSTEME_JARVIS/X/braking_live_v19650/DATA/data.json'
  with self.assertRaises(a.UpdateError):self.agent.apply(r)
 def test_pause_no_network_or_stop(self):
  a.write_json(self.storage/'control.json',{'paused':True});self.assertEqual(self.agent.poll()['state'],'PAUSE');self.assertEqual(self.processes.calls,[])
 def test_user_rollback(self):
  r=self.release();self.agent.apply(r);a.write_json(self.storage/'control.json',{'command':'rollback','paused':True});self.agent.poll();self.assertEqual(self.file.read_text(),'VALUE=1\n');self.assertEqual(self.agent.state['revision'],0)
 def test_safe_paths(self):
  for path in ('../outside.py','/tmp/a.py','C:/a.py','SYSTEME_JARVIS/../other.py','SYSTEME_JARVIS/NUL.py','SYSTEME_JARVIS/a.py.','SYSTEME_JARVIS/a\\b.py','SYSTEME_JARVIS/DIRECT_GITHUB/agent.py','SYSTEME_JARVIS/ENV_JARVIS_PUBLIC/a.py','SYSTEME_JARVIS/runtime_source_v191.json'):
   with self.subTest(path=path):
    with self.assertRaises(a.UpdateError):a.writable_path(self.root,path)
 def test_symlink(self):
  link=self.root/'SYSTEME_JARVIS/link';link.symlink_to(self.base,target_is_directory=True)
  with self.assertRaises(a.UpdateError):a.writable_path(self.root,'SYSTEME_JARVIS/link/out.py')
 def test_windows_restart_selects_exact_markers_without_mfd(self):
  backend=a.WindowsProcesses.__new__(a.WindowsProcesses);backend.root=self.root;backend.system=self.root/'SYSTEME_JARVIS';backend.python=Path(sys.executable)
  snapshot=[{'role':'engine','marker':m} for m in (r'bridge_v191\lmu_readonly_bridge_v191.py','RUN_SETUP_LIVE_V196_56.py',r'voice_v195\live_voice_session_v195.py')]
  with patch.object(a.subprocess,'Popen') as spawn:
   backend.restart(snapshot)
  self.assertEqual(spawn.call_count,3)
  self.assertTrue(all(call.args[0][0]==sys.executable for call in spawn.call_args_list))
  self.assertTrue(spawn.call_args_list[0].args[0][1].endswith('lmu_readonly_bridge_v191.py'))
  self.assertTrue(spawn.call_args_list[-1].args[0][1].endswith('live_voice_session_v195.py'))
 def test_wrong_repo(self):
  for repo in ('https://evil/a','a/b/c','../x'):
   with self.assertRaises(a.UpdateError):a.GitHub(repo)
 def test_idle_app_not_started(self):
  self.processes.active=[];self.agent.apply(self.release());self.assertEqual(self.processes.calls,[('stop',[]),('restart',[])])
 def test_no_network_after_stop(self):
  r=self.release();original=self.source.blob
  def guarded(key):
   self.assertFalse(self.processes.calls,'No download may happen after live components stop');return original(key)
  self.source.blob=guarded;self.agent.apply(r)
 def test_copies_not_hardlinks(self):
  target=self.base/'candidate';target.mkdir();self.agent.shadow(target);clone=target/TARGET;clone.write_text('VALUE=999\n');self.assertEqual(self.file.read_text(),'VALUE=1\n')
 def test_running_process_recovery_failure_frozen(self):
  self.processes.health=[False,False]
  with self.assertRaises(a.UpdateError):self.agent.apply(self.release())
  before=len(self.processes.calls);self.agent.poll();self.assertEqual(len(self.processes.calls),before);self.assertTrue((self.storage/'recovery_blocked.json').exists())
if __name__=='__main__':unittest.main(verbosity=2)
