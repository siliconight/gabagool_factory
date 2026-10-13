"""Level Factory CHANGELOG 0.196.0: the stoop's colliders are not only Deli Counter's.

The entry says of the merged stoop: "Its colliders are Deli Counter's own, in the greybox base, and
unchanged." The same entry's own measurement says otherwise -- on a mirror of cold run 9271's package the
merge copied THREE colliders a rowhome out of the stoop's slot children: the art's modules (Zoo builds a
prop module with a box collider) carry one a piece. Deli Counter's ramp, landing and block are in the
greybox base and unchanged; the modules' boxes stand under the ramp, as a flight's treads do, and the
contract body walked up over them in 9271 (`docs/cold_runs/cold_9271/stoop_walk.out.txt`) and again after
the merge in 9272. A CHANGELOG line only, as Lot's 76c1cd8 corrected 0.119.1's.

One anchored edit, asserted once:

    python patches/patch_lf_changelog_0196_colliders.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
OLD = ("  material with the rest of that side. Its colliders are Deli Counter's own, in the greybox base, and\n"
       "  unchanged.\n")
NEW = ("  material with the rest of that side. Deli Counter's colliders -- the ramp, the landing, the block --\n"
       "  are in the greybox base and unchanged; the art's modules bring a box collider a piece (Zoo builds a\n"
       "  prop module with one), which the merge copies out under `KitCollision` as it does every slot's.\n"
       "  They stand under the ramp, as a flight's treads do. (Corrected after the release: the entry first\n"
       "  said the stoop's colliders were Deli Counter's alone, and its own merge result counted three more.)\n")


def main():
    p = LF / "CHANGELOG.md"
    raw = p.read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    assert crlf in (0, lf), "mixed line endings"
    eol = b"\r\n" if crlf else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.count(OLD) == 1, ("anchor", text.count(OLD))
    p.write_bytes(text.replace(OLD, NEW).encode("utf-8").replace(b"\n", eol))
    print("Level Factory CHANGELOG 0.196.0: the stoop's colliders, corrected")


if __name__ == "__main__":
    main()
