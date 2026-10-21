"""Write patches/patch_roadmap_293_axonometric.py: 293's status (the block above its heading, embedded exactly)
replaced -- NARROWED, keeping its earlier status. Copied from `roadmap_292_npc_body/make_roadmap_292.py`. Refuses if
the name is taken.

    python patches/roadmap_293_axonometric/make_roadmap_293.py
"""
import pathlib
import re
import subprocess

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_293_axonometric.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t

# Deli Counter 0.254.0's commit, read from the repo, not typed
assert (F / "deli_counter" / "VERSION").read_bytes() == b"Deli Counter 0.254.0"
line = subprocess.run(["git", "-C", str(F / "deli_counter"), "log", "-1", "--format=%h %s"], capture_output=True,
                      text=True, check=True).stdout.strip()
DC, SUBJECT = line.split(" ", 1)
assert SUBJECT.startswith("0.254.0: "), SUBJECT


def status_of(n):
    m = list(re.finditer(r"(?m)^\*\*%d\. " % n, t))
    assert len(m) == 1, n
    h = m[0].start()
    s = t.rindex("\n\n", 0, h - 2) + 2
    block = t[s:h - 2]
    assert block.startswith("*STATUS: ") and block.endswith("*") and "\n" not in block, n
    heading = t[h - 2:t.index("\n", h)]
    assert t.count(heading) == 1, n
    return heading, block


H293, OLD293 = status_of(293)
assert OLD293.startswith("*STATUS: OPEN 2026-10-21 -- the walker's floor-plan guide"), OLD293
NEW293 = (
    "*STATUS: NARROWED 2026-10-21 -- the exploded axonometric drawn, for every building. Deli Counter 0.254.0 "
    "(" + DC + ", `patches/patch_dc_axonometric.py`): `axonometric.py` draws every storey at once from its spec, seen "
    "from above and to the south-west at true-isometric elevation -- each slab raised by a display offset that never "
    "moves an elevation (a storey's `data-elevation` beside its `data-offset`; the gap derived as the least rise that "
    "keeps one slab's drawing clear of the next, plus 2 m), walls standing to the 1.2 m plan cut with dark cut faces, "
    "doors as gaps with their thresholds, a window's sill wall and glass under the cut, furniture to the cut, roofs and "
    "ceilings off, every slab hole masked open with the slab's thickness on its far edges, stairs joined to the storey "
    "they climb to by an ascent line and alignment columns, ladders and open-to-below drop lines, markers on their "
    "storey, labels and a legend; offline and deterministic, the whole library in under a second, and `validate.py` "
    "writes `<name>.axo.svg` beside the plans, so the commit gate draws every building's. One layout, two drawings: "
    "the plan's wall arithmetic is `floorplan.wall_split` and `storey_walls`, refactored first with all 288 plans of "
    "the 159 specs byte for byte as before; the plan's two disagreements fixed -- a partition drawn at its built "
    "thickness (242 plans move, exactly those with a partition) and the storey height called floor to floor -- and "
    "`build_freshness.py` files both drawings as readers, so a change to one no longer reads every shell as stale. The "
    "guide's acceptance checks asked of library buildings in `test_axonometric.py` (8): the offset the drawing's alone, "
    "a doorway moved moving its gap in both drawings, a stair moved moving its flight and column, an atrium kept open, "
    "two markers one above the other on their own floors, every library building drawing every storey; frames of "
    "deli_a03, office and cbp_town_finale shown to the walker (`patches/dc_axonometric/axo_*.png`). No cold run: a "
    "build makes no drawing and the shells did not move. LEFT: ramps, platforms and fire escapes in either drawing; "
    "stairs drawn as treads rather than an ascent line; where a reviewer finds the drawing beside a level (a "
    "walker-review page, a level's export), chosen with the walker; the guide's section 8 for this view -- floors "
    "selected and the rest subdued -- belongs with roadmap 295's map. Earlier status kept: "
    + OLD293[len("*STATUS: "):])
assert "\n" not in NEW293 and NEW293.endswith("*")

PATCH = '''"""Roadmap 293 NARROWED (Deli Counter 0.254.0: an exploded axonometric of every building, with architectural
cutaways). Copied from `patch_roadmap_292_npc_body.py`: replaces 293's status block (the paragraph directly above its
heading, asserted to be the one this was written against) with one that keeps it after "Earlier status kept:". The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_293_axonometric.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    for n, heading, old, new in ITEMS:
        if new[:80] in text:
            raise SystemExit("REFUSED: %%d already applied; nothing written" %% n)
        if text.count(heading) != 1:
            raise SystemExit("REFUSED: %%d's heading is not there once; nothing written" %% n)
        h = text.find(heading)
        s = text.rindex("\\n\\n", 0, h) + 2
        if text[s:h] != old:
            raise SystemExit("REFUSED: %%d's status block is not the one this was written against; nothing written" %% n)
        text = text[:s] + new + text[h:]
        if text.count(new + heading) != 1:
            raise SystemExit("REFUSED: %%d's status no longer adjoins its heading; nothing written" %% n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 293: NARROWED, the earlier status kept; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % ([(293, H293, OLD293, NEW293)],)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars; Deli Counter", DC)
