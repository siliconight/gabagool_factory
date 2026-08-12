"""Resolve a content layer when it EXISTS, not when the spec is written.

Run from the factory root:

    python patch_lf_layer_resolve.py --check
    python patch_lf_layer_resolve.py

## The defect this repairs, measured

After the fan-out landed, `probe_dressing.tscn` reported no `Dressing` and no
`Fixtures` node on any of the five buildings. The compose job's own log shows
why -- the argv carried neither flag:

    run_presentation_compose.py --deli-repo ... --slots ...lf_lot_demo_001_5017.slots.json
      --modules ... --theme rockay --style 1 --greybox ... --building-id site
      --out ... --gameplay ...

`_layer_paths` resolved each layer by GLOBBING the producing job's output
directory. `_job_specs_for_plan` runs BEFORE ANY JOB EXECUTES, and the
per-building dressing jobs were new job ids with empty out dirs, so every glob
came back empty, every layer resolved to `""`, and the flag was silently
dropped.

This is the trap `docs/WALKABLE_SITE.md` states in capitals:

    PATHS ARE CONSTRUCTED, NOT PROBED. Every spec in this function is built
    BEFORE any job runs, so the compose output does not exist yet -- an
    `.is_file()` here silently yielded {} and the site placed the mission shell
    five times while every archetype composed correctly beside it.

## What it says about the code that came before

The glob was inherited from `_layer_glb`, which did the same thing and appeared
to work. It appeared to work because the workspace already held
`lf_lot_demo_001_5118_dressing.glb` in a stable out dir from an earlier run --
the glob was reading a STALE ARTIFACT from a previous build. On a clean
workspace the single-shell path never attached dressing either. The fan-out did
not introduce this; it removed the stale file that was hiding it.

## The fix

Two moments, separated:

- SPEC TIME builds a directory path from a job id. Constructed, never probed.
- EXECUTION TIME resolves the file inside it, in the adapter, where the
  producing job has completed and the file is really there.

`plan_commands` and `validate_configuration` both run inside `_attempt_job`,
after this job's dependencies have succeeded -- the same property the site
staging step relies on.

## And it refuses rather than dropping the flag

The old behaviour on a missing layer was to pass no `--dressing` and compose a
bare building, successfully. A building silently missing its props is the same
class of failure as a lot silently missing a building: the run reports success
and the artifact is not what was asked for. `validate_configuration` now fails
the job and names the directory it looked in.
"""
from __future__ import annotations

import sys
from pathlib import Path

CLI = Path("level_factory/apps/cli/commands/__init__.py")
PRES = Path("level_factory/adapters/presentation/__init__.py")
TEST = Path("level_factory/tests/unit/test_fanout.py")

