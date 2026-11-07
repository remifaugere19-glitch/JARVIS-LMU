"""JARVIS Direct: transactional, changed-file GitHub delivery. Python stdlib only."""
from __future__ import annotations
import argparse,base64,hashlib,json,os,re,shutil,subprocess,sys,tempfile,time,urllib.request,urllib.error
from pathlib import Path,PurePosixPath
PROTOCOL=1
MAX_FILE=32*1024*1024
MAX_TOTAL=128*1024*1024
TEXT={'.py','.json','.txt','.md','.ps1','.bat','.vbs','.html','.css','.js','.cs','.csproj','.toml','.ini','.cfg','.yaml','.yml','.csv'}
SUFFIXES=TEXT|{'.exe','.dll','.pyd','.png','.jpg','.svg','.wav','.onnx','.bin'}
class UpdateError(Exception):pass

def digest(data):return hashlib.sha256(data).hexdigest()
def atomic(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.tmp')
 with open(tmp,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)
def write_json(path,data):atomic(path,json.dumps(data,ensure_ascii=False,indent=2).encode())
def read_json(path,default=None):
 if not Path(path).exists():return default
 return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None

def safe_path(root,name):
 if not isinstance(name,str) or not name or '\\' in name or ':' in name or '\x00' in name:raise UpdateError('Chemin refuse')
 p=PurePosixPath(name)
 if p.is_absolute() or any(x in ('..','.') or not x or x[-1:] in ('.',' ') for x in p.parts):raise UpdateError('Chemin refuse')
 for x in p.parts:
  if re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?',x):raise UpdateError('Nom Windows reserve')
 target=Path(root).joinpath(*p.parts);resolved=target.resolve();base=Path(root).resolve()
 if resolved==base or not resolved.is_relative_to(base):raise UpdateError('Chemin sortant')
 if any(x.is_symlink() for x in [target,*target.parents] if x.is_relative_to(base)):raise UpdateError('Lien symbolique refuse')
 return target

def writable_path(root,name,protected=False):
 p=safe_path(root,name);parts=PurePosixPath(name).parts;low=[x.lower() for x in parts]
 if parts[0]!='SYSTEME_JARVIS' and len(parts)!=1:raise UpdateError('Hors application JARVIS')
 if p.suffix.lower() not in SUFFIXES:raise UpdateError('Type de fichier non pris en charge')
 if any(x.startswith('env_') or x in ('direct_github','journaux_diagnostic','anciennes_versions','__pycache__','memory','runtime') for x in low):raise UpdateError('Donnees locales ou agent proteges')
 if p.name.lower() in ('runtime_source_v191.json','preferences_interface.json','connexion_v196.json','etat_moteur_v196.json'):raise UpdateError('Etat local protege')
 is_protected=('/braking_live_v19650/data/' in '/'+name.lower() or '/master' in '/'+name.lower())
 if is_protected and not protected:raise UpdateError('Modification des reperes non autorisee par ce correctif')
 return p

class GitHub:
 def __init__(self,repo,branch='jarvis-direct'):
  if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9_.-]+',repo) or repo.split('/')[-1] in ('.','..'):raise UpdateError('Depot invalide')
  if not re.fullmatch(r'[A-Za-z0-9_.-]+',branch) or branch in ('.','..'):raise UpdateError('Branche invalide')
  self.base=f'https://raw.githubusercontent.com/{repo}/{branch}/';self.etag=None
 def get(self,path,limit=MAX_FILE):
  if not re.fullmatch(r'[A-Za-z0-9_./-]+',path) or '..' in path:raise UpdateError('Objet distant invalide')
  request=urllib.request.Request(self.base+path,headers={'User-Agent':'JARVIS-Direct/1','Cache-Control':'no-cache'})
  try:
   with urllib.request.urlopen(request,timeout=15) as f:
    if f.geturl().split('/')[2]!='raw.githubusercontent.com':raise UpdateError('Redirection inattendue')
    data=f.read(limit+1)
  except urllib.error.HTTPError as e:raise UpdateError('GitHub HTTP '+str(e.code)) from None
  if len(data)>limit:raise UpdateError('Objet distant trop volumineux')
  return data
 def channel(self):return json.loads(self.get('jarvis-updates/channel.json',2*1024*1024))
 def blob(self,hash_value):
  if not sha(hash_value):raise UpdateError('Empreinte invalide')
  data=self.get('jarvis-updates/blobs/'+hash_value)
  if digest(data)!=hash_value:raise UpdateError('Empreinte du telechargement incorrecte')
  return data

