@echo off
REM 1-clic : bench V2 + weaver + scoreboard, sans terminal à taper
cd /d "%~dp0"
python scripts\agent_loop.py --once
pause
