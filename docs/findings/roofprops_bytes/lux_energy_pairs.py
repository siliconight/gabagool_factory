"""Lux's applied scene, cold run against cold run, with the ids Godot draws at every save masked (roadmap 247).

    python docs/findings/roofprops_bytes/lux_energy_pairs.py <mission> <run A> <run B> [<run C> ...]

Reads each run's packaged `presentation/lux.applied.tscn` (`workspaces/cold-N-ws/.level_factory/exports/
LF_<mission>.portable-godot/`), masks a node's `unique_id=<n>` and Godot's drawn resource ids (`"<n>_<5 chars>"`,
`"<Type>_<5 chars>"`), and for each consecutive pair prints every line that still differs, under the node it
belongs to (`name <parent>`). Pairs whose line counts differ are said, not compared. Prints what it measured; it
names no cause.
"""
import pathlib
import re
import sys

F = pathlib.Path(__file__).resolve().parents[3]
ID = re.compile(r'"(\d+|[A-Za-z0-9]+)_([a-z0-9]{5})"')
UID = re.compile(r"unique_id=\d+")


def rows(mission, n):
    path = (F / "workspaces" / f"cold-{n}-ws" / ".level_factory" / "exports" / f"LF_{mission}.portable-godot"
            / "presentation" / "lux.applied.tscn")
    out, node = [], "(header)"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("[node "):
            name = re.search(r'name="([^"]+)"', line)
            parent = re.search(r'parent="([^"]*)"', line)
            node = "%s <%s>" % (name.group(1) if name else "?", parent.group(1) if parent else "")
        out.append((node, UID.sub("unique_id=#", ID.sub(r'"\1_#"', line))))
    return out


def main(mission, runs):
    for a, b in zip(runs, runs[1:]):
        ra, rb = rows(mission, a), rows(mission, b)
        if len(ra) != len(rb):
            print("%s vs %s: line counts %d and %d, not compared" % (a, b, len(ra), len(rb)))
            continue
        diff = [(x[0], x[1].strip(), y[1].strip()) for x, y in zip(ra, rb) if x[1] != y[1]]
        print("%s vs %s: %d of %d lines differ after the mask" % (a, b, len(diff), len(ra)))
        for node, x, y in diff:
            print("    %-58s %s  |  %s" % (node[:58], x[:34], y[:34]))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2:])
