"""Does one `--import` pass leave shared textures without a sidecar?

Found while measuring Level Factory 0.181.0 (`docs/findings/grader_speed/`): in every export --
cold run 9248's own and two re-exports of it -- 65 to 77 of the package's 415 sidecars under
`_tex/` carried Godot's DEFAULTS (`mipmaps/generate=false`, `process/fix_alpha_border=true`)
where `export._pin_shared_texture_imports` pins the opposite, and which ones varied between
exports (48 flips between two exports of unchanged code). A defaulted sidecar looks like one Godot
wrote fresh, so the suspicion is that the export's FIRST import pass -- whose verification counts
models only (`occluders.unimported_models`) -- leaves some textures unimported, the pin step finds
no sidecar to pin, and the second pass writes defaults.

This copies a package three times, removes every `.import` sidecar and any `.godot` from each copy
(the state before the first pass, near enough: Lux's own shipped sidecars go too), runs ONE
`--import` on each, and counts the PNGs under `_tex/` left with no sidecar. It measures and prints.

    python docs/findings/texture_pins/pin_loss_probe.py <package dir>
"""
import os
import shutil
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
G = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
X = os.path.join(F, "_scratch", "texture_pins")


def tex_pngs(root):
    out = []
    for r, _, fs in os.walk(root):
        if os.path.basename(r) != "_tex":
            continue
        out += [os.path.join(r, f) for f in fs if f.endswith(".png")]
    return sorted(out)


def main():
    src = os.path.abspath(sys.argv[1])
    assert os.path.isfile(os.path.join(src, "project.godot")), src
    shutil.rmtree(X, ignore_errors=True)
    os.makedirs(X)
    missing_sets = []
    for trial in (1, 2, 3):
        p = os.path.join(X, "pkg_%d" % trial)
        shutil.copytree(src, p)
        shutil.rmtree(os.path.join(p, ".godot"), ignore_errors=True)
        removed = 0
        for r, _, fs in os.walk(p):
            for f in fs:
                if f.endswith(".import"):
                    os.remove(os.path.join(r, f))
                    removed += 1
        t0 = time.time()
        done = subprocess.run([G, "--headless", "--path", p, "--import"], stdin=subprocess.DEVNULL,
                              capture_output=True, timeout=1200)
        wall = time.time() - t0
        pngs = tex_pngs(p)
        missing = [os.path.relpath(q, p).replace("\\", "/") for q in pngs if not os.path.exists(q + ".import")]
        glbs = [os.path.join(r, f) for r, _, fs in os.walk(p) for f in fs if f.endswith(".glb")]
        glb_missing = [g for g in glbs if not os.path.exists(g + ".import")]
        print("trial %d: removed %d sidecars; one --import, exit %s, %.1f s; PNGs under _tex/ %d, "
              "left without a sidecar %d; GLBs %d, without %d"
              % (trial, removed, done.returncode, wall, len(pngs), len(missing), len(glbs), len(glb_missing)))
        for m in missing[:5]:
            print("    e.g. " + m)
        missing_sets.append(set(missing))
        shutil.rmtree(p, ignore_errors=True)
        sys.stdout.flush()
    common = set.intersection(*missing_sets) if missing_sets else set()
    union = set.union(*missing_sets) if missing_sets else set()
    print("left without a sidecar in every trial: %d; in at least one: %d" % (len(common), len(union)))


if __name__ == "__main__":
    main()
