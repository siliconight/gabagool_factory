"""Deli Counter 0.215.0: the stair landing and the vault's opening follow the agent contract (the walker, 2026-10-13:
"continue to update the agent contract file so we can make singular changes when we know the size of characters
in the game").

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  agent_contract.py     `stair_flight_width()` (corridor + one bake cell) and `vault_aperture()` (the door minimum
                        rounded up to 0.1, by headroom + 0.1, sill 0), after `min_corridor_width`; `import math`
  presets.py            `_stair_flight_width` returns `agent_contract.stair_flight_width()` -- the formula it
                        spelt inline, now spelt once
  stairwell.py          `LANDING_DEPTH` reads `agent_contract.stair_flight_width()` (was a literal 1.2)
  vault_room.py         `APERTURE` reads `agent_contract.vault_aperture()` (was a literal 1.3 x 2.1)
  spec_types.py         the vault default reads it through `_vault_aperture()` (was a literal 1.3 x 2.1)
  agent_contract.json   `re_derive_when`'s NOT YET FOLLOWING sentence replaced; `stair_landing_derivation` and
                        `vault_aperture_derivation`, new (`dc_contract_follows/contract_additions.json`); every
                        other value checked unchanged
  test_body_follows_contract.py   NEW (`dc_contract_follows/test_body_follows_contract.py.txt`)
CHANGELOG and VERSION from `dc_contract_follows/CHANGELOG_0.215.0.md`; `--results-pending` leaves the RESULT_
keys to `--fill`. Every value is the number it replaces, so no built shell should move: `build.py --all` after
(the freshness gate asks for it when `presets.py` moves), its manifests compared to 0.214.0's.

Read before it was written, in this session: `agent_contract.py` whole; `presets._stair_flight_width` and its
import of the contract; `stairwell`'s imports and its clearance constants; `vault_room`'s imports and Zoo's
constants block; `spec_types.Opening.resolved` and `_min_door_width` (0.214.0); `agent_contract.json` as 0.214.0
left it; Zoo's `vault_forms.plan_vault`, `recipes/vault_door` and `core/dna` (the slot's opening reaches the
recipe); a built vault-door slot (`fit.openings`); IBC 2018 section 1011.6. Every file LF.

    python patches/patch_dc_contract_follows.py --results-pending
    (build.py --all; python -m pytest -q in deli_counter)
    python patches/patch_dc_contract_follows.py --fill
"""
import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_contract_follows"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILT": "result_built.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.214.0", b"Deli Counter 0.215.0"
CHANGELOG_HEAD = "## [0.214.0] - every walkable door is at least the contract's 1.25 m, and the contract says so"
SHA = {"agent_contract.py": "cc6970b04d64dc12", "agent_contract.json": "22b41f7f05a0b25b",
       "presets.py": "e9229ce9c4bdb958", "spec_types.py": "7cbf0bc656f1784f",
       "stairwell.py": "83015065d328b19a", "vault_room.py": "e0396ef73142c266"}
NEW = {"test_body_follows_contract.py": "test_body_follows_contract.py.txt"}

