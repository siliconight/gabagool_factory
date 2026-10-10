"""Patina 0.29.2: no conduit to a sign's face (roadmap 220). See
`patina_sign_conduit/CHANGELOG_0.29.2.md`.

Anchored edits (every anchor once; nothing written until all match):
  patina/anchors.py      conduit_targets' default kinds lose "sign", and its docstring says why
  patina/cli.py          the no-conduit note tells a missing lights manifest from one with no wall pack
  patina/version.py      0.29.2
  tests/test_anchors.py  the target list loses the sign
Copies the new test; CHANGELOG and VERSION.

    python patch_patina_sign_conduit.py [--suite-pending]
    PATINA_ROOT=<copy> python patch_patina_sign_conduit.py --draft

`--draft` lets the changelog's RESULT_ placeholders through, against a PATINA_ROOT copy only.
`--suite-pending` lets exactly RESULT_SUITE through into the repo, filled in by hand after the
suite runs and before the commit.
"""
import os
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
PA = pathlib.Path(os.environ.get("PATINA_ROOT") or HERE.parent / "patina")
SRC = HERE / "patina_sign_conduit"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

TARGETS_OLD = '''def conduit_targets(light_manifest, up_axis: int,
                    kinds=("wall_pack", "sign")) -> tuple:
    """``((pos, anchor_id), ...)`` for the exterior fixtures conduit runs to.

    DC derives a wall pack over every exterior door and one storefront sign
    from the real openings, and puts them in ``<name>.lights.json`` already
    stood proud of the wall face (``_WALL_PACK_OUT``, ``_SIGN_OUT``). Taking
    those positions as given is deliberate: it means the conduit needs no face
    math of its own, and no second chance to get a normal backwards.

    Interior kinds (``fluorescent``, ``window``) are not conduit targets --
    nothing runs up an outside wall to a ceiling strip light.
    """
'''
TARGETS_NEW = '''def conduit_targets(light_manifest, up_axis: int,
                    kinds=("wall_pack",)) -> tuple:
    """``((pos, anchor_id), ...)`` for the exterior fixtures conduit runs to.

    DC derives a wall pack over every exterior door and puts it in
    ``<name>.lights.json`` already stood proud of the wall face
    (``_WALL_PACK_OUT``). Taking that position as given is deliberate: it
    means the conduit needs no face math of its own, and no second chance to
    get a normal backwards.

    Interior kinds (``fluorescent``, ``window``) are not conduit targets --
    nothing runs up an outside wall to a ceiling strip light.

    NOR IS A SIGN (0.29.2, roadmap 220). RETRACTED, kept: ``sign`` was a
    target until 0.29.1. DC stands a sign's anchor on the sign's FACE,
    ``_SIGN_OUT`` (0.2 m) proud of the wall, and hangs every sign it derives
    over a door. The run therefore stood 0.2 m out in the air, and
    ``openings.apply``, starting it above the door head as it should, left a
    0.27 m stub from the head to the middle of the lit face, standing through
    it: the light bar walked on strip_club_a01's door sign in cold runs 9213
    and 9217, and ordered on all three signed buildings of club_block_014. A
    cabinet sign is fed through the wall behind it; nothing runs up the
    outside of the wall to its face.
    """
'''

CLI_OLD = '''            conduits = anchors.conduit_targets(scene.lights, up_axis)
            if not conduits and "exterior_light" in (
                    args.anchor_kinds or anchors.ANCHOR_KINDS):
                print("[patina] no <name>.lights.json beside this shell: no "
                      "conduit runs emitted (they run TO a fixture)",
                      file=sys.stderr)
'''
CLI_NEW = '''            conduits = anchors.conduit_targets(scene.lights, up_axis)
            if not conduits and "exterior_light" in (
                    args.anchor_kinds or anchors.ANCHOR_KINDS):
                # 0.29.2: with no sign target, a manifest whose only exterior
                # fixture is a sign orders none too -- and is not missing
                why = ("no <name>.lights.json beside this shell"
                       if scene.lights is None
                       else "no wall pack in <name>.lights.json")
                print("[patina] " + why + ": no conduit runs emitted (they "
                      "run TO a fixture)", file=sys.stderr)
'''

TEST_OLD = '''    got = anchors.conduit_targets(_LIGHTS, 1)
    assert [t[1] for t in got] == ["ext_0_N_pack_1", "ext_0_S_sign"]
'''
TEST_NEW = '''    got = anchors.conduit_targets(_LIGHTS, 1)
    # 0.29.2: the sign left the list -- a conduit to a sign's FACE stood 0.2 m
    # off the wall and through the face (tests/test_sign_conduit.py)
    assert [t[1] for t in got] == ["ext_0_N_pack_1"]
'''

VER_OLD = '__version__ = "0.29.1"\n'
VER_NEW = '__version__ = "0.29.2"\n'


def _staged(path, pairs):
    raw = path.read_bytes()
    assert b"\r" not in raw, (path, "has CR; this patch writes LF")
    s = raw.decode("utf-8")
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, s.count(old), old[:70])
        s = s.replace(old, new)
    return s.encode("utf-8")


def main():
    if DRAFT and not os.environ.get("PATINA_ROOT"):
        sys.exit("refusing: --draft is for a PATINA_ROOT copy, never the repo")
    assert (PA / "VERSION").read_bytes() == b"Patina 0.29.1", (PA / "VERSION").read_bytes()
    test_dst = PA / "tests" / "test_sign_conduit.py"
    assert not test_dst.exists(), "tests/test_sign_conduit.py already exists"
    entry = (SRC / "CHANGELOG_0.29.2.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.29.2] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {
        PA / "patina" / "anchors.py": _staged(PA / "patina" / "anchors.py", [(TARGETS_OLD, TARGETS_NEW)]),
        PA / "patina" / "cli.py": _staged(PA / "patina" / "cli.py", [(CLI_OLD, CLI_NEW)]),
        PA / "patina" / "version.py": _staged(PA / "patina" / "version.py", [(VER_OLD, VER_NEW)]),
        PA / "tests" / "test_anchors.py": _staged(PA / "tests" / "test_anchors.py", [(TEST_OLD, TEST_NEW)]),
    }
    ch = PA / "CHANGELOG.md"
    cl = ch.read_bytes()
    assert b"\r" not in cl, "CHANGELOG.md is not LF"
    text = cl.decode("utf-8")
    head = "## [0.29.1]"
    assert text.count(head) == 1, text.count(head)
    # every anchor matched: now write
    for p, raw in writes.items():
        p.write_bytes(raw)
    shutil.copyfile(SRC / "test_sign_conduit.py", test_dst)
    ch.write_bytes(text.replace(head, entry.rstrip("\n") + "\n\n" + head).encode("utf-8"))
    (PA / "VERSION").write_bytes(b"Patina 0.29.2")
    print("applied Patina 0.29.2" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
