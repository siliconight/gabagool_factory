"""Level Factory 0.150.0: the words a brief reaches for a deli resolve.

    python patch_lf_deli_words.py tests    # the test first: it must fail
    python patch_lf_deli_words.py code     # then the aliases

Anchored as read 2026-10-07 (both LF):
  * `level_factory/tests/unit/test_dc_preset_registry.py` (6,247 bytes): one
    test after `test_the_walkers_three_kinds_resolve_from_a_briefs_words`;
  * `level_factory/adapters/deli_counter/__init__.py` (14,810 bytes): four
    rows at the end of `_ARCHETYPE_ALIASES`.

Refused since 0.146.0: `deli`, `night_deli` and `stop_n_go`, "outside the
three kinds, and the detail audit of 2026-10-06 lists them as open". The
delis are no longer open there: Deli Counter 0.199.0-0.201.0 stop the case
at its wall, build it as Zoo 1.81.0's `deli_case` and hang a beer sign and
posters in the window, generated and drawn alike. `stop_n_go` is the
library's Flappahs store by another name (0.147.0 dresses it in FLAPPAHS).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"
TEST = LF / "tests" / "unit" / "test_dc_preset_registry.py"
ADAPTER = LF / "adapters" / "deli_counter" / "__init__.py"

TEST_ANCHOR = '''def test_the_words_left_refused_stay_refused():
'''
TEST_NEW = '''def test_a_delis_words_resolve_to_the_corner_deli():
    """0.150.0. Refused since 0.146.0 while the delis lacked the store's
    detail; Deli Counter 0.199.0-0.201.0 and Zoo 1.81.0 gave it them. A
    brief that asks for a deli in plain words gets `corner_deli`, and
    `stop_n_go`, the library's Flappahs store by another name, the store."""
    for alias in ("deli", "delicatessen", "night_deli"):
        assert _preset_for(alias) == "corner_deli", alias
    assert _preset_for("stop_n_go") == "convenience_store"
    assert _preset_for("corner_deli") == "corner_deli"


def test_the_words_left_refused_stay_refused():
'''

CODE_ANCHOR = '''    "movie_rental": "video_store",
}
'''
CODE_NEW = '''    "movie_rental": "video_store",
    # THE CORNER DELI (0.150.0). Refused from 0.146.0 while the delis lacked
    # the store's detail; Deli Counter 0.199.0-0.201.0 stop the case at its
    # wall, build it as Zoo 1.81.0's `deli_case` and hang a beer sign and
    # posters in the window, generated and drawn alike. `stop_n_go` is the
    # library's Flappahs store by another name (0.147.0 dresses it in
    # FLAPPAHS). `corner_store` stays refused, above: as often the deli as
    # the Flappahs store.
    "deli": "corner_deli", "delicatessen": "corner_deli",
    "night_deli": "corner_deli",
    "stop_n_go": "convenience_store",
}
'''


def _apply(path, size, old, new):
    data = path.read_bytes()
    assert len(data) == size, "%s is %d bytes, not the %d read; refusing" % (path.name, len(data), size)
    assert b"\r\n" not in data, "CRLF in %s; refusing" % path.name
    text = data.decode("utf-8")
    assert text.count(old) == 1, "%s: anchor found %d times" % (path.name, text.count(old))
    path.write_bytes(text.replace(old, new).encode("utf-8"))
    print("%s: %d -> %d bytes" % (path.name, size, len(path.read_bytes())))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    if which == "tests":
        _apply(TEST, 6247, TEST_ANCHOR, TEST_NEW)
    elif which == "code":
        _apply(ADAPTER, 14810, CODE_ANCHOR, CODE_NEW)
    else:
        raise SystemExit("say `tests` or `code`")


if __name__ == "__main__":
    main()
