

# --- 1.59.0: a car's paint rides its vertices --------------------------------

def test_every_painted_part_keeps_the_colour_its_own_material_carried():
    """The literals are the colours the recipe passed `make_material` before
    1.59.0; a table read back from the module would pass whatever it said."""
    form = {"paint": (0.18, 0.46, 0.78), "cladding": "tan"}
    t = car_forms.paint_tints(form)
    assert t == {"body": (0.18, 0.46, 0.78), "cladding": (0.42, 0.34, 0.22),
                 "chrome": (0.66, 0.67, 0.68), "lamp_head": (0.86, 0.88, 0.87),
                 "lamp_tail": (0.50, 0.03, 0.03), "lamp_amber": (0.80, 0.38, 0.03),
                 "plate": (0.80, 0.78, 0.62), "bumper_grey": (0.20, 0.21, 0.22)}
    assert car_forms.PAINTED == (1.0, 1.0, 1.0)
    # a plastic body is another pack: it keeps its own material
    assert "body" not in car_forms.paint_tints(form, "plastic")


def test_the_recipe_paints_with_one_material_and_tints_the_wear():
    src = open(_RECIPE, encoding="utf-8").read()
    assert "car_forms.paint_tints(f, kind_paint)" in src
    assert re.search(r'painted = materials\.make_material\("M_Car_painted", list\(car_forms\.PAINTED\)', src)
    assert "geometry.tint_wear(obj, tints[key])" in src
    # a part whose tint did not land is refused, not shipped in white
    assert re.search(r'raise RuntimeError\(f"simple_car: \{obj\.name\} has no Wear layer', src)
    # every group a tint names is a group the recipe builds
    groups = set(re.findall(r'"(\w+)": "Car_\w+"', src))
    assert set(car_forms.paint_tints({"paint": (1, 1, 1), "cladding": "grey"})) <= groups
