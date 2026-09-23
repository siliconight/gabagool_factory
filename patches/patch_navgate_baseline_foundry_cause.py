"""The foundry regression has a cause now, and it is 0.143.0.

WHAT THE EARLIER ENTRY SAID, and why it was wrong. It recorded the window as
2026-08-21..2026-09-23, named stair-guard work as suspected but "NOT
convicted", and said settling it needed a bisect over roughly fifteen commits.
It also carried forward a claim from a working summary that 0.143.0 had been
"proven unrelated three ways". That claim was false and this patch retracts it.

WHAT SETTLED IT, and it cost one command rather than a bisect.
`build/*.manifest.json` is TRACKED and carries `outputs_sha256_16`, a content
hash of the built glb:

    2026-09-16   pre-0.143.0   c600f22e9178d52e
    2026-09-23   0.143.0       8f2b4ae3a33c8567
    2026-09-23   rebuild       8f2b4ae3a33c8567   (unchanged)

So 0.143.0 moved this shell's geometry and nothing since has. Confirmed by
building the shell with `stairwell.py` from HEAD~1: the hash returned to
c600f22e9178d52e and both stairs gated `ok`; rebuilt at HEAD the hash returned
to 8f2b4ae3a33c8567 and stair_0 gated `no_path`. `stairwell.py` was restored
byte-for-byte (sha d36f19758dfed5be) after each swap.

THE MECHANISM, measured by sweeping the one quantity 0.143.0 introduced. For a
`switchback` the only effective line in that release's diff is `rail_span`
using `open_rail` in place of `open_`. Forcing `open_rail` to a constant and
rebuilding this shell at each value:

    1.0778  FAIL   glb 904eb5f9cdd2088d   polys 1675   (0.143.0's own value)
    1.2     FAIL   glb 5ff8dc1d9f688829   polys 1676
    1.25    FAIL   glb c72f878a29472f8e   polys 1676
    1.3     FAIL   glb f931dbf0d0ef6d7c   polys 1677
    1.35    FAIL   glb 81197e9930362090   polys 1677
    1.4     PASS   glb 631b6330d67b1159   polys 1681
    1.6     PASS   glb ace12dda7007ee1c   polys 1686
    1.8     PASS   glb beb6b62524e41cb6   polys 1684
    2.05    PASS   glb c600f22e9178d52e   polys 1687   (the pre-0.143.0 value)

Six to nine distinct hashes, monotone, and the 2.05 control reproduces the
pre-0.143.0 glb EXACTLY -- so the knob reached the geometry and the instrument
can see a difference.

THE PREMISE IS UNSATISFIABLE HERE, which is the real finding. 0.143.0 clips the
rail's opening to the solid plate beneath it, `step_d + WALKOFF_CLEAR` =
0.2778 + 0.8 = 1.0778 m. The bake needs an opening between 1.35 and 1.40 m to
connect this landing. The opening must therefore be about 0.3 m WIDER than the
floor under it, and no value of the clip satisfies both "opening <= floor" and
"connected". The fix is to size the FLOOR to the opening rather than the
opening to the floor -- it is not a bigger clip.

TWO CANDIDATE THRESHOLDS REFUTED, so nobody re-derives them:
`agent_contract.min_corridor_width()` is 1.10 and `min_door_width()` is 1.25;
both gate FAIL. The threshold is not a contract constant and, until it is
derived from something, it is a number measured on one shell at one bake
setting (radius 0.40, cell 0.10, climb 0.15, slope 55).

WHY THIS SHELL AND NOT THE OTHER 132. Its basement landing sits in a corner
against the south wall, so the rail's opening is its ONLY way off. Elsewhere a
landing has floor on more than one side and survives a narrow opening. That
makes the defect a connectivity question rather than a width one, which is
worth knowing before a width is picked.

Anchored: the anchor must match exactly once or this refuses to write.
"""
import json
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "deli_counter" / \
    "navgate_baseline.json"

OLD_TAIL = (
    "OPEN: which commit. The window 2026-08-21..2026-09-23 is dominated by "
    "stair-guard work (0.126.0, 0.134.0, 0.138.0, 0.143.0) and guards are "
    "suspected but not convicted -- st.width 1.8 exceeds min_corridor_width "
    "1.1, so this flight takes the filled guard and its side pieces measure "
    "flush to the flight edges. Settling it needs a bisect over that window."
)

NEW_TAIL = (
    "CAUSE FOUND 2026-09-23: Deli Counter 0.143.0, and the earlier note here "
    "saying guards were 'not convicted' is retracted along with a working "
    "summary's claim that 0.143.0 had been proven unrelated three ways -- it "
    "had not. build/*.manifest.json is tracked and carries outputs_sha256_16: "
    "this shell's glb reads c600f22e9178d52e before 0.143.0 and "
    "8f2b4ae3a33c8567 at and since it, so 0.143.0 moved the geometry and "
    "nothing after it did. Confirmed by building with stairwell.py from "
    "HEAD~1 (hash returns to c600f22e9178d52e, both stairs ok) and at HEAD "
    "(hash 8f2b4ae3a33c8567, stair_0 no_path), restoring stairwell.py "
    "byte-for-byte each time. MECHANISM: 0.143.0 clips the rail's opening to "
    "the solid plate beneath it, step_d + WALKOFF_CLEAR = 0.2778 + 0.8 = "
    "1.0778 m. Sweeping that one quantity and rebuilding at each value gives "
    "FAIL at 1.0778, 1.2, 1.25, 1.3 and 1.35 and PASS at 1.4, 1.6, 1.8 and "
    "2.05, with nine distinct glb hashes and the 2.05 control reproducing the "
    "pre-0.143.0 glb exactly. So the bake needs an opening roughly 0.3 m WIDER "
    "than the floor under it, and 0.143.0's premise -- opening <= floor -- is "
    "unsatisfiable for this stair at any clip value. The fix is to size the "
    "floor to the opening, not the opening to the floor. Two candidate "
    "thresholds refuted: min_corridor_width 1.10 and min_door_width 1.25 both "
    "FAIL, so the number is not a contract constant and is so far measured on "
    "one shell at one bake setting (radius 0.40, cell 0.10, climb 0.15, slope "
    "55). WHY THIS SHELL AND NOT THE OTHER 132: its basement landing sits in a "
    "corner against the south wall, so the rail's opening is its only way off; "
    "elsewhere a landing has floor on more than one side and survives a narrow "
    "opening. That makes this a connectivity defect rather than a width one. "
    "STILL OPEN: the fix itself, which is a geometry change to a released tool "
    "and is PIPELINE_ROADMAP.md item 176."
)


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    hits = text.count(OLD_TAIL)
    if hits != 1:
        raise SystemExit(f"REFUSED: anchor matched {hits} times")
    text = text.replace(OLD_TAIL, NEW_TAIL)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    d = json.loads(out.decode("utf-8"))
    assert d["counts"]["stair_failures"] == len(d["stair_failures"])
    entry = [e for e in d["stair_failures"]
             if e["shell"] == "foundry_heist_vertical"]
    assert len(entry) == 1 and "0.143.0" in entry[0]["reason"], \
        "REFUSED: the cause did not land in the foundry entry"
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes "
          f"(+{len(out) - before}); cause recorded")


if __name__ == "__main__":
    main()
