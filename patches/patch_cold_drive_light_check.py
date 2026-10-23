"""Every cold run runs the light check (the walker's walk of cold run 9383, finding 1). `tools/light_check.py` failed
three rooms of cold run 9383's level -- deli_a03's basement vault (p50 3), the office lobby (8), the pharmacy's retail
floor (2) -- in a level that shipped with 0 interventions, because nothing ran it: the narrowed audit's item 26,
"Nothing runs it or gates on it", and the walker found the dark by playing. The drive now runs it on the walk copy
under the level's own preset, keeps its verdict in the run's record (`docs/cold_runs/cold_N/light_check.txt`) and its
frames out of it (`_runs/cold/cold_N/light_check/`), and prints the counts in the driver log. It reports, it does not
stop the run: a dark room is a finding the run carries, and whether it should stop one is the walker's call once the
floors have settled. Anchored; refuses on a miss.

    python patches/patch_cold_drive_light_check.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SH = ROOT / "tools" / "cold_drive" / "cold_drive.sh"

OLD = """python tools/cold_drive/wire_sky.py _runs/walk_export_$M 2>&1 | tail -1
"""
NEW = """python tools/cold_drive/wire_sky.py _runs/walk_export_$M 2>&1 | tail -1
# THE LIGHT CHECK (2026-10-23, the walker's walk of cold run 9383): every room and every opening's landing, under the
# level's own preset, held to its floor (`tools/light_check.py`). It failed three rooms of 9383 that nobody had run it
# on. Its frames stay in the run's scratch, its verdict goes in the record, and a FAIL is reported, not a stop.
step light; python tools/light_check.py _runs/walk_export_$M --slots own --out _runs/cold/cold_$N/light_check \\
    > _runs/cold/cold_$N/light_check.log 2>&1
echo "light check exit $? -- $(grep -m1 -E '^  (FAIL|PASS|WARN|EXEMPT|REPORT) ' _runs/cold/cold_$N/light_check/light_check.txt 2>/dev/null || echo 'no verdict written')"
cp _runs/cold/cold_$N/light_check/light_check.txt docs/cold_runs/cold_$N/light_check.txt 2>/dev/null || true
"""


def main():
    raw = SH.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if "step light;" in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    if text.count(OLD) != 1:
        raise SystemExit("REFUSED: the anchor is there %d times; nothing written" % text.count(OLD))
    text = text.replace(OLD, NEW)
    SH.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print("tools/cold_drive/cold_drive.sh runs the light check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
