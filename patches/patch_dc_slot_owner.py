"""Deli Counter 0.203.0: a slot owns its own greybox nodes, never a sibling
slot's (roadmap 205).

    python patch_dc_slot_owner.py            # apply
    python patch_dc_slot_owner.py --check    # verify every anchor, write nothing

The placement gate (`portable_building._slot_greybox_extent`) and the
composer's fit (`themed_tscn._slot_extent`) counted a greybox node as the
slot's when its name was the slot id or began `<slot_id>_` -- the rule for an
opening's own parts. A sibling slot whose id begins the same way was
swallowed: gas_station_a02's `cooler_run` (3.28 m) took in `cooler_run_sales`
(8.0 m) and read 25.442 m, and the gate stopped cold run 9195's art leg on a
module built exactly to its slot. 5 library buildings carry such a sibling
with greybox nodes (the three pawn shops' `counter`, the two gas stations'
`cooler_run`).

One rule now, in `themed_tscn` (which `portable_building` already imports):
`longer_siblings(slot_id, slot_ids)` and `owns_node(slot_id, node, siblings)`
-- a node belongs to the longest slot id that names it. Both extents take the
building's slot ids, and both callers pass them.

Anchored on, as read 2026-10-07 (all LF):
  deli_counter/themed_tscn.py         44,123 bytes
  deli_counter/portable_building.py   42,406 bytes
Every anchor must match once; nothing is written until every file matched.
`themed_tscn.py` is in `build_freshness.GEOMETRY_SOURCES`: apply AFTER the
tests are proven failing, then `python build.py --all` once.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

THEMED = [
    ("def _slot_extent(per, slot_id):\n"
     "    lo = [1e18] * 3\n"
     "    hi = [-1e18] * 3\n"
     "    found = False\n"
     "    for nm, (l, h) in per.items():\n"
     "        # precise: the slot's node or a named sub-part (<slot_id>_lintel/...),\n"
     "        # never a numeric sibling (seg1 must not swallow seg10). See\n"
     "        # portable_building._slot_greybox_extent for the rationale.\n"
     "        if slot_id and (nm == slot_id or nm.startswith(slot_id + \"_\")):\n",
     "def longer_siblings(slot_id, slot_ids):\n"
     "    \"\"\"The slot ids that begin `<slot_id>_`: SIBLING slots, not parts of this\n"
     "    one (0.203.0, roadmap 205). gas_station_a02's `cooler_run_sales` begins\n"
     "    `cooler_run_`, and the pawn shops' `counter_service_..._1` begins\n"
     "    `counter_`.\"\"\"\n"
     "    return [x for x in slot_ids\n"
     "            if x and x != slot_id and x.startswith(slot_id + \"_\")]\n"
     "\n"
     "\n"
     "def owns_node(slot_id, node_name, siblings):\n"
     "    \"\"\"Does greybox node `node_name` belong to `slot_id`?\n"
     "\n"
     "    It does when it is the slot's own node or a named part of it\n"
     "    (`<slot_id>_lintel`, `_sill`, `_pane`) -- never a numeric neighbour\n"
     "    (`seg1` does not own `seg10`) -- and no LONGER slot id in `siblings`\n"
     "    (`longer_siblings`) names it. A node belongs to the longest slot id that\n"
     "    names it (0.203.0, roadmap 205). The placement gate\n"
     "    (`portable_building._slot_greybox_extent`) and the composer's fit\n"
     "    (`_slot_extent`) both ask this, so the two cannot disagree.\n"
     "    \"\"\"\n"
     "    if not slot_id or not (node_name == slot_id\n"
     "                           or node_name.startswith(slot_id + \"_\")):\n"
     "        return False\n"
     "    return not any(node_name == x or node_name.startswith(x + \"_\")\n"
     "                   for x in siblings)\n"
     "\n"
     "\n"
     "def _slot_extent(per, slot_id, slot_ids):\n"
     "    # ONE SLOT'S NODES ONLY (0.203.0, roadmap 205): the prefix rule alone let\n"
     "    # gas_station_a02's `cooler_run` (3.28 m) take in `cooler_run_sales`\n"
     "    # (8.0 m, 20 m away) and fit its module against 25.442 m. `slot_ids` is\n"
     "    # every slot of the building; see `owns_node`.\n"
     "    siblings = longer_siblings(slot_id, slot_ids)\n"
     "    lo = [1e18] * 3\n"
     "    hi = [-1e18] * 3\n"
     "    found = False\n"
     "    for nm, (l, h) in per.items():\n"
     "        # precise: the slot's node or a named sub-part (<slot_id>_lintel/...),\n"
     "        # never a numeric sibling (seg1 must not swallow seg10), never a\n"
     "        # sibling slot. See portable_building._slot_greybox_extent.\n"
     "        if owns_node(slot_id, nm, siblings):\n"),
    ("    for sl in slots:\n"
     "        ref = resolved_refs[id(sl)]\n"
     "        if not ref:\n"
     "            continue\n",
     "    # every slot id of the building, so a fit measures one slot's greybox\n"
     "    # nodes and never a sibling's (`owns_node`, 0.203.0)\n"
     "    slot_ids = {s.get(\"slot_id\") for s in slots if s.get(\"slot_id\")}\n"
     "    for sl in slots:\n"
     "        ref = resolved_refs[id(sl)]\n"
     "        if not ref:\n"
     "            continue\n"),
    ("            ge = _slot_extent(gb_per, sl.get(\"slot_id\", \"\"))\n",
     "            ge = _slot_extent(gb_per, sl.get(\"slot_id\", \"\"), slot_ids)\n"),
]

PORTABLE = [
    ("def _slot_greybox_extent(gb_bboxes, slot_id):\n"
     "    \"\"\"Union bbox of greybox nodes carrying the slot_id (an opening's\n"
     "    lintel/sill/pane sub-parts all share the slot_id).\"\"\"\n"
     "    lo = [1e18] * 3\n",
     "def _slot_greybox_extent(gb_bboxes, slot_id, slot_ids):\n"
     "    \"\"\"Union bbox of greybox nodes carrying the slot_id (an opening's\n"
     "    lintel/sill/pane sub-parts all share the slot_id) -- and only this\n"
     "    slot's: `slot_ids` is every slot of the building, so a sibling whose id\n"
     "    begins `<slot_id>_` keeps its own nodes (0.203.0, roadmap 205).\"\"\"\n"
     "    siblings = themed_tscn.longer_siblings(slot_id, slot_ids)\n"
     "    lo = [1e18] * 3\n"),
    ("        # only because the local-space union collapsed them onto the origin.\n"
     "        if nm == slot_id or nm.startswith(slot_id + \"_\"):\n",
     "        # only because the local-space union collapsed them onto the origin.\n"
     "        # AND NOT A SIBLING SLOT (0.203.0, roadmap 205): the prefix rule alone\n"
     "        # let gas_station_a02's `cooler_run` (3.28 m) take in\n"
     "        # `cooler_run_sales` (8.0 m) and read 25.442 m, refusing a module\n"
     "        # built exactly to its slot and stopping cold run 9195's art leg.\n"
     "        # One rule, shared with the composer's fit: `themed_tscn.owns_node`.\n"
     "        if themed_tscn.owns_node(slot_id, nm, siblings):\n"),
    ("    gb = _glb_visual_bboxes(greybox_glb)\n"
     "    cache = {}\n"
     "    checked = matched = 0\n",
     "    gb = _glb_visual_bboxes(greybox_glb)\n"
     "    # every slot id of the building: an extent is one slot's nodes, never a\n"
     "    # sibling's (0.203.0). Listed first, since `slots` is walked twice.\n"
     "    slots = list(slots)\n"
     "    slot_ids = {x.get(\"slot_id\") for x in slots if x.get(\"slot_id\")}\n"
     "    cache = {}\n"
     "    checked = matched = 0\n"),
    ("        ge = _slot_greybox_extent(gb, sid)\n",
     "        ge = _slot_greybox_extent(gb, sid, slot_ids)\n"),
]

FILES = [
    (DC / "themed_tscn.py", 44123, THEMED),
    (DC / "portable_building.py", 42406, PORTABLE),
]


def main():
    check = "--check" in sys.argv[1:]
    staged = []
    for path, size, edits in FILES:
        data = path.read_bytes()
        assert len(data) == size, "%s is %d bytes, read at %d" % (path.name, len(data), size)
        assert b"\r\n" not in data, "%s has CRLF; it was LF" % path.name
        text = data.decode("utf-8")
        for old, new in edits:
            assert text.count(old) == 1, "%s: anchor found %d times: %r" % (path.name, text.count(old), old[:70])
            text = text.replace(old, new)
        staged.append((path, data, text))
    for path, data, text in staged:
        if check:
            print("%s: every anchor matched once (%d -> %d bytes, not written)"
                  % (path.name, len(data), len(text.encode("utf-8"))))
            continue
        path.write_bytes(text.encode("utf-8"))
        print("%s: %d -> %d bytes" % (path.name, len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
