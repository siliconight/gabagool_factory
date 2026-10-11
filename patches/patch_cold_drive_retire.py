"""The package clean job: every cold run ends by retiring what a pushed record makes regenerable.

The walker, 2026-10-11: "we should have a package clean job so we don't accrue GBs of packages that
have already been pushed and verified as known good to GIT". `tools/factory_retire.py` holds the rules
(`patches/patch_retire_pushed.py` added the pushed ones); this makes them run without anyone
remembering to: `tools/cold_drive/cold_drive.sh` calls `factory_retire.py --apply` as its last step,
after the walk. The run's own workspace is never retired there -- its record is not written, let
alone pushed -- and the newest four stay, so the price that follows a run still finds its control.
`docs/FILING.md`'s rule 4 says so.

Anchored, each file asserted once, nothing written on a miss; refuses while a cold run is in flight
(bash reads the drive as it runs).

    python patches/patch_cold_drive_retire.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DRIVE = ROOT / "tools" / "cold_drive" / "cold_drive.sh"
FILING = ROOT / "docs" / "FILING.md"
ACTIVE = ROOT / "_runs" / "cold" / "ACTIVE"

D_OLD = ("python tools/cold_drive/wire_sky.py _runs/walk_export_$M 2>&1 | tail -1\n"
         "echo DONE\n")
D_NEW = ("python tools/cold_drive/wire_sky.py _runs/walk_export_$M 2>&1 | tail -1\n"
         "# THE PACKAGE CLEAN JOB (2026-10-11): what a pushed record makes regenerable goes --\n"
         "# workspaces beyond the newest four, release and test zips, test unpacks. This run's\n"
         "# own workspace stays: its record is not pushed yet. Never fatal to the run.\n"
         "step retire; python tools/factory_retire.py --apply 2>&1 | tail -1 || true\n"
         "echo DONE\n")
F_OLD = ("4. **Regenerable output is retired, not kept.** `tools/factory_retire.py`\n"
         "   (dry-run by default, `--apply` to act) retires perf copies that have\n"
         "   their JSON, walk exports older than a mission's newest, and cold-run\n"
         "   workspaces older than the last twelve that no finding reads.\n")
F_NEW = ("4. **Regenerable output is retired, not kept.** `tools/factory_retire.py`\n"
         "   (dry-run by default, `--apply` to act) retires perf copies that have\n"
         "   their JSON, walk exports older than a mission's newest, and cold-run\n"
         "   workspaces older than the last twelve that no finding reads. **What a\n"
         "   PUSHED record makes regenerable goes too** (2026-10-11): a cold-run\n"
         "   workspace beyond the newest four whose `NOTES.md` is in the branch the\n"
         "   root pushes to, a release zip whose notes are pushed (never the newest),\n"
         "   an install-test zip a pushed record names, and an install test's unpack\n"
         "   whose record is pushed (never the newest). Every cold run ends by\n"
         "   applying it (`tools/cold_drive/cold_drive.sh`'s last step), so the disk\n"
         "   does not wait for somebody to remember.\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def main():
    if ACTIVE.exists():
        sys.exit("refusing: a cold run is in flight (_runs/cold/ACTIVE), and bash reads the drive as it runs")
    d_raw, f_raw = DRIVE.read_bytes(), FILING.read_bytes()
    assert b"\r\n" not in d_raw and b"\r\n" not in f_raw, "both files are LF"
    drive, filing = d_raw.decode("utf-8"), f_raw.decode("utf-8")
    assert "step retire" not in drive and "PUSHED record" not in filing, "already applied"
    drive = _once(drive, D_OLD, D_NEW, "the drive's end")
    filing = _once(filing, F_OLD, F_NEW, "FILING's rule 4")
    DRIVE.write_bytes(drive.encode("utf-8"))
    FILING.write_bytes(filing.encode("utf-8"))
    print("cold_drive.sh ends with the package clean job; FILING.md rule 4 says so")


if __name__ == "__main__":
    sys.exit(main())
