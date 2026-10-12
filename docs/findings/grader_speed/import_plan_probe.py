"""REFUTED, KEPT -- read this first. This probe found the two plans' sidecars the same once uids were
set aside, and the real export with the PLAN applied failed the greybox-skin gate (105 slab surfaces
left greybox, the Empties merged to 148 meshes instead of 236): the light bake's re-import is when
`zoo_worldskin.gd` skins the models with the packs imported, and a sidecar does not record what an
import script did. An equivalence for an import plan has to be read off the imported RESULT (the
greybox census, the merge, the bake's users), not off the sidecars. `README.md` says the rest.

Can the export import its package once where it imports it three times?

Profiled (`README.md`): the sidecar step imports everything with Godot's defaults, rewrites the
models' sidecars (embedded images, mode 3) and the shared textures' pins, wipes the cache and
imports everything again; the light bake then re-imports every model for its lightmap UVs, and that
pass imports the shared textures 1,843 times. The package's `project.godot` already sets importer
DEFAULTS for models (`[importer_defaults] scene`, the worldskin script), so two of those settings
could be defaults instead of rewrites. Two arms on stripped copies of a shipped package (every
`.import` and the cache removed, the bake's own files removed), one at a time:

  CURRENT  Level Factory's `_write_import_sidecars` as it is, then `mark_imports` and the bake's
           first `--import`
  PLAN     the model defaults gain `gltf/embedded_image_handling: 3` and `meshes/light_baking: 2`;
           one `--import`; the shared and sign pins; a second `--import` WITHOUT the cache wiped
           (so only what changed re-imports); then `mark_imports` and the bake's first `--import`

It prints each step's wall time, the pins census, and every sidecar that differs between the arms
once uids are set aside -- the sidecars are what ships. It measures and prints.

    python docs/findings/grader_speed/import_plan_probe.py <package dir>
"""
import collections
import os
import re
import shutil
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
sys.path.insert(0, os.path.join(F, "docs", "findings", "texture_pins"))
from pathlib import Path  # noqa: E402

from packages.exporting import export as E  # noqa: E402
from packages.exporting import light_bake as L  # noqa: E402
from pin_step_probe import census  # noqa: E402

G = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
X = os.path.join(F, "_scratch", "import_plan")
BAKE_OUT = ("bake.exr", "bake.exr.import", "bake.lmbake", "bake.tscn")
UID = re.compile(r'^uid="uid://[a-z0-9]+"\s*$', re.M)


def _import(p):
    t0 = time.time()
    subprocess.run([G, "--headless", "--path", str(p), "--import"], stdin=subprocess.DEVNULL,
                   capture_output=True, timeout=1800)
    return time.time() - t0


def _stripped(src, name):
    p = Path(X) / name
    shutil.copytree(src, p)
    shutil.rmtree(p / ".godot", ignore_errors=True)
    for r, _, fs in os.walk(p):
        for f in fs:
            if f.endswith(".import"):
                os.remove(os.path.join(r, f))
    for f in BAKE_OUT:
        (p / f).unlink(missing_ok=True)
    return p


def _spawned(p):
    return [g.relative_to(p).as_posix() for g in p.rglob("prop_cruiser_*.glb")]


def current(src):
    p = _stripped(src, "current")
    t0 = time.time()
    E._write_import_sidecars(p, G)
    side = time.time() - t0
    L.mark_imports(p, _spawned(p))
    bake1 = _import(p)
    print("CURRENT: sidecar step %.1f s (two passes, the cache wiped between); the bake's first import "
          "%.1f s; total %.1f s; pins %s" % (side, bake1, side + bake1, census(p)), flush=True)
    return p


def plan(src):
    p = _stripped(src, "plan")
    proj = p / "project.godot"
    text = proj.read_text(encoding="utf-8")
    old = '"import_script/path": "res://zoo_worldskin.gd"\n'
    assert text.count(old) == 1, "the model defaults are not where this probe read them"
    proj.write_text(text.replace(old, '"import_script/path": "res://zoo_worldskin.gd",\n'
                                      '"gltf/embedded_image_handling": 3,\n'
                                      '"meshes/light_baking": 2\n'), encoding="utf-8")
    p1 = _import(p)
    pins = E._pin_shared_texture_imports(p) + E._pin_sign_texture_imports(p)
    rewrote = 0
    for sidecar in p.rglob("*.glb.import"):
        if "gltf/embedded_image_handling=3" not in sidecar.read_text(encoding="utf-8"):
            rewrote += 1
    p2 = _import(p)
    L.mark_imports(p, _spawned(p))
    bake1 = _import(p)
    print("PLAN: first import %.1f s; %d sidecars pinned, %d model sidecars NOT at mode 3; second "
          "import (no wipe) %.1f s; the bake's first import %.1f s; total %.1f s; pins %s"
          % (p1, pins, rewrote, p2, bake1, p1 + p2 + bake1, census(p)), flush=True)
    return p


def sidecars(root):
    out = {}
    for r, _, fs in os.walk(root):
        if ".godot" in r:
            continue
        for f in fs:
            if f.endswith(".import"):
                q = os.path.join(r, f)
                out[os.path.relpath(q, root).replace("\\", "/")] = UID.sub("", open(q, encoding="utf-8").read())
    return out


def main():
    src = os.path.abspath(sys.argv[1])
    shutil.rmtree(X, ignore_errors=True)
    os.makedirs(X)
    a, b = current(src), plan(src)
    sa, sb = sidecars(a), sidecars(b)
    differ = sorted(k for k in set(sa) & set(sb) if sa[k] != sb[k])
    print("sidecars: %d and %d; only one side: %s; different once uids are set aside: %d"
          % (len(sa), len(sb), sorted(set(sa) ^ set(sb))[:5], len(differ)))
    keys = collections.Counter()
    for k in differ:
        la = dict(ln.partition("=")[::2] for ln in sa[k].splitlines() if "=" in ln)
        lb = dict(ln.partition("=")[::2] for ln in sb[k].splitlines() if "=" in ln)
        for key in set(la) | set(lb):
            if la.get(key) != lb.get(key):
                keys[key] += 1
    print("keys that differ, over those sidecars:", dict(keys.most_common(12)))
    for k in differ[:5]:
        print("    e.g. " + k)
    shutil.rmtree(X, ignore_errors=True)


if __name__ == "__main__":
    main()
