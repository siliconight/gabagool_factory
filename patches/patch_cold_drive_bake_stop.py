"""tools/cold_drive/cold_drive.sh: a package asked to bake that ships unbaked STOPS the run (cold run 9242).

9242's export failed its light bake (`bake.tscn did not open`), restored the presentation scene,
shipped the package without its lightmap and printed a WARNING -- and the drive, which stops only
when nothing was exported, went on to the findings and the walk, and the run counted 0
interventions. The level was worse than 9241's and only a person reading the export's log said so
(roadmap 178's family: the instruments report and nothing blocks). After the export, unless
`EXPORT_FLAGS` asks for no bake, the drive reads the package's own `light_bake.json` -- the bake's
report, not the log line -- and stops on `ok` false or a missing report.

Anchored on the export step's line, asserted once; nothing written on a miss. NOT to be applied
while a cold run is in flight: bash reads a script as it runs.

    python patches/patch_cold_drive_bake_stop.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DRIVE = ROOT / "tools" / "cold_drive" / "cold_drive.sh"
ACTIVE = ROOT / "_runs" / "cold" / "ACTIVE"
ANCHOR = ('grep -q "^exported" /tmp/cold_leg.txt || die export\n')
ADD = ('# A package asked to bake that ships unbaked STOPS the run (cold run 9242: the export\n'
       '# warned, the drive went on, and the run counted zero). The bake\'s own report decides.\n'
       'if [[ "${EXPORT_FLAGS:-}" != *--no-bake-lights* ]]; then\n'
       '  python -c "import json,sys; sys.exit(0 if json.load(open(sys.argv[1], encoding=\'utf-8\')).get(\'ok\') else 1)" \\\n'
       '    "$WS/.level_factory/exports/LF_$M.portable-godot/light_bake.json" 2>/dev/null \\\n'
       '    || die "light bake: the package ships unbaked (light_bake.json ok is not true)"\n'
       'fi\n')


def main():
    if ACTIVE.exists():
        sys.exit("refusing: a cold run is in flight (_runs/cold/ACTIVE), and bash reads this script as it runs")
    raw = DRIVE.read_bytes()
    assert b"\r\n" not in raw, "cold_drive.sh is LF"
    text = raw.decode("utf-8")
    assert "the package ships unbaked" not in text, "already applied"
    assert text.count(ANCHOR) == 1, ("the export step", text.count(ANCHOR))
    text = text.replace(ANCHOR, ANCHOR + ADD)
    DRIVE.write_bytes(text.encode("utf-8"))
    print("cold_drive.sh: an unbaked package stops the run")


if __name__ == "__main__":
    sys.exit(main())
