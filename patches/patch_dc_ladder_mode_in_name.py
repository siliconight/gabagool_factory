"""Carry a ladder's `placement_mode` into its emitted node name.

The worldskin chooses a ladder's metal from the name -- rusted outside, clean
inside (the walker's call, 2026-09-23) -- and the name is the only channel it
has: `zoo_worldskin.gd` is an IMPORT post-processor handed one GLB, with no
access to the spec that authored the ladder.

The convention already exists in this file: `stair<n>col_` and `stair<n>ramp_`
carry their kind on the index token, and `zoo_worldskin._is_visual_stair`
reads them. This does the same with `ladder<n>ext_`.

NOTHING DOWNSTREAM PARSES THESE NAMES -- checked across deli_counter, lot,
level_factory and lasertag before writing: the gameplay side addresses a
ladder through the `LADDER_<n>` marker and the `ladder_<n>` id, which are
emitted separately and are untouched here.

HOLD UNTIL THE COLD RUN ENDS. Applying it mid-run would void the zero.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "deli_counter" / \
    "deli_counter.py"

# ---------------------------------------------------------------- anchor 1
A1 = """        H = self.s.story_height
        for li, ld in enumerate(self.s.ladders):
            along_x = ld.facing in ("N", "S")   # rails spread along X if facing N/S
"""

N1 = """        H = self.s.story_height
        for li, ld in enumerate(self.s.ladders):
            # WEATHER, IN THE NAME. The worldskin dresses an exterior ladder
            # in the theme's rusted steel and an interior one in a dark rail
            # against a bright rung, and it is handed one GLB with no sight of
            # this spec -- so the only channel is the node name. Same shape as
            # `stair<n>col_` / `stair<n>ramp_` above, which carry their kind on
            # the index token for the same reason.
            #
            # `placement_mode` is authored per ladder and defaults to
            # "interior" on the dataclass, so an unset one is correctly
            # interior: measured across the spec library, 109 ladders are
            # interior (52 explicit, 54 unset, 3 shaft) against 3 exterior.
            # A platform ladder counts as exterior -- it is the one on the
            # outside of a tank or a dock, and it weathers.
            mode = getattr(ld, "placement_mode", "interior")
            tag = "ext" if mode in ("exterior_wall", "platform") else ""
            along_x = ld.facing in ("N", "S")   # rails spread along X if facing N/S
"""

# ---------------------------------------------------------------- anchor 2
A2 = """                    self._box(f"ladder{li}_rail_{s}_{sgn}", rc, rs, self.VISUAL,
                              role="ladder")
"""

N2 = """                    self._box(f"ladder{li}{tag}_rail_{s}_{sgn}", rc, rs,
                              self.VISUAL, role="ladder")
"""

# ---------------------------------------------------------------- anchor 3
A3 = """                    self._box(f"ladder{li}_rung_{s}_{r}", cc, cs, self.VISUAL,
                              role="ladder")
"""

N3 = """                    self._box(f"ladder{li}{tag}_rung_{s}_{r}", cc, cs,
                              self.VISUAL, role="ladder")
"""

EDITS = ((A1, N1), (A2, N2), (A3, N3))


def _eol(data: bytes) -> str:
    crlf = data.count(b"\r\n")
    bare = data.count(b"\n") - crlf
    if crlf and bare:
        raise SystemExit(f"REFUSED: mixed endings, {crlf} CRLF and {bare} LF")
    return "\r\n" if crlf else "\n"


def main() -> None:
    data = TARGET.read_bytes()
    eol = _eol(data)
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(EDITS, 1):
        o = old.replace("\n", eol)
        n = new.replace("\n", eol)
        hits = text.count(o)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(o, n)
    out = text.encode("utf-8")
    if _eol(out) != eol:
        raise SystemExit("REFUSED: would change the file's line endings")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes "
          f"(+{len(out) - before}), endings unchanged ({eol!r})")


if __name__ == "__main__":
    main()
