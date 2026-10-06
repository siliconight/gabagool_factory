"""Level Factory 0.144.0, the second half: a failed light bake must not break
the package it gave up on.

Found by the bake default (`patch_lf_defaults_on.py`): the suite's
`test_presentation_export_and_portability` exported with the bake on for the
first time. Its stub presentation scene has no rig script, so the bake failed
and shipped the package unbaked, as designed. But its report's `reason`
carried the package's absolute path, and the closure scan refused the export:
`EXPORT_CLOSURE_BROKEN ... light_bake.json: absolute path`. The report is LF's
own log of a build step, which `closure._METADATA_FILES` exists to exempt.

    python patch_lf_bake_report_metadata.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

EDITS = {
    LF / "packages/exporting/closure.py": [(
        '''    # The export manifest records THIS verdict (`verified.export_closure`), so
    # it cannot be inside what the verdict describes -- the same reason
    # `export_closure_scan.json` itself is on this list.
    "LF_MANIFEST.json",
}
''',
        '''    # The export manifest records THIS verdict (`verified.export_closure`), so
    # it cannot be inside what the verdict describes -- the same reason
    # `export_closure_scan.json` itself is on this list.
    "LF_MANIFEST.json",
    # Added 0.144.0, when the light bake became the export's default. A bake
    # that fails ships the package unbaked and says why in this report, and
    # the suite's first failed bake (`test_presentation_export_and_
    # portability`, a presentation scene with no rig script) put the
    # package's absolute path into `reason` -- so this scan refused an
    # export the bake had already given up on cleanly. Same shape as
    # `glb_reference_scan.json`: LF's own log of a build step. No Godot
    # loader reads it; a grep of lux, dispatch and LF's assets finds no
    # reader of the file. A successful bake's report carries no path.
    "light_bake.json",
}
''')],
    LF / "tests/unit/test_light_bake.py": [(
        '''    assert parse(["export", "m", "--no-bake-lights"]).bake_lights is False
''',
        '''    assert parse(["export", "m", "--no-bake-lights"]).bake_lights is False


def test_a_failed_bake_leaves_a_package_the_closure_scan_accepts(tmp_path):
    """0.144.0 made the bake the export's default, and the suite's first
    failed bake put the package's absolute path into the report's `reason`;
    the closure scan then refused an export the bake had already abandoned
    cleanly. The report is LF's log of a build step and is exempt, as
    `glb_reference_scan.json` is."""
    from packages.exporting.closure import scan_closure
    pkg = tmp_path / "LF_t.portable-godot"
    (pkg / "presentation").mkdir(parents=True)
    (pkg / LB.PRESENTATION).write_text("[gd_scene format=3]\\n", encoding="utf-8")
    (pkg / "mission.tscn").write_text("[gd_scene format=3]\\n", encoding="utf-8")
    r = LB.bake(pkg, "godot.exe", log=lambda *a: None)
    # the shape that tripped the scan: a failure whose reason names the package
    assert r["ok"] is False and str(pkg) in r["reason"], r
    issues = [i for i in scan_closure(pkg).issues if i.startswith(LB.REPORT)]
    assert issues == [], issues
''')],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        assert b"\r\n" not in data, f"{path}: CRLF, and every anchor here is LF"
        text = data.decode("utf-8")
        for old, new in pairs:
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
