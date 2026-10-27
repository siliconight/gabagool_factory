"""Edit a Level Factory clone for 0.260.0 (the factory's roadmap 297): the library finds a shell's validation manifest by
the name Deli Counter writes it under, and the export's validation rule is a directory rule a profile can use. Run
from the clone's root. Asserts every anchor once; refuses on a miss."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


edit("packages/pipeline/building_library.py", [
('''    AN ABSENT VALIDATION MANIFEST IS NOT A FACADE. Deli Counter not having said
    is not Deli Counter saying yes, and this fails open deliberately: exactly
    one complete shell in the library has no validation manifest
    (`cbp_town_finale_midbalanced_schemafixed`) and it is a building. A rule
    that read absence as exclusion would drop it for never having been judged,
    which is the mistake `themed_fitness` refuses to make one direction over.''',
'''    AN ABSENT VALIDATION MANIFEST IS NOT A FACADE. Deli Counter not having said
    is not Deli Counter saying yes, and this fails open deliberately: a rule
    that read absence as exclusion would drop a building for never having been
    judged, which is the mistake `themed_fitness` refuses to make one direction
    over.

    THE MANIFEST IS FOUND BY THE NAME DELI COUNTER WRITES IT UNDER (0.260.0,
    the factory's roadmap 297; `validation_manifest`). This said exactly one
    complete shell had none -- `cbp_town_finale_midbalanced_schemafixed` -- and
    it has one: Deli Counter names a shell's validation manifest after its
    spec's `level`, and three shells' file stems are not their level's name
    (that one, `fuel_stop_heist3` and `fuel_stop_heist4`), so a facade or demo
    flag in theirs was never read.'''),
('''    data = _manifest(Path(str(build_dir)) / (aid + ".validation.json"))
    if (data or {}).get("facade") is True:''',
'''    data = validation_manifest(build_dir, aid)
    if (data or {}).get("facade") is True:'''),
('''def index(build_dir) -> tuple[list[dict], list[dict], list[dict]]:''',
'''def validation_manifest(build_dir, archetype_id):
    """A shell's validation manifest, or ``None`` (0.260.0, the factory's
    roadmap 297): `<id>.validation.json`, else the one named after the shell's
    spec -- Deli Counter writes it under the `level` its
    `<id>.gameplay.json` carries, and three library shells' file stems are not
    their level's name (`cbp_town_finale_midbalanced_schemafixed` writes
    `cbp_town_finale_midbalanced.validation.json`)."""
    root = Path(str(build_dir))
    aid = str(archetype_id)
    data = _manifest(root / (aid + ".validation.json"))
    if data is not None:
        return data
    level = (_manifest(root / (aid + ".gameplay.json")) or {}).get("level")
    if level and str(level) != aid:
        return _manifest(root / (str(level) + ".validation.json"))
    return None


def index(build_dir) -> tuple[list[dict], list[dict], list[dict]]:'''),
])

edit("packages/exporting/export.py", [
('''    skip: set[str] = set()
    if not ships_lux(profile.mode):
        skip |= _PRESENTATION_FILES
    if not profile.include_validation:
        skip |= {"validation"}''',
'''    skip, skip_dirs = base_skips(profile)'''),
('''    if (profile.mode == MODE_PURE_SHELL and graybox_dir
            and graybox_dir.exists() and base_dir is not graybox_dir):
        _copy_tree(graybox_dir, export_dir, skip=skip)
    if base_dir and base_dir.exists():
        _copy_tree(base_dir, export_dir, skip=skip)''',
'''    if (profile.mode == MODE_PURE_SHELL and graybox_dir
            and graybox_dir.exists() and base_dir is not graybox_dir):
        _copy_tree(graybox_dir, export_dir, skip=skip, skip_dirs=skip_dirs)
    if base_dir and base_dir.exists():
        _copy_tree(base_dir, export_dir, skip=skip, skip_dirs=skip_dirs)'''),
('''#: `res://site.tscn`, as an ext_resource line would carry it.''',
'''def base_skips(profile) -> tuple[set, set]:
    """``(names, directories)`` the functional base's copy leaves out (0.260.0,
    the factory's roadmap 297).

    A NAME rule cannot leave a directory out: `_copy_tree` walks files and
    matches `skip` against each file's NAME, so the `"validation"` this added
    to `skip` matched nothing -- the handoff's `validation/` directory holds
    `report.*` and `overlays/` -- and `include_validation` was a knob with no
    effect. It is a directory rule now, and the knob leaves `validation/` out
    when a profile turns it off. The default ships it, as it always has."""
    skip: set[str] = set()
    skip_dirs: set[str] = set()
    if not ships_lux(profile.mode):
        skip |= _PRESENTATION_FILES
    if not profile.include_validation:
        skip_dirs |= {"validation"}
    return skip, skip_dirs


#: `res://site.tscn`, as an ext_resource line would carry it.'''),
])
