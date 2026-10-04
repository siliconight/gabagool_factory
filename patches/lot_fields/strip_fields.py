"""The "off" side of pricing the parking fields: in a COPY of a built
package, remove every node a field brought -- its slab (`field_<i>`), its
bay lines (`fmark_<n>_bay_line`) and its cars (the `cover_<i>` its
gameplay's `field_plan.cover_index` names) -- with their children, from
EVERY scene in the package that carries them. Sub-resources are left; an
unused one costs nothing at runtime. The driveway's kerb cut stays: it is
the sidewalk band split one more time, the same surface. Prints what it
removed per scene and refuses a package where any carrying scene does not
hold every field car.

THE FIRST VERSION STRIPPED ONLY `site.tscn`, AND ITS PRICE WAS VOID. The
package loads `presentation/lux.applied.tscn`, the site scene as the Lux
stage re-saved it, which carries its own copy of every node. Priced on
cold run 9141, "off" read 0.00 draws different from "on" at all 53
headings -- the instrument could not see the change, so it measured
nothing. Kept here above the version that replaced it.

    python strip_fields.py <package copy> <site.site.gameplay.json>
"""
import json
import pathlib
import re
import sys


def strip(text, cars):
    lines = text.split("\n")
    out, drop, gone = [], False, set()
    removed = {"slab": 0, "line": 0, "car": 0}
    for ln in lines:
        if ln.startswith("["):
            drop = False
            m = re.match(r'^\[node name="([^"]+)"', ln)
            if m:
                name = m.group(1)
                pm = re.search(r' parent="([^"]*)"', ln)
                parent = pm.group(1) if pm else None
                top = None
                if parent == ".":
                    top = name
                elif parent is not None:
                    top = parent.lstrip("./").split("/")[0]
                if parent == "." and (re.fullmatch(r"field_\d+", name)
                                      or re.fullmatch(r"fmark_\d+_bay_line", name)
                                      or name in cars):
                    gone.add(name)
                    removed["slab" if name.startswith("field_") else
                            "line" if name.startswith("fmark_") else "car"] += 1
                if top in gone:
                    drop = True
        if not drop:
            out.append(ln)
    return "\n".join(out), removed


def main():
    pkg, gp = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    plan = json.loads(gp.read_text(encoding="utf-8")).get("field_plan") or {}
    cars = {f"cover_{i}" for i in plan.get("cover_index") or []}
    touched = 0
    for scene in sorted(pkg.rglob("*.tscn")):
        raw = scene.read_bytes()
        if b'name="field_' not in raw and b'_bay_line"' not in raw:
            continue
        crlf = b"\r\n" in raw
        text = raw.decode("utf-8").replace("\r\n", "\n")
        new, removed = strip(text, cars)
        if removed["car"] != len(cars):
            sys.exit("%s: field_plan names %d cars, the scene held %d of them"
                     % (scene, len(cars), removed["car"]))
        body = new.replace("\n", "\r\n") if crlf else new
        scene.write_bytes(body.encode("utf-8"))
        touched += 1
        print("%s: removed %d field slab(s), %d bay line(s), %d car(s)"
              % (scene.relative_to(pkg), removed["slab"], removed["line"], removed["car"]))
    if not touched:
        sys.exit("no scene in %s carries a field: nothing to strip, so no 'off' side" % pkg)


if __name__ == "__main__":
    main()
