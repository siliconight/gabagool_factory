"""Deli Counter 0.214.0: every walkable door is at least the contract's 1.25 m, and the contract says so (factory
roadmap 197; the walker, 2026-10-13: "widen the doors and keep 1.25", called out in the agent contract).

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  spec_types.py         a width-less door resolves to `agent_contract.min_door_width()` (`_min_door_width`),
                        not 1.2
  stair_core.py         `_PUNCH_DOOR_W` reads the contract's `min_corridor_width_m` (1.1, the number it was),
                        commented with why it is under the door minimum; a crossing exactly the door's width
                        is punched (a 1e-9 tolerance); the doored check reads a width-less door through
                        `Opening.resolved()` instead of a literal 1.2
  level_design.py       `_STAFF_DOOR_WIDTH` reads the contract's `min_door_width_m` (1.25, the number it was)
  presets.py            61 narrow door literals in 15 enterable presets -> `DOOR_W`, the contract's minimum
                        (`dc_door_width/presets_doors.py`, which asserts both counts)
  agent_contract.json   `clearances.derivation` re-worked at the contract's own 0.1 cell;
                        `clearances.min_door_width_note` and `clearances.re_derive_when`, new
                        (`dc_door_width/contract_clearances.json`); every other value checked unchanged

The walker, after the pause: "continue to update the agent contract file so we can make singular changes when we
know the size of characters in the game". So every door width this builder's code writes reads the contract --
the two literals that spelt its numbers (the staff door's 1.25, the punched landing door's 1.1) included -- and
`re_derive_when` says what one change to a body moves, and what does not follow yet.
  migrate_door_width.py NEW (`dc_door_width/migrate_door_width.py.txt`), then RUN: 152 doors in 29 specs
  test_door_width.py    NEW (`dc_door_width/test_door_width.py.txt`)
CHANGELOG and VERSION from `dc_door_width/CHANGELOG_0.214.0.md`; `--results-pending` leaves the RESULT_ keys to
`--fill`, which also corrects the entry's `re_derive_when` bullet (`ENTRY_EDITS`) once
`patch_dc_door_width_vault_note.py`, the release's second edit, has named the vault aperture. The shells are rebuilt after (`build.py --all`: `presets.py` moves, so the build-freshness gate asks
for every shell).

Read before it was written, in this session: `spec_types.Opening` and `resolved`; `stair_core`'s constants,
`_punch_door` and its one call site; `presets.py`'s imports, every door literal and `make`; `agent_contract.json`
whole and `agent_contract.py` whole (`contract()` merges the file over `_DEFAULTS`, and
`test_agent_contract.py` pairs only the keys `_DEFAULTS` carries, so a new note key is not one of them);
`navigability.check` (it warns); `level_design`'s aisle and staff door; `stairwell`'s landing; Level Factory's
Deli Counter adapter (`new_level.py` with mode, floors, basement, seed, never `--stairs-first`); the 0.213.0
CHANGELOG entry. Every file LF.

    python patches/patch_dc_door_width.py --results-pending
    (build.py --all)
    python patches/patch_dc_door_width_vault_note.py
    python patches/patch_dc_door_width_refurnish.py
    (build.py specs/<name>.json for its 8 specs; python -m pytest -q in deli_counter)
    python patches/patch_dc_door_width.py --fill
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_door_width"
sys.path.insert(0, str(SRC))
import presets_doors   # noqa: E402

PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILT": "result_built.txt", "RESULT_SUITE": "result_suite.txt",
           "RESULT_STAIRS_FIRST": "result_stairs_first.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.213.0", b"Deli Counter 0.214.0"
CHANGELOG_HEAD = "## [0.213.0] - mid-rise Empties: five to twelve storeys of brick, out of today's streets"
SHA = {"spec_types.py": "669dd187cebca754", "stair_core.py": "9d3cac8b7d82e52a",
       "presets.py": "4c3e9cd80276bfef", "agent_contract.json": "0224405895d0dad1",
       "level_design.py": "6df932b71fd838df"}
CONTRACT_KEYS = ["derivation", "min_door_width_note", "re_derive_when"]
NEW = {"migrate_door_width.py": "migrate_door_width.py.txt", "test_door_width.py": "test_door_width.py.txt"}
MIGRATED = "29 spec(s): 152 door(s) to 1.25 m"

SPEC_TYPES = [
    ("            \"door\":   dict(width=1.2, height=2.2, sill=0.0),\n",
     "            # A WIDTH-LESS DOOR IS THE CONTRACT'S (0.214.0, factory roadmap\n"
     "            # 197): `clearances.min_door_width_m`, read when the door is\n"
     "            # resolved. It was 1.2, under the contract's 1.25, and 47 of the\n"
     "            # library's doors were built at it.\n"
     "            \"door\":   dict(width=_min_door_width(), height=2.2, sill=0.0),\n"),
    ("@dataclass\nclass Opening:\n",
     "def _min_door_width():\n"
     "    \"\"\"`agent_contract.min_door_width()`: the width a door with none of its\n"
     "    own is built at. Read when a door is resolved, so a contract named by\n"
     "    $DC_AGENT_CONTRACT is the one that answers.\"\"\"\n"
     "    import agent_contract\n"
     "    return agent_contract.min_door_width()\n"
     "\n"
     "\n"
     "@dataclass\nclass Opening:\n"),
]

LEVEL_DESIGN = [
    ("_STAFF_DOOR_WIDTH = 1.25            # agent_contract min_door_width_m\n",
     "#: The contract's `min_door_width_m`, asked (0.214.0, factory roadmap 197). It\n"
     "#: was a literal 1.25 beside a comment naming the contract, while\n"
     "#: `staff_aisle_width` says the staff room asks the contract for its door: a\n"
     "#: contract that moved the number would have left this door where it was.\n"
     "_STAFF_DOOR_WIDTH = __import__(\"agent_contract\").min_door_width()\n"),
]

STAIR_CORE = [
    ("import stair_place\nimport stairwell\n",
     "import stair_place\nimport stairwell\nfrom spec_types import Opening\n"),
    ("_PUNCH_DOOR_W = 1.1     # m; door punched where an enclosure crosses a landing\n",
     "#: The door punched where an enclosure crosses a landing, in m: the contract's\n"
     "#: `min_corridor_width_m` (0.214.0, factory roadmap 197; it was a literal 1.1,\n"
     "#: the same number), so a change to the body moves it with the corridor and\n"
     "#: the flight (`presets.STAIR_FLIGHT_WIDTH`, the corridor plus a cell). Of the\n"
     "#: 20 crossings in `stair_regression`'s 140 variants, 18 are 1.2 m -- a\n"
     "#: flight's width and `stairwell.LANDING_DEPTH` are both 1.2 -- and 2 are\n"
     "#: 1.1, the door's own. It is UNDER `min_door_width_m` (1.25), and the\n"
     "#: contract names it: at 1.25 none of the 20 is punched and the sweep's checks\n"
     "#: fail 21 times against 2 -- 16 a stair's top flight facing the solid\n"
     "#: partition (STAIR_EXIT_FACES_SOLID), 3 a prop in a stair's reserved volume.\n"
     "#: Level Factory never builds stairs-first.\n"
     "_PUNCH_DOOR_W = __import__(\"agent_contract\").min_corridor_width()\n"),
    ("    if ov1 - ov0 < _PUNCH_DOOR_W:\n"
     "        return False                      # crossing too short for a doorway\n",
     "    # A crossing exactly the door's width is not too short. Two of the 20\n"
     "    # measured are 1.1000000000000014 against a 1.1 door and were punched by\n"
     "    # 1.4e-15; spelt 6.1 - 5.0, the same crossing is 1.0999999999999996 and\n"
     "    # was not (0.214.0).\n"
     "    if ov1 - ov0 < _PUNCH_DOOR_W - 1e-9:\n"
     "        return False                      # crossing too short for a doorway\n"),
    ("            half = (op.get(\"width\") or 1.2) / 2\n",
     "            # The width it is BUILT at: a width-less door is the contract's\n"
     "            # minimum (0.214.0), and garages, breaches and vaults have their\n"
     "            # own. This read a literal 1.2 for all four.\n"
     "            half = Opening(kind=op.get(\"kind\", \"door\"),\n"
     "                           width=op.get(\"width\")).resolved()[\"width\"] / 2\n"),
]

DERIVATION_WAS = ("    \"derivation\": \"min_door_width >= 2*ceil(agent_radius/cell_size)*cell_size + 2*cell_size  ->  "
                  "2*ceil(0.4/0.15)*0.15 + 0.3 = 1.2; ratified 1.25 for margin. min_corridor = 2*agent_radius + "
                  "0.3 body margin.\",\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _read(rel):
    raw = (DC / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _anchored(rel, text, edits):
    for old, new in edits:
        assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:70])
        text = text.replace(old, new)
    return text


def _contract(text):
    """The derivation's line replaced and the two new keys written after it, each string through
    `json.dumps`; then the whole file is parsed both ways and everything else asserted unmoved."""
    clear = json.loads((SRC / "contract_clearances.json").read_text(encoding="utf-8"))
    assert sorted(clear) == sorted(CONTRACT_KEYS), sorted(clear)
    new_lines = "".join("    \"%s\": %s,\n" % (key, json.dumps(clear[key])) for key in CONTRACT_KEYS)
    out = _anchored("agent_contract.json", text, [(DERIVATION_WAS, new_lines)])
    was, now = json.loads(text), json.loads(out)
    assert "min_door_width_note" not in was["clearances"] and "re_derive_when" not in was["clearances"]
    for key in CONTRACT_KEYS:
        assert now["clearances"][key] == clear[key], key
    del now["clearances"]["min_door_width_note"], now["clearances"]["re_derive_when"]
    now["clearances"]["derivation"] = was["clearances"]["derivation"]
    assert now == was, "agent_contract.json: something besides the door texts moved"
    return out


#: Applied by `--fill` with the results, to the entry and to Deli Counter's CHANGELOG alike. The entry was
#: written before the release's second and third edits: `patch_dc_door_width_vault_note.py` named a second
#: body-sized literal in `re_derive_when`, and `patch_dc_door_width_refurnish.py` refurnished the library.
ENTRY_EDITS = [
    ("    follows on its own, what needs the migration re-run, and the one body-sized number that does not follow\n"
     "    yet: `stairwell.LANDING_DEPTH`, a literal 1.2.\n",
     "    follows on its own, what needs the migration re-run, and the body-sized numbers that do not follow\n"
     "    yet: `stairwell.LANDING_DEPTH`, a literal 1.2, and the vault door's aperture, 1.3 x 2.1 m, spelt in\n"
     "    `vault_room.APERTURE`, `spec_types`' vault default and Zoo's `vault_forms.DEFAULT_OPENING`. The vault\n"
     "    is named by the release's second edit, `patch_dc_door_width_vault_note.py`.\n"),
    ("    clear, it fails L21, hanging 0.12 m over the basement stair's hole. No place on that wall holds it\n"
     "    until the stair moves.\n",
     "    clear, it fails L21, hanging 0.12 m over the basement stair's hole. No place on that wall holds it\n"
     "    until the stair moves.\n"
     "- **The library refurnished around its wider doors** (`migrate_furnish_recipes.py`, the release's third\n"
     "  edit, `patch_dc_door_width_refurnish.py`). The library is held to be a fixed point of the furnishing\n"
     "  pass, and widening a door moves what furnish puts beside it: the full suite failed both fixed-point\n"
     "  tests on `cr_gas`. Measured spec by spec (the factory's `docs/findings/door_widths/refurnish_delta.py`),\n"
     "  the refurnish moves 8 specs, every one a spec whose doors changed:\n"
     "  - `cr_gas`, `foundry_heist_vertical`, `gas_station`, `gas_street` and `gs_corner_station`: pieces\n"
     "    move, none lost;\n"
     "  - `cr_pawn` loses a cartons stack and a floor safe, and `stop_n_go` its back-room cigarette rack;\n"
     "  - `rowhouse_raid` gains four chair sets.\n"
     "  The rack stood 0.96 m from `rear_service`, which widened 1.0 -> 1.25 m, so `test_club_fixtures`' pin\n"
     "  on the library's cigarette machines moves 119 -> 118 with that reason beside it. The 8 shells are\n"
     "  rebuilt. `migrate_furnish_recipes.py --check`'s own summary is not a measure of this: it reads\n"
     "  -7,923 / +7,819 on 0.213.0, where the library is a fixed point.\n"),
]


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.214.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        text = _anchored(rel, text, ENTRY_EDITS)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.214.0: results filled")


def main():
    if FILL:
        return fill()
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.214.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.214.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (DC / rel).exists(), ("already applied", rel)

    writes = {}
    eol, text = _read("spec_types.py")
    writes["spec_types.py"] = (_anchored("spec_types.py", text, SPEC_TYPES), eol)
    eol, text = _read("stair_core.py")
    writes["stair_core.py"] = (_anchored("stair_core.py", text, STAIR_CORE), eol)
    eol, text = _read("level_design.py")
    writes["level_design.py"] = (_anchored("level_design.py", text, LEVEL_DESIGN), eol)
    eol, text = _read("presets.py")
    widened, funcs = presets_doors.widen(text)
    writes["presets.py"] = (widened, eol)
    eol, text = _read("agent_contract.json")
    writes["agent_contract.json"] = (_contract(text), eol)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]

    # every anchor matched: now write
    for rel, (body, e) in writes.items():
        (DC / rel).write_bytes(body.encode("utf-8").replace(b"\n", e))
    for r, data in news.items():
        (DC / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(VERSION)
    print("presets at DOOR_W: %s" % ", ".join(funcs))
    run = subprocess.run([sys.executable, "migrate_door_width.py"], cwd=DC, check=True,
                         capture_output=True, text=True)
    print(run.stdout.rstrip())
    last = run.stdout.strip().splitlines()[-1]
    assert last == MIGRATED, ("the migration did not do what was measured", last)
    print("Deli Counter 0.213.0 -> 0.214.0")


if __name__ == "__main__":
    main()