class WindowsProcesses:
 def __init__(self,root,python):
  if os.name!='nt':raise UpdateError('Gestion des processus reservee a Windows')
  self.root=Path(root).resolve();self.system=self.root/'SYSTEME_JARVIS';self.python=Path(python)
  self.ps=Path(__file__).with_name('processes.ps1');self.work=self.system/'DIRECT_GITHUB'
 def call(self,action,items=None):
  self.work.mkdir(exist_ok=True);request=self.work/'process_request.json';write_json(request,{'root':str(self.root),'items':items or []})
  env=os.environ.copy();env['JARVIS_DIRECT_REQUEST']=str(request)
  r=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(self.ps),'-Action',action],env=env,capture_output=True,text=True,timeout=30,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  if r.returncode:raise UpdateError('Controle processus Windows en echec : '+r.stderr[-1000:])
  return json.loads(r.stdout.strip() or '[]')
 def snapshot(self):return self.call('snapshot')
 def stop(self,snapshot):self.call('stop',snapshot)
 def restart(self,snapshot):
  roles={p['role'] for p in snapshot};env=os.environ.copy();env['PATH']=str(self.python.parent)+os.pathsep+env.get('PATH','')
  engine=self.system/'MOTEUR_V196/JARVIS_V196_50_STABLE_OEIL_OPTIONNEL'
  env['LMU_ENGINEER_DATA_DIR']=str(engine/'TROISIEME_OEIL/RUNTIME')
  flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
  if 'mfd' in roles:
   # Only a real MFD update uses its existing administrator launcher.
   # Routine Python updates leave the already-running MFD untouched.
   launcher=engine/'background_mfd_v194/LANCER_V194_BACKGROUND_ADMIN.bat'
   subprocess.Popen(['cmd.exe','/d','/c',str(launcher)],cwd=launcher.parent,env=env,creationflags=flags)
   ready=subprocess.run([str(self.python),str(engine/'TOOLS/wait_mfd_ready.py')],cwd=engine,env=env,capture_output=True,timeout=40,creationflags=flags)
   if ready.returncode:raise UpdateError('MFD non pret apres relance')
  markers={p['marker'] for p in snapshot if p['role']=='engine'}
  for marker in (r'bridge_v191\lmu_readonly_bridge_v191.py','RUN_SETUP_LIVE_V196_56.py',r'voice_v195\live_voice_session_v195.py'):
   if marker not in markers:continue
   script=engine.joinpath(*marker.replace('\\','/').split('/'))
   logs=self.system/'JOURNAUX_DIAGNOSTIC';logs.mkdir(exist_ok=True)
   log=logs/('direct_'+script.stem+'_'+str(time.time_ns())+'.log')
   with open(log,'ab',buffering=0) as output:
    subprocess.Popen([str(self.python),str(script)],cwd=engine,env=env,stdout=output,stderr=output,stdin=subprocess.DEVNULL,creationflags=flags)
  if 'interface' in roles:
   pyw=self.python.with_name('pythonw.exe');subprocess.Popen([str(pyw),str(self.system/'INTERFACE/server.py')],cwd=self.system/'INTERFACE',env=env,creationflags=flags)
 def healthy(self,snapshot,timeout=75):
  expected={p['marker'] for p in snapshot if p['role']!='edge'}
  if not expected:return True
  deadline=time.monotonic()+timeout;stable=0
  while time.monotonic()<deadline:
   now=self.snapshot();markers=[p['marker'] for p in now]
   okay=all(markers.count(m)==1 for m in expected)
   if okay and any('live_voice_session_v195.py' in m for m in expected):
    hb=read_json(self.system/'INTERFACE/etat_moteur_v196.json',{})
    voice_pids={p['pid'] for p in now if 'live_voice_session_v195.py' in p['marker']}
    okay=hb.get('pid') in voice_pids and -2<time.time()-float(hb.get('timestamp',0))<8
   stable=stable+1 if okay else 0
   if stable>=3:return True
   time.sleep(1)
  return False

