@echo off
rem Roadmap 202's install test: START_HERE.md's commands, typed into cmd.exe in a fresh unpack.
rem   install_test.cmd <factory folder> <log folder>
rem One deviation from the page, counted: `setup --venv` downloads from PyPI, which waits for the
rem walker's yes, so `--python` names this machine's own 3.14.4, which carries the three packages.
setlocal
set "F=%~1"
set "LOG=%~2"
cd /d "%F%" || exit /b 9
echo == setup %TIME%
call .\factory setup --python C:\Users\Brannen\AppData\Local\Python\pythoncore-3.14-64\python.exe --godot C:\Godot\4.7\Godot_v4.7-stable_win64.exe > "%LOG%\setup.txt" 2>&1
echo setup exit %ERRORLEVEL%
echo == make %TIME%
call .\factory -C levels make docs\first_level\batch.json > "%LOG%\make.txt" 2>&1
echo make exit %ERRORLEVEL%
echo == walk %TIME%
call .\factory -C levels walk restaurant_row_001 > "%LOG%\walk.txt" 2>&1
echo walk exit %ERRORLEVEL%
echo == done %TIME%