AGENT_CONTRACT = [
    ("import json\nimport os\n", "import json\nimport math\nimport os\n"),
    ("def min_corridor_width():\n"
     "    return float(contract()[\"clearances\"][\"min_corridor_width_m\"])\n",
     "def min_corridor_width():\n"
     "    return float(contract()[\"clearances\"][\"min_corridor_width_m\"])\n"
     "\n"
     "\n"
     "def stair_flight_width():\n"
     "    \"\"\"The width a generator draws a stair flight at, and the depth of a\n"
     "    stair's landing, in metres: the corridor minimum and one bake cell over\n"
     "    (`clearances.stair_landing_derivation`).\n"
     "\n"
     "    A flight is a corridor to the nav bake, and one AT the minimum keeps a\n"
     "    strip whose joining depends on where the voxel grid falls (measured in\n"
     "    `presets._stair_flight_width`'s docstring). A landing as deep as the\n"
     "    flight is wide is the building code's rule (IBC 2018 section 1011.6),\n"
     "    without its 48 in cap, which assumes a human body. Spelt once, here:\n"
     "    `presets.STAIR_FLIGHT_WIDTH` and `stairwell.LANDING_DEPTH` both read it\n"
     "    (0.215.0), so a change to the body moves the flight and the landing\n"
     "    together.\n"
     "    \"\"\"\n"
     "    c = contract()\n"
     "    return round(float(c[\"clearances\"][\"min_corridor_width_m\"])\n"
     "                 + float(c[\"nav_bake\"][\"cell_size_m\"]), 3)\n"
     "\n"
     "\n"
     "def vault_aperture():\n"
     "    \"\"\"The round vault door's opening, as a fresh dict of width, height and\n"
     "    sill in metres: the door minimum rounded up to the next 0.1 m, by the\n"
     "    headroom and 0.1, on the floor (`clearances.vault_aperture_derivation`).\n"
     "\n"
     "    1.3 x 2.1, sill 0, at the ratified contract -- the numbers\n"
     "    `vault_room.APERTURE` and `spec_types`' vault default spelt beside a\n"
     "    comment giving this rule, until 0.215.0. The quotient is rounded to nine\n"
     "    places before the ceiling, so a door already on the 0.1 grid (1.3 / 0.1\n"
     "    is not always 13.0 in a float) is not rounded past it. The sill is 0\n"
     "    because 0.15 put a step above `unassisted_step_max_m` in the doorway.\n"
     "    \"\"\"\n"
     "    c = contract()[\"clearances\"]\n"
     "    width = math.ceil(round(float(c[\"min_door_width_m\"]) / 0.1, 9)) * 0.1\n"
     "    return {\"width\": round(width, 3),\n"
     "            \"height\": round(float(c[\"min_headroom_m\"]) + 0.1, 3),\n"
     "            \"sill\": 0.0}\n"),
]

PRESETS = [
    ("    import agent_contract\n"
     "    c = agent_contract.contract()\n"
     "    return round(float(c[\"clearances\"][\"min_corridor_width_m\"])\n"
     "                 + float(c[\"nav_bake\"][\"cell_size_m\"]), 3)\n"
     "\n"
     "\n"
     "STAIR_FLIGHT_WIDTH = _stair_flight_width()\n",
     "    # Spelt once, in the contract's loader (0.215.0): the stair landing is as\n"
     "    # deep as this, and both read `agent_contract.stair_flight_width`.\n"
     "    return agent_contract.stair_flight_width()\n"
     "\n"
     "\n"
     "STAIR_FLIGHT_WIDTH = _stair_flight_width()\n"),
]

STAIRWELL = [
    ("LANDING_DEPTH = 1.2             # m of clear floor at each entry/exit edge\n",
     "#: m of clear floor at each entry/exit edge: a landing as deep as the flight\n"
     "#: the generator draws is wide, the contract's corridor and one bake cell\n"
     "#: (`agent_contract.stair_flight_width`; IBC 2018 1011.6's rule without its\n"
     "#: 48 in cap). A literal 1.2 until 0.215.0, the same number.\n"
     "LANDING_DEPTH = agent_contract.stair_flight_width()\n"),
]

VAULT_ROOM = [
    ("#: `vault_forms.DEFAULT_OPENING`: the body contract's `min_door_width_m` 1.25\n"
     "#: rounded up, 2.1 m against `min_headroom_m` 2.0. Sill 0: Deli Counter's old\n"
     "#: 0.15 sat above `clearances.unassisted_step_max_m` (0.1025), the known\n"
     "#: contract tension (the factory root's \"Known contract tensions\"), and Zoo\n"
     "#: lays a 16 mm threshold plate there.\n"
     "APERTURE = {\"width\": 1.3, \"height\": 2.1, \"sill\": 0.0}\n",
     "#: `vault_forms.DEFAULT_OPENING`: the body contract's `min_door_width_m` 1.25\n"
     "#: rounded up, 2.1 m against `min_headroom_m` 2.0 -- asked of the contract\n"
     "#: since 0.215.0 (`agent_contract.vault_aperture`), where it was spelt here.\n"
     "#: Deli Counter writes it into the vault door's slot and Zoo builds the door\n"
     "#: to it. Sill 0: Deli Counter's old 0.15 sat above\n"
     "#: `clearances.unassisted_step_max_m` (0.1025), the known contract tension\n"
     "#: (the factory root's \"Known contract tensions\"), and Zoo lays a 16 mm\n"
     "#: threshold plate there.\n"
     "APERTURE = __import__(\"agent_contract\").vault_aperture()\n"),
]

