"""Zoo 1.6.0 -- an anchor that says its hardware already stands gets none.

Anchored patch; asserts each block matches exactly once and refuses on a miss.

WHY. Lot 0.79.0 derives its streetlight light anchors FROM the streetlight
poles `site_furniture` stands, so pole and light are coincident by
construction. `FIXTURES["streetlight"]` would build a second pole inside the
first the day a site-level fixture job exists. The manifest now says so --
`"hardware": "slot:cover_12"` -- and this is the reader for that field, so
it is a contract rather than an unread note (CLAUDE.md: an unused parameter
is an unfinished thought).
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FX = ROOT / "zoo" / "zoo_keeper" / "core" / "fixtures.py"


def _apply(path, pairs):
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit(f"REFUSED: {path} has mixed line endings "
                         f"({crlf} CRLF of {lf} LF)")
    eol = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    if eol == "\r\n":
        text = text.replace("\r\n", "\n")
    for i, (old, new) in enumerate(pairs):
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"REFUSED: anchor {i} matches {n} times, not 1")
        text = text.replace(old, new, 1)
    out = text.replace("\n", eol) if eol == "\r\n" else text
    path.write_bytes(out.encode("utf-8"))
    print(f"[patch] {path.name}: {len(pairs)} block(s), "
          f"{len(raw)} -> {len(out.encode('utf-8'))} bytes, eol={eol!r}")


OLD = '''        if t in HARDWARE_ELSEWHERE:
            skipped.append({"id": aid, "type": t,
                            "reason": "hardware built elsewhere: %s"
                                      % HARDWARE_ELSEWHERE[t]})
            continue
'''

NEW = '''        if t in HARDWARE_ELSEWHERE:
            skipped.append({"id": aid, "type": t,
                            "reason": "hardware built elsewhere: %s"
                                      % HARDWARE_ELSEWHERE[t]})
            continue
        # THIS ANCHOR\'S LAMP IS ALREADY STANDING. `HARDWARE_ELSEWHERE` is a
        # rule about a TYPE; this is one anchor saying that the thing the
        # light appears to come from exists in the scene already and naming
        # it. Lot 0.79.0 derives each `streetlight` anchor from the pole
        # `site_furniture` stands and tags it `"hardware": "slot:cover_12"`,
        # so building the species here would put a second pole inside the
        # first. The same type on a manifest with no such tag still gets
        # its hardware, which is what a building\'s own anchors want.
        if a.get("hardware"):
            skipped.append({"id": aid, "type": t,
                            "reason": "hardware already placed: %s"
                                      % str(a.get("hardware"))})
            continue
'''


def main():
    if not FX.exists():
        raise SystemExit(f"REFUSED: {FX} not found")
    _apply(FX, [(OLD, NEW)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
