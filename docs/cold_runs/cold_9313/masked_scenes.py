"""The 24 files 9313's package differs from 9312's in, each attributed (the factory's roadmap 251 and 247).

For the two scenes Level Factory 0.212.0 changed (`site.tscn`, `site_backdrop.tscn`): the differing lines, and how
many of them are `add_uv2 = true`. For the 12 scenes Godot saves (the presentation, `bake.tscn`, the standing
Empties' `site.tscn`): the differing lines before and after masking Godot's per-save ids -- node `unique_id`s,
resource `id="..."` values and the `ExtResource("...")` / `SubResource("...")` references that carry them -- which
roadmap 247 names as what remains of it. For `validation/report.json`: the leaves that differ. Prints and stops.

    python docs/cold_runs/cold_9313/masked_scenes.py [9312 9313]
"""
import json
import pathlib
import re
import sys

F = pathlib.Path(__file__).resolve().parents[3]
PKG = "workspaces/cold-{n}-ws/.level_factory/exports/LF_urban_row_001.portable-godot"
GODOT_SAVED = ["presentation/lux.applied.tscn", "bake.tscn"] + [
    "lot/%s/site.tscn" % e for e in ("gs_cornershop_c", "gs_cornershop_d", "gs_midrise_a", "gs_midrise_b",
                                      "gs_midrise_c", "gs_midrise_d", "gs_midrise_e", "gs_midrise_f",
                                      "gs_midrise_h", "gs_midrise_i")]
CHANGED = ["site.tscn", "site_backdrop.tscn"]
# REFUTED AND KEPT: the first run of this masked `unique_id = N` and the scenes write `unique_id=N`, no
# spaces, so it reported 964 lines of the presentation and every line of the Empties' scenes as unmasked --
# the instrument's miss, not a finding. The pattern now takes either spelling.
MASKS = [(re.compile(r'unique_id\s*=\s*-?\d+'), 'unique_id=#'),
         (re.compile(r'id="[^"]*"'), 'id="#"'),
         (re.compile(r'(Ext|Sub)Resource\("[^"]*"\)'), r'\1Resource("#")'),
         (re.compile(r'uid="uid://[^"]*"'), 'uid="#"')]


def lines(p):
    return p.read_text(encoding="utf-8").split("\n")


def differing(a, b):
    if len(a) != len(b):
        return None
    return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]


def masked(line):
    for pat, rep in MASKS:
        line = pat.sub(rep, line)
    return line


def flat(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flat(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from flat(v, p + "[" + str(i) + "]")
    else:
        yield p, o


def main():
    a, b = (sys.argv[1], sys.argv[2]) if len(sys.argv) == 3 else ("9312", "9313")
    pa, pb = F / PKG.format(n=a), F / PKG.format(n=b)
    print("== the two scenes 0.212.0 changed: differing lines, and how many are the UV2 mark")
    for rel in CHANGED:
        la, lb = lines(pa / rel), lines(pb / rel)
        marks_a = sum(1 for l in la if l == "add_uv2 = true")
        marks_b = sum(1 for l in lb if l == "add_uv2 = true")
        rest_a = [l for l in la if l != "add_uv2 = true"]
        rest_b = [l for l in lb if l != "add_uv2 = true"]
        print("  %-34s lines %d/%d  add_uv2 lines %d/%d  with those lines removed: %s"
              % (rel, len(la), len(lb), marks_a, marks_b,
                 "identical" if rest_a == rest_b else "%d lines differ" % len(differing(rest_a, rest_b) or [-1])))
    print("== the 12 scenes Godot saves: differing lines before and after the per-save-id mask")
    for rel in GODOT_SAVED:
        la, lb = lines(pa / rel), lines(pb / rel)
        d = differing(la, lb)
        if d is None:
            print("  %-34s lines %d/%d  (line counts differ; not masked)" % (rel, len(la), len(lb)))
            continue
        after = [i for i in d if masked(la[i]) != masked(lb[i])]
        print("  %-34s lines %d/%d  differing %d  after the mask %d" % (rel, len(la), len(lb), len(d), len(after)))
        for i in after[:3]:
            print("      %d: %s\n         %s" % (i + 1, la[i][:110], lb[i][:110]))
    print("== validation/report.json: leaves that differ")
    ra = dict(flat(json.loads((pa / "validation/report.json").read_text(encoding="utf-8"))))
    rb = dict(flat(json.loads((pb / "validation/report.json").read_text(encoding="utf-8"))))
    d = [k for k in sorted(set(ra) | set(rb)) if ra.get(k) != rb.get(k)]
    print("  %d leaves: %s" % (len(d), ", ".join(d[:12])[:300]))
    for k in d[:4]:
        print("      %s: %r -> %r" % (k[:60], str(ra.get(k))[:50], str(rb.get(k))[:50]))


if __name__ == "__main__":
    main()
