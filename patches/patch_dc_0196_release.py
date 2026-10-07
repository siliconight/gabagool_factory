"""Deli Counter 0.196.0: VERSION and CHANGELOG for the nav gate's entrance check.

    python patch_dc_0196_release.py <suite line>

Anchored on VERSION and the CHANGELOG head as read 2026-10-06.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.196.0] - the nav gate asks whether an entrance reaches each stair

**Why.** A stair whose two ends join is a stair, not a route. deli_a01's
up-stair passed this gate in every build: both ends on one island, navigable
"yes". Meanwhile two crate stacks cut its foot off from the stairwell's
door, and its whole upper storey with it (cold runs 9187 and 9188; 0.195.0;
`docs/findings/deli_a01_upper_storey_9188/` at the factory root).

**The check** (`godot/addon/deli_counter/nav_gate.gd`).
- `_entry_points` takes each storey-0 exterior door and garage from
  gameplay.json and moves it `ENTRY_IN` = 1.0 m along its wall's inward
  normal. That is past the wall's erosion and inside the 1.5 m approach no
  seeded piece stands in.
- Each point is snapped with the marker rule (`MARKER_MAX_ABOVE`), so it
  never lands on furniture.
- Each stair reports `from_entry`: is either end on an island an entrance is
  on? It is null when no entrance snapped or an end is off the mesh.
- The result carries `entries` (points, snapped, `stairs_judged`,
  `stairs_unreached`), and `nav_gate.py`'s verdict prints "stairs an
  entrance reaches: k/n" and names each stair it does not.
- **Reported, not gated**, like `navigable`. The stair verdict and the exit
  code are unchanged.

**The control fails first.** On the shipped deli_a01 (cold run 9188's GLB
with its own gameplay file), both stairs read "ok" and navigable "yes",
as before, and the new line reads "stairs an entrance reaches: 1/2 -- no
entrance reaches stair deli_stair_up". On 0.195.0's deli_a01 it reads 2/2.

**The library** (`nav_gate.py --all`, after 0.195.0).
- 98 shells have judged stairs, 149 stairs in all, and 148 are reached from
  an entrance.
- **The one that is not is `primos_pizza_stair_0`**, basement to storey 1
  through the ground floor. Its ends join and all three entrances snap, but
  the ground floor cannot reach it. Roadmap 189 located that neck: its
  discharge plate stands against the north wall beside its breach panel.
- No shell with stairs went unjudged. 14 have no storey-0 exterior door: the
  12 Empties, shut by design, and the two facade shells, which have no stairs.

**Frozen** (`navgate_baseline.json`, `entry_unreached`): primos_pizza, with
that reason. `test_navgate_population` fails on a new stair no entrance
reaches, on a frozen one an entrance now reaches, and on a result from
before this check.

**Tests:**
- `test_navgate_entries.py`, 4. All four failed with the gate patch stashed.
- `test_navgate_population.py`, +4. With primos_pizza dropped from the
  frozen set, the no-new test fails and names it.

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.195.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.195.0] - a seeded piece leaves a body's width"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.196.0")
    print("Deli Counter 0.196.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
