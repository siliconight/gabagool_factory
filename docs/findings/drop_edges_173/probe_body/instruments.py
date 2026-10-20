"""Write a drop-edge instrument at several lattice phases: any walkable_edge.gd with its two SEAM_NUDGE constants
replaced, one file a phase, for gate_ab.py to run side by side -- the phase sweep's `phase_instruments.py`, taking the
instrument as an argument so the probe-body change (Level Factory 0.222.0) and the instrument before it are swept
alike. A generator: it refuses if either constant is not found exactly once, and prints what it wrote.

    python instruments.py <walkable_edge.gd> <out dir> <prefix>

The phases span the gate's 0.5 m cell on both axes. Each keeps the shipped instrument's odd millimetres (3.1 and
2.3), so no phase puts a query on a round coordinate, and moves the lattice a quarter cell at a time.
"""
import hashlib
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
PHASES = {
    "p00": (0.0031, 0.0023),   # the shipped phase, the control
    "p11": (0.1281, 0.1273),
    "p22": (0.2531, 0.2523),
    "p33": (0.3781, 0.3773),
    "p20": (0.2531, 0.0023),
    "p02": (0.0031, 0.2523),
}
out = Path(sys.argv[2])
prefix = sys.argv[3]
out.mkdir(parents=True, exist_ok=True)
text = SRC.read_bytes().decode("utf-8")
print("source", SRC, hashlib.sha256(SRC.read_bytes()).hexdigest()[:16])
for name, (dx, dz) in PHASES.items():
    t = text
    for const, val in (("SEAM_NUDGE_X", dx), ("SEAM_NUDGE_Z", dz)):
        old = "const %s := " % const
        lines = [ln for ln in t.split("\n") if ln.startswith(old)]
        assert len(lines) == 1, (const, len(lines))
        t = t.replace(lines[0], "%s%r" % (old, val))
    p = out / ("walkable_edge_%s_%s.gd" % (prefix, name))
    p.write_bytes(t.encode("utf-8"))
    print("wrote", p.name, "dx %r dz %r" % (dx, dz), hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
