@echo off
rem The factory's front door on Windows: runs Level Factory with a Python it finds, so that
rem Blender and Godot are all a machine needs (roadmap 202). Every argument goes to Level
rem Factory unchanged:
rem
rem     factory setup --venv --godot C:\Godot\Godot_v4.7-stable_win64.exe
rem     factory init levels
rem
rem The Python, first found wins:
rem   1. %FACTORY_PYTHON%, when set;
rem   2. the factory's own environment, .venv\Scripts\python.exe, once `setup --venv` made it;
rem   3. the Python inside Blender: beside %BLENDER% when set, then under every
rem      "%ProgramFiles%\Blender Foundation\Blender *" (the installer's folder);
rem   4. python.exe on PATH.
rem Level Factory needs no package beyond the standard library, so any of these can run it.
rem What the TOOLS run under is a separate question, which `setup` and the doctor answer.
setlocal EnableDelayedExpansion
set "ROOT=%~dp0"
set "PY=%FACTORY_PYTHON%"
if not defined PY if exist "%ROOT%.venv\Scripts\python.exe" set "PY=%ROOT%.venv\Scripts\python.exe"
if not defined PY if defined BLENDER (
  for %%F in ("%BLENDER%") do set "BDIR=%%~dpF"
  for /d %%V in ("!BDIR!*") do if exist "%%V\python\bin\python.exe" set "PY=%%V\python\bin\python.exe"
)
if not defined PY (
  for /d %%B in ("%ProgramFiles%\Blender Foundation\Blender *") do (
    for /d %%V in ("%%B\*") do if exist "%%V\python\bin\python.exe" set "PY=%%V\python\bin\python.exe"
  )
)
if not defined PY for %%P in (python.exe) do if not "%%~$PATH:P"=="" set "PY=%%~$PATH:P"
if not defined PY (
  echo factory: no Python found. Install Blender from blender.org, or set BLENDER to its blender.exe. 1>&2
  exit /b 3
)
"%PY%" "%ROOT%level_factory\apps\cli\main.py" %*
exit /b %ERRORLEVEL%
