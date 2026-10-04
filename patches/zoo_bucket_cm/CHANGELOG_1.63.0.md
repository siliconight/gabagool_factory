## [1.63.0] - a module is grouped no finer than the name it is given

Cold run 9149 stopped at art on its first blocking `ZOO_STEM_COLLISION`.
The freight terminal's parapet tiles -- wall slots since Deli Counter
0.177.0, cut at millimetre-snapped lines -- were 4.514 and 4.515 m (and
4.909 against 4.910). `plan_kit` grouped exact-fit slots by dims to 0.1 mm
and named them in whole centimetres, so it made two modules under one name,
`wall_delco_1997_04_w451_mmetal`, and 1.62.0 refused the kit.

That refusal was correct by its own definition. The defect was one number
asked at two resolutions: Deli Counter 0.177.0 had moved its own name check
to centimetres for exactly these tiles, and this side's grouping had not
moved. A group finer than the name it is given is a collision by
construction.

`dims_key` is now whole centimetres. Two slots a millimetre apart are one
module, built to the first slot's dims; neighbouring parapet tiles meet
within a millimetre. A difference the name cannot carry at that resolution
-- 2.8 against 3.1 m without `fit.key_height` -- still collides and is still
refused.

`tests/test_bucket_at_name_resolution.py`:
- a millimetre apart is one module (fails on 1.62.0);
- the control: a real height difference collides unmarked and splits
  marked.
