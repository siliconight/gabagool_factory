"""Deli Counter 0.283.0: a bank's lobby hangs its printed offers, and its teller line names the bank.

Run in a Deli Counter clone's root (on 0.282.0). Every anchor is asserted to occur exactly once; nothing is written
on a miss.
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).parent
R = pathlib.Path.cwd()


def edit(rel, pairs):
    p = R / rel
    t = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n")
    for a, b in pairs:
        assert t.count(a) == 1, (rel, t.count(a), a[:80])
        t = t.replace(a, b)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print(p, "edited")


edit("level_design.py", [
# the printed offers: a run of Zoo 1.137.0's `poster_wall` form `bank`
('''    _piece("poster_wall_store", ((1.6, 0.01, 0.6), (1.0, 0.01, 0.6),''',
 '''    # A BANK'S PRINTED OFFERS (0.283.0, Zoo 1.137.0's `bank` family: the
    # walker's bank comps, the Christmas Club and the rate board): framed,
    # hung square and level at the eye, 0.30 m apart -- runs of two, three
    # and four 0.46 x 0.62 m sheets. A bank lobby's fixture, so nowhere else.
    # Its steps are the library's gentlest: each frame hangs level, and a
    # lobby's walls differ by 5 cm, not all at one height (the placement
    # guide's tell, `test_the_runs_do_not_all_hang_at_one_height`)
    _piece("poster_wall_bank", ((2.0, 0.01, 0.62), (1.25, 0.01, 0.62),
                                (2.75, 0.01, 0.62)), "wall", front=True,
           variants=4, form="bank", most=2, most_big=(150.0, 3),
           lift=_eye_height(), collision="none", distinct=True, off_glass=True,
           lift_steps=(-0.05, 0.0, 0.05)),
    _piece("poster_wall_store", ((1.6, 0.01, 0.6), (1.0, 0.01, 0.6),'''),
('''                   "fixtures": ("security_camera", "wall_clock")},''',
 '''                   "fixtures": ("security_camera", "wall_clock", "poster_wall_bank")},'''),
# the teller line names the bank its door sign names
('''def _room_containing(spec, story, x, y):''',
 '''#: THE WORDS A SIGN READS A BANK FROM: Zoo's `storefront_names` names a
#: building's door by the first kind whose words its business carries, and a
#: bank's are these -- wider than `lights.is_bank`'s, so a credit union's
#: teller line names it too.
_BANK_SIGN_WORDS = ("bank", "credit", "savings")
#: Zoo's bank names and the sign pylon's colourways: a line's sixteen variants
#: are every name in every colourway (`teller_line_forms.VARIANTS`).
_BANK_NAMES = 4
_SIGN_COLOURWAYS = 4


def bank_teller_variant(business):
    """The `teller_line` variant naming the bank its door sign does (Zoo
    1.137.0, `teller_line_forms.variant_for`): the sign is ``names[k % 4]`` in
    ``COLOURWAYS[(k // 7) % 4]``, ``k`` the crc32 of ``business``
    (`club_building_id`, the key the sign's anchor carries)."""
    import zlib
    k = zlib.crc32(str(business or "").encode("utf-8")) & 0xFFFFFFFF
    return k % _BANK_NAMES + _BANK_NAMES * ((k // 7) % _SIGN_COLOURWAYS)


def dress_bank_teller_lines(spec):
    """A bank's teller lines (0.283.0): Zoo 1.137.0's form `bank`, a
    nameboard over the windows, in the variant whose name and colours are the
    door sign's. A LINE is `_teller_lines`' -- 6 m and more, 2 m tall -- and
    only a line: `bank_tower_a01`'s three 3 m teller desks would each number
    their windows 1 and 2. A building whose sign is not a bank's dresses none.
    Returns how many volumes changed; a second call changes none."""
    import re
    business = club_building_id(spec)
    words = set(re.split(r"[^a-z]+", str(business).lower()))
    if not words & set(_BANK_SIGN_WORDS):
        return 0
    want = bank_teller_variant(business)
    changed = 0
    for v, _story, _axis in _teller_lines(spec):
        before = (v.get("form"), v.get("variant"))
        v["form"] = "bank"
        if want:
            v["variant"] = want
        else:
            v.pop("variant", None)
        if (v.get("form"), v.get("variant")) != before:
            changed += 1
    return changed


def _room_containing(spec, story, x, y):'''),
('''    added += place_fixtures(spec)
    # ...AND THE BINS AFTER THEM (0.266.0): every bin this pass or an earlier
    # one stood goes against a wall, and nothing else moves.''',
 '''    added += place_fixtures(spec)
    # A BANK'S TELLER LINE NAMES THE BANK (0.283.0), from the spec alone: it
    # moves nothing, so a line furnished by any release gets the same form
    dress_bank_teller_lines(spec)
    # ...AND THE BINS AFTER THEM (0.266.0): every bin this pass or an earlier
    # one stood goes against a wall, and nothing else moves.'''),
])

edit("tests/test_poster_walls.py", [
('''PIECES = {"poster_wall_club": "club", "poster_wall_bar": "bar", "poster_wall_store": "store"}''',
 '''PIECES = {"poster_wall_club": "club", "poster_wall_bar": "bar", "poster_wall_store": "store",
          "poster_wall_bank": "bank"}'''),
('''BAND = {"club": 0.64, "bar": 0.5, "store": 0.6}''',
 '''BAND = {"club": 0.64, "bar": 0.5, "store": 0.6, "bank": 0.62}'''),
])

for src, rel in (("test_bank_posters_teller.py", "tests/test_bank_posters_teller.py"),
                 ("migrate_bank_posters.py", "migrations/migrate_bank_posters.py")):
    dst = R / rel
    assert not dst.exists(), dst
    shutil.copyfile(HERE / src, dst)
    print(dst, "written")
