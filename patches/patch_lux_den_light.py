"""Lux 0.72.0: a den is lit at its walls and in its own colour (roadmap 219 note 1).

The walker, 2026-10-09, of club_block_014's strip club at midnight: "still a tad too dark...
still be dark and moody, but lit enough for a player to see and experience it". A den's bake now
lays, beside the room fills and freed with them before the save: washers along every wall of a
tinted den room, each in the colour of the nearest club wash; a fill in the room's own colour at
DEN_FILL_SHARE; and a white fill at DEN_BACK_SHARE in a den's untinted back rooms. Chosen on
re-baked copies of cold run 9217's walk copy (`docs/findings/club_light_trials/`).

Anchored edits to `addons/lux/runtime/lux_light_loader.gd`, every anchor once, nothing written
until all match:
- the den constants after BAKE_FILL_BULB_SHARE (`lux_den_light/consts_block.gd.txt`);
- `add_bake_fills`' room loop (`fill_loop_old` -> `fill_loop_new`);
- `_lay_den_washers` before `_probe_building` (`washers_block.gd.txt`).
`tools/bake_fill_selftest.gd`: the four checks that held a den unfilled now hold it filled.
New: `tools/den_light_selftest.gd`. CHANGELOG and VERSION from `lux_den_light/CHANGELOG_0.72.0.md`.

    python patch_lux_den_light.py
    LUX_ROOT=<copy> python patch_lux_den_light.py --draft
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_den_light"
DRAFT = "--draft" in sys.argv
LOADER = "addons/lux/runtime/lux_light_loader.gd"
SELFTEST = "tools/bake_fill_selftest.gd"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


CONSTS_ANCHOR = "const BAKE_FILL_BULB_SHARE := 0.5\n"
WASHERS_ANCHOR = (
    "\n\n## The site building a room probe stands in. Lot's `merge_lights` ids every\n"
)
DOC_OLD = (
    "## Lay the bake-only room fills under `scene_root` and return their\n"
    "## container, or null when nothing asks for one. Clears an earlier call's\n"
)
DOC_NEW = (
    "## Lay the bake-only room fills under `scene_root` and return their\n"
    "## container, or null when nothing asks for one. A den's rooms are filled\n"
    "## too since 0.72.0, and its tinted rooms washed at their walls (DEN_WASH_LEVEL).\n"
    "## Clears an earlier call's\n"
)

SELFTEST_EDITS = [
    ('\t_check("a club room gets none", _fills_of(fills, "club_floor").size(), 0)\n',
     '\t# 0.72.0: a club room is filled too, in its own colour, and washed at its\n'
     '\t# walls (tools/den_light_selftest.gd holds what each of those is)\n'
     '\t_check("a club room is filled, 2 x 2", _fills_of(fills, "club_floor").size(), 4)\n'),
    ('\t_check("seven in all", fills.get_child_count(), 7)\n',
     '\t_check("eleven fills and the club\'s twelve washers", fills.get_child_count(), 23)\n'),
    ('\t_check("a club building\'s back room keeps no fill", _fills_of(dens, "b5_back_rooms_ambient").size(), 0)\n'
     '\t_check("...nor its tinted floor", _fills_of(dens, "b5_main_floor_ambient").size(), 0)\n',
     '\t# 0.72.0: a den\'s back room is filled at DEN_BACK_SHARE, its tinted floor\n'
     '\t# at DEN_FILL_SHARE -- 0.68.2 held both at none\n'
     '\t_check("a club building\'s back room is filled at the den\'s back share",\n'
     '\t\t_fills_of(dens, "b5_back_rooms_ambient").size(), 2)\n'
     '\t_check("...and its tinted floor", _fills_of(dens, "b5_main_floor_ambient").size(), 4)\n'),
    ('\t_check("...and lays the same seven", again.get_child_count() if again != null else -1, 7)\n',
     '\t_check("...and lays the same twenty-three", again.get_child_count() if again != null else -1, 23)\n'),
]


def main():
    if DRAFT and not os.environ.get("LUX_ROOT"):
        sys.exit("refusing: --draft is for a LUX_ROOT copy, never the repo")
    v = (LUX / "VERSION").read_bytes()
    assert v == b"Lux 0.71.0", v
    entry = _src("CHANGELOG_0.72.0.md")
    assert entry.startswith("## [0.72.0] - "), entry[:40]
    consts = _src("consts_block.gd.txt")
    if not DRAFT:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
        assert "RESULT_" not in consts, "the constants still carry an unfilled result"

    p = LUX / LOADER
    d = p.read_bytes()
    assert b"\r" not in d, (LOADER, "has CR; this patch writes LF")
    t = d.decode("utf-8")
    assert "DEN_WASH_LEVEL" not in t, "already applied"
    for old, new in ((CONSTS_ANCHOR, CONSTS_ANCHOR + consts),
                     (_src("fill_loop_old.gd.txt"), _src("fill_loop_new.gd.txt")),
                     (WASHERS_ANCHOR, _src("washers_block.gd.txt") + WASHERS_ANCHOR),
                     (DOC_OLD, DOC_NEW)):
        n = t.count(old)
        assert n == 1, (LOADER, n, old[:70])
        t = t.replace(old, new)

    s = LUX / SELFTEST
    sd = s.read_bytes()
    assert b"\r" not in sd, (SELFTEST, "has CR")
    st = sd.decode("utf-8")
    for old, new in SELFTEST_EDITS:
        n = st.count(old)
        assert n == 1, (SELFTEST, n, old[:70])
        st = st.replace(old, new)

    new_test = LUX / "tools" / "den_light_selftest.gd"
    assert not new_test.exists(), new_test
    cl = LUX / "CHANGELOG.md"
    cd = cl.read_bytes()
    assert b"## [0.72.0]" not in cd
    head = b"# Changelog\n\n"
    assert cd.startswith(head)
    # every anchor matched: now write
    p.write_bytes(t.encode("utf-8"))
    s.write_bytes(st.encode("utf-8"))
    new_test.write_bytes(_src("den_light_selftest.gd").encode("utf-8"))
    cl.write_bytes(head + entry.encode("utf-8") + cd[len(head):])
    (LUX / "VERSION").write_bytes(b"Lux 0.72.0")
    print("Lux 0.71.0 -> 0.72.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
