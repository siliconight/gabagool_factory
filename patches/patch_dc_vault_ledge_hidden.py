"""Deli Counter 0.227.0: a vault ledge inside furniture draws no box of its own -- the furniture is its look.

FOUND resolving factory roadmap 177's last z-fight pairs. On the factory's cold run 9322 two of the four pairs were
the office's `base:VAULTLEDGE_0 / reception_desk`. The office preset puts a 5 m vault ledge and a 5 m reception
desk at the same spot, (0, -8), on purpose: the desk is the obstacle a body vaults, and the ledge is its vault tag.
But the ledge also drew its own box -- 1.1 m tall inside a desk 1.0 m tall -- so a 0.2 m strip stood 10 cm proud of
the desk top along its 5 m and the two boxes' ends z-fought. Level Factory 0.217.0's vault ledge skin then gave that
strip the building's drywall. Deli Counter's own `test_zfight_gate.py` already names the pair as a fight.

MEASURED across the spec library, 2026-10-19 (the session's `ledge_overlap_census.py`, by volume, on a 5 cm grid):
228 vault ledges in 446 specs; 111 stand clear of every volume; 98 cross one in part; 19 stand at least half inside
one -- 14 wholly in a register counter, 5 mostly in a reception desk (the office's 91 %, the 9 % being the strip).

THE RULE, a call made 2026-10-19 under the walker's standing instruction to make decisions that can be changed
later: a ledge at least `ledge_cover.HIDDEN_BY` (0.5) of whose box lies inside one visible volume draws no visual box.
Its collision and its VAULTLEDGE tag stay, so the vault, the grade and the nav bake see the same solid; only the
duplicate look goes. The 98 partial crossings keep their box: a ledge running past a counter is still a half-wall
where it stands clear. The threshold is the dial.

What it changes (anchored; refuses on a miss; LF-safe):
  * ledge_cover.py (new, pure): HIDDEN_BY and cover(center, size, volumes) -> (fraction, name), against the one
    visible volume covering most of the box.
  * deli_counter.py: `import ledge_cover`; `_vault_ledges` asks it before drawing, and prints which ledge it left
    to its furniture.
  * test_ledge_cover.py (new, 6): the office's ledge is 91 % its desk's; a ledge in open floor, one wholly in a
    counter, an invisible volume hiding nothing; the emitter asks; the dial is recorded as one.
  * VERSION 0.226.0 -> 0.227.0, CHANGELOG.

AFTER APPLYING: `python build.py --all` (the pre-commit gate refuses until the built shells are newer than the
code), then the suite and the commit.

    python patches/patch_dc_vault_ledge_hidden.py --tests   # the test file only (prove it fails first)
    python patches/patch_dc_vault_ledge_hidden.py           # everything
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
CODE = DC / "deli_counter.py"
CODE_SHA = "d49ab95a3ebc9ae6"

IMPORT_OLD = "import prop_species\n"
IMPORT_NEW = "import prop_species\nimport ledge_cover\n"

LEDGE_OLD = r'''            name = f"VAULTLEDGE_{vi}"
            self._box(name, (vl.x, vl.y, z), size, self.VISUAL, role="floor")
            self._col_box(name, (vl.x, vl.y, z), size)
            self._record_surface(name + self.col_suffix["convex"], vl.material)
'''
LEDGE_NEW = r'''            name = f"VAULTLEDGE_{vi}"
            # A LEDGE INSIDE FURNITURE IS THE FURNITURE'S VAULT TAG (0.227.0,
            # `ledge_cover`): at least half inside a visible volume -- a register
            # counter, a reception desk -- it draws no box of its own, because the
            # volume is its look; drawn, it stood a second box inside the first and
            # z-fought it. The collision and the tag stay, so the vault does.
            frac, under = ledge_cover.cover((vl.x, vl.y, z), size, self.s.volumes)
            if frac < ledge_cover.HIDDEN_BY:
                self._box(name, (vl.x, vl.y, z), size, self.VISUAL, role="floor")
            else:
                print(f"[deli_counter] {name} draws no box: {frac:.0%} of it inside {under}, which is its look")
            self._col_box(name, (vl.x, vl.y, z), size)
            self._record_surface(name + self.col_suffix["convex"], vl.material)
'''

MODULE = r'''"""How much of a vault ledge stands inside furniture -- and so whether it draws a box of its own (0.227.0).

