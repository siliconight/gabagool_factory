"""Write `street_shots.gd` beside this file: the field frame script with its
SHOTS replaced by two views of the whole row along the through road -- one
from above and in front, one from the far sidewalk at eye height looking
down the row -- placed from a site's own drawn spec (`site.site.drawn.json`:
the buildings and the through road, road 0). Plan (x, y) is Godot (x, -y).

    python make_street_shots.py <site.site.drawn.json>
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "lot_fields" / "field_shots.gd"


def g(x, y, h):
    return "Vector3(%.2f, %.2f, %.2f)" % (x, h, -y)


def main():
    s = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    road = s["roads"][0]
    y_road = (road["a"][1] + road["b"][1]) / 2.0
    xs = [b["at"][0] for b in s["buildings"]]
    x0, x1 = min(xs), max(xs)
    mid = (x0 + x1) / 2.0
    far_walk = y_road - road["width"] / 2.0 - road.get("sidewalk", 0) / 2.0
    shots = [
        ("street_above", g(mid, y_road - 70.0, 55.0), g(mid, y_road + 20.0, 0.0)),
        ("street_down_the_row", g(x0 - 30.0, far_walk, 1.7), g(x1, y_road + 12.0, 3.0)),
    ]
    body = ",\n".join('\t["%s", %s, %s]' % sh for sh in shots)
    src = SRC.read_text(encoding="utf-8")
    new, k = re.subn(r"const SHOTS: Array = \[\n.*?\n\]\n", "const SHOTS: Array = [\n" + body + ",\n]\n",
                     src, flags=re.S)
    assert k == 1, "SHOTS block not found"
    new = re.sub(r"## Shoots each parking field.*?Written by make_shots\.py\.",
                 "## Shoots the whole row along the through road, from above and from the\n"
                 "## far sidewalk, with a plain fill so the night level reads, into the\n"
                 "## folder after `--`. Written by make_street_shots.py.", new, flags=re.S)
    (HERE / "street_shots.gd").write_text(new, encoding="utf-8", newline="\n")
    print("%d shot(s) -> street_shots.gd" % len(shots))


if __name__ == "__main__":
    main()
