"""One-time local setup. No modification of JARVIS, LMU, voice or presets."""
import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
from agent import write_json,read_json
REPOSITORY='remifaugere19-glitch/JARVIS-LMU'
BRANCH='jarvis-direct'
ENGINE='MOTEUR_V196/JARVIS_V196_50_STABLE_OEIL_OPTIONNEL'
def resolve_root(path):
 p=Path(path).resolve()
 for root in (p,p/'JARVIS_LMU',p.parent if p.name=='SYSTEME_JARVIS' else p):
  if (root/'SYSTEME_JARVIS'/ENGINE/'voice_v195/live_voice_session_v195.py').is_file():return root
 raise ValueError('Choisir le dossier contenant JARVIS_LMU ou SYSTEME_JARVIS')
def setup(path,startup=True,launch=True):
 if os.name!='nt' and startup:raise ValueError('Installation Windows uniquement')
 root=resolve_root(path);system=root/'SYSTEME_JARVIS';python=system/'ENV_JARVIS_PUBLIC/Scripts/python.exe';pythonw=python.with_name('pythonw.exe')
 if os.name=='nt' and not pythonw.is_file():raise ValueError('Installer d abord JARVIS avec son installateur habituel')
 dest=system/'DIRECT_GITHUB';dest.mkdir(exist_ok=True)
 for name in ('agent.py','processes.ps1','installer.py'):
  src=Path(__file__).with_name(name);target=dest/name
  if src.resolve()!=target.resolve():shutil.copy2(src,target)
 config={'root':str(root),'python':str(python),'repository':REPOSITORY,'branch':BRANCH,'poll_seconds':15}
 write_json(dest/'config.json',config);write_json(dest/'control.json',{'paused':False})
 # Keep inventory hashes only; nothing is uploaded from the PC.
 inventory={}
 for p in (system/ENGINE).rglob('*.py'):
  if '__pycache__' not in p.parts:inventory[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
 write_json(dest/'base_inventory.json',{'root_version':'V58 or compatible','files':inventory})
 if startup:
  import winreg
  keyname='JARVISDirect_'+hashlib.sha256(str(root).lower().encode()).hexdigest()[:12]
  command=subprocess.list2cmdline([str(pythonw),str(dest/'agent.py'),'--config',str(dest/'config.json')])
  with winreg.CreateKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Run') as key:winreg.SetValueEx(key,keyname,0,winreg.REG_SZ,command)
  desktop=Path(os.environ.get('USERPROFILE',str(Path.home())))/'Desktop';desktop.mkdir(exist_ok=True)
  # VBScript escapes quotes by doubling them (JSON is not VBScript quoting).
  command_ui=subprocess.list2cmdline([str(pythonw),str(dest/'installer.py')]);vbs='Set sh=CreateObject("WScript.Shell")\nsh.Run "'+command_ui.replace('"','""')+'",0,False\n'
  (desktop/'JARVIS - mises a jour directes.vbs').write_text(vbs,encoding='utf-16')
 if launch:
  subprocess.Popen([str(pythonw),str(dest/'agent.py'),'--config',str(dest/'config.json')],cwd=dest,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 return dest

def main():
 import tkinter as tk
 from tkinter import filedialog,messagebox
 window=tk.Tk();window.title('JARVIS — modifications directes GitHub');window.geometry('720x420');window.configure(padx=22,pady=20)
 location=tk.StringVar();state=tk.StringVar(value='Choisir la copie JARVIS a mettre a jour.')
 local=Path(__file__).parent
 try:
  cfg=read_json(local/'config.json',{});location.set(cfg.get('root',''))
 except Exception:pass
 tk.Label(window,text='Modifications du code complet de JARVIS',font=('Segoe UI',15,'bold')).pack(anchor='w')
 tk.Label(window,text='Depot : '+REPOSITORY+' / '+BRANCH,wraplength=670).pack(anchor='w',pady=(10,15))
 tk.Entry(window,textvariable=location,width=95).pack(fill='x')
 tk.Button(window,text='Choisir mon dossier JARVIS',command=lambda:location.set(filedialog.askdirectory(title='Dossier de JARVIS'))).pack(anchor='w',pady=6)
 tk.Label(window,text='Une grosse correction peut relancer JARVIS et interrompre brievement les annonces.\nLMU reste ouvert. Aucun fichier complet JARVIS a retelecharger.',justify='left').pack(anchor='w',pady=10)
 def activate():
  try:dest=setup(location.get());state.set('Agent active. Canal verifie toutes les 15 secondes.');messagebox.showinfo('JARVIS','Agent installe. Tu peux garder LMU et JARVIS ouverts.\nLe panneau permet de mettre en pause ou annuler une mise a jour.')
  except Exception as e:messagebox.showerror('Installation',str(e))
 def control(action):
  try:
   root=resolve_root(location.get());dest=root/'SYSTEME_JARVIS/DIRECT_GITHUB'
   if not (dest/'config.json').exists():raise ValueError('Activer d abord cet agent')
   if action=='resume':
    (dest/'recovery_blocked.json').unlink(missing_ok=True);write_json(dest/'control.json',{'paused':False})
    cfg=read_json(dest/'config.json');pyw=Path(cfg['python']).with_name('pythonw.exe')
    subprocess.Popen([str(pyw),str(dest/'agent.py'),'--config',str(dest/'config.json')],cwd=dest,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   elif action=='pause':write_json(dest/'control.json',{'paused':True})
   else:write_json(dest/'control.json',{'command':'rollback','paused':True})
  except Exception as e:messagebox.showerror('JARVIS',str(e))
 buttons=tk.Frame(window);buttons.pack(anchor='w',pady=8)
 for label,fn in [('Activer une fois',activate),('Pause',lambda:control('pause')),('Reprendre',lambda:control('resume')),('Annuler derniere MAJ',lambda:control('rollback'))]:tk.Button(buttons,text=label,command=fn).pack(side='left',padx=(0,8))
 tk.Label(window,textvariable=state,wraplength=670,justify='left',fg='#185183').pack(anchor='w',pady=12)
 def refresh():
  try:
   root=resolve_root(location.get());s=read_json(root/'SYSTEME_JARVIS/DIRECT_GITHUB/status.json',{})
   if s:state.set(time.strftime('%H:%M:%S',time.localtime(s.get('timestamp',0)))+' — Revision '+str(s.get('revision',0))+' — '+s.get('state','')+'\n'+s.get('message',''))
  except Exception:pass
  window.after(1500,refresh)
 refresh();window.mainloop()
if __name__=='__main__':main()