A vault ledge (`spec_types.VaultLedge`) is a waist-height box the game marks vaultable. Where a spec puts one at a
piece of furniture -- a register counter, a reception desk -- the ledge is that furniture's vault tag, and the
furniture's own box (a `Volume`, which the art pass dresses as a Zoo prop) is its look. Drawing the ledge as well
stood a second box inside the first: the office's reception desk is 1.0 m tall and its ledge 1.1 m, so a 0.2 m
strip stood 10 cm proud of the desk along its 5 m, and the two boxes' ends z-fought (the factory's cold run 9322:
`base:VAULTLEDGE_0 / reception_desk`). Measured across the spec library on 2026-10-19: 228 ledges; 111 stand clear
of every volume; 98 cross one in part; 19 stand at least half inside one (14 wholly in a register counter, 5 mostly
in a reception desk).

THE RULE, a call made 2026-10-19 and meant to be changed: a ledge at least HIDDEN_BY of whose box lies inside one
visible volume draws no box; its collision and VAULTLEDGE tag stay, so the vault is unchanged. The share is by
volume, of the ledge's own box, against the one volume that covers most of it. A volume with `visual` False hides
nothing: it draws nothing either, so the ledge's box is the only look there is.

Frame: Deli Counter's spec frame, metres, Z up; a box is a centre and a size, a volume's `z` its centre.
"""

#: The share of a ledge's box inside one visible volume at which the volume is its look. The dial.
HIDDEN_BY = 0.5


def _overlap(c0, s0, c1, s1) -> float:
    """The volume two axis-aligned boxes share."""
    shared = 1.0
    for k in range(3):
        lo = max(c0[k] - s0[k] / 2, c1[k] - s1[k] / 2)
        hi = min(c0[k] + s0[k] / 2, c1[k] + s1[k] / 2)
        if hi <= lo:
            return 0.0
        shared *= hi - lo
    return shared


def cover(center, size, volumes):
    """``(fraction, name)``: the share of the box ``(center, size)`` inside the one visible volume covering most of
    it, and that volume's name -- ``(0.0, None)`` when none does. ``volumes`` are ``spec_types.Volume``s, or
    anything with name, x, y, z, size_x, size_y, size_z and, optionally, visual."""
    own = size[0] * size[1] * size[2]
    if own <= 0:
        return 0.0, None
    best, name = 0.0, None
    for v in volumes:
        if not getattr(v, "visual", True):
            continue
        f = _overlap(center, size, (v.x, v.y, v.z), (v.size_x, v.size_y, v.size_z)) / own
        if f > best:
            best, name = f, v.name
    return best, name
'''

TEST = r'''"""A vault ledge inside furniture draws no box of its own (0.227.0; see ledge_cover.py).

Found on the factory's cold run 9322, whose office z-fought `base:VAULTLEDGE_0` against `reception_desk`: the preset
stands its 5 m ledge in its 5 m desk on purpose -- the desk is the vault -- and the ledge drew a box 10 cm taller.

