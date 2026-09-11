"""Roadmap batch 19, 2026-09-11: item 140 narrowed by Pixelcoat 0.28.0.
REPLACE mode (batch 3's mechanism): the old status block is kept verbatim
inside the new one. Asserts the anchor matches exactly once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD = """*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON, MEASURED THE SAME HOUR*

**140. The drywall skin is white noise.**"""

NEW = """*STATUS: NARROWED 2026-09-11 -- THE DIAL FOUND BY SWEEPING, FIXED IN PIXELCOAT
0.28.0, MEASURED BACK INTO THE PLASTER/TILE BAND; NOT YET RE-WALKED. The
metric reproduced on the shipped packs (drywall 23.9 / 0.12, carpet 10.0 /
0.08). Sweeping the grammar through the real synthesizer at the shipped
256 px: `detail_strength` alone -- the per-texel hash grain, 0.18 on drywall
and 0.22 on carpet -- took drywall to 10.7 / 0.61; the micro band's cells and
octaves moved NOTHING at one decimal, because its weight (0.30 x 0.12 of a
+-0.5 field) is under one step of `posterize: 16` and quantises away. What
ships: drywall grain 0.04, meso worley 24, micro 40/2 -> std 11.6 / ac1
0.70 (concrete's correlation at plaster's amplitude); carpet grain 0.05,
meso fbm 48/2 at band 0.7 so the amplitude is pile, not noise -> 7.5 /
0.66. `tests/test_theme_profiles.py` now synthesises delco_1997's drywall,
carpet and plaster at pack size and holds ac1 >= 0.5 (0.3 plaster) in a
spread band. RESIDUE: the eye has not judged it -- 0.70 may read flat under
the nearest filter, and orange peel as relief (a normal map) is the honest
version of the material and is not emitted. EARLIER STATUS, KEPT VERBATIM:
OPEN 2026-09-11 -- FOUND BY A PERSON, MEASURED THE SAME HOUR*

**140. The drywall skin is white noise.**"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    n = text.count(OLD)
    if n != 1:
        print(f"anchor matched {n} times; refusing", file=sys.stderr)
        return 1
    out = text.replace(OLD, NEW, 1).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); item 140 narrowed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
