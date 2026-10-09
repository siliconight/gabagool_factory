"""Every library sign width x every name: the cap height each version sets, in cm.

    python sign_table.py <zoo_root> <out.json>

Run once against 1.89.0 (the repo) and once against 1.90.0 (the patched copy). Prints what it
measured: the version, how many cells, and how many did not set.
"""
import json
import sys

sys.path.insert(0, sys.argv[1])
from zoo_keeper.core import club_names as CN  # noqa: E402
from zoo_keeper.core import price_pylon_forms as PY  # noqa: E402
from zoo_keeper.core import storefront_names as SN  # noqa: E402
from zoo_keeper.core import card_art as CA  # noqa: E402

#: measured off deli_counter/build/*.lights.json on 2026-10-09: 95 signs, all 0.6 m tall
WIDTHS = (2.0, 2.05, 2.2, 2.3, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 4.8, 5.0)
H = 0.6
NEW = hasattr(SN, "DENSITY")
civic = {t for kind, _m, names in SN.KINDS if kind in SN.CIVIC for t in names}
texts = SN.all_strings() + list(CN.NAMES) + [str(SN.NUMBERS[1])]
rows = []
for w in WIDTHS:
    for t in texts:
        if NEW:
            tx = SN.TEXEL * SN.DENSITY
            voice = "civic" if t in civic else "shop"
            face, cap, lines = SN.layout(t, round(w * tx) - 10 * SN.DENSITY - 2 * SN.OUTLINE,
                                         round(H * tx) - 14 * SN.DENSITY - 2 * SN.OUTLINE, voice)
            # the cap in cm: px / (px a metre) * 100
            rows.append({"w": w, "text": t, "face": face, "cap_cm": round(cap / tx * 100, 2),
                         "lines": len(lines)})
        else:
            from zoo_keeper.core import pixel_type as pt
            tx = SN.TEXEL
            face = PY.HEAD_FACE
            s, lines = SN.layout(t, round(w * tx) - 10, round(H * tx) - 14, face)
            if not s:
                face = "m5x7"
                s, lines = SN.layout(t, round(w * tx) - 10, round(H * tx) - 14, face)
            cap_px = len(pt.trim(pt.render("H", s, face))) if s else 0
            rows.append({"w": w, "text": t, "face": face, "cap_cm": round(cap_px / tx * 100, 2),
                         "lines": len(lines)})
# the atlas a 2.8 m sign builds, face and edge tiles, as sign_box asks for it
spec = {"kind": "storefront_sign", "w_m": 2.8, "h_m": H, "text": "MOM THINKS I'M AT BINGO",
        "colours": PY.COLOURWAYS[0]}
edge = dict(spec, w_m=0.1, h_m=0.1, edge=True, text="")
if NEW:
    spec["voice"] = "shop"
atlas = CA.build_atlas({"face": spec, "edge": edge}, "SignBox_Face", smooth=NEW)
png = atlas["canvas"].png()
out = {"new": NEW, "rows": rows, "atlas": atlas["size"], "png_bytes": len(png)}
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
print("version", "1.90.0" if NEW else "1.89.0", "cells", len(rows),
      "unset", sum(1 for r in rows if not r["cap_cm"]), "atlas", atlas["size"], "png", len(png))
