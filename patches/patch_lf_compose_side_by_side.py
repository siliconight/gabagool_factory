"""Level Factory 0.186.0: a job's independent commands run side by side, and every command's output
reaches `job.log` (factory roadmap 239, the art leg).

Anchored edits, each asserted once, nothing written until all of them matched:
  packages/adapters/sdk.py           `PlannedCommand.parallel` (False by default; in `as_dict` only
                                     when set, so no existing record changes)
  packages/jobs/scheduler.py         `_run_commands`: each command's result in plan order, a run of
                                     consecutive parallel commands side by side up to the job's class
                                     width, every command's log joined into `job.log` in plan order
                                     (each command used to rewrite it); `_attempt_job` reads it
  adapters/presentation/__init__.py  the per-building composes are parallel; the mission shell's,
                                     whose output folder holds theirs and is cleared first, is not
  tests/unit/test_commands_side_by_side.py   NEW, from `lf_compose_side_by_side/`
CHANGELOG and VERSION from `lf_compose_side_by_side/CHANGELOG_0.186.0.md`; `--results-pending` leaves
the RESULT_ keys to `--fill`.

    python patches/patch_lf_compose_side_by_side.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_compose_side_by_side.py --fill
    LF_ROOT=<copy> python patches/patch_lf_compose_side_by_side.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_compose_side_by_side"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.185.0", b"0.186.0"
CHANGELOG_HEAD = ("## [0.185.0] - Blender jobs run three at a time where the machine allows, the "
                  "width cold run 9251 measured\n")
SDK = "packages/adapters/sdk.py"
SCHED = "packages/jobs/scheduler.py"
PRES = "adapters/presentation/__init__.py"
TEST = "tests/unit/test_commands_side_by_side.py"
SHA = {SDK: "b86b92d8ffae39c9", SCHED: "d7c880620810c113", PRES: "6438ccd3976bdf11"}

K_FIELD_OLD = ("    timeout_seconds: int | None = None\n"
               "\n"
               "    def argv(self) -> list[str]:\n")
K_FIELD_NEW = ("    timeout_seconds: int | None = None\n"
               "    #: May run side by side with the commands next to it that are also\n"
               "    #: parallel (0.186.0): nothing it reads is written by them, nothing it\n"
               "    #: writes is read or cleared by them. A run of consecutive parallel\n"
               "    #: commands goes at once, up to the job's class width; the rest in turn.\n"
               "    parallel: bool = False\n"
               "\n"
               "    def argv(self) -> list[str]:\n")
K_DICT_OLD = ("    def as_dict(self) -> dict:\n"
              "        return {\n"
              "            \"executable\": str(self.executable),\n"
              "            \"arguments\": list(self.arguments),\n"
              "            \"working_directory\": str(self.working_directory),\n"
              "            \"environment\": dict(self.environment),\n"
              "            \"expected_outputs\": list(self.expected_outputs),\n"
              "            \"resource_class\": self.resource_class,\n"
              "            \"timeout_seconds\": self.timeout_seconds,\n"
              "        }\n")
K_DICT_NEW = ("    def as_dict(self) -> dict:\n"
              "        out = {\n"
              "            \"executable\": str(self.executable),\n"
              "            \"arguments\": list(self.arguments),\n"
              "            \"working_directory\": str(self.working_directory),\n"
              "            \"environment\": dict(self.environment),\n"
              "            \"expected_outputs\": list(self.expected_outputs),\n"
              "            \"resource_class\": self.resource_class,\n"
              "            \"timeout_seconds\": self.timeout_seconds,\n"
              "        }\n"
              "        if self.parallel:\n"
              "            out[\"parallel\"] = True\n"
              "        return out\n")

S_LOOP_OLD = ("        result = None\n"
              "        for cmd in planned:\n"
              "            log_path = self.jobs_dir / job.job_id / str(job.attempt) / \"job.log\"\n"
              "            result = run_command(\n"
              "                cmd.argv(),\n"
              "                cwd=cmd.working_directory,\n"
              "                env={**cmd.environment, \"DELI_OUT\": str(work_dir),\n"
              "                     \"LF_OUT\": str(work_dir)},\n"
              "                log_path=log_path,\n"
              "                timeout_s=cmd.timeout_seconds,\n"
              "                cancel=cancel,\n"
              "            )\n"
              "            job.log_path = str(log_path)\n")
S_LOOP_NEW = ("        result = None\n"
              "        log_path = self.jobs_dir / job.job_id / str(job.attempt) / \"job.log\"\n"
              "        for result in self._run_commands(\n"
              "                planned, work_dir, log_path, cancel,\n"
              "                width=self.concurrency.get(job.resource_class, 1)):\n"
              "            job.log_path = str(log_path)\n")
S_METHOD_OLD = ("    # ------------------------------------------------------------------\n"
                "    def _advise(self, adapter, job_spec: dict, context: dict, job: Job) -> list:\n")
S_METHOD_NEW = (
    "    # ------------------------------------------------------------------\n"
    "    def _run_commands(self, planned, work_dir: Path, log_path: Path,\n"
    "                      cancel, *, width: int = 1):\n"
    "        \"\"\"Each planned command's RunResult, in plan order (0.186.0).\n"
    "\n"
    "        A run of consecutive `PlannedCommand.parallel` commands goes side by\n"
    "        side, up to ``width`` (the job's class cap); every other command goes\n"
    "        alone, in turn. Results come back in plan order either way, and a\n"
    "        caller that stops at a failure never starts the commands after it.\n"
    "\n"
    "        `job.log` HOLDS EVERY COMMAND. Each command used to rewrite it, so a\n"
    "        job of sixteen composes kept the last building's output and its 1.6 s\n"
    "        -- read in 2026-10 as the whole job's command time. A job of one\n"
    "        command writes it as before; a job of several writes each to its own\n"
    "        part and joins the parts into `job.log` in plan order.\"\"\"\n"
    "        from concurrent.futures import ThreadPoolExecutor\n"
    "\n"
    "        def env_of(cmd):\n"
    "            return {**cmd.environment, \"DELI_OUT\": str(work_dir),\n"
    "                    \"LF_OUT\": str(work_dir)}\n"
    "\n"
    "        def run(n, cmd):\n"
    "            part = log_path if len(planned) == 1 else log_path.with_name(\"job.%d.log\" % n)\n"
    "            return run_command(cmd.argv(), cwd=cmd.working_directory, env=env_of(cmd),\n"
    "                               log_path=part, timeout_s=cmd.timeout_seconds,\n"
    "                               cancel=cancel)\n"
    "\n"
    "        def joined(n, res):\n"
    "            if len(planned) == 1:\n"
    "                return res\n"
    "            part = log_path.with_name(\"job.%d.log\" % n)\n"
    "            text = part.read_bytes() if part.is_file() else b\"\"\n"
    "            with open(log_path, \"wb\" if n == 0 else \"ab\") as log:\n"
    "                log.write(text)\n"
    "            part.unlink(missing_ok=True)\n"
    "            res.log_path = log_path\n"
    "            return res\n"
    "\n"
    "        i = 0\n"
    "        while i < len(planned):\n"
    "            j = i + 1\n"
    "            if getattr(planned[i], \"parallel\", False):\n"
    "                while j < len(planned) and getattr(planned[j], \"parallel\", False):\n"
    "                    j += 1\n"
    "            batch = list(range(i, j))\n"
    "            if len(batch) == 1 or width <= 1:\n"
    "                for n in batch:\n"
    "                    yield joined(n, run(n, planned[n]))\n"
    "            else:\n"
    "                with ThreadPoolExecutor(max_workers=min(width, len(batch))) as ex:\n"
    "                    futures = [ex.submit(run, n, planned[n]) for n in batch]\n"
    "                    results = [f.result() for f in futures]\n"
    "                for n, res in zip(batch, results):\n"
    "                    yield joined(n, res)\n"
    "            i = j\n"
    "\n"
    "    # ------------------------------------------------------------------\n"
    "    def _advise(self, adapter, job_spec: dict, context: dict, job: Job) -> list:\n")

P_DEF_OLD = ("        def compose(*, slots, gameplay, greybox, out, bid, scene_rel,\n"
             "                    dressing, fixtures, roofprops, modules):\n")
P_DEF_NEW = ("        def compose(*, slots, gameplay, greybox, out, bid, scene_rel,\n"
             "                    dressing, fixtures, roofprops, modules, parallel=False):\n")
P_CMD_OLD = ("                resource_class=\"python_cpu\", timeout_seconds=600,\n"
             "            )\n")
P_CMD_NEW = ("                resource_class=\"python_cpu\", timeout_seconds=600,\n"
             "                parallel=parallel,\n"
             "            )\n")
P_LOOP_OLD = ("                modules=modules.get(str(a[\"id\"])),\n"
              "            ))\n")
P_LOOP_NEW = ("                modules=modules.get(str(a[\"id\"])),\n"
              "                # SIDE BY SIDE (0.186.0): each building clears and writes only\n"
              "                # its own folder under the lot's. The mission shell's compose\n"
              "                # above is not parallel: Deli Counter's `build_package` clears\n"
              "                # its output folder first, and that folder holds these.\n"
              "                parallel=True,\n"
              "            ))\n")


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.186.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.186.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.186.0.md")
    assert entry.startswith("## [0.186.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_commands_side_by_side.py.txt")
    assert not (LF / TEST).exists(), "already applied"
    kp, k_eol, sdk = _read(SDK)
    assert "parallel: bool" not in sdk, "already applied"
    sdk = _once(sdk, K_FIELD_OLD, K_FIELD_NEW, "PlannedCommand's fields")
    sdk = _once(sdk, K_DICT_OLD, K_DICT_NEW, "PlannedCommand.as_dict")
    sp, s_eol, sched = _read(SCHED)
    sched = _once(sched, S_LOOP_OLD, S_LOOP_NEW, "the command loop")
    sched = _once(sched, S_METHOD_OLD, S_METHOD_NEW, "before _advise")
    pp, p_eol, pres = _read(PRES)
    pres = _once(pres, P_DEF_OLD, P_DEF_NEW, "compose()'s signature")
    pres = _once(pres, P_CMD_OLD, P_CMD_NEW, "compose()'s command")
    pres = _once(pres, P_LOOP_OLD, P_LOOP_NEW, "the per-building composes")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(kp, k_eol, sdk)
    _write(sp, s_eol, sched)
    _write(pp, p_eol, pres)
    (LF / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.185.0 -> 0.186.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
