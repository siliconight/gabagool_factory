"""Make themed_site_assemble emit a coherent, relocatable site package.

Run from the factory root:

    python patch_lf_walkable_site.py            # apply
    python patch_lf_walkable_site.py --check    # report only, write nothing

Every edit asserts its anchor and the script refuses to write if any one of
them has drifted, rather than applying a partial change.

THE DEFECT. `themed_site_assemble` emits site.tscn referencing its buildings as
`res://C:/Projects/...`. `res://` is rooted at the Godot project directory, so
that asks for a folder literally named `C:` inside the project and can resolve
nowhere -- not in a preview project, not in a consumer's, not at all. Nothing
ever loaded the scene, so nothing ever said so.

WHAT CHANGES. The site spec names its buildings by paths relative to the site's
own out dir; a new first planned command copies those sources in under exactly
those names and rewrites their internal refs to be scene-relative; and Lot is
asked for `--portable` so the site and walk scenes reference their contents
relative to themselves. The result is a folder a consumer can drop anywhere.

FOUR THINGS THIS ALSO REPAIRS, each measured rather than assumed:

1. `collect_outputs` filtered to .tscn/.json/.csv, so staged geometry would
   never reach out/ or the build cache. The first run would have looked right
   in the attempt dir and a CACHE HIT would have restored a site with no
   buildings in it.
2. `fingerprint_inputs` re-reads the spec and folds every path it names, so
   that a building added there cannot be missed. Those `_fold` calls test
   `path.exists()` against the process CWD, so relative refs would silently
   drop out and the fingerprint would stop watching the buildings. It now
   folds the staging manifest, which is derived from the same spec.
3. The scheduler checked `planned[0].expected_outputs` only. Any adapter
   planning more than one command has had its later outputs unchecked, and a
   check that cannot fail is indistinguishable from one that passed.
4. `adapter_version` is bumped because the OUTPUT LAYOUT changed. Without it
   every existing cache entry stays valid and a re-run serves the old broken
   site from cache while reporting success.

THE GREYBOX PATH GETS THE SAME FIX. Its buildings[].glb refs were absolute too,
so lot_assemble has always emitted res://C:/ as well. Its nav-QA scene is
deliberately left on res://addons/lot/: that scene is consumed by Lot's own
walktest harness, which supplies addons/lot/ and resolves it today.
"""
from __future__ import annotations

import sys
from pathlib import Path

CLI = Path("level_factory/apps/cli/commands/__init__.py")
ADAPTER = Path("level_factory/adapters/lot/__init__.py")
SCHED = Path("level_factory/packages/jobs/scheduler.py")

EDITS: list[tuple[Path, str, str, str]] = []

# ---------------------------------------------------------------------------
# 1. the site spec names relative paths, and records where to copy them from
# ---------------------------------------------------------------------------
EDITS.append((CLI, "spec: staging accumulators", """\
    count = max(1, int(getattr(model, "building_count", 1) or 1))
    glb = str(_latest_output(deli_out, "shell.glb"))
    gameplay = str(_latest_output(deli_out, "shell.gameplay.json"))
""", """\
    count = max(1, int(getattr(model, "building_count", 1) or 1))
    glb = str(_latest_output(deli_out, "shell.glb"))
    gameplay = str(_latest_output(deli_out, "shell.gameplay.json"))

    # WHERE EACH BUILDING COMES FROM, beside where the spec will name it.
    #
    # The spec's geometry refs are relative to the site's own out dir, because
    # Lot writes each ext_resource as os.path.join(glb_dir, src) with
    # glb_dir=".": an absolute src passes straight through and ships as
    # res://C:/..., which is a request for a folder named "C:" inside the
    # consumer's project. So the spec says "lot/<id>/site.tscn" and a staging
    # step run before Lot puts the package there.
    #
    # These are ABSOLUTE and stay absolute. They are build inputs, not
    # deliverables -- the staging step reads them and the fingerprint watches
    # them, and neither of those happens inside a Godot project.
    #
    # CONSTRUCTED, NOT PROBED, for the same reason the rest of this function
    # is: it runs while the plan is built, before any compose job has produced
    # anything. Nothing here may ask whether a source exists in order to decide
    # what to do; the staging step refuses at run time if one is missing.
    staged_packages: dict[str, str] = {}
    staged_glbs: dict[str, str] = {}
"""))

