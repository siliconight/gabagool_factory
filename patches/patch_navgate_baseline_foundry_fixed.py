"""`foundry_heist_vertical` leaves the stair baseline: it is fixed, not known.

The baseline's own note says a fixed shell must be removed, and the reason is
`test_baseline_has_not_gone_stale`'s: an entry that no longer fails hides the
next shell that starts to. This one was in for eight hours.

It never belonged there in the ordinary sense. The other three entries are
shells that have never passed; this was a REGRESSION introduced by 0.143.0 and
recorded so the gate stayed live for the other 132 shells while it was found.
0.144.0 fixes it -- `stair_guards` lets a rail's opening hang past its plate by
up to one body radius -- and the shell gates `navigable: yes` with both stairs
`ok` at glb 4914523fd9cf46ab.

Everything worth keeping from the entry is now in stairwell.py beside the code
and in PIPELINE_ROADMAP.md item 176: the sweep, the two refuted hypotheses, the
refuted fix, and the fact that 1.4 is a one-shell threshold rather than a
library minimum.

Anchored on the whole entry, which must match exactly once.
"""
import json
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "deli_counter" / \
    "navgate_baseline.json"


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    before = len(data)
    d = json.loads(data.decode("utf-8"))
    entries = d["stair_failures"]
    keep = [e for e in entries if e["shell"] != "foundry_heist_vertical"]
    if len(keep) != len(entries) - 1:
        raise SystemExit(
            f"REFUSED: expected exactly one foundry entry, removed "
            f"{len(entries) - len(keep)}")
    if len(keep) != 3:
        raise SystemExit(f"REFUSED: {len(keep)} entries left, expected 3")
    d["stair_failures"] = keep
    d["counts"]["stair_failures"] = len(keep)
    out = (json.dumps(d, indent=2) + "\n").encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes; "
          f"stair_failures {len(keep)}")


if __name__ == "__main__":
    main()
