"""Deli Counter 0.286.2: the release that carries `migrations/README.md`'s index line for `migrate_bank_money.py`.

`tools/factory_index.py --write` wrote that line after 0.286.1 was committed and tagged, and it was committed on its
own (d16861c5), as the line for each earlier bank migration was. So Deli Counter's newest code commit was newer than
its VERSION, and factory 1.42.1's `verify-manifest --strict` read it STALE (`patches/factory_1_42_1_verify_stale.out.txt`):
rightly, since a set certified at 0.286.1 would carry a commit no release names. This release names it and changes
nothing else.

What it changes (anchored; nothing written on a miss): deli_counter/VERSION 0.286.1 -> 0.286.2, and a CHANGELOG entry.

    python patches/patch_dc_index_0286_2.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
OLD, NEW = b"Deli Counter 0.286.1", b"Deli Counter 0.286.2"
HEAD = "## [0.286.1] - a vault's money rack is steel\n"
ENTRY = ("## [0.286.2] - the migrations index names migrate_bank_money.py\n\n"
         "`migrations/README.md`'s generated index (the factory's `tools/factory_index.py --write`) gained its line for "
         "`migrate_bank_money.py` after 0.286.1 was tagged, in a commit of its own, so the newest code commit was newer "
         "than VERSION and the factory's `verify-manifest --strict` read Deli Counter STALE. This release carries that "
         "line and changes nothing else.\n\n")


def main():
    v = DC / "VERSION"
    if v.read_bytes() != OLD:
        raise SystemExit("REFUSED: deli_counter/VERSION reads %r, not %r; nothing written" % (v.read_bytes(), OLD))
    cl = DC / "CHANGELOG.md"
    raw = cl.read_bytes()
    if b"\r\n" in raw or not raw.decode("utf-8").startswith(HEAD):
        raise SystemExit("REFUSED: deli_counter/CHANGELOG.md is not LF opening on 0.286.1; nothing written")
    v.write_bytes(NEW)
    cl.write_bytes(ENTRY.encode("utf-8") + raw)
    print("Deli Counter 0.286.1 -> 0.286.2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