EDITS.append((CLI, "spec: varied lot source", """\
        def _source(entry):
            scene = (themed_map or {}).get(entry["id"])
            return {"scene": scene} if scene else {"glb": entry["glb"]}
""", """\
        def _source(entry):
            aid = str(entry["id"])
            scene = (themed_map or {}).get(entry["id"])
            if scene:
                # The package is the composed scene's whole DIRECTORY: site.tscn
                # is useless without the site_base.glb and art/ beside it, every
                # one of which it references as res://<name> rooted at that
                # package.
                staged_packages[aid] = str(Path(scene).parent)
                return {"scene": f"lot/{aid}/site.tscn"}
            staged_glbs[aid] = str(entry["glb"])
            return {"glb": f"buildings/{aid}.glb"}
"""))

EDITS.append((CLI, "spec: single-shell source", """\
        source = ({"scene": themed_scene}
                  if themed_scene and not themed_map else {"glb": glb})
""", """\
        # Same defect, same fix, on the path that predates the varied lot: this
        # one has been emitting res://C:/ for as long as it has existed.
        if themed_scene and not themed_map:
            staged_packages["shell"] = str(Path(themed_scene).parent)
            source = {"scene": "lot/shell/site.tscn"}
        else:
            staged_glbs["shell"] = glb
            source = {"glb": "buildings/shell.glb"}
"""))

EDITS.append((CLI, "spec: write the staging manifest", """\
    dest = (ws.internal_dir / "temp" / model.mission_id
            / f"candidate_seed_{int(seed)}"
            / ("themed" if themed_scene else "")
            / "site.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(pretty_dumps(spec), encoding="utf-8")
    return dest
""", """\
    dest = (ws.internal_dir / "temp" / model.mission_id
            / f"candidate_seed_{int(seed)}"
            / ("themed" if themed_scene else "")
            / "site.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(pretty_dumps(spec), encoding="utf-8")

    # The staging manifest, beside the spec it belongs to. Separate file rather
    # than extra keys in the spec because Lot reads the spec and this is not
    # Lot's business -- and because a spec that carried absolute source paths
    # would be exactly the artifact this change exists to stop shipping.
    #
    # `gameplay` refs stay absolute in the spec on purpose. They are read by
    # merge_gameplay at build time and never appear in any emitted scene, so
    # they are a build input like these are, and keeping them resolvable is
    # what lets fingerprint_inputs keep watching them.
    repos = ws.load_tools_local().get("repositories", {})
    lot_repo = str(repos.get("lot", ""))
    manifest = {
        "packages": staged_packages,
        "glbs": staged_glbs,
        # Lot's walk scene, asked for portably, names these bare at the site
        # root rather than under addons/lot/ -- so the pack never has to claim
        # an addons/ directory inside somebody else's project.
        "addon_dir": (str(Path(lot_repo) / "godot" / "addons" / "lot")
                      if lot_repo else ""),
    }
    (dest.parent / "packages.json").write_text(
        pretty_dumps(manifest), encoding="utf-8")
    return dest
"""))

EDITS.append((CLI, "job spec: hand the manifest to the adapter", """\
            specs[job.job_id] = {
                "site_spec_path": str(site_spec),
                "walkable": True,
""", """\
            specs[job.job_id] = {
                "site_spec_path": str(site_spec),
                # Written beside the spec by _write_site_spec. The adapter
                # plans a staging command against it before Lot runs.
                "staging_manifest_path": str(
                    Path(site_spec).parent / "packages.json"),
                "walkable": True,
"""))

# ---------------------------------------------------------------------------
# 2. the adapter: stage first, ask Lot for portable refs, publish the geometry
# ---------------------------------------------------------------------------
EDITS.append((ADAPTER, "adapter: version bump", '''\
    adapter_version = "0.3.0"
''', '''\
    # 0.4.0: the OUTPUT LAYOUT changed -- buildings are staged under lot/<id>/
    # and every ext_resource is relative rather than res://C:/... An entry
    # cached under the old rules is a site whose refs resolve nowhere, so it
    # must be retired rather than served alongside the new ones.
    adapter_version = "0.4.0"
'''))

