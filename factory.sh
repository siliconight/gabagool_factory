#!/bin/sh
# The factory's front door on Linux: runs Level Factory with a Python it finds, so that Blender
# and Godot are all a machine needs (roadmap 202). Every argument goes to Level Factory unchanged:
#
#     ./factory.sh setup --venv --godot ~/Godot_v4.7-stable_linux.x86_64
#     ./factory.sh init levels
#
# The Python, first found wins:
#   1. $FACTORY_PYTHON, when set;
#   2. the factory's own environment, .venv/bin/python, once `setup --venv` made it;
#   3. the Python inside Blender's archive from blender.org: beside $BLENDER when set, then the
#      `blender` on PATH, then ~/blender*/blender and /opt/blender*/blender;
#   4. python3 on PATH. A distribution's Blender uses the system Python and carries none of its
#      own, and some distributions leave `venv` out of python3 (Debian and Ubuntu package it as
#      python3-venv), so Blender's archive is the one to install.
# Level Factory needs no package beyond the standard library, so any of these can run it.
# What the TOOLS run under is a separate question, which `setup` and the doctor answer.
ROOT=$(cd "$(dirname "$0")" && pwd)
PY="${FACTORY_PYTHON:-}"
if [ -z "$PY" ] && [ -x "$ROOT/.venv/bin/python" ]; then
  PY="$ROOT/.venv/bin/python"
fi
if [ -z "$PY" ]; then
  for cand in "${BLENDER:-}" "$(command -v blender 2>/dev/null)" "$HOME"/blender*/blender /opt/blender*/blender; do
    [ -n "$cand" ] && [ -x "$cand" ] || continue
    dir=$(dirname "$(readlink -f "$cand")")
    for p in "$dir"/*/python/bin/python3.[0-9]*; do
      case "$p" in *-config) continue ;; esac
      [ -x "$p" ] && PY="$p"
    done
    [ -n "$PY" ] && break
  done
fi
if [ -z "$PY" ]; then
  PY=$(command -v python3 2>/dev/null)
fi
if [ -z "$PY" ]; then
  echo "factory: no Python found. Install Blender from blender.org, or set BLENDER to its blender." >&2
  exit 3
fi
exec "$PY" "$ROOT/level_factory/apps/cli/main.py" "$@"
