"""Deli Counter 0.190.0, the stair-width rule's second half: every generator
draws its flights at `STAIR_FLIGHT_WIDTH`, not only the two that drew 0.9 m.

`test_stair_flight_width.py::test_no_preset_draws_a_flight_narrower_than_a_corridor`
failed after `patch_dc_stair_flight_width.py` on the two that draw 1.0 m:
`pawn_shop` and `suburban_safehouse`. The library's 1.0 m flights from them
(cr_pawn and night_pawn) connect at 8 of 8 grid origins as built, so their
frozen specs are left as they are. A generator still draws the one width
that was measured at 8 of 8 and sits a cell over the contract's corridor.

    python patch_dc_stair_flight_width_all.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRESETS = ROOT / "deli_counter" / "presets.py"

SAFE_OLD = '''    spec["stairs"] = [{"x": 5.0, "y": 4.0, "from_story": stair_lo, "to_story": 1, "width": 1.0, "run": 3.5, "style": "switchback", "cut_slabs": True}]
'''
SAFE_NEW = '''    spec["stairs"] = [{"x": 5.0, "y": 4.0, "from_story": stair_lo, "to_story": 1, "width": STAIR_FLIGHT_WIDTH, "run": 3.5, "style": "switchback", "cut_slabs": True}]
'''
PAWN_OLD = '''    spec["stairs"] = [{"x": 2.5, "y": 5.5, "from_story": 0, "to_story": 1,
                       "width": 1.0, "run": run, "style": "switchback", "cut_slabs": True}]
'''
PAWN_NEW = '''    spec["stairs"] = [{"x": 2.5, "y": 5.5, "from_story": 0, "to_story": 1,
                       "width": STAIR_FLIGHT_WIDTH, "run": run,
                       "style": "switchback", "cut_slabs": True}]
'''

EDITS = {PRESETS: [(SAFE_OLD, SAFE_NEW), (PAWN_OLD, PAWN_NEW)]}


def main():
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path.name}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
