"""The High look without the sun's real-time shadows (roadmap 243; the walker, 2026-10-12: "yes, test the
High look without sun shadows").

    python docs/findings/lux_tiers/sun_variants.py            # the arms, their frames and the sheet
    python docs/findings/lux_tiers/sun_variants.py --price    # and one Level Factory station pass an arm
    python docs/findings/lux_tiers/sun_variants.py --arms B2  # only the named arms (comma-separated)

Cold run 9264's level runs Lux's High tier under the `blue_hour` preset: a sun 4 degrees up, its shadows
on. Lux builds that sun at run time (`LuxLighting.ensure_sun`, a plain DirectionalLight3D, bake mode
dynamic), so the lightmap holds only its bounce: its light and its shadows are drawn live every frame,
and the tiers measured (`tier_frames.py`) put most of High's 2,100 extra draws a heading there. Arms,
each a copy of the package:

  control   `tools/lux_rebake.py` with nothing changed: the bake the export ran, again. Its frames must
            match the shipped High frames (`_scratch/frames_lux_tiers/shots_high/`), or the re-bake is not
            the export's and arm B says nothing
  A         the preset's `sun_shadows` false and NOTHING re-baked: the sun still lit live, unshadowed
  B         the sun built as a BAKED light (`light_bake_mode = BAKE_STATIC` in the vendored
            `ensure_sun`), its live shadows off, re-baked by `lux_rebake.py`, the preset's
            `sun_shadows` turned off BEFORE the bake. RETRACTED, KEPT: this said "REFUTED AS A TEST OF
            THE QUESTION: the lightmapper honours a light's shadow flag, so the sun baked unoccluded
            and B came out as flat as A". B's frames were in no table then; measured since, B and B2
            are one picture within a re-bake's noise (1.6 to 2.5 levels, at most 0.01 % of pixels
            over 16) and each differs from A by 3.3 to 11.7 -- the flag does not change the bake
  B2        the same baked sun with its shadows ON for the bake, and `sun_shadows` turned off in the
            baked copy's preset afterwards: the lightmap carries the sun's light and its shadows on
            everything static, and no frame redraws them live; the live sun lights only what moves

Each arm is shot at `tier_frames.py`'s stations; the sheet sets High (shipped), A, B and Low side by
side, a row a station, from these frames and the tier run's. Copies go to `_scratch/sun_variants/` and
are removed; frames stay under `_scratch/frames_sun_variants/`. It measures and stops.
"""
import pathlib
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
PKG = F / "workspaces" / "cold-9264-ws" / ".level_factory" / "exports" / "LF_restaurant_row_001.portable-godot"
SCR = F / "_scratch" / "sun_variants"
FR = F / "_scratch" / "frames_sun_variants"
TIER_FR = F / "_scratch" / "frames_lux_tiers"
OUT = F / "docs" / "findings" / "lux_tiers"
STATIONS = ["--station", "line:-60,1.8,25.5,20,6.0,26.0",
            "--station", "corner:65,1.8,16,80.6,6.0,20",
            "--station", "up:-31.7,1.8,25.5,-15.1,9.0,27.27"]
SHOTS = ("line", "corner", "up", "spawn", "objective", "elev_N")
PRESET = "runtime/lux/presets/blue_hour.tres"
LIGHTING = "runtime/lux/runtime/lux_lighting.gd"
SUN_OLD = '\tsun.name = &"LuxSun"\n'
SUN_NEW = ('\tsun.name = &"LuxSun"\n'
           "\t# THE SUN BAKED (a variant, docs/findings/lux_tiers/sun_variants.py)\n"
           "\tsun.light_bake_mode = Light3D.BAKE_STATIC\n")


def _edit(path, old, new):
    raw = path.read_bytes()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if text.count(old) != 1:
        sys.exit("UNKNOWN SHAPE: %d of %r in %s" % (text.count(old), old[:40], path))
    path.write_bytes(text.replace(old, new).replace("\n", eol).encode("utf-8"))


