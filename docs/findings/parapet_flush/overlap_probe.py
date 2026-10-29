"""Count covers of one kind that overlap another of the same kind on the same face, in one Patina checkout's dressing
of a shell: same normal, same plane (within 1 cm) and height, and their spans along the wall overlapping. Spans are
Zoo's built lengths (`_COVER` span x size / 0.6, Patina's `openings._ZOO_SPAN`). Measures only; metres.

    python docs/findings/parapet_flush/overlap_probe.py <patina checkout> <shell.glb> [cover ...]
"""
import json
import os
import subprocess
import sys
import tempfile

PY = r"C:\Projects\gabagool_studios\gabagool_factory\.venv\Scripts\python.exe"
patina, glb = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
kinds = sys.argv[3:] or ["base_course", "curb", "edge_strip"]
SPAN = {"edge_strip": 2.0, "base_course": 2.0, "curb": 2.0}
with tempfile.TemporaryDirectory() as tmp:
    out = os.path.join(tmp, "x.patina.glb")
    subprocess.run([PY, "-m", "patina.cli", glb, "--mode", "vertex-color", "--out", out, "--theme", "default",
                    "--dressing", "--anchors", "--gutters"], cwd=patina, check=True, capture_output=True)
    orders = json.load(open(out[:-4] + ".dressing.json", encoding="utf-8"))["orders"]
for kind in kinds:
    os_ = [o for o in orders if o["cover"] == kind]
    pairs = 0
    for i, a in enumerate(os_):
        for b in os_[i + 1:]:
            if a["normal"] != b["normal"] or abs(a["pos"][2] - b["pos"][2]) > 0.01:
                continue
            ta = a.get("tangent") or [1, 0, 0]
            ax = 0 if abs(ta[0]) > 0.5 else 1
            if abs(a["pos"][1 - ax] - b["pos"][1 - ax]) > 0.01:
                continue
            la = max(0.2, SPAN[kind] * max(a.get("size", 0.6), 0.1) / 0.6)
            lb = max(0.2, SPAN[kind] * max(b.get("size", 0.6), 0.1) / 0.6)
            if abs(a["pos"][ax] - b["pos"][ax]) < (la + lb) / 2.0:
                pairs += 1
    print(kind, "orders", len(os_), "overlapping pairs", pairs)
