"""Level Factory 0.202.0: what a pick counts -- the grade breaks a tie, and two kinds of major are shown and not
counted (the walker, 2026-10-13: "ties should go to the higher grade"; then the call on which finding types stop
counting as majors for picking, left to the factory "for the moment").

The census that decided it: `docs/findings/pick_majors/major_census.py` (62 cold workspace missions, 186
candidates). LOT_DESTINATION_ABOVE_FLOOR on 96 candidates, the walk test walking every leg on 95, chose 28 of the
62 picks (12 to a lower completion or score than the new rule picks, 16 equal, none higher); Laser Tag's five
verdicts on the fight, taken together, chose none.

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  packages/pipeline/pick.py        the docstring's rule, THE GRADE and WHAT A PICK COUNTS; ADVISORY and
                                   ANSWERED_BY_WALK; Candidate's score, grade, walked, not_counted and its line;
                                   walked_every_leg; candidates() counting by them and reading the score through
                                   lasertag_report.report_score; pick() keyed on the score before the seed
  apps/cli/commands/__init__.py    `pick --json` carries not_counted, score and grade
  tests/unit/test_pick_counts.py   NEW (`lf_pick_counts/test_pick_counts.py.txt`)
CHANGELOG and VERSION from `lf_pick_counts/CHANGELOG_0.202.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`.

Read before it was written, in this session: `pick.py` whole (0.169.0, 5,426 bytes, LF); `cmd_pick` and
`cmd_make`'s pick leg in `apps/cli/commands/__init__.py` (210,874 bytes, LF); `lasertag_report.report_score`,
`_SEVERITY`, `normalize_report`; `tests/unit/test_make_and_pick.py`, whose fixtures write a walk test of `ok`
alone and a report with no score; one real walk test (cold run 9285, seed_9104) and Lot's director
(`nav_qa_director.gd`: `_conclude`, `_set_leg`'s credited vertical leg) and `_navqa_anchors` (the objective is a
crew proxy at its room's floor). Every file LF.

    python patches/patch_lf_pick_counts.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_pick_counts.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_pick_counts"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.201.0", b"0.202.0"
CHANGELOG_HEAD = ("## [0.201.0] - The urban street's near side: the mission's buildings stand among "
                  "mid-rises")
SHA = {"packages/pipeline/pick.py": "58c5b5e7e126a7ac",
       "apps/cli/commands/__init__.py": "5825a200071751eb"}
NEW = {"tests/unit/test_pick_counts.py": "test_pick_counts.py.txt"}

DOC_RULE_OLD = ("* **Among the rest:** the fewest major findings wins, then the highest route completion Laser\n"
                "  Tag measured, then the lowest seed.\n")
DOC_RULE_NEW = ("* **Among the rest:** the fewest major findings wins, then the highest route completion Laser\n"
                "  Tag measured, then the higher Laser Tag score, then the lowest seed. Two kinds of major\n"
                "  are shown and not counted (WHAT A PICK COUNTS, below).\n")

DOC_TAIL_OLD = ("(`summary.route_completion_rate`); a candidate without one sorts last and says so.\n"
                "\n"
                "Everything is read from the workspace, from the files the shell leg wrote; nothing is run.\n")
DOC_TAIL_NEW = (
    "(`summary.route_completion_rate`); a candidate without one sorts last and says so.\n"
    "\n"
    "THE GRADE (0.202.0; the walker, 2026-10-13: \"ties should go to the higher grade\"). Cold run 9283\n"
    "picked card_block_001's seed_9061 at PASS_WITH_TUNING 77 over seed_9263 at 89, one major each and\n"
    "route completion 1.00 each, on the lower seed. The report's score (`lasertag_report.report_score`)\n"
    "now breaks that tie before the seed; Laser Tag's grade is a pure function of it, so the higher score\n"
    "is the higher grade. A report without one sorts last among its ties. The factory's copy of this\n"
    "rule, `tools/cold_drive/pick_candidate.py`, learned it first and this file did not, so for a day the\n"
    "cold runs and `level-factory pick` picked by two rules; that copy now reads this one.\n"
    "\n"
    "WHAT A PICK COUNTS (0.202.0). The walker asked which finding types should stop counting as majors\n"
    "for picking and left the call to the factory; its census (`docs/findings/pick_majors/` in the\n"
    "factory root, 62 cold workspace missions, 186 candidates) decided it. A major counts unless it is\n"
    "one of two kinds, each shown on the candidate's line as \"not counted\":\n"
    "\n"
    "* `ADVISORY` -- Laser Tag's verdicts on the fight its bots played, not on the level: a crew that\n"
    "  lost nobody (TRIVIAL_ENCOUNTER), died before it could react (NO_REACTION_TIME,\n"
    "  LT_NO_SURVIVABLE_OPENING), or never fired or was fired on (NO_ENGAGEMENT, NO_CONTACT). Its bots,\n"
    "  weapons and time-to-kill are not the game's -- `lasertag_report`'s reason LT_NO_SURVIVABLE_OPENING\n"
    "  does not block -- and the fight moves when the level does not: Laser Tag 0.31.0 changed only how\n"
    "  its guards walk and moved gas_block_001 seed_9181's crew survival from 9.51 to 18.88 s. They are\n"
    "  one set because they bracket one fight. Cold run 9283's three candidates carried one each,\n"
    "  NO_REACTION_TIME twice (crews dead in 6.44 and 7.80 s) and TRIVIAL_ENCOUNTER once, and not counting\n"
    "  either alone would have picked the other's failure. They still reach the pick through the score;\n"
    "  taken together they change none of the 62 picks.\n"
    "* `ANSWERED_BY_WALK` -- a doubt raised by a tool that cannot see what the walk test measures, not\n"
    "  counted where the walk test walked every leg (`walked_every_leg`). LOT_DESTINATION_ABOVE_FLOOR is\n"
    "  Lot saying an objective 3.3 to 4.0 m up -- a storey -- may stand where no stair reaches; the walk\n"
    "  test walks a crew body to it. It was on 96 of the 186 candidates, walked to on 95, and Laser Tag's\n"
    "  crew completed the route on 93. Counted, it chose 28 of the 62 picks: on 12 a lower route\n"
    "  completion or score than this rule picks, on 16 an equal one, on none a higher.\n"
    "\n"
    "Still counted: the out codes; the structural findings (a spawn missing, in collision or cut off; no\n"
    "world collision); every other tool's majors; and TRAVERSAL. On both of the two candidates that\n"
    "carried it the crew was wiped in 20 and 21 of 25 runs, a fight outcome, but a crew held by the\n"
    "geometry reads the same way.\n"
    "\n"
    "Everything is read from the workspace, from the files the shell leg wrote; nothing is run.\n")

IMPORTS_OLD = ("from collections import Counter, defaultdict\n"
               "from dataclasses import dataclass, field\n"
               "from pathlib import Path\n"
               "\n"
               "OUT_CODES = (\"LT_ROUTE_NEVER_COMPLETED\", \"LT_MAP_ENEMY_PATHING_BROKEN\")\n"
               "MAJOR = (\"major\", \"critical\", \"blocker\")\n")
IMPORTS_NEW = ("from collections import defaultdict\n"
               "from dataclasses import dataclass, field\n"
               "from pathlib import Path\n"
               "\n"
               "from packages.validation.lasertag_report import report_score\n"
               "\n"
               "OUT_CODES = (\"LT_ROUTE_NEVER_COMPLETED\", \"LT_MAP_ENEMY_PATHING_BROKEN\")\n"
               "MAJOR = (\"major\", \"critical\", \"blocker\")\n"
               "#: Laser Tag's verdicts on the fight its bots played: shown, not counted (WHAT A PICK COUNTS).\n"
               "ADVISORY = frozenset({\"LT_MAP_TRIVIAL_ENCOUNTER\", \"LT_MAP_NO_REACTION_TIME\",\n"
               "                      \"LT_NO_SURVIVABLE_OPENING\", \"LT_MAP_NO_ENGAGEMENT\", \"LT_MAP_NO_CONTACT\"})\n"
               "#: Doubts the walk test answers: not counted where it walked every leg (WHAT A PICK COUNTS).\n"
               "ANSWERED_BY_WALK = frozenset({\"LOT_DESTINATION_ABOVE_FLOOR\"})\n")

CANDIDATE_OLD = ("    out: list = field(default_factory=list)\n"
                 "\n"
                 "    def candidate_id(self, mission_id: str) -> str:\n"
                 "        return f\"{mission_id}.candidate.seed_{self.seed}\"\n"
                 "\n"
                 "    def line(self) -> str:\n"
                 "        rc = \"?\" if self.completion is None else f\"{self.completion:.2f}\"\n"
                 "        why = \", \".join(self.out) if self.out else \"nothing\"\n"
                 "        return f\"seed {self.seed}: {self.major} major, route completion {rc}, out for {why}\"\n")
CANDIDATE_NEW = ("    out: list = field(default_factory=list)\n"
                 "    score: float | None = None\n"
                 "    grade: str = \"?\"\n"
                 "    walked: bool = False\n"
                 "    not_counted: list = field(default_factory=list)\n"
                 "\n"
                 "    def candidate_id(self, mission_id: str) -> str:\n"
                 "        return f\"{mission_id}.candidate.seed_{self.seed}\"\n"
                 "\n"
                 "    def line(self) -> str:\n"
                 "        rc = \"?\" if self.completion is None else f\"{self.completion:.2f}\"\n"
                 "        sc = \"?\" if self.score is None else f\"{self.score:g}\"\n"
                 "        nc = f\" (not counted: {', '.join(self.not_counted)})\" if self.not_counted else \"\"\n"
                 "        why = \", \".join(self.out) if self.out else \"nothing\"\n"
                 "        return (f\"seed {self.seed}: {self.major} major{nc}, route completion {rc}, \"\n"
                 "                f\"grade {self.grade} {sc}, out for {why}\")\n")

WALKED_OLD = ("    return max(paths, key=attempt) if paths else None\n"
              "\n"
              "\n"
              "def candidates(internal_dir: Path, mission_id: str) -> list[Candidate]:\n")
WALKED_NEW = ("    return max(paths, key=attempt) if paths else None\n"
              "\n"
              "\n"
              "def walked_every_leg(walk) -> bool:\n"
              "    \"\"\"True when the walk test passed and a crew body walked every leg to every anchor.\n"
              "\n"
              "    Stricter than its `ok`, which also passes a leg Lot's director CREDITS as vertical access\n"
              "    without walking it (\"ok(N vertical leg(s) via ladder)\", `nav_qa_director._set_leg`), and an\n"
              "    objective only a ladder reaches is exactly the doubt LOT_DESTINATION_ABOVE_FLOOR raises. So\n"
              "    every crew walker (`player_*`; its targets are every heist anchor, the objective at its room's\n"
              "    floor among them) must read exactly \"ok\" with every target reached. A walk test that names no\n"
              "    crew walker has answered nothing and reads False. Bots are not read: the director credits a\n"
              "    bot with no walkable target as a matter of course.\n"
              "    \"\"\"\n"
              "    if not isinstance(walk, dict) or not walk.get(\"ok\"):\n"
              "        return False\n"
              "    crew = [w for w in walk.get(\"walkers\") or []\n"
              "            if isinstance(w, dict) and str(w.get(\"name\", \"\")).startswith(\"player_\")]\n"
              "    return bool(crew) and all(w.get(\"status\") == \"ok\"\n"
              "                              and w.get(\"targets_reached\") == w.get(\"targets_total\") for w in crew)\n"
              "\n"
              "\n"
              "def candidates(internal_dir: Path, mission_id: str) -> list[Candidate]:\n")

BODY_OLD = ("    rows = {s: Candidate(s) for s in seeds}\n"
            "    out = defaultdict(list)\n"
            "    major = Counter()\n"
            "    for issue in issues:\n"
            "        m = _SEED.search(str(issue.get(\"candidate_id\") or \"\"))\n"
            "        if not m or int(m.group(1)) not in rows:\n"
            "            continue\n"
            "        seed = int(m.group(1))\n"
            "        if issue.get(\"severity\") in MAJOR:\n"
            "            major[seed] += 1\n"
            "            if issue.get(\"code\") in OUT_CODES:\n"
            "                out[seed].append(str(issue[\"code\"]))\n"
            "    for seed, row in rows.items():\n"
            "        row.major = major[seed]\n"
            "        row.out = list(out[seed])\n"
            "        walk = _newest(list(jobs.glob(\n"
            "            f\"{mission_id}.walktest_navqa.candidate.seed_{seed}/*/out/*.walktest.json\")))\n"
            "        if walk is None:\n"
            "            row.out.append(\"no walktest\")\n"
            "        else:\n"
            "            try:\n"
            "                if not json.loads(walk.read_text(encoding=\"utf-8\")).get(\"ok\"):\n"
            "                    row.out.append(\"walktest not ok\")\n"
            "            except (OSError, ValueError) as exc:\n"
            "                row.out.append(f\"walktest unreadable ({type(exc).__name__})\")\n"
            "        report = _newest(list(jobs.glob(\n"
            "            f\"{mission_id}.laser_tag_evaluate.candidate.seed_{seed}/*/out/lasertag.report.json\")))\n"
            "        try:\n"
            "            row.completion = float(json.loads(report.read_text(encoding=\"utf-8\"))\n"
            "                                   [\"summary\"][\"route_completion_rate\"])\n"
            "        except (AttributeError, OSError, ValueError, KeyError, TypeError):\n"
            "            row.completion = None\n"
            "    return [rows[s] for s in seeds]\n")
BODY_NEW = ("    rows = {s: Candidate(s) for s in seeds}\n"
            "    majors = defaultdict(list)\n"
            "    for issue in issues:\n"
            "        m = _SEED.search(str(issue.get(\"candidate_id\") or \"\"))\n"
            "        if not m or int(m.group(1)) not in rows:\n"
            "            continue\n"
            "        if issue.get(\"severity\") in MAJOR:\n"
            "            majors[int(m.group(1))].append(str(issue.get(\"code\")))\n"
            "    for seed, row in rows.items():\n"
            "        row.out = [code for code in majors[seed] if code in OUT_CODES]\n"
            "        walk = _newest(list(jobs.glob(\n"
            "            f\"{mission_id}.walktest_navqa.candidate.seed_{seed}/*/out/*.walktest.json\")))\n"
            "        if walk is None:\n"
            "            row.out.append(\"no walktest\")\n"
            "        else:\n"
            "            try:\n"
            "                walked = json.loads(walk.read_text(encoding=\"utf-8\"))\n"
            "            except (OSError, ValueError) as exc:\n"
            "                row.out.append(f\"walktest unreadable ({type(exc).__name__})\")\n"
            "            else:\n"
            "                if not isinstance(walked, dict) or not walked.get(\"ok\"):\n"
            "                    row.out.append(\"walktest not ok\")\n"
            "                row.walked = walked_every_leg(walked)\n"
            "        for code in majors[seed]:\n"
            "            if code in ADVISORY or (code in ANSWERED_BY_WALK and row.walked):\n"
            "                row.not_counted.append(code)\n"
            "            else:\n"
            "                row.major += 1\n"
            "        report = _newest(list(jobs.glob(\n"
            "            f\"{mission_id}.laser_tag_evaluate.candidate.seed_{seed}/*/out/lasertag.report.json\")))\n"
            "        try:\n"
            "            data = json.loads(report.read_text(encoding=\"utf-8\"))\n"
            "        except (AttributeError, OSError, ValueError):\n"
            "            data = None\n"
            "        try:\n"
            "            row.completion = float(data[\"summary\"][\"route_completion_rate\"])\n"
            "        except (KeyError, TypeError, ValueError):\n"
            "            row.completion = None\n"
            "        if isinstance(data, dict):\n"
            "            row.score = report_score(data)\n"
            "            row.grade = str(data.get(\"grade\") or \"?\")\n"
            "    return [rows[s] for s in seeds]\n")

PICK_OLD = ("    best = sorted(pool, key=lambda r: (r.major,\n"
            "                                       -(r.completion if r.completion is not None else -1.0),\n"
            "                                       r.seed))[0]\n")
PICK_NEW = ("    best = sorted(pool, key=lambda r: (r.major,\n"
            "                                       -(r.completion if r.completion is not None else -1.0),\n"
            "                                       -(r.score if r.score is not None else -1.0),\n"
            "                                       r.seed))[0]\n")

JSON_OLD = ("            \"candidates\": [{\"seed\": r.seed, \"major\": r.major, \"route_completion\": r.completion,\n"
            "                            \"out\": r.out} for r in rows]}))\n")
JSON_NEW = ("            \"candidates\": [{\"seed\": r.seed, \"major\": r.major, \"not_counted\": r.not_counted,\n"
            "                            \"route_completion\": r.completion, \"score\": r.score,\n"
            "                            \"grade\": r.grade, \"out\": r.out} for r in rows]}))\n")


def _edits():
    return {
        "packages/pipeline/pick.py": [(DOC_RULE_OLD, DOC_RULE_NEW), (DOC_TAIL_OLD, DOC_TAIL_NEW),
                                      (IMPORTS_OLD, IMPORTS_NEW), (CANDIDATE_OLD, CANDIDATE_NEW),
                                      (WALKED_OLD, WALKED_NEW), (BODY_OLD, BODY_NEW), (PICK_OLD, PICK_NEW)],
        "apps/cli/commands/__init__.py": [(JSON_OLD, JSON_NEW)],
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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.202.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.202.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.202.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.202.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in _edits().items():
        raw = (LF / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:70])
            text = text.replace(old, new)
        compile(text, rel, "exec")
        writes[rel] = (text, eol)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, (body, e) in writes.items():
        (LF / rel).write_bytes(body.encode("utf-8").replace(b"\n", e))
    for r, data in news.items():
        (LF / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.201.0 -> 0.202.0")


if __name__ == "__main__":
    main()
