"""Patina 0.38.1: no quoin within a standing body's height.

`framing.quoin_orders` starts the quoined body just above the lowest band clear of a standing body (`BODY_CLEAR_M`,
1.85, mirroring Deli Counter's agent contract), instead of from the ground: a quoin stands 6 cm proud with no
collider, and the walkable-space rule forbids that where a body walks.

Proven: tests/test_quoins.py's body-height case fails on 0.38.0 (fails_on_old.out.txt); the clone's suite, 419
passed, 12 skipped (suite_clone.out.txt); the slice rebuilt (the factory's docs/findings/slice_look/, slice 10).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'patina'
PINS = {'CHANGELOG.md': 'a1538bdb7cee7a3d', 'VERSION': '6a63f389e1fabe5e', 'patina/framing.py': '3f4108d6c9ac7a05', 'patina/version.py': '4816dc030e403846', 'tests/test_quoins.py': '6feae02ff37b3fd6'}
EDITS = {'CHANGELOG.md': [('lines 4-5', 'versioning follows [SemVer](https://semver.org/).\n\n', "versioning follows [SemVer](https://semver.org/).\n\n## [0.38.1] - no quoin within a standing body's height\n\n### Fixed\n- **`framing.quoin_orders`**: 0.38.0 laid quoins from the ground. A block stands 6 cm proud of the wall with no\n  collision, and a wall's collider ends at its face, so every block within a body's height was geometry a body walks\n  into -- the rule panel fields and pilasters were withdrawn for (Level Factory's Patina adapter; Zoo's\n  `arch.relief_parts`). The quoined body now starts just above the lowest band clear of a standing body\n  (`BODY_CLEAR_M`, 1.85: Deli Counter's `agent_contract.json` player height, 1.8, and a hand), as a quoined upper\n  body over a plain base storey does; a civic building with no band that high gets none. Tests:\n  tests/test_quoins.py (the body-height case fails on 0.38.0; the mirror is pinned against the contract where it can\n  be read).\n\n")], 'VERSION': [('lines 1-1', 'Patina 0.38.0', 'Patina 0.38.1')], 'patina/framing.py': [('lines 731-732', 'QUOIN_BAND_CLEAR = 0.05\n\n', "QUOIN_BAND_CLEAR = 0.05\n#: NOTHING PROUD WITHIN A STANDING BODY'S HEIGHT (0.38.1). A quoin stands `_BAND_PROUD` off the wall with no collision,\n#: and a wall's collider ends at its face, so a block within a body's height is geometry a body walks into -- the rule\n#: the panel fields and pilasters were withdrawn for (Level Factory's Patina adapter, Zoo's `arch.relief_parts`).\n#: 0.38.0 laid them from the ground. So the quoined body starts above the lowest band clear of a standing body, as a\n#: quoined upper body over a plain base storey does; a civic building with no band that high gets none. The figure\n#: mirrors Deli Counter's `agent_contract.json` `characters.player.height_m` (1.8) and a hand over it; a test pins the\n#: mirror where the contract can be read.\nBODY_CLEAR_M = 1.85\n\n"), ('lines 762-764', '    n_y, s_y, e_x, w_x = planes[(0, 1)], planes[(0, -1)], planes[(1, 0)], planes[(-1, 0)]\n    orders = []\n    z, k = ground, 0\n', '    n_y, s_y, e_x, w_x = planes[(0, 1)], planes[(0, -1)], planes[(1, 0)], planes[(-1, 0)]\n    # the lowest band clear of a standing body: the quoins start just above it\n    over = sorted(b["pos"][2] + b["size2"][1] / 2.0 for b in bands\n                  if b["pos"][2] - b["size2"][1] / 2.0 >= ground + BODY_CLEAR_M)\n    if not over:\n        return []\n    orders = []\n    z, k = over[0] + QUOIN_BAND_CLEAR, 0\n')], 'patina/version.py': [('lines 9-9', '__version__ = "0.38.0"\n', '__version__ = "0.38.1"\n')], 'tests/test_quoins.py': [('lines 48-48', '                         round(framing.QUOIN_SHORT + framing._BAND_PROUD, 3)}\n', '                         round(framing.QUOIN_SHORT + framing._BAND_PROUD, 3)}\n\n\ndef test_no_block_stands_within_a_standing_bodys_height():\n    """FAILS ON 0.38.0: its quoins ran from the ground, 6 cm proud and without collision, where a body walks."""\n    m = _block(storeys=2)\n    bands = framing.string_course_orders(m, _regions(), seed=1999)\n    q = framing.quoin_orders(_named(m, "bank_branch_a02"), _regions(), seed=1999, bands=bands)\n    assert q\n    ground = min(framing._base_z(s) for s in m.slots if s.story is not None and int(s.story) == 0)\n    lowest = min(o["pos"][2] - o["size2"][1] / 2.0 for o in q)\n    assert lowest >= ground + framing.BODY_CLEAR_M\n    # and they start on the band that cleared it, not part way up a wall\n    first = min(b["pos"][2] + b["size2"][1] / 2.0 for b in bands\n                if b["pos"][2] - b["size2"][1] / 2.0 >= ground + framing.BODY_CLEAR_M)\n    assert lowest == pytest.approx(first + framing.QUOIN_BAND_CLEAR, abs=1e-3)\n\n\ndef test_with_no_band_clear_of_a_body_there_are_no_quoins():\n    m = _block(storeys=2)\n    bands = framing.string_course_orders(m, _regions(), seed=1999)\n    assert framing.quoin_orders(_named(m, "bank_branch_a02"), _regions(), seed=1999, bands=[]) == []\n    low = [b for b in bands if b["pos"][2] < 1.0]\n    assert framing.quoin_orders(_named(m, "bank_branch_a02"), _regions(), seed=1999, bands=low) == []\n\n\ndef test_the_body_height_mirrors_the_agent_contract():\n    import json\n    import pathlib\n    contract = pathlib.Path(__file__).resolve().parents[2] / "deli_counter" / "agent_contract.json"\n    if not contract.is_file():\n        pytest.skip("no Deli Counter beside this repo to read the contract from")\n    h = json.loads(contract.read_text(encoding="utf-8"))["characters"]["player"]["height_m"]\n    assert h <= framing.BODY_CLEAR_M <= h + 0.1\n')]}
WHOLE = {}
NEW_FILES = {}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s/%s has mixed line endings; nothing written" % (REPO.name, name))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %s/%s is %s, not the %s this patch was written against; nothing written"
                         % (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %s/%s: the anchor at %s is there %d times; nothing written"
                                 % (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
