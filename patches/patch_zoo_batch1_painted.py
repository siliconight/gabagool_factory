#!/usr/bin/env python
"""patch_zoo_batch1_painted.py -- Zoo 0.43.0 -> 0.44.0

WHAT
  Batch 1 of the metal split: vending_machine, simple_car, helmet and
  queue_stanchion move from `metal` to `metal_painted`.

  GENOME DATA ONLY. All four already pass plan["material"] straight into
  make_material, so no recipe changes.

  THIS CHANGES WHAT RENDERS, once the theme libraries carry metal_painted
  (they do, as of pixelcoat 0.15.0). Requires patch_metal_split.py first --
  the kind must be in KNOWN_KINDS or the whole suite fails.

THE TRAP THIS BATCH IS SHAPED AROUND
  dna.resolve_plan does, with no warning:

      if material not in genome["materials"]["options"]:
          material = genome["materials"]["default"]

  A style naming a kind missing from `options` is DISCARDED. So each species
  is edited in two places, and getting it wrong produces a render that looks
  untouched. The new test asserts the invariant across ALL 53 genomes.

USAGE   (run from anywhere; paths are absolute)
  pwsh:  python patch_zoo_batch1_painted.py --check
         python patch_zoo_batch1_painted.py
         python patch_zoo_batch1_painted.py --selftest
         python patch_zoo_batch1_painted.py --revert

CONTRACT
  * refuses on drift (sha256 per target, recorded at generation time)
  * all-or-nothing
  * .pre_batch1 sidecars for --revert
  * __pycache__ purged after any write
"""
import argparse, hashlib, io, json, os, shutil, sys, tempfile

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
TAG = "batch1"
M = json.loads(r"""{
 "tool": "zoo",
 "from_version": "0.43.0",
 "to_version": "0.44.0",
 "tag": "batch1",
 "edits": [],
 "whole": {
  "zoo/zoo_keeper/genome/species/vending_machine.json": "{\n \"species\": \"vending_machine\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. No source meshes, no scraped data.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 0.7,\n   \"max\": 1.05,\n   \"default\": 0.85\n  },\n  \"depth\": {\n   \"min\": 0.6,\n   \"max\": 0.9,\n   \"default\": 0.75\n  },\n  \"height\": {\n   \"min\": 1.6,\n   \"max\": 2.0,\n   \"default\": 1.83\n  }\n },\n \"parts\": [\n  \"body\",\n  \"glass\",\n  \"panel\",\n  \"coin_slot\",\n  \"tray\"\n ],\n \"params\": {\n  \"lit\": {\n   \"min\": 0,\n   \"max\": 1,\n   \"default\": 1\n  }\n },\n \"materials\": {\n  \"default\": \"metal_painted\",\n  \"options\": [\n   \"metal_painted\",\n   \"plastic\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.62,\n    0.14,\n    0.14\n   ],\n   \"wear\": 0.2,\n   \"bevel\": 0.005\n  },\n  \"1990s\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.58,\n    0.16,\n    0.16\n   ],\n   \"wear\": 0.28,\n   \"bevel\": 0.005\n  },\n  \"blue\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.14,\n    0.26,\n    0.55\n   ],\n   \"wear\": 0.24,\n   \"bevel\": 0.005\n  },\n  \"snack\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.18,\n    0.2,\n    0.22\n   ],\n   \"wear\": 0.26,\n   \"bevel\": 0.005\n  },\n  \"modern\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.12,\n    0.14,\n    0.16\n   ],\n   \"wear\": 0.06,\n   \"bevel\": 0.003\n  },\n  \"center_city\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.6704,\n    0.233,\n    0.26\n   ],\n   \"wear\": 0.07,\n   \"bevel\": 0.005,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.315,\n    0.296,\n    0.29\n   ],\n   \"wear\": 0.42,\n   \"bevel\": 0.005,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.5828,\n    0.1386,\n    0.147\n   ],\n   \"wear\": 0.34,\n   \"bevel\": 0.005,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 6000\n },\n \"attachments\": [\n  \"ATT_tray\"\n ],\n \"keywords\": [\n  \"vending machine\",\n  \"vending\",\n  \"soda machine\",\n  \"snack machine\"\n ]\n}\n",
  "zoo/zoo_keeper/genome/species/simple_car.json": "{\n \"species\": \"simple_car\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. No source meshes, no scraped data.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 1.55,\n   \"max\": 2.0,\n   \"default\": 1.75\n  },\n  \"depth\": {\n   \"min\": 3.6,\n   \"max\": 5.2,\n   \"default\": 4.3\n  },\n  \"height\": {\n   \"min\": 1.3,\n   \"max\": 1.75,\n   \"default\": 1.45\n  }\n },\n \"parts\": [\n  \"body\",\n  \"cabin\",\n  \"wheel\",\n  \"window\",\n  \"bumper\"\n ],\n \"params\": {\n  \"wheels\": {\n   \"min\": 4,\n   \"max\": 4,\n   \"default\": 4\n  },\n  \"doors\": {\n   \"min\": 2,\n   \"max\": 4,\n   \"default\": 4\n  },\n  \"body_style\": [\n   \"sedan\",\n   \"hatchback\",\n   \"coupe\"\n  ],\n  \"wheel_segments\": {\n   \"min\": 10,\n   \"max\": 24,\n   \"default\": 14\n  }\n },\n \"materials\": {\n  \"default\": \"metal_painted\",\n  \"options\": [\n   \"metal_painted\",\n   \"plastic\",\n   \"glass\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.55,\n    0.56,\n    0.58\n   ],\n   \"wear\": 0.2,\n   \"bevel\": 0.01\n  },\n  \"1970s\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.55,\n    0.35,\n    0.1\n   ],\n   \"wear\": 0.45,\n   \"bevel\": 0.014\n  },\n  \"1980s\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.62,\n    0.1,\n    0.08\n   ],\n   \"wear\": 0.35,\n   \"bevel\": 0.012\n  },\n  \"1990s\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.3,\n    0.42,\n    0.35\n   ],\n   \"wear\": 0.3,\n   \"bevel\": 0.01\n  },\n  \"police\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.1,\n    0.1,\n    0.12\n   ],\n   \"wear\": 0.25,\n   \"bevel\": 0.01\n  },\n  \"racing\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.7,\n    0.08,\n    0.06\n   ],\n   \"wear\": 0.15,\n   \"bevel\": 0.01\n  },\n  \"center_city\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.606,\n    0.632,\n    0.7\n   ],\n   \"wear\": 0.07,\n   \"bevel\": 0.01,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.5388,\n    0.5119,\n    0.5007\n   ],\n   \"wear\": 0.42,\n   \"bevel\": 0.01,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.517,\n    0.5544,\n    0.609\n   ],\n   \"wear\": 0.34,\n   \"bevel\": 0.01,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 12000\n },\n \"attachments\": [\n  \"ATT_roof\",\n  \"ATT_driver_seat\",\n  \"ATT_trunk\"\n ],\n \"keywords\": [\n  \"car\",\n  \"sedan\",\n  \"hatchback\",\n  \"coupe\",\n  \"automobile\"\n ],\n \"prompt_rules\": [\n  {\n   \"any\": [\n    \"hatchback\"\n   ],\n   \"set\": {\n    \"params.body_style\": \"hatchback\"\n   }\n  },\n  {\n   \"any\": [\n    \"coupe\"\n   ],\n   \"set\": {\n    \"params.body_style\": \"coupe\"\n   }\n  }\n ]\n}\n",
  "zoo/zoo_keeper/genome/species/helmet.json": "{\n \"species\": \"helmet\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. No source meshes, no scraped data.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 0.2,\n   \"max\": 0.3,\n   \"default\": 0.24\n  },\n  \"depth\": {\n   \"min\": 0.24,\n   \"max\": 0.34,\n   \"default\": 0.28\n  },\n  \"height\": {\n   \"min\": 0.12,\n   \"max\": 0.22,\n   \"default\": 0.16\n  }\n },\n \"parts\": [\n  \"shell\",\n  \"brim\",\n  \"visor\"\n ],\n \"params\": {\n  \"brim\": {\n   \"min\": 0,\n   \"max\": 1,\n   \"default\": 0\n  },\n  \"visor\": {\n   \"min\": 0,\n   \"max\": 1,\n   \"default\": 0\n  },\n  \"segments\": {\n   \"min\": 12,\n   \"max\": 32,\n   \"default\": 20\n  }\n },\n \"materials\": {\n  \"default\": \"plastic\",\n  \"options\": [\n   \"plastic\",\n   \"metal_painted\",\n   \"carbon\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"plastic\",\n   \"color\": [\n    0.75,\n    0.72,\n    0.1\n   ],\n   \"wear\": 0.2,\n   \"bevel\": 0.002\n  },\n  \"construction\": {\n   \"material\": \"plastic\",\n   \"color\": [\n    0.85,\n    0.7,\n    0.05\n   ],\n   \"wear\": 0.35,\n   \"bevel\": 0.002\n  },\n  \"military\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.22,\n    0.26,\n    0.18\n   ],\n   \"wear\": 0.5,\n   \"bevel\": 0.002\n  },\n  \"motorcycle\": {\n   \"material\": \"carbon\",\n   \"color\": [\n    0.08,\n    0.08,\n    0.1\n   ],\n   \"wear\": 0.1,\n   \"bevel\": 0.002\n  },\n  \"sports\": {\n   \"material\": \"plastic\",\n   \"color\": [\n    0.7,\n    0.1,\n    0.08\n   ],\n   \"wear\": 0.25,\n   \"bevel\": 0.002\n  },\n  \"center_city\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.79,\n    0.784,\n    0.22\n   ],\n   \"wear\": 0.07,\n   \"bevel\": 0.002,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.5048,\n    0.4791,\n    0.4687\n   ],\n   \"wear\": 0.42,\n   \"bevel\": 0.002,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"plastic\",\n   \"color\": [\n    0.705,\n    0.7128,\n    0.105\n   ],\n   \"wear\": 0.34,\n   \"bevel\": 0.002,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 4000\n },\n \"attachments\": [\n  \"ATT_head_socket\"\n ],\n \"keywords\": [\n  \"helmet\",\n  \"hard hat\",\n  \"hardhat\"\n ],\n \"prompt_rules\": [\n  {\n   \"any\": [\n    \"construction\",\n    \"hard hat\",\n    \"hardhat\",\n    \"police\",\n    \"bobby\",\n    \"peaked\",\n    \"cap\",\n    \"brim\",\n    \"trooper\",\n    \"ranger\"\n   ],\n   \"set\": {\n    \"params.brim\": 1\n   }\n  },\n  {\n   \"any\": [\n    \"visor\",\n    \"motorcycle\"\n   ],\n   \"set\": {\n    \"params.visor\": 1\n   }\n  }\n ],\n \"connectors\": {\n  \"anchor\": {\n   \"type\": \"head\"\n  }\n }\n}\n",
  "zoo/zoo_keeper/genome/species/queue_stanchion.json": "{\n \"species\": \"queue_stanchion\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. A rope/belt queue post: weighted base, post, finial, belt hooks.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 0.28,\n   \"max\": 0.42,\n   \"default\": 0.35\n  },\n  \"depth\": {\n   \"min\": 0.28,\n   \"max\": 0.42,\n   \"default\": 0.35\n  },\n  \"height\": {\n   \"min\": 0.9,\n   \"max\": 1.1,\n   \"default\": 1.0\n  }\n },\n \"parts\": [\n  \"QueueStanchion_Base\",\n  \"QueueStanchion_Post\",\n  \"QueueStanchion_Finial\",\n  \"QueueStanchion_Hook\"\n ],\n \"params\": {},\n \"materials\": {\n  \"default\": \"metal_painted\",\n  \"options\": [\n   \"metal_painted\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.62,\n    0.55,\n    0.3\n   ],\n   \"wear\": 0.18,\n   \"bevel\": 0.004\n  },\n  \"delco\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.55,\n    0.56,\n    0.58\n   ],\n   \"wear\": 0.28,\n   \"bevel\": 0.004\n  },\n  \"center_city\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.606,\n    0.632,\n    0.7\n   ],\n   \"wear\": 0.098,\n   \"bevel\": 0.004,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.5388,\n    0.5119,\n    0.5007\n   ],\n   \"wear\": 0.5,\n   \"bevel\": 0.004,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.5828,\n    0.5445,\n    0.315\n   ],\n   \"wear\": 0.32,\n   \"bevel\": 0.004,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 1400\n },\n \"attachments\": [\n  \"ATT_belt\"\n ],\n \"collision\": true,\n \"connectors\": {\n  \"anchor\": {\n   \"type\": \"floor\"\n  },\n  \"sockets\": {\n   \"ATT_belt\": {\n    \"type\": \"grip\"\n   }\n  }\n },\n \"keywords\": [\n  \"queue stanchion\",\n  \"rope post\",\n  \"belt barrier\",\n  \"crowd post\"\n ]\n}\n",
  "zoo/VERSION": "Zoo 0.44.0\n"
 },
 "new": {
  "zoo/tests/test_material_options_closed.py": "\"\"\"The material-options invariant, and batch 1 of the metal split.\n\n`dna.resolve_plan` and `dna.resolve_module_plan` both do this, silently:\n\n    if material not in genome[\"materials\"][\"options\"]:\n        material = genome[\"materials\"][\"default\"]\n\nA style block naming a kind that is missing from `options` is DISCARDED, and\nthe species quietly renders in its default material. Nothing logs. The render\nlooks plausible. That is the trap the metal split walks into once per species,\nand it is why these tests sweep every genome rather than only the ones a given\nbatch touched.\n\"\"\"\n\nimport glob\nimport json\nimport os\n\nimport pytest\n\nfrom zoo_keeper.core import skins\n\nSPECIES_DIR = os.path.join(os.path.dirname(os.path.dirname(\n    os.path.abspath(__file__))), \"zoo_keeper\", \"genome\", \"species\")\nBATCH1 = (\"vending_machine\", \"simple_car\", \"helmet\", \"queue_stanchion\")\n\n\ndef _genomes():\n    out = []\n    for p in sorted(glob.glob(os.path.join(SPECIES_DIR, \"*.json\"))):\n        out.append(json.load(open(p, encoding=\"utf-8\")))\n    return out\n\n\ndef test_the_sweep_is_actually_reading_genomes():\n    \"\"\"Guard the guard: every assertion below is a loop, and a loop over an\n    empty directory passes vacuously.\"\"\"\n    g = _genomes()\n    assert len(g) >= 50, \"only %d genomes found\" % len(g)\n    assert any(x[\"species\"] == \"vending_machine\" for x in g)\n\n\n@pytest.mark.parametrize(\"g\", _genomes(), ids=lambda g: g[\"species\"])\ndef test_every_style_material_is_in_options(g):\n    opts = set(g[\"materials\"].get(\"options\", []))\n    for name, style in g.get(\"styles\", {}).items():\n        if not isinstance(style, dict) or \"material\" not in style:\n            continue\n        assert style[\"material\"] in opts, (\n            \"%s style %r names %r, which is not in materials.options %s. \"\n            \"resolve_plan will discard it and silently use %r.\"\n            % (g[\"species\"], name, style[\"material\"], sorted(opts),\n               g[\"materials\"].get(\"default\")))\n\n\n@pytest.mark.parametrize(\"g\", _genomes(), ids=lambda g: g[\"species\"])\ndef test_default_material_is_in_options(g):\n    opts = set(g[\"materials\"].get(\"options\", []))\n    assert g[\"materials\"][\"default\"] in opts, (\n        \"%s default %r is not in its own options -- the fallback target is \"\n        \"itself unreachable\" % (g[\"species\"], g[\"materials\"][\"default\"]))\n\n\n@pytest.mark.parametrize(\"g\", _genomes(), ids=lambda g: g[\"species\"])\ndef test_every_named_kind_is_in_the_vocabulary(g):\n    \"\"\"A kind nothing knows takes the 0.6 default roughness and resolves no\n    pack. This is the check that would have caught `tar` on day one.\"\"\"\n    named = set(g[\"materials\"].get(\"options\", []))\n    named.add(g[\"materials\"][\"default\"])\n    for style in g.get(\"styles\", {}).values():\n        if isinstance(style, dict) and \"material\" in style:\n            named.add(style[\"material\"])\n    unknown = named - set(skins.KNOWN_KINDS)\n    assert not unknown, \"%s names unknown kinds: %s\" % (g[\"species\"],\n                                                        sorted(unknown))\n\n\n@pytest.mark.parametrize(\"sp\", BATCH1)\ndef test_batch1_species_are_on_painted_metal(sp):\n    g = json.load(open(os.path.join(SPECIES_DIR, sp + \".json\"),\n                       encoding=\"utf-8\"))\n    opts = g[\"materials\"][\"options\"]\n    assert \"metal_painted\" in opts, \"%s did not gain metal_painted\" % sp\n    assert \"metal\" not in opts, (\n        \"%s still offers raw `metal`; a prompt naming it would resolve the \"\n        \"theme-owned pack and ignore the genome colour\" % sp)\n    for name, style in g.get(\"styles\", {}).items():\n        assert style.get(\"material\") != \"metal\", \\\n            \"%s style %r was left on raw metal\" % (sp, name)\n\n\ndef test_batch1_is_the_only_thing_that_moved():\n    \"\"\"The other 49 genomes must still be on plain `metal`. When batch 2 lands\n    this list changes deliberately, not by surprise.\"\"\"\n    moved = [g[\"species\"] for g in _genomes()\n             if \"metal_painted\" in g[\"materials\"].get(\"options\", [])]\n    assert sorted(moved) == sorted(BATCH1), (\n        \"species on metal_painted: %s\\nexpected exactly batch 1: %s\"\n        % (sorted(moved), sorted(BATCH1)))\n"
 },
 "changelogs": {
  "zoo/CHANGELOG.md": "## [0.44.0] - batch 1: the four painted-metal species\n\nThe first four species whose metal is unambiguously paint, taken from the\nchroma measurement in 0.43.0:\n\n    simple_car        chroma 0.64    9 styles\n    helmet            chroma 0.57    3 styles\n    vending_machine   chroma 0.48    8 styles\n    queue_stanchion   chroma 0.32    5 styles\n\nAll four already pass `plan[\"material\"]` straight into `make_material`, so no\nrecipe changed. This is genome data only.\n\n### Changed\n- Each species swaps `metal` for `metal_painted` in `materials.options`, in\n  `materials.default` where that was `metal` (all but helmet, whose default is\n  `plastic`), and in every style block whose `material` was `metal`.\n\n`metal` is REMOVED from these four rather than left alongside `metal_painted`.\nLeft in, a prompt naming \"metal\" would resolve the theme-owned pack and ignore\nthe genome colour -- the exact defect this split exists to fix. Removed, that\nprompt falls through to the species default, which is now the painted kind.\n\n### Added\n- `tests/test_material_options_closed.py`. It asserts, for ALL 53 genomes and\n  not just these four, that every `styles[*].material` and the `default` are\n  present in `materials.options`.\n\n### Why that test is the point of this batch\n`dna.resolve_plan` does this, with no warning:\n\n    if material not in genome[\"materials\"][\"options\"]:\n        material = genome[\"materials\"][\"default\"]\n\nA style naming a kind missing from `options` is DISCARDED and the species\nquietly renders in its default. So every species edit is two places, and the\nfailure mode is a render that looks untouched -- which is unfalsifiable by\neye. The first attempt at generating this patch hit exactly that class of bug\nfrom the other side: a substring rewrite of `\"metal\",` also matched inside\n`\"material\": \"metal\",`, so queue_stanchion had its styles rewritten and its\noptions list left alone. The genomes are byte-exact `json.dumps(indent=1)`\noutput, so the edit is now structural and the generated diff is asserted to\ntouch no line that does not mention metal.\n\n### Still on plain `metal`\n38 species. Eight are the remaining coloured ones: chair, filing_cabinet,\nwater_tank, flat_top_grill, shelving, atm, vault_door -- plus gold_bar, which\nis chroma 0.61 but is BARE metal and wants `metal_bare`, not paint. The other\n30 are already near-grey and correctly keep `metal`; ten of those are\narchitecture and must.\n\nNOTE for batch 2: `shelving.json` is NOT byte-exact indent=1 round-trippable,\nunlike every other genome checked. It needs an anchored edit or a deliberate\nreformat, not a structural re-dump.\n\n"
 },
 "pre_sha": {
  "zoo/zoo_keeper/genome/species/vending_machine.json": "402244a95a2f29838e076b85729019f81200cfe1466b5fa3fc9c1168759e8e15",
  "zoo/zoo_keeper/genome/species/simple_car.json": "8f3dc8070aa594d0984a19a408e696f5be0897971ade23866afcee92a6ed8e8b",
  "zoo/zoo_keeper/genome/species/helmet.json": "451bb47e19bd03bbc4543460e3f1c78ff95cf5491a46c751c5862a79c72753ce",
  "zoo/zoo_keeper/genome/species/queue_stanchion.json": "f4772528aef5ac1568e674cd28fa22d207665f57b245adf245792866eab20731",
  "zoo/VERSION": "d33c5b395b1cbf1165d1b843ce2baad8910f0d7678de3fbc7c9f0ab6861d6033",
  "zoo/CHANGELOG.md": "5a13525ffa34cc49f7e0aab4db000a26e4eefcaaed1294f318d3a402187466a7"
 }
}""")


