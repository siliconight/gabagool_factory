"""Level Factory 0.243.0 on a clone: a brief whose archetype names no Deli Counter preset may anchor an AUTHORED library
family -- `<archetype>_aNN.json` in Deli Counter's specs/ -- whose variant the seed picks (the factory's roadmap 309,
its bridge). Anchored; refuses on a miss.

    python edit_lf_authored_anchor.py <clone>

Edits adapters/deli_counter/__init__.py; writes tests/unit/test_authored_anchor.py. VERSION and CHANGELOG are the
generator's.
"""
import pathlib
import sys

C = pathlib.Path(sys.argv[1])
p = C / "adapters" / "deli_counter" / "__init__.py"
raw = p.read_bytes()
crlf = b"\r\n" in raw
t = raw.decode("utf-8").replace("\r\n", "\n")
assert "authored_family" not in t

EDITS = [
    ('''def _preset_or_raw(job_spec) -> str:
''', '''#: An authored family's variants in Deli Counter's specs/: `<family>_a01.json`, `_a02`, ...
_AUTHORED_VARIANT = re.compile(r"^(?P<family>[a-z0-9_]+)_a(?P<n>\\d+)\\.json$")


def authored_family(repository, archetype: str, seed) -> Path | None:
    """The authored spec a brief anchors when its archetype names no preset, or None.

    THE BRIDGE OF THE FACTORY'S ROADMAP 309. A brief's anchor is generated
    from a preset (`_preset_for`), and 60 of the library's 97 families -- 25
    of them real building types: courthouses, funeral homes, museums,
    landmark halls, arenas, casinos, clinics, walk-ups -- have none, so no
    brief could anchor one. Cold run 9394's `funeral_home` brief was refused
    at the shell leg. An archetype that IS an authored family's name -- the
    family exactly, no alias, no keyword -- anchors one of its variants,
    sorted by number and picked by the seed, so a mission replays the same
    and five candidates spread over the family. Nothing is generated: the
    variant is the library's own spec, built as the library builds it. A
    preset for the family, when there is one, wins in `plan_commands`.

    Exact names only, for `_preset_for`'s reason: a guessed building is
    worse than a refusal, and `corner_store` stays refused because no family
    is called that."""
    a = (archetype or "").strip().lower()
    specs = Path(str(repository)) / "specs"
    if not a or a.startswith("lf_") or not specs.is_dir():
        return None
    found = []
    for f in specs.iterdir():
        m = _AUTHORED_VARIANT.match(f.name)
        if m and m.group("family") == a:
            found.append((int(m.group("n")), f))
    if not found:
        return None
    found.sort()
    return found[int(seed or 0) % len(found)][1]


def _preset_or_raw(job_spec) -> str:
'''),
    ('''        preset = _preset_for(str(job_spec.get("archetype", "")))
        mode = str(job_spec.get("mode", "heist"))
        level = self._level_name(job_spec)
        spec_path = repo / "specs" / f"{level}.json"
        out_glb = work / "shell.glb"
''', '''        mode = str(job_spec.get("mode", "heist"))
        level = self._level_name(job_spec)
        spec_path = repo / "specs" / f"{level}.json"
        out_glb = work / "shell.glb"
        try:
            preset = _preset_for(str(job_spec.get("archetype", "")))
        except UnknownArchetype:
            # an authored family by its exact name (roadmap 309), else the
            # refusal stands
            authored = authored_family(repo, str(job_spec.get("archetype", "")), job_spec.get("seed"))
            if authored is None:
                raise
            return self._plan_authored(authored, spec_path, out_glb, repo, py, blender)
'''),
    ('''    def collect_outputs(self, job_spec, context) -> Iterable[Path]:
''', '''    def _plan_authored(self, authored, spec_path, out_glb, repo, py, blender) -> Sequence[PlannedCommand]:
        """An authored variant's job: the spec copied byte for byte to the
        job's level name, then built exactly as a generated one is. No mode,
        floors, seed or holes is passed -- the variant is what its author and
        the library's passes made it, furnished and seeded already."""
        copy = ("import shutil, sys; shutil.copyfile(sys.argv[1], sys.argv[2]); "
                "print('authored anchor', sys.argv[1])")
        build_args = [str(repo / "build.py"), str(spec_path),
                      "--out", str(out_glb), "--blender", blender]
        return [
            PlannedCommand(
                executable=Path(str(py)), arguments=("-c", copy, str(authored), str(spec_path)),
                working_directory=repo,
                expected_outputs=("shell.glb", "shell.gameplay.json",
                                  "shell.slots.json", "shell.lights.json"),
                resource_class="python_cpu", timeout_seconds=300,
            ),
            PlannedCommand(
                executable=Path(str(py)), arguments=tuple(build_args),
                working_directory=repo,
                expected_outputs=(),
                resource_class="blender", timeout_seconds=900,
            ),
        ]

    def collect_outputs(self, job_spec, context) -> Iterable[Path]:
'''),
]
for old, new in EDITS:
    assert t.count(old) == 1, (t.count(old), old[:80])
    t = t.replace(old, new)