EDITS.append((ADAPTER, "adapter: collect .glb and .gd", '''\
        wanted = (".tscn", ".json", ".csv")
''', '''\
        # .glb and .gd are here because the site now CONTAINS its buildings
        # rather than pointing at them. Left at (.tscn, .json, .csv), the staged
        # geometry and the walk scripts would never be published to out/ nor
        # written to the build cache: the attempt dir would look correct and a
        # cache hit would restore a site scene referencing files that are not
        # there. A published artifact has to be the whole artifact.
        wanted = (".tscn", ".json", ".csv", ".glb", ".gd")
'''))

EDITS.append((ADAPTER, "adapter: plan the staging command", '''\
        args = [str(repo / "lot.py"), spec, str(work)]
        if job_spec.get("walkable", True):
            args.append("--walkable")
        if job_spec.get("navqa"):
            args.append("--navqa")
''', '''\
        args = [str(repo / "lot.py"), spec, str(work)]
        if job_spec.get("walkable", True):
            args.append("--walkable")
        if job_spec.get("navqa"):
            args.append("--navqa")
        # Scene-relative ext_resource paths in the shipped scenes. Godot 4.7
        # resolves a non-res:// path against the referencing scene's own
        # directory (probed: a root scene instancing lot/a/inner.tscn, which
        # named a bare leaf.tscn existing only beside it, imported and loaded
        # clean), which is what makes the out dir droppable anywhere rather
        # than only at a consumer's project root.
        manifest = str(job_spec.get("staging_manifest_path", ""))
        if manifest:
            args.append("--portable")

        commands = []
        if manifest:
            # FIRST, and a separate command rather than a side effect inside
            # this function: plan_commands is called to build the fingerprint
            # as well as to run the job, including on the cache-hit path where
            # nothing is meant to execute. Copying geometry from here would run
            # at times nobody chose. As a planned command it is logged,
            # re-runnable alone, and folded into the fingerprint like any other.
            # this file is level_factory/adapters/lot/__init__.py, so the
            # level_factory root is three names up: lot -> adapters -> here.
            lf_root = Path(__file__).resolve().parents[2]
            commands.append(PlannedCommand(
                executable=Path(str(py)),
                arguments=(str(lf_root / "tools" / "stage_site_packages.py"),
                           manifest, str(work)),
                working_directory=lf_root,
                expected_outputs=tuple(self._staged_outputs(manifest)),
                resource_class="python_cpu",
                timeout_seconds=600,
            ))
'''))

EDITS.append((ADAPTER, "adapter: return both commands", '''\
        return [
            PlannedCommand(
                executable=Path(str(py)),
                arguments=tuple(args),
                working_directory=repo,
                expected_outputs=tuple(expected),
                resource_class="python_cpu",
                timeout_seconds=600,
            )
        ]
''', '''\
        commands.append(PlannedCommand(
            executable=Path(str(py)),
            arguments=tuple(args),
            working_directory=repo,
            expected_outputs=tuple(expected),
            resource_class="python_cpu",
            timeout_seconds=600,
        ))
        return commands

    @staticmethod
    def _staged_outputs(manifest_path: str) -> list[str]:
        """What the staging step must have put in the out dir, by name.

        Named as expected outputs so the scheduler fails the job when a package
        did not arrive, instead of leaving it to Lot to emit a site with a
        building missing and every stage reporting success -- which a varied lot
        has already done once.
        """
        try:
            doc = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            # The manifest is written at plan time and read here at run time.
            # If it cannot be read there is nothing to assert; the staging
            # command will say so itself and exit nonzero.
            return []
        out = [f"lot/{pid}/site.tscn" for pid in (doc.get("packages") or {})]
        out += [f"buildings/{bid}.glb" for bid in (doc.get("glbs") or {})]
        return sorted(out)
'''))

