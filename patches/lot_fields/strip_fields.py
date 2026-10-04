"""The "off" side of pricing the parking fields: in a COPY of a built
package, remove from `site.tscn` every node a field brought -- its slab
(`field_<i>`), its bay lines (`fmark_<n>_bay_line`) and its cars (the
`cover_<i>` its gameplay's `field_plan.cover_index` names) -- with their
children. Sub-resources are left; an unused one costs nothing at runtime.
The driveway's kerb cut stays: it is the sidewalk band split one more time,
the same surface. Prints what it removed and refuses a package whose scene
has none of them.

    python strip_fields.py <package copy> <site.site.gameplay.json>
"""
import json
import pathlib
import re
import sys


def main():
    pkg, gp = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    plan = json.loads(gp.read_text(encoding="utf-8")).get("field_plan") or {}
    cars = {f"cover_{i}" for i in plan.get("cover_index") or []}
    scene = pkg / "site.tscn"
    raw = scene.read_bytes()
    assert b"\r\n" not in raw, "CRLF scene; not handled"
    lines = raw.decode("utf-8").split("\n")
    out, drop, gone, removed = [], False, set(), {"slab": 0, "line": 0, "car": 0}
    for ln in lines:
        if ln.startswith("["):
            drop = False
            m = re.match(r'^\[node name="([^"]+)"', ln)
            if m:
                name = m.group(1)
                pm = re.search(r' parent="([^"]*)"', ln)
                parent = pm.group(1) if pm else None
                top = None
                if parent in (".", None):
                    top = name
                elif parent is not None:
                    top = parent.lstrip("./").split("/")[0]
                if parent in (".",) and (re.fullmatch(r"field_\d+", name) or re.fullmatch(r"fmark_\d+_bay_line", name)
                                         or name in cars):
                    gone.add(name)
                    removed["slab" if name.startswith("field_") else "line" if name.startswith("fmark_") else "car"] += 1
                if top in gone:
                    drop = True
        if not drop:
            out.append(ln)
    if not gone:
        sys.exit("no field node in %s: nothing to strip, so no 'off' side" % scene)
    if len(cars) != removed["car"]:
        sys.exit("field_plan names %d cars, the scene held %d of them" % (len(cars), removed["car"]))
    scene.write_bytes("\n".join(out).encode("utf-8"))
    print("removed %(slab)d field slab(s), %(line)d bay line(s), %(car)d car(s)" % removed,
          "-- %d of %d bytes kept" % (len("\n".join(out).encode("utf-8")), len(raw)))


if __name__ == "__main__":
    main()
