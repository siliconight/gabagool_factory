"""Write patches/patch_roadmap_293_treads.py: 293's status (the block above its heading, embedded exactly) replaced --
still NARROWED, the stairs drawn as treads -- keeping its earlier status. Copied from
`roadmap_293_axonometric/make_roadmap_293.py`. Refuses if the name is taken.

    python patches/roadmap_293_treads/make_roadmap_293_treads.py
"""
import pathlib
import re
import subprocess

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_293_treads.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t

# Deli Counter 0.255.0's commit, read from the repo, not typed
assert (F / "deli_counter" / "VERSION").read_bytes() == b"Deli Counter 0.255.0"
line = subprocess.run(["git", "-C", str(F / "deli_counter"), "log", "-1", "--format=%h %s"], capture_output=True,
                      text=True, check=True).stdout.strip()
DC, SUBJECT = line.split(" ", 1)
assert SUBJECT.startswith("0.255.0: "), SUBJECT


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
assert OLD293.startswith("*STATUS: NARROWED 2026-10-21 -- the exploded axonometric drawn, for every building."), OLD293
NEW293 = (
    "*STATUS: NARROWED 2026-10-21 -- the stairs drawn as treads (the walker: \"draw the stairs as treads next\"). "
    "Deli Counter 0.255.0 (" + DC + ", `patches/patch_dc_axo_treads.py`): every flight is drawn as the treads and turn "
    "landings `stairwell.ascent_surfaces` says the builder builds -- the headroom gate's copy of `Builder._stairs`, so "
    "the drawing and that gate read one stair -- on the storey it climbs from at its true rise, solid to that floor "
    "where the builder fills the leg (`flight_solid_under`), one riser thick where it does not, a turn landing one riser "
    "thick as built (the first draft stood it as a 3.6 m column at office's stair head, caught in its frame); tread "
    "sides drawn seamless so a flight reads as one stepped stringer; a dashed leader carries each flight's head across "
    "the exploded gap. Three tests -- the treads are the builder's, every surface at its own height and place; a "
    "landing is a plate and a solid leg stands on its floor; a stair moved moves its treads -- all failing on 0.254.0 "
    "on behaviour. Frames to the walker (`patches/dc_axo_treads/axo_*.png`, office's stair cropped). LEFT: ramps, "
    "platforms and fire escapes in either drawing; a cut switchback's second leg drawn solid to its own storey where "
    "the builder carries it to the stair's lowest floor (`flight_solid_base`), a gap away in an exploded drawing; "
    "where a reviewer finds the drawing beside a level, chosen with the walker. Earlier status kept: "
    + OLD293[len("*STATUS: "):])
assert "\n" not in NEW293 and NEW293.endswith("*")

PATCH = '''"""Roadmap 293 still NARROWED, the stairs drawn as treads (Deli Counter 0.255.0). Copied from
`patch_roadmap_293_axonometric.py`: replaces 293's status block (the paragraph directly above its heading, asserted to
be the one this was written against) with one that keeps it after "Earlier status kept:". The index is NOT touched
here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_293_treads.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
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
    print("roadmap 293: NARROWED, the stairs as treads; the earlier status kept; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % ([(293, H293, OLD293, NEW293)],)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars; Deli Counter", DC)
