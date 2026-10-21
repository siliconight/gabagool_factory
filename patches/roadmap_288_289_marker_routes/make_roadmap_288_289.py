"""Write patches/patch_roadmap_288_289_marker_routes.py: 288's and 289's statuses (each the block above its heading,
embedded exactly) replaced -- 288 NARROWED again, 289 CLOSED -- each keeping its earlier status. Copied from
`roadmap_289_sight_contract/make_roadmap_289.py`'s status half. Refuses if the name is taken, and while a figure it
quotes is still a placeholder.

    python patches/roadmap_288_289_marker_routes/make_roadmap_288_289.py
"""
import pathlib
import re
import subprocess

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_288_289_marker_routes.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t

# Deli Counter 0.251.0's commit, read from the repo, not typed
assert (F / "deli_counter" / "VERSION").read_bytes() == b"Deli Counter 0.251.0"
DC = subprocess.run(["git", "-C", str(F / "deli_counter"), "log", "-1", "--format=%h %s"], capture_output=True,
                    text=True, check=True).stdout.strip()
HASH, SUBJECT = DC.split(" ", 1)
assert SUBJECT.startswith("0.251.0: "), SUBJECT
# the library-wide census at 0.251.0, from docs/findings/furnish_route_cost/route_cost.out.txt
LIB = ("the dressing's detours over 10 % 8 -> 1 (the one left self_storage_a01's mid_aisle, which holds no marker), all "
       "of furnishing's 34 -> 28, narrowed to single file 179 -> 150 "
       "(`docs/findings/furnish_route_cost/route_cost.out.txt`)")
assert "<<" not in LIB, "fill LIB from the library census first"


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


H288, OLD288 = status_of(288)
H289, OLD289 = status_of(289)
NEW288 = (
    "*STATUS: NARROWED 2026-10-21 -- the corner stores' floors and the objective rooms done. Deli Counter 0.251.0 "
    "(" + HASH + ", `patches/patch_dc_marker_routes.py`) keeps a room's dressing off its routes when it holds an "
    "objective or loot marker: `reserves_routes(spec, room, building)` says what keeps off a room's routes -- every "
    "floor piece on a corner store's floor (0.250.0), the clusters in a marker room, nothing elsewhere -- and the "
    "shelter pass stands its piece off them where a clear spot is, else anywhere clear. The census's FUNCTIONAL arm "
    "(the spec less only furnish's dressing, the guide's own B -> C measure) had found 8 dressing detours over 10 % at "
    "0.250.0, 7 of them door -> marker in objective rooms of 97-240 m2 at 3.0-7.3 % share, not the small rooms the "
    "census first called them. Over the 50 specs that moved (217 rooms, 1,000 pairs, "
    "`patches/dc_marker_routes/census_changed.out.txt`, `pairs_compare.out.txt`): dressing detours 7 -> 0 (worst "
    "1.270 -> 1.052), dressing narrowings 37 -> 5; all of furnishing over 10 % 18 -> 12, narrowings 80 -> 51; pair by "
    "pair none crossed over 10 %; 51 rooms moved, every one a marker room, furnish's pieces 8,434 -> 8,428 and one "
    "shelter piece more; the combat audit's codes unchanged. Over the library: " + LIB + ". Refuted and kept: every "
    "floor piece off a marker room's routes (47 rooms, 45 under 12 % already, lost 45 pieces); the shelter piece "
    "strictly off them (the pawn_shop preset's safe_room lost its shelter). No cold run: restaurant_row_001 at seed "
    "9003 draws none of the 50 specs; plan views of four rooms in `patches/dc_marker_routes/`. LEFT: working "
    "furniture is not kept off a marker room's routes, and a desk can stand where a pile stood (funeral_home_a02's "
    "records_office 1.270 -> 1.154) -- whether it should is the walker's call, priced by the refuted shape; a cluster "
    "group that fits nowhere off its routes leaves its room barer (clinic_a01's dispensary about 5 -> 2.4 %), the "
    "barren side of the walker's band, which wants primary furniture rather than more piles; the offices' and vaults' "
    "narrowings, which are their function's; the eleven authored cases; the census's limits. Earlier status kept: "
    + OLD288[len("*STATUS: "):])
NEW289 = (
    "*STATUS: CLOSED 2026-10-21 -- the contract's note too. Deli Counter 0.251.0 (" + HASH + ") rewrites "
    "`agent_contract.json`'s `sightlines` note: it names what derives the crossing now -- Lot's copies, held to Laser "
    "Tag's by `check_sight_drift`, and Level Factory's advisory, from the body each run fields -- and that nothing in "
    "the factory carries the old 1.2 any more (searched first: no assignment of a 1.4 eye or a 1.2 crossing in any "
    "tool's code, the search's control finding 0.228.0's `EYE_HEIGHT = 1.4`); no number in the file moved, and Lot's "
    "suite, which reads it, passes (854). Earlier status kept: " + OLD289[len("*STATUS: "):])

PATCH = '''"""Roadmap 288 NARROWED again (Deli Counter 0.251.0: a room holding an objective or loot marker keeps its dressing
off its routes) and 289 CLOSED (the contract's sightlines note). Copied from `patch_roadmap_289_sight_contract.py`'s
status half: replaces each item's status block (the paragraph directly above its heading, asserted to be the one this
was written against) with one that keeps it after "Earlier status kept:". The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_288_289_marker_routes.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
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
    print("roadmap 288: NARROWED, 289: CLOSED, the earlier statuses kept; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % ([(288, H288, OLD288, NEW288), (289, H289, OLD289, NEW289)],)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars; Deli Counter", HASH)
