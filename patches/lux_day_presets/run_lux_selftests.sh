#!/bin/sh
# Every Lux self-test in a project, each as its docstring says: headless, but streetlight_shadow_selftest.gd windowed
# under gl_compatibility (it reads frames). Prints one line a test with its exit code.
P="$1"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
for f in $(ls "$P/tools" | grep "_selftest.gd$"); do
  if [ "$f" = "streetlight_shadow_selftest.gd" ]; then
    "$G" --rendering-method gl_compatibility --path "$P" -s "res://tools/$f" < /dev/null > /dev/null 2>&1
    echo "$f (windowed) exit $?"
  else
    "$G" --headless --path "$P" -s "res://tools/$f" < /dev/null > /dev/null 2>&1
    echo "$f exit $?"
  fi
done
