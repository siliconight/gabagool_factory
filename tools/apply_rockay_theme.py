#!/usr/bin/env python3
"""Add the `rockay` theme to the factory: a coastal art-deco / hurricane-night
style on every Zoo species, plus the Pixelcoat `rockay` skin-library profile.

Idempotent. Run from the gabagool_factory root (or pass --zoo / --pixelcoat):

    python apply_rockay_theme.py \
        --zoo   zoo/zoo_keeper/genome/species \
        --pixelcoat pixelcoat/profiles

The Zoo `rockay` style is derived from each species' own `default` block with a
consistent transform (subtle cool/teal wet-night tint, +weathering for salt and
humidity, low ambient for a storm night, brighter emissive so neon reads). The
heavy visual identity is carried by the Pixelcoat textures (teal-glazed brick,
ocean-mirror facade, wavy glass, deco brass, terrazzo); these per-species styles
are the flat-fallback + tint layer under them.
"""
from __future__ import annotations
import argparse, json, os, glob

COLOR_MUL = [0.94, 0.99, 1.05]   # subtle cool/teal, wet-night
WEAR_ADD = 0.14                  # salt + humidity weathering
WEAR_MAX = 0.9
AMBIENT = 0.05                   # storm night, faint neon bounce
EMISSIVE_BOOST = 1.3             # neon pops at night

ROCKAY_THEME = {
    "theme": "rockay",
    "description": ("Rockay City coastal art-deco, hurricane night: teal-glazed "
        "exterior brick, polished casino concrete and terrazzo underfoot, deco "
        "brass fittings, ocean-mirror curtain-wall glass and wavy display glass, "
        "warm salt-worn stucco. Built for the Category 5 beachfront-casino mission."),
    "materials": {
        "brick": "brick_glazed_green",
        "concrete": "concrete_polished_casino",
        "glass": "glass_wavy",
        "glass_facade": "glass_facade_mirror_blue",
        "metal": "metal_brass_casino",
        "tile": "terrazzo",
        "wood": "hardwood_plank",
        "carpet": "carpet_delco",
        "ceiling_tile": "ceiling_tile_delco",
        "drywall": "drywall_delco",
        "plaster": "stucco_warm",
    },
}


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, v))


def rockay_style(default: dict) -> dict:
    color = default.get("color", [0.6, 0.6, 0.6])
    style = {
        "material": default.get("material", "metal"),
        "color": [round(_clamp(c * m), 4) for c, m in zip(color, COLOR_MUL)],
        "wear": round(min(WEAR_MAX, float(default.get("wear", 0.15)) + WEAR_ADD), 3),
        "bevel": default.get("bevel", 0.004),
        "ambient": AMBIENT,
    }
    if "emissive_color" in default:
        style["emissive_color"] = default["emissive_color"]
    if "emissive_strength" in default:
        style["emissive_strength"] = round(float(default["emissive_strength"]) * EMISSIVE_BOOST, 3)
    return style


def apply_zoo(species_dir: str) -> int:
    n = 0
    for path in sorted(glob.glob(os.path.join(species_dir, "*.json"))):
        if os.path.basename(path).startswith("_"):
            continue
        g = json.load(open(path, encoding="utf-8"))
        styles = g.get("styles", {})
        base = styles.get("default") or (styles[sorted(styles)[0]] if styles else {})
        styles["rockay"] = rockay_style(base)
        g["styles"] = styles
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(g, indent=1, ensure_ascii=False) + "\n")
        n += 1
    return n


def apply_pixelcoat(profiles_dir: str) -> str:
    themes = os.path.join(profiles_dir, "themes")
    os.makedirs(themes, exist_ok=True)
    out = os.path.join(themes, "rockay.json")
    # validate referenced materials exist with matching kind
    mats = os.path.join(profiles_dir, "materials")
    for kind, mid in ROCKAY_THEME["materials"].items():
        mp = os.path.join(mats, f"{mid}.json")
        if not os.path.isfile(mp):
            raise SystemExit(f"rockay theme references missing material '{mid}' ({mp})")
        mk = json.load(open(mp, encoding="utf-8")).get("kind")
        if mk != kind:
            raise SystemExit(f"material '{mid}' is kind '{mk}', mapped to slot '{kind}'")
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(ROCKAY_THEME, indent=2) + "\n")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zoo", default="zoo/zoo_keeper/genome/species")
    ap.add_argument("--pixelcoat", default="pixelcoat/profiles")
    a = ap.parse_args()
    if os.path.isdir(a.zoo):
        print(f"zoo: rockay style added to {apply_zoo(a.zoo)} species in {a.zoo}")
    else:
        print(f"zoo: species dir not found, skipped ({a.zoo})")
    if os.path.isdir(a.pixelcoat):
        print(f"pixelcoat: wrote {apply_pixelcoat(a.pixelcoat)}")
    else:
        print(f"pixelcoat: profiles dir not found, skipped ({a.pixelcoat})")
