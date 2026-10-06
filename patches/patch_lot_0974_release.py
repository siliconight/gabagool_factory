"""Lot 0.97.4: VERSION and CHANGELOG for the repo-hygiene move (no patch
script: two `git mv`, one `git rm`, and one path line in the moved test).

    python patch_lot_0974_release.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOT = ROOT / "lot"

ENTRY = '''## 0.97.4 - the root test moves under tests/, and the `--out-dir/` directory goes

Repo hygiene (`docs/findings/repo_hygiene_2026-10/` at the factory root).
- `test_ladders_reach_the_site.py` stood at the root beside `tests/`. It is
  under `tests/` now, with `HERE` pointing at the repo root as the other
  tests' path line does; it ran 5 passed there and the suite 669.
- A tracked directory literally named `--out-dir/` held one assembled
  `example_compound.tscn`: an `assemble` run given the flag's name as its
  value. Nothing read it (the tests assemble `specs/example_compound.json`
  into a temp dir). Removed.

**Suite:** 669 passed, as 0.97.3.

'''


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.97.3", v.read_bytes()
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.97.3 - no spawn inside an Empty"), text[:60]
    cl.write_bytes((ENTRY + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.97.4")
    print("Lot 0.97.4: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
