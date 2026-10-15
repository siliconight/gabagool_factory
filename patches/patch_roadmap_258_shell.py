"""Roadmap 258, filed 2026-10-15: the mission's own shell is built three times a run and ships as a dead asset.
Appends the item (status directly above its heading) at the end of the roadmap; asserts the last item is 257.
The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_258_shell.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS = (
    "*STATUS: OPEN 2026-10-15 -- MEASURED ON COLD RUN 9316, NOT DECIDED. Three Blender builds of the mission's own "
    "shell, 1.7 min each, 5.1 of the run's 8.0 min; the shell composed and gated as the first `presentation_compose` "
    "arm with 0/0 modules; its GLB in the package twice, `assets/shell.glb` and `assets/lot.glb`, the same 552,532 "
    "bytes, referenced by no scene; its gameplay record staged for Dispatch only when the site has no markers of its "
    "own, which a Lot site always has. The decision it owes is design -- whether the brief's archetype should be the "
    "generated shell, placed, or the library family it anchors today -- and is not made here.*"
)

BODY = """**258. The mission's own shell is built three times a run and ships as a dead asset.** Found 2026-10-15,
sizing roadmap 170's bulkhead: the status written that morning said every level made this week had a stair head
open to the sky, because the nine `lf_<mission>_<seed>` specs with such a stair are the mission's own shells.
Read against cold run 9316's package, no file in it carries the generated shell's hatch, and the retraction led
here (`docs/findings/roof_openings_170/README.md`, "Step 2").

**What the generated shell is, and where it goes.** `deli_generate` builds the brief's archetype preset through
Blender once per candidate -- `lf_precinct_yard_001_{9001,9102,9203}` on 9316, 1.7 min each, 5.1 of the run's
8.0 min from batch to DONE -- and `lot_assemble` depends on it. With a `lot_library` set, which every cold-run
brief sets, Lot stands the library's buildings (`building_library.lot_for_brief`, anchored on the brief's
archetype FAMILY: courthouse_a02, clinic_a01, convenience_store_a01, airport_terminal_a01 on 9316's seed_9203)
and stages only those (`stage_site_packages.py`'s `[stage] glb` lines). The shell itself then:

- is composed and gated as the first `presentation_compose` arm -- "placement gate [OK]: 0/0 modules sit on the
  greybox collision", 131 solids, and the hatch excusal's "1 excused" fired on it before it fired on any building
  that ships;
- is bundled by `exporting/localize.py` into the package as `assets/shell.glb`, and again as `assets/lot.glb`
  (Dispatch's "passthrough of the DC shell"), the same 552,532 bytes as seed_9203's `shell.glb`, with
  `mission.tscn`, `site.tscn` and `handoff_bindings.json` referencing neither;
- has its gameplay record read by `staging/dispatch_inputs.py` only when the site has no markers of its own
  (the 9191 duplication that rule was written against), which a Lot site never lacks -- so its anchors,
  interactives and ladders reach Dispatch on no cold run;
- leaves its spec behind: `deli_counter/specs/` holds 287 `lf_*` files written by runs (items 70 and 73 made
  that a design), which `tests/test_audit_specs.py` and `build_freshness` walk.

**The single-shell path is why it exists.** A brief with no `lot_library` IS this shell: one unnamed building,
`shell.patina.*` outputs, placed as the level. The planner says so ("AN EMPTY LOT IS THE SINGLE-SHELL PATH") and
keeps every mission that does not set the library byte-for-byte. With a library, the shell is the path's
residue: planned, built, gated, bundled, and read by nothing a package carries.

**Two readings, and the item does not choose.** (1) The shell is waste on the library path: plan it once or not
at all when a library stands, stage Dispatch's file-check placeholder (`dispatch_inputs` already writes a
"valid-enough" one when no GLB is given), drop the compose arm and the two assets -- about 5 minutes and 1.1 MB a
run, and the cold-run clock (239) moves by it. (2) The shell is the mission's building that the library path
forgot: the brief asks for a `police_station` and gets a courthouse family; placing the generated shell as the
anchored building would make the brief's archetype real and give the bulkhead and the hatch their nine mission
buildings back. The second changes what a level IS and is the walker's; the first is Level Factory's and cheap.

**WHAT WOULD CLOSE THIS.** The decision, then its build: either the library path stops building what it does not
ship (a planner change, proven by a cold run whose package matches today's and whose clock is shorter), or the
generated shell is placed (a Lot and Level Factory change, a design the walker reads first). Either way the
package stops carrying an asset nothing references, which `export_closure` could refuse.
"""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "\n**258. " not in text, "258 already filed"
    assert text.rfind("\n**257. ") > text.rfind("\n*STATUS:"), "257 is not the last item, or a status follows it"
    out = text.rstrip("\n") + "\n\n" + STATUS + "\n\n" + BODY.rstrip("\n") + "\n"
    assert out.count("\n**258. ") == 1
    RM.write_bytes(out.encode("utf-8"))
    print("roadmap 258 filed; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
