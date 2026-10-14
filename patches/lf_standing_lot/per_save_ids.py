"""Do two Godot scenes differ in anything but the ids Godot draws at every save?

    python patches/lf_standing_lot/per_save_ids.py <package A> <package B> <relative path> [...]

Masks a node's `unique_id=<n>` and an ext_resource or sub_resource id of Godot's own drawing (`"<n>_<5 chars>"`,
`"<Type>_<5 chars>"`) wherever it appears, then compares the two texts line by line. Prints, per file, the count
of differing lines before and after the mask, and the first lines that still differ after it. Prints what it
measured; it names no cause.
"""
import re
import sys
from pathlib import Path

MASKS = [
    (re.compile(r"unique_id=\d+"), "unique_id=#"),
    # Godot's drawn ids: "12_ab3x9" for an ext_resource, "StandardMaterial3D_ab3x9" for a sub_resource
    (re.compile(r'"(\d+|[A-Za-z0-9]+)_([a-z0-9]{5})"'), r'"\1_#"'),
]


def masked(text):
    for rx, sub in MASKS:
        text = rx.sub(sub, text)
    return text


def main(a_root, b_root, rels):
    for rel in rels:
        a = (Path(a_root) / rel).read_text(encoding="utf-8").splitlines()
        b = (Path(b_root) / rel).read_text(encoding="utf-8").splitlines()
        raw = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
        ma, mb = [masked(x) for x in a], [masked(y) for y in b]
        left = [(i, x, y) for i, (x, y) in enumerate(zip(ma, mb)) if x != y]
        print("%-40s lines %d/%d, differing %d, after the mask %d%s" % (
            rel, len(a), len(b), raw, len(left) + abs(len(a) - len(b)),
            "" if len(a) == len(b) else " (line counts differ)"))
        for i, x, y in left[:3]:
            print("    line %d\n      A %s\n      B %s" % (i + 1, x[:160], y[:160]))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
