"""Zoo 1.59.0: a car's paint rides its vertices, so a car is four draws.

Measured on cold run 9141 (`docs/cold_runs/cold_9141/NOTES.md`): the
parking fields' 17 cars cost +33 draws a heading and +0.15 ms, about 11
draws a visible car. A built car was 10-12 meshes on 9-11 materials, and
six to eight of those materials were ONE pack (`metal_painted`) in six to
eight colours -- body, brightwork, three lamp colours, the plate, cladding,
the grey bumper -- because a tintable pack makes one material per colour,
and `merge.pack_by_material` cannot pack across materials. That is the
colour-only variation `CLAUDE.md`'s draw-call rule names first, and Zoo
1.8.0's `geometry.tint_wear` is the path that rule asks for.

Anchored edits (every anchor once; refuses on a miss):
`zoo_keeper/core/car_forms.py` (`PAINTED`, `FIXED_PAINT`, `paint_tints`),
`zoo_keeper/recipes/simple_car.py` (the painted parts share one material
and carry their colour in `Wear`), `tests/test_car_forms.py`. CHANGELOG and
VERSION from `zoo_car_paint/CHANGELOG_1.59.0.md`.

    python patch_zoo_car_paint.py
    ZOO_ROOT=<copy> python patch_zoo_car_paint.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_car_paint"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


FORMS_ADD = '''

#: THE PAINTED PARTS (1.59.0). Every part of a car painted with the
#: `metal_painted` pack, by the recipe's group key, and the colour it wears
#: when it is not the body's paint or the cladding: brightwork, the three lamp
#: lenses, the plate and the grey bumper. These are the colours the recipe
#: passed to `make_material` before 1.59.0, moved here so a test can hold them.
#: They share ONE material, `PAINTED`, whose base is white; each part carries
#: its colour in its `Wear` attribute (`geometry.tint_wear`), so
#: `merge.pack_by_material` packs them into one mesh. Before, a tintable pack
#: made one material per colour and a car was 9-11 materials, 10-12 draws.
PAINTED = (1.0, 1.0, 1.0)
FIXED_PAINT = {
    "chrome": (0.66, 0.67, 0.68),
    "lamp_head": (0.86, 0.88, 0.87),
    "lamp_tail": (0.50, 0.03, 0.03),
    "lamp_amber": (0.80, 0.38, 0.03),
    "plate": (0.80, 0.78, 0.62),
    "bumper_grey": CLADDING["grey"],
}


def paint_tints(form, body_kind="metal_painted"):
    """{group key: rgb} for every part that wears `PAINTED`, from a car's
    form. The body joins only when its kind is `metal_painted` -- a genome
    may ask for `plastic`, which is another pack and keeps its own material.
    Pure."""
    out = dict(FIXED_PAINT)
    out["cladding"] = tuple(CLADDING[form["cladding"]])
    if body_kind == "metal_painted":
        out["body"] = tuple(form["paint"])
    return out
'''


def main():
    v = (ZOO / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "1.58.0", v
    _edit(ZOO / "zoo_keeper" / "core" / "car_forms.py", [
        ('INTERIOR = {"grey": (0.24, 0.24, 0.25), "tan": (0.40, 0.33, 0.24),\n'
         '            "blue_grey": (0.18, 0.21, 0.27)}\n',
         'INTERIOR = {"grey": (0.24, 0.24, 0.25), "tan": (0.40, 0.33, 0.24),\n'
         '            "blue_grey": (0.18, 0.21, 0.27)}\n' + FORMS_ADD),
    ])
    _edit(ZOO / "zoo_keeper" / "recipes" / "simple_car.py", [
        ('    for key, obj in by_group.items():\n'
         '        materials.assign([obj], mats[key])\n',
         '    # ONE PAINTED MATERIAL (1.59.0): every `metal_painted` part wears\n'
         '    # `car_forms.PAINTED` and carries its own colour in `Wear`, so the\n'
         '    # merge packs them into one mesh -- the same base colour glTF computed\n'
         '    # from the material\'s factor, moved into COLOR_0, which Level Factory\'s\n'
         '    # import draws as albedo. A lamp renamed to light at night (see the\n'
         '    # lamps above) would have to leave this material again.\n'
         '    tints = car_forms.paint_tints(f, kind_paint)\n'
         '    painted = materials.make_material("M_Car_painted", list(car_forms.PAINTED),\n'
         '                                      "metal_painted")\n'
         '    for key, obj in by_group.items():\n'
         '        if key not in tints:\n'
         '            materials.assign([obj], mats[key])\n'
         '            continue\n'
         '        materials.assign([obj], painted)\n'
         '        if not geometry.tint_wear(obj, tints[key]):\n'
         '            raise RuntimeError(f"simple_car: {obj.name} has no Wear layer, so its "\n'
         '                               f"paint would not land")\n'),
    ])
    tests = ZOO / "tests" / "test_car_forms.py"
    s = tests.read_text(encoding="utf-8")
    assert "\r" not in s
    s = s.rstrip("\n") + "\n" + (SRC / "tests_append.py").read_text(encoding="utf-8")
    tests.write_text(s, encoding="utf-8", newline="\n")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    assert s.startswith("## [1.58.0]"), "changelog head"
    ch.write_text((SRC / "CHANGELOG_1.59.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.59.0", encoding="utf-8", newline="\n")
    print("Zoo 1.59.0 applied")


if __name__ == "__main__":
    main()
