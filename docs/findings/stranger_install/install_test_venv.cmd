@echo off
rem Roadmap 202's install test, the page's own setup line: START_HERE.md's commands, typed into
rem cmd.exe in a fresh unpack, with `setup --venv` -- the one step that touches the network. The
rem walker said yes to the PyPI download on 2026-10-11; install tests 1-3 had deviated to
rem `--python <this machine's 3.14>` while that yes was waited for (install_test.cmd).
rem   install_test_venv.cmd <factory folder> <log folder>
setlocal
set "F=%~1"
set "LOG=%~2"
cd /d "%F%" || exit /b 9
echo == setup %TIME%
call .\factory setup --venv --godot C:\Godot\4.7\Godot_v4.7-stable_win64.exe > "%LOG%\setup.txt" 2>&1
echo setup exit %ERRORLEVEL%
echo == make %TIME%
call .\factory -C levels make docs\first_level\batch.json > "%LOG%\make.txt" 2>&1
echo make exit %ERRORLEVEL%
echo == walk %TIME%
call .\factory -C levels walk restaurant_row_001 > "%LOG%\walk.txt" 2>&1
echo walk exit %ERRORLEVEL%
echo == done %TIME%
