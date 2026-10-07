"""Level Factory 0.153.0: the brief's pacing reaches Lot, Lot's verdict reaches
the operator, and the brief fields nothing builds from are named (roadmap 200).

    python patch_lf_brief_pacing.py            # apply
    python patch_lf_brief_pacing.py --check    # verify every anchor, write nothing

Three disconnections on one dial, measured 2026-10-07:
  - `target_minutes` was written at the site spec's top level; Lot's pacing
    reads `pacing.target_minutes`, so 144 of 144 candidate specs on disk were
    judged against Lot's 7-15 min default (177 of 181 cold-run briefs ask for
    25-35).
  - the site spec carried no `mode`, so Lot's estimate counted no travel.
  - the Lot adapter matched "outside target" in the status, which only the
    straddle case carries; "likely TOO SHORT" and "likely TOO LONG" never
    surfaced.
And six brief fields build nothing: route_shape, objective_hypotheses,
extraction_relationship, verticality, landmark, seed_policy. The first five are
read only by `MissionBrief.functional_signature`, so changing one re-locks a
mission and changes no geometry. `batch create` now names the ones a brief
sets.

The mode turns on Lot's heist gate (`site_tactical.gate`, which fails the build
unless spawn, objective and extraction are joined). Measured first: it passes
on all 144 candidate specs on disk
(`docs/findings/brief_pacing_mode/heist_gate_census.py`).

Anchored on, as read 2026-10-07 (all LF):
  level_factory/apps/cli/commands/__init__.py   188,668 bytes
  level_factory/adapters/lot/__init__.py         18,236 bytes
  level_factory/packages/core/models.py          13,143 bytes
Every anchor must match once; nothing is written until every file matched.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

COMMANDS = [
    # 1. the mode, asked once; the unbuilt fields, named once
    ("#: A brief's word for \"place my own generated building\" (0.145.0).\n"
     "LOT_LIBRARY_NONE = \"none\"\n",
     "#: A brief's word for \"place my own generated building\" (0.145.0).\n"
     "LOT_LIBRARY_NONE = \"none\"\n"
     "\n"
     "\n"
     "def mission_mode(model) -> str:\n"
     "    \"\"\"THE MISSION'S MODE, asked once (0.153.0, roadmap 200). The brief has no\n"
     "    `mode` field, so every mission is a heist. Deli Counter's spec and Lot's\n"
     "    site spec both read this, so the two cannot disagree.\"\"\"\n"
     "    return getattr(model, \"mode\", None) or \"heist\"\n"
     "\n"
     "\n"
     "#: BRIEF FIELDS NOTHING BUILDS FROM YET (0.153.0, roadmap 200). Each is\n"
     "#: recorded in the brief and in the workspace's copy of it. Searched across\n"
     "#: every repo on 2026-10-07: the first five are read only by\n"
     "#: `MissionBrief.functional_signature`, so changing one re-locks a mission\n"
     "#: and changes no geometry; `seed_policy` is read by nothing. 181 cold-run\n"
     "#: briefs set the first five; none sets `seed_policy`. A field leaves this\n"
     "#: list in the release that builds something from it.\n"
     "UNBUILT_BRIEF_FIELDS = (\"route_shape\", \"objective_hypotheses\",\n"
     "                       \"extraction_relationship\", \"verticality\", \"landmark\",\n"
     "                       \"seed_policy\")\n"
     "\n"
     "\n"
     "def unbuilt_brief_fields(brief: dict) -> list[str]:\n"
     "    \"\"\"The fields this brief sets that nothing builds from yet, in\n"
     "    `UNBUILT_BRIEF_FIELDS` order. An empty value is not set.\"\"\"\n"
     "    return [f for f in UNBUILT_BRIEF_FIELDS if brief.get(f)]\n"),
    # 2. batch create says them out loud
    ("        note = _default_lot_library(ws, brief)\n"
     "        if note:\n"
     "            print(note)\n",
     "        note = _default_lot_library(ws, brief)\n"
     "        if note:\n"
     "            print(note)\n"
     "        # RECORDED, NOT BUILT (0.153.0, roadmap 200): a design intent the\n"
     "        # brief carries and nothing builds from is named, never silently\n"
     "        # dropped.\n"
     "        unbuilt = unbuilt_brief_fields(brief)\n"
     "        if unbuilt:\n"
     "            print(f\"[batch] {mission_id}: recorded, not built -- nothing builds \"\n"
     "                  f\"from {', '.join(unbuilt)} yet (roadmap 200)\")\n"),
    # 3. Deli Counter's spec reads the one mode
    ("                \"mode\": getattr(model, \"mode\", None) or \"heist\",\n",
     "                \"mode\": mission_mode(model),\n"),
    # 4. the site spec's docstring stops claiming readers that do not exist
    ("    degrees). Extra keys Lot ignores (site_shape/route_shape/target_minutes) are\n"
     "    kept for LF's own readers.\n",
     "    degrees). Extra keys Lot ignores (site_shape/route_shape/target_minutes) are\n"
     "    kept for the record: Level Factory reads `site_shape`, and nothing reads\n"
     "    the other two (roadmap 200). Lot's pacing reads `mode` and\n"
     "    `pacing.target_minutes` (0.153.0).\n"),
    # 5. the site spec carries the mode and the window where Lot reads them
    ("        \"route_shape\": model.route_shape,\n"
     "        \"target_minutes\": list(model.target_minutes),\n"
     "    }\n",
     "        \"route_shape\": model.route_shape,\n"
     "        \"target_minutes\": list(model.target_minutes),\n"
     "        # THE BRIEF'S PACING REACHES LOT (0.153.0, roadmap 200). Lot's\n"
     "        # `site_pacing` reads its window from `pacing.target_minutes` and\n"
     "        # counts travel only for a `mode` it knows. The key above reached no\n"
     "        # reader, so every level was judged against Lot's 7-15 min default\n"
     "        # (144 of 144 candidate specs on disk) with no travel counted (cold\n"
     "        # run 9193: `\"mode\": null`). The mode also turns on Lot's heist gate\n"
     "        # (`site_tactical.gate`): spawn, objective and extraction must be\n"
     "        # joined, and all 144 were\n"
     "        # (`docs/findings/brief_pacing_mode/heist_gate_census.py`).\n"
     "        \"mode\": mission_mode(model),\n"
     "        \"pacing\": {\"target_minutes\": list(model.target_minutes)},\n"
     "    }\n"),
]

ADAPTER = [
    ("from packages.adapters.sdk import BaseAdapter, PlannedCommand\n"
     "from packages.core.hashing import hash_file, scene_payload_hashes\n"
     "\n"
     "class LotAdapter(BaseAdapter):\n",
     "from packages.adapters.sdk import BaseAdapter, PlannedCommand\n"
     "from packages.core.hashing import hash_file, scene_payload_hashes\n"
     "\n"
     "#: THE STATUSES LOT'S PACING WRITES (`site_pacing.estimate_pacing`, Lot\n"
     "#: 0.97.4), by name (0.153.0, roadmap 200). Anything else is reported as\n"
     "#: LOT_PACING_UNREAD, never passed. `tests/unit/test_brief_pacing.py` reads\n"
     "#: Lot's source and fails when the two lists differ.\n"
     "LOT_PACING_WITHIN = (\"within target\",)\n"
     "LOT_PACING_OUTSIDE = (\"likely TOO SHORT vs target\",\n"
     "                      \"likely TOO LONG vs target\",\n"
     "                      \"partly outside target (range straddles the window)\")\n"
     "LOT_PACING_STATUSES = LOT_PACING_WITHIN + LOT_PACING_OUTSIDE\n"
     "\n"
     "\n"
     "class LotAdapter(BaseAdapter):\n"),
    ("        # Pacing is an ESTIMATE and never blocks (24.2). Surface an outside-target\n"
     "        # window as an informational note the operator can weigh.\n"
     "        pacing = data.get(\"pacing\") or {}\n"
     "        status = str(pacing.get(\"status\", \"\"))\n"
     "        if \"outside target\" in status:\n"
     "            issues.append({\n"
     "                \"code\": \"LOT_PACING_OUTSIDE_TARGET\",\n"
     "                \"severity\": \"moderate\",\n"
     "                \"category\": \"pacing\",\n"
     "                \"message\": (f\"pacing estimate {pacing.get('estimate_expected_min','?')} min \"\n"
     "                            f\"({pacing.get('range_min','?')}) vs target \"\n"
     "                            f\"{pacing.get('target_min','?')}: {status}\"),\n"
     "                \"blocking\": False,  # pacing never blocks\n"
     "                \"raw_source_path\": str(gameplay),\n"
     "            })\n",
     "        # Pacing is an ESTIMATE and never blocks (24.2). Surface an outside-target\n"
     "        # window as an informational note the operator can weigh.\n"
     "        #\n"
     "        # EVERY STATUS LOT WRITES, BY NAME (0.153.0, roadmap 200). This matched\n"
     "        # \"outside target\" in the status, which only the straddle case carries,\n"
     "        # so \"likely TOO SHORT vs target\" and \"likely TOO LONG vs target\" --\n"
     "        # the two verdicts that mean most -- never surfaced. A status not in\n"
     "        # LOT_PACING_STATUSES, or no pacing block at all, is said out loud\n"
     "        # rather than read as a pass.\n"
     "        raw = data.get(\"pacing\")\n"
     "        pacing = raw if isinstance(raw, dict) else {}\n"
     "        status = str(pacing.get(\"status\", \"\"))\n"
     "        if status in LOT_PACING_OUTSIDE:\n"
     "            # What the estimate counted, from its own breakdown: the reader\n"
     "            # weighs a window against the phases that filled it.\n"
     "            counted = []\n"
     "            for part in pacing.get(\"breakdown\") or []:\n"
     "                phase = str(part.get(\"phase\", \"?\"))\n"
     "                phase = \"travel\" if phase.startswith(\"travel\") else phase\n"
     "                if phase not in counted:\n"
     "                    counted.append(phase)\n"
     "            issues.append({\n"
     "                \"code\": \"LOT_PACING_OUTSIDE_TARGET\",\n"
     "                \"severity\": \"moderate\",\n"
     "                \"category\": \"pacing\",\n"
     "                \"message\": (f\"pacing estimate {pacing.get('estimate_expected_min','?')} min \"\n"
     "                            f\"({pacing.get('range_min','?')}) vs target \"\n"
     "                            f\"{pacing.get('target_min','?')}: {status} \"\n"
     "                            f\"(counted: {', '.join(counted) or 'nothing'})\"),\n"
     "                \"blocking\": False,  # pacing never blocks\n"
     "                \"raw_source_path\": str(gameplay),\n"
     "            })\n"
     "        elif status not in LOT_PACING_WITHIN:\n"
     "            issues.append({\n"
     "                \"code\": \"LOT_PACING_UNREAD\",\n"
     "                \"severity\": \"moderate\",\n"
     "                \"category\": \"pacing\",\n"
     "                \"message\": (\"Lot's gameplay manifest carries no pacing block\"\n"
     "                            if raw is None else\n"
     "                            f\"Lot's pacing status {status!r} is not one this \"\n"
     "                            f\"adapter knows (LOT_PACING_STATUSES)\"),\n"
     "                \"blocking\": False,  # pacing never blocks\n"
     "                \"raw_source_path\": str(gameplay),\n"
     "            })\n"),
]

MODELS = [
    ("    route_shape: str = \"\"\n"
     "    objective_hypotheses: list[str] = field(default_factory=list)\n",
     "    #: RECORDED, NOT BUILT (roadmap 200): nothing builds from `route_shape`,\n"
     "    #: `objective_hypotheses`, `extraction_relationship`, `verticality`,\n"
     "    #: `landmark` or `seed_policy` yet. The first five are in\n"
     "    #: `functional_signature` below, so changing one re-locks a mission and\n"
     "    #: changes no geometry. `batch create` names the ones a brief sets\n"
     "    #: (`apps.cli.commands.UNBUILT_BRIEF_FIELDS`).\n"
     "    route_shape: str = \"\"\n"
     "    objective_hypotheses: list[str] = field(default_factory=list)\n"),
]

FILES = [
    (LF / "apps" / "cli" / "commands" / "__init__.py", 188668, COMMANDS),
    (LF / "adapters" / "lot" / "__init__.py", 18236, ADAPTER),
    (LF / "packages" / "core" / "models.py", 13143, MODELS),
]


def main():
    check = "--check" in sys.argv[1:]
    staged = []
    for path, size, edits in FILES:
        data = path.read_bytes()
        assert len(data) == size, "%s is %d bytes, read at %d" % (path.name, len(data), size)
        assert b"\r\n" not in data, "%s has CRLF; it was LF" % path.name
        text = data.decode("utf-8")
        for old, new in edits:
            assert text.count(old) == 1, "%s: anchor found %d times: %r" % (path.name, text.count(old), old[:70])
            text = text.replace(old, new)
        staged.append((path, data, text))
    for path, data, text in staged:
        if check:
            print("%s: every anchor matched once (%d -> %d bytes, not written)"
                  % (path.name, len(data), len(text.encode("utf-8"))))
            continue
        path.write_bytes(text.encode("utf-8"))
        print("%s: %d -> %d bytes" % (path.name, len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