def _shoot(arm, project):
    with open(FR / ("shots_%s.json" % arm), "w") as out, open(FR / ("shots_%s.err" % arm), "w") as err:
        rc = subprocess.run([sys.executable, str(F / "tools" / "look_shots.py"), str(project), "--scene",
                             "mission.tscn", "--out", str(FR / ("shots_" + arm)), "--json"] + STATIONS,
                            stdout=out, stderr=err, stdin=subprocess.DEVNULL, timeout=1800).returncode
    print("%-8s shots exit %d" % (arm, rc), flush=True)
    if "--price" in sys.argv:
        rep = OUT / ("perf_sun_%s.json" % arm)
        rc = subprocess.run([sys.executable, str(F / "level_factory" / "tools" / "perf_stations_run.py"),
                             str(project), "--json", str(rep)], capture_output=True, text=True,
                            stdin=subprocess.DEVNULL, timeout=1800).returncode
        print("%-8s price pass exit %d (%s)" % (arm, rc, "measured" if rep.exists() else "NOT MEASURED"),
              flush=True)


def _rebake(src, dest, log):
    with open(log, "w") as fh:
        rc = subprocess.run([sys.executable, str(F / "tools" / "lux_rebake.py"), str(src), str(dest)],
                            stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=3600).returncode
    tail = log.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-1:]
    print("rebake %s exit %d: %s" % (dest.name, rc, tail[0] if tail else ""), flush=True)
    if rc != 0:
        sys.exit("the re-bake failed; see %s" % log)


def main():
    arms = ("control", "A", "B", "B2")
    for i, a in enumerate(sys.argv):
        if a == "--arms":
            arms = tuple(sys.argv[i + 1].split(","))
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    FR.mkdir(parents=True, exist_ok=True)
    if "control" in arms:   # the export's bake again, nothing changed
        _rebake(PKG, SCR / "control", FR / "rebake_control.log")
        _shoot("control", SCR / "control")
        shutil.rmtree(SCR / "control")
    if "A" in arms:         # the sun unshadowed, nothing re-baked
        shutil.copytree(PKG, SCR / "A")
        _edit(SCR / "A" / PRESET, "sun_shadows = true\n", "sun_shadows = false\n")
        _shoot("A", SCR / "A")
        shutil.rmtree(SCR / "A")
    if "B" in arms:         # the sun baked with its shadows already off (see the docstring)
        shutil.copytree(PKG, SCR / "B_src")
        _edit(SCR / "B_src" / LIGHTING, SUN_OLD, SUN_NEW)
        _edit(SCR / "B_src" / PRESET, "sun_shadows = true\n", "sun_shadows = false\n")
        _rebake(SCR / "B_src", SCR / "B", FR / "rebake_B.log")
        shutil.rmtree(SCR / "B_src")
        _shoot("B", SCR / "B")
        shutil.rmtree(SCR / "B")
    if "B2" in arms:        # the sun baked WITH its shadows, then its live shadows off
        shutil.copytree(PKG, SCR / "B2_src")
        _edit(SCR / "B2_src" / LIGHTING, SUN_OLD, SUN_NEW)
        _rebake(SCR / "B2_src", SCR / "B2", FR / "rebake_B2.log")
        shutil.rmtree(SCR / "B2_src")
        _edit(SCR / "B2" / PRESET, "sun_shadows = true\n", "sun_shadows = false\n")
        _shoot("B2", SCR / "B2")
        shutil.rmtree(SCR / "B2")
    shutil.rmtree(SCR, ignore_errors=True)
    # the control's frames against the shipped High frames
    from PIL import Image, ImageChops
    for shot in SHOTS:
        a = Image.open(TIER_FR / "shots_high" / (shot + ".png")).convert("RGB")
        b = Image.open(FR / "shots_control" / (shot + ".png")).convert("RGB")
        diff = ImageChops.difference(a, b).convert("L")
        hist = diff.histogram()
        n = sum(hist)
        mean = sum(i * c for i, c in enumerate(hist)) / n
        over = sum(hist[17:]) / n * 100.0
        print("control vs shipped High, %-9s mean abs diff %.3f, pixels over 16 levels %.3f %%" % (shot, mean, over))
    args = []
    for shot in SHOTS:
        args += ["High %s=%s" % (shot, TIER_FR / "shots_high" / (shot + ".png")),
                 "A sun unshadowed %s=%s" % (shot, FR / "shots_A" / (shot + ".png")),
                 "B2 sun baked with its shadows %s=%s" % (shot, FR / "shots_B2" / (shot + ".png")),
                 "Low %s=%s" % (shot, TIER_FR / "shots_low" / (shot + ".png"))]
    subprocess.run([sys.executable, str(F / "docs" / "findings" / "edge_menu" / "sheet.py"),
                    str(OUT / "sun_variants.png"), "4"] + args, check=True)
    print("sheet: docs/findings/lux_tiers/sun_variants.png")


if __name__ == "__main__":
    main()
