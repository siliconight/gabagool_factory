r"""Is this package lightable by somebody who is not Lux? Measure, do not assume.

    python probe_lightable.py <site.site.lights.json> [--json]

`probe_lux_free.py` proves a package does not REQUIRE Lux. That is the wrong
half of the promise. `planner.py` says an unlit art package "still ships
validated fixtures and their `LuxEmit` markers, which is a contract another
lighting system can read", and `--art --unlit` is documented as being "for a
team bringing its own". Nothing checks that the contract is actually there,
typed, whole, and in a frame the reader is told about. This does.

WHAT IT IS NOT. It does not open Godot, it does not look at the GLBs, and it
says nothing about whether the lighting is any GOOD. It reads one manifest and
reports what a consumer would find in it. The marker half of the contract --
`LuxEmit_*` empties inside the fixture GLBs -- is `lux_fixture_gate`'s job and
is not re-checked here.

## The schema, read from the producers rather than guessed

Two producers, and they do not agree on the envelope:

  * `deli_counter/lights.py` builds the PER-BUILDING manifest and stamps
    `LIGHT_MANIFEST_VERSION`, currently "1.1.0".
  * `lot.merge_lights` composes those into the SITE manifest and stamps a
    HARDCODED "1.0.0", never reading the version of the files it merges. So a
    site manifest can carry 1.1.0 anchors under a 1.0.0 envelope. That is why
    the version check below warns rather than trusts, and why `drop` is
    counted directly instead of being inferred from the version.

Envelope: light_manifest_version, site (or building_id), space, rig_library,
anchors. Anchor, always: id, type, source, pos, rot_y, reacts_to_alarm --
plus `building` on a site manifest (null for the ones Lot owns outdoors).
Anchor, by type: row{count,spacing} on rows, size[w,h] on window/sign, wall on
wall-mounted, room on interior, drop on ceiling-hung.

A ROW IS NOT A LAMP. 75 anchor records on the rockay build are 225 lights,
because a `row` carries count and spacing and `LuxLightLoader._rig_for` passes
both to the rig. Counting records and calling them lights understates the real
number by 3x here. Both figures are reported; neither is called "the" count.

An unrecognised type, a missing required key, a duplicate id or an unknown
frame string is a FAIL, not a warning: a consumer that cannot name what it is
holding has learned nothing and must say so.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

#: Types `LuxLightLoader._rig_for` knows how to build a rig for. `sun` is in
#: the loader's docstring as "handled by the preset" -- it is a legal anchor
#: type that yields no rig, so it is known-but-rigless rather than unknown.
KNOWN_TYPES = {
    "fluorescent", "pendant", "streetlight", "wall_pack", "window", "sign",
}
RIGLESS_TYPES = {"sun"}

#: Types whose omni RANGE is derived from `drop` (deli_counter >= 0.97).
#: Without it `_rig_for` falls back to a flat 4.0 -- the value its own comment
#: records as leaving "a lit ceiling over a PITCH-BLACK floor" in a 5.7 m hall.
DROP_DERIVED = {"fluorescent", "pendant"}

REQUIRED_ANCHOR_KEYS = {"id", "type", "source", "pos", "rot_y", "reacts_to_alarm"}

#: The frame both producers stamp. Compared by PREFIX because Deli Counter's
#: string carries an extra clause about ceiling rows that Lot's does not.
FRAME_PREFIX = "Blender Z-up, meters"

KNOWN_VERSIONS = {"1.0.0", "1.1.0"}


class Report:
    def __init__(self) -> None:
        self.fails: list[str] = []
        self.notes: list[str] = []
        self.facts: dict = {}

    def fail(self, msg: str) -> None:
        self.fails.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)


def probe(path: Path, rep: Report) -> None:
    # READ BYTES, NOT TEXT. These files are CRLF and `read_text` decodes with
    # universal newlines, so `len(text.encode())` is short by exactly one byte
    # per line -- 23,522 against 24,800 on the rockay site manifest, which is
    # precisely its 1,278 CRLFs. CLAUDE.md records the same trap costing a
    # grounding check its meaning. The size a consumer sees is the size on
    # disk.
    try:
        raw = path.read_bytes()
    except OSError as exc:
        rep.fail(f"unreadable: {exc}")
        return
    try:
        doc = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        rep.fail(f"not UTF-8: {exc}")
        return
    except json.JSONDecodeError as exc:
        rep.fail(f"not JSON: {exc}")
        return
    if not isinstance(doc, dict):
        rep.fail(f"top level is {type(doc).__name__}, expected an object")
        return

    rep.facts["bytes_on_disk"] = len(raw)
    rep.facts["line_endings"] = "CRLF" if b"\r\n" in raw else "LF"

    version = doc.get("light_manifest_version")
    rep.facts["light_manifest_version"] = version
    if version is None:
        rep.fail("no `light_manifest_version` -- this is not a light manifest")
    elif version not in KNOWN_VERSIONS:
        rep.fail(f"unknown manifest version {version!r}; known: "
                 f"{', '.join(sorted(KNOWN_VERSIONS))}")

    scope = doc.get("site") or doc.get("building_id")
    rep.facts["scope"] = scope
    rep.facts["scope_kind"] = "site" if "site" in doc else (
        "building" if "building_id" in doc else None)
    if scope is None:
        rep.fail("no `site` and no `building_id` -- the manifest names no subject")

    space = doc.get("space")
    rep.facts["space"] = space
    if not isinstance(space, str) or not space.startswith(FRAME_PREFIX):
        rep.fail(f"frame string is {space!r}; expected one starting "
                 f"{FRAME_PREFIX!r}. A consumer that guesses the frame puts "
                 f"every light in the wrong place.")

    rep.facts["rig_library"] = doc.get("rig_library")

    anchors = doc.get("anchors")
    if not isinstance(anchors, list):
        rep.fail(f"`anchors` is {type(anchors).__name__}, expected a list")
        return
    if not anchors:
        rep.fail("`anchors` is empty -- nothing to light with")
        return

    rep.facts["anchor_records"] = len(anchors)

    seen_ids: dict[str, int] = {}
    per_type_records: dict[str, int] = {}
    per_type_lights: dict[str, int] = {}
    total_lights = 0
    drop_have = 0
    drop_want = 0
    extra_keys: set[str] = set()
    z_lo, z_hi = math.inf, -math.inf

    for i, a in enumerate(anchors):
        where = f"anchors[{i}]"
        if not isinstance(a, dict):
            rep.fail(f"{where} is {type(a).__name__}, expected an object")
            continue

        missing = REQUIRED_ANCHOR_KEYS - set(a)
        if missing:
            rep.fail(f"{where} id={a.get('id')!r} missing "
                     f"{', '.join(sorted(missing))}")

        aid = a.get("id")
        if isinstance(aid, str):
            if aid in seen_ids:
                rep.fail(f"duplicate id {aid!r} at {where} and "
                         f"anchors[{seen_ids[aid]}] -- ids are how authored "
                         f"overrides bind, so a duplicate silently loses one")
            else:
                seen_ids[aid] = i

        t = a.get("type")
        if not isinstance(t, str) or (t not in KNOWN_TYPES
                                      and t not in RIGLESS_TYPES):
            rep.fail(f"{where} id={aid!r} has unrecognised type {t!r}; "
                     f"known: {', '.join(sorted(KNOWN_TYPES | RIGLESS_TYPES))}")
            t = str(t)

        row = a.get("row")
        n = 1
        if isinstance(row, dict):
            try:
                n = int(row.get("count", 1))
            except (TypeError, ValueError):
                rep.fail(f"{where} id={aid!r} row.count is "
                         f"{row.get('count')!r}, not a number")
                n = 1
            if n < 1:
                rep.fail(f"{where} id={aid!r} row.count is {n}")
                n = 1
            if not isinstance(row.get("spacing"), (int, float)):
                rep.fail(f"{where} id={aid!r} has row.count without a "
                         f"numeric row.spacing")

        per_type_records[t] = per_type_records.get(t, 0) + 1
        per_type_lights[t] = per_type_lights.get(t, 0) + n
        total_lights += n

        if t in DROP_DERIVED:
            drop_want += 1
            if isinstance(a.get("drop"), (int, float)):
                drop_have += 1

        pos = a.get("pos")
        if (not isinstance(pos, list) or len(pos) != 3
                or not all(isinstance(v, (int, float)) and math.isfinite(v)
                           for v in pos)):
            rep.fail(f"{where} id={aid!r} pos is {pos!r}, expected three "
                     f"finite numbers")
        else:
            z_lo, z_hi = min(z_lo, pos[2]), max(z_hi, pos[2])

        if not isinstance(a.get("reacts_to_alarm"), bool):
            rep.fail(f"{where} id={aid!r} reacts_to_alarm is "
                     f"{a.get('reacts_to_alarm')!r}, expected a boolean")

        extra_keys |= set(a) - REQUIRED_ANCHOR_KEYS - {
            "row", "size", "wall", "room", "drop", "building"}

    rep.facts["lights_after_row_expansion"] = total_lights
    rep.facts["per_type_records"] = dict(sorted(per_type_records.items()))
    rep.facts["per_type_lights"] = dict(sorted(per_type_lights.items()))
    rep.facts["up_axis_min_max"] = [z_lo, z_hi] if anchors else None
    rep.facts["drop_coverage"] = f"{drop_have}/{drop_want}"

    if drop_want and drop_have < drop_want:
        rep.note(
            f"{drop_want - drop_have} of {drop_want} ceiling-hung anchor(s) "
            f"carry no `drop`. Lux derives the omni range from it and falls "
            f"back to a flat 4.0 without it. Deli Counter stamps `drop` from "
            f"0.97; a manifest missing it was built before that.")
    if extra_keys:
        rep.note(f"anchor keys this probe does not model: "
                 f"{', '.join(sorted(extra_keys))}")
    if doc.get("light_manifest_version") == "1.0.0" and drop_have:
        rep.note("envelope says 1.0.0 and the anchors carry `drop` (a 1.1.0 "
                 "field). `lot.merge_lights` hardcodes the site envelope "
                 "version and does not propagate the building one.")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("manifest", help="a *.lights.json (site or building)")
    ap.add_argument("--json", action="store_true", help="machine-readable")
    args = ap.parse_args(argv)

    rep = Report()
    probe(Path(args.manifest), rep)

    if args.json:
        print(json.dumps({"ok": not rep.fails, "facts": rep.facts,
                          "fails": rep.fails, "notes": rep.notes}, indent=2))
        return 0 if not rep.fails else 1

    print(f"  {args.manifest}")
    for k, v in rep.facts.items():
        print(f"    {k:28s} {v}")
    for n in rep.notes:
        print(f"\n  NOTE  {n}")
    if rep.fails:
        print(f"\n  NOT LIGHTABLE -- {len(rep.fails)} problem(s):")
        for f in rep.fails:
            print(f"    - {f}")
        return 1
    print("\n  LIGHTABLE: envelope, frame, types, ids and geometry all read "
          "clean. This says the contract is present and well-formed. It does "
          "not say the lighting is good.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
