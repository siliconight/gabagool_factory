"""Level Factory 0.154.0's release: VERSION and the CHANGELOG entry.

    python patch_lf_0154_release.py

Anchored on VERSION (b'0.153.0') and on CHANGELOG.md's head (632,510 bytes,
LF, as read 2026-10-07).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

HEAD = "## [0.153.0] - The brief's pacing reaches Lot, and Lot's verdict reaches the operator\n"
ENTRY = """## [0.154.0] - The contract's step-up reaches Laser Tag's crew

**Roadmap 203.** Cold run 9194's crew wedged leaving bank_branch_a04's vault, at
a stair ramp's open side 0.118 m high: route completion 8% and 0% on the two
candidates that drew that bank. The agent contract gives the player
`max_step_up_m` 0.5, and says a transition above
`clearances.unassisted_step_max_m` (0.1025) needs the consumer's step-up.
Laser Tag's crew had none. Laser Tag 0.24.0 steps up to its scenario's
`player_max_step_up_m`, and this release fills it from the contract.

**The seam.**
- `packages.validation.agent_contract._FIELDS` maps
  `characters.player.max_step_up_m` to `player_max_step_up_m`.
- `adapters.laser_tag._STOCK_SCENARIO` carries the fallback, 0.5 (the
  contract's own).
- This is the same road the radius, height, eye and walk speed travel
  (roadmap 123). A Deli Counter checkout's contract wins over the stock, and
  a job's own scenario wins over both.

**Measured, with Laser Tag 0.24.0** on 9194's two staged evaluation
projects (same level, seed and 25 runs):
- seed_9054: completion 0.08 -> 0.84, PlayerStuck 1,306 -> 4.
- seed_9256: completion 0.00 -> 0.84, PlayerStuck 2,366 -> 7.
- The step-up-off control reproduces 9194's reports exactly.
- Record: `docs/findings/stair_step_up/` at the factory root.

**Tests:** `tests/unit/test_step_up_reaches_the_crew.py`, 4. On 0.153.0 all 4
fail: the field is not read, not stocked, and refused by `_write_scenario` as
unknown. `test_agent_contract_seam.py`'s cross-repo check, that every stock key
is a real `@export` in Laser Tag's scenario, passes against Laser Tag 0.24.0.

**Suite:** 2,002 passed, 14 skipped, 1 xfailed (exit 0). That is 0.153.0's
1,997, these 4, and one more case of `test_sibling_locator`, which runs once
per source file.

"""


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.153.0", repr(v)
    c = (LF / "CHANGELOG.md").read_bytes()
    assert len(c) == 632510 and b"\r\n" not in c, len(c)
    text = c.decode("utf-8")
    assert text.startswith(HEAD) and text.count(HEAD) == 1
    (LF / "VERSION").write_bytes(b"0.154.0")
    (LF / "CHANGELOG.md").write_bytes((ENTRY + text).encode("utf-8"))
    print("Level Factory 0.154.0: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