Run: python -m pytest -q test_ledge_cover.py
"""
import inspect
from pathlib import Path
from types import SimpleNamespace

import ledge_cover
import spec_loader

HERE = Path(__file__).resolve().parent


def _ledge_box(spec, vl):
    """The box `deli_counter._vault_ledges` builds for a ledge: centre and size, spec frame."""
    z = vl.story * spec.story_height + vl.height / 2
    size = (vl.length, vl.thick, vl.height) if vl.axis == "X" else (vl.thick, vl.length, vl.height)
    return (vl.x, vl.y, z), size


def _vol(name, c, s, visual=True):
    return SimpleNamespace(name=name, x=c[0], y=c[1], z=c[2], size_x=s[0], size_y=s[1], size_z=s[2], visual=visual)


def test_the_offices_reception_desk_is_its_ledges_look():
    spec = spec_loader.load_spec(str(HERE / "specs" / "office.json"))
    (vl,) = spec.vault_ledges
    frac, under = ledge_cover.cover(*_ledge_box(spec, vl), spec.volumes)
    assert under == "reception_desk" and abs(frac - 1.0 / 1.1) < 1e-6, (frac, under)
    assert frac >= ledge_cover.HIDDEN_BY


def test_a_ledge_in_open_floor_draws_itself():
    far = _vol("crate", (20.0, 20.0, 0.5), (1.0, 1.0, 1.0))
    assert ledge_cover.cover((0.0, 0.0, 0.55), (4.0, 0.2, 1.1), [far]) == (0.0, None)


def test_a_ledge_wholly_inside_a_counter_is_the_counters():
    counter = _vol("register_counter", (0.0, 0.0, 0.6), (5.0, 0.8, 1.2))
    frac, under = ledge_cover.cover((0.0, 0.0, 0.55), (4.0, 0.2, 1.1), [counter])
    assert under == "register_counter" and abs(frac - 1.0) < 1e-9


def test_an_invisible_volume_hides_nothing():
    ghost = _vol("register_counter", (0.0, 0.0, 0.6), (5.0, 0.8, 1.2), visual=False)
    assert ledge_cover.cover((0.0, 0.0, 0.55), (4.0, 0.2, 1.1), [ghost]) == (0.0, None)


def test_the_emitter_asks_before_it_draws():
    src = (HERE / "deli_counter.py").read_text(encoding="utf-8")
    body = src[src.index("    def _vault_ledges(self):"):src.index("    def _platforms(self):")]
    assert "ledge_cover.cover((vl.x, vl.y, z), size, self.s.volumes)" in body
    assert "if frac < ledge_cover.HIDDEN_BY:" in body
    # the collision and its tag stay either way
    assert body.index("self._col_box(name") > body.index("if frac < ledge_cover.HIDDEN_BY:")


def test_the_threshold_is_a_dial_and_says_so():
    assert ledge_cover.HIDDEN_BY == 0.5
    assert "meant to be changed" in inspect.getsource(ledge_cover)
'''

CHANGELOG = '''## [0.227.0] - a vault ledge inside furniture draws no box of its own

**Found resolving factory roadmap 177's last z-fight pairs.** Two of cold run 9322's four were the office's
`base:VAULTLEDGE_0 / reception_desk`. The office preset stands its 5 m vault ledge in its 5 m reception desk on
purpose -- the desk is the obstacle a body vaults, and the ledge its tag -- but the ledge also drew its own box,
1.1 m tall inside a desk 1.0 m tall: a 0.2 m strip 10 cm proud of the desk top along its length, z-fighting the
desk's ends. Across the spec library: 228 ledges; 111 clear of every volume, 98 crossing one in part, and 19 at
least half inside one (14 wholly in a register counter, 5 mostly in a reception desk).

**The rule, a call made 2026-10-19 and meant to be changed:** a ledge at least `ledge_cover.HIDDEN_BY` (0.5) inside
one visible volume draws no visual box. Its collision and VAULTLEDGE tag stay, so the vault, the grades and the nav
bake see the same solid; only the duplicate look goes. A ledge crossing furniture in part keeps its box.

### Added
- `ledge_cover.py`: `HIDDEN_BY` and `cover(center, size, volumes)`, the share of a box inside the one visible
  volume covering most of it.
- `test_ledge_cover.py` (6, which fail to import on 0.226.0).

### Changed
- `_vault_ledges` asks `ledge_cover` before it draws, and says which ledge it left to its furniture.

'''


def _apply(path, old, new, count=1):
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    assert crlf == 0 or lf == 0, f"{path.name}: mixed endings ({crlf} CRLF, {lf} LF)"
    eol = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    o, n = old.replace("\n", eol), new.replace("\n", eol)
    assert text.count(o) == count, f"{path.name}: anchor found {text.count(o)} times, wanted {count}: {old[:70]!r}"
    path.write_bytes(text.replace(o, n).encode("utf-8"))


def write_tests():
    p = DC / "test_ledge_cover.py"
    assert not p.exists(), f"{p.name} exists"
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote deli_counter/test_ledge_cover.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    raw = CODE.read_bytes()
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == CODE_SHA, ("deli_counter.py is not the file this patch read", got)
    assert "import ledge_cover" not in raw.decode("utf-8"), "already applied"
    mod = DC / "ledge_cover.py"
    assert not mod.exists(), "ledge_cover.py exists"
    v = DC / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Deli Counter 0.226.0", v.read_text(encoding="utf-8")
    cl = DC / "CHANGELOG.md"
    rawc = cl.read_bytes()
    crlf = rawc.count(b"\r\n")
    eol = "\r\n" if crlf else "\n"
    text = rawc.decode("utf-8")
    assert text.startswith("## [0.226.0]"), text[:40]
    _apply(CODE, IMPORT_OLD, IMPORT_NEW)
    _apply(CODE, LEDGE_OLD, LEDGE_NEW)
    mod.write_text(MODULE, encoding="utf-8", newline="\n")
    v.write_text("Deli Counter 0.227.0", encoding="utf-8")
    cl.write_bytes((CHANGELOG.replace("\n", eol) + text).encode("utf-8"))
    write_tests()
    print("Deli Counter 0.227.0 applied: ledge_cover.py, _vault_ledges, test, VERSION, CHANGELOG -- now build.py --all")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
