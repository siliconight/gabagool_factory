"""Light anchors by type across Deli Counter's built library: anchors, lamps and buildings a type.

    python docs/findings/fixture_rows/type_census.py [<deli_counter build dir>]

Reads every `<shell>.lights.json` in the build directory (default: the factory's
`deli_counter/build`) and counts, per anchor type, the anchors, the lamps their rows carry
(`row.count`, 1 when absent) and the buildings carrying any. Written for Deli Counter 0.208.0
(roadmap 229's species step: a home's room writes `dome` where it wrote `fluorescent`), to read
the library before and after its rebuild. It prints what it counted and stops.
"""
import collections
import json
import pathlib
import sys


def census(build):
    anchors, lamps, buildings = collections.Counter(), collections.Counter(), collections.defaultdict(set)
    files = sorted(pathlib.Path(build).glob("*.lights.json"))
    for p in files:
        doc = json.loads(p.read_text(encoding="utf-8"))
        for a in doc.get("anchors") or []:
            t = str(a.get("type", "?"))
            anchors[t] += 1
            lamps[t] += int((a.get("row") or {}).get("count", 1) or 1)
            buildings[t].add(p.name[:-len(".lights.json")])
    return len(files), anchors, lamps, buildings


def main(argv):
    build = argv[0] if argv else str(pathlib.Path(__file__).resolve().parents[3] / "deli_counter" / "build")
    n, anchors, lamps, buildings = census(build)
    print("%d lights manifests in %s" % (n, build))
    print("%-18s %8s %8s %10s" % ("type", "anchors", "lamps", "buildings"))
    for t in sorted(anchors, key=lambda k: -anchors[k]):
        print("%-18s %8d %8d %10d" % (t, anchors[t], lamps[t], len(buildings[t])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
