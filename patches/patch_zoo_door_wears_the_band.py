"""Zoo 1.79.0: a door box can wear the sign pack its building's band wears.

The walker, 2026-10-06, option A on `docs/findings/two_names_one_building/`:
one name list on both signs. Level Factory 0.148.0 deals each shell one
business and builds the band from its Pixelcoat pack; this release lets the
door box wear the SAME pack, so the two signs on one building are one
business by construction rather than by two tables agreeing.

  * `zoo_cli --fixtures ... --sign-pack DIR` -- the pack directory.
  * `build_fixtures` hands it to every `sign_box` placement of the build (a
    fixtures build is one shell, and a shell is one business), and to
    nothing else.
  * `sign_box` loads that pack before it would pick one from a skin
    library, and wears it through the branch that already dressed a face
    from a pack. Without one, nothing changes: the face is named from
    `storefront_names`, which Pixelcoat 0.61.0's sign profile now mirrors.

    python patch_zoo_door_wears_the_band.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZOO = ROOT / "zoo"

EDITS = {
    ZOO / "tools/zoo_cli.py": [
        ('''                         "whose interior fixtures are already baked "
                         "per-building.")
''',
         '''                         "whose interior fixtures are already baked "
                         "per-building.")
    ap.add_argument("--sign-pack", dest="sign_pack",
                    help="with --fixtures: a Pixelcoat sign pack directory "
                         "every door box of this build wears -- the business "
                         "the building's street band was dealt (1.79.0), so "
                         "its two signs name one business")
'''),
        ('''        options={"save_blend": not args.no_blend, "clear_scene": True,
                 "seed": args.seed, "types": types})
''',
         '''        options={"save_blend": not args.no_blend, "clear_scene": True,
                 "seed": args.seed, "types": types,
                 "sign_pack": (os.path.abspath(args.sign_pack)
                               if getattr(args, "sign_pack", None) else None)})
'''),
    ],
    ZOO / "zoo_keeper/bpylayer/build.py": [
        ('''        if p.get("business"):
            sp_plan["business"] = p["business"]
''',
         '''        if p.get("business"):
            sp_plan["business"] = p["business"]
        # 1.79.0: the business the building's street band was dealt, as its
        # pack; a door box wears it, so one building's two signs are one name
        if species == "sign_box" and opts.get("sign_pack"):
            sp_plan["sign_pack"] = opts["sign_pack"]
'''),
    ],
    ZOO / "zoo_keeper/recipes/sign_box.py": [
        ('''    pack = None
    skins_dir, skin_theme = materials.get_skin_library()
    if skins_dir:
        from ..core import skins as skinlib
        pack = skinlib.pick_pack(
''',
         '''    pack = None
    if plan.get("sign_pack"):
        # 1.79.0: the business Level Factory dealt this building -- the pack
        # its street band wears -- so the door and the band are one name
        from ..core import skins as skinlib
        pack = skinlib.load_pack(str(plan["sign_pack"]))
    skins_dir, skin_theme = materials.get_skin_library()
    if pack is None and skins_dir:
        from ..core import skins as skinlib
        pack = skinlib.pick_pack(
'''),
    ],
}

TEST = '''"""A door box can wear its building's band (1.79.0): one name on both signs.

The walker, 2026-10-06, option A. Level Factory 0.148.0 deals each shell one
business and passes its Pixelcoat pack to the shell's fixtures build; the
door box wears it. The Blender-bound code is read as source, as
`test_car_forms` does.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "zoo_cli_door", os.path.join(HERE, "..", "tools", "zoo_cli.py"))
zoo_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(zoo_cli)


def _src(*parts):
    return open(os.path.join(HERE, "..", *parts), encoding="utf-8").read()


def test_the_cli_takes_a_sign_pack(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["zoo_cli", "--fixtures", "x.lights.json",
                                      "--out", "o", "--sign-pack", "packs/sign_jawns_hoagies"])
    args = zoo_cli.parse_args()
    assert args.sign_pack == "packs/sign_jawns_hoagies"
    assert "\\"sign_pack\\": (os.path.abspath(args.sign_pack)" in _src("tools", "zoo_cli.py")


def test_only_a_door_box_is_given_the_pack():
    src = _src("zoo_keeper", "bpylayer", "build.py")
    assert 'if species == "sign_box" and opts.get("sign_pack"):' in src


def test_the_door_box_wears_the_given_pack_before_it_would_pick_one():
    src = _src("zoo_keeper", "recipes", "sign_box.py")
    given = src.index('if plan.get("sign_pack"):')
    picked = src.index("skinlib.pick_pack(")
    assert given < picked
    assert "if pack is None and skins_dir:" in src
'''


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    test = ZOO / "tests" / "test_door_wears_the_band.py"
    assert not test.exists()
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))
    test.write_bytes(TEST.encode("utf-8"))
    print("wrote", test.relative_to(ROOT))


if __name__ == "__main__":
    main()
