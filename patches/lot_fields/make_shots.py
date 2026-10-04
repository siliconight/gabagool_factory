"""Write `field_shots.gd` beside this file: the dumpster frame script
(`patches/lot_dumpsters/dumpster_shots.gd`) with its SHOTS replaced by one
street-level and one overhead view of every parking field and one front
view of every pad, read off a site's gameplay (`field_plan`, `yard_plan`).
Plan (x, y) is Godot (x, -y).

    python make_shots.py <site.site.gameplay.json>
"""
import json
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "lot_dumpsters" / "dumpster_shots.gd"
NORMAL = {"S": (0.0, -1.0), "N": (0.0, 1.0), "E": (1.0, 0.0), "W": (-1.0, 0.0)}


def g(x, y, h):
    return "Vector3(%.2f, %.2f, %.2f)" % (x, h, -y)


def main():
    gp = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    shots = []
    for f in (gp.get("field_plan") or {}).get("placed") or []:
        (ax, ay), (bx, by) = f["driveway"]["a"], f["driveway"]["b"]
        ux, uy = bx - ax, by - ay
        n = math.hypot(ux, uy)
        ux, uy = ux / n, uy / n
        cx, cy = f["at"]
        shots.append((f["name"] + "_street", g(ax - ux * 3.0, ay - uy * 3.0, 1.7), g(cx, cy, 0.6)))
        shots.append((f["name"] + "_above", g(ax - ux * 6.0, ay - uy * 6.0, 14.0), g(cx, cy, 0.0)))
    for i, y in enumerate((gp.get("yard_plan") or {}).get("placed") or []):
        nx, ny = NORMAL[y["wall"]]
        cx, cy = y["at"]
        shots.append(("pad_%d_%s" % (i, y["building"]), g(cx + nx * 9.0, cy + ny * 9.0, 2.2), g(cx, cy, 0.4)))
    body = ",\n".join('\t["%s", %s, %s]' % s for s in shots)
    src = SRC.read_text(encoding="utf-8")
    new, k = re.subn(r"const SHOTS: Array = \[\n.*?\n\]\n", "const SHOTS: Array = [\n" + body + ",\n]\n", src, flags=re.S)
    assert k == 1, "SHOTS block not found"
    new = new.replace("## Shoots each of the walker's lot's dumpsters from in front of it and from\n"
                      "## above, with a plain fill so the night level reads, into the folder after `--`.",
                      "## Shoots each parking field from the street and from above, and each\n"
                      "## dumpster's pad from in front, with a plain fill so the night level\n"
                      "## reads, into the folder after `--`. Written by make_shots.py.")
    (HERE / "field_shots.gd").write_text(new, encoding="utf-8", newline="\n")
    print("%d shot(s) -> field_shots.gd" % len(shots))


if __name__ == "__main__":
    main()