SPEC_TYPES = [
    ("    import agent_contract\n"
     "    return agent_contract.min_door_width()\n",
     "    import agent_contract\n"
     "    return agent_contract.min_door_width()\n"
     "\n"
     "\n"
     "def _vault_aperture():\n"
     "    \"\"\"`agent_contract.vault_aperture()`, a fresh dict: the round vault\n"
     "    door's opening, read when a vault is resolved (0.215.0).\"\"\"\n"
     "    import agent_contract\n"
     "    return dict(agent_contract.vault_aperture())\n"),
    ("            # Zoo's round vault door (`vault_room.APERTURE`): 1.3 x 2.1 on\n"
     "            # the floor. 1.4 x 2.3 at sill 0.15 put a step above\n"
     "            # `unassisted_step_max_m` (0.1025) in the doorway.\n"
     "            \"vault\":  dict(width=1.3, height=2.1, sill=0.0),\n",
     "            # Zoo's round vault door (`vault_room.APERTURE`): the contract's\n"
     "            # `vault_aperture()`, 1.3 x 2.1 on the floor (0.215.0; a literal\n"
     "            # until then). 1.4 x 2.3 at sill 0.15 put a step above\n"
     "            # `unassisted_step_max_m` (0.1025) in the doorway.\n"
     "            \"vault\":  _vault_aperture(),\n"),
]


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
    add = json.loads((SRC / "contract_additions.json").read_text(encoding="utf-8"))
    was = json.loads(text)
    when = was["clearances"]["re_derive_when"]
    assert when.count(add["re_derive_when_old"]) == 1, "re_derive_when's sentence not found once"
    new_when = when.replace(add["re_derive_when_old"], add["re_derive_when_new"])
    line = "    \"re_derive_when\": %s,\n" % json.dumps(when)
    lines = ("    \"re_derive_when\": %s,\n" % json.dumps(new_when)
             + "    \"stair_landing_derivation\": %s,\n" % json.dumps(add["stair_landing_derivation"])
             + "    \"vault_aperture_derivation\": %s,\n" % json.dumps(add["vault_aperture_derivation"]))
    out = _anchored("agent_contract.json", text, [(line, lines)])
    now = json.loads(out)
    for key in ("stair_landing_derivation", "vault_aperture_derivation"):
        assert key not in was["clearances"] and now["clearances"][key] == add[key], key
        del now["clearances"][key]
    assert now["clearances"]["re_derive_when"] == new_when
    now["clearances"]["re_derive_when"] = when
    assert now == was, "agent_contract.json: something besides the three texts moved"
    return out


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.215.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.215.0: results filled")


def main():
    if FILL:
        return fill()
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.215.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.215.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (DC / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in (("agent_contract.py", AGENT_CONTRACT), ("presets.py", PRESETS),
                       ("stairwell.py", STAIRWELL), ("vault_room.py", VAULT_ROOM),
                       ("spec_types.py", SPEC_TYPES)):
        eol, text = _read(rel)
        writes[rel] = (_anchored(rel, text, edits), eol)
    eol, text = _read("agent_contract.json")
    writes["agent_contract.json"] = (_contract(text), eol)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    for rel, (body, _e) in writes.items():
        if rel.endswith(".py"):
            compile(body, rel, "exec")
    # every anchor matched: now write
    for rel, (body, e) in writes.items():
        (DC / rel).write_bytes(body.encode("utf-8").replace(b"\n", e))
    for r, data in news.items():
        (DC / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(VERSION)
    print("Deli Counter 0.214.0 -> 0.215.0")


if __name__ == "__main__":
    main()
