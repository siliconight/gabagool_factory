## [1.60.0] - a slot marked `fit.key_height` names its height

`module_stem` names a wall, doorway or window by its width alone. The
docstring gives the reason -- "its thickness and the storey height are
fixed, so `_w<cm>` is a complete key". Deli Counter 0.175.2's Empties are the
first buildings where that is false:
- their walls run the full 3.1 m storey where no slab sits above;
- under the roof they stop at 2.8 m.

Cold run 9148's kit for `gs_empty_rowhome_f` listed
`wall_delco_1997_01_w200_mbrick_idrywall` twice -- two buckets of 11 slots,
two heights, one file -- and the module on disk was 2.8 m. Every 3.1 m side
wall got a 2.8 m panel: a 0.3 m strip at each storey line, which the frames
showed. The buckets were already split by their exact dims; only the name
was shared, and the later build overwrote the earlier.

Of the library's buildings, only the 8 facade shells have a wall name
covering two heights. So height is not added to every wall: that would
rename every wall in every building to fix eight.
- Deli Counter (>= 0.176.0) marks each slot whose name covers two heights
  with `fit.key_height`.
- Here `height_cm` joins the name when the slot is marked.
- Unmarked, every name is as before.

`themed_tscn.resolve_themed_stem` in Deli Counter is the mirror and changes
in the same release.

`tests/test_key_height.py`:
- two marked heights build two named walls (fails on 1.59.0);
- the control: an unmarked wall keeps its name.
