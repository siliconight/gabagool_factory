"""The wires a themed site strings, read off the run's own drawn spec through Lot's own functions.

    python docs/cold_runs/cold_9263/wire_spans.py <site.site.drawn.json>

Prints every pole (plan metres, x east and y north, the frame the spec is in) and every span
`site_poles.spans` strings: its two poles, its plan length, its 32 m cell and the lowest point of its
lowest wire above the road's surface (the sidewalk band's top, `lot.SIDEWALK_H`, is where a pole
stands). Then the cells and the triangles `wire_meshes` draws. The Godot frame a camera is given in
is (x, height, -y). It measures and stops.
"""
import json
import math
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(F / "lot"))

import lot          # noqa: E402
import site_poles   # noqa: E402


def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    cover = spec.get("cover") or []
    poles = [p for p in cover if p.get("species") == "utility_pole"]
    print("Lot %s, %d poles" % ((F / "lot" / "VERSION").read_text().strip(), len(poles)))
    for p in sorted(poles, key=lambda q: (q["line"], q["line_i"])):
        print("  %-8s line %-3s i %d  plan (%.2f, %.2f)  yaw %.0f  form %s"
              % (p["name"], p["line"], p["line_i"], p["at"][0], p["at"][1], p["yaw"], p.get("form") or "auto"))
    base = lot.SIDEWALK_H
    spans = site_poles.spans(cover)
    print("%d spans" % len(spans))
    cells = {}
    for a, b in spans:
        mx, my = (a["at"][0] + b["at"][0]) / 2.0, (a["at"][1] + b["at"][1]) / 2.0
        cell = (int(math.floor(mx / site_poles.WIRE_CELL_M)), int(math.floor(my / site_poles.WIRE_CELL_M)))
        cells.setdefault(cell, 0)
        cells[cell] += 1
        low = min(z for name in site_poles.WIRES for _x, _y, z in site_poles.wire_path(a, b, name, base))
        kind = "along" if a["line"] == b["line"] else "tie"
        print("  %-8s %-8s %-5s %5.1f m  mid plan (%.1f, %.1f)  cell %s  lowest %.2f m"
              % (a["name"], b["name"], kind, math.hypot(a["at"][0] - b["at"][0], a["at"][1] - b["at"][1]),
                 mx, my, cell, low))
    body, _sub, files = site_poles.wire_meshes(cover, base)
    tris = sum(t.count("\nf ") for t in files.values())
    print("%d cells %s, %d triangles, %d nodes" % (len(files), sorted(files), tris,
                                                    sum(1 for l in body if l.startswith("[node "))))


if __name__ == "__main__":
    main()
