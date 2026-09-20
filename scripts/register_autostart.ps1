#Requires -Version 5.1
# Demarrage auto Horcruxe SANS admin : dossier Startup (Task Scheduler casse sur cette machine).
# Installe avec : .\scripts\register_autostart.ps1
# Retire avec : Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\horcruxe-lab.bat"

$ErrorActionPreference = "Stop"
$bat = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\horcruxe-lab.bat"
$body = "@echo off`r`nstart /min `"`" `"%USERPROFILE%\.local\bin\orx.exe`" up --no-browser`r`ncd /d `"C:\Users\Utilisateur\Documents\Horcruxe Labs`"python scripts\agent_loop.py --once`r`n"
Set-Content -Path $bat -Value $body -Encoding Ascii
Write-Host "Autostart installe : $bat"
