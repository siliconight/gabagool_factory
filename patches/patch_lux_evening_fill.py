"""Lux 0.81.0: the evening's fill.

Blue Hour's sky in the bake lifted -- `sky_energy` 0.7 -> 1.5, `ground_color` (0.10, 0.11, 0.16) -> (0.20, 0.19,
0.22) -- so a baked facade and street read at dusk; the sun, exposure, fixtures and sky colours unchanged.

Proven: tools/day_presets_selftest.gd's Blue Hour checks fail on 0.80.0 (fails_on_old.out.txt); that self-test,
street_lamps_selftest and room_ambient_selftest pass on the clone; the slice rebuilt and priced (the factory's
docs/findings/slice_look/, slice 12: street frames about 45 % brighter, draws +0).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'lux'
PINS = {'CHANGELOG.md': '3ca69a2e1741f141', 'VERSION': '7da7dd7b15104d38', 'addons/lux/presets/blue_hour.tres': '62adda0560a4d072', 'tools/day_presets_selftest.gd': '2e13687dfd82e5f8'}
EDITS = {'CHANGELOG.md': [('lines 1-2', '# Changelog\n\n', '# Changelog\n\n## [0.81.0] - the evening\'s fill\n\nThe walker, 2026-10-30, of the game\'s vertical slice: "lift the evening fill". At the brief\'s `evening` (Level\nFactory maps it to Blue Hour) every facade and the ground were close to black -- the slice\'s street frames 22-40 of\n255 in the level\'s light -- with only the signs, the windows and the canopy reading. A baked surface takes its fill\nfrom the sky in the bake (Level Factory 0.164.0\'s `environment_mode = 1`) and not from `ambient_energy`, and Blue\nHour\'s sky gave it little: `sky_energy` 0.7 over a `ground_color` of (0.10, 0.11, 0.16). Raised to 1.5 over (0.20,\n0.19, 0.22); the sun, its 4 degrees, the exposure, the fixtures and the sky\'s colours are unchanged, so the signs,\nwindows and canopy stay the brightest things in a frame. Measured on the slice (the factory\'s\n`docs/findings/slice_look/`, slice 12): the street frames 30.7 -> 45.5 (ave_east), 33.9 -> 49.9 (the bank), 25.5 ->\n39.1 (the sidewalk), the interior objective 40.4 -> 40.8; draws +0 exactly, the fill living in the lightmap. Tests:\ntools/day_presets_selftest.gd pins the sky and ground and that the sun stays at dusk (fails on 0.80.0).\n\n')], 'VERSION': [('lines 1-1', 'Lux 0.80.0', 'Lux 0.81.0')], 'addons/lux/presets/blue_hour.tres': [('lines 21-22', 'ground_color = Color(0.1, 0.11, 0.16, 1)\nsky_energy = 0.7\n', 'ground_color = Color(0.2, 0.19, 0.22, 1)\nsky_energy = 1.5\n')], 'tools/day_presets_selftest.gd': [('lines 106-107', '\t_check("noon brighter than morning", noon.sun_energy > morning.sun_energy, [morning.sun_energy, noon.sun_energy])\n\tif _fails:\n', '\t_check("noon brighter than morning", noon.sun_energy > morning.sun_energy, [morning.sun_energy, noon.sun_energy])\n\t# THE EVENING\'S FILL (0.81.0). The walker, 2026-10-30, of the vertical slice: "lift the evening fill". A baked\n\t# surface takes its fill from the sky in the bake (Level Factory 0.164.0), and Blue Hour\'s 0.7 sky over a\n\t# 0.1 ground gave the slice\'s street frames 22-40 of 255: everything but the signs and windows near black.\n\tvar blue: LuxPreset = _load("blue_hour.tres")\n\t_check("Blue Hour loads", blue != null, "blue_hour.tres")\n\tif blue != null:\n\t\t_check("Blue Hour\'s sky lights the bake (>= 1.5)", blue.sky_energy >= 1.5, blue.sky_energy)\n\t\tvar g: Color = blue.ground_color\n\t\t_check("Blue Hour\'s ground lifts the undersides (>= 0.18)", (g.r + g.g + g.b) / 3.0 >= 0.18, g)\n\t\t_check("Blue Hour stays dusk: its sun at 4 degrees", is_equal_approx(blue.sun_elevation_deg, 4.0),\n\t\t\tblue.sun_elevation_deg)\n\tif _fails:\n')]}
WHOLE = {}
NEW_FILES = {}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s/%s has mixed line endings; nothing written" % (REPO.name, name))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %s/%s is %s, not the %s this patch was written against; nothing written"
                         % (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %s/%s: the anchor at %s is there %d times; nothing written"
                                 % (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
