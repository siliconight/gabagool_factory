"""Roadmap 170, step 1: a lid on every roof hatch -- Zoo 1.113.0 `roof_hatch` + Deli Counter 0.224.0.

The census (`docs/findings/roof_openings_170/`) found 43 roof ladders climbing out through a bare hole in the
slab and nothing in any tool putting a lid on it. This ships the lid: Zoo grows a `roof_hatch` species (a steel
curb around the opening and a hinged lid, `open` by default standing on its back hinge, `closed` flush), and
Deli Counter emits one `roof_hatch` prop slot per `hatch` vertical link on the roof slab, with a `hatch`
interactive machine (open / closed) so the game can shut it and every walker keeps the ladder's exit.

New files, written beside this patch and expected to exist before it runs:
  zoo/zoo_keeper/genome/species/roof_hatch.json   zoo/zoo_keeper/recipes/roof_hatch.py   zoo/tests/test_roof_hatch.py
  deli_counter/roof_hatch.py                       deli_counter/test_roof_hatch.py
Anchored edits here (each asserted once, every touched file pinned by sha16):
  Zoo:  genome/minted.json (+roof_hatch), VERSION 1.112.0 -> 1.113.0, CHANGELOG.
  DC:   interactives.py (the `hatch` machine + kind), prop_species.py (roof_hatch owns its collision),
        deli_counter.py (import; `_vertical_links` emits the slot, its greybox box and the gameplay entry),
        VERSION 0.223.0 -> 0.224.0, CHANGELOG.

    python patches/patch_roof_hatch.py
    (cd zoo && python -m pytest -q)          (cd deli_counter && python -m pytest -q)
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ZOO = ROOT / "zoo"
DC = ROOT / "deli_counter"

NEW = [ZOO / "zoo_keeper/genome/species/roof_hatch.json", ZOO / "zoo_keeper/recipes/roof_hatch.py",
       ZOO / "tests/test_roof_hatch.py", DC / "roof_hatch.py", DC / "test_roof_hatch.py"]

SHA = {
    ZOO / "VERSION": "1daa3ef5af7e03d0",
    ZOO / "CHANGELOG.md": "c9188d80db0cb737",
    ZOO / "zoo_keeper/genome/minted.json": "7e362b08a4481fd0",
    ZOO / "tests/test_coincident_faces.py": "a85a1e8e5a5dfa12",
    DC / "interactives.py": "a0d8fcc1764444ac",
    DC / "prop_species.py": "c3fe1049c25523aa",
    DC / "deli_counter.py": "baa6b8e7ad4d0d92",
    DC / "VERSION": "23207341b828fa46",
    DC / "CHANGELOG.md": "439391f87efff2c2",
}

ZOO_CHANGELOG = """## [1.113.0] - a roof hatch: the curb and lid around a ladder's opening

**Factory roadmap 170, step 1.** The walker, 2026-09-23: a building does not have an open hole in its roof.
Counted 2026-10-15 over Deli Counter's 446 specs (the factory's `docs/findings/roof_openings_170/`): 43 roof
ladders climb out through a `hatch` link that cuts the slab, and nothing in any tool put a lid on it.

