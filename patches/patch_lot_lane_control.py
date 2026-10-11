"""Lot 0.113.0: a lane stops at a street, and the audit counts it (roadmap 199 and 230 step 3).

Anchored edits in `site_streets.py` (the junction control) and `site_targets.py` (the lane as a
measure and a finding), one test appended to `tests/test_site_targets.py`, a new
`tests/test_site_streets_lane.py`; each file pinned by hash and each anchor asserted once, nothing
written on a miss; the file's own line endings kept. Applies on Lot 0.112.0. CHANGELOG and VERSION
from `lot_lane_control/CHANGELOG_0.113.0.md`; `--suite-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_lot_lane_control.py --suite-pending && cd lot && python -m pytest -q
    python patches/patch_lot_lane_control.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_lane_control"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"Lot 0.112.0", b"Lot 0.113.0"
CHANGELOG_HEAD = "## 0.112.0 - the guide's gameplay targets in the site audit\n"
SHA = {"site_streets.py": "0330182e226c5e74", "site_targets.py": "aac675b3e6bddf27",
       "tests/test_site_targets.py": "3d167a53615160aa"}
NEW = {"tests/test_site_streets_lane.py": "test_site_streets_lane.py"}

S_OLD = (
    "            signalised = ((minor and is_arterial(other))\n"
    "                          or (other_minor and is_arterial(road)))\n")
S_NEW = (
    "            # A LANE STOPS (0.113.0): a road without a sidewalk is a service\n"
    "            # lane or an alley, and its junction with a street is\n"
    "            # stop-controlled, never signalised -- a signal is for a street\n"
    "            # meeting an arterial. Level Factory 0.177.0's `block` grammar\n"
    "            # ends its lane on two side streets, and the rule as it stood\n"
    "            # would have hung a signal at the alley's mouth.\n"
    "            signalised = ((minor and is_arterial(other) and bool(road.sidewalk))\n"
    "                          or (other_minor and is_arterial(road) and bool(other.sidewalk)))\n")
T_DOC_OLD = (
    "  never \"huge parking lots behind every use\").\n"
    "\n"
    "NOT MEASURED HERE")
T_DOC_NEW = (
    "  never \"huge parking lots behind every use\");\n"
    "- the service lane (0.113.0): the roads carrying `kind: service_lane` (Level Factory 0.177.0's\n"
    "  `block` grammar lays one behind the row between two side streets) and the buildings they\n"
    "  `serve`, the guide's connector with an owner and users; the loop it closes is counted above.\n"
    "\n"
    "NOT MEASURED HERE")
T_MEAS_OLD = (
    "    roads = site.get(\"roads\", [])\n"
    "    junctions, loops = road_graph(roads)\n")
T_MEAS_NEW = (
    "    roads = site.get(\"roads\", [])\n"
    "    junctions, loops = road_graph(roads)\n"
    "    lanes = [r for r in roads if str(r.get(\"kind\", \"\")) == \"service_lane\"]\n")
T_KEYS_OLD = (
    "        \"yards\": len(site.get(\"yards\") or []),\n"
    "    }\n")
T_KEYS_NEW = (
    "        \"yards\": len(site.get(\"yards\") or []),\n"
    "        \"service_lanes\": len(lanes),\n"
    "        \"lane_serves\": sum(len(r.get(\"serves\") or []) for r in lanes),\n"
    "    }\n")
T_FIND_OLD = (
    "                             f\"driveway(s) and {m['yards']} yard(s) with a dumpster for {n} building(s)\"))\n"
    "    return out\n")
T_FIND_NEW = (
    "                             f\"driveway(s) and {m['yards']} yard(s) with a dumpster for {n} building(s)\"))\n"
    "    if m[\"service_lanes\"]:\n"
    "        out.append((\"INFO\", CODE, f\"{m['service_lanes']} service lane(s) behind the row serving \"\n"
    "                                 f\"{m['lane_serves']} building(s): the guide's connector with an owner \"\n"
    "                                 f\"and users\"))\n"
    "    else:\n"
    "        out.append((\"INFO\", CODE, \"no service lane: deliveries and refuse share the front street; the \"\n"
    "                                 \"guide's rear passage or service lane is the loop a strip lacks\"))\n"
    "    return out\n")
TEST_ADDED = (
    "\n\ndef test_a_service_lane_is_counted_as_the_connector_it_is():\n"
    "    lane = {\"a\": [-30.0, 25.0], \"b\": [60.0, 25.0], \"width\": 5.0, \"sidewalk\": 0.0,\n"
    "            \"kind\": \"service_lane\", \"serves\": [\"b0\", \"b1\", \"b2\"]}\n"
    "    side1 = {\"a\": [-30.0, -23.0], \"b\": [-30.0, 50.0], \"width\": 10.0, \"sidewalk\": 3.0}\n"
    "    side2 = {\"a\": [60.0, -23.0], \"b\": [60.0, 50.0], \"width\": 10.0, \"sidewalk\": 3.0}\n"
    "    s = _site(roads=[MAIN, side1, side2, lane])\n"
    "    m = ST.measures(s)\n"
    "    assert m[\"service_lanes\"] == 1 and m[\"lane_serves\"] == 3 and m[\"loops\"] == 1\n"
    "    text = \" | \".join(f[2] for f in ST.findings(s))\n"
    "    assert \"1 service lane(s) behind the row serving 3 building(s)\" in text and \"1 loop(s)\" in text\n"
    "    bare = \" | \".join(f[2] for f in ST.findings(_site()))\n"
    "    assert \"no service lane: deliveries and refuse share the front street\" in bare\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LOT / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = LOT / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Lot 0.113.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.113.0.md").decode("utf-8")
    assert entry.startswith("## 0.113.0 - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"

    sp, s_eol, streets = _read("site_streets.py")
    assert "A LANE STOPS" not in streets, "already applied"
    streets = _once(streets, S_OLD, S_NEW, "the junction control")

    tp, t_eol, targets = _read("site_targets.py")
    targets = _once(targets, T_DOC_OLD, T_DOC_NEW, "the docstring")
    targets = _once(targets, T_MEAS_OLD, T_MEAS_NEW, "the measure")
    targets = _once(targets, T_KEYS_OLD, T_KEYS_NEW, "the keys")
    targets = _once(targets, T_FIND_OLD, T_FIND_NEW, "the finding")

    xp, x_eol, tests = _read("tests/test_site_targets.py")
    assert tests.endswith("\n")
    tests = tests.rstrip("\n") + "\n" + TEST_ADDED
    for rel in NEW:
        assert not (LOT / rel).exists(), (rel, "already exists")

    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # Every pin and anchor matched: now write.
    sp.write_bytes(streets.replace("\n", s_eol.decode()).encode("utf-8"))
    tp.write_bytes(targets.replace("\n", t_eol.decode()).encode("utf-8"))
    xp.write_bytes(tests.replace("\n", x_eol.decode()).encode("utf-8"))
    for rel, name in NEW.items():
        (LOT / rel).write_bytes(_src(name))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.112.0 -> 0.113.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
