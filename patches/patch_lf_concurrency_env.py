"""Level Factory 0.184.0: the scheduler's caps can be overridden for one invocation, so a wider width
is measured before it becomes a default (factory roadmap 239, the art leg).

Anchored edits in `packages/jobs/scheduler.py`, each asserted once, nothing written until all of
them matched: `CONCURRENCY_ENV` and `concurrency_overrides` after `DEFAULT_CONCURRENCY`, and
`Scheduler.__init__` applies `LF_CONCURRENCY` when it was given no caps of its own, saying what it
changed; a new `tests/unit/test_concurrency_override.py` from `lf_concurrency_env/`. CHANGELOG and
VERSION from `lf_concurrency_env/CHANGELOG_0.184.0.md`; `--results-pending` leaves RESULT_SUITE to
`--fill`.

    python patches/patch_lf_concurrency_env.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_concurrency_env.py --fill
    LF_ROOT=<copy> python patches/patch_lf_concurrency_env.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_concurrency_env"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.183.0", b"0.184.0"
CHANGELOG_HEAD = "## [0.183.0] - The editor's import of the lightmap is kept, not done again\n"
SCHED = "packages/jobs/scheduler.py"
TEST = "tests/unit/test_concurrency_override.py"
SHA = {SCHED: "d64b70eb2103abdf"}

D_OLD = ("DEFAULT_CONCURRENCY = {\n"
         "    \"python_cpu\": 4, \"blender\": 1, \"godot_headless\": godot_cap(_os.cpu_count()),\n"
         "    \"godot_interactive\": 1, \"io_heavy\": 2, \"lightweight\": 8,\n"
         "}\n")
D_NEW = (D_OLD +
         "\n"
         "#: An override of the caps for ONE invocation, from the environment (0.184.0):\n"
         "#: `LF_CONCURRENCY=\"blender=3,python_cpu=6\"`. For measuring a wider width before\n"
         "#: it becomes a default -- `godot_headless` is a measurement (`godot_cap`), and\n"
         "#: `blender` 1 is TDD 19.2's, never measured, while cold run 9250's art leg ran\n"
         "#: 102 s of Blender jobs one after another. A run under one says so in its output;\n"
         "#: a class this scheduler does not know, or a width below 1, refuses the run\n"
         "#: rather than being ignored.\n"
         "CONCURRENCY_ENV = \"LF_CONCURRENCY\"\n"
         "\n"
         "\n"
         "def concurrency_overrides(text) -> dict:\n"
         "    \"\"\"``{class: width}`` from `CONCURRENCY_ENV`'s ``class=width[,class=width]``;\n"
         "    empty for none. Raises ValueError on anything else, naming it.\"\"\"\n"
         "    out = {}\n"
         "    for part in (text or \"\").split(\",\"):\n"
         "        part = part.strip()\n"
         "        if not part:\n"
         "            continue\n"
         "        name, eq, value = part.partition(\"=\")\n"
         "        name = name.strip()\n"
         "        if not eq or name not in DEFAULT_CONCURRENCY:\n"
         "            raise ValueError(\"%s: %r is not <class>=<width> for a class of %s\"\n"
         "                             % (CONCURRENCY_ENV, part, sorted(DEFAULT_CONCURRENCY)))\n"
         "        try:\n"
         "            width = int(value.strip())\n"
         "        except ValueError:\n"
         "            raise ValueError(\"%s: %r names no whole width\" % (CONCURRENCY_ENV, part)) from None\n"
         "        if width < 1:\n"
         "            raise ValueError(\"%s: %r would never run that class\" % (CONCURRENCY_ENV, part))\n"
         "        out[name] = width\n"
         "    return out\n")
I_OLD = "        self.concurrency = dict(concurrency or DEFAULT_CONCURRENCY)\n"
I_NEW = ("        self.concurrency = dict(concurrency or DEFAULT_CONCURRENCY)\n"
         "        # caps given to the constructor are the caller's; the environment's\n"
         "        # override is for the command line's scheduler (0.184.0)\n"
         "        overrides = {} if concurrency else concurrency_overrides(\n"
         "            _os.environ.get(CONCURRENCY_ENV))\n"
         "        if overrides:\n"
         "            print(\"[scheduler] %s: %s\" % (CONCURRENCY_ENV, \", \".join(\n"
         "                \"%s %d -> %d\" % (k, self.concurrency.get(k, 1), v)\n"
         "                for k, v in sorted(overrides.items()))))\n"
         "            self.concurrency.update(overrides)\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.184.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.184.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.184.0.md")
    assert entry.startswith("## [0.184.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_concurrency_override.py.txt")
    assert not (LF / TEST).exists(), "already applied"
    sp, s_eol, sched = _read(SCHED)
    assert "CONCURRENCY_ENV" not in sched, "already applied"
    sched = _once(sched, D_OLD, D_NEW, "after DEFAULT_CONCURRENCY")
    sched = _once(sched, I_OLD, I_NEW, "the constructor's caps")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(sp, s_eol, sched)
    (LF / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.183.0 -> 0.184.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
