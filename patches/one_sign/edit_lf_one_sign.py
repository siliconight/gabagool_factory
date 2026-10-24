"""Level Factory 0.241.0 on a CLONE (<repo>): a shell whose street band was dealt builds no lit door box -- one sign a
building (the walker's walk of cold run 9386, finding 1: "in real life this would be 1 sign"). Anchored; refuses on a
miss.

    python edit_lf_one_sign.py <repo>
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


edit("apps/cli/commands/__init__.py", [
    ('''                    if door:
                        specs[job.job_id]["sign_pack"] = door''',
     '''                    if door:
                        specs[job.job_id]["sign_pack"] = door
                        # ONE SIGN A BUILDING (0.241.0). The walker, walking
                        # cold run 9386, of a pharmacy with its band along the
                        # parapet and a lit box over its door: "in real life
                        # this would be 1 sign". A shell dealt a band keeps
                        # the band and builds no door box (Zoo 1.123.0's
                        # `--skip-fixture-types`); Lot 0.129.0 leaves that
                        # box's lamp out of the site's lights. A shell dealt
                        # none keeps its box as its one sign.
                        specs[job.job_id]["skip_fixture_types"] = ["sign"]'''),
])
edit("adapters/zoo/__init__.py", [
    ('''            # the business the shell's band was dealt (0.148.0): its door box
            # wears the same pack (Zoo 1.79.0)
            if job_spec.get("sign_pack"):''',
     '''            # one sign a building (0.241.0): what this shell leaves out, as ONE
            # comma list -- Zoo's CLI reads `--fixture-types` and this the same way
            if job_spec.get("skip_fixture_types"):
                zoo_args += ["--skip-fixture-types",
                             ",".join(str(t) for t in job_spec["skip_fixture_types"])]
            # the business the shell's band was dealt (0.148.0): its door box
            # wears the same pack (Zoo 1.79.0)
            if job_spec.get("sign_pack"):'''),
])
edit("tests/unit/test_fixture_pipeline.py", [
    ('''def test_zoo_fixtures_marker_contract_blocks(tmp_path):''',
     '''def test_a_banded_shell_s_fixtures_leave_out_its_door_box(tmp_path):
    """0.241.0, one sign a building (the walker, cold run 9386): a fixtures job told to skip `sign` passes Zoo
    `--skip-fixture-types sign` as one comma list, and the planner tells every shell it deals a band to. FAILS ON
    0.240.0."""
    lights = tmp_path / "shell.lights.json"
    lights.write_text(json.dumps({
        "light_manifest_version": "1.1", "building_id": "lf_m1",
        "anchors": [{"id": "a", "type": "sign", "pos": [0, 0, 3]}]}))
    spec = {"mode": "fixtures", "lights_path": str(lights), "theme": "delco",
            "skip_fixture_types": ["sign", "neon"]}
    cmds = ZooAdapter().plan_commands(spec, {
        "repository": str(tmp_path), "work_dir": str(tmp_path / "work"),
        "blender_executable": "blender"})
    args = list(cmds[0].arguments)
    assert args[args.index("--skip-fixture-types") + 1] == "sign,neon"
    src = (Path(__file__).resolve().parents[2] / "apps" / "cli" / "commands" / "__init__.py").read_text(
        encoding="utf-8")
    at = src.index('specs[job.job_id]["sign_pack"] = door')
    assert 'specs[job.job_id]["skip_fixture_types"] = ["sign"]' in src[at:at + 900]


def test_zoo_fixtures_marker_contract_blocks(tmp_path):'''),
])
print("lf: a banded shell's fixtures skip the door box; test")
