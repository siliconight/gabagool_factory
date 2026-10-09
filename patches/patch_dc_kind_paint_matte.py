"""Deli Counter 0.204.0, a second fix: `material_kind.SKIN_KINDS` learns Zoo's
`paint_matte`.

`SKIN_KINDS` is a literal copy of `zoo_keeper.core.skins.KNOWN_KINDS`, and
`test_material_kind.test_the_kinds_are_zoo_s_when_zoo_is_beside_this_repo`
pins it to Zoo's list when Zoo is beside this repo. Zoo 1.82.0 (2026-10-07
22:35, the getaway van) added `paint_matte`; Deli Counter 0.203.0's suite ran
at 14:54 that day, before it, and no Deli Counter suite ran again until
0.204.0's, which found the test failing. It fails the same against Zoo 1.88.0
with this repo untouched, so it is the drift the test exists to catch, not
0.204.0's payphone change. No spec writes the kind -- Lot stands the van --
so it has no `KIND_BY_MATERIAL` row.

    python patch_dc_kind_paint_matte.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "deli_counter" / "material_kind.py"

OLD = """    # THE CHAIN-LINK FENCE'S FABRIC (Zoo 1.77.0, Pixelcoat 0.59.0): Lot stands
    # the fence; no spec here writes it, so it has no KIND_BY_MATERIAL row
    "chain_link",
)
"""
NEW = """    # THE CHAIN-LINK FENCE'S FABRIC (Zoo 1.77.0, Pixelcoat 0.59.0): Lot stands
    # the fence; no spec here writes it, so it has no KIND_BY_MATERIAL row
    "chain_link",
    # THE GETAWAY VAN'S PAINT (Zoo 1.82.0, roadmap 206): flat black, object-
    # owned, no pack in any theme. Lot stands the van, so no spec here writes
    # it. Copied in 0.204.0: Zoo grew it after 0.203.0's suite ran, and the
    # pin to Zoo's list had failed since
    "paint_matte",
)
"""


def main():
    d = P.read_bytes()
    assert b"\r\n" not in d, "material_kind.py is LF; it has CRLF now"
    t = d.decode("utf-8")
    assert '"paint_matte"' not in t, "already applied"
    assert t.count(OLD) == 1, t.count(OLD)
    P.write_bytes(t.replace(OLD, NEW).encode("utf-8"))
    print("material_kind.SKIN_KINDS: + paint_matte")


if __name__ == "__main__":
    main()
