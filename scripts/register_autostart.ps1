#Requires -Version 5.1
# Demarrage auto Horcruxe : daemon orx headless + 1 tour agent, au logon.
# Installe avec : .\scripts\register_autostart.ps1
# Retire avec : Unregister-ScheduledTask -TaskName HorcruxeLab -Confirm:$false

$ErrorActionPreference = "Stop"
$Repo = "C:\Users\Utilisateur\Documents\Horcruxe Labs"
$Orx = "$env:USERPROFILE\.local\bin\orx.exe"

$action1 = New-ScheduledTaskAction -Execute $Orx -Argument "up --no-browser" -WorkingDirectory $Repo
$action2 = New-ScheduledTaskAction -Execute "python" -Argument "scripts\agent_loop.py --once" -WorkingDirectory $Repo
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName HorcruxeLab -Action @($action1, $action2) -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Host "Autostart installe : orx daemon + tour agent a chaque ouverture de session."
