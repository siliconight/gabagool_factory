"""Zoo 1.155.0: a street tree's crown raised clear of the sidewalk.

tree_forms.CROWN_CLEAR_M (8 ft), crown_lift and squeeze; street_tree lifts the skeleton before its cards.

Proven: tests/test_crown_raised.py fails on 1.154.0 under Blender (fails_on_old.out.txt); the clone's pure suite
(suite_clone.out.txt) and its whole Blender set (suite_bpy_clone.out.txt); built as the slice (the factory's
docs/findings/slice_look/).
"""
import base64
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'zoo'
PINS = {'CHANGELOG.md': '87804d7c188e7e31', 'VERSION': '7176ea896543f45e', 'tests/test_coincident_faces.py': '9c10d4cf0661cf9d', 'zoo_keeper/core/tree_forms.py': '22227b81515b50a4', 'zoo_keeper/recipes/street_tree.py': 'efa7f461e6b53019'}
EDITS = {'CHANGELOG.md': [('lines 1-1', "## [1.154.0] - grime at a wall's base\n", '## [1.155.0] - a street tree\'s crown raised clear of the sidewalk\n\nThe factory\'s roadmap 324 (the vertical slice). Measured on the slice\'s built trees: leaf cards down to 0.53 m above\nthe grate on the pin oak, 0.91 m on the London plane, 1.16 m on the red maple -- a body walked through cards at eye\nheight, a camera on the sidewalk stood inside a crown of near-black blocks, and every sightline down a sidewalk was\nscreened by leaves. A street tree is pruned clear of the walk under it: 8 ft over a sidewalk is the common municipal\nclearance, and the walker\'s tree guide gives a street tree a "Raised crown, pruning scars" (the factory\'s\n`docs/reference/PA_NATIVE_TREES_PHILLY_DELCO.md`).\n\n### Added\n- **`tree_forms.CROWN_CLEAR_M`** (8 ft, 2.4384 m) and **`crown_lift`**: before a card is placed, every point of the\n  grown skeleton above the grate is pressed toward the highest clump\'s centre until each card -- placed by its\n  centre, keeping its size -- clears the ground by `CROWN_CLEAR_M`. The top of the crown stays, and the limbs keep\n  their order and proportions, so a pin oak\'s drooping, level and rising limbs stay three zones, lifted (the guide\'s\n  instruction for it). Pressing the crown after its cards were on would squash them into plates, the first build\'s\n  lesson, so the cards are untouched.\n- **`tree_forms.squeeze`**: the recipe\'s last per-axis correction scales height by h / ez and can bring the lowest\n  card back a little under the clearance; one squeeze of the built vertices, its k within a few percent of 1, puts\n  it back.\n- 14 ft over a road is the street\'s figure and is not applied: a kerb tree\'s crown overhangs a parking lane only at\n  its edge.\n\nTests: tests/test_crown_raised.py, every species built in Blender (fails on 1.154.0: every species\' lowest card hangs\nunder the clearance).\n\n## [1.154.0] - grime at a wall\'s base\n')], 'VERSION': [('lines 1-1', '1.154.0', '1.155.0')], 'tests/test_coincident_faces.py': [('lines 274-274', '    "london_plane": (7, 3, 4, 3, 5.45, 313.1),\n', '    # 1.155.0: its crown raised clear of the sidewalk, re-measured over the three corners: one limb joint and one\n    # trunk-foot pair no longer meet\n    "london_plane": (5, 2, 3, 2, 7.35, 313.1),\n'), ('lines 648-648', '    (5.45 mm): 1988."""\n', '    (5.45 mm): 1988. 1.155.0 raised every tree\'s crown clear of the sidewalk:\n    london_plane meets one limb joint and one trunk foot fewer: 1986."""\n'), ('lines 650-650', '    assert total == 1988, total\n', '    assert total == 1986, total\n'), ('lines 652-652', '    assert exposed == 543, exposed\n', '    assert exposed == 542, exposed\n'), ('lines 655-655', '    assert total + 18 + 6 + 6 + 2 + 884 + 128 - 1 - 3 - 1 == 3027\n', '    assert total + 18 + 6 + 6 + 2 + 884 + 128 - 1 - 3 - 1 + 2 == 3027\n')], 'zoo_keeper/core/tree_forms.py': [('lines 237-237', 'CARD_SCALE = 2.2\n', 'CARD_SCALE = 2.2\n\n#: THE CROWN RAISED (1.155.0). A street tree is pruned clear of the walk under it: 8 ft (2.4384 m) over a sidewalk is\n#: the common municipal clearance, and the walker\'s tree guide gives a street tree a "Raised crown, pruning scars"\n#: (the factory\'s docs/reference/PA_NATIVE_TREES_PHILLY_DELCO.md, its growing-situation table). Measured on the\n#: vertical slice\'s built trees before this (2026-10-31): leaves down to 0.53 m on the pin oak, 0.91 m on the London\n#: plane, 1.16 m on the red maple -- a body walked through cards at eye height and every sightline down the sidewalk\n#: was screened by them. 14 ft over a road is the street\'s figure; it is not applied, since a kerb tree\'s crown\n#: overhangs a parking lane only at its edge.\nCROWN_CLEAR_M = 8 * 0.3048\n#: A YOUNG TREE KEEPS ITS CROWN. A tree too short to hold a crown above `CROWN_CLEAR_M` -- the genome\'s smallest\n#: corner, or a newly planted one -- is lifted only so far: pressed past half its height a crown stacks its cards on\n#: each other. Measured, kept: without this floor the generic `street_tree` at its smallest corner went from 6\n#: coincident face pairs to 187 (tests/test_coincident_faces.py).\nLIFT_K_MIN = 0.5\n#: `squeeze` is the last correction, not a second lift: past this it is left undone.\nSQUEEZE_K_MIN = 0.9\n\n\ndef crown_lift(clumps, z0: float, clear: float = CROWN_CLEAR_M):\n    """``(k, anchor)`` raising a crown clear of the ground before its cards are placed: ``clumps`` are (centre z,\n    card half-height) of every leaf clump, ``z0`` the ground. A point at height ``z`` moves to\n    ``anchor - (anchor - z) * k``, ``anchor`` the highest clump\'s centre: the top of the crown stays, every card --\n    placed by its centre, keeping its size -- clears ``z0 + clear``, and everything between keeps its order and its\n    proportions, so a pin oak\'s drooping, level and rising limbs stay three zones, lifted. ``k`` is 1 for a crown\n    already clear, and for one that cannot be (a card at the top reaches under the clearance); never under\n    `LIFT_K_MIN`, so a tree too short to clear is lifted as far as its crown keeps its shape."""\n    if not clumps:\n        return 1.0, z0\n    anchor = max(z for z, _h in clumps)\n    floor = z0 + clear\n    k = 1.0\n    for z, h in clumps:\n        if z - h >= floor:\n            continue\n        room = anchor - floor - h\n        if room <= 0.0 or anchor - z <= 1e-9:\n            return 1.0, anchor\n        k = min(k, room / (anchor - z))\n    return max(k, LIFT_K_MIN), anchor\n\n\ndef squeeze(lo: float, top: float, z0: float, clear: float = CROWN_CLEAR_M) -> float:\n    """``k`` pressing built geometry spanning ``lo`` .. ``top`` up so ``lo`` clears ``z0 + clear``, ``top`` kept:\n    ``z -> top - (top - z) * k``. 1 when ``lo`` is already clear or ``top`` is not, and when the press would pass\n    `SQUEEZE_K_MIN` -- a crown the lift could not clear is not crushed here."""\n    floor = z0 + clear\n    if lo >= floor or top <= floor:\n        return 1.0\n    k = (top - floor) / (top - lo)\n    return k if k >= SQUEEZE_K_MIN else 1.0\n')], 'zoo_keeper/recipes/street_tree.py': [('lines 370-372', '\n        def _fitp(p):\n            return ((p[0] - cx) * kx, (p[1] - cy) * ky, z0 + (p[2] - z0) * kz)\n', "\n        def _fitp0(p):\n            return ((p[0] - cx) * kx, (p[1] - cy) * ky, z0 + (p[2] - z0) * kz)\n\n        # THE CROWN RAISED (1.155.0, `tree_forms.crown_lift`): every point above the grate is pressed up toward the\n        # top until the lowest card's bottom clears `CROWN_CLEAR_M`, before a card is placed -- so the cards keep\n        # their size and shape (squashing a crown after its leaves were on it made plates, the first build's\n        # lesson) and the limbs keep their order. A card's reach below its centre is at most its half (an upright\n        # card); its centre stands `0.2 c` over the tip, as placed below.\n        lift_k, lift_top = tree_forms.crown_lift(\n            [(_fitp0(p)[2] + c * 0.2, c * CARD_SCALE / 2.0) for p, c in big + small], z0)\n\n        def _fitp(p):\n            q = _fitp0(p)\n            if lift_k == 1.0 or q[2] <= z0 + 1e-9:\n                return q\n            return (q[0], q[1], lift_top - (lift_top - q[2]) * lift_k)\n"), ('lines 418-419', '                v.co.z = z0 + (v.co.z - z0) * kz\n        trunk_top_z = z0 + (first - z0)\n', '                v.co.z = z0 + (v.co.z - z0) * kz\n        # the last correction scales height by h / ez and can bring the lowest card back under the clearance a\n        # little; a second lift on the built vertices puts it back, its k within a few percent of 1 (1.155.0)\n        lows = [v.co.z for v in leaves.verts]\n        top2 = max(lows) if lows else z0\n        k2 = tree_forms.squeeze(min(lows), top2, z0) if lows else 1.0\n        if k2 != 1.0:\n            for bmx in (wood, twigs, leaves):\n                for v in bmx.verts:\n                    if v.co.z > z0 + 1e-9:\n                        v.co.z = top2 - (top2 - v.co.z) * k2\n        trunk_top_z = z0 + (first - z0)\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_crown_raised.py': '"""A street tree\'s crown is raised clear of the sidewalk (1.155.0, the factory\'s roadmap 324).\n\nThe vertical slice\'s built trees hung leaf cards down to 0.53 m (pin oak), 0.91 m (London plane) and 1.16 m (red\nmaple): a body walked through cards at eye height, and every sightline down a sidewalk was screened by them. A street\ntree is pruned to 8 ft (2.44 m) over a walk -- the walker\'s tree guide: a "Raised crown" on a street edge.\nFAILS ON 1.154.0: there is no `crown_lift`, and every species\' lowest card hangs under the clearance.\n"""\nimport pytest\n\nfrom zoo_keeper.core import tree_forms as T\n\nTREES = ("street_tree", "red_maple", "pin_oak", "honey_locust", "london_plane", "callery_pear")\n\n\ndef test_the_lift_brings_the_lowest_card_to_the_clearance_and_keeps_the_top():\n    z0 = -3.25\n    clumps = [(-2.0, 0.7), (0.0, 0.8), (2.5, 0.75)]\n    k, anchor = T.crown_lift(clumps, z0)\n    assert 0.0 < k < 1.0 and anchor == pytest.approx(2.5)\n\n    def lift(z):\n        return anchor - (anchor - z) * k\n\n    # every card, placed by its centre and keeping its size, clears; the lowest exactly; the top card unmoved\n    assert min(lift(z) - h for z, h in clumps) == pytest.approx(z0 + T.CROWN_CLEAR_M)\n    assert lift(2.5) == pytest.approx(2.5)\n    assert T.squeeze(-0.9, 3.25, z0) == pytest.approx((3.25 - (z0 + T.CROWN_CLEAR_M)) / (3.25 + 0.9))\n    # order and proportion: a three-zone crown stays three zones\n    zs = [lift(z) for z, _h in clumps]\n    assert zs == sorted(zs)\n\n\ndef test_a_crown_already_clear_is_left_as_it_is():\n    assert T.crown_lift([(1.0, 0.5), (2.0, 0.5)], -3.0)[0] == 1.0\n    assert T.crown_lift([], -3.0)[0] == 1.0\n    assert T.CROWN_CLEAR_M == pytest.approx(8 * 0.3048, abs=1e-3)\n\n\ndef test_a_young_tree_is_lifted_only_as_far_as_its_crown_keeps_its_shape():\n    """A tree too short to hold a crown above the clearance is not crushed into a band at its top: pressed past half\n    its height a crown stacks its cards (the generic tree at its smallest corner went 6 -> 187 coincident pairs)."""\n    z0 = -2.0                                    # a 4 m tree: its top card clears, its lowest cannot without crushing\n    k, _anchor = T.crown_lift([(-1.5, 0.4), (0.0, 0.4), (1.5, 0.4)], z0)\n    assert k == T.LIFT_K_MIN\n    assert T.squeeze(-1.0, 2.0, z0) == 1.0       # the last correction never becomes a second lift\n\n\n@pytest.mark.parametrize("species", TREES)\ndef test_bpy_no_leaf_hangs_under_the_clearance(tmp_path, species):\n    pytest.importorskip("bpy")\n    import bpy\n    from zoo_keeper.bpylayer import build\n    from zoo_keeper.core import kit\n    # a slot inside every species\' genome (a callery pear\'s width stops at 4.8 m; past it the kit builds a panel)\n    h = 6.5\n    slot = {"slot_id": "t", "role": "prop", "size_mod": "full", "style": 1, "species": species,\n            "material": "wood", "fit": {"dims": [4.0, 4.0, h], "pivot": "center"}}\n    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)\n    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,\n                             options={"save_blend": False})\n    assert res["report"]["status"] == "pass", res["report"]["checks"]\n    crown = bpy.data.objects["StreetTree_Crown"]\n    lowest = min((crown.matrix_world @ v.co).z for v in crown.data.vertices)\n    assert lowest - (-h / 2.0) >= T.CROWN_CLEAR_M - 0.02, (species, lowest + h / 2.0)\n'}
#: binary files (a font, a texture): base64, each pinned by its sha256
BINARY_FILES = {}


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
    for name in list(NEW_FILES) + list(BINARY_FILES):
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    blobs = {}
    for name, (digest, b64) in BINARY_FILES.items():
        blobs[name] = base64.b64decode(b64)
        if hashlib.sha256(blobs[name]).hexdigest() != digest:
            raise SystemExit("REFUSED: %s/%s does not decode to its sha256; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, raw in blobs.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(raw)
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES) + len(blobs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
