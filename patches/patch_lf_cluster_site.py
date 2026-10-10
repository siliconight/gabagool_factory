"""Level Factory 0.176.1: the site spec's draw takes the cluster template too (cold run 9231, roadmap 230).

Anchored edits in `packages/pipeline/building_library.py` (`preferred_for_brief`, asked by
`lot_for_brief`), `apps/cli/commands/__init__.py` (the site spec builder's `pick_lot` call),
`tests/unit/test_cluster.py` (two tests appended) and `tests/unit/test_site_audit_report.py` (Lot
0.112.0's `S_TARGETS` lines beside the four codes it pins); each file pinned by hash and each anchor
asserted once, nothing written on a miss; the file's own line endings kept. CHANGELOG and VERSION
from `lf_cluster_site/CHANGELOG_0.176.1.md`; `--suite-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_lf_cluster_site.py --suite-pending && cd level_factory && python -m pytest -q > out.txt 2>&1; echo exit=$?
    python patches/patch_lf_cluster_site.py --fill
    LF_ROOT=<copy> python patches/patch_lf_cluster_site.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_cluster_site"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"0.176.0", b"0.176.1"
CHANGELOG_HEAD = ("## [0.176.0] - The buildings beside the objective are drawn by a cluster template, "
                  "when the brief asks\n")
SHA = {"packages/pipeline/building_library.py": "e32cedb701a9f59b",
       "apps/cli/commands/__init__.py": "0d384d3b80ea19a4",
       "tests/unit/test_cluster.py": "f737a3d47ff0025c",
       "tests/unit/test_site_audit_report.py": "e4a78a61023a063f"}

# Lot 0.112.0 adds its `S_TARGETS` lines (the guide's gameplay targets, every one INFO) to every
# audit, and this test pinned the exact list of 9209's four codes: it pins them BESIDE the targets
# now, and proves every target line Lot keeps reaches the report as info.
REPORT_OLD = (
    '    kept = sorted((f["severity"], f["code"]) for f in block["findings"])\n'
    '    assert kept == [("INFO", "S_GETAWAY_AT_SPAWN"), ("INFO", "S_STREET_CROSS"),\n'
    '                    ("INFO", "S_STREET_CROSS"), ("MED", "S_RESPONDER_ARC")], kept\n'
    '    got = _issues(tmp_path, {"site_audit": block})\n'
    '    assert sorted((i["severity"], i["code"]) for i in got) == [\n'
    '        ("info", "S_GETAWAY_AT_SPAWN"), ("info", "S_STREET_CROSS"),\n'
    '        ("info", "S_STREET_CROSS"), ("moderate", "S_RESPONDER_ARC")], got\n'
    '    assert not any(i["blocking"] for i in got)\n'
)
REPORT_NEW = (
    '    # Lot 0.112.0 says the guide\'s gameplay targets on every audit (`S_TARGETS`,\n'
    '    # every line INFO): 9209\'s four codes stand beside them, and every target\n'
    '    # line Lot keeps reaches the report as info, never blocking\n'
    '    kept = sorted((f["severity"], f["code"]) for f in block["findings"]\n'
    '                  if f["code"] != "S_TARGETS")\n'
    '    assert kept == [("INFO", "S_GETAWAY_AT_SPAWN"), ("INFO", "S_STREET_CROSS"),\n'
    '                    ("INFO", "S_STREET_CROSS"), ("MED", "S_RESPONDER_ARC")], kept\n'
    '    got = _issues(tmp_path, {"site_audit": block})\n'
    '    assert sorted((i["severity"], i["code"]) for i in got if i["code"] != "S_TARGETS") == [\n'
    '        ("info", "S_GETAWAY_AT_SPAWN"), ("info", "S_STREET_CROSS"),\n'
    '        ("info", "S_STREET_CROSS"), ("moderate", "S_RESPONDER_ARC")], got\n'
    '    n_targets = sum(1 for f in block["findings"] if f["code"] == "S_TARGETS")\n'
    '    targets = [i for i in got if i["code"] == "S_TARGETS"]\n'
    '    assert len(targets) == n_targets and all(i["severity"] == "info" for i in targets), got\n'
    '    assert not any(i["blocking"] for i in got)\n'
)

LIB_OLD = (
    "def lot_for_brief(model, candidate_id, *, themed: bool = False):\n"
)
LIB_NEW = (
    "def preferred_for_brief(model):\n"
    "    \"\"\"The cluster template's families for a brief, or None (0.176.1): the one\n"
    "    place the template is read off a brief, so the site spec's own draw and\n"
    "    `lot_for_brief` cannot disagree about it. Cold run 9231: the planner and\n"
    "    the compose spec drew the template's lot and the site spec drew the old\n"
    "    one, the art leg dressed a pharmacy the site never placed, and the\n"
    "    export's closure gate stopped the run on the station's unresolved glb.\"\"\"\n"
    "    from packages.pipeline import cluster\n"
    "    template = cluster.template_for(getattr(model, \"cluster\", \"\"),\n"
    "                                    getattr(model, \"archetype\", \"\") or \"\")\n"
    "    return cluster.preferred_families(template) if template else None\n"
    "\n"
    "\n"
    "def lot_for_brief(model, candidate_id, *, themed: bool = False):\n"
)
LIB_BODY_OLD = (
    "    # the cluster template's families, when the brief names one (0.176.0)\n"
    "    from packages.pipeline import cluster\n"
    "    template = cluster.template_for(getattr(model, \"cluster\", \"\"),\n"
    "                                    getattr(model, \"archetype\", \"\") or \"\")\n"
    "    return lot_for(getattr(model, \"lot_library\", None),\n"
    "                   getattr(model, \"building_count\", 1),\n"
    "                   candidate_id, themed=themed,\n"
    "                   anchor=getattr(model, \"archetype\", \"\") or \"\",\n"
    "                   preferred=cluster.preferred_families(template) if template else None)\n"
)
LIB_BODY_NEW = (
    "    # the cluster template's families, when the brief names one (0.176.0),\n"
    "    # read by the one function the site spec builder also asks (0.176.1)\n"
    "    return lot_for(getattr(model, \"lot_library\", None),\n"
    "                   getattr(model, \"building_count\", 1),\n"
    "                   candidate_id, themed=themed,\n"
    "                   anchor=getattr(model, \"archetype\", \"\") or \"\",\n"
    "                   preferred=preferred_for_brief(model))\n"
)
CMD_OLD = (
    "        # Anchored on the brief's archetype, the same draw `lot_for_brief`\n"
    "        # makes for the planner and the compose spec (roadmap 149).\n"
    "        lot = building_library.pick_lot(\n"
    "            complete, seed, count,\n"
    "            anchor=getattr(model, \"archetype\", \"\") or \"\")\n"
)
CMD_NEW = (
    "        # Anchored on the brief's archetype AND drawn by its cluster template,\n"
    "        # the same draw `lot_for_brief` makes for the planner and the compose\n"
    "        # spec (roadmap 149; 0.176.1). 0.176.0 threaded the template through\n"
    "        # `lot_for_brief` and missed this fourth draw, the one `grep lot_for`\n"
    "        # does not name: cold run 9231 planned and dressed the template's\n"
    "        # pharmacy while this spec placed the station the old draw gave, and\n"
    "        # the export's closure gate stopped the run on the station's\n"
    "        # unresolved glb. The template is read by the one function\n"
    "        # `lot_for_brief` reads it by, so the four draws cannot disagree.\n"
    "        lot = building_library.pick_lot(\n"
    "            complete, seed, count,\n"
    "            anchor=getattr(model, \"archetype\", \"\") or \"\",\n"
    "            preferred=building_library.preferred_for_brief(model))\n"
)
TEST_TAIL_MARK = "def test_the_anchor_still_stands_first_and_is_not_drawn_twice():\n"


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = LF / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Level Factory 0.176.1's changelog filled")


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.176.1.md")
    assert entry.startswith("## [0.176.1] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"

    lp, l_eol, lib = _read("packages/pipeline/building_library.py")
    assert "preferred_for_brief" not in lib, "already applied"
    lib = _once(lib, LIB_OLD, LIB_NEW, "lot_for_brief's head")
    lib = _once(lib, LIB_BODY_OLD, LIB_BODY_NEW, "lot_for_brief's body")

    cp, c_eol, cmd = _read("apps/cli/commands/__init__.py")
    cmd = _once(cmd, CMD_OLD, CMD_NEW, "the site spec's draw")
    assert cmd.count("pick_lot(") == 1

    tp, t_eol, tests = _read("tests/unit/test_cluster.py")
    assert tests.count(TEST_TAIL_MARK) == 1 and tests.endswith("\n")
    tests = tests.rstrip("\n") + "\n" + _src("test_cluster_site.py.txt")

    rp, r_eol, report = _read("tests/unit/test_site_audit_report.py")
    report = _once(report, REPORT_OLD, REPORT_NEW, "the report test's pinned list")

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # Every pin and anchor matched: now write.
    lp.write_bytes(lib.replace("\n", l_eol.decode()).encode("utf-8"))
    cp.write_bytes(cmd.replace("\n", c_eol.decode()).encode("utf-8"))
    tp.write_bytes(tests.replace("\n", t_eol.decode()).encode("utf-8"))
    rp.write_bytes(report.replace("\n", r_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.176.0 -> 0.176.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