class Agent:
 def __init__(self,root,storage,source,processes,python=None):
  self.root=Path(root).resolve();self.storage=Path(storage).resolve();self.storage.mkdir(parents=True,exist_ok=True)
  self.source=source;self.processes=processes;self.python=str(python or sys.executable)
  self.state_path=self.storage/'state.json';self.pending=self.storage/'transaction.json';self.status_path=self.storage/'status.json'
  self.blobs={}
  self.state=read_json(self.state_path,{'protocol':1,'revision':0,'blocked':[]})
  if self.state.get('protocol')!=1 or type(self.state.get('revision')) is not int:raise UpdateError('Etat local invalide')
 def blob(self,hash_value):
  if not sha(hash_value):raise UpdateError('Empreinte invalide')
  if hash_value not in self.blobs:
   data=self.source.blob(hash_value)
   if len(data)>MAX_FILE or digest(data)!=hash_value:raise UpdateError('Objet telecharge incorrect')
   self.blobs[hash_value]=data
  return self.blobs[hash_value]
 def scope(self,snapshot,release):
  paths=[x['path'].lower() for x in release['files']];roles={'engine'}
  if any('/interface/' in p or p.endswith(('.bat','.vbs','.ps1')) for p in paths):roles|={'interface','edge'}
  if any('/background_mfd_v194/' in p for p in paths):roles.add('mfd')
  return [p for p in snapshot if p['role'] in roles]
 def status(self,state,message,**extra):
  result={'agent_pid':os.getpid(),'state':state,'message':message,'revision':self.state['revision'],'timestamp':time.time(),**extra}
  write_json(self.status_path,result);return result
 def validate(self,release):
  if not isinstance(release,dict) or set(release)-{'revision','id','title','files','checks','restart','allow_protected_data'}:raise UpdateError('Format du correctif invalide')
  if type(release.get('revision')) is not int or release['revision']!=self.state['revision']+1:raise UpdateError('Revision precedente manquante')
  if not isinstance(release.get('id'),str) or not re.fullmatch('[A-Za-z0-9_.-]{1,80}',release['id']):raise UpdateError('Identifiant invalide')
  entries=release.get('files');checks=release.get('checks')
  if not isinstance(entries,list) or not 1<=len(entries)<=1000 or not isinstance(checks,list) or not 1<=len(checks)<=50:raise UpdateError('Fichiers et tests obligatoires')
  if release.get('restart')!=True:raise UpdateError('Un changement de code exige une relance controlee')
  targets=set();total=0
  for entry in entries:
   if not isinstance(entry,dict) or set(entry)!={'path','before','after'}:raise UpdateError('Entree de fichier invalide')
   p=writable_path(self.root,entry['path'],release.get('allow_protected_data') is True);key=str(p.resolve()).casefold()
   if key in targets:raise UpdateError('Chemin duplique')
   targets.add(key)
   if any(x is not None and not sha(x) for x in (entry['before'],entry['after'])) or entry['before']==entry['after']:raise UpdateError('Empreintes invalides')
   if p.exists() and not p.is_file():raise UpdateError('Cible existante non reguliere')
   current=digest(p.read_bytes()) if p.is_file() else None
   if current!=entry['before']:raise UpdateError('Base locale differente : '+entry['path'])
   if entry['after'] is not None:
    blob=self.blob(entry['after']);total+=len(blob)
    if len(blob)>MAX_FILE or total>MAX_TOTAL:raise UpdateError('Correctif trop volumineux')
    if p.suffix.lower()=='.py':compile(blob,entry['path'],'exec')
    if p.suffix.lower()=='.json':json.loads(blob)
  for check in checks:
   if not isinstance(check,dict) or set(check)!={'name','sha256','timeout'} or not re.fullmatch(r'test_[A-Za-z0-9_]+\.py',check['name']):raise UpdateError('Test invalide')
   if not sha(check['sha256']) or type(check['timeout']) is not int or not 1<=check['timeout']<=180:raise UpdateError('Test invalide')
  return release
 def shadow(self,candidate):
  # Tests run against copies, never hardlinks to the live installation.
  total=0
  for base,dirs,files in os.walk(self.root,followlinks=False):
   dirs[:]=[d for d in dirs if not Path(base,d).is_symlink() and not d.lower().startswith('env_') and d.lower() not in ('direct_github','journaux_diagnostic','anciennes_versions','__pycache__','.git','runtime')]
   for name in files:
    p=Path(base,name)
    if p.is_symlink() or p.suffix.lower() not in TEXT|{'.exe','.dll','.pyd'} or p.stat().st_size>32*1024*1024:continue
    total+=p.stat().st_size
    if total>128*1024*1024:raise UpdateError('Copie de verification trop volumineuse')
    q=candidate/p.relative_to(self.root);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 def check_candidate(self,release,stage):
  candidate=stage/'candidate'/'JARVIS_LMU';candidate.mkdir(parents=True);self.shadow(candidate)
  for e in release['files']:
   p=safe_path(candidate,e['path'])
   if e['after'] is None:p.unlink(missing_ok=True)
   else:atomic(p,self.blob(e['after']))
  check_dir=candidate.parent/'VALIDATION_DIRECTE';check_dir.mkdir();env=os.environ.copy();env['JARVIS_CANDIDATE_ROOT']=str(candidate);env['PYTHONDONTWRITEBYTECODE']='1'
  # Do not import live modules through PYTHONPATH while testing copies.
  env.pop('PYTHONPATH',None)
  for spec in release['checks']:
   code=self.blob(spec['sha256']);compile(code,spec['name'],'exec');path=check_dir/spec['name'];path.write_bytes(code)
   run=subprocess.run([self.python,'-B',str(path)],cwd=candidate.parent,env=env,capture_output=True,timeout=spec['timeout'])
   atomic(stage/(spec['name']+'.log'),run.stdout[-200000:]+run.stderr[-200000:])
   if run.returncode:raise UpdateError('Test en echec : '+spec['name'])
 def backup(self,release,snapshot):
  folder=self.storage/'ANCIENNES_VERSIONS'/f"revision_{self.state['revision']:06d}_avant_{release['id']}";folder.mkdir(parents=True,exist_ok=False)
  for e in release['files']:
   p=safe_path(self.root,e['path'])
   if p.is_file():atomic(safe_path(folder,e['path']),p.read_bytes())
  journal={'release':release,'snapshot':snapshot,'previous_state':self.state,'backup':str(folder),'created':time.time()}
  write_json(folder/'manifest.json',journal);write_json(self.pending,journal);return journal
 def restore(self,journal):
  folder=Path(journal['backup']).resolve()
  if not folder.is_relative_to((self.storage/'ANCIENNES_VERSIONS').resolve()):raise UpdateError('Sauvegarde hors dossier')
  for e in journal['release']['files']:
   p=safe_path(self.root,e['path'])
   if e['before'] is None:p.unlink(missing_ok=True)
   else:
    data=safe_path(folder,e['path']).read_bytes()
    if digest(data)!=e['before']:raise UpdateError('Sauvegarde corrompue')
    atomic(p,data)
  self.state=journal['previous_state'];write_json(self.state_path,self.state)
 def rollback(self,journal):
  roles={p['role'] for p in journal['snapshot']}
  fresh=[p for p in self.processes.snapshot() if p['role'] in roles];self.processes.stop(fresh);self.restore(journal)
  self.processes.restart(journal['snapshot'])
  if not self.processes.healthy(journal['snapshot']):raise UpdateError('Ancienne version restauree mais relance non confirmee')
  self.state.setdefault('blocked',[]).append(journal['release']['id']);write_json(self.state_path,self.state);self.pending.unlink(missing_ok=True)
 def recover(self):
  if not self.pending.exists():return
  journal=read_json(self.pending);self.status('RECUPERATION','Restauration d une mise a jour interrompue')
  self.rollback(journal);self.status('RESTAURE','Version precedente restauree apres interruption')
 def apply(self,release):
  self.blobs={}
  if release.get('id') in self.state.get('blocked',[]):return self.status('BLOQUE','Ce correctif a deja ete annule ; attendre une correction',update_id=release.get('id'))
  self.status('VERIFICATION','Telechargement et tests du correctif',update_id=release.get('id'))
  self.validate(release)
  with tempfile.TemporaryDirectory(prefix='verification_',dir=self.storage) as tmp:
   stage=Path(tmp);self.check_candidate(release,stage)
   # Recheck preimages after tests and before stopping any JARVIS component.
   self.validate(release);snapshot=self.scope(self.processes.snapshot(),release);journal=self.backup(release,snapshot)
   self.status('APPLICATION','Sauvegarde prete ; relance de JARVIS si actif',update_id=release['id'])
   try:
    self.processes.stop(snapshot)
    for e in release['files']:
     p=writable_path(self.root,e['path'],release.get('allow_protected_data') is True)
     if e['after'] is None:p.unlink(missing_ok=True)
     else:atomic(p,self.blob(e['after']))
    self.processes.restart(snapshot)
    if not self.processes.healthy(snapshot):raise UpdateError('Nouveau JARVIS non operationnel')
    self.state={**self.state,'revision':release['revision'],'last_update':release['id']};write_json(self.state_path,self.state)
    self.pending.unlink();return self.status('APPLIQUE','Correctif applique ; LMU conserve ouvert',update_id=release['id'])
   except Exception as error:
    try:self.rollback(journal)
    except Exception as recovery_error:
     write_json(self.storage/'recovery_blocked.json',{'message':str(recovery_error)})
     self.status('RESTAURATION_A_VERIFIER',str(recovery_error),update_id=release['id']);raise
    return self.status('ANNULE','Ancienne version restauree : '+str(error),update_id=release['id'])
 def poll(self):
  if (self.storage/'recovery_blocked.json').exists():return self.status('RESTAURATION_A_VERIFIER','Restauration interrompue : reprendre depuis le panneau local')
  self.recover()
  control=read_json(self.storage/'control.json',{})
  if control.get('command')=='rollback':
   control['command']=None;write_json(self.storage/'control.json',control)
   candidates=[]
   for f in (self.storage/'ANCIENNES_VERSIONS').glob('*/manifest.json'):
    item=read_json(f)
    if item['release']['revision']==self.state['revision']:candidates.append(item)
   if not candidates:return self.status('AUCUNE_SAUVEGARDE','Aucune mise a jour a annuler')
   item=max(candidates,key=lambda x:x['created']);write_json(self.pending,item);self.rollback(item)
   return self.status('ANNULE','Derniere mise a jour annulee depuis le panneau')
  if control.get('paused'):return self.status('PAUSE','Mises a jour automatiques en pause')
  channel=self.source.channel()
  if not isinstance(channel,dict) or channel.get('protocol')!=1 or not isinstance(channel.get('updates'),list):raise UpdateError('Canal incompatible')
  updates=sorted(channel['updates'],key=lambda x:x.get('revision',-1))
  if len({x.get('revision') for x in updates})!=len(updates):raise UpdateError('Revisions dupliquees')
  last_result=None
  for update in updates:
   if update.get('revision',0)>self.state['revision']:
    result=self.apply(update)
    if result['state']!='APPLIQUE':return result
    last_result=result
  if last_result:return last_result
  return self.status('A_JOUR','Canal verifie ; aucun nouveau correctif')

class InstanceLock:
 def __init__(self,path):self.path=Path(path)
 def __enter__(self):
  self.file=open(self.path,'a+b')
  if self.file.tell()==0:self.file.write(b'0');self.file.flush()
  self.file.seek(0)
  try:
   if os.name=='nt':
    import msvcrt;msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
   else:
    import fcntl;fcntl.flock(self.file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
  except OSError:self.file.close();raise UpdateError('Agent deja actif')
  return self
 def __exit__(self,*args):self.file.close()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--once',action='store_true');args=ap.parse_args()
 config=read_json(args.config);root=Path(config['root']).resolve();storage=Path(args.config).resolve().parent
 backend=WindowsProcesses(root,config['python']);source=GitHub(config['repository'],config.get('branch','jarvis-direct'));agent=Agent(root,storage,source,backend,config['python'])
 with InstanceLock(storage/'agent.lock'):
  while True:
   try:agent.poll()
   except Exception as exc:
    # No credentials or sensitive headers are logged; this public channel has no token.
    agent.status('ERREUR',str(exc))
   if args.once:break
   time.sleep(max(10,min(300,int(config.get('poll_seconds',15)))))
if __name__=='__main__':main()
