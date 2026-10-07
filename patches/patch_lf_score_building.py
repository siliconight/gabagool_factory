"""Level Factory 0.152.0: the score is the building the brief asked for.

    python patch_lf_score_building.py

Roadmap 201. `site_variation.site_placements` drew the spawn and the objective
building independently from the seed, so the score ignored the archetype and
could be the spawn building (3 of 12 three-building sites, seeds 9000-9011).

  - `site_placements(..., objective=None)`: given, it IS the objective; the
    spawn is drawn among the other buildings; the objective's own draw is
    still made, so the extraction draw -- and every building's placement --
    does not move. Not given, the roles are the draw that always was.
  - `building_library.score_building(entries, archetype)`: "b0" when a family
    answers to the archetype (`pick_lot` places that family first), else None.
  - `_write_site_spec` passes it on the library path and records
    `objective_from` ("archetype" or "seed") in the site spec.

Anchored on, as read 2026-10-07 (all LF):
  level_factory/packages/pipeline/site_variation.py     29,140 bytes
  level_factory/packages/pipeline/building_library.py   36,302 bytes
  level_factory/apps/cli/commands/__init__.py          187,926 bytes
Every anchor must match once; nothing is written until every file matched.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

SITE_VARIATION = [
    ("def site_placements(seed: int, count: int, *, spacing: int = 45,\n"
     "                    footprints=None, shape=None, fronts=None,\n"
     "                    extents=None) -> dict:\n",
     "def site_placements(seed: int, count: int, *, spacing: int = 45,\n"
     "                    footprints=None, shape=None, fronts=None,\n"
     "                    extents=None, objective=None) -> dict:\n"),
    ("    The row is centred on the origin. It used to start there and march out along\n",
     "    ``objective`` (0.152.0): the building id that IS the score -- the brief's\n"
     "    archetype, which `pick_lot` places first (`building_library.score_building`).\n"
     "    Given, the spawn is drawn among the other buildings. Not given, the roles\n"
     "    are the seeded draw that always was.\n"
     "\n"
     "    The row is centred on the origin. It used to start there and march out along\n"),
    ("    ids = [f\"b{i}\" for i in range(count)]\n"
     "    spawn = ids[next(rng) % count]\n"
     "    objective = ids[next(rng) % count]\n",
     "    ids = [f\"b{i}\" for i in range(count)]\n"
     "    if objective is not None and objective not in ids:\n"
     "        raise ValueError(\"objective %r is not one of this site's buildings %r\"\n"
     "                         % (objective, ids))\n"
     "    if objective is not None and count > 1:\n"
     "        # THE SCORE IS THE BUILDING THE BRIEF ASKED FOR (0.152.0, roadmap 201).\n"
     "        # The two draws below used to pick spawn and objective independently,\n"
     "        # so the score ignored the archetype and, on 3 of 12 three-building\n"
     "        # sites (seeds 9000-9011), the crew spawned inside it. The objective's\n"
     "        # draw is still made, so the extraction draw does not move.\n"
     "        rest = [b for b in ids if b != objective]\n"
     "        spawn = rest[next(rng) % len(rest)]\n"
     "        next(rng)\n"
     "    else:\n"
     "        spawn = ids[next(rng) % count]\n"
     "        objective = ids[next(rng) % count]\n"),
]

BUILDING_LIBRARY = [
    ("            out.append(f)\n    return out\n\n\ndef pick_lot(",
     "            out.append(f)\n    return out\n\n\n"
     "def score_building(entries: list[dict], archetype: str):\n"
     "    \"\"\"The site building that IS the score: ``\"b0\"`` when a library family\n"
     "    answers to the brief's archetype, ``None`` when none does.\n"
     "\n"
     "    `pick_lot` places a variant of an anchor family FIRST, so the archetype's\n"
     "    building is always b0 on an anchored lot. With no such family the\n"
     "    archetype is not on the site at all, and the seeded pick stands rather\n"
     "    than a guess (0.152.0, roadmap 201).\n"
     "    \"\"\"\n"
     "    return \"b0\" if anchor_families(entries, archetype) else None\n"
     "\n"
     "\n"
     "def pick_lot("),
]

COMMANDS = [
    ("    lot = []\n    library = getattr(model, \"lot_library\", None)\n",
     "    lot = []\n"
     "    # the building that IS the score, when the lot is anchored (0.152.0)\n"
     "    score = None\n"
     "    library = getattr(model, \"lot_library\", None)\n"),
    ("        lot = building_library.pick_lot(\n"
     "            complete, seed, count,\n"
     "            anchor=getattr(model, \"archetype\", \"\") or \"\")\n",
     "        lot = building_library.pick_lot(\n"
     "            complete, seed, count,\n"
     "            anchor=getattr(model, \"archetype\", \"\") or \"\")\n"
     "        # THE SCORE IS THE BUILDING THE BRIEF ASKED FOR (0.152.0, roadmap\n"
     "        # 201): the anchor family's building, which `pick_lot` placed first.\n"
     "        score = building_library.score_building(\n"
     "            complete, getattr(model, \"archetype\", \"\") or \"\")\n"),
    ("        placed = site_placements(seed, len(lot), footprints=footprints,\n"
     "                                 shape=model.site_shape,\n",
     "        placed = site_placements(seed, len(lot), footprints=footprints,\n"
     "                                 shape=model.site_shape,\n"
     "                                 objective=score,\n"),
    ("        \"objective\": placed[\"objective\"],\n"
     "        \"extraction\": placed[\"extraction\"],\n",
     "        \"objective\": placed[\"objective\"],\n"
     "        \"extraction\": placed[\"extraction\"],\n"
     "        # WHICH RULE PICKED THE SCORE (0.152.0): \"archetype\" when the lot\n"
     "        # is anchored and b0 is the brief's building; \"seed\" otherwise --\n"
     "        # a single generated shell (every copy is the archetype's) or a lot\n"
     "        # whose library has no family for the archetype.\n"
     "        \"objective_from\": \"archetype\" if score else \"seed\",\n"),
]

FILES = [
    (LF / "packages" / "pipeline" / "site_variation.py", 29140, SITE_VARIATION),
    (LF / "packages" / "pipeline" / "building_library.py", 36302, BUILDING_LIBRARY),
    (LF / "apps" / "cli" / "commands" / "__init__.py", 187926, COMMANDS),
]


def main():
    staged = []
    for path, size, edits in FILES:
        data = path.read_bytes()
        assert len(data) == size, "%s is %d bytes, read at %d" % (path.name, len(data), size)
        assert b"\r\n" not in data, "%s has CRLF; it was LF" % path.name
        text = data.decode("utf-8")
        for old, new in edits:
            assert text.count(old) == 1, "%s: anchor found %d times: %r" % (path.name, text.count(old), old[:60])
            text = text.replace(old, new)
        staged.append((path, data, text))
    for path, data, text in staged:
        path.write_bytes(text.encode("utf-8"))
        print("%s: %d -> %d bytes" % (path.name, len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
