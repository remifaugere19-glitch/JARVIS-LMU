param([ValidateSet('snapshot','stop')][string]$Action)
$ErrorActionPreference='Stop'
$request=Get-Content -LiteralPath $env:JARVIS_DIRECT_REQUEST -Raw | ConvertFrom-Json
$root=[IO.Path]::GetFullPath([string]$request.root).TrimEnd('\')
$engine=Join-Path $root 'SYSTEME_JARVIS\MOTEUR_V196\JARVIS_V196_50_STABLE_OEIL_OPTIONNEL'
$interface=Join-Path $root 'SYSTEME_JARVIS\INTERFACE'
function Classify($p) {
 $name=([string]$p.Name).ToLowerInvariant();$cmd=[string]$p.CommandLine
 # LMU, Steam, Discord and unrelated Python/browser processes never match.
 if ($name -in @('python.exe','pythonw.exe')) {
  foreach($relative in @('voice_v195\live_voice_session_v195.py','bridge_v191\lmu_readonly_bridge_v191.py','RUN_SETUP_LIVE_V196_56.py')) {
   $marker=Join-Path $engine $relative
   if ($cmd.IndexOf($marker,[StringComparison]::OrdinalIgnoreCase) -ge 0) {return @{role='engine';marker=$relative}}
  }
  if ($cmd.IndexOf((Join-Path $interface 'server.py'),[StringComparison]::OrdinalIgnoreCase) -ge 0) {return @{role='interface';marker='INTERFACE/server.py'}}
 }
 if ($name -eq 'msedge.exe' -and $cmd.IndexOf((Join-Path $interface '.profil_fenetre'),[StringComparison]::OrdinalIgnoreCase) -ge 0) {return @{role='edge';marker='INTERFACE/edge'}}
 $exe=Join-Path $engine 'background_mfd_v194\bin\Debug\net10.0\JARVIS_V194.exe'
 if ($name -eq 'jarvis_v194.exe' -and [string]::Equals([string]$p.ExecutablePath,$exe,[StringComparison]::OrdinalIgnoreCase)) {return @{role='mfd';marker='background_mfd_v194/JARVIS_V194.exe'}}
 return $null
}
if ($Action -eq 'snapshot') {
 $result=@(Get-CimInstance Win32_Process | ForEach-Object {
  $match=Classify $_
  if ($null -ne $match) {@{pid=[int]$_.ProcessId;created=[string]$_.CreationDate.Ticks;role=$match.role;marker=$match.marker}}
 })
 ConvertTo-Json -InputObject $result -Depth 5 -Compress
} else {
 foreach($item in $request.items) {
  $pidValue=[int]$item.pid
  $p=Get-CimInstance Win32_Process -Filter "ProcessId=$pidValue"
  if ($null -eq $p) {continue}
  $match=Classify $p
  if ($null -eq $match -or $match.marker -ne $item.marker -or [string]$p.CreationDate.Ticks -ne [string]$item.created) {throw 'Processus modifie : arret refuse'}
  Stop-Process -Id $pidValue -ErrorAction Stop
 }
 '[]'
}