if "\nimport re\n" not in t:
    anchor = "from pathlib import Path\n"
    assert t.count(anchor) == 1, "no pathlib import to anchor on"
    t = t.replace(anchor, "import re\n" + anchor)
p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
print("edited", p.name)

test = C / "tests" / "unit" / "test_authored_anchor.py"
assert not test.exists()
test.write_bytes('''"""A brief may anchor an authored library family that no preset generates (0.243.0, the factory's roadmap 309).

Cold run 9394's `funeral_row_001` (archetype `funeral_home`) was refused at the shell leg: a brief's anchor was
generated from a Deli Counter preset, and 60 of the library's 97 families had none. FAILS ON 0.242.0.
"""
from pathlib import Path

import pytest

from adapters.deli_counter import DeliCounterAdapter, UnknownArchetype, authored_family


def _repo(tmp_path, names):
    (tmp_path / "specs").mkdir()
    for n in names:
        (tmp_path / "specs" / n).write_text("{}", encoding="utf-8")
    return tmp_path


def _ctx(repo):
    return {"repository": str(repo), "work_dir": str(repo / "w"), "python_executable": "python",
            "blender_executable": "blender"}


def test_the_seed_picks_a_variant_of_the_family_by_its_exact_name(tmp_path):
    repo = _repo(tmp_path, ["funeral_home_a01.json", "funeral_home_a02.json", "funeral_home_a03.json",
                            "lf_funeral_home_9003.json", "funeral_home_annex_a01.json"])
    picks = [authored_family(repo, "funeral_home", s).name for s in (0, 1, 2, 3)]
    assert picks == ["funeral_home_a01.json", "funeral_home_a02.json", "funeral_home_a03.json",
                     "funeral_home_a01.json"]
    assert authored_family(repo, "funeral", 0) is None          # no keyword guess
    assert authored_family(repo, "corner_store", 0) is None


def test_a_civic_brief_copies_its_variant_and_builds_it(tmp_path):
    repo = _repo(tmp_path, ["funeral_home_a01.json", "funeral_home_a02.json"])
    cmds = DeliCounterAdapter().plan_commands(
        {"archetype": "funeral_home", "seed": 9003, "level_name": "lf_m"}, _ctx(repo))
    copy, build = list(cmds[0].arguments), list(cmds[1].arguments)
    assert copy[0] == "-c" and Path(copy[2]).name == "funeral_home_a02.json"       # 9003 % 2
    assert Path(copy[3]).name == "lf_m_9003.json"
    assert Path(build[0]).name == "build.py" and Path(build[1]).name == "lf_m_9003.json"
    assert "new_level.py" not in " ".join(copy + build)


def test_a_preset_still_wins_and_a_stranger_is_still_refused(tmp_path):
    repo = _repo(tmp_path, ["bank_a01.json"])
    ad = DeliCounterAdapter()
    args = list(ad.plan_commands({"archetype": "bank", "seed": 1, "level_name": "lf_m"}, _ctx(repo))[0].arguments)
    assert Path(args[0]).name == "new_level.py" and args[args.index("--preset") + 1] == "bank"
    with pytest.raises(UnknownArchetype):
        ad.plan_commands({"archetype": "nightclub", "seed": 1, "level_name": "lf_m"}, _ctx(repo))
'''.encode("utf-8"))
print("wrote", test.name)
