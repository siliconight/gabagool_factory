r"""The mission tag only exists when the anchor does not. Ensure the TAG.

    python patch_lf_mission_anchor_tags.py --check
    python patch_lf_mission_anchor_tags.py
    python patch_lf_mission_anchor_tags.py --revert
    python patch_lf_mission_anchor_tags.py --selftest

Run from the FACTORY ROOT (the directory holding `level_factory/`).

THE DEFECT, and it is the good kind: correct data produces a worse result than
missing data.

`ensure_mission_anchors` guarantees a `player_start` and an `extraction` exist
so the mission flow has something to bind to. Both synthesized anchors carry a
TAG -- `["mission_start"]`, `["extraction"]` -- and the tag is what
`mission_flow`'s `location_tag` binds against:

    {"step": "spawn",   "location_tag": "mission_start"}
    {"step": "extract", "location_tag": "extraction"}

But each branch is guarded on the TYPE being absent. So the tag arrives only
when Lot supplied nothing. Measured on lot_demo_001, 135 anchors:

    player_start   Lot emits none  -> synthesized, tags ["mission_start"]
                                      -> beat `spawn` binds
    extraction     Lot emits FIVE  -> branch skipped, no tag anywhere
                                      -> beat `extract` binds to nothing

    BLOCKER [assembly] Proposed beat 'extract' binds to no anchor and has
    no trigger.

Five real extraction points -- `BAY`, `CENTER_FIELD_TRUCK`, `DRIVE`, `LOT`,
`LOT_11`, every one `"tags": []` -- and the mission fails to assemble because
they exist. Delete them and it would pass. Dispatch exits 1, and
`lot_demo_001.dispatch_handoff` has been the run's only blocker.

THE FIX. Ensure what the binder actually reads. In order:

  1. an anchor already carries the tag -> nothing to do
  2. anchors of that type exist -> tag them, because they ARE the thing the
     beat is asking for
  3. neither -> synthesize at the centroid, exactly as before

ALL of them, not the first. `shell_ids` on a beat is a list; a location beat
naming `extraction` means the extraction points, and picking one would be
inventing a preference nobody expressed. Five tagged anchors say "the level has
five of these"; one says "this one is special", which is a claim about the
mission that this function has no business making. Its own docstring is the
rule: "without inventing a mission."
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("level_factory/packages/staging/dispatch_inputs.py")
SIDECAR = ".pre_anchortags"


OLD = '''def ensure_mission_anchors(anchors: list, source: str, up: str = "z") -> list:
    """Guarantee a player_start and an extraction exist so spawn/extraction
    checks have something to bind to, without inventing a mission. Placed at the
    centroid / first anchor when absent."""
    types = {a["type"] for a in anchors}
    if anchors:
        cx = sum(a["pos"][0] for a in anchors) / len(anchors)
        cy = sum(a["pos"][1] for a in anchors) / len(anchors)
    else:
        cx = cy = 0.0
    if "player_start" not in types:
        anchors.insert(0, {"id": f"{source}:mission_start", "type": "player_start",
                           "pos": [cx, cy, 0.0], "tags": ["mission_start"]})
    if "extraction" not in types:
        anchors.append({"id": f"{source}:extraction", "type": "extraction",
                        "pos": [cx, cy, 0.0], "tags": ["extraction"]})
    return anchors'''


NEW = '''#: anchor type -> the `mission_flow` location_tag that binds to it.
#: `location_tag` matches an anchor's TAGS, never its type, so a type with no
#: tagged instance is invisible to the mission flow no matter how many of them
#: the level contains.
_MISSION_TAG = {"player_start": "mission_start", "extraction": "extraction"}


def ensure_mission_anchors(anchors: list, source: str, up: str = "z") -> list:
    """Guarantee the spawn and extraction TAGS exist, so the mission flow has
    something to bind to -- without inventing a mission.

    Ensuring the tag rather than the type, because the tag is what binds.
    `mission_flow` asks for `location_tag: "extraction"` and the binder reads
    `tags`; an anchor merely TYPED extraction is invisible to it.

    That distinction was the whole defect, and it made correct data worse than
    missing data. Both branches used to be guarded on the type being absent, so
    the tag arrived only when the level had nothing. Measured on lot_demo_001,
    135 anchors: Lot emits no `player_start`, so one was synthesized WITH its
    tag and `spawn` bound; Lot emits five real `extraction` anchors -- BAY,
    CENTER_FIELD_TRUCK, DRIVE, LOT, LOT_11, all `"tags": []` -- so the branch
    was skipped, nothing carried the tag, and Dispatch refused the mission:
    "BLOCKER [assembly] Proposed beat 'extract' binds to no anchor and has no
    trigger." Deleting the five would have made it pass.

    Order: already tagged -> leave it; typed but untagged -> tag them, they ARE
    what the beat asks for; neither -> synthesize at the centroid as before.

    ALL matching anchors get the tag, not the first. `shell_ids` on a beat is a
    list. Tagging one would say "this extraction point is the mission's", which
    is a claim about the mission, and this function's contract is not to make
    those.
    """
    if anchors:
        cx = sum(a["pos"][0] for a in anchors) / len(anchors)
        cy = sum(a["pos"][1] for a in anchors) / len(anchors)
    else:
        cx = cy = 0.0

    for atype, tag in _MISSION_TAG.items():
        tagged = [a for a in anchors if tag in (a.get("tags") or ())]
        if tagged:
            continue
        typed = [a for a in anchors if a.get("type") == atype]
        if typed:
            for a in typed:
                a["tags"] = list(a.get("tags") or ()) + [tag]
            continue
        made = {"id": f"{source}:{tag}", "type": atype,
                "pos": [cx, cy, 0.0], "tags": [tag]}
        if atype == "player_start":
            anchors.insert(0, made)
        else:
            anchors.append(made)
    return anchors'''


EDITS = {TARGET: ((OLD, NEW),)}

_CRLF = "\\r\\n"


def _selftest() -> int:
    """Run the patched function against the three cases that matter.

    Case 2 is the one lot_demo_001 hit, and the one the old code got wrong.
    """
    import importlib.util
    path = Path.cwd() / TARGET
    spec = importlib.util.spec_from_file_location("dispatch_inputs", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_inputs"] = mod
    spec.loader.exec_module(mod)
    f = mod.ensure_mission_anchors

    bad = 0

    # 1. nothing supplied -> both synthesized, both tagged
    out = f([], "lot")
    got = sorted(t for a in out for t in a.get("tags", ()))
    ok = got == ["extraction", "mission_start"] and len(out) == 2
    bad += not ok
    print(f"  [{'ok  ' if ok else 'FAIL'}] empty input -> {len(out)} anchors, tags {got}")

    # 2. THE lot_demo_001 CASE: five typed, untagged extractions, no player_start
    five = [{"id": f"lot:{n}", "type": "extraction", "pos": [0.0, 0.0, 0.0],
             "tags": []} for n in ("BAY", "DRIVE", "LOT", "LOT_11", "TRUCK")]
    out = f(list(five), "lot")
    extr = [a for a in out if "extraction" in (a.get("tags") or ())]
    start = [a for a in out if "mission_start" in (a.get("tags") or ())]
    ok = len(extr) == 5 and len(start) == 1 and len(out) == 6
    bad += not ok
    print(f"  [{'ok  ' if ok else 'FAIL'}] five typed extractions -> "
          f"{len(extr)} tagged extraction, {len(start)} tagged start, "
          f"{len(out)} total (no synthetic extraction added)")

    # 3. already tagged -> untouched, nothing duplicated
    pre = [{"id": "lot:x", "type": "extraction", "pos": [1.0, 2.0, 0.0],
            "tags": ["extraction", "keep_me"]},
           {"id": "lot:s", "type": "player_start", "pos": [0.0, 0.0, 0.0],
            "tags": ["mission_start"]}]
    out = f(list(pre), "lot")
    ok = len(out) == 2 and out[0]["tags"] == ["extraction", "keep_me"]
    bad += not ok
    print(f"  [{'ok  ' if ok else 'FAIL'}] already tagged -> {len(out)} anchors, "
          f"tags preserved {out[0]['tags']}")

    print("  selftest FAILED" if bad else "  selftest passed")
    return 1 if bad else 0


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count("\r\n")
    lf = body.count("\n") - crlf
    return "\r\n" if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace("\r\n", "\n").replace("\n", eol)


def _find(body: str, anchor: str):
    candidate = _as(anchor, _eol(body))
    return candidate, body.count(candidate)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)
    eol = _eol(body)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0][:70]!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count("\r\n")
    if eol == "\r\n" and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    try:
        compile(out, str(path), "exec")
    except SyntaxError as exc:
        print(f"REFUSING: {path.name} -- the patched file does not parse: {exc}")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--selftest" in argv:
        return _selftest()

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    if not check:
        print("  next: python patch_lf_mission_anchor_tags.py --selftest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
