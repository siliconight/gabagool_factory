"""Lot 0.84.0: handbills on the alley walls and the poles, as HUNG pieces.

Every anchor asserted to match exactly once; nothing is written on a miss.
"""
import pathlib
import sys

LOT = pathlib.Path(__file__).resolve().parent.parent / "lot"

EDITS = [
    # the stem mirror spells Zoo's `_n<variant>` after the form
    ('''def cover_module_stem(species: str, theme: str, style: int,
                      dims, form: str = None) -> str:''',
     '''def cover_module_stem(species: str, theme: str, style: int,
                      dims, form: str = None, variant: int = None) -> str:'''),
    ('''    w, d, h = (int(round(float(v) * 100)) for v in dims)
    base = f"prop_{species}_{theme}_{int(style):02d}_w{w}_d{d}_h{h}"
    return base + f"_f{form}" if form else base''',
     '''    w, d, h = (int(round(float(v) * 100)) for v in dims)
    base = f"prop_{species}_{theme}_{int(style):02d}_w{w}_d{d}_h{h}"
    # ``variant`` (0.84.0) is Zoo's `_n<variant>`, after the form and added
    # only when non-zero -- `kit.module_stem`'s own rule -- so no name built
    # before it moves. First caller: the hung posters (`site_posters`).
    stem = base + (f"_f{form}" if form else "")
    return stem + (f"_n{int(variant)}" if variant else "")'''),
    # the slot writer: hung pieces after the cover
    ('''        if cv.get("blade"):
            slots[-1]["form"] = str(cv["blade"])
    doc = {''',
     '''        if cv.get("blade"):
            slots[-1]["form"] = str(cv["blade"])
    n_cover = len(slots)
    # THE HUNG PIECES (0.84.0, `site_posters`): paper on an alley wall or a
    # pole. Not cover -- they live in their own list so nothing that reads
    # cover as cover ever sees them -- but slots all the same, so the kit
    # build that makes the street makes them. The slot stands at the
    # record's own mount height, with no collision, and carries Zoo's
    # dressing: the family as `form`, the sheet order as `variant`.
    for i, hv in enumerate(site_spec.get("hung", []) or []):
        sp, dims = hv.get("species"), hv.get("dims")
        if not sp or not dims or len(dims) < 3:
            continue
        cx, cy = hv["at"]
        base = SIDEWALK_H if hv.get("base") == "sidewalk" else 0.0
        slot = {
            "slot_id": f"hung_{i}", "role": "prop", "size_mod": "full",
            "style": int(hv.get("style") or 1),
            "material": COVER_MATERIALS.get(sp, "metal_painted"),
            "current_ref": "prop_greybox_01", "kit_axis": "theme",
            "species": sp,
            "transform": {"translation": [round(cx, 4), round(cy, 4),
                                          round(base + float(hv["z"]), 4)],
                          "rot_y": float(hv.get("yaw") or 0.0),
                          "scale": [1.0, 1.0, 1.0]},
            "fit": {"dims": [float(dims[0]), float(dims[1]), float(dims[2])],
                    "pivot": "center", "openings": [], "collision": "none"},
        }
        if hv.get("form"):
            slot["form"] = str(hv["form"])
        if hv.get("variant"):
            slot["variant"] = int(hv["variant"])
        slots.append(slot)
    coverage = {"prop/site_cover": n_cover}
    if len(slots) > n_cover:
        coverage["prop/site_hung"] = len(slots) - n_cover
    doc = {'''),
    ('''        "coverage": {"prop/site_cover": len(slots)},''',
     '''        "coverage": coverage,'''),
    # the material
    ('''                   # the gas station's price pylon (site_furniture.plan_pylons)
                   "price_pylon": "metal_painted"}''',
     '''                   # the gas station's price pylon (site_furniture.plan_pylons)
                   "price_pylon": "metal_painted",
                   # the handbills (site_posters): paper, the genome's own kind
                   "poster_wall": "paper"}'''),
    # the resolver reads either list
    ('''def cover_module_refs(site_spec, prefix, out_dir=None):''',
     '''def cover_module_refs(site_spec, prefix, out_dir=None, key="cover"):'''),
    ('''    for i, cv in enumerate(site_spec.get("cover", []) or []):
        sp, dims = cv.get("species"), cv.get("dims")''',
     '''    # ``key`` (0.84.0): "cover", or "hung" for `site_posters`' pieces --
    # the same resolution, a list of its own, refs keyed by its own index.
    for i, cv in enumerate(site_spec.get(key, []) or []):
        sp, dims = cv.get("species"), cv.get("dims")'''),
    ('''        st = int(cv.get("style") or style)
        tried = ([cover_module_stem(sp, theme, st, dims, form=cv["blade"])]
                 if cv.get("blade") else [])
        tried.append(cover_module_stem(sp, theme, st, dims))''',
     '''        st = int(cv.get("style") or style)
        form = cv.get("blade") or cv.get("form")
        tried = []
        if form and cv.get("variant"):
            tried.append(cover_module_stem(sp, theme, st, dims, form=form,
                                           variant=cv["variant"]))
        if form:
            tried.append(cover_module_stem(sp, theme, st, dims, form=form))
        # A HUNG PIECE STOPS AT ITS FORM. A poster run's plain name is
        # another family's art (Zoo draws `poster_wall` with no form as the
        # club's), so an alley slot with no alley module is drawn as nothing,
        # and said, rather than as a strip club's poster in an alley.
        if key == "cover" or not form:
            tried.append(cover_module_stem(sp, theme, st, dims))'''),
    ('''            findings.append((CODE_COVER_MODULE_MISSING,
                             f"cover_{i} ({sp}): no {' or '.join(tried)}.glb "''',
     '''            findings.append((CODE_COVER_MODULE_MISSING,
                             f"{key}_{i} ({sp}): no {' or '.join(tried)}.glb "'''),
    ('''                             f"cover_{i} ({sp}): {stem} built with status "''',
     '''                             f"{key}_{i} ({sp}): {stem} built with status "'''),
    # the scene writer
    ('''def _outdoor_nodes(site_spec, preview=False, self_flooring=None, skins=None,
                   cover_refs=None, signs=None):''',
     '''def _outdoor_nodes(site_spec, preview=False, self_flooring=None, skins=None,
                   cover_refs=None, signs=None, hung_refs=None):'''),
    ('''        bl, sr = _box_node(f"cover_{i}", (sx, sy, sz), (cx, base + sy / 2, -cy),
                           COVER_COLOR)
        body += bl
        sub += sr
''',
     '''        bl, sr = _box_node(f"cover_{i}", (sx, sy, sz), (cx, base + sy / 2, -cy),
                           COVER_COLOR)
        body += bl
        sub += sr

    # THE HUNG PIECES (0.84.0, `site_posters`): the module Zoo built, at the
    # record's own height. One with no module is not drawn -- a centimetre
    # box on a wall stands in for nothing -- and the resolver has said so.
    hung_refs = hung_refs or {}
    for i, hv in enumerate(site_spec.get("hung", []) or []):
        if i not in hung_refs:
            continue
        base = SIDEWALK_H if hv.get("base") == "sidewalk" else 0.0
        xform = _godot_transform(tuple(hv["at"]), float(hv.get("yaw") or 0.0),
                                 z=base + float(hv["z"]))
        body += [f'[node name="hung_{i}" parent="." '
                 f'instance=ExtResource("{hung_refs[i]}")]',
                 f'transform = Transform3D({xform})', '']
'''),
    ('''    res_lines += cover_ext

    outdoor_body, outdoor_sub = _outdoor_nodes(
        site_spec, preview=preview, self_flooring=self_flooring, skins=skins,
        cover_refs=cover_refs, signs=signs)''',
     '''    res_lines += cover_ext
    hung_refs, hung_ext, hung_findings = cover_module_refs(
        site_spec, prefix, os.path.dirname(os.path.abspath(out_path)), key="hung")
    for code, msg in hung_findings:
        print(f"[lot] {code}: {msg}")
    # a module both lists use is declared once
    res_lines += [ln for ln in hung_ext if ln not in res_lines]

    outdoor_body, outdoor_sub = _outdoor_nodes(
        site_spec, preview=preview, self_flooring=self_flooring, skins=skins,
        cover_refs=cover_refs, signs=signs, hung_refs=hung_refs)'''),
    # assemble: plan them once the street stands
    ('''    tscn_out = os.path.join(out_dir, f"{site_spec['name']}.tscn")
    write_godot_scene(site_spec, merged, tscn_out, preview=preview,''',
     '''    # THE HANDBILLS (0.84.0, `site_posters`): on the alley walls and the
    # poles, once the street's poles stand and the buildings' openings are
    # merged. Their own list, never `cover`.
    import site_posters
    import site_streets as _poster_streets
    poster_findings = []
    site_spec["hung"] = site_posters.plan(site_spec, merged,
                                          _poster_streets.roads(site_spec),
                                          poster_findings)
    merged["poster_plan"] = {"placed": site_spec["hung"]}
    for f_ in poster_findings:
        print(f"[lot] {f_}")

    tscn_out = os.path.join(out_dir, f"{site_spec['name']}.tscn")
    write_godot_scene(site_spec, merged, tscn_out, preview=preview,'''),
]


def main():
    p = LOT / "lot.py"
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8")
    if crlf:
        assert raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings"
        s = s.replace("\r\n", "\n")
    for a, b in EDITS:
        n = s.count(a)
        if n != 1:
            sys.exit(f"REFUSED: anchor matched {n} times:\n{a[:160]}")
        s = s.replace(a, b, 1)
    if crlf:
        s = s.replace("\n", "\r\n")
    p.write_bytes(s.encode("utf-8"))
    print("patched lot.py")


if __name__ == "__main__":
    main()
