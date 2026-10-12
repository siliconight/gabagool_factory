"""Reproduce the light bake's first import on a copy, with the engine's log kept.

`pin_phase_probe.py` put the loss in one step of a real export: the light bake's first `--import`
(after `mark_imports` sets static lightmaps on every model's sidecar) turned 86 of 415 pinned
sidecars under `_tex/` into Godot's defaults, and nothing before or after it moved one. This
repeats that step's preparation on a stripped copy -- Level Factory's own `_write_import_sidecars`,
then `light_bake.mark_imports`, `add_primitive_uv2`, `mark_steady_rigs` and the bake scene, exactly
the bake's order -- runs the one `--import` with `--verbose`, counts the pins, and keeps the
engine's output beside the copy for reading. It measures and prints.

    python docs/findings/texture_pins/pin_bake_import_probe.py <package dir>
"""
import os
import shutil
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path  # noqa: E402

from packages.exporting import export as E  # noqa: E402
from packages.exporting import light_bake as L  # noqa: E402
from pin_step_probe import census  # noqa: E402

G = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
X = os.path.join(F, "_scratch", "texture_pins", "bake_import")


def main():
    src = os.path.abspath(sys.argv[1])
    shutil.rmtree(X, ignore_errors=True)
    os.makedirs(X)
    p = Path(X) / "pkg"
    shutil.copytree(src, p)
    shutil.rmtree(p / ".godot", ignore_errors=True)
    for r, _, fs in os.walk(p):
        for f in fs:
            if f.endswith(".import"):
                os.remove(os.path.join(r, f))
    E._write_import_sidecars(p, G)
    print("after the sidecar step:", census(p), flush=True)
    before = {}
    for r, _, fs in os.walk(p):
        if os.path.basename(r) == "_tex":
            for f in fs:
                if f.endswith(".png.import"):
                    q = os.path.join(r, f)
                    before[q] = open(q, encoding="utf-8").read()
    L.mark_imports(p)
    L.add_primitive_uv2(p)
    L.mark_steady_rigs(p / L.PRESENTATION)
    (p / L.BAKE_SCENE).write_text(L.bake_scene_text(), encoding="utf-8", newline="\n")
    t0 = time.time()
    done = subprocess.run([G, "--headless", "--verbose", "--path", str(p), "--import"],
                          stdin=subprocess.DEVNULL, capture_output=True, timeout=1800)
    log = Path(X) / "bake_import.log"
    log.write_bytes((done.stdout or b"") + (done.stderr or b""))
    print("the bake's first --import, %.1f s, exit %s: %s" % (time.time() - t0, done.returncode, census(p)), flush=True)
    changed = [q for q, text in before.items() if open(q, encoding="utf-8").read() != text]
    print("%d of %d _tex/ sidecars rewritten by it; the log is %s" % (len(changed), len(before), log))
    with open(Path(X) / "rewritten.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(os.path.relpath(q, p).replace("\\", "/") for q in sorted(changed)) + "\n")
    for q in sorted(changed)[:5]:
        print("    e.g. " + os.path.relpath(q, p).replace("\\", "/"))


if __name__ == "__main__":
    main()
