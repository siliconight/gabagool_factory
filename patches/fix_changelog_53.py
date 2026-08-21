import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "zoo", "CHANGELOG.md")
with open(P, "rb") as fh:
    raw = fh.read()
eol = "\r\n" if b"\r\n" in raw else "\n"
src = raw.decode("utf-8").replace("\r\n", "\n")

ANCHOR = """### Notes
- Measured, not assumed: 53 recipe modules, 79 `make_material` calls."""

CORRECTION = """### Corrected
- The 0.45.0 entry states that with `ensure_ascii=False` all 53 genomes
  round-trip. That is wrong. 49 of 53 do; `litter_scrap`, `pebble`,
  `rubble_frag` and `weed_tuft` do not. The selftest that measured it was
  written after that entry was published. The 0.45.0 text is left standing and
  corrected here, matching how the batch-1 note was corrected in 0.45.0 itself.

"""

if "The 0.45.0 entry states that with" in src:
    print("ALREADY PRESENT -- the correction is in zoo/CHANGELOG.md")
    sys.exit(0)

n = src.count(ANCHOR)
if n != 1:
    print("REFUSING -- anchor appears %d time(s), expected 1" % n)
    sys.exit(1)

out = src.replace(ANCHOR, CORRECTION + ANCHOR)
with open(P + ".pre_corr", "wb") as fh:
    fh.write(raw)
with open(P, "wb") as fh:
    fh.write(out.replace("\n", eol).encode("utf-8"))
print("APPLIED -- correction added to the zoo 0.47.0 entry")
