"""Price the sun variants against the level as it ships (roadmap 243; `sun_variants.py` made them).

    python docs/findings/lux_tiers/sun_price.py

Level Factory's fixed-station harness through `docs/findings/horizon_glow/price_glow.py`, the edge
menu's comparison: control_1 (cold run 9264's package as shipped, High), the subject, control_2 (the
shipped package again), per heading against the two controls' mean, the controls' spread the noise
floor. Two subjects, each built the way `sun_variants.py` builds it:

  A    the shipped package with the preset's `sun_shadows` off, nothing re-baked
  B2   the sun built BAKE_STATIC, re-baked by `tools/lux_rebake.py` WITH its shadows, then the preset's
       `sun_shadows` off: the lightmap carries the sun and its shadows, no frame redraws them

A re-baked subject carries re-bake noise besides the change (`sun_variants.py`'s control: a re-bake with
nothing changed reads 1.6 to 2.4 levels from the shipped frames); draw counts it cannot move. Reports go
to `price_sun_<arm>/` beside this file; the copies to `_scratch/sun_price/`, removed after. Nothing
else runs beside a price.
"""
import pathlib
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sun_variants as SV   # noqa: E402  (the same edits, the same rebake)

SCR = F / "_scratch" / "sun_price"
OUT = pathlib.Path(__file__).resolve().parent


def _price(subject, name):
    out = OUT / ("price_sun_" + name)
    out.mkdir(exist_ok=True)
    with open(out / "price.txt", "w") as fh:
        rc = subprocess.run([sys.executable, str(F / "docs" / "findings" / "horizon_glow" / "price_glow.py"),
                             str(SCR / "control"), str(subject), str(out)], stdout=fh, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, timeout=7200).returncode
    print("%s price exit %d" % (name, rc), flush=True)
    for line in (out / "price.txt").read_text(encoding="utf-8").strip().splitlines()[-4:]:
        print("   " + line, flush=True)


def main():
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    shutil.copytree(SV.PKG, SCR / "control")
    shutil.copytree(SV.PKG, SCR / "A")
    SV._edit(SCR / "A" / SV.PRESET, "sun_shadows = true\n", "sun_shadows = false\n")
    _price(SCR / "A", "A")
    shutil.rmtree(SCR / "A")
    shutil.copytree(SV.PKG, SCR / "B2_src")
    SV._edit(SCR / "B2_src" / SV.LIGHTING, SV.SUN_OLD, SV.SUN_NEW)
    SV._rebake(SCR / "B2_src", SCR / "B2", SCR / "rebake_B2.log")
    shutil.rmtree(SCR / "B2_src")
    SV._edit(SCR / "B2" / SV.PRESET, "sun_shadows = true\n", "sun_shadows = false\n")
    _price(SCR / "B2", "B2")
    shutil.rmtree(SCR, ignore_errors=True)


if __name__ == "__main__":
    main()
