"""Lux 0.75.0: a home's dome lights its room (roadmap 229's species step, beside Zoo 1.98.0 and
Deli Counter 0.208.0).

Anchored edits in `addons/lux/runtime/lux_light_loader.gd` (`DOME_ENERGY`, `DOME_LAMP_DROP_M`,
`HOME_BAY_M` after `BULB_LAMP_DROP_M`; the `dome` branch before `heat_lamp`),
`addons/lux/runtime/lux_lighting.gd` (a dome ranks with the bulbs for shadows) and
`addons/lux/runtime/lux_leak_meter.gd` (the class word), and a new `tools/dome_lamp_selftest.gd`;
each file pinned by hash and each anchor asserted once, nothing written on a miss; the files' own
line endings kept. Applies on Lux 0.74.0. CHANGELOG and VERSION from `lux_dome/CHANGELOG_0.75.0.md`;
`--results-pending` leaves RESULT_SELFTEST to `--fill`.

    python patches/patch_lux_dome.py --results-pending && godot --headless --path lux -s res://tools/dome_lamp_selftest.gd
    python patches/patch_lux_dome.py --fill
    LUX_ROOT=<copy> python patches/patch_lux_dome.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_dome"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"Lux 0.74.0", b"Lux 0.75.0"
CHANGELOG_HEAD = "## [0.74.0] - one bad tube a room, not a row\n"
LOADER = "addons/lux/runtime/lux_light_loader.gd"
LIGHTING = "addons/lux/runtime/lux_lighting.gd"
LEAK = "addons/lux/runtime/lux_leak_meter.gd"
SHA = {LOADER: "b9035d09ffc9c6b6", LIGHTING: "e9baf2965a80f442", LEAK: "8b53682d318d01ed"}
NEW_TEST = "tools/dome_lamp_selftest.gd"

CONST_OLD = "const BULB_LAMP_DROP_M := 0.022\n"
CONST_NEW = (CONST_OLD +
             "\n"
             "## A HOME'S DOME (0.75.0, roadmap 229's species step). Deli Counter 0.208.0\n"
             "## writes a home's room as `dome` anchors -- a fixture a `HOME_BAY_M` bay\n"
             "## (its 0.207.1) at the ceiling plane -- and Zoo 1.98.0's `dome_fixture` is\n"
             "## the hardware: a canopy on the ceiling, a frosted bowl under it. Until\n"
             "## then a bedroom hung a 2 x 4 office troffer and its cool row.\n"
             "##\n"
             "## Two incandescent bulbs behind frosted glass, the one light of the room:\n"
             "## warm, the pendant's colour, and brighter than its bare bulb (1.3) by the\n"
             "## second bulb less what the glass keeps. Steady, so it bakes; never chosen\n"
             "## to fail (`LuxFixtureSpawner.choose_failing` reads fluorescents and\n"
             "## pendants), because a home's bad bulb gets changed.\n"
             "const DOME_ENERGY := 1.6\n"
             "## The lamp hangs UNDER the glass, for the pendant's reason (BULB_LAMP_DROP_M:\n"
             "## a lamp inside a closed shell bakes to nothing). Zoo's deepest dome is its\n"
             "## genome's 0.16 m height -- canopy, bowl and the finial's exposed half --\n"
             "## below the anchor, plus the centimetre the pole's lamp keeps under its\n"
             "## lens. Zoo owns the first number: a deeper bowl moves this.\n"
             "const DOME_LAMP_DROP_M := 0.17\n"
             "## Deli Counter's `_HOME_SPACING`: a home's fixtures stand a bay apart, and\n"
             "## the dome's pool reaches its bay's corner -- range = sqrt(drop^2 +\n"
             "## (HOME_BAY_M / sqrt 2)^2) -- so two neighbours' pools meet and no corner\n"
             "## of a bay is outside both. Deli Counter owns the number.\n"
             "const HOME_BAY_M := 7.0\n")

BRANCH_OLD = '\t\t"heat_lamp":\n'
BRANCH_NEW = (
    '\t\t"dome":\n'
    "\t\t\t# A HOME'S DOME (0.75.0): the pendant's machinery and colour, the\n"
    "\t\t\t# lamp under the bowl, the pool to the bay's corner (see DOME_*).\n"
    "\t\t\tvar dm := LuxFluorescentRig.new()\n"
    '\t\t\tdm.name = String(a.get("id", "dome"))\n'
    "\t\t\tvar rdm := LuxLightRig.new()\n"
    '\t\t\trdm.rig_name = &"Dome (incandescent, baked)"\n'
    "\t\t\trdm.light_color = LuxColorTemp.kelvin(LuxColorTemp.INCANDESCENT)\n"
    "\t\t\trdm.energy = DOME_ENERGY\n"
    '\t\t\tvar ddrop := float(a.get("drop", 0.0))\n'
    "\t\t\tvar half_diag := HOME_BAY_M / sqrt(2.0)\n"
    "\t\t\trdm.light_range = clampf(sqrt(ddrop * ddrop + half_diag * half_diag), 4.0, 7.5) \\\n"
    "\t\t\t\t\tif ddrop > 0.0 else 5.5\n"
    '\t\t\trdm.count = int(row.get("count", 1))\n'
    '\t\t\trdm.spacing = float(row.get("spacing", 0.0))\n'
    "\t\t\trdm.mount_height = -DOME_LAMP_DROP_M\n"
    "\t\t\trdm.flicker_amount = 0.0\n"
    "\t\t\t_make_downlight(rdm)\n"
    "\t\t\tdm.rig = rdm\n"
    "\t\t\treturn dm\n"
    + BRANCH_OLD)

RANK_OLD = '\tif name.contains("bulb") or name.contains("pendant"):\n'
RANK_NEW = ('\t# a home\'s dome (0.75.0) is a bulb behind glass, ranked with the bulbs\n'
            '\tif name.contains("bulb") or name.contains("pendant") or name.contains("dome"):\n')
LEAK_OLD = '\tfor w in ["sign", "pack", "street", "window", "bulb", "pendant", "fluorescent", "ceiling"]:\n'
LEAK_NEW = '\tfor w in ["sign", "pack", "street", "window", "bulb", "pendant", "dome", "fluorescent", "ceiling"]:\n'


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LUX / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = LUX / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_selftest.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_selftest.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SELFTEST", value, "RESULT_SELFTEST")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Lux 0.75.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LUX_ROOT"):
        sys.exit("refusing: --draft is for a LUX_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LUX / "VERSION").read_bytes().strip() == VERSION_WAS, (LUX / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.75.0.md")
    assert entry.startswith("## [0.75.0] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    assert not (LUX / NEW_TEST).exists(), f"{NEW_TEST} already exists"

    lp, l_eol, loader = _read(LOADER)
    assert "DOME_LAMP_DROP_M" not in loader, "already applied"
    loader = _once(loader, CONST_OLD, CONST_NEW, "the bulb's drop")
    loader = _once(loader, BRANCH_OLD, BRANCH_NEW, "the heat lamp's branch")
    gp, g_eol, lighting = _read(LIGHTING)
    lighting = _once(lighting, RANK_OLD, RANK_NEW, "the bulbs' shadow rank")
    kp, k_eol, leak = _read(LEAK)
    leak = _once(leak, LEAK_OLD, LEAK_NEW, "the leak meter's classes")

    cl = LUX / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert CHANGELOG_HEAD in cl_text and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:200]
    test = _src("dome_lamp_selftest.gd")
    # Every pin and anchor matched: now write.
    lp.write_bytes(loader.replace("\n", l_eol.decode()).encode("utf-8"))
    gp.write_bytes(lighting.replace("\n", g_eol.decode()).encode("utf-8"))
    kp.write_bytes(leak.replace("\n", k_eol.decode()).encode("utf-8"))
    (LUX / NEW_TEST).write_bytes(test.replace("\n", l_eol.decode()).encode("utf-8"))
    cl_text = cl_text.replace(CHANGELOG_HEAD, entry.rstrip("\n") + "\n\n" + CHANGELOG_HEAD, 1)
    cl.write_bytes(cl_text.replace("\n", cl_eol.decode()).encode("utf-8"))
    (LUX / "VERSION").write_bytes(VERSION)
    print("Lux 0.74.0 -> 0.75.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
