"""Roadmap 232 CLOSED by Zoo 1.99.1: `add_hemisphere` keeps the upper half it names, every vertex scaled.

Replaces 232's status block (asserted whole, and asserted to adjoin 232's heading) and appends one
paragraph to its body, which keeps the item's first reading and says where it was wrong. Run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_232_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
HEAD = "\n\n**232. `add_hemisphere` keeps the lower half: four species' caps hang inside their bodies.**"
OLD_STATUS = (
    "*STATUS: OPEN 2026-10-11 -- measured, not started. `geometry.add_hemisphere` (Zoo) documents an "
    "\"upper hemisphere shell (open bottom)\" and keeps the LOWER half: printed in Blender 5.1.1, a unit "
    "hemisphere at the origin returns 101 vertices at z -1.0000 .. 0.0000 with faces pointing down and "
    "out (mean face normal z -0.64) -- its bisect keeps the side opposite its plane normal. Its four "
    "callers besides the dome all place it as a cap ON TOP -- `bollard` at the post's top, "
    "`exhaust_fan` on its drum, `soda_cup` as its lid, `helmet` as its shell -- so each builds its cap "
    "hanging inside its own body, hidden. Found by the dome (roadmap 229, cold run 9239), whose 1.98.1 "
    "no longer depends on the helper's side. Owner: Zoo. Fix the helper to keep what it says (or say "
    "what it keeps), then each of the four needs its census and a frame: the caps will appear, which "
    "is a look change, and a cap that rises may meet another part's plane.*")
NEW_STATUS = (
    "*STATUS: CLOSED 2026-10-11 -- Zoo 1.99.1 (`patches/patch_zoo_hemisphere_fix.py`, "
    "`docs/findings/hemisphere_half/`). The helper keeps the upper half (its bisect's normal up; "
    "`clear_inner` clears the side behind the normal) and transforms the vertices its cut makes: at "
    "`segments` 14, an odd ring count, 14 of them had stayed at radius 0.975 on a hemisphere asked for "
    "at 0.5. Built through the kit path at the default corner, each cap's crown reach -- how far its "
    "topmost vertices lie from its axis -- went from the full radius to 0.0000 m: bollard 0.0830, "
    "exhaust fan 0.3500, soda cup 0.0247, helmet 0.1299; the exhaust fan from 0.385 m to its slot's "
    "0.550 m; the bollard's pipe shortened by its cap's rise so its height holds at 1.050 m; every "
    "triangle count unchanged. The dome builds the same vertex for vertex, normals included. Census: "
    "two rows of Zoo's coincident-face table read differently and moved with it (the soda cup's "
    "nearest cover 0.21 -> 2.0 mm, the exhaust fan's one buried pair counted as two, same parts and "
    "area), no coincidence new. 11 new tests, 10 of them failing on 1.99.0. No level carries the four "
    "species, so no cold run reads it.*")
TAIL = ("The fix is one line in the helper -- keep the upper half -- and four censuses and four frames "
        "to see what each species looks like with the cap it was written to have.")
ADD = """

**CLOSED BY ZOO 1.99.1, 2026-10-11** (`docs/findings/hemisphere_half/README.md`, `caps.png`). Three things this item said were wrong; they stay above, and this is what replaced them. **The exhaust fan's dome was not inside its drum:** the hood's radius is the fan's full half-width and the drum's is 0.7 of it, so the lower half hung AROUND the drum as an open bowl -- visible, and the wrong shape -- and the fan stood 0.385 m in a 0.55 m slot, because a kit build re-centres a module but does not stretch it. **Not every cap drew nothing:** the bollard's and the soda cup's were hidden, but the fan's bowl and the helmet's upturned shell were in plain sight; nobody had looked, because no level asks for any of the four (no level-factory job sets `roof_props_slots`, and no tool names a bollard, a soda cup or a helmet). **The fix was not one line:** an odd ring count left the bisect's new rim vertices untransformed, which the helmet's genome reaches at 14, 18, 22, 26 and 30 segments when a prompt names the count; and the bollard needed its pipe shortened by the cap's rise, because `fit_to` scales a piece to its slot: a cap built above the pipe would have squeezed the whole bollard to make room for it. Left as a note, not fixed: the fan's hood is an open shell, so from below its inside is culled and the ring between its rim and the drum shows the sky."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "CLOSED BY ZOO 1.99.1" not in text, "already applied"
    assert text.count(OLD_STATUS) == 1, ("232's status not found once", text.count(OLD_STATUS))
    assert text.count(HEAD) == 1, "232's heading not found once"
    s = text.index(OLD_STATUS)
    h = text.index(HEAD)
    assert s + len(OLD_STATUS) == h, "232's status does not adjoin its heading"
    nxt = text.find("\n\n", h + len(HEAD))
    body = text[h:nxt] if nxt > 0 else text[h:].rstrip("\n")
    assert body.endswith(TAIL), ("232's body does not end where this patch read it", body[-120:])
    end = h + len(body)
    text = text[:end] + ADD + text[end:]
    text = text[:s] + NEW_STATUS + text[s + len(OLD_STATUS):]
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 232 CLOSED, its paragraph appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
