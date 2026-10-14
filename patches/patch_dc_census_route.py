"""Deli Counter 0.216.0: the census's body-sized literals read the agent contract, and combat_audit reads the builder's
openings (the walker, 2026-10-13: "continue to update the agent contract file so we can make singular changes
when we know the size of characters in the game"; the census: `docs/findings/agent_contract_follows/`).

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  agent_contract.py   accessors after `vault_aperture`: body_height, body_eye_height, max_step_up, nav_radius,
                      door_approach (layout_lint's formula, spelt once)
  enterability.py     MIN_PASS_WIDTH = 2 body radii; STAND_HEIGHT = body height
  stairwell.py        _AGENT_PASS_WIDTH = 2 body radii
  sightlines.py       EYE, SIGHT_BLOCK_H = the body's eye
  vault_room.py       DOOR_WIDTH = the door minimum; APPROACH = door_approach()
  layout_lint.py      _door_approach_m returns agent_contract.door_approach()
  guards.py           MAX_STEP_UP = the body's step-up
  combat_audit.py     WIDE_DOOR = 4 body radii; _op_width reads Opening.resolved() -- KIND_DEFAULT_W removed
  lights.py           _AISLE_MIN_FALLBACK = the door minimum
  level_design.py     _CLUSTER_GAP's upper end = 2 bake radii
  ladder_geom.py      HOLE_ALONG = CLIMB_STANDOFF + body radius + HOLE_ALONG_MARGIN (0.45, now named)
  test_contract_census.py   NEW (`dc_census_route/test_contract_census.py.txt`)
CHANGELOG and VERSION from `dc_census_route/CHANGELOG_0.216.0.md`; `--results-pending` leaves the RESULT_ keys
to `--fill`. Every value but combat_audit's two stale defaults is the literal it replaces, exactly in a float
(each checked before this was written), so `build.py --all` after should move no output.

Read before it was written, in this session: each constant's line and comment (the census's output, then the
comment blocks whole); `agent_contract.py` as 0.215.0 left it; `layout_lint._door_approach_m`;
`combat_audit`'s `_op_width` and its four callers and `WIDE_DOOR`'s use; each module's imports
(`agent_contract` has none of this repo's, so no cycle). Every file LF.

    python patches/patch_dc_census_route.py --results-pending
    (build.py --all; python -m pytest -q in deli_counter; combat_audit.py --all and --all-presets against
     the 0.215.0 outputs)
    python patches/patch_dc_census_route.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_census_route"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AUDIT": "result_audit.txt", "RESULT_BUILT": "result_built.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.215.0", b"Deli Counter 0.216.0"
CHANGELOG_HEAD = "## [0.215.0] - the stair landing and the vault's opening follow the agent contract"
SHA = {"agent_contract.py": "4055c12aa9e5643c", "enterability.py": "3e090bd56f89e0a4",
       "stairwell.py": "36082e3027642d81", "sightlines.py": "d5ae4f81c52345c1",
       "vault_room.py": "ed39202272fd7cf9", "layout_lint.py": "461a001c7705482d",
       "guards.py": "f65c3d5c918c4180", "combat_audit.py": "099f1178e2a296d2",
       "lights.py": "0d11fa424685d0b2", "level_design.py": "f333595b52a139f2",
       "ladder_geom.py": "ab9ff7f5adf5cc55"}
NEW = {"test_contract_census.py": "test_contract_census.py.txt"}
AC = "__import__(\"agent_contract\")"

EDITS = {
    "agent_contract.py": [
        ("    return {\"width\": round(width, 3),\n"
         "            \"height\": round(float(c[\"min_headroom_m\"]) + 0.1, 3),\n"
         "            \"sill\": 0.0}\n",
         "    return {\"width\": round(width, 3),\n"
         "            \"height\": round(float(c[\"min_headroom_m\"]) + 0.1, 3),\n"
         "            \"sill\": 0.0}\n"
         "\n"
         "\n"
         "# THE BODY'S OTHER NUMBERS, ASKED (0.216.0). The factory's census of this\n"
         "# repo's literals found each of these spelt beside a comment naming it; the\n"
         "# walker wants one change to this file to re-size everything.\n"
         "\n"
         "def body_height():\n"
         "    \"\"\"The player capsule's height, in metres (`characters.player.height_m`).\"\"\"\n"
         "    return float(contract()[\"characters\"][\"player\"][\"height_m\"])\n"
         "\n"
         "\n"
         "def body_eye_height():\n"
         "    \"\"\"Where the BODY's eye is, in metres above its feet\n"
         "    (`characters.player.eye_height_m`): the standing eye an offline sightline\n"
         "    is drawn from. Not `eye_height()`, which is the gameplay camera's\n"
         "    (`review.gameplay_camera_eye_m`) -- two fields, both 1.6 at the ratified\n"
         "    contract.\"\"\"\n"
         "    return float(contract()[\"characters\"][\"player\"][\"eye_height_m\"])\n"
         "\n"
         "\n"
         "def max_step_up():\n"
         "    \"\"\"What a controller can lift itself over, in metres\n"
         "    (`characters.player.max_step_up_m`).\"\"\"\n"
         "    return float(contract()[\"characters\"][\"player\"][\"max_step_up_m\"])\n"
         "\n"
         "\n"
         "def nav_radius():\n"
         "    \"\"\"The BAKE's agent radius, in metres (`nav_bake.agent_radius_m`): the\n"
         "    fattest navigating body plus 0.05. Not a body -- `body_radius()` is.\"\"\"\n"
         "    return float(contract()[\"nav_bake\"][\"agent_radius_m\"])\n"
         "\n"
         "\n"
         "def door_approach():\n"
         "    \"\"\"The floor a body needs in front of a door, in metres: two body radii\n"
         "    and 0.3. `layout_lint.DOOR_APPROACH_M` spelt this formula and\n"
         "    `vault_room.APPROACH` its value; both read it here since 0.216.0.\"\"\"\n"
         "    return 2.0 * body_radius() + 0.3\n"),
    ],
    "enterability.py": [
        ("MIN_PASS_WIDTH = 0.7     # below this, the default capsule can't fit at all\n",
         "# The contract's body, asked (0.216.0): two radii, and its height.\n"
         "MIN_PASS_WIDTH = 2.0 * %s.body_radius()  # below this, the default capsule can't fit at all\n" % AC),
        ("STAND_HEIGHT   = 1.8     # at/above = walk in standing; between = crouch-only\n",
         "STAND_HEIGHT   = %s.body_height()  # at/above = walk in standing; between = crouch-only\n" % AC),
    ],
    "stairwell.py": [
        ("_AGENT_PASS_WIDTH = 0.7      # capsule pass band (docs/scale_guidelines.md)\n",
         "# capsule pass band (docs/scale_guidelines.md): two of the contract's body\n"
         "# radii, asked (0.216.0; a literal 0.7, the same number)\n"
         "_AGENT_PASS_WIDTH = 2.0 * agent_contract.body_radius()\n"),
    ],
    "sightlines.py": [
        ("EYE = 1.6            # standing eye height (volume must cross this to block)\n"
         "SIGHT_BLOCK_H = 1.6  # a volume taller than this blocks standing sight\n",
         "# The contract's body's eye, asked (0.216.0; both were a literal 1.6).\n"
         "EYE = %s.body_eye_height()  # standing eye height (volume must cross this to block)\n"
         "SIGHT_BLOCK_H = EYE  # a volume taller than this blocks standing sight\n" % AC),
    ],
    "vault_room.py": [
        ("#: `agent_contract.min_door_width_m`.\n"
         "DOOR_WIDTH = 1.25\n",
         "#: `agent_contract.min_door_width_m`, asked (0.216.0; a literal 1.25).\n"
         "DOOR_WIDTH = __import__(\"agent_contract\").min_door_width()\n"),
        ("#: Floor a body needs in front of a door (layout_lint.DOOR_APPROACH_M:\n"
         "#: 2 x player radius + 0.3).\n"
         "APPROACH = 1.0\n",
         "#: Floor a body needs in front of a door (layout_lint.DOOR_APPROACH_M:\n"
         "#: 2 x player radius + 0.3), asked of `agent_contract.door_approach` (0.216.0;\n"
         "#: a literal 1.0).\n"
         "APPROACH = __import__(\"agent_contract\").door_approach()\n"),
    ],
    "layout_lint.py": [
        ("def _door_approach_m():\n"
         "    import agent_contract\n"
         "    r = float(agent_contract.contract()[\"characters\"][\"player\"][\"radius_m\"])\n"
         "    return 2.0 * r + 0.3\n",
         "def _door_approach_m():\n"
         "    # Spelt once, in the contract's loader (0.216.0): `vault_room.APPROACH`\n"
         "    # reads the same function.\n"
         "    import agent_contract\n"
         "    return agent_contract.door_approach()\n"),
    ],
    "guards.py": [
        ("MAX_STEP_UP = 0.5        # m \u2014 the recommended player step-up budget\n",
         "# the contract's `characters.player.max_step_up_m`, asked (0.216.0; a literal 0.5)\n"
         "MAX_STEP_UP = %s.max_step_up()  # m \u2014 the recommended player step-up budget\n" % AC),
    ],
    "combat_audit.py": [
        ("WIDE_DOOR = 1.4          # >= passes two agents / a loot carry comfortably\n"
         "KIND_DEFAULT_W = {\"door\": 1.2, \"window\": 1.6, \"garage\": 3.5, \"breach\": 1.5,\n"
         "                  \"vault\": 1.4, \"teller\": 2.0, \"safe_deposit\": 2.0}\n"
         "\n"
         "\n"
         "def _op_width(op):\n"
         "    w = getattr(op, \"width\", None)\n"
         "    return w if w is not None else KIND_DEFAULT_W.get(op.kind, 1.2)\n",
         "# >= passes two agents / a loot carry comfortably: four of the contract's body\n"
         "# radii, asked (0.216.0; a literal 1.4, the same number)\n"
         "WIDE_DOOR = 4.0 * __import__(\"agent_contract\").body_radius()\n"
         "\n"
         "\n"
         "def _op_width(op):\n"
         "    # The width the builder BUILDS (0.216.0): `Opening.resolved`. This kept its\n"
         "    # own copy of the defaults, and two were stale -- a width-less door at 1.2\n"
         "    # where the builder uses the contract's 1.25 (0.214.0), a width-less vault\n"
         "    # at 1.4 where it uses `vault_aperture`'s 1.3.\n"
         "    return float(op.resolved()[\"width\"])\n"),
    ],
    "lights.py": [
        ("#: `clearances.min_door_width_m`, the number `island_aisle_width` returns.\n"
         "_AISLE_MIN_FALLBACK = 1.25\n",
         "#: `clearances.min_door_width_m`, the number `island_aisle_width` returns --\n"
         "#: asked of the contract, which can always be asked (0.216.0; a literal 1.25).\n"
         "_AISLE_MIN_FALLBACK = __import__(\"agent_contract\").min_door_width()\n"),
    ],
    "level_design.py": [
        ("#: Below the 0.8 m a 0.4 m-radius body needs, so a cluster is one obstacle to\n"
         "#: the navmesh, and is cleared from everything else as one.\n"
         "_CLUSTER_GAP = (0.3, 0.8)\n",
         "#: Below the 0.8 m a 0.4 m-radius body needs, so a cluster is one obstacle to\n"
         "#: the navmesh, and is cleared from everything else as one. The upper end is\n"
         "#: two of the contract's BAKE radii, asked (0.216.0; a literal 0.8).\n"
         "_CLUSTER_GAP = (0.3, 2.0 * __import__(\"agent_contract\").nav_radius())\n"),
    ],
    "ladder_geom.py": [
        ("# Body clearance the through-hole provides along the approach direction:\n"
         "# standoff + capsule radius + margin. Biased: HOLE_BEHIND behind the face.\n"
         "HOLE_ALONG = 1.3\n",
         "# Body clearance the through-hole provides along the approach direction:\n"
         "# standoff + capsule radius + margin. Biased: HOLE_BEHIND behind the face.\n"
         "# The radius is the contract's body's, asked (0.216.0; HOLE_ALONG was a\n"
         "# literal 1.3, the same number); the margin was never derived and is named.\n"
         "HOLE_ALONG_MARGIN = 0.45\n"
         "HOLE_ALONG = round(CLIMB_STANDOFF + __import__(\"agent_contract\").body_radius()\n"
         "                   + HOLE_ALONG_MARGIN, 3)\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.216.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.216.0: results filled")


def main():
    if FILL:
        return fill()
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.216.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.216.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (DC / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in EDITS.items():
        raw = (DC / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:70])
            text = text.replace(old, new)
        compile(text, rel, "exec")
        writes[rel] = (text, eol)
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
    print("Deli Counter 0.215.0 -> 0.216.0")


if __name__ == "__main__":
    main()
