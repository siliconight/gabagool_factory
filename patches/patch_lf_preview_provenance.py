r"""Stamp the preview with what it was built from, and say it out loud.

    python patch_lf_preview_provenance.py --check
    python patch_lf_preview_provenance.py
    python patch_lf_preview_provenance.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

Roadmap addendum item F, "preview freshness is invisible":

    `run --art` does not write `preview/<mission>_walk`; only `walk` does, via
    a full `rmtree` and rebuild. Nothing in the preview records which run it
    came from, so reading it after a pipeline change silently reads the
    previous walk. Cost about an hour and five refuted hypotheses. Cheapest
    fix: stamp the source job's fingerprint digest into the preview directory
    and have `walk` print it.

Exactly that. `build_walk_preview` writes `walk.source.json` beside the scene:

    {"schema": "level_factory.walk_provenance.v0.1",
     "source": "<content dir it was copied from>",
     "level_scene": "mission.tscn",
     "content_digest": "sha256:<16 hex>",
     "file_count": 47,
     "built_at": "2026-08-12T23:41:07+00:00"}

`content_digest` is over the RELATIVE PATH AND CONTENT HASH of every file
copied in, sorted. Not the directory mtime, which changes when nothing did, and
not a job id, which the preview cannot see from where it stands. Two previews
with the same digest were built from the same bytes; two with different digests
were not, and that is the whole question this item is about.

`walk` prints the digest and the timestamp under the lines that already say
which artefact it wrapped. A person who opens the preview folder tomorrow can
read the same file and compare.

WHY IT IS CHEAP AND WHY IT IS STILL WORTH IT. `walk` rmtree's and rebuilds, so
the preview is always current AT THE MOMENT `walk` RUNS. The failure is
reading it later -- after a `run` that changed the pipeline and did not touch
the preview -- and believing what you see. Five refuted hypotheses came out of
that gap, and the fix is one file and one printed line.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

PREVIEW = Path("level_factory/packages/preview/walk_preview.py")
COMMANDS = Path("level_factory/apps/cli/commands/__init__.py")
SIDECAR = ".pre_walkprov"


OLD_RET = '''    return {"dest": str(dest), "level_scene": level, "walk_scene": "walk.tscn",
            "spawn_transform": list(spawn), "spawn_source": spawn_src,
            "lighting": lighting, "content_copied": copied, "bots": bots}'''

NEW_RET = '''    # 6. WHAT THIS WAS BUILT FROM. `walk` rmtree's and rebuilds, so a preview
    # is current at the moment it is made -- and nothing recorded that, so
    # reading the folder after a later `run` (which does not touch it) shows
    # the previous walk with no way to tell. Roadmap addendum item F: "cost
    # about an hour and five refuted hypotheses."
    prov = _provenance(content_dir, dest, level)
    (dest / "walk.source.json").write_text(
        json.dumps(prov, indent=2, sort_keys=True), encoding="utf-8")

    return {"dest": str(dest), "level_scene": level, "walk_scene": "walk.tscn",
            "spawn_transform": list(spawn), "spawn_source": spawn_src,
            "lighting": lighting, "content_copied": copied, "bots": bots,
            "provenance": prov}'''


OLD_HELPER = '''def build_walk_preview(content_dir, player_src, dest, *, name="level"):'''

NEW_HELPER = '''def _provenance(content_dir: Path, dest: Path, level: str) -> dict:
    """A digest of the content this preview was built from.

    Over the RELATIVE PATH AND CONTENT of every copied file, sorted. Not the
    directory mtime -- that moves when nothing did, and a copy sets it on every
    build. Not a job id either: the preview is handed a directory and cannot
    see the graph it came from. Bytes are the thing both readers can compare.

    The player, the bots and this file are excluded: they are the preview's own
    scaffolding, not the content under test, and a new overlay script should
    not read as a different level.
    """
    ours = {"player_walk.gd", "player_walk.tscn", "walk.tscn", "project.godot",
            "walk_bot.gd", "shot_bot.gd", "debug_overlay.gd",
            "walk.source.json", "walkbot.json", "shotbot.json"}
    h = hashlib.sha256()
    n = 0
    for p in sorted(dest.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(dest).as_posix()
        if rel in ours or rel.endswith(".uid") or rel.startswith(".godot/"):
            continue
        h.update(rel.encode("utf-8"))
        h.update(hashlib.sha256(p.read_bytes()).digest())
        n += 1
    return {
        "schema": "level_factory.walk_provenance.v0.1",
        "source": str(content_dir),
        "level_scene": level,
        "content_digest": "sha256:" + h.hexdigest()[:16],
        "file_count": n,
        "built_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }


def build_walk_preview(content_dir, player_src, dest, *, name="level"):'''


OLD_IMPORT = '''import re
import shutil
from pathlib import Path'''

NEW_IMPORT = '''import datetime as _dt
import hashlib
import json
import re
import shutil
from pathlib import Path'''


OLD_PRINT = '''    print(f"  wraps {report['level_scene']} + player at {report['spawn_source']} "
          f"(x={origin[0]}, y={origin[1]}, z={origin[2]})")'''

NEW_PRINT = '''    print(f"  wraps {report['level_scene']} + player at {report['spawn_source']} "
          f"(x={origin[0]}, y={origin[1]}, z={origin[2]})")
    # SAY WHAT IT WAS BUILT FROM, and leave the same words in the folder. A
    # preview read after a later `run` is the previous walk, and nothing said
    # so -- addendum item F. `walk.source.json` beside the scene carries this
    # verbatim, so the answer survives the terminal scrolling away.
    _prov = report.get("provenance") or {}
    if _prov:
        print(f"  content: {_prov['content_digest']} "
              f"({_prov['file_count']} file(s)) built {_prov['built_at']}")
        print(f"  recorded in {report['dest']}\\\\walk.source.json")'''


EDITS = {PREVIEW: ((OLD_IMPORT, NEW_IMPORT), (OLD_HELPER, NEW_HELPER),
                   (OLD_RET, NEW_RET)),
         COMMANDS: ((OLD_PRINT, NEW_PRINT),)}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _find(body: str, anchor: str):
    candidate = _as(anchor, _eol(body))
    return candidate, body.count(candidate)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)
    eol = _eol(body)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()[:70]!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    try:
        compile(out, str(path), "exec")
    except SyntaxError as exc:
        print(f"REFUSING: {path.name} -- the patched file does not parse: {exc}")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
