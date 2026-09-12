"""Roadmap batch 23, 2026-09-11: item 142 narrowed (its hypothesis refuted,
the real cause measured) and item 147 filed from that measurement.
REPLACE for 142 (old status kept verbatim), APPEND for 147. Asserts.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD_142 = """*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON, HALF MEASURED*

**142. A prop ships black.**"""

NEW_142 = """*STATUS: NARROWED 2026-09-11 -- THE HYPOTHESIS IS REFUTED AND THE CAUSE IS
MEASURED: THE PROP IS NOT UNSKINNED, IT IS UNLIT; FILED AS ITEM 147. REFUTED,
kept: "a primitive with no UVs samples one texel". The prop GLBs' second
primitive is `Prop-colonly` -- the collision mesh, which Godot never draws --
and the visible `Prop_Panel` carries `TEXCOORD_0`, `COLOR_0` at ~0.8 and the
skin material with its texture (`prop_delco_1997_01_*`, concrete) or
(`prop_delco_1997_05_*`, `M_Skin_metal_delco_1997`, metallic 0.85, the
`metal_rusted_street` pack, albedo mean 115/80/53). The walked "waist-high
box in a ward" is a style-5 metal prop: the 1.2 x 2.4 x 1.0 supply cart or
the 4.0 x 1.4 x 1.1 nurse station. SECOND HYPOTHESIS, TESTED AND REFUTED
TOO: a rough conductor with nothing to reflect renders as albedo x 0.15
under GL Compatibility -- so the walked copy's nurse-station GLB was
patched to metallic 0.0 (Godot read the imported material back at 0.00),
re-imported, and `look_shots --station` re-shot from 2.7 m: mean 6.5 ->
6.5, crushed 75.06% -> 74.88%. A knob with no effect. THE MEASUREMENT:
from `site.site.lights.json`, the nearest lamp point to the counter is
4.0 m away in plan (`ground_west_ward_ceiling`, at 3.2 m up), ~4.7 m to
the counter's side faces; Lux's fluorescent range is `clamp(drop + 0.75,
4.0, 7.5)` = 4.0 m for this drop (32 of the copy's 54 spawned fluorescents
carry `omni_range = 4.0`) and Godot's attenuation is hard zero at the
range. Nothing reaches it. The prop is black because it stands where no
light does, and the wall beside it is skinned because it stands 1.7 m from
a lamp. That is a room-lighting fact, not a prop fact -- item 147. What
remains of THIS item: nothing about the prop; `texel_density.gd`'s planned
"textured material and no UVs" report would have found nothing here, and
is not built. EARLIER STATUS, KEPT VERBATIM: OPEN 2026-09-11 -- FOUND BY A
PERSON, HALF MEASURED*

**142. A prop ships black.**"""

APPEND = """
*STATUS: OPEN 2026-09-11 -- MEASURED FROM ITEM 142'S BLACK PROP; ITEM 54'S
PRICE, NOW SEEN FROM THE FLOOR*

**147. One centre row at a 4.0 m reach cannot light a room wider than 8 m,
and the median room is 12 m.** Deli Counter lays ONE fluorescent row per
room along its longer axis at the room's centre line (`lights._row_for_bounds`),
and Lux ranges each lamp at `clamp(drop + 0.75, 4.0, 7.5)` -- 4.0 m for
the 3.2 m drop every 3.7 m storey gives -- because item 54 priced the
per-mesh light budget and cut the range to the floor-pool minimum. Those
two rules together light a band 8 m wide down the middle of the room and
nothing outside it. Measured over the library's 692 rooms
(`build/*.gameplay.json`, 2026-09-11): median short side 12.0 m, p90 21.0
m; 573 of 692 (83%) are wider than 2 x 4.2 m, 453 (65%) wider than 2 x
5.0 m. On cold run 9005's hospital the wards are 12 m wide, the nurse
station stands 4 m off the centre line, and it was walked as "a prop with
no skin, black" (item 142). Every wall-side prop in every ward is in the
same dark margin, and so is the wall base. **WHAT WOULD CLOSE THIS:** rows
that cover the room -- `ceil(short_side / (2 x reach))` parallel rows at
`short_side / rows` spacing, with `reach` derived in DC from the same drop
Lux derives its range from (one formula, named in both places, pinned by a
test) -- and the per-mesh light census run before and after on the
hospital and `lot_demo_001`, because a second row in a 12 m room is more
lamps within 4.0 m of every 5 m slab tile and item 54's budget of 8 per
mesh is the ceiling this has to fit under. If it does not fit, the honest
alternative is a range that reaches the wall and a budget paid in shadows
or in tiles, and that is item 54 reopened, not this item closed quietly.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    if text.count(OLD_142) != 1:
        print("142 anchor matched %d times; refusing" % text.count(OLD_142), file=sys.stderr)
        return 1
    if "\n**147. " in text:
        print("item 147 already present", file=sys.stderr)
        return 1
    lines = text.split("\n")
    # an item heading is `**NNN. `; `**482 collected**` is a count line
    later = [l for l in lines if l.startswith("**") and l[2:5].isdigit()
             and l[5:7] == ". " and int(l[2:5]) > 146]
    if later:
        print("an item after 146 exists: %r" % later[0][:40], file=sys.stderr)
        return 1
    text = text.replace(OLD_142, NEW_142, 1)
    text = text.rstrip("\n") + "\n" + APPEND.rstrip("\n") + "\n"
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 142 narrowed, 147 filed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
