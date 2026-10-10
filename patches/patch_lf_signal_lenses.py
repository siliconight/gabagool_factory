"""Level Factory 0.165.0: a traffic signal lights one lens at a time, every head in step.

Roadmap 219, the walker's note 9, walking club_block_014 on 2026-10-09: "stop lights are only
bright for 1 color at a time, and if you have 2 here, they need to be the same". Zoo's
`traffic_signal` lights all three lenses, on purpose, and leaves which is lit to whoever runs the
level. The import (`assets/godot/zoo_worldskin.gd`) now gives each `M_TrafficSignal_Lens_<colour>`
material a lit shader on one 60 s clock: green 33 s, amber 4 s, red 23 s; the unlit lens is its
own glass, dark. No per-node term: every head Lot stands faces the through road.

Anchored edits, the script pinned by hash, every anchor once, nothing written until all match:
- `assets/godot/zoo_worldskin.gd`: the constants and shader after the shutters' (`consts_block`),
  the pass in `_post_import` after the shutters', and its two functions after theirs
  (`funcs_block`);
- `tests/unit/test_worldskin_signal_lenses.py`: new;
- `tests/unit/test_worldskin_crt_motion.py`: `_signal_lenses` joins `MATERIAL_REPLACERS`, the
  guard's set of passes that replace a surface's material.
CHANGELOG and VERSION from `lf_signal_lenses/CHANGELOG_0.165.0.md`.

    python patch_lf_signal_lenses.py [--suite-pending]
    LF_ROOT=<copy> python patch_lf_signal_lenses.py --draft

`--draft` lets a changelog still carrying RESULT_ placeholders through, and only against an
LF_ROOT copy. `--suite-pending` lets exactly one through, RESULT_SUITE, into the repo, filled in
by hand after the suite runs and before the commit.
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_signal_lenses"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

SCRIPT = "assets/godot/zoo_worldskin.gd"
TEST = "tests/unit/test_worldskin_signal_lenses.py"
#: the guard that pins which passes REPLACE a surface's material: the lens
#: clock is one, and joins its set on purpose (its first suite run, without
#: this, failed on exactly that)
GUARD = "tests/unit/test_worldskin_crt_motion.py"
#: sha256[:16] of each file as read on 2026-10-09 for this patch
SHA = {SCRIPT: "9127ef2ddf390563", GUARD: "4787fa0b08620a60"}
GUARD_OLD = ("MATERIAL_REPLACERS = {\"_assign_stairs\", \"_assign_slabs\", \"_shutters\", "
             "\"_turning_parts\", \"_sway_crowns\",\n"
             "                      \"_assign_ladders\"}\n")
GUARD_NEW = ("MATERIAL_REPLACERS = {\"_assign_stairs\", \"_assign_slabs\", \"_shutters\", "
             "\"_turning_parts\", \"_sway_crowns\",\n"
             "                      \"_assign_ladders\", \"_signal_lenses\"}\n")


def _read(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


CONSTS_ANCHOR = "var _shutter_shader: Shader = null\nvar _shutter_materials: Dictionary = {}\n"
CALL_ANCHOR = (
    "\tvar shut: int = _shutters(scene)\n"
    "\tif shut > 0:\n"
    "\t\tprint(\"[worldskin] %s  %d shutter surface(s) given their clock\" % [base, shut])\n"
)
CALL_NEW = (
    CALL_ANCHOR
    + "\t# EVERY GLB, before the kit branch for the same reason: a signal's\n"
    "\t# lenses arrive in a street piece's GLB.\n"
    "\tvar lenses: int = _signal_lenses(scene)\n"
    "\tif lenses > 0:\n"
    "\t\tprint(\"[worldskin] %s  %d signal lens surface(s) given the junction's clock\" % [base, lenses])\n"
)
FUNCS_ANCHOR = (
    "\tsm.set_shader_parameter(\"closed_color\", Color(c.r, c.g, c.b, 1.0))\n"
    "\t_shutter_materials[key] = sm\n"
    "\treturn sm\n"
)

CHANGELOG_HEAD = "## [0.164.0] - The sky is in the bake\n"


def _stage():
    p = LF / SCRIPT
    d = p.read_bytes()
    got = hashlib.sha256(d).hexdigest()[:16]
    assert got == SHA[SCRIPT], (SCRIPT, "is not the file this patch read", got)
    assert b"\r" not in d, (SCRIPT, "has CR; this patch writes LF")
    t = d.decode("utf-8")
    assert "SIGNAL_LENS" not in t, "already applied"
    for old, new in ((CONSTS_ANCHOR, CONSTS_ANCHOR + _read("consts_block.gd.txt")),
                     (CALL_ANCHOR, CALL_NEW),
                     (FUNCS_ANCHOR, FUNCS_ANCHOR + _read("funcs_block.gd.txt"))):
        n = t.count(old)
        assert n == 1, (SCRIPT, n, old[:70])
        t = t.replace(old, new)
    test = LF / TEST
    assert not test.exists(), (TEST, "already exists")
    g = LF / GUARD
    gd = g.read_bytes()
    got = hashlib.sha256(gd).hexdigest()[:16]
    assert got == SHA[GUARD], (GUARD, "is not the file this patch read", got)
    assert b"\r" not in gd, (GUARD, "has CR; this patch writes LF")
    gt = gd.decode("utf-8")
    assert gt.count(GUARD_OLD) == 1, (GUARD, gt.count(GUARD_OLD))
    return {p: t.encode("utf-8"), test: _read("test_worldskin_signal_lenses.py").encode("utf-8"),
            g: gt.replace(GUARD_OLD, GUARD_NEW).encode("utf-8")}


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.164.0", repr(v)
    staged = _stage()
    entry = _read("CHANGELOG_0.165.0.md")
    assert entry.startswith("## [0.165.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    cl = LF / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r" not in data, "CHANGELOG.md is not LF"
    text = data.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # Every anchor and hash matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).encode("utf-8"))
    (LF / "VERSION").write_bytes(b"0.165.0")
    print("Level Factory 0.164.0 -> 0.165.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
