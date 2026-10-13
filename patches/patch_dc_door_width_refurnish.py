"""Deli Counter 0.214.0, third edit: the library refurnished around its wider doors, and the one count that moved.

Applied after `patch_dc_door_width.py` and `patch_dc_door_width_vault_note.py`, in the same release. The library is
held to be a fixed point of the furnishing pass (`test_wall_backing`, `test_club_fixtures`): strip what
`level_design.furnish` wrote, furnish again, and nothing moves. Widening a door moves what furnish puts beside
it, so after the door migration the full suite failed both fixed-point tests on `cr_gas`.

Attributed before anything was written (the factory's `docs/findings/door_widths/refurnish_delta.py`): a
refurnish moves 8 specs, every one a spec whose doors changed.
  cr_gas, foundry_heist_vertical, gas_station, gas_street, gs_corner_station   pieces move, none lost
  cr_pawn                                                                      a cartons stack and a floor safe lost
  stop_n_go                                                                    its cigarette rack lost
  rowhouse_raid                                                                four chair sets gained
`migrate_furnish_recipes.py --check`'s own summary is NOT a measure of this: it reads -7,923 / +7,819 on 0.213.0,
where the library is a fixed point, because its two counters count different things.

stop_n_go's rack stood against the north wall of its back room, 0.96 m from `rear_service`, which widened from
1.0 to 1.25 m; refurnished, it is placed no more, and `test_club_fixtures` pins the library's cigarette
machines at 119. The pin moves to 118 with the reason beside it, as 0.202.0 moved it from 121.

This runs `migrate_furnish_recipes.py` (it writes only the specs that change, in the library's indent=1 form --
all 8 were in it), then the pin's anchored edit, sha16-pinned. The 8 shells are rebuilt after
(`build.py specs/<name>.json`).

    python patches/patch_dc_door_width_refurnish.py
"""
import hashlib
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SHA = {"test_club_fixtures.py": "5523d0942b4a2d43"}
REFURNISHED = ["cr_gas", "cr_pawn", "foundry_heist_vertical", "gas_station", "gas_street", "gs_corner_station",
               "rowhouse_raid", "stop_n_go"]

PIN_OLD = ("    # 121 -> 119 cigarette machines (0.202.0): two stood against open room\n"
           "    # edges, and no wall in their rooms holds them\n"
           "    assert counts == {\"dartboard\": 11, \"cigarettes\": 119}, counts\n")
PIN_NEW = ("    # 121 -> 119 cigarette machines (0.202.0): two stood against open room\n"
           "    # edges, and no wall in their rooms holds them. 119 -> 118 (0.214.0):\n"
           "    # stop_n_go's back-room rack stood on its north wall 0.96 m from\n"
           "    # `rear_service`, which widened 1.0 -> 1.25 m to the contract's door, and\n"
           "    # refurnished beside it the rack is placed no more\n"
           "    assert counts == {\"dartboard\": 11, \"cigarettes\": 118}, counts\n")


def main():
    assert (DC / "VERSION").read_bytes().strip() == b"Deli Counter 0.214.0", (DC / "VERSION").read_bytes()
    rel = "test_club_fixtures.py"
    raw = (DC / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    assert b"\r\n" not in raw, (rel, "is LF")
    text = raw.decode("utf-8")
    assert text.count(PIN_OLD) == 1, (rel, "anchor", text.count(PIN_OLD))
    run = subprocess.run([sys.executable, "migrate_furnish_recipes.py"], cwd=DC, check=True,
                         capture_output=True, text=True)
    print(run.stdout.rstrip())
    moved = subprocess.run(["git", "-C", str(DC), "diff", "--name-only", "--", "specs/"], check=True,
                           capture_output=True, text=True).stdout.split()
    for name in REFURNISHED:
        assert "specs/%s.json" % name in moved, ("not changed against HEAD", name)
    (DC / rel).write_bytes(text.replace(PIN_OLD, PIN_NEW).encode("utf-8"))
    print("Deli Counter 0.214.0: the library refurnished (%d specs); the cigarette pin 119 -> 118"
          % len(REFURNISHED))


if __name__ == "__main__":
    main()
