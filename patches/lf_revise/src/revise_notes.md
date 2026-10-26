# Increment 6 (roadmap 316) working notes -- not shipped

- `update_design {path, revision, choices?, intent?, name?}`: the caller names the revision it edited; a mismatch
  is a `conflict` refusal (the design moved since it was read). Values are checked against the catalog; the result
  is revision + 1, `updated_at` moved, written atomically. Returns the design and `rebuilds`: the union of the
  changed controls' `rebuilds` words (layout / lighting / backdrop / art).
- `walk_level` re-writes `request/` from the CURRENT revision and re-imports it (`batch create`) before the art leg,
  so the brief that builds is the revision the panel shows. It refuses with `needs_new_layouts` when a changed
  control rebuilds the layout (streets, layouts to generate): the chosen layout was built from the old ones.
- Panel: supported and conditional controls editable (OptionButton / SpinBox / CheckBox), intent as text; Save
  makes the revision; Undo saves the previous values as a new revision (history is never rewritten).
- Proof wanted: change time of day evening -> midnight on `levels/panel_trial`, walk again; the art leg's jobs
  that rebuild are the lighting ones (`lux_apply` and what depends on it), the shell's are cache hits; the walk's
  label moves to revision 2.
