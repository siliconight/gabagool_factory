"""What Lux's four quality tiers look like and cost on one level (roadmap 243; the walker, 2026-10-12, on
which tier a package should run: "didn't know we had this... not sure" -- shown, not decided).

    python docs/findings/lux_tiers/tier_frames.py            # the frames and the sheet
    python docs/findings/lux_tiers/tier_frames.py --price    # and one Level Factory station pass a tier

`LuxRoot.quality_tier` (0 High, 1 Medium, 2 Low, 3 Compatibility; `LuxQualityProfile.make_tier`) is
never set by any factory tool, so every package runs High. ONE copy of cold run 9264's package --
imported once, by the first shots -- with the tier written on the scene's LuxRoot node
(`presentation/lux.applied.tscn`, which `mission.tscn` loads through `bake.tscn`) and nothing else,
rewritten before each tier's shots; each tier shot by `tools/look_shots.py` at its derived cameras
(spawn, objective, extraction, the overview, the four elevations) and at three given ones on the main
street (`line`, `corner` and `up` of cold run 9263's wire stations). The sheet puts the tiers side by
side, a row a station. The copy is made under `_scratch/lux_tiers/` and removed; the frames stay under
`_scratch/frames_lux_tiers/`. (The first version made a copy a tier, and each fresh copy re-imported the
package's ~500 models before its first shot: about 13 minutes a tier. It was stopped after one.)

THE CONTROL that the dial is read: the tier changes post-processing, glow and sun shadows, which every
frame shows; frames identical across tiers would mean the scene's value never reached Lux, and the
sheet would say nothing. It measures and stops.
"""
import pathlib
import re
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
PKG = F / "workspaces" / "cold-9264-ws" / ".level_factory" / "exports" / "LF_restaurant_row_001.portable-godot"
SCR = F / "_scratch" / "lux_tiers"
FR = F / "_scratch" / "frames_lux_tiers"
OUT = F / "docs" / "findings" / "lux_tiers"
TIERS = (("high", 0), ("medium", 1), ("low", 2), ("compat", 3))
STATIONS = ["--station", "line:-60,1.8,25.5,20,6.0,26.0",
            "--station", "corner:65,1.8,16,80.6,6.0,20",
            "--station", "up:-31.7,1.8,25.5,-15.1,9.0,27.27"]
SHOTS = ("line", "corner", "up", "spawn", "objective", "overview", "elev_N")


def _tier(copy, n):
    """Write `quality_tier = n` on the LuxRoot node, replacing the line a previous tier wrote."""
    scene = copy / "presentation" / "lux.applied.tscn"
    text = scene.read_text(encoding="utf-8")
    text = re.sub(r"\nquality_tier = \d+(?=\n)", "", text)
    ids = re.findall(r'^\[ext_resource type="Script"[^\]]*path="[^"]*/lux_root\.gd" id="([^"]+)"\]', text, re.M)
    anchor = '\nscript = ExtResource("%s")' % ids[0] if len(ids) == 1 else None
    if anchor is None or text.count(anchor) != 1:
        sys.exit("UNKNOWN SHAPE: LuxRoot in %s" % scene)
    scene.write_text(text.replace(anchor, anchor + "\nquality_tier = %d" % n), encoding="utf-8", newline="\n")


def main():
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    FR.mkdir(parents=True, exist_ok=True)
    copy = SCR / "package"
    shutil.copytree(PKG, copy)
    for name, n in TIERS:
        _tier(copy, n)
        with open(FR / ("shots_%s.json" % name), "w") as out, open(FR / ("shots_%s.err" % name), "w") as err:
            rc = subprocess.run([sys.executable, str(F / "tools" / "look_shots.py"), str(copy), "--scene",
                                 "mission.tscn", "--out", str(FR / ("shots_" + name)), "--json"] + STATIONS,
                                stdout=out, stderr=err, stdin=subprocess.DEVNULL, timeout=1200).returncode
        print("%-7s shots exit %d" % (name, rc), flush=True)
        if "--price" in sys.argv:
            rep = OUT / ("perf_%s.json" % name)
            rc = subprocess.run([sys.executable, str(F / "level_factory" / "tools" / "perf_stations_run.py"),
                                 str(copy), "--json", str(rep)], capture_output=True, text=True,
                                stdin=subprocess.DEVNULL, timeout=1800).returncode
            print("%-7s price pass exit %d (%s)" % (name, rc, "measured" if rep.exists() else "NOT MEASURED"),
                  flush=True)
    shutil.rmtree(SCR, ignore_errors=True)
    args = []
    for shot in SHOTS:
        for name, _n in TIERS:
            args.append("%s %s=%s" % (name, shot, FR / ("shots_" + name) / (shot + ".png")))
    subprocess.run([sys.executable, str(F / "docs" / "findings" / "edge_menu" / "sheet.py"),
                    str(OUT / "tiers.png"), "4"] + args, check=True)
    print("sheet: docs/findings/lux_tiers/tiers.png")


if __name__ == "__main__":
    main()
