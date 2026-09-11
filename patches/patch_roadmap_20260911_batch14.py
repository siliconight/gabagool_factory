"""Roadmap batch 14, 2026-09-11: close 96, file 137.

STATUS replaces a block and keeps the old one verbatim inside the new (batch
5's mechanism); APPEND adds a new item at the end of the file (batch 6's).
Each asserts its anchor and refuses on a miss.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    96: """*STATUS: CLOSED 2026-09-11 -- DECIDED (WINDOW AREA LIGHTS), WIRED, MEASURED,
AND THE FIRST CALL OF THE PATH FOUND A DEFECT NOBODY COULD HAVE SEEN BEFORE.
Lux 0.30.0 adds `LuxLightLoader.bake_daylight(path, scene_root)`: only the
anchors with no hardware and no marker (`window`) under a `LuxDaylight`
container beside the spawner's `LuxFixtureLights`, through the same
`_rig_for` table (the shadowed area rig of item 60's first tier), returning
`count` and `in_manifest` separately. Level Factory 0.70.0's driver takes
`--lights <site.site.lights.json>` and calls it after the fixture spawn,
re-owning the container so `pack()` keeps it; `lux.quality.json` reports
`daylight_lights` / `daylight_anchors_in_manifest`; `LUX_NO_DAYLIGHT` fires
when the manifest asked and nothing was made. THE SECOND FACE IS FINISHED
TOO: the adapter passes `lights_json`, the key `fingerprint_inputs` had hashed
since it was written and the command had never taken; the spec builder points
it at the assembly job's merged manifest. RUN ON cold-9005-ws: 18 window
anchors of 35, 18 lights, 0 issues; export closure ok; `mesh_light_census`
counts 18 under `Site/LuxDaylight` beside 39 fixtures. THE DEFECT: every
baked window panel stood PERPENDICULAR to its wall -- `_place` mapped Deli
Counter's rot_y ("0 == +X") straight onto `rotation.y`, right for a rig that
lays lamps along local +X (the fluorescent row) and a quarter turn wrong for
one that faces local +Z (the area rig's quad). Seen as white quads sticking
out of the west facade in the S elevation, derived (f = t + 90 under the axis
swap), fixed in Lux 0.30.1, re-rendered flat. The omni beneath the panel is
orientation-free and was never wrong. THE COST THE ITEM PREDICTED, NOW A
NUMBER: the same package with `LuxDaylight` stripped has 2 meshes over the
per-mesh light budget of 8 (worst 9); with it, 12 (worst 12), every one an
east-ward ceiling or floor plate -- filed as item 137, because it is item 54's
budget law and not this item's wiring. SEEN, NOT TOUCHED: Zoo writes its
`LuxEmit_*` markers with a translation only, so a sign rig spawned on the
marker path inherits an identity basis and its quad faces +Z whatever the
wall; the sign's own hardware carries the visible face, which is why nobody
has noticed. Item 55's territory.*""",
}

APPEND = """
*STATUS: OPEN 2026-09-11 -- MEASURED ON THE RUN THAT CREATED IT, NOT TUNED.
ITEM 54'S BUDGET LAW MEETS ITEM 96'S DECISION*

**137. The window lights push ten interior plates over the per-mesh light
budget.** Found 2026-09-11, the first time a built level lit its windows
(item 96). `tools/mesh_light_census.py` over cold run 9005's export,
`county_hospital_001`, Blue Hour, GL Compatibility's default of 8 positional
lights per mesh:

    package                          lights   meshes over 8   worst
    LuxDaylight stripped (before)        39               2       9
    as exported (after)                  57              12      12

Every one of the ten is an east-ward ceiling or floor plate
(`ceiling_ground_east_ward/Ceiling_Panel_t1_*`, `floor_ward_east_1/*`,
`ceiling_ward_east_1/*`) and the census names the daylight rigs among the
claimants -- `LuxDaylight/b0_ext_1_N_window_2/AreaPanel_Omni` at margin 4.50,
range 6.4.

**WHY, and it is two facts that were each fine alone.** Under Compatibility
`LuxAreaLightRig` approximates the panel with an OmniLight3D whose range is
`max(panel_size) * 4` -- 6.4 m for a 1.6 m window, 9.6 m for a 2.4 m one --
and the anchor sits ON the building envelope (item 85 measured the windows at
-0.150 m, the wall centreline, by design). So half of every window's sphere
is inside the building, and a 6-10 m sphere from the wall reaches two rooms
of plates. The fluorescent rows already paid this law once: item 54 trimmed
their range to 4.0 and their density to one lamp per 4 m for exactly these
tiles.

**WHAT WOULD CLOSE THIS.** Derive the window omni's range from what a
window lights rather than from the panel's size -- a wash a few metres into
the room, not a sphere -- or give the daylight rigs the item 60 treatment
(shadows) so the wall occludes the half that faces out; then re-run the census
and land on 2. Neither is done here because the number was 12 and not 120:
the level ships, and a tuning made without looking at the room it changes is
the kind item 54 warned against.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    lines = raw.decode("utf-8").split("\n")
    for num, block in STATUS.items():
        heading = re.compile(r"^\*\*%d\. " % num)
        hits = [i for i, l in enumerate(lines) if heading.match(l)]
        if len(hits) != 1:
            print(f"item {num}: heading matched {len(hits)} times", file=sys.stderr)
            return 1
        h = hits[0]
        if h < 3 or lines[h - 1].strip() != "":
            print(f"item {num}: no blank line above heading", file=sys.stderr)
            return 1
        e = h - 1
        while e > 0 and lines[e].strip() == "":
            e -= 1
        blanks = h - 1 - e
        if not lines[e].rstrip().endswith("*"):
            print(f"item {num}: line above the blank does not close a status "
                  f"block: {lines[e][:60]!r}", file=sys.stderr)
            return 1
        s = None
        for i in range(e, max(-1, e - 40), -1):
            if lines[i].startswith("*STATUS:"):
                s = i
                break
        if s is None:
            print(f"item {num}: no *STATUS: within 40 lines", file=sys.stderr)
            return 1
        old = "\n".join(lines[s:e + 1]).strip()
        if not (old.startswith("*STATUS: ") and old.endswith("*")):
            print(f"item {num}: old block is not a *STATUS: ...* block", file=sys.stderr)
            return 1
        old_body = old[len("*STATUS: "):-1].rstrip()
        merged = block[:-1] + "\nEARLIER STATUS, KEPT VERBATIM: " + old_body + "*"
        lines[s:e + 1 + blanks] = merged.split("\n") + [""]
    if any(l.startswith("**137. ") for l in lines):
        print("item 137 already present", file=sys.stderr)
        return 1
    if not any(l.startswith("**136. ") for l in lines):
        print("item 136 not found; refusing to append after it", file=sys.stderr)
        return 1
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines += [""] + APPEND.strip("\n").split("\n") + [""]
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); {len(STATUS)} replaced, 1 appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
