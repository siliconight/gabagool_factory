"""Level Factory 0.199.0: the price reports what the package holds in memory (factory roadmap 238; the memory
measured by part in the factory's `docs/findings/texture_memory/`).

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of
them matched:
  tools/perf_stations.gd        reads the engine's texture, buffer and video memory into `geometry` once
                                every station is warm, before the measured passes
  tools/perf_stations_run.py    `MIB`; prints the three in MiB beside the passes, says so when a report has
                                none, and prints none of a report that has only some
  tests/unit/test_perf_memory.py   NEW (`lf_perf_memory/test_perf_memory.py.txt`)
CHANGELOG and VERSION from `lf_perf_memory/CHANGELOG_0.199.0.md`; `--results-pending` leaves the RESULT_
keys to `--fill`.

Read before it was written, in this session: `perf_stations.gd`'s warm-up (the station loop, `cold_worst`,
`_geometry`), its pass loop and `_write` (the `geometry` it reports, the v1 schema);
`perf_stations_run.py`'s header, its schema and `complete` refusals, the passes block and the light census
after it; `test_perf_stations_run.py`'s stub Godot and `_pkg`; `test_perf_passes.py`, which reads the
probe as source; `texture_split_probe.gd`, whose `RENDER_TEXTURE_MEM_USED` read this one agrees with or
does not. Every file LF.

    python patches/patch_lf_perf_memory.py --results-pending
    (python -m pytest -q in level_factory; exit 0 and the tally, docs/COMMANDS.md trap 1; the measurement)
    python patches/patch_lf_perf_memory.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_perf_memory"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_MEASURED": "result_measured.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.198.0", b"0.199.0"
CHANGELOG_HEAD = "## [0.198.0] - The reflection atlas is sized to the package's probes"
PROBE = "tools/perf_stations.gd"
RUNNER = "tools/perf_stations_run.py"
SHA = {PROBE: "7ca3b804394a065e", RUNNER: "a526c85e11fc3a7e"}
NEW = {"tests/unit/test_perf_memory.py": "test_perf_memory.py.txt"}

EDITS = {
    PROBE: [
        ("\tprint(\"[perf] warmed %d station(s); worst frame while warming %.1f ms\"\n"
         "\t\t% [stations.size(), cold_worst])\n"
         "\t_geometry[\"cold_worst_ms\"] = cold_worst\n",
         "\tprint(\"[perf] warmed %d station(s); worst frame while warming %.1f ms\"\n"
         "\t\t% [stations.size(), cold_worst])\n"
         "\t_geometry[\"cold_worst_ms\"] = cold_worst\n"
         "\t# WHAT THE PACKAGE HOLDS (0.199.0, factory roadmap 238), read once every\n"
         "\t# station is warm: what a station shows is resident by now, and the\n"
         "\t# measured passes below revisit what was warmed. The engine's monitors, in\n"
         "\t# bytes; the runner reports MiB.\n"
         "\t_geometry[\"texture_mem_bytes\"] = int(Performance.get_monitor(\n"
         "\t\tPerformance.RENDER_TEXTURE_MEM_USED))\n"
         "\t_geometry[\"buffer_mem_bytes\"] = int(Performance.get_monitor(\n"
         "\t\tPerformance.RENDER_BUFFER_MEM_USED))\n"
         "\t_geometry[\"video_mem_bytes\"] = int(Performance.get_monitor(\n"
         "\t\tPerformance.RENDER_VIDEO_MEM_USED))\n"),
    ],
    RUNNER: [
        ("EXIT_OK = 0\n",
         "EXIT_OK = 0\n"
         "#: bytes in a MiB, the unit the memory is printed in (0.199.0)\n"
         "MIB = 1024 * 1024\n"
         "#: what the probe reads after the warm-up, together (0.199.0)\n"
         "MEMORY_KEYS = (\"texture_mem_bytes\", \"buffer_mem_bytes\", \"video_mem_bytes\")\n"),
        ("    else:\n"
         "        print(\"  passes: one per heading (a report from before 0.141.0)\")\n"
         "\n"
         "    census = rows[0].get(\"light_census\") or {}\n",
         "    else:\n"
         "        print(\"  passes: one per heading (a report from before 0.141.0)\")\n"
         "\n"
         "    # WHAT THE PACKAGE HOLDS (0.199.0, factory roadmap 238): the engine's\n"
         "    # texture, buffer and video memory, read by the probe once every station\n"
         "    # was warm. The probe writes the three together; a report from before\n"
         "    # carries none and says so, and one with only some prints none of them --\n"
         "    # a missing field is never read as a zero.\n"
         "    mem = doc.get(\"geometry\") or {}\n"
         "    have = [k for k in MEMORY_KEYS if k in mem]\n"
         "    if len(have) == len(MEMORY_KEYS):\n"
         "        print(\"  memory after the warm-up: textures %.1f MiB, buffers %.1f MiB, \"\n"
         "              \"video %.1f MiB\" % tuple(int(mem[k]) / MIB for k in MEMORY_KEYS))\n"
         "    elif have:\n"
         "        print(\"  memory: only %s in this report -- not printed\" % \", \".join(have))\n"
         "    else:\n"
         "        print(\"  memory: none in this report (a probe from before 0.199.0)\")\n"
         "\n"
         "    census = rows[0].get(\"light_census\") or {}\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.199.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.199.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.199.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.199.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, pairs in EDITS.items():
        p = LF / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    news = {rel: (SRC / src).read_bytes().replace(b"\r\n", b"\n") for rel, src in NEW.items()}
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    for rel, data in news.items():
        (LF / rel).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.198.0 -> 0.199.0")


if __name__ == "__main__":
    main()
