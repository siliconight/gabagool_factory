"""Gather the 2026-10-20 review's frames into a page folder's img/, as 1280-wide JPEGs. Every source is a frame shot today
with tools/look_shots.py from a walk copy (tools/walk_export.py) of a cold run's package, or a cold run's own record.
Prints what it copied and stops; a missing source fails.

    python collect_frames.py <page dir>
"""
import pathlib
import sys

from PIL import Image

F = pathlib.Path(__file__).resolve().parents[3]
R = F / "_scratch" / "review"
SOURCES = {
    "desk_before": R / "office_9349" / "desk_rdd247d9b_6.png",
    "desk_after": R / "office_9350" / "desk_rdd247d9b_6.png",
    "cubicles_before": R / "office_9349" / "cubicles_e_2.png",
    "cubicles_after": R / "office_9350" / "cubicles_e_2.png",
    "phone0_before": R / "phones_9350" / "payphone_0L3.png",
    "phone0_after": R / "phones_9351" / "payphone_0L3.png",
    "phone2_before": R / "phones_9350" / "payphone_2R3.png",
    "phone2_after": R / "phones_9351" / "payphone_2R3.png",
    "hatch_before": R / "hatchi_9348" / "INSPECT_studio_hatch_from_above.png",
    "hatch_after": R / "hatchi_9352" / "INSPECT_studio_hatch_from_above.png",
    "hatch_side_before": R / "hatchi_9348" / "INSPECT_studio_hatch_hinge_side.png",
    "hatch_side_after": R / "hatchi_9352" / "INSPECT_studio_hatch_hinge_side.png",
    "spawn_morning": R / "tod_9353" / "spawn.png",
    "spawn_noon": R / "tod_9354" / "spawn.png",
    "extraction_morning": R / "tod_9353" / "extraction.png",
    "extraction_noon": R / "tod_9354" / "extraction.png",
    "fronts": F / "docs" / "cold_runs" / "cold_9348" / "fronts_9282_vs_9348.jpg",
}

page = pathlib.Path(sys.argv[1]).resolve()
(page / "img").mkdir(parents=True, exist_ok=True)
missing = [k for k, p in SOURCES.items() if not p.is_file()]
if missing:
    raise SystemExit("MISSING sources: " + ", ".join("%s (%s)" % (k, SOURCES[k]) for k in missing))
for key, p in SOURCES.items():
    im = Image.open(p).convert("RGB")
    if im.width > 1280:
        im = im.resize((1280, round(im.height * 1280 / im.width)))
    out = page / "img" / (key + ".jpg")
    im.save(out, quality=84)
    print("%-20s %s -> %s %dx%d" % (key, p.relative_to(F), out.name, im.width, im.height))
