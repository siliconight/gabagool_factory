"""Zoo 1.123.0 on a CLONE (<repo>): a fixtures build can leave out named anchor types (`--skip-fixture-types`), so a
shell whose street band names it builds no lit door box (the walker's walk of cold run 9386, finding 1: "in real life
this would be 1 sign"). Anchored; refuses on a miss.

    python edit_zoo_skip_types.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("zoo_keeper/core/fixtures.py", [
    ('''def plan(manifest: dict, types=None) -> dict:
    """The fixture build plan for a lights manifest.

    ``types``: optional iterable of anchor types to include (default: every
    type in FIXTURES). Returns::''',
     '''def plan(manifest: dict, types=None, skip=None) -> dict:
    """The fixture build plan for a lights manifest.

    ``types``: optional iterable of anchor types to include (default: every
    type in FIXTURES). ``skip``: optional iterable of anchor types to leave
    out, whatever ``types`` says (1.123.0) -- a caller that wants everything
    but one kind names that kind, not every other: Level Factory leaves out a
    shell's ``sign`` when its street band names the business, one sign a
    building (the walker, cold run 9386). Returns::'''),
    ('''    wanted = set(types) if types else set(FIXTURES)
    placements, skipped, counts = [], [], {}''',
     '''    wanted = set(types) if types else set(FIXTURES)
    left_out = set(skip or ())
    placements, skipped, counts = [], [], {}'''),
    ('''        if t not in wanted:
            skipped.append({"id": aid, "type": t,
                            "reason": "filtered out by --fixture-types"})
            continue''',
     '''        if t in left_out:
            skipped.append({"id": aid, "type": t,
                            "reason": "left out by --skip-fixture-types"})
            continue
        if t not in wanted:
            skipped.append({"id": aid, "type": t,
                            "reason": "filtered out by --fixture-types"})
            continue'''),
])
edit("zoo_keeper/bpylayer/build.py", [
    ('''    plan = fixtures_mod.plan(lights_manifest, types=opts.get("types"))''',
     '''    plan = fixtures_mod.plan(lights_manifest, types=opts.get("types"), skip=opts.get("skip"))'''),
])
edit("tools/zoo_cli.py", [
    ('''    ap.add_argument("--sign-pack", dest="sign_pack",''',
     '''    ap.add_argument("--skip-fixture-types", dest="skip_fixture_types",
                    help="with --fixtures: comma list of anchor types to leave "
                         "out whatever --fixture-types says (1.123.0), e.g. "
                         "'sign' for a shell whose street band already names "
                         "the business -- one sign a building")
    ap.add_argument("--sign-pack", dest="sign_pack",'''),
    ('''    types = None
    if args.fixture_types:
        types = [t.strip() for t in args.fixture_types.split(",") if t.strip()]
''',
     '''    types = None
    if args.fixture_types:
        types = [t.strip() for t in args.fixture_types.split(",") if t.strip()]
    skip = None
    if getattr(args, "skip_fixture_types", None):
        skip = [t.strip() for t in args.skip_fixture_types.split(",") if t.strip()]
'''),
    ('''        print(json.dumps(fixtures_mod.plan(manifest, types=types),''',
     '''        print(json.dumps(fixtures_mod.plan(manifest, types=types, skip=skip),'''),
    ('''                 "seed": args.seed, "types": types,''',
     '''                 "seed": args.seed, "types": types, "skip": skip,'''),
])

TEST = '''"""A fixtures build leaves out named anchor types (1.123.0): one sign a building, the walker walking cold run 9386 --
"in real life this would be 1 sign". FAILS ON 1.122.0, whose `plan` takes no `skip`."""
from zoo_keeper.core import fixtures


def _manifest():
    return {"light_manifest_version": "1.1.0", "building_id": "shop", "anchors": [
        {"id": "ext_0_S_sign", "type": "sign", "pos": [-3.5, -9.35, 2.55], "rot_y": 270.0, "size": [2.4, 0.6]},
        {"id": "ceiling_0", "type": "fluorescent", "pos": [0.0, 0.0, 3.0]}]}


def test_a_skipped_type_builds_nothing_and_says_why():
    p = fixtures.plan(_manifest(), skip=["sign"])
    assert {pl["type"] for pl in p["placements"]} == {"fluorescent"}
    assert any(s["id"] == "ext_0_S_sign" and "skip-fixture-types" in s["reason"] for s in p["skipped"])


def test_no_skip_builds_the_door_box_as_before():
    p = fixtures.plan(_manifest())
    assert {pl["type"] for pl in p["placements"]} == {"fluorescent", "sign"}
'''
(R / "tests" / "test_fixture_skip.py").write_text(TEST, encoding="utf-8", newline="\n")
print("fixtures.plan(skip=), --skip-fixture-types; tests/test_fixture_skip.py")
