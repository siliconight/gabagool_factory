"""Deli Counter 0.201.0: VERSION and CHANGELOG for the deli's window.

    python patch_dc_0201_release.py <suite line>

Anchored on VERSION and the CHANGELOG head as read 2026-10-07.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.201.0] - a deli hangs its beer sign in its front window and tapes its posters under it

**What it was.** Not one of the six library delis carried a window sign or a
window poster.
- The store rules (`migrate_window_sign`, `migrate_window_poster`, 0.160.0
  and 0.170.0) qualify a store only: a `sales_floor` with snack gondolas, and
  a storey-0 `storefront_glass` wall. They hang the sign beside a door in a
  wall of glass.
- A corner deli's street face is brick. It has the customers' door
  (`front_customer_entry`, pos -0.28) and one punched window: 2.0 m wide,
  sill 0.85, head 2.25 (`Opening.resolved`'s 1.4 m), 10.5 m from the door.
  The window opens into the market aisles.

**The window rule** (`migrate_window_sign.front_window`, `plan_window`).
- **The front window** is the storey-0 window on the wall that carries the
  customers' door, the one nearest that door.
- **The sign** hangs in it, centred, its top at the window's head, 4 cm
  inside the wall's inner face, against the pane as a deli's neon hangs.
- **The posters** (`migrate_window_poster.plan_window`) are taped low under
  it:
  - 10 cm over the sill and 5 cm under the sign's foot;
  - 0.25 m toward the customers' door, where they pass.
- **A window too small for both** hangs the sign and says why it has no
  posters. A building with no window on the door's wall is refused, and says
  so.
- **The store's rule is untouched.** Three library stores keep their sign
  exactly where it was (pinned).

**Generated and drawn alike.**
- `presets.corner_deli` runs both rules, as `gas_station` dresses its glass.
- The two migrations brought the six library delis to them: each has the
  sign at (0, -13.755, 1.95) and the posters at (-0.25, -13.79, 1.25).
- **The neon names** are Zoo's six invented beers (`club_names.WINDOW_NAMES`),
  dealt by the spec's name. **The posters** are the store family's sale
  sheets.

**A sign hung in a window stands on no floor.** In a deli's window the sign's
foot is at 1.65 m, under the headroom line that exempts a hung sign from
furnish's room count.
- `level_design._room_volume_count` now exempts a `form: window` sign at any
  height, as 0.170.0 exempted paper on a wall. Counted, it would have cost
  the market aisles a piece on every refurnish.
- **`test_window_sign`'s control moves to the sign's WALL form.** It proved
  the headroom line still counts a low piece by lowering the window sign
  itself, and would have failed for this change rather than for the rule it
  guards. Found by running the window tests against a scratch copy with this
  release applied: `assert 13 == 13 + 1`.

**Tests:** `test_deli_window.py`, 11.
- **9 fail on 0.200.0.**
- **2 guards pass either side:** furnish's fixed point on the six delis,
  and the stores' signs where they were.
- `test_window_sign.py`'s moved control passes either side.

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.200.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.200.0] - a deli's case asks for Zoo's deli case"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.201.0")
    print("Deli Counter 0.201.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