EDITS.append((ADAPTER, "adapter: fingerprint the staged sources", '''\
        if inputs:
            fp["building_hashes"] = inputs
        return fp
''', '''\
        # The staged sources, by their ABSOLUTE build-time paths.
        #
        # The loop above reads the spec rather than trusting the caller's list,
        # so a building added to the spec cannot be missed by someone forgetting
        # to extend a parallel argument. That property depends on the paths in
        # the spec resolving, and they are now relative to the site out dir --
        # so `_fold` would test them against the process CWD, miss, and quietly
        # fold nothing. The manifest is derived from the same spec by the same
        # function, so folding it keeps the property rather than replacing it
        # with a promise.
        manifest_path = job_spec.get("staging_manifest_path")
        if manifest_path and Path(str(manifest_path)).exists():
            try:
                man = json.loads(
                    Path(str(manifest_path)).read_text(encoding="utf-8"))
            except (OSError, ValueError):
                man = {}
            for source in (man.get("packages") or {}).values():
                _fold(Path(str(source)) / "site.tscn")
            for source in (man.get("glbs") or {}).values():
                _fold(Path(str(source)))
        if inputs:
            fp["building_hashes"] = inputs
        return fp
'''))

# ---------------------------------------------------------------------------
# 3. the scheduler checks every planned command's contract, not just the first
# ---------------------------------------------------------------------------
EDITS.append((SCHED, "scheduler: check all expected outputs", '''\
        missing = [o for o in planned[0].expected_outputs
                   if not (work_dir / o).exists()] if planned else []
''', '''\
        # EVERY planned command's contract, not just the first one's. This read
        # planned[0] alone, so an adapter that plans more than one command had
        # its later outputs unchecked -- and a check that cannot fail is
        # indistinguishable from one that passed.
        missing = [o for cmd in planned for o in cmd.expected_outputs
                   if not (work_dir / o).exists()]
'''))


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    for path in (CLI, ADAPTER, SCHED):
        if not path.is_file():
            print(f"[patch] {path} not found -- run from the factory root")
            return 1

    files: dict[Path, tuple[bytes, bool, str]] = {}
    for path in (CLI, ADAPTER, SCHED):
        raw = path.read_bytes()
        crlf = b"\r\n" in raw
        files[path] = (raw, crlf, raw.decode("utf-8").replace("\r\n", "\n"))
        print(f"[patch] {path}: {len(raw)} bytes, "
              f"endings={'CRLF' if crlf else 'LF'}")

    problems = []
    for path, name, before, _ in EDITS:
        text = files[path][2]
        after = next(a for p, n, b, a in EDITS if n == name)
        if after in text:
            print(f"[patch]   ALREADY APPLIED: {name}")
        elif before not in text:
            print(f"[patch]   ANCHOR NOT FOUND: {name}")
            problems.append(name)
        elif text.count(before) != 1:
            print(f"[patch]   ANCHOR NOT UNIQUE ({text.count(before)}x): {name}")
            problems.append(name)

    if problems:
        print("[patch] REFUSING to write: "
              f"{len(problems)} anchor(s) did not match cleanly. The source has "
              "drifted from what this patch was written against -- re-read it "
              "and re-author rather than forcing a partial edit.")
        return 1

    for path, name, before, after in EDITS:
        raw, crlf, text = files[path]
        if after in text:
            continue
        files[path] = (raw, crlf, text.replace(before, after))
        print(f"[patch]   applied: {name}")

    # `json` is used by the adapter's new fingerprint and expected-output code;
    # it is already imported there, but say so rather than assume it.
    adapter_text = files[ADAPTER][2]
    if "\nimport json\n" not in adapter_text:
        print("[patch] REFUSING: the lot adapter does not import json, which "
              "the new code needs. Add the import and re-run.")
        return 1

    if check_only:
        print("[patch] --check: no write")
        return 0

    for path, (raw, crlf, text) in files.items():
        payload = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
        path.write_bytes(payload)
        print(f"[patch] wrote {path}: {len(raw)} -> {len(payload)} bytes "
              f"({len(payload) - len(raw):+d})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
