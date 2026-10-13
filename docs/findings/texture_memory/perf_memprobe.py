"""Where, in the fixed-station harness, a package's texture memory grows (roadmap 238; Level Factory 0.199.0).

    python docs/findings/texture_memory/perf_memprobe.py <imported package copy> [--no-shadow-atlases]

Level Factory 0.199.0's harness reads the engine's memory once every station is warm. On cold run 9276's
package it read 76.0 MiB of textures, where `texture_split_probe.gd`'s `mission` arm read 65.6 on the same
copy. This writes a copy of the harness's probe into the package as `perf_memprobe.gd`, with three prints
added -- the main scene in and 60 frames on; the probe's camera at the first station with a frame drawn;
every station warm -- and runs it as `perf_stations_run.py` runs its probe, windowed (headless draws
nothing). `--no-shadow-atlases` writes an `override.cfg` for the run setting the positional shadow atlas to 0
and the directional to 256, the `-patlas`/`-datlas` arms of `texture_split_probe.gd`. Whatever it writes into
the package it removes. Prints the three readings and stops.
"""
import pathlib
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
PROBE = F / "level_factory" / "tools" / "perf_stations.gd"
POINTS = [  # (where, before or after it, what the print says)
    ("\troot.add_child(scene)\n\tawait _settle(60)\n", "after", "the main scene in, 60 frames on"),
    ("\tvar cap: int = int(ProjectSettings.get_setting(\n"
     "\t\t\"rendering/limits/opengl/max_lights_per_object\", 8))\n", "before",
     "the probe's camera at station 0, a frame drawn"),
    ("\t_geometry[\"cold_worst_ms\"] = cold_worst\n", "after", "every station warmed"),
]
OVERRIDE = ("[rendering]\n\nlights_and_shadows/positional_shadow/atlas_size=0\n"
            "lights_and_shadows/directional_shadow/size=256\n")


def _mark(label):
    return ("\tprint(\"[memprobe] %s: textures %%.1f MiB, buffers %%.1f MiB\" %% ["
            "Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0, "
            "Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED) / 1048576.0])\n" % label)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pkg = pathlib.Path(sys.argv[1]).resolve()
    if not (pkg / ".godot").is_dir():
        sys.exit("UNKNOWN SHAPE: %s has no .godot -- import the copy first" % pkg)
    src = PROBE.read_text(encoding="utf-8")
    for where, side, label in POINTS:
        if src.count(where) != 1:
            sys.exit("UNKNOWN SHAPE: %d of %r in %s" % (src.count(where), where[:40], PROBE))
        src = src.replace(where, where + _mark(label) if side == "after" else _mark(label) + where)
    made = [pkg / "perf_memprobe.gd", pkg / "perf_memprobe.json"]
    (pkg / "perf_memprobe.gd").write_text(src, encoding="utf-8", newline="\n")
    if "--no-shadow-atlases" in sys.argv:
        if (pkg / "override.cfg").exists():
            sys.exit("UNKNOWN SHAPE: %s already has an override.cfg" % pkg)
        (pkg / "override.cfg").write_text(OVERRIDE, encoding="utf-8", newline="\n")
        made.append(pkg / "override.cfg")
    try:
        r = subprocess.run([GODOT, "--path", str(pkg), "--script", "res://perf_memprobe.gd", "--",
                            "--out", "res://perf_memprobe.json"], capture_output=True, text=True,
                           timeout=900, stdin=subprocess.DEVNULL)
    finally:
        for p in made:
            if p.exists():
                p.unlink()
    lines = [l for l in r.stdout.splitlines() if l.startswith("[memprobe]")]
    print("%s%s, exit %d" % (pkg, " (shadow atlases shrunk)" if "--no-shadow-atlases" in sys.argv else "",
                             r.returncode))
    for l in lines:
        print(l)
    if len(lines) != len(POINTS):
        print("UNKNOWN SHAPE: %d of the %d readings printed" % (len(lines), len(POINTS)))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
