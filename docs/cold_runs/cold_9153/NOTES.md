# Cold run 9153 -- 0 interventions; the windows show, the gutters arrive

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack:**
- Level Factory 0.140.0 -- a lit face keeps its own UVs;
- Patina 0.25.0 -- gutters back at the eave, downspouts;
- Zoo 1.67.0 -- an open trough, a leader into a boot, painted metal.

**Result:** every leg ran, in 32.8 minutes, with `INTERVENTIONS: 0`. No
`STEM COLLISION` in any job log.

## The painted windows, in a cold run at last

`patches/lf_empties/pane_census.gd` on the walk copy: all 164 painted panes
import as `M_Window_pane_Face` with `uv1_triplanar false`,
`uv1_world_triplanar false`, `uv1_scale` 1.0 -- their own UVs -- emission
on, energy 1.60, Lux's binder name test true.

The frames (`docs/findings/empties_gutters_9153/`) show the windows from the
street:
- at night a few lit among mostly dark ones, in more than one light;
- with the fill, the sashes, blinds and shades.

That matches the re-import proof made from 9152's walk copy.

## The gutters

**Patina's own orders:**

| building | gutters at z | downspouts |
|---|---|---|
| `gs_empty_rowhome_f` | 8.92 (9151, 9152: 9.92 on the parapet) | 2 |
| freight terminal | 5.62 (from its parapet top at 6.92) | 16 |
| gas station | 3.22 (no parapet; unchanged) | 8 |

**In the frames:** a pale leader down each rowhome front at the house's end,
into a boot at the sidewalk, and a pale gutter under each cornice.

## Found in the frames: the gutter broke over every top-floor window

Close up, the gutter stopped at each top-floor window bay. `roofline_slots`
returned wall slots only, and a window is a slot of its own. Measured on
Deli Counter's real `gs_empty_rowhome_f`: a 0.95 m gap, -1.975 to -1.025.

Fixed in **Patina 0.25.1**: the top storey's exterior openings are part of
the roofline. The rowhome goes from 22 to 25 gutter sections, the freight
terminal from 82 to 90, the gas station from 41 to 49. No gutter or
downspout touches an opening keep-out.

## Seen, recorded

**Each visible cover is a draw call** (9152 notes). The gutters add sections
and the downspouts add meshes. The price is taken on cold run 9154, the
final state, against 9152 at fixed stations, with 9152 measured twice as the
control.
