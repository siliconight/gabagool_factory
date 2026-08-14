r"""level_factory 0.27.0, corrected BEFORE it is committed.

    python patch_lf_027b.py --check
    python patch_lf_027b.py
    python patch_lf_027b.py --selftest
    python patch_lf_027b.py --revert

Run from the FACTORY ROOT, AFTER patch_lf_027.py and BEFORE the 0.27.0
commit. It does not move VERSION -- 0.27.0 was never tagged, so there is no
released number to correct, only an uncommitted working tree.

WHY THIS EXISTS

0.27.0's selftest passed 40 of 40 and the real export ran green. Then the
archive it produced was opened and read, and `LF_MANIFEST.json` -- the file
whose entire job is telling a recipient what they are holding -- was wrong
about two of its fields. Neither check would have caught it, because both
asserted the plumbing carried what it was handed, and both times it did.

    "candidate": "lot_demo_001.candidate.seed_XXXX"
    "tools": { "deli_counter": "0.2.0", "lot": "0.4.0", "zoo": "0.3.0" }

TWO DEFECTS, AND ONLY ONE OF THEM IS MINE

MINE: `tools` was the ADAPTER versions.

`export_mission` receives `tool_versions=_adapter_versions()`, which is the
version of each ADAPTER inside Level Factory -- the code that drives a tool --
not the version of the tool. That parameter has always meant that; it feeds
`build_license_manifest`, where it is correct. I put it under a key named
`tools` and shipped `lot: 0.4.0` in a file a recipient reads to find out what
built their level, when lot is 0.41.0.

That is the exact failure this repo spent factory-v1.17.0 on: a number under
a label that names something else. The doc's own example says
`"tools": { "deli_counter": "0.89.0", "lot": "0.41.0" }` -- the certified set
-- and I had `factory.manifest.json` open in `_factory_pin` to read it from.

FIXED: `tools` is now the PINNED set from `factory.manifest.json`, which is
what `factory_tag` recovers and therefore the only set consistent with the
two fields beside it. The adapter versions keep their place under `adapters`,
labelled for what they are.

NOT MINE: `.selected` contains a literal placeholder.

    workspaces/lot-demo-ws/.level_factory/approvals/lot_demo_001.selected
      -> "lot_demo_001.candidate.seed_XXXX"

`cmd_approve` writes `--candidate` to that file verbatim, with nothing
checking it. Someone approved the gate with the template string from a doc
instead of a candidate id, and the marker has held it since 2026-08-13
23:21 UTC. The functional lock, written earlier the same day, has the real
answer: `lot_demo_001.candidate.seed_5219`.

This patch does NOT repair the marker and does not change what reads it.
What it does is stop the export from shipping the bad value, and start
saying so out loud:

  * `candidate` in the manifest comes from the lock first, marker second --
    the same precedence 0.27.0 already used for the seed, which is the only
    reason `"seed": 5219` came out right while `candidate` did not.
  * When the marker and the lock disagree, `cmd_export` prints both to
    stderr. It has been disagreeing silently for a day.

WHAT IS STILL WRONG AND IS NOT FIXED HERE, BECAUSE IT IS NOT A NAMING BUG

`_selected_lot_out` derives its path from that marker:

    jobs/lot_demo_001.lot_assemble.candidate.seed_XXXX/out   does not exist
    jobs/lot_demo_001.lot_assemble.candidate.seed_5219/out   is the real one

So `graybox_dir` in `cmd_export` is a dead path, and the export has been
succeeding on the Dispatch handoff alone. The same function feeds the
post-art functional-regression check a `site.site.gameplay.json` that is not
there; `_merged_gameplay` fills four of its six keys from the Deli side via
`setdefault`, so whether that check is still comparing anything real depends
on what the site file contributes, and I have not measured it. I am not
going to change which job directory an export reads from inside a patch about
filenames, and I am not going to assert a gate is vacuous without running it.
It needs its own patch and its own run.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPORT = "level_factory/packages/exporting/export.py"
COMMANDS = "level_factory/apps/cli/commands/__init__.py"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_027b"

EDITS: list[tuple[str, str, str]] = [
    # ----------------------------------------------------------- export.py --
    (EXPORT,
     "    built_utc: str | None = None,\n) -> ExportResult:\n",
     "    built_utc: str | None = None,\n"
     "    # The CERTIFIED SET from factory.manifest.json, which is what\n"
     "    # factory_tag recovers. Distinct from `tool_versions` above, which\n"
     "    # is the ADAPTER versions -- the code that drives each tool, not the\n"
     "    # tool. They differ by an order of magnitude (lot's adapter is\n"
     "    # 0.4.0; lot is 0.41.0) and 0.27.0 shipped the wrong one of the two\n"
     "    # under a key named `tools`.\n"
     "    pinned_tools: dict | None = None,\n"
     ") -> ExportResult:\n"),

    (EXPORT,
     '        "tools": {k: v for k, v in sorted(tool_versions.items())},\n',
     '        "tools": (dict(sorted(pinned_tools.items()))\n'
     "                  if pinned_tools else None),\n"
     '        "tools_source": ("factory.manifest.json" if pinned_tools\n'
     "                         else None),\n"
     "        # NOT the same numbers, and no longer pretending to be.\n"
     '        "adapters": {k: v for k, v in sorted(tool_versions.items())},\n'),

    # ----------------------------------------------------------- commands --
    (COMMANDS,
     "def _factory_pin() -> tuple[str | None, str | None]:\n",
     "def _factory_pin() -> tuple[str | None, str | None, dict | None]:\n"),

    # THE WHOLE BODY, not just the return. The first draft of this patch
    # replaced only the last two lines and referred to a `data` that the
    # lines above never bind -- they assign `v` straight off `json.loads`.
    # It compiled, applied, selftested green, and died at runtime with
    # `name 'data' is not defined` on the first real export. The `except`
    # branch was wrong in the same edit for the same reason: it still
    # returned a 2-tuple into a 3-way unpack, and only the error path would
    # ever have shown it.
    (COMMANDS,
     "        try:\n"
     "            v = json.loads(p.read_text(encoding=\"utf-8\")).get(\n"
     '                "factory_version")\n'
     "        except (OSError, ValueError):\n"
     "            return None, None\n"
     '        return (str(v), f"factory-v{v}") if v else (None, None)\n'
     "    return None, None\n",

     "        try:\n"
     '            data = json.loads(p.read_text(encoding="utf-8"))\n'
     "        except (OSError, ValueError):\n"
     "            return None, None, None\n"
     '        v = data.get("factory_version")\n'
     "        tools = {\n"
     '            name: str(e.get("version"))\n'
     '            for name, e in (data.get("tools") or {}).items()\n'
     '            if isinstance(e, dict) and e.get("version")\n'
     "        } or None\n"
     '        return ((str(v), f"factory-v{v}", tools) if v\n'
     "                else (None, None, tools))\n"
     "    return None, None, None\n"),

    (COMMANDS,
     "    factory_version, factory_tag = _factory_pin()\n",

     "    # WHICH CANDIDATE, from the lock first. Same precedence as the seed\n"
     "    # above, and for the same reason -- which is also the only reason\n"
     "    # `seed` came out right while `candidate` did not: the marker holds\n"
     "    # a literal `seed_XXXX` template that cmd_approve wrote verbatim\n"
     "    # from --candidate, and nothing has ever checked it.\n"
     "    lock_candidate = None\n"
     "    if lock_file.exists():\n"
     "        try:\n"
     "            lock_candidate = json.loads(\n"
     '                lock_file.read_text(encoding="utf-8")).get("candidate_id")\n'
     "        except (OSError, ValueError):\n"
     "            lock_candidate = None\n"
     "    if (lock_candidate and selected_candidate\n"
     "            and lock_candidate != selected_candidate):\n"
     "        # SAY IT EVERY TIME. This has been true and silent since\n"
     "        # 2026-08-13, and it only surfaced because someone opened the\n"
     "        # archive and read the file it ended up in.\n"
     '        print(f"[export] WARNING the candidate_selected marker and the '
     'functional lock disagree:", file=sys.stderr)\n'
     '        print(f"[export]   marker: {selected_candidate}", file=sys.stderr)\n'
     '        print(f"[export]   lock:   {lock_candidate}", file=sys.stderr)\n'
     '        print(f"[export]   the lock wins for the export manifest; '
     'jobs are still resolved from the marker", file=sys.stderr)\n'
     "    export_candidate = lock_candidate or selected_candidate\n"
     "    factory_version, factory_tag, pinned_tools = _factory_pin()\n"),

    (COMMANDS,
     "        seed=export_seed, candidate_id=selected_candidate,\n",
     "        seed=export_seed, candidate_id=export_candidate,\n"
     "        pinned_tools=pinned_tools,\n"),

    # ----------------------------------------------------------- CHANGELOG --
    (CHANGELOG,
     "Stage 1b of `docs/EXPORT_NAMING.md`. 0.26.0 landed the build directory; this\n"
     "lands the archive name, the stable folder inside it, and `LF_MANIFEST.json`.\n",

     "Stage 1b of `docs/EXPORT_NAMING.md`. 0.26.0 landed the build directory; this\n"
     "lands the archive name, the stable folder inside it, and `LF_MANIFEST.json`.\n"
     "\n"
     "CORRECTED BEFORE COMMIT, AND THE CORRECTION IS THE INTERESTING PART\n"
     "\n"
     "The selftest passed 40 of 40 and the real export ran green. Then the\n"
     "archive was opened and `LF_MANIFEST.json` -- the file whose whole job is\n"
     "telling a recipient what they hold -- was wrong about two fields. Neither\n"
     "check would ever have caught it: both asserted that the plumbing carried\n"
     "what it was handed, and both times it did. What was handed in was wrong.\n"
     "\n"
     "    \"candidate\": \"lot_demo_001.candidate.seed_XXXX\"\n"
     "    \"tools\": { \"deli_counter\": \"0.2.0\", \"lot\": \"0.4.0\" }\n"
     "\n"
     "`tools` was the ADAPTER versions. `export_mission` is handed\n"
     "`_adapter_versions()` -- the version of the code that DRIVES each tool --\n"
     "and that is correct for `build_license_manifest`, which is what the\n"
     "parameter was added for. Putting it under a key named `tools` shipped\n"
     "`lot: 0.4.0` to a reader asking what built their level, when lot is\n"
     "0.41.0. That is the same defect factory-v1.17.0 was spent on: a number\n"
     "under a label naming something else. `tools` is now the pinned set from\n"
     "`factory.manifest.json` -- the set `factory_tag` recovers, and therefore\n"
     "the only one consistent with the two fields beside it -- and the adapter\n"
     "versions keep their place under `adapters`, labelled for what they are.\n"
     "\n"
     "`candidate` came from `.selected`, which holds the literal string\n"
     "`lot_demo_001.candidate.seed_XXXX`. `cmd_approve` writes `--candidate`\n"
     "to that file verbatim and nothing checks it; someone approved the gate\n"
     "with a doc's placeholder. The functional lock has the real answer, and\n"
     "the manifest now reads the lock first -- the same precedence the seed\n"
     "already used, which is the only reason `\"seed\": 5219` was right in the\n"
     "same file where `candidate` was not. When the two disagree, `cmd_export`\n"
     "now prints both to stderr instead of picking one quietly.\n"
     "\n"
     "AND THE FIX FOR THAT SHIPPED A NameError, WHICH IS WORTH RECORDING.\n"
     "\n"
     "The first draft of the correction rewrote only `_factory_pin`'s return\n"
     "statement and referred to a `data` the lines above never bind. It\n"
     "compiled, applied, and passed a selftest of seventeen checks -- all of\n"
     "which read STRINGS out of the patched file rather than calling the\n"
     "function. The first real export died with `name 'data' is not defined`\n"
     "after the manifest work had already run. The same edit left the\n"
     "`except` branch returning a 2-tuple into a 3-way unpack, reachable only\n"
     "on an unreadable manifest, which no check would have reached either.\n"
     "The selftest now calls `_factory_pin` against this checkout and against\n"
     "a deliberately corrupt manifest. A helper that resolves something from\n"
     "disk is exercised against disk, or it is not tested.\n"
     "\n"
     "STILL WRONG, NOT FIXED HERE. `_selected_lot_out` builds a job path from\n"
     "that same marker, so `graybox_dir` points at\n"
     "`lot_assemble.candidate.seed_XXXX/out`, which does not exist -- the\n"
     "export has been succeeding on the Dispatch handoff alone. The same\n"
     "function feeds the post-art regression check a `site.site.gameplay.json`\n"
     "that is not there. Whether that check still compares anything real\n"
     "depends on what the site file contributes to signatures\n"
     "`_merged_gameplay` otherwise fills from the Deli side, and that has not\n"
     "been measured. Changing which job directory an export reads from does\n"
     "not belong in a patch about filenames, and a gate should not be called\n"
     "vacuous without running it.\n"),
]

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    # Refuse to run before 0.27.0, or after the commit it is meant to precede.
    v = (root / "level_factory" / "VERSION").read_text(encoding="utf-8")
    if "0.27.0" not in v:
        print(f"REFUSING: level_factory/VERSION says {v.strip()!r}, not 0.27.0 "
              f"-- run patch_lf_027.py first")
        return 1

    # The first draft of this patch is on some disks, applied and broken --
    # `_factory_pin` referring to an unbound `data`. Its anchors are gone, so
    # this would otherwise refuse with an anchor count of 0 and leave the
    # reader guessing which of two states they are in. Name it instead.
    cmds = (root / COMMANDS).read_text(encoding="utf-8")
    # SCOPED TO THE FUNCTION. The first version of this guard searched the
    # whole 112 KB module for `data = json.loads(`, which appears in it for
    # unrelated reasons, so the guard never fired -- a check that looked
    # right and matched something else. Twice in one patch now.
    _i = cmds.find("def _factory_pin(")
    _fn = cmds[_i:cmds.find("\ndef ", _i + 1)] if _i >= 0 else ""
    if ('(data.get("tools") or {}).items()' in _fn
            and "data = json.loads(" not in _fn):
        print("REFUSING: the FIRST draft of patch_lf_027b is applied here -- "
              "its _factory_pin raises NameError: name 'data' is not defined.")
        print("  Revert it, then run this again:")
        print("      python patches\\patch_lf_027b.py --revert")
        return 1

    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        raw = p.read_bytes()
        body = raw.decode("utf-8")
        if body.count(_CRLF):
            print(f"REFUSING: {rel} has CRLF line endings; these anchors are LF")
            return 1
        out, done = body, 0
        for old, new in edits:
            if new in out:
                done += 1
                continue
            if out.count(old) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old, new, 1)

        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
        if rel.endswith(".py"):
            try:
                compile(out, str(p), "exec")
            except SyntaxError as exc:
                print(f"REFUSING: {rel} -- does not parse after the edit: {exc}")
                return 1
        data = out.encode("utf-8")
        if data == raw:
            print(f"  already applied  {rel}")
            continue
        if check:
            print(f"  would patch  {rel}  {len(raw):,} -> {len(data):,} bytes "
                  f"({len(data) - len(raw):+,})")
            continue
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        p.write_bytes(data)
        print(f"  patched      {rel}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import importlib
    import json
    import tempfile
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    exp = importlib.import_module("packages.exporting.export")
    importlib.reload(exp)

    PINNED = {"lot": "0.41.0", "deli_counter": "0.89.0", "zoo": "0.36.0"}
    ADAPTERS = {"lot": "0.4.0", "deli_counter": "0.2.0", "zoo": "0.3.0"}

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        handoff = tmp / "handoff"
        handoff.mkdir()
        (handoff / "mission.tscn").write_text("[gd_scene]\n", encoding="utf-8")
        result = exp.export_mission(
            mission_id="m1", handoff_dir=handoff, presentation_dir=None,
            source_dir=None, profile=exp.ExportProfile(),
            tool_versions=ADAPTERS, out_root=tmp / "exports",
            seed=5219, candidate_id="m1.candidate.seed_5219",
            factory_version="1.18.0", pinned_tools=PINNED,
            built_utc="2026-08-14T20:32:26+00:00")
        man = json.loads((result.export_dir / exp.EXPORT_MANIFEST_NAME)
                         .read_text(encoding="utf-8"))

        check("tools is the CERTIFIED set, not the adapters",
              man["tools"] == dict(sorted(PINNED.items())))
        check("lot reads 0.41.0, the number a recipient wants",
              man["tools"]["lot"] == "0.41.0")
        check("and says where that set came from",
              man["tools_source"] == "factory.manifest.json")
        check("the adapter versions survive, under their own name",
              man["adapters"] == dict(sorted(ADAPTERS.items())))
        check("and are NOT the same numbers",
              man["adapters"]["lot"] != man["tools"]["lot"])
        check("tools agrees with the tag beside it",
              man["factory_tag"] == "factory-v1.18.0")

        # No pin available -> null, not a silent fallback to the adapters.
        r2 = exp.export_mission(
            mission_id="m2", handoff_dir=handoff, presentation_dir=None,
            source_dir=None, profile=exp.ExportProfile(),
            tool_versions=ADAPTERS, out_root=tmp / "exports2",
            built_utc="2026-08-14T20:32:26+00:00")
        m2 = json.loads((r2.export_dir / exp.EXPORT_MANIFEST_NAME)
                        .read_text(encoding="utf-8"))
        check("with no pin, tools is null rather than the adapters again",
              m2["tools"] is None and m2["tools_source"] is None)
        check("and the adapters are still recorded",
              m2["adapters"] == dict(sorted(ADAPTERS.items())))

    # CALL IT. The first draft of this patch checked _factory_pin by reading
    # strings out of the file, which is how a NameError shipped: every string
    # was present and the function could not run. A helper that resolves
    # something from disk gets exercised against disk.
    cmd = importlib.import_module("apps.cli.commands")
    importlib.reload(cmd)
    pin = cmd._factory_pin()
    check("_factory_pin runs at all, and returns three values",
          isinstance(pin, tuple) and len(pin) == 3)
    version, tag, tools = pin
    check("it finds this factory's version by walking up",
          bool(version) and tag == f"factory-v{version}")
    check("and the pinned set it returns is the manifest's",
          isinstance(tools, dict) and tools.get("lot")
          == json.loads((root / "factory.manifest.json").read_text(
              encoding="utf-8"))["tools"]["lot"]["version"])
    check("which is a real tool version, not an adapter version",
          tools.get("level_factory", "").startswith("0.2"))

    # The error path returns three values too -- the branch the string-only
    # check could not see.
    import tempfile as _tf
    with _tf.TemporaryDirectory() as td:
        bad_root = Path(td)
        (bad_root / "factory.manifest.json").write_text("{not json",
                                                        encoding="utf-8")
        src = (root / COMMANDS).read_text(encoding="utf-8")
        i = src.index("def _factory_pin(")
        j = src.index("def _lock_path(")
        ns: dict = {"Path": Path, "json": json, "__file__":
                    str(bad_root / "a" / "b" / "c.py")}
        exec(compile(src[i:j], "<_factory_pin>", "exec"), ns)
        check("an unreadable manifest still returns three values",
              ns["_factory_pin"]() == (None, None, None))

    cmds = (root / COMMANDS).read_text(encoding="utf-8")
    check("the CLI reads the candidate off the lock",
          'lock_candidate = json.loads(' in cmds
          and 'get("candidate_id")' in cmds)
    check("the lock wins over the marker",
          "export_candidate = lock_candidate or selected_candidate" in cmds)
    check("and a disagreement is printed, not resolved quietly",
          "the candidate_selected marker and the functional lock disagree"
          in cmds)
    check("the pinned set is read from the manifest and passed down",
          "pinned_tools=pinned_tools" in cmds
          and "factory_version, factory_tag, pinned_tools = _factory_pin()"
          in cmds)
    check("and the old two-value unpacking is gone, with one caller left",
          "factory_version, factory_tag = _factory_pin()" not in cmds
          and cmds.count("= _factory_pin()") == 1)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check("0.27.0 is still one entry and was not renumbered",
          cl.count("## [0.27.0]") == 1 and "## [0.28.0]" not in cl)
    check("the entry records both defects",
          "seed_XXXX" in cl and "ADAPTER versions" in cl)
    check("and names the one it did not fix",
          "STILL WRONG, NOT FIXED HERE" in cl and "_selected_lot_out" in cl)
    check("and refuses to call the regression gate vacuous unrun",
          "should not be called\nvacuous without running it" in cl)

    print()
    print("  the manifest names the certified set, and the marker's lie is loud"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel in (EXPORT, COMMANDS, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        return bad

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lf_027b.py --selftest")
        print()
        print("  THEN RE-EXPORT -- the manifest inside the package changed,")
        print("  and the archive built before this one carries the bad values:")
        print("    python -m level_factory -C workspaces\\lot-demo-ws \\")
        print("        export lot_demo_001 --mode portable-godot --format zip")
        print()
        print("  expect a WARNING naming the marker/lock disagreement.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
