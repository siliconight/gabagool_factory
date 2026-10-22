"""Slim a `build.py --all` log to what it decided: every spec it built, the tracebacks it printed, and its exit code
(the shape of `patches/dc_ramp_cut/build.out.txt`).

    python patches/dc_desk_move/slim_build_log.py <full log> <out.txt>

Copied from `patches/dc_table_chairs/slim_build_log.py`, its version changed.
"""
import re
import sys

lines = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
# one `[build] <spec>.json -> <spec>.glb` line a spec: the facades print "built FACADE", the rest "built '<id>'",
# so counting either of those alone misses the other (it first read 132 of 159 that way)
built = [ln for ln in lines if ln.startswith("[build] ") and " -> " in ln and ln.endswith(".glb")]
tracebacks = sum(1 for ln in lines if ln.startswith("Traceback"))
exits = [ln for ln in lines if re.match(r"^build exit \d+$", ln)]
if len(exits) != 1:
    raise SystemExit("FAIL: the log carries %d exit lines, not one" % len(exits))
out = ["# build.py --all on Deli Counter 0.256.0, slimmed from %d lines of Blender output to what it decided:" % len(lines),
       "# every spec it built, the tracebacks it printed, and its exit code",
       "built %d specs; tracebacks %d; %s" % (len(built), tracebacks, exits[0])] + built
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print(out[2])
