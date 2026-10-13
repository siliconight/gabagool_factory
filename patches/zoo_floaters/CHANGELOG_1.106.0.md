## [1.106.0] - floaters: one rule for a detail laid on a surface

**Factory roadmap 234.** The walker asked for "Floaters" as a core concept, and the README has carried it
since 2026-10-11: a detail made as its own small mesh and laid ON a host surface, not cut into it. A solid
floater rests on its host with only a skirt below the host plane; a flat floater hovers a known amount off
it, one-sided. The helper the README described was not built. Each species so far chose its own number:
`flat_forms.JOIN` buries 4 mm and `crt_forms.STAND_BURY` 6 mm, `counter_register.PROUD` stands 3 mm off and
`flat_forms.ART_PROUD` 5 mm.

- **`core.floaters`**, pure Python:
  - `FLOATER_SKIRT`, 4 mm: past the coplanar census's 2 mm window (`PROBE_WINDOW`), Zoo's JOIN.
  - `FLOATER_PROUD`, 3 mm: on Godot's default depth buffer a 3 mm gap fights only beyond 50 m.
  - `basis` and `frame`: a right-handed frame whose z is the host's normal, turned about it.
  - `solid_frame`, for a solid floater lowered by its skirt; `flat_quad`, a flat floater's corners, wound
    to face along the normal.
  - A zero normal, a skirt out of the host, or a flat floater not off it, refuses.
- **`bpylayer.geometry.add_floater(bm, point, normal, build, spin, skirt)`**: `build(bm)` makes the
  floater in its own frame (Z up, its base at z = 0); its verts are carried onto the host.
- **`add_flat_floater(bm, point, normal, w, h, spin, proud)`** lays the one-sided quad. It gains `spin`
  over the README's first sketch, so a quad's width can lie along the face.
- **No species uses them yet.** Each built its floaters before the rule had a name; moving one is a change
  to that species' mesh, priced and censused as any other.
- The README's section says the helper is built, with its signatures.
- `tests/test_floaters.py`:
  - the numbers against `tests/test_coincident_faces`' `PROBE_TOL` and `fight_distance_m`;
  - the frame on eleven normals and five spins;
  - a solid floater's points at their height less the skirt;
  - a flat floater proud and facing out;
  - the refusals and determinism;
  - a bpy half building both and reading them back.

  It fails to import on 1.105.0.

**Suite:** 4,614 passed, 455 skipped, 1 xfailed in 5 min 44 s, where 1.105.0 passed 4,566 and skipped 449: the new file's 48 pure checks, and its six Blender checks skipped outside Blender. The new file fails to collect on 1.105.0, run against an export of it

**In Blender:** the whole of `tests/test_floaters.py` under Blender 5.1.1 with the command in its docstring: 54 passed, the six bmesh checks among them -- a knob built by `add_floater` on three normals, its lowest vertex the skirt below the host and its highest its height less the skirt, and a quad by `add_flat_floater` on three, facing along the normal and standing proud. No species calls either helper, so no build moved and no census is affected
