#Requires -Version 5.1
# orx_auto : tout automatisé. 1 commande = dashboard + baseline + exps + scoreboard.
# Usage : .\scripts\orx_auto.ps1
$ErrorActionPreference = "Continue"
$Repo = "C:\Users\Utilisateur\Documents\Horcruxe Labs"
Set-Location $Repo

function Say($m) { Write-Host ">> $m" }

# 1. orx présent ?
$orx = Get-Command orx -ErrorAction SilentlyContinue
if (-not $orx) {
  Say "orx absent. Télécharge l'exe Windows beta : https://openresearch.sh/download"
  Say "Mets orx.exe dans le PATH, relance ce script. En attendant : mode sans-orx."
  $modeSansOrx = $true
} else {
  $modeSansOrx = $false
  Say "orx trouvé : $($orx.Source)"
}

# 2. Dashboard auto (si orx présent)
if (-not $modeSansOrx) {
  Say "Démarrage orx up en fond..."
  Start-Process orx -ArgumentList "up" -WindowStyle Minimized
  Start-Sleep -Seconds 5
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:4791" -TimeoutSec 5 -UseBasicParsing
    Say "Dashboard OK (HTTP $($r.StatusCode))."
  } catch {
    Say "Dashboard pas encore joignable, il démarre en fond. Ouvre http://127.0.0.1:4791 dans 30s."
  }
  orx install-skills 2>$null | Out-Null
}

# 3. Baseline auto (toujours, même sans orx)
Say "Bench V2 baseline..."
python "recherches\001-memoire-araignee\code\bench_v2.py" --n 2000 --queries 30 --seed 42 --out "recherches\001-memoire-araignee\papers\draft-001-spider-hot-cache\bench-v2.json"
Say "Ledger + scoreboard..."
python "common\hypothesis_engine.py" run --id H001-math-notation --bench "bench_v2 baseline" --result "en-attente"
python "scripts\scoreboard.py"

# 4. Exps auto (si orx présent)
if (-not $modeSansOrx) {
  Say "Lancement exps miroir..."
  orx exp run H001-math-notation 2>$null
  orx exp run H003-graph-weaver 2>$null
}

Say "Fini. Voir papers/SCOREBOARD.md + http://127.0.0.1:4791"
