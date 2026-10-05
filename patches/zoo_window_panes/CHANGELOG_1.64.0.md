## [1.64.0] - an Empty's window is painted: lit, dark, curtained, barred

Cold run 9150 put the rowhome Empties across a street with real walls, roofs
and shut doors. At night they read as a black mass outside the streetlight
pools: every window was one opaque `glass_facade` pane. The walker's comp
for this (a Vampire: The Masquerade -- Bloodlines street, 2026-10-04: "I
think its actually ok to have lights on in the windows at night to show
life") is read off in the factory root's `docs/reference/EMPTIES_COMPS.md`,
"LIT WINDOWS AT NIGHT": mixed per building, most dark, some lit warm, many
lit ones behind bars, curtains and blinds, no real lights.

`core/window_panes.py` paints ONE ATLAS of eight states:
- `lit`, `lit_blind`, `lit_curtain`, `lit_bars`;
- `dark`, `dark_curtain`, `dark_bars`;
- `boarded` -- the 1990s vacant rowhouse.

Each cell is a rowhouse window: a painted-wood frame, a double-hung sash
with a meeting rail, six-over-six muntins. It is painted twice:
- an albedo;
- an EMISSION image that is black wherever the room light does not show --
  frames, muntins, bars, plywood. Blind slats and curtain fabric let a
  little through.

Glow taken from the albedo would have lit the plywood and the curtains.

A facade window slot carrying `pane` (Deli Counter >= 0.179.0):
- is named `_p<state>`, keyed on it, and carries it to the plan;
- `_arch.build_slab` UV-maps the pane's street face to that state's cell;
- `materials.make_pane_material` makes `M_Window_pane_Face` from the two
  images, so Lux's emissive binder darkens every lit window in the power
  cut.

An enterable window, or a state the atlas does not know, is built exactly as
before.

**Cost.**
- Every Empty window wears the same material, so the variety is UVs and
  costs no submission. Each window was already its own mesh.
- One 192x160 atlas pair is packed into each painted window module.
- No light.
- A lit window glows by day too. That is accepted, the game being mostly
  night, and recorded here rather than solved.

`tests/test_window_panes.py`:
- the atlas is the same bytes every build;
- only lit cells glow;
- each state's UVs sit inside its own cell;
- two states of one window are two named modules (fails on 1.63.0);
- controls: an enterable window and an unknown state are named as before;
- the state reaches the build plan;
- under Blender, a painted pane wears `M_Window_pane_Face`.