EDITS: list[tuple[Path, str, str, str]] = [
    (CLI, "cli: hand over the directory, not a guessed file", '''\
                deps = set(job.depends_on)
                found: dict[str, str] = {}
                for dep in plan.graph.jobs():
                    if dep.job_id not in deps or dep.stage_id != stage:
                        continue
                    hits = sorted((jobs_dir / dep.job_id / "out")
                                  .glob(f"*{suffix}"))
                    if len(hits) > 1:
                        raise RuntimeError(
                            f"{dep.job_id} published {len(hits)} '{suffix}' "
                            f"layers ({', '.join(h.name for h in hits)}); one "
                            f"bake is one placement against one shell and there "
                            f"is no basis for choosing between them")
                    found[getattr(dep, "archetype_id", None) or ""] = (
                        str(hits[0]) if hits else "")
                return found
''', '''\
                deps = set(job.depends_on)
                found: dict[str, str] = {}
                for dep in plan.graph.jobs():
                    if dep.job_id not in deps or dep.stage_id != stage:
                        continue
                    found[getattr(dep, "archetype_id", None) or ""] = str(
                        jobs_dir / dep.job_id / "out")
                return found
'''),
    (CLI, "cli: name what the layer keys now mean", '''\
            def _layer_paths(stage: str, suffix: str) -> dict:
                """``{archetype_id or "": glb}`` -- one CONTENT LAYER per building.
''', '''\
            def _layer_paths(stage: str, suffix: str) -> dict:
                """``{archetype_id or "": out_dir}`` -- where each building's
                CONTENT LAYER will be, once its job has run.

                A DIRECTORY, and constructed from a job id rather than found on
                disk. This globbed for the file itself and returned `""` when it
                found nothing -- and it always found nothing, because this whole
                function runs BEFORE ANY JOB EXECUTES. Measured 2026-08-06: five
                composed buildings, zero `--dressing` flags, and a probe
                reporting no Dressing node anywhere. It had appeared to work only
                while a previous run's artifact happened to be sitting in a
                stable out dir for the glob to find.

                The adapter resolves the file inside this directory at execution
                time, when the producing job has finished. See
                docs/WALKABLE_SITE.md's rule: paths are constructed, not probed.
''')
,
    (PRES, "presentation: a layer dir resolves to its one file", '''\
def _driver_path() -> Path:
''', '''\
def resolve_layer(directory: str, suffix: str) -> tuple[str, str]:
    """``(path, problem)`` -- the one ``*<suffix>`` file in ``directory``.

    Called at EXECUTION time, from `validate_configuration` and
    `plan_commands`, both of which run after this job's dependencies have
    succeeded. The spec can only construct the directory: it is written while
    the plan is built, before the job that fills it has run.

    Returns a problem string rather than raising so the caller can collect
    every fault and report them together -- a compose missing three layers is
    making three statements.

    Absence is a PROBLEM, not an empty answer. Passing no `--dressing` composes
    a bare building and exits zero, so a building silently missing its props
    looks exactly like a building that was never meant to have any.
    """
    root = Path(str(directory))
    if not root.is_dir():
        return "", f"layer directory missing: {root}"
    hits = sorted(root.glob(f"*{suffix}"))
    if not hits:
        return "", (f"no '*{suffix}' in {root} -- the job that bakes it "
                    f"reported success without publishing one")
    if len(hits) > 1:
        return "", (f"{root} holds {len(hits)} '{suffix}' layers "
                    f"({', '.join(h.name for h in hits)}); one bake is one "
                    f"placement against one shell and there is no basis for "
                    f"choosing between them")
    return str(hits[0]), ""


def _driver_path() -> Path:
'''),
    (PRES, "presentation: refuse a layer that is not there", '''\
        for a in _lot_archetypes(job_spec):
            for key in ("glb", "slots", "gameplay"):
                p = a.get(key)
                if p and not Path(str(p)).exists():
                    problems.append(
                        f"lot archetype {a['id']}: {key} missing: {p}")
        return problems
''', '''\
        for a in _lot_archetypes(job_spec):
            for key in ("glb", "slots", "gameplay"):
                p = a.get(key)
                if p and not Path(str(p)).exists():
                    problems.append(
                        f"lot archetype {a['id']}: {key} missing: {p}")
        # Every content layer this job was told about must actually be there.
        # It runs after the bakes have succeeded, so an empty directory here is
        # a real fault -- and the alternative is composing a bare building and
        # exiting zero, which is how five buildings came out undressed with
        # every stage reporting success.
        for key, suffix in (("dressing_glb", "_dressing.glb"),
                            ("fixtures_glb", "_fixtures.glb")):
            for aid, directory in sorted(_layer_map(job_spec.get(key)).items()):
                _, problem = resolve_layer(directory, suffix)
                if problem:
                    problems.append(
                        f"{key} for {aid or 'the mission shell'}: {problem}")
        return problems
'''),
    (TEST, "test: a first run must FAIL, not compose without props", '''\
def test_an_unresolved_layer_is_an_empty_string_not_a_neighbours(tmp_path, monkeypatch):
    """A first run has published nothing. Nobody inherits anybody's props."""
    brief = _brief(_library(tmp_path / "build"))
    plan = _plan(brief)
    specs = _specs(tmp_path, plan, brief, monkeypatch, publish=False)
    spec = specs[_stages(plan, "presentation_compose")[0].job_id]
    assert set(spec["dressing_glb"].values()) == {""}
    assert all("--dressing" not in a for a in _compose_args(spec, tmp_path))
''', '''\
def test_an_unbaked_layer_refuses_rather_than_being_dropped(tmp_path, monkeypatch):
    """A first run has published nothing -- and that must FAIL the job.

    This test previously asserted the opposite: that every layer resolved to
    `""` and no `--dressing` was passed at all. That is precisely what shipped
    on 2026-08-06, and the probe found five buildings with no props on any of
    them. "Nobody inherits anybody's props" was the right instinct. "So nobody
    gets any props, and the run succeeds" was the wrong conclusion, and it was
    sitting in this file labelled as intended behaviour.

    A compose that cannot find a bake it was told about is a failed job, not a
    bare building.
    """
    brief = _brief(_library(tmp_path / "build"))
    plan = _plan(brief)
    specs = _specs(tmp_path, plan, brief, monkeypatch, publish=False)
    spec = specs[_stages(plan, "presentation_compose")[0].job_id]
    # the spec names DIRECTORIES, which exist as constructions before the jobs
    # that fill them have run
    assert all(v and not str(v).endswith(".glb")
               for v in spec["dressing_glb"].values())
    problems = PresentationAdapter().validate_configuration(
        spec, {"repository": ""})
    assert any("dressing_glb" in p for p in problems), (
        "an unbaked layer must refuse the job, not quietly drop the flag")
'''),
    (PRES, "presentation: compose with the resolved file", '''\
        dressing = _layer_map(job_spec.get("dressing_glb"))
        fixtures = _layer_map(job_spec.get("fixtures_glb"))
''', '''\
        # Directories in the spec, files here. `validate_configuration` has
        # already refused this job if any of them cannot be resolved, so a
        # blank at this point cannot be reached by a job that is running.
        dressing = {aid: resolve_layer(d, "_dressing.glb")[0]
                    for aid, d in _layer_map(
                        job_spec.get("dressing_glb")).items()}
        fixtures = {aid: resolve_layer(d, "_fixtures.glb")[0]
                    for aid, d in _layer_map(
                        job_spec.get("fixtures_glb")).items()}
'''),
]


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    for path in (CLI, PRES, TEST):
        if not path.is_file():
            print(f"[patch] {path} not found -- run from the factory root")
            return 1
    files: dict[Path, tuple[bytes, bool, str]] = {}
    for path in (CLI, PRES, TEST):
        raw = path.read_bytes()
        crlf = b"\r\n" in raw
        files[path] = (raw, crlf, raw.decode("utf-8").replace("\r\n", "\n"))
        print(f"[patch] {path}: {len(raw)} bytes, "
              f"endings={'CRLF' if crlf else 'LF'}")

    problems = []
    for path, name, before, after in EDITS:
        text = files[path][2]
        if after in text:
            print(f"[patch]   ALREADY APPLIED: {name}")
        elif before not in text:
            print(f"[patch]   ANCHOR NOT FOUND: {name}")
            problems.append(name)
        elif text.count(before) != 1:
            print(f"[patch]   ANCHOR NOT UNIQUE ({text.count(before)}x): {name}")
            problems.append(name)
    if problems:
        print(f"[patch] REFUSING to write: {len(problems)} anchor(s) did not "
              f"match cleanly.")
        return 1

    for path, name, before, after in EDITS:
        raw, crlf, text = files[path]
        if after in text:
            continue
        files[path] = (raw, crlf, text.replace(before, after))
        print(f"[patch]   applied: {name}")

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
