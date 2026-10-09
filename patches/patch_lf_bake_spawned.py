"""Level Factory 0.162.1: the light bake keeps the responders' car dynamic
(roadmap 212, found by cold run 9208).

The bake set every GLB sidecar to Static Lightmaps, the responders' cruiser
among them; measured on Godot 4.7 that gives its meshes gi_mode STATIC, and
a spawned static mesh outside the bake takes neither the lightmap nor the
probes. `mark_imports` sets the paths the themed site's `responders.json`
names to Dynamic (3) instead.

Anchored edits (every anchor once; refuses on a miss; nothing is written
until every anchor in every file matched):
- `packages/exporting/light_bake.py`: `DYNAMIC`, `mark_imports(spawned=)`,
  `bake(spawned=)` and its log line.
- `packages/exporting/export.py`: `responder_vehicle_scenes` and the bake's
  call.
- `tests/unit/test_light_bake.py`, `tests/unit/test_responder_arrivals_in_package.py`, and
  `tests/unit/test_merge_empties.py`, whose source-order test reads the bake's call.
CHANGELOG and VERSION from `lf_bake_spawned/CHANGELOG_0.162.1.md`.

    python patch_lf_bake_spawned.py
    LF_ROOT=<copy> python patch_lf_bake_spawned.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_bake_spawned"
CHANGELOG_HEAD = "## [0.162.0] - Each responder arrival names the car it brings\n"

BAKE = [
    ("""STATIC_LIGHTMAPS = 2
""",
     """STATIC_LIGHTMAPS = 2
#: `meshes/light_baking` Dynamic (0.162.1). A model the gameplay layer spawns
#: is never in the bake, so its light has to come from the `LightmapGI`'s
#: probes, which only a GI_MODE_DYNAMIC mesh samples. Measured 2026-10-08 on
#: Godot 4.7, the responders' cruiser imported at 2 gave its five meshes
#: gi_mode STATIC, and at 3 gi_mode DYNAMIC (cold run 9208's notes at the
#: factory root).
DYNAMIC = 3
"""),
    ("""def mark_imports(export_dir: Path) -> dict:
    \"\"\"Static Lightmaps on every model's sidecar but those whose own second
    UV set is shader data. ``{"baked": [...], "dynamic": [...]}``, package-
    relative paths. A sidecar with no `meshes/light_baking` line is an
    import Godot has not written yet, and is said rather than guessed.\"\"\"
    out = {"baked": [], "dynamic": [], "unreadable": []}
    for sidecar in sorted(Path(export_dir).rglob("*.glb.import")):
        if ".godot" in sidecar.parts:
            continue
        glb = sidecar.with_suffix("")
        rel = glb.relative_to(export_dir).as_posix()
        if glb_has_uv2(glb):
            out["dynamic"].append(rel)
            continue
        text = sidecar.read_text(encoding="utf-8")
        new, k = re.subn(rf"^{re.escape(LIGHT_BAKING)}=\\d+$", f"{LIGHT_BAKING}={STATIC_LIGHTMAPS}",
                         text, flags=re.M)
        if k != 1:
            out["unreadable"].append(rel)
            continue
        if new != text:
            sidecar.write_text(new, encoding="utf-8", newline="\\n")
        out["baked"].append(rel)
    return out
