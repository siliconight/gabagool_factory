"""The "off" side of pricing the getaway van: in a COPY of a built package,
remove the van's node -- the `cover_<i>` whose drawn-spec record says
`source: getaway_van` -- with its children, from EVERY scene in the package
that carries it. Sub-resources are left; an unused one costs nothing at
runtime. Prints what it removed per scene, and refuses a package where no
scene carries the van or a carrying scene does not hold it.

EVERY SCENE, because the first parking-fields price stripped only `site.tscn`
and was void: the package loads `presentation/lux.applied.tscn`, the Lux
stage's re-save of the site, which carries its own copy of every node, and
"off" read 0.00 draws different from "on" at all 53 headings (cold run 9141,
`patches/lot_fields/strip_fields.py`). This is that script's shape, for one
node.

    python strip_van.py <package copy> <site.site.drawn.json>
"""
import json
import pathlib
import re
import sys


def van_nodes(drawn):
    """The scene node names of the getaway van(s) the drawn spec records."""
    return {f"cover_{i}" for i, cv in enumerate(drawn.get("cover") or [])
            if cv.get("source") == "getaway_van"}


def strip(text, names):
    """``text`` without the top-level nodes in ``names`` and their children;
    and how many of them it removed."""
    out, drop, gone = [], False, set()
    for ln in text.split("\n"):
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
                if parent == "." and name in names:
                    gone.add(name)
                if top in gone:
                    drop = True
        if not drop:
            out.append(ln)
    return "\n".join(out), len(gone)


def main():
    pkg, drawn_path = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    names = van_nodes(json.loads(drawn_path.read_text(encoding="utf-8")))
    if not names:
        sys.exit("%s records no getaway van: nothing to strip, so no 'off' side" % drawn_path)
    touched = 0
    for scene in sorted(pkg.rglob("*.tscn")):
        raw = scene.read_bytes()
        if not any(('name="%s"' % n).encode() in raw for n in names):
            continue
        crlf = b"\r\n" in raw
        text = raw.decode("utf-8").replace("\r\n", "\n")
        new, removed = strip(text, names)
        if removed != len(names):
            sys.exit("%s: the drawn spec names %d van node(s) %s, the scene held %d at the top"
                     % (scene, len(names), sorted(names), removed))
        scene.write_bytes((new.replace("\n", "\r\n") if crlf else new).encode("utf-8"))
        touched += 1
        print("%s: removed %s" % (scene.relative_to(pkg), ", ".join(sorted(names))))
    if not touched:
        sys.exit("no scene in %s carries %s: nothing to strip, so no 'off' side" % (pkg, sorted(names)))


if __name__ == "__main__":
    main()
