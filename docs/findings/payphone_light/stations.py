"""A caller's camera for every payphone lamp a walk project spawned.

    python stations.py <walk project> [--out D]

Reads `presentation/lux.applied.tscn` and finds every rig the fixture spawner
stood for a `LuxEmit_payphone_hood` marker (`Spawned_payphone_hood*`, under
`LuxFixtureLights`). The rig stands on the marker's global transform
(`LuxFixtureSpawner.spawn`), so its basis is the payphone's own: local +Z is
the caller's side (Zoo's -Y through the glTF export), local +Y up.

For each, in Godot world metres, Y up:
- the lamp: the rig's origin;
- the instrument's middle: the lamp plus (0.04, -0.961, -0.288) in the
  payphone's axes, from Zoo 1.89.0's layout at the default slot (the lamp at
  0, 2.211, -0.177 from the ground under the slot's middle; the instrument's
  face at y 0.111 and its middle 1.25 up, 0.04 right of the middle);
- the eye: 1.4 m out from the instrument's face along the caller's side, at
  1.6 m over the ground the payphone stands on (the lamp's height less 2.211).

Prints one `--station NAME:EX,EY,EZ,TX,TY,TZ` line per payphone and what it
read. Refuses a scene with no `LuxFixtureLights`, a container that is not at
the identity (then a rig's transform would not be world), or no payphone rig.
Godot writes a Transform3D's basis as ROWS: the axis vectors are its columns.
"""
import argparse
import pathlib
import re

SCENE = pathlib.Path("presentation") / "lux.applied.tscn"
NODE = re.compile(r'^\[node name="([^"]+)" type="[^"]+" parent="([^"]*)"[^\]]*\]$', re.M)
XFORM = re.compile(r"^transform = Transform3D\(([^)]*)\)$", re.M)
LAMP_TO_INST = (0.04, -0.961, -0.288)
LAMP_DROP = 2.211
EYE_OUT = 1.4
EYE_UP = 1.6


def blocks(text):
    """[(name, parent, body)] for every node, in order."""
    out = []
    marks = list(NODE.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((m.group(1), m.group(2), text[m.end():end]))
    return out


def xform(body):
    m = XFORM.search(body)
    if not m:
        return None
    v = [float(x) for x in m.group(1).split(",")]
    assert len(v) == 12, v
    rows = (v[0:3], v[3:6], v[6:9])
    cols = [tuple(rows[r][c] for r in range(3)) for c in range(3)]
    return cols, tuple(v[9:12])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    a = ap.parse_args()
    text = (pathlib.Path(a.project) / SCENE).read_text(encoding="utf-8")
    bl = blocks(text)
    box = [b for b in bl if b[0] == "LuxFixtureLights"]
    if len(box) != 1:
        raise SystemExit(f"{len(box)} LuxFixtureLights containers; wanted 1")
    t = xform(box[0][2])
    if t is not None and (t[1] != (0.0, 0.0, 0.0) or t[0] != [(1, 0, 0), (0, 1, 0), (0, 0, 1)]):
        raise SystemExit(f"LuxFixtureLights is not at the identity: {t}")
    rigs = [b for b in bl if b[0].startswith("Spawned_payphone_hood") and b[1] == "LuxFixtureLights"]
    if not rigs:
        raise SystemExit("no Spawned_payphone_hood rig under LuxFixtureLights")
    for name, _parent, body in rigs:
        t = xform(body)
        if t is None:
            raise SystemExit(f"{name}: no transform")
        (x_ax, y_ax, z_ax), o = t
        inst = tuple(o[k] + x_ax[k] * LAMP_TO_INST[0] + y_ax[k] * LAMP_TO_INST[1] + z_ax[k] * LAMP_TO_INST[2]
                     for k in range(3))
        ground = o[1] - LAMP_DROP
        flat = (z_ax[0], 0.0, z_ax[2])
        n = (flat[0] ** 2 + flat[2] ** 2) ** 0.5
        eye = (inst[0] + flat[0] / n * EYE_OUT, ground + EYE_UP, inst[2] + flat[2] / n * EYE_OUT)
        tag = name.replace("Spawned_", "").replace("payphone_hood", "pp")
        print(f"# {name}: lamp ({o[0]:.3f}, {o[1]:.3f}, {o[2]:.3f}), caller side "
              f"({z_ax[0]:+.3f}, {z_ax[1]:+.3f}, {z_ax[2]:+.3f}), ground {ground:.3f}")
        print(f"--station {tag}:{eye[0]:.3f},{eye[1]:.3f},{eye[2]:.3f},{inst[0]:.3f},{inst[1]:.3f},{inst[2]:.3f}")


if __name__ == "__main__":
    main()
