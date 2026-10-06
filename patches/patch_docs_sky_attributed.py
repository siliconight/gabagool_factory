"""The sky cost attributed -- and the two earlier claims about it retracted.

Anchored; refuses on any miss. Root repo only.
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
BUDGET = ROOT / "docs" / "DRAW_CALL_BUDGET.md"
SKY = ROOT / "docs" / "proposals" / "SKY_PROVIDER.md"


def edit(path, pairs, label):
    raw = path.read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s has mixed endings" % path)
    eol = "\r\n" if crlf else "\n"
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for i, (old, new) in enumerate(pairs):
        if t.count(old) != 1:
            raise SystemExit("REFUSED: %s anchor %d matched %d times"
                             % (label, i, t.count(old)))
        t = t.replace(old, new, 1)
    path.write_bytes((t.replace("\n", eol) if eol == "\r\n" else t).encode("utf-8"))
    print("[patch] %s: %d blocks" % (path.name, len(pairs)))


BUDGET_OLD = '''**And it is not the cube.** SkyMint's cloud block — five noise fetches, a
`pow`, and the lighting that follows — runs on every pixel whether or not
there are clouds: `cloud_density = 1.0` zeroes the *mask* after the fetches,
not before them. `docs/proposals/SKY_PROVIDER.md` §Cost claimed the reverse
and is corrected there. The cheap version is one `if` around that block
when density is 1.0, which would change `glow_occlusion` slightly (it reads
cloud `thickness` even with no clouds) and has not been priced. That is the
next measurement, not this one.
'''
BUDGET_NEW = '''**And it is not the shader — ATTRIBUTED on cold run 9091's package, twelve
copies later.** The paragraph that stood here said the cost was the cloud
block and the cheap version was one `if`. Measured, that `if` recovered
nothing, and neither did anything else in the shader. Same package, one
change per copy, same harness, median GPU delta over the stations whose
worst heading matched (reports in `docs/cold_runs/cold_9091/`):

| copy | what changed | Δ gpu ms |
|---|---|---:|
| cloud branch | `if (cloud_density < 1.0)` around the cloud work | −0.00 |
| cloud branch, hard | the same, `false` at compile time | −0.05 |
| + TIME = 0 | every `TIME` a constant | −0.00 |
| + no equirect | the `SKY_COORDS` path deleted | −0.07 |
| + minimal tail | sun block only after the fetch | −0.05 |
| QUALITY | `process_mode` REALTIME → QUALITY | +0.03 |
| QUALITY + write-on-change | and no uniform written after frame 1 (counted: 0 in 120) | −0.06 |
| mipmaps | mip chains on the cube faces | −0.08 |
| **V1** | a valid sky of ONLY the two cube fetches and the grade | −0.07 |
| **V2** | a valid sky of a FLAT COLOUR, no fetch at all | −0.05 |
| **V5** | V2 with `radiance_size` 128 → 32 | **−0.67** |
| **V4** | V2 with ambient Flat Color and `reflected_light_source` DISABLED | **−1.23** |
| sky off (9090) | Lux's ProceduralSkyMaterial instead of SkyMint | −1.39 |

A flat colour through a custom sky shader costs what the whole of SkyMint
costs. **The cost is not in the sky pass; it is the sky's radiance map —
rendered and filtered from the custom shader every frame on GL
Compatibility, and read back by every lit surface as ambient and
reflection.** Shrinking the map halves it; taking away its readers removes
it. `delco_night` leaves `ambient_mode` at its default, Sky, with
`room_probes_replace_ambient` putting the sky's contribution at 1.0 — so
every exterior surface's ambient IS a sample of this map, and every
material's specular reflects it.

**A retraction inside the attribution.** Two earlier copies read −1.24 ms:
a "minimal shader" and "minimal + sun", each built with an early `return`
in `sky()`. The harness swallows engine stderr; a windowed capture
(`tools/sky_look.gd`) printed `SHADER ERROR: Using 'return' in the 'sky'
processor function is incorrect`. Those shaders never compiled, Godot drew
no sky, and −1.24 was the cost of no sky — which is also why it matched
"sky off" so neatly. Every conclusion drawn from them for the hour in
between was discarded, and V1/V2 were built valid and compile-checked in
a window before being measured. Name what produced the artefact.

**What this leaves the walker to choose**, because each has a look attached:

- **Radiance 32** (V5): −0.67 ms. Ambient and reflections come from a 32²
  map of a black sky with stars, instead of 128². At night that is a blur
  of a blur. Cheapest to ship — one enum in `skymint.gd`.
- **Flat ambient, no sky reflections** (V4): −1.23 ms, the whole cost.
  Exterior ambient becomes the preset's `ambient_color` (0.16, 0.19, 0.30)
  at 0.55 rather than a sample of the sky; no material reflects the sky.
  That is a visible change to the night, in either direction, and the
  walker judges it at runtime.
- **Leave it**: 1.3 ms at 720p, scaling with pixels, on a card that has
  the headroom — and an open item for the GL Compatibility target.

`process_mode` QUALITY did not help, with the uniform writes proven off.
Either Compatibility re-renders the radiance every frame whatever the mode,
or something not counted still dirties the sky; the two are not separated,
and it is the next question if V5 is chosen.
'''

SKY_OLD = '''RETRACTED: "with clouds off ... the per-pixel cloud work (7 texture fetches)
is gone." It is not. Read the shader rather than the profile: the five noise
fetches, the `pow` and the cloud lighting run on every pixel, and
`cloud_density = 1.0` zeroes the resulting MASK, after the work. Clouds off
is a look, not a saving. The saving is one branch around that block, which
would move `glow_occlusion` slightly (it reads cloud thickness even at zero
coverage) and is unpriced.
'''
SKY_NEW = '''RETRACTED: "with clouds off ... the per-pixel cloud work (7 texture fetches)
is gone." It is not. Read the shader rather than the profile: the five noise
fetches, the `pow` and the cloud lighting run on every pixel, and
`cloud_density = 1.0` zeroes the resulting MASK, after the work. Clouds off
is a look, not a saving.

RETRACTED AGAIN, same day, by measurement: the branch around that block
recovered nothing, and nor did any edit to the shader — a valid sky of a
flat colour costs what SkyMint costs. **The cost is the radiance map**: on
GL Compatibility a custom sky's radiance cubemap is rendered and filtered
every frame and read by every lit surface as ambient and reflection.
`radiance_size` 128 → 32 recovers half; flat ambient plus reflections
disabled recovers all of it. The full ladder, and the two broken-shader
copies that misled it for an hour, are in `docs/DRAW_CALL_BUDGET.md` § "The
sky, priced". Which of the two to ship is a look call and is the walker's.
'''


def main() -> int:
    edit(BUDGET, [(BUDGET_OLD, BUDGET_NEW)], "DRAW_CALL_BUDGET.md")
    edit(SKY, [(SKY_OLD, SKY_NEW)], "SKY_PROVIDER.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
