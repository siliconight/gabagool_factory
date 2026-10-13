"""Deli Counter 0.213.0, before its commit: the six mid-rise Empties recorded UNJUDGED in the nav gate's baseline,
as the rowhome Empties are (factory roadmap 241).

`patch_dc_midrise.py` was applied and filled, and the repository's pre-commit gate (`check.py`) refused the
commit: `test_navgate_population.py::test_no_new_unjudged_shell` -- "these shells are newly UNJUDGED and are not
in the baseline: gs_midrise_a ... gs_midrise_f. Either give each a marker whose type ends in _spawn, or add it to
navgate_baseline.json with a reason." An Empty has no interior for a spawn marker to stand in, and the baseline
already says so for `gs_facade_rowhome` and the twelve rowhome Empties. So, anchored and pinned:
  navgate_baseline.json   six entries after `gs_empty_rowhome_l`, the last of the list; `counts.unjudged` 21 -> 27,
                          which `test_navgate_population.py` holds equal to the list's length
  CHANGELOG.md            one bullet in the 0.213.0 entry, and the same in `dc_midrise/CHANGELOG_0.213.0.md`

Read before it was written: the gate's output, `navgate_baseline.json`'s `counts` and the rowhome Empties'
entries, and `test_navgate_population.py`'s count checks. Both files LF.

    python patches/patch_dc_midrise_navgate.py
"""
import hashlib
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
ENTRY = HERE / "dc_midrise" / "CHANGELOG_0.213.0.md"
SHA = {"navgate_baseline.json": "95c5162c2a12e255", "CHANGELOG.md": "0a1a8b78a4cca334"}
NAMES = ["gs_midrise_%s" % c for c in "abcdef"]
REASON = ("a mid-rise Empty (Deli Counter 0.213.0, roadmap 241): facade-only, sealed, no interior for a spawn "
          "marker to stand in, so zero markers checked is the correct outcome -- the same call as "
          "gs_facade_rowhome and the rowhome Empties")

LAST_OLD = ('      "reason": "an Empty (Deli Counter 0.174.0, roadmap 106): facade-only, sealed, no interior for a '
            'spawn marker to stand in, so zero markers checked is the correct outcome -- the same call as '
            'gs_facade_rowhome (0.184.0, one of the six added)"\n'
            '    }\n'
            '  ],\n'
            '  "stair_failures": [\n')
LAST_NEW = LAST_OLD[:-len('    }\n  ],\n  "stair_failures": [\n')] + "".join(
    '    },\n'
    '    {\n'
    '      "shell": "%s",\n'
    '      "checked": 0,\n'
    '      "navigable": null,\n'
    '      "stairs_ok": true,\n'
    '      "reason": "%s"\n' % (n, REASON) for n in NAMES) + '    }\n  ],\n  "stair_failures": [\n'
COUNT_OLD = '    "unjudged": 21,\n'
COUNT_NEW = '    "unjudged": 27,\n'

BULLET_OLD = "  Each needs a capability this builder does not have yet.\n"
BULLET_NEW = (BULLET_OLD +
              "- **`navgate_baseline.json`** records the six UNJUDGED, as it records `gs_facade_rowhome` and the\n"
              "  twelve rowhome Empties: an Empty has no interior for a spawn marker to stand in, so the nav gate\n"
              "  checking zero markers is the correct outcome. `counts.unjudged` 21 -> 27.\n")


def _lf(path):
    raw = path.read_bytes()
    assert b"\r\n" not in raw, (path, "is not LF")
    return raw.decode("utf-8")


def main():
    writes = {}
    for rel, pairs in (("navgate_baseline.json", ((LAST_OLD, LAST_NEW), (COUNT_OLD, COUNT_NEW))),
                       ("CHANGELOG.md", ((BULLET_OLD, BULLET_NEW),))):
        p = DC / rel
        text = _lf(p)
        got = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
            text = text.replace(old, new)
        writes[p] = text
    entry = _lf(ENTRY)
    assert entry.count(BULLET_OLD) == 1, "the entry's anchor"
    writes[ENTRY] = entry.replace(BULLET_OLD, BULLET_NEW)
    # every anchor matched: now write
    for p, text in writes.items():
        p.write_bytes(text.encode("utf-8"))
    print("navgate_baseline.json: six mid-rise Empties recorded UNJUDGED, counts.unjudged 27")


if __name__ == "__main__":
    main()
