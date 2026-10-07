"""Level Factory 0.154.0: the contract's step-up reaches Laser Tag's crew
(roadmap 203).

    python patch_lf_step_up.py            # apply
    python patch_lf_step_up.py --check    # verify every anchor, write nothing

`agent_contract._FIELDS` maps `characters.player.max_step_up_m` to the
scenario field `player_max_step_up_m`, and the adapter's `_STOCK_SCENARIO`
carries its fallback (0.5, the contract's own), beside the radius, height, eye
and walk speed. Laser Tag 0.24.0 exports the field and steps up to it.

Anchored on, as read 2026-10-07:
  level_factory/packages/validation/agent_contract.py    4,871 bytes, LF
  level_factory/adapters/laser_tag/__init__.py          24,817 bytes, CRLF
A CRLF file is matched with its endings normalised and written back CRLF; a
mixed file is refused. Every anchor must match once; nothing is written until
every file matched.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

CONTRACT = [
    ("    \"player_walk_speed_mps\": \"walk_speed_mps\",\n",
     "    \"player_walk_speed_mps\": \"walk_speed_mps\",\n"
     "    # the step the player's controller lifts itself over (0.154.0, roadmap\n"
     "    # 203): Laser Tag 0.24.0's crew steps up to it\n"
     "    \"player_max_step_up_m\": \"max_step_up_m\",\n"),
]

ADAPTER = [
    ("    \"player_walk_speed_mps\": 4.0,\n",
     "    \"player_walk_speed_mps\": 4.0,\n"
     "    # THE CONTRACT'S STEP-UP (0.154.0, roadmap 203): `max_step_up_m`, the step\n"
     "    # the player's controller lifts itself over. Laser Tag's crew had none, and\n"
     "    # cold run 9194's bank crew wedged at a 0.118 m stair edge the contract's\n"
     "    # player walks on.\n"
     "    \"player_max_step_up_m\": 0.5,\n"),
]

FILES = [
    (LF / "packages" / "validation" / "agent_contract.py", 4871, CONTRACT),
    (LF / "adapters" / "laser_tag" / "__init__.py", 24817, ADAPTER),
]


def _load(path, size):
    data = path.read_bytes()
    assert len(data) == size, "%s is %d bytes, read at %d" % (path.name, len(data), size)
    crlf, lf = data.count(b"\r\n"), data.count(b"\n")
    assert crlf in (0, lf), "%s mixes endings (%d CRLF of %d lines); refused" % (path.name, crlf, lf)
    return data, data.decode("utf-8").replace("\r\n", "\n"), crlf == lf and lf > 0


def main():
    check = "--check" in sys.argv[1:]
    staged = []
    for path, size, edits in FILES:
        data, text, is_crlf = _load(path, size)
        for old, new in edits:
            assert text.count(old) == 1, "%s: anchor found %d times: %r" % (path.name, text.count(old), old[:70])
            text = text.replace(old, new)
        out = (text.replace("\n", "\r\n") if is_crlf else text).encode("utf-8")
        staged.append((path, data, out, is_crlf))
    for path, data, out, is_crlf in staged:
        tag = "CRLF" if is_crlf else "LF"
        if check:
            print("%s: every anchor matched once (%d -> %d bytes, %s, not written)" % (path.name, len(data), len(out), tag))
            continue
        path.write_bytes(out)
        print("%s: %d -> %d bytes (%s)" % (path.name, len(data), len(out), tag))


if __name__ == "__main__":
    main()