""",
     """def mark_imports(export_dir: Path, spawned=()) -> dict:
    \"\"\"Static Lightmaps on every model's sidecar but those whose own second
    UV set is shader data. ``{"baked": [...], "dynamic": [...], ...}``,
    package-relative paths. A sidecar with no `meshes/light_baking` line is
    an import Godot has not written yet, and is said rather than guessed.

    ``spawned`` (0.162.1): the package-relative paths of models the gameplay
    layer spawns -- the responders' car. Each is set to `DYNAMIC` and listed
    under ``spawned``, ahead of the second-UV test; a path with no sidecar is
    listed under ``spawned_unmatched``. 0.162.0 baked the car's import static
    like any prop, and a spawned one would have had neither the lightmap nor
    the probes.\"\"\"
    out = {"baked": [], "dynamic": [], "spawned": [], "spawned_unmatched": [], "unreadable": []}
    wanted = set(spawned)
    for sidecar in sorted(Path(export_dir).rglob("*.glb.import")):
        if ".godot" in sidecar.parts:
            continue
        glb = sidecar.with_suffix("")
        rel = glb.relative_to(export_dir).as_posix()
        if rel in wanted:
            value, bucket = DYNAMIC, "spawned"
        elif glb_has_uv2(glb):
            out["dynamic"].append(rel)
            continue
        else:
            value, bucket = STATIC_LIGHTMAPS, "baked"
        text = sidecar.read_text(encoding="utf-8")
        new, k = re.subn(rf"^{re.escape(LIGHT_BAKING)}=\\d+$", f"{LIGHT_BAKING}={value}",
                         text, flags=re.M)
        if k != 1:
            out["unreadable"].append(rel)
            continue
        if new != text:
            sidecar.write_text(new, encoding="utf-8", newline="\\n")
        out[bucket].append(rel)
    out["spawned_unmatched"] = sorted(wanted - set(out["spawned"]) - set(out["unreadable"]))
    return out
"""),
    ("""def bake(export_dir, godot_executable, *, log=print) -> dict:
""",
     """def bake(export_dir, godot_executable, *, log=print, spawned=()) -> dict:
"""),
    ("""        report["imports"] = mark_imports(export_dir)
""",
     """        report["imports"] = mark_imports(export_dir, spawned)
