"""Record a Zoo working tree as `manifest.json` + `files/` for
`patch_zoo_lottery.py`: every file git reports modified or new against
HEAD, with the SHA-256 of its HEAD bytes (null when new) and of its bytes now.

    python patches/zoo_lottery/record.py          # from the factory root

Run it BEFORE committing Zoo, while HEAD is still the version being patched
from. `core.autocrlf` is asserted off for the files recorded: a HEAD blob and
a working file that differ only in line endings would record a before-state
no checkout has.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent.parent / "zoo"
SKIP = ("_census/", "_preview/")


def _git(*args):
    return subprocess.run(["git", "-C", str(ZOO), *args], check=True, capture_output=True).stdout


def main():
    rows = []
    out = _git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
    files = HERE / "files"
    if files.exists():
        shutil.rmtree(files)
    for line in out.splitlines():
        state, rel = line[:2], line[3:].strip().strip('"')
        if rel.startswith(SKIP) or "__pycache__" in rel:
            continue
        assert state in (" M", "??"), f"unexpected state {state!r} for {rel}"
        now = (ZOO / rel).read_bytes()
        before = None
        if state == " M":
            head = _git("show", f"HEAD:{rel}")
            assert b"\r\n" not in head or b"\r\n" in now, f"{rel}: line endings changed under git"
            before = hashlib.sha256(head).hexdigest()
        dst = files / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(now)
        rows.append({"path": rel, "before": before, "after": hashlib.sha256(now).hexdigest()})
    head_version = _git("show", "HEAD:VERSION").decode("utf-8").strip()
    manifest = {"from_version": head_version, "to_version": (ZOO / "VERSION").read_text().strip(),
                "files": sorted(rows, key=lambda r: r["path"])}
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(f"recorded {len(rows)} files, {manifest['from_version']} -> {manifest['to_version']}")


if __name__ == "__main__":
    main()
