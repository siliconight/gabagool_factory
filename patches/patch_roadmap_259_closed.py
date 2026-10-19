"""Roadmap 259 CLOSED, 2026-10-19: the one module its narrowing left out by decision is out of the build -- Deli Counter
0.233.0.

The status line is replaced at its front, the NARROWED status kept after it verbatim; a paragraph goes after the
item's last body line, its BUILT paragraph, which is also the roadmap's last line. Anchored on both lines' sha256 and
the heading two lines below the status. The index is NOT touched here: run `python tools/roadmap_status.py --write`
then `--check` after it.

    python patches/patch_roadmap_259_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
STATUS_SHA = "88fc332364e0d9253f342c100e19200ba0f5c51e0717cf18311efcab80bd0bb7"
HEADING_PREFIX = "**259. Deli Counter's freshness gate watches 22 of the 54 modules a shell build reaches.**"
OLD_PREFIX = "*STATUS: NARROWED 2026-10-19 -- "
BODY_END_SHA = "cf827f517a2df5c3ad60dfb0ac30b95cb36c816f58da2498acca507824a98c9d"

NEW = ("*STATUS: CLOSED 2026-10-19 -- every module a shell build reads is watched or named read-only with why, and the "
       "one left out by decision no longer reaches a build. Deli Counter 0.233.0 (9be68b3b, "
       "`patches/patch_dc_lint_out_of_the_build.py`): `host_openings` moved verbatim to `partition_bounds.py`, watched "
       "since it was written, and layout_lint keeps `_host_openings` as an alias; stairwell asks it and "
       "`agent_contract.door_approach()`, the function `DOOR_APPROACH_M` was always computed from, and imports the lint "
       "nowhere. Read off the call sites (`docs/findings/build_freshness_259/call_sites.out.txt`), those two were the "
       "lint's only build-time readers: the evidence report writes a report, and furnish and stair_pitch read its "
       "findings when a spec is made, which the spec's own hash covers. `test_lint_out_of_the_build.py` (3; two fail "
       "on 0.232.0, `patches/dc_lint_out_of_the_build/`). Rebuilt with build.py --all: all 159 tracked build records changed their build time alone "
       "(`patches/dc_lint_out_of_the_build/build_time_only.py`, which reads each manifest's output "
       "digest too; on 0.231.0's rebuild it flags that commit's 57 moved records, the control). The suite: 1598 passed, 2 skipped, "
       "and the hook's checks all passed. So `layout_lint` stays out "
       "of `GEOMETRY_SOURCES` as a reader, and the call that kept it out by decision is retired. Earlier status kept: "
       "NARROWED 2026-10-19 -- ")

BODY = [
    "",
    "**CLOSED, 2026-10-19** (Deli Counter 0.233.0, 9be68b3b; `patches/patch_dc_lint_out_of_the_build.py` and "
    "`dc_lint_out_of_the_build/`). The residue the BUILT paragraph left -- stairwell reading `_host_openings` and "
    "`DOOR_APPROACH_M` from a lint the gate does not watch -- is moved, not watched: one function and one number, no "
    "geometry. `build_freshness.NOT_BAKED` says layout_lint is a reader again, and "
    "`test_gates_that_only_read_shells_are_not_watched` records its premise as true again. The first apply was "
    "refused by the patch's own guard, nothing written: a docstring line in stairwell still named "
    "`layout_lint.DOOR_APPROACH_M`, which the dry check had not reached; it names the contract's function now. "
    "Rebuilt, the 159 tracked build records changed their build time alone, and the checker that says so "
    "flags the 57 records 0.231.0's rebuild moved.",
]


def _sha(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def main():
    assert "@@" not in NEW and not any("@@" in b for b in BODY), "a marker is left in the text"
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if _sha(l) == STATUS_SHA]
    assert len(hits) == 1, f"item 259's status found {len(hits)} times"
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(HEADING_PREFIX), "the status no longer adjoins 259's heading"
    old = lines[i]
    assert old.startswith(OLD_PREFIX) and old.endswith("*")
    ends = [j for j, l in enumerate(lines) if _sha(l) == BODY_END_SHA]
    assert len(ends) == 1 and ends[0] > i, f"item 259's last body line found {len(ends)} times"
    j = ends[0]
    assert j == len(lines) - 2 and lines[-1] == "", "item 259's BUILT paragraph is no longer the roadmap's last line"
    for k in range(i + 3, j):
        assert not lines[k].startswith("*STATUS:"), "another status inside item 259 at line %d" % (k + 1)
    for block in BODY:
        assert not (block.startswith("**") and block[2:3].isdigit()), "a body line would parse as an item"
    lines[j + 1:j + 1] = BODY
    lines[i] = NEW + old[len(OLD_PREFIX):]
    assert lines[i].startswith("*STATUS: CLOSED 2026-10-19 -- every module") and lines[i].endswith("*")
    assert lines[-1] == ""
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 259 CLOSED (Deli Counter 0.233.0); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
