"""Compare two `car_hashes.py` reports: is every simple_car build the same?

    python compare_hashes.py car_hashes_1850.json car_hashes_1860.json

Prints each build (style and slot) as SAME or DIFFERS, every mesh that
differs, and the totals. A report without the fields it reads fails.
Prints what it measured and stops.
"""
import json
import sys


def main(a_path, b_path):
    a = json.load(open(a_path, encoding="utf-8"))
    b = json.load(open(b_path, encoding="utf-8"))
    if set(a) != set(b):
        raise SystemExit("the reports cover different builds: %s" % sorted(set(a) ^ set(b)))
    meshes = differ = 0
    for key in sorted(a):
        ra, rb = a[key], b[key]
        for need in ("objects", "attachments", "form"):
            if need not in ra or need not in rb:
                raise SystemExit("%s: no %r in a report" % (key, need))
        print("%-26s %-7s style=%s objects=%d" % (key, "SAME" if ra == rb else "DIFFERS",
                                                 ra["form"].get("style"), len(ra["objects"])))
        for name in sorted(set(ra["objects"]) | set(rb["objects"])):
            meshes += 1
            if ra["objects"].get(name) != rb["objects"].get(name):
                differ += 1
                print("    %s: %s -> %s" % (name, ra["objects"].get(name), rb["objects"].get(name)))
        if ra["attachments"] != rb["attachments"]:
            print("    attachments: %s -> %s" % (ra["attachments"], rb["attachments"]))
    print("%d builds, %d meshes compared, %d differ" % (len(a), meshes, differ))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
