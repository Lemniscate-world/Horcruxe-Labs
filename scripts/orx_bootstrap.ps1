#Requires -Version 5.1
# Bootstrap OpenResearch pour Horcruxe Labs (Windows)
# Usage : .\scripts\orx_bootstrap.ps1

$ErrorActionPreference = "Stop"
$Repo = "C:\Users\Utilisateur\Documents\Horcruxe Labs"

if (-not (Get-Command orx -ErrorAction SilentlyContinue)) {
  Write-Host "orx introuvable. Telecharge l'exe Windows beta sur https://openresearch.sh/download"
  Write-Host "puis relance ce script."
  exit 1
}

Set-Location $Repo
git rev-parse --is-inside-work-tree | Out-Null
Write-Host "== orx up (dashboard local) =="
Start-Process orx -ArgumentList "up"
Write-Host "Dashboard : http://127.0.0.1:4791"
Write-Host ""
Write-Host "Ensuite dans le dashboard : New Project -> Existing repo -> $Repo (branche main)"
Write-Host "Experiences miroir de hypotheses/ledger.json :"
Write-Host "  orx exp run H001-math-notation"
Write-Host "  orx exp run H003-graph-weaver"
orx install-skills
Write-Host "Skills installees pour OpenCode."