### Added
- **`roof_hatch`** (`genome/species/roof_hatch.json`, `recipes/roof_hatch.py`): a roof scuttle. Four curb walls
  on the slot's edges, the slot's exact (w, d, h) -- Deli Counter sizes it to the hole plus 0.08 m a side, 0.2 m
  tall -- and a lid plate the curb's own size, hinged on a rod along the back (local -Y) top edge.
  - **The lid is the species' interactive.** Deli Counter's `hatch` machine maps `open` and `closed` to this
    species; `state_art: ["closed"]` is what makes Zoo build the closed lid rather than defer it as identical
    art (`kit.slot_variants`). `open`, the default, stands the lid on its hinge 100 degrees from flat -- past
    vertical, leaning away from the opening the way a hold-open arm keeps a real scuttle -- and keeps a
    collision box on it (a sheet of steel a body on the roof walks into; the walker's rule, "if I see
    collision, I expect collision"). `closed` lays it flush in the curb's top with its own box over the hole.
  - **`fit_objects` is the curb.** The raised lid is art above the slot, as a swung door leaf is beside its
    frame; it must not drag the module's fit or pivot.
  - Metal, in the skylight's five styles; `tris_lod0` 300.
  - **The curb is one ring mesh, not four boxes.** The first cut's four boxes put each end wall's outer face
    on the long walls' end faces -- one plane, facing the same way -- and the census read 8 coincident pairs
    at every corner. A ring of 16 shared vertices has no two faces on a plane: `tools/coplanar_census.py`
    (Blender 5.1.1, `--species roof_hatch bollard`, the bollard the control with its known 2 / 2 / 1) reads
    the hatch's three corners at 260 / 260 / 260 tris and 0 pairs; `tests/test_coincident_faces.py` counts
    three builds more. The closed lid rests sunk `FLOATER_SKIRT` into the curb's top, as a floater rests.
- `tests/test_roof_hatch.py`: discovered and valid, `state_art` is `closed`, plans at Deli Counter's dims,
  and an interactive hatch slot yields both the open base and the built closed variant.

"""

DC_CHANGELOG = """## [0.224.0] - a lid on every roof hatch

**Factory roadmap 170, step 1** (`docs/findings/roof_openings_170/` there). A `hatch` vertical link on the roof
slab cuts the slab and emits a `HATCH_<x>_<y>` marker, and nothing put a lid on the hole: 43 roof ladders in the
library climb out through bare sky. Zoo 1.113.0 grows `roof_hatch`, a steel curb with a hinged lid; this release
stands one on every such opening.

### Added
- **`roof_hatch.py`** (pure): `roof_hatches(spec, style)` derives, for every `hatch` link whose story is the
  roof slab and that cuts it, one `prop` slot of species `roof_hatch` -- the hole plus `CURB` 0.08 m a side,
  `HEIGHT` 0.2 m, centred on the link and standing on the slab's top face (`top * story_height`) -- with the
  `hatch` interactive machine on it and its gameplay entry. `rot_for` turns the slot so the hinge side (local
  -Y) is away from the ladder's climber: `ladder.climb_rect` reserves the body's envelope along the ladder's
  `facing`, so that side is local +Y. A hatch with no ladder at its (x, y) faces north. A hatch below the roof
  is a floor-to-floor opening and gets nothing.
- **`interactives.py`: the `hatch` kind.** States `open` (default) and `closed`, both mapped to `roof_hatch`,
  `close` / `open` transitions, reversible; `collision_per_state` open False (passable), closed True. Open is
  the default so the ladder's `roof_hatch_exit` stays a route for every walker and the lid stands clear;
  shutting it is the game's, as a door's is.
- **`prop_species.SPECIES_OWNS_COLLISION`** gains `roof_hatch`: the greybox draws the slot's box for the swap
  to replace and emits no collider over the hole (a solid box there would block the ladder); the module's own
  `-colonly` boxes -- the curb, and the lid in each state -- are the collision.
- `_vertical_links` emits the slot, its greybox box and the gameplay interactive after the links' own
  markers; `test_roof_hatch.py` pins the machine, the slot, the size, the yaw, the roof-only rule and the ids.

### The library
- Rebuilt with it (`build.py --all`; the pre-commit freshness gate refused the commit until the 157 shells
  were newer than the code), so the library's 43 roof hatches carry their lids from this release. The
  bulkhead for the 16 stair heads is step 2.

"""


def sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _replace_once(text, old, new, label):
    assert text.count(old) == 1, (label, old[:70])
    return text.replace(old, new)


def main():
    pending = [str(p.relative_to(ROOT)) for p, s in SHA.items() if s == "RESULT_PENDING"]
    for p in NEW:
        assert p.exists(), f"new file missing: {p}"
    for p, want in SHA.items():
        assert b"\r\n" not in p.read_bytes(), f"{p} is CRLF; the patch assumes LF"
        if want != "RESULT_PENDING":
            assert sha16(p) == want, f"{p}: sha16 {sha16(p)} != {want}; re-ground"
    texts = {}

    def edit(p, old, new):
        t = texts.get(p) or p.read_text(encoding="utf-8")
        texts[p] = _replace_once(t, old, new, p.name)

    # --- Zoo ---------------------------------------------------------------------------------------------
    minted = json.loads((ZOO / "zoo_keeper/genome/minted.json").read_text(encoding="utf-8"))
    assert isinstance(minted, list) and "roof_hatch" not in minted
    edit(ZOO / "VERSION", "1.112.0", "1.113.0")
    edit(ZOO / "CHANGELOG.md", "## [1.112.0] - a door under its building's band says the trade",
         ZOO_CHANGELOG + "## [1.112.0] - a door under its building's band says the trade")
    # The census counts three builds more (run after the recipe was finished; the comment is the record).
    edit(ZOO / "tests/test_coincident_faces.py",
         "#: 1,500 is the genome's budget.\nCENSUS_BUILDS = 399",
         "#: 1,500 is the genome's budget.\n"
         "#: 1.113.0: `roof_hatch`, three builds more, same tool, Blender 5.1.1 --\n"
         "#: `blender -b --python tools/coplanar_census.py -- --species roof_hatch\n"
         "#: bollard`, the bollard the control (its known 2 / 2 / 1): \"6 builds, 3 with\n"
         "#: coincident pairs, 0 that did not build\", the hatch's three corners 260 / 260\n"
         "#: / 260 tris and 0 pairs. Not first run: the first cut built the curb from\n"
         "#: four boxes and read 8 pairs a corner -- each end wall's outer face on the\n"
         "#: long walls' end faces, one plane facing one way -- so the curb became one\n"
         "#: ring of 16 shared vertices (`recipes/roof_hatch._ring`), and the closed lid\n"
         "#: rests sunk FLOATER_SKIRT into its top. 300 is the genome's budget. The\n"
         "#: record is the factory's `patches/roof_hatch/census.log`.\n"
         "CENSUS_BUILDS = 402")
    # --- Deli Counter -------------------------------------------------------------------------------------
    edit(DC / "interactives.py",
         '        "collision_per_state": {"intact": True, "drilled": True},\n    },\n}\n',
         '        "collision_per_state": {"intact": True, "drilled": True},\n    },\n'
         '    "hatch": {\n'
         '        # a roof scuttle (factory roadmap 170): the lid on the hole a roof ladder\n'
         '        # climbs out through. OPEN IS THE DEFAULT -- the ladder\'s `roof_hatch_exit`\n'
         '        # is a route every walker takes, so the lid stands up out of the way until\n'
         '        # the game shuts it, as a door\'s leaf is the game\'s. Both states are\n'
         '        # `roof_hatch`: Zoo 1.113.0 draws the closed lid itself (its genome\'s\n'
         '        # `state_art`), flush in the curb, with its own collision over the hole.\n'
         '        "kind": "hatch",\n'
         '        "states": ["open", "closed"],\n'
         '        "default": "open",\n'
         '        "state_geometry": {"open": "roof_hatch", "closed": "roof_hatch"},\n'
         '        "transitions": [\n'
         '            {"event": "close", "from": "open", "to": "closed"},\n'
         '            {"event": "open", "from": "closed", "to": "open"},\n'
         '        ],\n'
         '        "reversible": True,\n'
         '        "collision_per_state": {"open": False, "closed": True},\n'
         '    },\n}\n')
    edit(DC / "interactives.py",
         '                    "safe_deposit": "safe_deposit_boxes"}',
         '                    "safe_deposit": "safe_deposit_boxes",\n'
         '                    "hatch": "hatch"}')
    edit(DC / "prop_species.py",
         'SPECIES_OWNS_COLLISION = frozenset({"cubicle_bank"})',
         '#: `roof_hatch` (0.224.0, factory roadmap 170): the module is a curb AROUND a hole\n'
         '#: with a lid in two states; a solid greybox box over the hole would block the\n'
         '#: ladder that climbs out through it.\n'
         'SPECIES_OWNS_COLLISION = frozenset({"cubicle_bank", "roof_hatch"})')
    edit(DC / "deli_counter.py", "import vault_room\n", "import vault_room\nimport roof_hatch\n")
    edit(DC / "deli_counter.py",
         '                    "breachable": bool(v.breachable)})\n\n    def _rooms(self):',
         '                    "breachable": bool(v.breachable)})\n'
         '        # A LID ON EVERY ROOF HATCH (0.224.0, factory roadmap 170): one `roof_hatch`\n'
         '        # prop slot per hatch link on the roof slab, open by default, the game\'s to\n'
         '        # shut. The species owns its collision, so the greybox draws the slot\'s box\n'
         '        # for the swap to replace and puts no collider over the hole.\n'
         '        style = skin_style.style_for(roof_hatch.MATERIAL, self._mat_style,\n'
         '                                     self.s.default_material)\n'
         '        for slot, entry, c, size in roof_hatch.roof_hatches(self.s, style=style):\n'
         '            self._box(slot["slot_id"], c, size, self.VISUAL, role="prop")\n'
         '            self.slots.append(slot)\n'
         '            self.gameplay["interactives"].append(entry)\n\n    def _rooms(self):')
    edit(DC / "VERSION", "Deli Counter 0.223.0", "Deli Counter 0.224.0")
    edit(DC / "CHANGELOG.md", "## [0.223.0] - an open floor nobody named: layout_lint L26",
         DC_CHANGELOG + "## [0.223.0] - an open floor nobody named: layout_lint L26")
    # every anchor held: write
    for p, t in texts.items():
        p.write_text(t, encoding="utf-8", newline="\n")
    minted.append("roof_hatch")
    (ZOO / "zoo_keeper/genome/minted.json").write_text(json.dumps(minted, indent=1) + "\n",
                                                        encoding="utf-8", newline="\n")
    print("roof hatch applied: Zoo 1.113.0 + Deli Counter 0.224.0; now both suites")
    if pending:
        print("pins were RESULT_PENDING for:", ", ".join(pending), "-- fill them from the pre-patch tree")


if __name__ == "__main__":
    sys.exit(main())
