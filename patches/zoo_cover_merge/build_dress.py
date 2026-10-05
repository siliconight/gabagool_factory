"""Build one building's dressing with the Zoo checked out now, exactly as cold
run 9154's `zoo_dressing_build` job did, into <out>/<building>/.

    python build_dress.py <out_dir> <building> [<building> ...]

The command is copied from that job's `1/job.log`: `zoo_cli.py --dress`
under Blender, the run's own Patina manifest, Pixelcoat skins, theme
`delco_1997`, seed 9080. Prints Zoo's own summary lines and the exit code.
"""
import pathlib
import subprocess
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
WS = F / "workspaces" / "cold-9154-ws" / ".level_factory" / "jobs"
BLENDER = r"C:\blender\blender.exe"

out = pathlib.Path(sys.argv[1])
for bid in sys.argv[2:]:
    manifest = WS / f"gas_block_001.patina_dressing.{bid}" / "out" / f"{bid}.patina.dressing.json"
    assert manifest.is_file(), manifest
    dst = out / bid
    dst.mkdir(parents=True, exist_ok=True)
    cmd = [BLENDER, "--background", "--python", str(F / "zoo" / "tools" / "zoo_cli.py"), "--",
           "--dress", str(manifest), "--out", str(dst),
           "--skins", str(WS / "gas_block_001.pixelcoat_build" / "out"),
           "--theme", "delco_1997", "--seed", "9080", "--no-blend"]
    r = subprocess.run(cmd, cwd=str(F / "zoo"), capture_output=True, text=True, timeout=1200)
    print(f"== {bid}: exit {r.returncode}")
    for line in r.stdout.splitlines():
        if line.startswith("[zoo]") and ("dressing built" in line or "covers" in line
                                         or "merged" in line or "glb:" in line):
            print("  " + line)
    if r.returncode != 0:
        print(r.stdout[-2000:])
        print(r.stderr[-2000:])
