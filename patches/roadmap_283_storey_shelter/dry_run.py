"""Dry-run patches/patch_roadmap_283_storey_shelter.py on a scratch copy of the roadmap, regenerate and check the index there,
and show every line that moved against the live roadmap.

    python patches/roadmap_283_storey_shelter/dry_run.py <new scratch dir>

The scratch dir gets `factory.manifest.json` (the marker `tools/roadmap_status.py` walks up to), the roadmap, a copy of
`roadmap_status.py` under `tools/` and of the patch under `patches/`. Runs the patch, `--write`, `--check`, and the
patch a second time (which must refuse), then diffs the dry roadmap against the live one and prints each hunk's line
range and its first characters. Writes `dry_run.out.txt` beside this file.
"""
import difflib
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[1]
D = pathlib.Path(sys.argv[1])
assert not D.exists(), "the scratch dir must be new"
(D / "tools").mkdir(parents=True)
(D / "patches").mkdir()
shutil.copy2(F / "factory.manifest.json", D)
shutil.copy2(F / "PIPELINE_ROADMAP.md", D)
shutil.copy2(F / "tools" / "roadmap_status.py", D / "tools")
shutil.copy2(F / "patches" / "patch_roadmap_283_storey_shelter.py", D / "patches")
out = []
for what, cmd in (("first", ["patches/patch_roadmap_283_storey_shelter.py"]), ("write", ["tools/roadmap_status.py", "--write"]),
                  ("check", ["tools/roadmap_status.py", "--check"]), ("second", ["patches/patch_roadmap_283_storey_shelter.py"])):
    r = subprocess.run([sys.executable, str(D / cmd[0]), *cmd[1:]], capture_output=True, text=True, cwd=str(D))
    out.append((r.stdout + r.stderr).rstrip("\n"))
    out.append("%s exit %d" % (what, r.returncode))
live = (F / "PIPELINE_ROADMAP.md").read_text(encoding="utf-8").splitlines()
dry = (D / "PIPELINE_ROADMAP.md").read_text(encoding="utf-8").splitlines()
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, live, dry, autojunk=False).get_opcodes():
    if tag == "equal":
        continue
    out.append("%s live %d-%d -> dry %d-%d" % (tag, i1 + 1, i2, j1 + 1, j2))
    for ln in dry[j1:j2]:
        out.append("    + " + ln[:150])
text = "\n".join(out) + "\n"
(HERE / "dry_run.out.txt").write_text(text, encoding="utf-8", newline="\n")
print(text)
