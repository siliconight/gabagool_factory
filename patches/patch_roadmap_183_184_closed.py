"""PIPELINE_ROADMAP.md: close items 183 and 184 on cold run 9164's measurements.

Each status line is replaced whole and the earlier one kept verbatim at its
item's end. The index is left to `tools/roadmap_status.py --write`.

    python patch_roadmap_183_184_closed.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

S183_OLD = ("*STATUS: OPEN 2026-10-05 -- MEASURED, NOT STARTED. On gs_empty_rowhome_f in cold run 9162's walk "
            "copy, rays at 1.0 and 2.0 m pass 10 m into the shell through the front door (x 1.2-1.8) and stop at "
            "the face everywhere else; a 0.4 m capsule stops in the reveal.*\n")
S183_NEW = ("*STATUS: CLOSED 2026-10-05 -- Deli Counter 0.186.0 fills a facade's door full-thickness, as its "
            "window's pane. Cold run 9164 (0 interventions), the same probe on gs_empty_rowhome_f: every ray "
            "across the doorway stops at the face at 1.0 and 2.0 m; the walk capsule stops at the wall, where "
            "it had reached 0.26 m into the reveal. The walker, the same day: Empties keep their doors closed, "
            "never meant to be entered.*\n")
B183_END = '''  * The fix is Deli Counter's: a facade doorway gets a leaf collider, as
    its window gets a pane.
'''
B183_NEW = B183_END + "\n*Earlier status, kept verbatim:* " + S183_OLD

S184_OLD = ("*STATUS: OPEN 2026-10-05 -- FOUND, CAUSE NOT ESTABLISHED. Two dashed lines in the sky over "
            "gs_empty_rowhome_l's roof in 9160's and 9161's street frames; the gutter Patina hangs on the "
            "neighbouring house's party wall projects along their slope, about 30 px below them.*\n")
S184_NEW = ("*STATUS: CLOSED 2026-10-05 -- Patina 0.29.1 gutters only an Empty's faces with openings. Cold run "
            "9164 (0 interventions): the Empties' gutter orders went from 158 front/back plus 144 east/west to "
            "158 and 0; -16 draws at the median view (-62 at most), median frame -0.076 ms against a +0.030 "
            "control. The lines' cause was never pinned past the gutter's slope; the 30 px residue is "
            "unexplained, and no frame since has been checked for them.*\n")
B184_END = '''  * A rowhouse roof drains front and back, and the downspouts already keep
    to faces with openings. A party wall wants a coping, not a gutter.
'''
B184_NEW = B184_END + "\n*Earlier status, kept verbatim:* " + S184_OLD


def main():
    s = ROADMAP.read_text(encoding="utf-8")
    assert "\r" not in s
    for old in (S183_OLD, B183_END, S184_OLD, B184_END):
        assert s.count(old) == 1, old[:60]
    s = (s.replace(S183_OLD, S183_NEW).replace(B183_END, B183_NEW)
          .replace(S184_OLD, S184_NEW).replace(B184_END, B184_NEW))
    ROADMAP.write_text(s, encoding="utf-8", newline="\n")
    print("closed roadmap items 183 and 184")


if __name__ == "__main__":
    main()
