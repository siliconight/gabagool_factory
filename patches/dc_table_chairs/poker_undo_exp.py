"""Is the undo rule what took two bar video poker machines? Copy the dc_seats clone's modules into a fresh temp dir,
exempt `how == "stool"` from the undo there, refurnish final_stand and strip_club_a03 (as the clone's specs stand, in
memory) with both module sets in separate processes, and count video_poker_bar per room tag. Writes nothing in the
clone."""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

CLONE = r"C:\Users\Brannen\AppData\Local\Temp\claude\C--Projects-gabagool-studios-gabagool-factory\27f14f8b-7ce5-44c0-a704-178a824035d7\scratchpad\dc_seats"
PROBE = r'''
import collections, copy, json, os, re, sys
sys.path.insert(0, sys.argv[1])
import level_design as L, migrate_furnish_recipes as M
assert os.path.samefile(L.__file__, os.path.join(sys.argv[1], "level_design.py"))
for name in ("final_stand", "strip_club_a03"):
    d = json.load(open(os.path.join(sys.argv[2], "specs", name + ".json"), encoding="utf-8"))
    M.migrate(d)
    c = collections.Counter(m.group(1) for v in d["volumes"]
                            for m in [re.match(r"^video_poker_bar_(r[0-9a-f]{8})_\d+$", v["name"])] if m)
    print(name, dict(sorted(c.items())))
'''
tmp = tempfile.mkdtemp(prefix="dc_poker_exp_")
for f in glob.glob(os.path.join(CLONE, "*.py")) + [os.path.join(CLONE, "agent_contract.json")]:
    shutil.copy2(f, tmp)
p = os.path.join(tmp, "level_design.py")
t = open(p, encoding="utf-8").read()
old = "                        if lo >= 1 and not got:\n"
assert t.count(old) == 1
open(p, "w", encoding="utf-8", newline="\n").write(t.replace(old, "                        if lo >= 1 and not got and how != \"stool\":\n"))
probe = os.path.join(tmp, "_probe.py")
open(probe, "w", encoding="utf-8").write(PROBE)
for label, mods in (("the clone (stools undone too)", CLONE), ("stools exempt from the undo", tmp)):
    r = subprocess.run([sys.executable, "-B", probe, mods, CLONE], capture_output=True, text=True)
    print("==", label)
    print(r.stdout.strip() or r.stderr[-1500:])
shutil.rmtree(tmp)
