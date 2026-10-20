"""Write patches/patch_lux_day_presets.py (Lux 0.79.0, the factory's roadmap 217) from the proven lux_tod clone.

New files only: each is embedded verbatim, and the generator refuses to write the patch unless the clone's VERSION and
CHANGELOG are what the patch would make of the real repo's.

    python gen_lux_day_presets.py            # dry: build the patch in memory, check it compiles
    python gen_lux_day_presets.py --write    # write it (refuses if the name is taken)
    python gen_lux_day_presets.py --to <p>   # write a copy elsewhere, for a dry run
"""
import pathlib
import sys

FACTORY = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LUX = FACTORY / "lux"
SCRATCH = pathlib.Path(r"C:\Users\Brannen\AppData\Local\Temp\claude\C--Projects-gabagool-studios-gabagool-factory"
                       r"\27f14f8b-7ce5-44c0-a704-178a824035d7\scratchpad")
CLONE = SCRATCH / "lux_tod"
NEW = ["addons/lux/presets/delco_morning.tres", "addons/lux/presets/delco_high_noon.tres",
       "tools/day_presets_selftest.gd", "tools/day_presets_selftest.gd.uid"]
HEADER = "# Changelog\n\n"

files = {}
for n in NEW:
    assert not (LUX / n).exists(), n
    raw = (CLONE / n).read_bytes()
    assert b"\r\n" not in raw, n
    files[n] = raw.decode("utf-8")
entry = (SCRATCH / "lux_changelog_0790.md").read_text(encoding="utf-8")
assert entry.startswith("## [0.79.0]") and entry.endswith("\n\n")
real = (LUX / "CHANGELOG.md").read_bytes().decode("utf-8")
assert "\r\n" not in real and real.startswith(HEADER + "## [0.78.0]")
assert (CLONE / "CHANGELOG.md").read_bytes().decode("utf-8") == HEADER + entry + real[len(HEADER):], "the clone's CHANGELOG"
assert (LUX / "VERSION").read_bytes() == b"Lux 0.78.0" and (CLONE / "VERSION").read_bytes() == b"Lux 0.79.0"
template = (SCRATCH / "patch_lux_day_presets.py").read_text(encoding="utf-8")
assert template.count("NEW_FILES_DATA") == 1 and template.count("CHANGELOG_DATA") == 1
BODY = template.replace("NEW_FILES_DATA", repr(files)).replace("CHANGELOG_DATA", repr(entry))

dest = FACTORY / "patches" / "patch_lux_day_presets.py"
if "--to" in sys.argv:
    to = pathlib.Path(sys.argv[sys.argv.index("--to") + 1])
    to.write_text(BODY, encoding="utf-8", newline="\n")
    print("wrote the dry copy", to)
elif "--write" in sys.argv:
    assert not dest.exists(), "name taken"
    dest.write_text(BODY, encoding="utf-8", newline="\n")
    compile(BODY, str(dest), "exec")
    print("wrote", dest, len(BODY), "chars; it compiles")
else:
    compile(BODY, "patch_lux_day_presets.py", "exec")
    print("dry: the patch would be", len(BODY), "chars and compiles; --write to write it")