"""),
    ("""        log("[export] light bake: %d model(s) and %d primitive mesh(es) lightmapped, %d kept dynamic; "
            "%d steady rig(s) baked, %d failing and %d cycling left live; %s; %d users, %s s in the editor"
            % (len(report["imports"]["baked"]), sum(report["primitives"].values()),
               len(report["imports"]["dynamic"]), report["rigs"]["static"], report["rigs"]["live"],
""",
     """        log("[export] light bake: %d model(s) and %d primitive mesh(es) lightmapped, %d kept dynamic, "
            "%d spawned set dynamic; "
            "%d steady rig(s) baked, %d failing and %d cycling left live; %s; %d users, %s s in the editor"
            % (len(report["imports"]["baked"]), sum(report["primitives"].values()),
               len(report["imports"]["dynamic"]), len(report["imports"]["spawned"]),
               report["rigs"]["static"], report["rigs"]["live"],
"""),
]

EXPORT = [
    ("""        _bake_lights(export_dir, godot_executable)
""",
     """        # the responders' car (0.162.1): spawned by the gameplay layer, so
        # its import is set dynamic and it takes the lightmap's probes
        _bake_lights(export_dir, godot_executable,
                     spawned=responder_vehicle_scenes(themed_site_dir))
"""),
    ("""def write_responder_arrivals(export_dir: Path, lot_gameplay,
""",
     """def responder_vehicle_scenes(themed_site_dir) -> list:
    \"\"\"The package-relative paths of the cars the themed site names in
    `responders.json` (Lot 0.101.0): models the gameplay layer spawns, which
    the light bake sets dynamic rather than baking (0.162.1). Empty without
    one.\"\"\"
    if not themed_site_dir:
        return []
    named = Path(themed_site_dir) / "responders.json"
    if not named.is_file():
        return []
    doc = json.loads(named.read_text(encoding="utf-8"))
    return sorted({v["scene"] for v in doc.get("vehicles") or []})


def write_responder_arrivals(export_dir: Path, lot_gameplay,
"""),
]

TEST_BAKE = [
    ("""    got = LB.mark_imports(tmp_path)
    assert got == {"baked": ["shell.glb"], "dynamic": ["grill.glb"], "unreadable": ["odd.glb"]}
""",
     """    got = LB.mark_imports(tmp_path)
    assert got == {"baked": ["shell.glb"], "dynamic": ["grill.glb"], "spawned": [],
                   "spawned_unmatched": [], "unreadable": ["odd.glb"]}
"""),
    ("""def test_inline_primitives_unwrap_themselves_once(tmp_path):
""",
     """def test_a_spawned_model_is_set_dynamic_not_baked(tmp_path):
    \"\"\"0.162.1: the responders' car is spawned by the gameplay layer and never
    in the bake, so its import is Dynamic (3), which samples the lightmap's
    probes; Static Lightmaps (2) would leave a spawned car unlit by either.
    A spawned path with no sidecar is said, not dropped.\"\"\"
    (tmp_path / "cover").mkdir()
    _glb(tmp_path / "shell.glb", uv2=False)
    _glb(tmp_path / "cover" / "car.glb", uv2=False)
    (tmp_path / "shell.glb.import").write_text(_SIDECAR, encoding="utf-8")
    (tmp_path / "cover" / "car.glb.import").write_text(_SIDECAR, encoding="utf-8")
    got = LB.mark_imports(tmp_path, spawned=["cover/car.glb", "cover/gone.glb"])
    assert got["baked"] == ["shell.glb"] and got["spawned"] == ["cover/car.glb"]
    assert got["spawned_unmatched"] == ["cover/gone.glb"]
    assert "meshes/light_baking=3" in (tmp_path / "cover" / "car.glb.import").read_text(encoding="utf-8")
    assert "meshes/light_baking=2" in (tmp_path / "shell.glb.import").read_text(encoding="utf-8")
    assert LB.DYNAMIC == 3 and LB.STATIC_LIGHTMAPS == 2


def test_inline_primitives_unwrap_themselves_once(tmp_path):
"""),
]

TEST_ARRIVALS = [
    ("""def test_the_manifest_lists_it(tmp_path):
""",
     """def test_the_bake_is_told_which_car_is_spawned(tmp_path):
    \"\"\"0.162.1: the themed site's cars, as the light bake reads them, and the
    export handing them over (read as source; the bake itself needs a GPU).\"\"\"
    from packages.exporting.export import responder_vehicle_scenes
    assert responder_vehicle_scenes(_themed(tmp_path)) == [CAR]
    assert responder_vehicle_scenes(None) == [] and responder_vehicle_scenes(tmp_path) == []
    src = (Path(__file__).resolve().parents[2] / "packages" / "exporting" / "export.py").read_text(encoding="utf-8")
    assert "spawned=responder_vehicle_scenes(themed_site_dir)" in src


def test_the_manifest_lists_it(tmp_path):
"""),
]

TEST_MERGE = [
    ("""    bake = src.index("_bake_lights(export_dir, godot_executable)")
""",
     """    # the call's opening: 0.162.1 hands the bake the spawned cars as well
    bake = src.index("_bake_lights(export_dir, godot_executable")
"""),
]


EDITS = {
    str(pathlib.Path("packages") / "exporting" / "light_bake.py"): BAKE,
    str(pathlib.Path("packages") / "exporting" / "export.py"): EXPORT,
    str(pathlib.Path("tests") / "unit" / "test_light_bake.py"): TEST_BAKE,
    str(pathlib.Path("tests") / "unit" / "test_responder_arrivals_in_package.py"): TEST_ARRIVALS,
    str(pathlib.Path("tests") / "unit" / "test_merge_empties.py"): TEST_MERGE,
}


def _stage(root, edits):
    staged = {}
    for rel, pairs in edits.items():
        p = root / rel
        d = p.read_bytes()
        crlf, lf = d.count(b"\r\n"), d.count(b"\n")
        assert crlf in (0, lf), (rel, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    return staged


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.162.0", repr(v)
    staged = _stage(LF, EDITS)
    entry = (SRC / "CHANGELOG_0.162.1.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    c = (LF / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:80]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    (LF / "CHANGELOG.md").write_bytes((entry + text).encode("utf-8"))
    (LF / "VERSION").write_bytes(b"0.162.1")
    print("Level Factory 0.162.0 -> 0.162.1")


if __name__ == "__main__":
    main()