def _abs(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _write(path, text):
    """Never truncate the target before the content is known good."""
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    os.close(fd)
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def _purge_bytecode(rels):
    """Delete __pycache__ for every package dir we just rewrote a .py in.

    Found the hard way: rewriting version.py in the same wall-clock SECOND
    that its .pyc was written left the .pyc valid by Python's (mtime, size)
    check -- both were 366 bytes and both stamped the same second -- so the
    interpreter kept serving the OLD constant and the selftest reported the
    change had not landed. It had. A patch tool that edits live Python must
    invalidate bytecode or it can silently appear to do nothing.
    """
    seen = set()
    for rel in rels:
        if not rel.endswith(".py"):
            continue
        d = os.path.join(os.path.dirname(_abs(rel)), "__pycache__")
        if d in seen or not os.path.isdir(d):
            continue
        seen.add(d)
        shutil.rmtree(d, ignore_errors=True)
        print("  purged " + os.path.relpath(d, ROOT))
    return len(seen)


# --------------------------------------------------------------------------- #
# pre-flight
# --------------------------------------------------------------------------- #

def preflight(expect_patched=False):
    """Returns (ok, list of problem strings). Writes nothing, ever."""
    bad = []
    targets = set(M["pre_sha"])
    for rel in sorted(targets):
        p = _abs(rel)
        if not os.path.isfile(p):
            bad.append("MISSING  " + rel)
            continue
        got = _sha(p)
        want = M["pre_sha"][rel]
        if got != want and not expect_patched:
            bad.append("DRIFT    %s\n           on disk %s\n           expect  %s"
                       % (rel, got[:16], want[:16]))
    # anchors must be present exactly once
    for e in M["edits"]:
        p = _abs(e["path"])
        if not os.path.isfile(p):
            continue
        src = _read(p)
        n = src.count(e["anchor"])
        if n != 1 and not expect_patched:
            bad.append("ANCHOR   %s occurs %d times (need exactly 1)"
                       % (e["path"], n))
    for rel in M["new"]:
        p = _abs(rel)
        if os.path.isfile(p) and not expect_patched:
            bad.append("EXISTS   %s (refusing to overwrite a file this "
                       "patch claims to create)" % rel)
    return (not bad), bad


# --------------------------------------------------------------------------- #
# apply
# --------------------------------------------------------------------------- #

def apply():
    ok, bad = preflight()
    if not ok:
        print("REFUSED -- nothing written:")
        for b in bad:
            print("  " + b)
        return 1

    # Build every output IN MEMORY first. Only then touch the disk.
    out = {}

    by_file = {}
    for e in M["edits"]:
        by_file.setdefault(e["path"], []).append(e)
    for rel, edits in by_file.items():
        src = _read(_abs(rel))
        for e in edits:
            src = src.replace(e["anchor"], e["after"], 1)
        out[rel] = src

    for rel, text in M["whole"].items():
        out[rel] = text
    for rel, text in M["new"].items():
        out[rel] = text

    head = "# Changelog\n\n"
    for cl_rel, entry in M["changelogs"].items():
        cl = _read(_abs(cl_rel))
        if not cl.startswith(head):
            print("REFUSED -- %s does not start with the expected header"
                  % cl_rel)
            return 1
        out[cl_rel] = head + entry + cl[len(head):]

    # sidecars, then write
    for rel in sorted(out):
        p = _abs(rel)
        if os.path.isfile(p):
            shutil.copy2(p, p + ".pre_" + TAG)
    for rel in sorted(out):
        _write(_abs(rel), out[rel])
        print("  wrote  %-52s %8d bytes" % (rel, len(out[rel].encode("utf-8"))))

    _purge_bytecode(out)

    print("")
    print("%s %s -> %s" % (M["tool"], M["from_version"], M["to_version"]))
    return 0


def revert():
    n = 0
    for rel in sorted(set(list(M["pre_sha"]) + list(M["new"]))):
        p = _abs(rel)
        side = p + ".pre_" + TAG
        if os.path.isfile(side):
            shutil.copy2(side, p)
            os.remove(side)
            print("  restored " + rel)
            n += 1
        elif rel in M["new"] and os.path.isfile(p):
            os.remove(p)
            print("  removed  " + rel)
            n += 1
    _purge_bytecode(set(list(M["pre_sha"]) + list(M["new"])))
    print("reverted %d file(s)" % n)
    return 0 if n else 1


# --------------------------------------------------------------------------- #
# selftest -- must FAIL if the change is backed out
# --------------------------------------------------------------------------- #

def selftest():
    sys.path.insert(0, os.path.join(ROOT, "zoo"))
    fails = []
    try:
        return _selftest(fails)
    except Exception as exc:
        print("SELFTEST FAILED -- %s: %s" % (type(exc).__name__, exc))
        for f in fails:
            print("  - " + f)
        return 1


def _selftest(fails):
    import glob as _glob
    import json as _json
    import types as _types

    BATCH1 = ("vending_machine", "simple_car", "helmet", "queue_stanchion")
    SPD = os.path.join(ROOT, "zoo", "zoo_keeper", "genome", "species")

    from zoo_keeper.core import skins

    # ---- 0. ordering: the kind must already be registered ------------------
    if "metal_painted" not in skins.KNOWN_KINDS:
        fails.append("metal_painted is not in KNOWN_KINDS -- apply "
                     "patch_metal_split.py FIRST or the whole suite fails")
        print("SELFTEST FAILED (1):")
        for f in fails:
            print("  - " + f)
        return 1

    genomes = {}
    for p in sorted(_glob.glob(os.path.join(SPD, "*.json"))):
        g = _json.load(open(p, encoding="utf-8"))
        genomes[g["species"]] = g
    if len(genomes) < 50:
        fails.append("only %d genomes read -- the sweeps below would pass "
                     "vacuously" % len(genomes))

    # ---- 1. THE INVARIANT, swept over every genome -------------------------
    for sp, g in sorted(genomes.items()):
        opts = set(g["materials"].get("options", []))
        if g["materials"]["default"] not in opts:
            fails.append("%s: default %r is not in its own options"
                         % (sp, g["materials"]["default"]))
        for name, s in g.get("styles", {}).items():
            if isinstance(s, dict) and "material" in s:
                if s["material"] not in opts:
                    fails.append("%s style %r names %r, not in options -- "
                                 "resolve_plan discards it SILENTLY"
                                 % (sp, name, s["material"]))
        named = opts | {g["materials"]["default"]}
        for s in g.get("styles", {}).values():
            if isinstance(s, dict) and "material" in s:
                named.add(s["material"])
        unknown = named - set(skins.KNOWN_KINDS)
        if unknown:
            fails.append("%s names kinds outside the vocabulary: %s"
                         % (sp, sorted(unknown)))

    # ---- 2. batch 1 actually moved, and nothing else did -------------------
    for sp in BATCH1:
        g = genomes.get(sp)
        if g is None:
            fails.append("%s genome missing" % sp); continue
        opts = g["materials"]["options"]
        if "metal_painted" not in opts:
            fails.append("%s did not gain metal_painted" % sp)
        if "metal" in opts:
            fails.append("%s still offers raw metal" % sp)
        left = [n for n, s in g.get("styles", {}).items()
                if isinstance(s, dict) and s.get("material") == "metal"]
        if left:
            fails.append("%s styles left on raw metal: %s" % (sp, left))
    moved = sorted(sp for sp, g in genomes.items()
                   if "metal_painted" in g["materials"].get("options", []))
    if moved != sorted(BATCH1):
        fails.append("species on metal_painted: %s\n      expected exactly "
                     "batch 1: %s" % (moved, sorted(BATCH1)))

    # ---- 3. THE FALSIFICATION: run the real resolver -----------------------
    #      Not a re-implementation of the fallback rule -- dna.resolve_plan
    #      itself, for every style of every batch-1 species. If `options` and
    #      the style disagree, this returns the default and the assert fires.
    from zoo_keeper.core import dna, seeding

    def _intent(era):
        return _types.SimpleNamespace(
            era=era, style_tags=(), material=None, color=None, wear=None,
            prompt_norm="", size_hint=1.0, counts={})

    ran = 0
    for sp in BATCH1:
        g = genomes.get(sp)
        if g is None:
            continue
        for style_name, s in g.get("styles", {}).items():
            if not isinstance(s, dict) or "material" not in s:
                continue
            try:
                plan = dna.resolve_plan(_intent(style_name), g,
                                        seeding.RNGStreams("selftest/%s/%s"
                                                           % (sp, style_name)),
                                        "selftest")
            except Exception as exc:
                fails.append("resolve_plan(%s, %s) raised %s: %s"
                             % (sp, style_name, type(exc).__name__, exc))
                continue
            ran += 1
            if plan["style"] != style_name:
                continue          # a style the picker does not select by era
            if plan["material"] != s["material"]:
                fails.append("resolve_plan(%s, %s) returned material %r but "
                             "the style declares %r -- the SILENT FALLBACK "
                             "fired" % (sp, style_name, plan["material"],
                                        s["material"]))
    if ran == 0:
        fails.append("resolve_plan was never exercised -- check 3 is asleep")
    else:
        print("  resolve_plan exercised on %d (species, style) pairs" % ran)

    # ---- 4. the new test file exists and passes ---------------------------
    tf = os.path.join(ROOT, "zoo", "tests", "test_material_options_closed.py")
    if not os.path.isfile(tf):
        fails.append("tests/test_material_options_closed.py is missing")
    else:
        try:
            import pytest as _pytest
            if _pytest.main([tf, "-q"]) != 0:
                fails.append("test_material_options_closed.py failed")
        except ImportError:
            print("  (pytest not importable here; run it yourself)")

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("SELFTEST OK -- invariant swept over %d genomes, batch 1 moved and "
          "nothing else, and the REAL dna.resolve_plan returns metal_painted "
          "for every batch-1 style" % len(genomes))
    return 0


def check():
    ok, bad = preflight()
    print("targets:")
    for rel in sorted(M["pre_sha"]):
        p = _abs(rel)
        state = "ok" if os.path.isfile(p) and _sha(p) == M["pre_sha"][rel] else "DRIFT/MISSING"
        print("  %-14s %s" % (state, rel))
    for rel in M["new"]:
        print("  %-14s %s" % ("create" if not os.path.isfile(_abs(rel)) else "EXISTS", rel))
    print("")
    if ok:
        print("PRE-FLIGHT CLEAN -- apply would write %d file(s)"
              % (len(M["pre_sha"]) + len(M["new"])))
        return 0
    print("PRE-FLIGHT REFUSED:")
    for b in bad:
        print("  " + b)
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--revert", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check()
    if a.revert:
        return revert()
    if a.selftest:
        return selftest()
    return apply()


if __name__ == "__main__":
    sys.exit(main())
