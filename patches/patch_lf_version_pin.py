"""Repair a version pin this session's earlier patch invalidated.

Run from the factory root:

    python patch_lf_version_pin.py --check
    python patch_lf_version_pin.py

WHAT HAPPENED. `patch_lf_walkable_site.py` bumped `LotAdapter.adapter_version`
0.3.0 -> 0.4.0. The bump is correct and load-bearing: the site's OUTPUT LAYOUT
changed (buildings staged under `lot/<id>/`, every ext_resource relative), so a
cache entry written under the old rules is a site whose refs resolve nowhere
and must be retired rather than served.

`tests/unit/test_scene_payload.py::test_both_adapters_use_the_one_rule` pins
both adapter versions as a record that a specific fix was bumped into effect.
The bump invalidated the pin. I did not notice because I ran only the tests I
had just written, and not the suite -- which is the whole reason the suite
exists, and the same shape as running a gate that was never wired up.

WHAT THIS CHANGES. The pinned value, and nothing else. The test's real subject
is the first two assertions -- that Lot and Lux resolve the same
`scene_payload_hashes` object rather than two copies that can drift -- and
those are untouched.

A NOTE ON THE PIN ITSELF, not acted on here. An exact-equality pin fails on
every legitimate future bump, which means the next person to bump either
adapter gets a red suite that says nothing about what they broke. That is a
real cost and a real trade: it also guarantees a bump is never invisible.
Changing it is a decision about how this repo wants to spend its attention,
not something a patch about a walkable site should quietly decide.
"""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path("level_factory/tests/unit/test_scene_payload.py")

BEFORE = '''    # and the bump that makes the fix take effect
    assert LuxAdapter.adapter_version == "0.4.0"
    assert LotAdapter.adapter_version == "0.3.0"
'''

AFTER = '''    # and the bump that makes the fix take effect
    assert LuxAdapter.adapter_version == "0.4.0"
    # Lot 0.3.0 -> 0.4.0: the site's OUTPUT LAYOUT changed (buildings staged
    # under lot/<id>/, every ext_resource relative instead of res://C:/...), so
    # entries cached under the old rules had to retire rather than be served
    # alongside the new ones. See docs/WALKABLE_SITE.md.
    assert LotAdapter.adapter_version == "0.4.0"
'''


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    if not TARGET.is_file():
        print(f"[patch] {TARGET} not found -- run from the factory root")
        return 1

    raw = TARGET.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    print(f"[patch] {TARGET}: {len(raw)} bytes, "
          f"endings={'CRLF' if crlf else 'LF'}")

    if AFTER in text:
        print("[patch]   ALREADY APPLIED")
        return 0
    if BEFORE not in text:
        print("[patch]   ANCHOR NOT FOUND -- the pin has moved or been "
              "changed by hand. Read the test and re-author; do not force.")
        return 1
    if text.count(BEFORE) != 1:
        print(f"[patch]   ANCHOR NOT UNIQUE ({text.count(BEFORE)}x)")
        return 1

    text = text.replace(BEFORE, AFTER)
    print("[patch]   applied: lot adapter version pin 0.3.0 -> 0.4.0")

    if check_only:
        print("[patch] --check: no write")
        return 0

    payload = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
    TARGET.write_bytes(payload)
    print(f"[patch] wrote {TARGET}: {len(raw)} -> {len(payload)} bytes "
          f"({len(payload) - len(raw):+d})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
