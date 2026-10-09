"""Deli Counter 0.204.0's release: VERSION and the CHANGELOG entry.

    python patch_dc_0204_release.py

Anchored on VERSION (b'Deli Counter 0.203.0') and on CHANGELOG.md's head (the
0.203.0 entry's heading, LF).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

HEAD = "## [0.203.0] - a slot owns its own greybox nodes, never a sibling slot's\n"
ENTRY = """## [0.204.0] - a payphone on a wall is a wall unit

**What the walker asked for.** Roadmap 210, 2026-10-09: "yes light it, and do
the indoor wall form".

**What was there.** `level_design._piece("payphone", ..., "wall")` stands a
payphone against a wall, and it asked for no form. So Zoo's `auto` built
every one as a booth on a post, standing on the floor in front of the wall.
Cold run 9212 shipped two of them: the airport terminal's and the funeral
home's.

**The piece now asks for Zoo 1.88.0's `wall` form:** no post, a conduit down
the wall, and a phone book on two rings under the shelf. Since Zoo 1.89.0 it
also has a lit header and a hood lamp.

**The library, refurnished** (`migrate_furnish_recipes.py`, the L23 rule: a
piece edit needs a refurnish):
- **On a copy first:** 128 specs. 38 changed, and in them exactly 39 payphone
  volumes gained `"form": "wall"`. Nothing else moved, structurally or byte
  for byte once that field is taken out.
- **Then the repo,** which matched the copy file for file.
- **The 38 shells rebuilt** (`build.py <spec>` for each; `--all` is that
  loop): 0 failures, and `build_freshness` up to date at 146.
- **The tracked outputs that moved:**
  - 32 `slots.json`, each only in its payphones' `form`;
  - 38 manifests, only in `built_utc` and their two hashes.
- **Six more `slots.json` carry the form too:** police station 07, the
  `cbp_town_finale` finale (two payphones), `final_stand`,
  `foundry_heist_vertical`, `office` and `survival_demo`. `.gitignore` keeps
  those six out. 32 tracked slots plus 7 untracked is the 39.

**Left alone: the two payphones the piece did not place.** `primos_pizza`
and `strip_retail_a01` each carry an AUTHORED payphone, named plain
`payphone`.
- Its slot is 0.5 x 0.5 x 1.6 m, unrotated, 0.25 m off the dining room's
  back partition.
- The refurnish does not touch an authored volume.
- A wall unit there would hang a quarter of a metre off the wall, so both
  stay booths on their posts.

**A second fix: `material_kind.SKIN_KINDS` learns `paint_matte`.**
- `SKIN_KINDS` is a literal copy of Zoo's `skins.KNOWN_KINDS`.
  `test_material_kind.test_the_kinds_are_zoo_s_when_zoo_is_beside_this_repo`
  pins it to Zoo's list.
- Zoo 1.82.0 (the getaway van, 2026-10-07 22:35) added `paint_matte`.
  0.203.0's suite had run at 14:54 that day, and this release's was the
  first since. It found the pin failing.
- **The pin fails the same against Zoo 1.88.0** with this repo untouched. It
  is the drift the test exists to catch, not this release's change.
- No spec writes the kind (Lot stands the van), so it has no
  `KIND_BY_MATERIAL` row.

**Tests:** `test_payphone_wall_form.py`, 4.
- **On 0.203.0 three fail:** the piece has no form, and the 39 payphones it
  placed, and their slots, ask for none.
- **The fourth** guards that the form moved no size.

**Suite:** 1358 passed, 2 skipped in 95 s (`python -m pytest -q`). That is
0.203.0's 1354 and this release's 4. Before the kind fix, 1 failed: the pin
to Zoo's kinds.

"""


def main():
    v = DC / "VERSION"
    assert v.read_bytes().strip() == b"Deli Counter 0.203.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"\r\n" not in d, "CHANGELOG.md is LF; it has CRLF now"
    t = d.decode("utf-8")
    assert t.startswith(HEAD) and t.count(HEAD) == 1, t[:90]
    assert "## [0.204.0]" not in t
    cl.write_bytes((ENTRY + t).encode("utf-8"))
    v.write_bytes(v.read_bytes().replace(b"0.203.0", b"0.204.0"))
    print("Deli Counter 0.203.0 -> 0.204.0")


if __name__ == "__main__":
    main()
