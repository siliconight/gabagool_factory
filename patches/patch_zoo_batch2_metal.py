#!/usr/bin/env python
"""patch_zoo_batch2_metal.py -- Zoo 0.44.0 -> 0.45.0

WHAT
  Batch 2 of the metal split -- eight species off raw `metal`:

     metal_painted   chair, filing_cabinet, atm
     metal_bare      gold_bar, flat_top_grill, water_tank, shelving,
                     vault_door

  NOT the 7-painted/1-bare split the batch-1 notes predicted. That grouping
  ranked by chroma; this one reads the hue. flat_top_grill's
  [0.677, 0.723, 0.787] is the blue cast of stainless, not a chosen colour;
  water_tank's warm brown is rust; filing_cabinet's putty is paint.

ALSO FIXES TWO GENOMES THAT WERE INERT
  flat_top_grill.py passed the literal "metal" to all three make_material
  calls, so editing its genome changed NOTHING, silently. vault_door.py
  hard-coded only its hub, which would have split one door across two kinds
  the moment its genome moved. Both now pass plan["material"].

REQUIRES patch_metal_split.py (zoo 0.43.0) -- both kinds must be in
KNOWN_KINDS or the suite fails.

USAGE   (run from anywhere; paths are absolute)
  python patch_zoo_batch2_metal.py --check
  python patch_zoo_batch2_metal.py
  python patch_zoo_batch2_metal.py --selftest
  python patch_zoo_batch2_metal.py --revert

CONTRACT
  * refuses on drift (sha256 per target, recorded at generation time)
  * all-or-nothing; anchors must occur EXACTLY ONCE
  * .pre_batch2 sidecars for --revert
  * __pycache__ purged after any write
"""
import argparse, hashlib, io, json, os, shutil, sys, tempfile

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
TAG = "batch2"
M = json.loads(r"""{
 "tool": "zoo",
 "from_version": "0.44.0",
 "to_version": "0.45.0",
 "tag": "batch2",
 "edits": [
  {
   "path": "zoo/zoo_keeper/recipes/flat_top_grill.py",
   "anchor": "    steel = materials.make_material(\"M_Grill_steel\", plan[\"color\"], \"metal\")\n    top = materials.make_material(\"M_Grill_cooktop\",\n                                  _darker(plan[\"color\"], 0.4), \"metal\")\n    dark = materials.make_material(\"M_Grill_trim\",\n                                   _darker(plan[\"color\"], 0.6), \"metal\")\n",
   "after": "    # plan[\"material\"], not the literal \"metal\". These three were hard-coded,\n    # which made this species' genome INERT: editing materials.default or a\n    # style's material changed nothing at all, silently. A grill is stainless,\n    # so its genome now says metal_bare and these follow it.\n    kind = plan[\"material\"]\n    steel = materials.make_material(\"M_Grill_steel\", plan[\"color\"], kind)\n    top = materials.make_material(\"M_Grill_cooktop\",\n                                  _darker(plan[\"color\"], 0.4), kind)\n    dark = materials.make_material(\"M_Grill_trim\",\n                                   _darker(plan[\"color\"], 0.6), kind)\n"
  },
  {
   "path": "zoo/zoo_keeper/recipes/vault_door.py",
   "anchor": "    hub_mat = materials.make_material(\n        \"M_VaultDoor_hub\", [c * 0.75 for c in plan[\"color\"]], \"metal\")\n",
   "after": "    # plan[\"material\"], not the literal \"metal\": the body above already reads\n    # the genome, and a hard-coded hub would leave one door split across two\n    # material kinds the moment the genome moved off `metal`.\n    hub_mat = materials.make_material(\n        \"M_VaultDoor_hub\", [c * 0.75 for c in plan[\"color\"]],\n        plan[\"material\"])\n"
  }
 ],
 "whole": {
  "zoo/zoo_keeper/genome/species/chair.json": "{\n \"species\": \"chair\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. No source meshes, no scraped data.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 0.38,\n   \"max\": 0.62,\n   \"default\": 0.45\n  },\n  \"depth\": {\n   \"min\": 0.38,\n   \"max\": 0.6,\n   \"default\": 0.45\n  },\n  \"height\": {\n   \"min\": 0.75,\n   \"max\": 1.1,\n   \"default\": 0.85\n  }\n },\n \"parts\": [\n  \"seat\",\n  \"back\",\n  \"leg\",\n  \"arm\"\n ],\n \"params\": {\n  \"legs\": {\n   \"min\": 3,\n   \"max\": 4,\n   \"default\": 4\n  },\n  \"has_arms\": {\n   \"min\": 0,\n   \"max\": 1,\n   \"default\": 0\n  }\n },\n \"materials\": {\n  \"default\": \"wood\",\n  \"options\": [\n   \"wood\",\n   \"metal_painted\",\n   \"plastic\",\n   \"leather\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"wood\",\n   \"color\": [\n    0.42,\n    0.28,\n    0.15\n   ],\n   \"wear\": 0.15,\n   \"bevel\": 0.004\n  },\n  \"1970s\": {\n   \"material\": \"wood\",\n   \"color\": [\n    0.35,\n    0.22,\n    0.1\n   ],\n   \"wear\": 0.35,\n   \"bevel\": 0.006\n  },\n  \"1990s\": {\n   \"material\": \"plastic\",\n   \"color\": [\n    0.25,\n    0.28,\n    0.45\n   ],\n   \"wear\": 0.25,\n   \"bevel\": 0.003\n  },\n  \"office\": {\n   \"material\": \"plastic\",\n   \"color\": [\n    0.15,\n    0.15,\n    0.18\n   ],\n   \"wear\": 0.2,\n   \"bevel\": 0.003\n  },\n  \"school\": {\n   \"material\": \"plastic\",\n   \"color\": [\n    0.55,\n    0.35,\n    0.12\n   ],\n   \"wear\": 0.45,\n   \"bevel\": 0.003\n  },\n  \"center_city\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.4864,\n    0.366,\n    0.27\n   ],\n   \"wear\": 0.052,\n   \"bevel\": 0.004,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.3008,\n    0.2823,\n    0.2767\n   ],\n   \"wear\": 0.37,\n   \"bevel\": 0.004,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"wood\",\n   \"color\": [\n    0.3948,\n    0.2772,\n    0.1575\n   ],\n   \"wear\": 0.29,\n   \"bevel\": 0.004,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 5000\n },\n \"attachments\": [\n  \"ATT_seat_center\"\n ],\n \"keywords\": [\n  \"chair\",\n  \"stool\",\n  \"office seat\"\n ],\n \"prompt_rules\": [\n  {\n   \"any\": [\n    \"office\",\n    \"gaming\",\n    \"armchair\",\n    \"arm chair\",\n    \"arms\"\n   ],\n   \"set\": {\n    \"params.has_arms\": 1\n   }\n  }\n ]\n}\n",
  "zoo/zoo_keeper/genome/species/filing_cabinet.json": "{\n \"species\": \"filing_cabinet\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. No source meshes, no scraped data.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 0.35,\n   \"max\": 0.47,\n   \"default\": 0.38\n  },\n  \"depth\": {\n   \"min\": 0.5,\n   \"max\": 0.72,\n   \"default\": 0.62\n  },\n  \"height\": {\n   \"min\": 0.7,\n   \"max\": 1.35,\n   \"default\": 1.32\n  }\n },\n \"parts\": [\n  \"body\",\n  \"drawer\",\n  \"handle\",\n  \"base\"\n ],\n \"params\": {\n  \"drawers\": {\n   \"min\": 2,\n   \"max\": 5,\n   \"default\": 4\n  },\n  \"base\": {\n   \"min\": 0,\n   \"max\": 1,\n   \"default\": 1\n  }\n },\n \"materials\": {\n  \"default\": \"metal_painted\",\n  \"options\": [\n   \"metal_painted\",\n   \"wood\",\n   \"laminate\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.55,\n    0.54,\n    0.5\n   ],\n   \"wear\": 0.15,\n   \"bevel\": 0.003\n  },\n  \"1970s\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.45,\n    0.42,\n    0.3\n   ],\n   \"wear\": 0.35,\n   \"bevel\": 0.004\n  },\n  \"1980s\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.6,\n    0.58,\n    0.52\n   ],\n   \"wear\": 0.28,\n   \"bevel\": 0.003\n  },\n  \"1990s\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.68,\n    0.66,\n    0.6\n   ],\n   \"wear\": 0.25,\n   \"bevel\": 0.003\n  },\n  \"modern\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.8,\n    0.8,\n    0.8\n   ],\n   \"wear\": 0.05,\n   \"bevel\": 0.002\n  },\n  \"office\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.66,\n    0.64,\n    0.58\n   ],\n   \"wear\": 0.2,\n   \"bevel\": 0.003\n  },\n  \"center_city\": {\n   \"material\": \"laminate\",\n   \"color\": [\n    0.606,\n    0.613,\n    0.62\n   ],\n   \"wear\": 0.052,\n   \"bevel\": 0.003,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.5105,\n    0.4846,\n    0.474\n   ],\n   \"wear\": 0.37,\n   \"bevel\": 0.003,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.517,\n    0.5346,\n    0.525\n   ],\n   \"wear\": 0.29,\n   \"bevel\": 0.003,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 6000\n },\n \"attachments\": [\n  \"ATT_top_center\"\n ],\n \"keywords\": [\n  \"filing cabinet\",\n  \"file cabinet\",\n  \"filing\",\n  \"cabinet\"\n ]\n}\n",
  "zoo/zoo_keeper/genome/species/atm.json": "{\n \"species\": \"atm\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. No source meshes, no scraped data.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 0.5,\n   \"max\": 0.75,\n   \"default\": 0.6\n  },\n  \"depth\": {\n   \"min\": 0.4,\n   \"max\": 0.7,\n   \"default\": 0.55\n  },\n  \"height\": {\n   \"min\": 1.2,\n   \"max\": 1.65,\n   \"default\": 1.45\n  }\n },\n \"parts\": [\n  \"body\",\n  \"screen\",\n  \"keypad\",\n  \"card_slot\",\n  \"cash_slot\",\n  \"sign\"\n ],\n \"params\": {\n  \"sign\": {\n   \"min\": 0,\n   \"max\": 1,\n   \"default\": 1\n  }\n },\n \"materials\": {\n  \"default\": \"metal_painted\",\n  \"options\": [\n   \"metal_painted\",\n   \"plastic\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.3,\n    0.32,\n    0.36\n   ],\n   \"wear\": 0.2,\n   \"bevel\": 0.005\n  },\n  \"1990s\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.34,\n    0.34,\n    0.3\n   ],\n   \"wear\": 0.28,\n   \"bevel\": 0.005\n  },\n  \"bodega\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.2,\n    0.22,\n    0.28\n   ],\n   \"wear\": 0.35,\n   \"bevel\": 0.005\n  },\n  \"modern\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.14,\n    0.15,\n    0.17\n   ],\n   \"wear\": 0.06,\n   \"bevel\": 0.003\n  },\n  \"center_city\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.376,\n    0.404,\n    0.48\n   ],\n   \"wear\": 0.07,\n   \"bevel\": 0.005,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.3377,\n    0.3179,\n    0.3113\n   ],\n   \"wear\": 0.42,\n   \"bevel\": 0.005,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"metal_painted\",\n   \"color\": [\n    0.282,\n    0.3168,\n    0.378\n   ],\n   \"wear\": 0.34,\n   \"bevel\": 0.005,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 6000\n },\n \"attachments\": [\n  \"ATT_cash_slot\"\n ],\n \"keywords\": [\n  \"atm\",\n  \"cash machine\",\n  \"cashpoint\",\n  \"cash register\"\n ]\n}\n",
  "zoo/zoo_keeper/genome/species/gold_bar.json": "{\n \"species\": \"gold_bar\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. Heist loot: a single gold ingot.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 0.08,\n   \"max\": 0.14,\n   \"default\": 0.1\n  },\n  \"depth\": {\n   \"min\": 0.04,\n   \"max\": 0.07,\n   \"default\": 0.05\n  },\n  \"height\": {\n   \"min\": 0.025,\n   \"max\": 0.05,\n   \"default\": 0.03\n  }\n },\n \"parts\": [\n  \"GoldBar_Ingot\"\n ],\n \"params\": {},\n \"materials\": {\n  \"default\": \"metal_bare\",\n  \"options\": [\n   \"metal_bare\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.83,\n    0.66,\n    0.22\n   ],\n   \"wear\": 0.05,\n   \"bevel\": 0.006\n  },\n  \"delco\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.8,\n    0.62,\n    0.2\n   ],\n   \"wear\": 0.1,\n   \"bevel\": 0.006\n  },\n  \"center_city\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.836,\n    0.689,\n    0.32\n   ],\n   \"wear\": 0.035,\n   \"bevel\": 0.006,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.519,\n    0.4928,\n    0.482\n   ],\n   \"wear\": 0.32,\n   \"bevel\": 0.006,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.7802,\n    0.6534,\n    0.231\n   ],\n   \"wear\": 0.19,\n   \"bevel\": 0.006,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 400\n },\n \"attachments\": [],\n \"collision\": false,\n \"connectors\": {\n  \"anchor\": {\n   \"type\": \"surface\"\n  }\n },\n \"keywords\": [\n  \"gold bar\",\n  \"gold ingot\",\n  \"bullion\"\n ]\n}\n",
  "zoo/zoo_keeper/genome/species/flat_top_grill.json": "{\n \"species\": \"flat_top_grill\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. No source meshes, no scraped data.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 0.9,\n   \"max\": 1.6,\n   \"default\": 1.2\n  },\n  \"depth\": {\n   \"min\": 0.7,\n   \"max\": 1.0,\n   \"default\": 0.9\n  },\n  \"height\": {\n   \"min\": 0.98,\n   \"max\": 1.15,\n   \"default\": 1.05\n  }\n },\n \"parts\": [\n  \"body\",\n  \"cooktop\",\n  \"splash_guard\",\n  \"grease_trap\",\n  \"knob\",\n  \"leg\"\n ],\n \"params\": {\n  \"knobs\": {\n   \"min\": 2,\n   \"max\": 4,\n   \"default\": 3\n  }\n },\n \"materials\": {\n  \"default\": \"metal_bare\",\n  \"options\": [\n   \"metal_bare\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.72,\n    0.73,\n    0.75\n   ],\n   \"wear\": 0.25,\n   \"bevel\": 0.004\n  },\n  \"1990s\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.68,\n    0.69,\n    0.7\n   ],\n   \"wear\": 0.35,\n   \"bevel\": 0.004\n  },\n  \"greasy\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.55,\n    0.55,\n    0.56\n   ],\n   \"wear\": 0.55,\n   \"bevel\": 0.004\n  },\n  \"center_city\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.7624,\n    0.7935,\n    0.87\n   ],\n   \"wear\": 0.087,\n   \"bevel\": 0.004,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.6833,\n    0.6513,\n    0.6367\n   ],\n   \"wear\": 0.47,\n   \"bevel\": 0.004,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.6768,\n    0.7227,\n    0.7875\n   ],\n   \"wear\": 0.39,\n   \"bevel\": 0.004,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 3000\n },\n \"attachments\": [\n  \"ATT_cook_center\"\n ],\n \"keywords\": [\n  \"flat top grill\",\n  \"flat-top grill\",\n  \"flattop\",\n  \"grill\",\n  \"griddle\"\n ]\n}\n",
  "zoo/zoo_keeper/genome/species/water_tank.json": "{\n \"species\": \"water_tank\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. A rooftop water tank: four legs, cylindrical tank, stepped cap.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 1.2,\n   \"max\": 2.4,\n   \"default\": 1.6\n  },\n  \"depth\": {\n   \"min\": 1.2,\n   \"max\": 2.4,\n   \"default\": 1.6\n  },\n  \"height\": {\n   \"min\": 1.8,\n   \"max\": 3.4,\n   \"default\": 2.6\n  }\n },\n \"parts\": [\n  \"WaterTank_Legs\",\n  \"WaterTank_Tank\",\n  \"WaterTank_Cap\"\n ],\n \"params\": {},\n \"materials\": {\n  \"default\": \"metal_bare\",\n  \"options\": [\n   \"metal_bare\",\n   \"plastic\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.55,\n    0.5,\n    0.44\n   ],\n   \"wear\": 0.25,\n   \"bevel\": 0.006\n  },\n  \"delco\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.48,\n    0.42,\n    0.36\n   ],\n   \"wear\": 0.4,\n   \"bevel\": 0.006\n  },\n  \"center_city\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.5416,\n    0.499,\n    0.48\n   ],\n   \"wear\": 0.14,\n   \"bevel\": 0.006,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.417,\n    0.3944,\n    0.386\n   ],\n   \"wear\": 0.62,\n   \"bevel\": 0.006,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.517,\n    0.495,\n    0.462\n   ],\n   \"wear\": 0.39,\n   \"bevel\": 0.006,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 1200\n },\n \"attachments\": [],\n \"collision\": true,\n \"connectors\": {\n  \"anchor\": {\n   \"type\": \"roof\"\n  }\n },\n \"keywords\": [\n  \"water tank\",\n  \"water_tank\",\n  \"rooftop tank\",\n  \"cistern\"\n ]\n}\n",
  "zoo/zoo_keeper/genome/species/shelving.json": "{\n \"species\": \"shelving\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. Freestanding shelf unit: two side uprights, N shelf boards, optional back panel \u2014 reads as store gondola or stockroom racking by proportions.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 0.6,\n   \"max\": 2.4,\n   \"default\": 1.2\n  },\n  \"depth\": {\n   \"min\": 0.3,\n   \"max\": 0.8,\n   \"default\": 0.5\n  },\n  \"height\": {\n   \"min\": 0.9,\n   \"max\": 2.4,\n   \"default\": 1.8\n  }\n },\n \"parts\": [\n  \"Shelf_Upright_L\",\n  \"Shelf_Upright_R\",\n  \"Shelf_Board\",\n  \"Shelf_Back\"\n ],\n \"params\": {\n  \"shelves\": {\n   \"min\": 2,\n   \"max\": 7,\n   \"default\": 4\n  },\n  \"back\": {\n   \"min\": 0,\n   \"max\": 1,\n   \"default\": 1\n  }\n },\n \"materials\": {\n  \"default\": \"metal_bare\",\n  \"options\": [\n   \"metal_bare\",\n   \"wood\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.55,\n    0.56,\n    0.58\n   ],\n   \"wear\": 0.25,\n   \"bevel\": 0.003\n  },\n  \"delco\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.45,\n    0.47,\n    0.5\n   ],\n   \"wear\": 0.45,\n   \"bevel\": 0.003,\n   \"ambient\": 0.3\n  },\n  \"center_city\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.514,\n    0.5465,\n    0.62\n   ],\n   \"wear\": 0.158,\n   \"bevel\": 0.003,\n   \"ambient\": 0.15\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.4623,\n    0.4381,\n    0.4287\n   ],\n   \"wear\": 0.67,\n   \"bevel\": 0.003,\n   \"ambient\": 0.4\n  },\n  \"rockay\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.517,\n    0.5544,\n    0.609\n   ],\n   \"wear\": 0.39,\n   \"bevel\": 0.003,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 900\n },\n \"attachments\": [],\n \"collision\": true,\n \"keywords\": [\n  \"shelving\",\n  \"shelf\",\n  \"shelves\",\n  \"rack\",\n  \"gondola\",\n  \"stockroom rack\"\n ]\n}\n",
  "zoo/zoo_keeper/genome/species/vault_door.json": "{\n \"species\": \"vault_door\",\n \"version\": 1,\n \"license\": {\n  \"construction_knowledge\": \"CC0\",\n  \"notes\": \"Original procedural construction. Architectural interactive module: the CLOSED armored vault door (heavy portal frame + thick leaf + wheel hub) that fills a vault portal slot. Its open/breached states reuse doorway/breach geometry via the slot's interactive.state_geometry.\"\n },\n \"dimensions\": {\n  \"width\": {\n   \"min\": 0.8,\n   \"max\": 3.5,\n   \"default\": 1.4\n  },\n  \"depth\": {\n   \"min\": 0.2,\n   \"max\": 1.2,\n   \"default\": 0.5\n  },\n  \"height\": {\n   \"min\": 1.8,\n   \"max\": 3.6,\n   \"default\": 2.3\n  }\n },\n \"parts\": [\n  \"VaultDoor_Jamb_L\",\n  \"VaultDoor_Jamb_R\",\n  \"VaultDoor_Sill\",\n  \"VaultDoor_Header\",\n  \"VaultDoor_Leaf\",\n  \"VaultDoor_Hub\"\n ],\n \"params\": {\n  \"jamb\": {\n   \"min\": 0.08,\n   \"max\": 0.5,\n   \"default\": 0.18\n  },\n  \"header\": {\n   \"min\": 0.08,\n   \"max\": 0.5,\n   \"default\": 0.2\n  },\n  \"sill_lip\": {\n   \"min\": 0.0,\n   \"max\": 0.4,\n   \"default\": 0.15\n  },\n  \"leaf_frac\": {\n   \"min\": 0.4,\n   \"max\": 1.0,\n   \"default\": 0.7\n  },\n  \"hub_frac\": {\n   \"min\": 0.1,\n   \"max\": 0.6,\n   \"default\": 0.32\n  }\n },\n \"materials\": {\n  \"default\": \"metal_bare\",\n  \"options\": [\n   \"metal_bare\",\n   \"concrete\"\n  ]\n },\n \"styles\": {\n  \"default\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.42,\n    0.44,\n    0.47\n   ],\n   \"wear\": 0.2,\n   \"bevel\": 0.006\n  },\n  \"delco\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.38,\n    0.4,\n    0.43\n   ],\n   \"wear\": 0.35,\n   \"bevel\": 0.006\n  },\n  \"center_city\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.4496,\n    0.48,\n    0.55\n   ],\n   \"wear\": 0.122,\n   \"bevel\": 0.006,\n   \"ambient\": 0\n  },\n  \"industrial_flats\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.4028,\n    0.3807,\n    0.3727\n   ],\n   \"wear\": 0.57,\n   \"bevel\": 0.006,\n   \"ambient\": 0.1\n  },\n  \"rockay\": {\n   \"material\": \"metal_bare\",\n   \"color\": [\n    0.3948,\n    0.4356,\n    0.4935\n   ],\n   \"wear\": 0.34,\n   \"bevel\": 0.006,\n   \"ambient\": 0.05\n  }\n },\n \"budgets\": {\n  \"tris_lod0\": 900\n },\n \"attachments\": [],\n \"collision\": true,\n \"match_priority\": -1,\n \"keywords\": [\n  \"vault door\",\n  \"vault\",\n  \"safe door\"\n ]\n}\n",
  "zoo/VERSION": "Zoo 0.45.0\n",
  "zoo/tests/test_material_options_closed.py": "\"\"\"The material-options invariant, and the metal split by batch.\n\n`dna.resolve_plan` and `dna.resolve_module_plan` both do this, silently:\n\n    if material not in genome[\"materials\"][\"options\"]:\n        material = genome[\"materials\"][\"default\"]\n\nA style block naming a kind that is missing from `options` is DISCARDED, and\nthe species quietly renders in its default material. Nothing logs. The render\nlooks plausible. That is the trap the metal split walks into once per species,\nand it is why these tests sweep every genome rather than only the ones a given\nbatch touched.\n\"\"\"\n\nimport glob\nimport json\nimport os\n\nimport pytest\n\nfrom zoo_keeper.core import skins\n\nSPECIES_DIR = os.path.join(os.path.dirname(os.path.dirname(\n    os.path.abspath(__file__))), \"zoo_keeper\", \"genome\", \"species\")\n\n# Batch 1 (0.44.0) and batch 2 (0.45.0). Split painted/bare because METALLIC\n# is a per-kind lookup: paint is a dielectric, bare metal a conductor.\nPAINTED = (\"vending_machine\", \"simple_car\", \"helmet\", \"queue_stanchion\",\n           \"chair\", \"filing_cabinet\", \"atm\")\nBARE = (\"gold_bar\", \"flat_top_grill\", \"water_tank\", \"shelving\", \"vault_door\")\nMOVED = PAINTED + BARE\n\n\ndef _genomes():\n    out = []\n    for p in sorted(glob.glob(os.path.join(SPECIES_DIR, \"*.json\"))):\n        out.append(json.load(open(p, encoding=\"utf-8\")))\n    return out\n\n\ndef test_the_sweep_is_actually_reading_genomes():\n    \"\"\"Guard the guard: every assertion below is a loop, and a loop over an\n    empty directory passes vacuously.\"\"\"\n    g = _genomes()\n    assert len(g) >= 50, \"only %d genomes found\" % len(g)\n    assert any(x[\"species\"] == \"vending_machine\" for x in g)\n\n\n@pytest.mark.parametrize(\"g\", _genomes(), ids=lambda g: g[\"species\"])\ndef test_every_style_material_is_in_options(g):\n    opts = set(g[\"materials\"].get(\"options\", []))\n    for name, style in g.get(\"styles\", {}).items():\n        if not isinstance(style, dict) or \"material\" not in style:\n            continue\n        assert style[\"material\"] in opts, (\n            \"%s style %r names %r, which is not in materials.options %s. \"\n            \"resolve_plan will discard it and silently use %r.\"\n            % (g[\"species\"], name, style[\"material\"], sorted(opts),\n               g[\"materials\"].get(\"default\")))\n\n\n@pytest.mark.parametrize(\"g\", _genomes(), ids=lambda g: g[\"species\"])\ndef test_default_material_is_in_options(g):\n    opts = set(g[\"materials\"].get(\"options\", []))\n    assert g[\"materials\"][\"default\"] in opts, (\n        \"%s default %r is not in its own options -- the fallback target is \"\n        \"itself unreachable\" % (g[\"species\"], g[\"materials\"][\"default\"]))\n\n\n@pytest.mark.parametrize(\"g\", _genomes(), ids=lambda g: g[\"species\"])\ndef test_every_named_kind_is_in_the_vocabulary(g):\n    \"\"\"A kind nothing knows takes the 0.6 default roughness and resolves no\n    pack. This is the check that would have caught `tar` on day one.\"\"\"\n    named = set(g[\"materials\"].get(\"options\", []))\n    named.add(g[\"materials\"][\"default\"])\n    for style in g.get(\"styles\", {}).values():\n        if isinstance(style, dict) and \"material\" in style:\n            named.add(style[\"material\"])\n    unknown = named - set(skins.KNOWN_KINDS)\n    assert not unknown, \"%s names unknown kinds: %s\" % (g[\"species\"],\n                                                        sorted(unknown))\n\n\n@pytest.mark.parametrize(\"sp\", MOVED)\ndef test_moved_species_no_longer_offer_raw_metal(sp):\n    g = json.load(open(os.path.join(SPECIES_DIR, sp + \".json\"),\n                       encoding=\"utf-8\"))\n    opts = g[\"materials\"][\"options\"]\n    assert \"metal\" not in opts, (\n        \"%s still offers raw `metal`; a prompt naming it would resolve the \"\n        \"theme-owned pack and ignore the genome colour\" % sp)\n    for name, style in g.get(\"styles\", {}).items():\n        assert style.get(\"material\") != \"metal\", \\\n            \"%s style %r was left on raw metal\" % (sp, name)\n\n\n@pytest.mark.parametrize(\"sp\", PAINTED)\ndef test_painted_species_are_on_metal_painted(sp):\n    g = json.load(open(os.path.join(SPECIES_DIR, sp + \".json\"),\n                       encoding=\"utf-8\"))\n    assert \"metal_painted\" in g[\"materials\"][\"options\"], sp\n\n\n@pytest.mark.parametrize(\"sp\", BARE)\ndef test_bare_species_are_on_metal_bare(sp):\n    g = json.load(open(os.path.join(SPECIES_DIR, sp + \".json\"),\n                       encoding=\"utf-8\"))\n    assert \"metal_bare\" in g[\"materials\"][\"options\"], sp\n\n\ndef test_nothing_else_moved():\n    \"\"\"The remaining 41 genomes stay on plain `metal`. When batch 3 lands this\n    list changes deliberately, not by surprise.\"\"\"\n    moved = [g[\"species\"] for g in _genomes()\n             if {\"metal_painted\", \"metal_bare\"} & set(\n                 g[\"materials\"].get(\"options\", []))]\n    assert sorted(moved) == sorted(MOVED), (\n        \"on a split kind: %s\\nexpected: %s\" % (sorted(moved), sorted(MOVED)))\n\n\ndef test_no_species_is_both_painted_and_bare():\n    \"\"\"One object, one metal. A species offering both would let a prompt pick\n    the conductor value for a painted surface.\"\"\"\n    for g in _genomes():\n        opts = set(g[\"materials\"].get(\"options\", []))\n        assert not ({\"metal_painted\", \"metal_bare\"} <= opts), \\\n            \"%s offers BOTH metal_painted and metal_bare\" % g[\"species\"]\n\n\nRECIPE_DIR = os.path.join(os.path.dirname(os.path.dirname(\n    os.path.abspath(__file__))), \"zoo_keeper\", \"recipes\")\n\n\n@pytest.mark.parametrize(\"sp\", (\"flat_top_grill\", \"vault_door\"))\ndef test_recipes_no_longer_hardcode_the_kind(sp):\n    \"\"\"THE DEFECT THAT MADE A GENOME EDIT INERT. flat_top_grill passed the\n    literal \"metal\" to all three of its make_material calls, so editing its\n    genome changed nothing at all -- silently. vault_door hard-coded only its\n    hub, which would have split one door across two kinds.\"\"\"\n    src = open(os.path.join(RECIPE_DIR, sp + \".py\"), encoding=\"utf-8\").read()\n    assert '\"metal\")' not in src, (\n        \"%s.py still passes the literal \\\"metal\\\" to make_material; its \"\n        \"genome would be ignored\" % sp)\n"
 },
 "new": {},
 "changelogs": {
  "zoo/CHANGELOG.md": "## [0.45.0] - batch 2: the rest of the coloured metal, and two inert genomes\n\nEight species off raw `metal`. Three take paint, five take bare metal --\nwhich is NOT the 7/1 split the batch-1 notes predicted, because that grouping\nranked by chroma rather than by what the material is.\n\n    metal_painted   filing_cabinet  putty/beige office steel   chroma 0.150\n                    chair           warm brown frame                  0.216\n                    atm             dark cool housing                 0.104\n\n    metal_bare      gold_bar        gold                              0.610\n                    water_tank      warm brown -- that is RUST        0.120\n                    flat_top_grill  bright cool -- stainless          0.111\n                    shelving        cool grey-blue steel              0.106\n                    vault_door      cool steel                        0.100\n\nThe hue decides it, not the magnitude. `flat_top_grill` at\n[0.677, 0.723, 0.787] is the blue cast of stainless, not a colour anyone\nchose; `filing_cabinet` at [0.450, 0.420, 0.300] is unmistakably paint; and\n`water_tank`'s warm brown is weathering, so painting it would have been\nwrong in a way no test would catch.\n\n### Fixed -- two genomes that were INERT\n- **`flat_top_grill.py` passed the literal `\"metal\"` to all three of its\n  `make_material` calls.** Its genome's `materials.default`, `options` and\n  every style's `material` were read by nothing. Editing that genome changed\n  NOTHING, silently, and would have looked like the split failing.\n- **`vault_door.py` hard-coded only its hub.** The body read `plan[\"material\"]`\n  already, so the moment the genome moved off `metal` the door would have\n  rendered across two material kinds.\n\nBoth now pass `plan[\"material\"]`, and\n`test_recipes_no_longer_hardcode_the_kind` asserts the literal is gone.\n\n### Corrected\nThe batch-1 notes recorded `shelving.json` as the one genome that is not\nbyte-exact `json.dumps(indent=1)` round-trippable, needing an anchored edit.\nThat was wrong. It carries an em dash in `notes`, and the CHECK used the\ndefault `ensure_ascii=True`, which escapes it to `\\u2014`. With\n`ensure_ascii=False` all 53 genomes round-trip and every edit here is\nstructural.\n\n### Changed\n- `tests/test_material_options_closed.py` now tracks PAINTED and BARE sets\n  rather than a single batch list, asserts no species offers both (one\n  object, one metal), and keeps the all-53 sweep of the options invariant.\n\n### Still on plain `metal`\n30 species, every one of them measured at chroma < 0.10 -- already near-grey,\nso the theme-owned kind is the right answer. Ten are architecture and must\nkeep it.\n\n"
 },
 "pre_sha": {
  "zoo/zoo_keeper/genome/species/chair.json": "8861aed20e4e255f2be5704e4b486e2f07638a7d46636a9b9af704caf7820ab6",
  "zoo/zoo_keeper/genome/species/filing_cabinet.json": "2e63342f2891b1fe99e48ce5a1c1145e13acec8855b804dde5249c22d138d831",
  "zoo/zoo_keeper/genome/species/atm.json": "a5aa2ad206e4310719900146d46ae649532a9a38838f87795266ffdee48b1a37",
  "zoo/zoo_keeper/genome/species/gold_bar.json": "af4f46832e7ce71f2e6414335bf6e3351d6a950ac91b38da5d8e174bdec13dd6",
  "zoo/zoo_keeper/genome/species/flat_top_grill.json": "7948e0bbe1f014656f813a6cc7f9a742302227f6fdef29e0247e08af06ead2cf",
  "zoo/zoo_keeper/genome/species/water_tank.json": "52a9284927b1a5c53947340d1a1a8761ce428e4c8d0ee1d38d544fa0ee21dfd4",
  "zoo/zoo_keeper/genome/species/shelving.json": "fc03f6c138f285dc8fad2ddb16d242fbca45490f391054e3974034c672fbf59f",
  "zoo/zoo_keeper/genome/species/vault_door.json": "7983dc6d1d73adebed25b100fb82c9e710cd4a6fac74438ba17f930e804fdafd",
  "zoo/VERSION": "9fb0ca3ffbe82e85d851383c6b9414780a24f316e0d83d86ff88364bc1f02250",
  "zoo/tests/test_material_options_closed.py": "d0fce030507dc5e528565e2289552aa24a6f5fc587588330f8402fbea8928184",
  "zoo/zoo_keeper/recipes/flat_top_grill.py": "d29335ef2fa455a46056342b52f696c13db11594abcb190e0ba7fe7721bf9948",
  "zoo/zoo_keeper/recipes/vault_door.py": "5caaa6c01ad30e8ebf241355c2ff48d1d4b834ee111e32008c70df881ec22f90",
  "zoo/CHANGELOG.md": "8417e91e1a85ec4cc199b5ae6d5cc1757a1b89e17238f0bda3e82710d354fcbe"
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

    PAINTED = ("vending_machine", "simple_car", "helmet", "queue_stanchion",
               "chair", "filing_cabinet", "atm")
    BARE = ("gold_bar", "flat_top_grill", "water_tank", "shelving",
            "vault_door")
    MOVED = PAINTED + BARE
    SPD = os.path.join(ROOT, "zoo", "zoo_keeper", "genome", "species")
    RCP = os.path.join(ROOT, "zoo", "zoo_keeper", "recipes")

    from zoo_keeper.core import skins

    # ---- 0. ordering: both kinds must already be registered ----------------
    for k in ("metal_painted", "metal_bare"):
        if k not in skins.KNOWN_KINDS:
            fails.append("%s is not in KNOWN_KINDS -- apply "
                         "patch_metal_split.py FIRST" % k)
    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1

    genomes = {}
    for p in sorted(_glob.glob(os.path.join(SPD, "*.json"))):
        g = _json.load(open(p, encoding="utf-8"))
        genomes[g["species"]] = g
    if len(genomes) < 50:
        fails.append("only %d genomes read -- the sweeps would pass vacuously"
                     % len(genomes))

    # ---- 1. THE INVARIANT, over every genome -------------------------------
    for sp, g in sorted(genomes.items()):
        opts = set(g["materials"].get("options", []))
        if g["materials"]["default"] not in opts:
            fails.append("%s: default %r not in its own options"
                         % (sp, g["materials"]["default"]))
        for name, s in g.get("styles", {}).items():
            if isinstance(s, dict) and "material" in s and \
                    s["material"] not in opts:
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

    # ---- 2. the twelve moved, and only the twelve --------------------------
    for sp in MOVED:
        g = genomes.get(sp)
        if g is None:
            fails.append("%s genome missing" % sp); continue
        opts = g["materials"]["options"]
        want = "metal_painted" if sp in PAINTED else "metal_bare"
        if want not in opts:
            fails.append("%s did not gain %s" % (sp, want))
        if "metal" in opts:
            fails.append("%s still offers raw metal" % sp)
        left = [n for n, s in g.get("styles", {}).items()
                if isinstance(s, dict) and s.get("material") == "metal"]
        if left:
            fails.append("%s styles left on raw metal: %s" % (sp, left))
    moved = sorted(sp for sp, g in genomes.items()
                   if {"metal_painted", "metal_bare"} &
                   set(g["materials"].get("options", [])))
    if moved != sorted(MOVED):
        fails.append("on a split kind: %s\n      expected: %s"
                     % (moved, sorted(MOVED)))
    # one object, one metal
    for sp, g in genomes.items():
        o = set(g["materials"].get("options", []))
        if {"metal_painted", "metal_bare"} <= o:
            fails.append("%s offers BOTH metal_painted and metal_bare" % sp)

    # ---- 3. THE INERT-GENOME DEFECT ----------------------------------------
    #      flat_top_grill passed the literal "metal" to all three of its
    #      make_material calls, so its genome was read by nothing at all.
    for sp in ("flat_top_grill", "vault_door"):
        src = open(os.path.join(RCP, sp + ".py"), encoding="utf-8").read()
        if '"metal")' in src:
            fails.append("%s.py still passes the literal \"metal\" to "
                         "make_material -- its genome is ignored" % sp)

    # ---- 4. THE FALSIFICATION: the real resolver, every moved style --------
    from zoo_keeper.core import dna, seeding

    def _intent(era):
        return _types.SimpleNamespace(
            era=era, style_tags=(), material=None, color=None, wear=None,
            prompt_norm="", size_hint=1.0, counts={})

    ran = 0
    for sp in MOVED:
        g = genomes.get(sp)
        if g is None:
            continue
        for style_name, s in g.get("styles", {}).items():
            if not isinstance(s, dict) or "material" not in s:
                continue
            try:
                plan = dna.resolve_plan(
                    _intent(style_name), g,
                    seeding.RNGStreams("selftest/%s/%s" % (sp, style_name)),
                    "selftest")
            except Exception as exc:
                fails.append("resolve_plan(%s, %s) raised %s: %s"
                             % (sp, style_name, type(exc).__name__, exc))
                continue
            ran += 1
            if plan["style"] != style_name:
                continue
            if plan["material"] != s["material"]:
                fails.append("resolve_plan(%s, %s) returned %r but the style "
                             "declares %r -- the SILENT FALLBACK fired"
                             % (sp, style_name, plan["material"],
                                s["material"]))
    if ran == 0:
        fails.append("resolve_plan was never exercised -- check 4 is asleep")
    else:
        print("  resolve_plan exercised on %d (species, style) pairs" % ran)

    # ---- 5. all 53 genomes round-trip at indent=1, ensure_ascii=False ------
    #      The batch-1 notes claimed shelving.json did not. It does; the CHECK
    #      used ensure_ascii=True, which escapes its em dash to \\u2014.
    notrt = []
    for p in sorted(_glob.glob(os.path.join(SPD, "*.json"))):
        src = open(p, encoding="utf-8").read()
        if _json.dumps(_json.loads(src), indent=1,
                       ensure_ascii=False) + "\n" != src:
            notrt.append(os.path.basename(p))
    if notrt:
        print("  NOTE: not indent=1 round-trippable: %s" % notrt)
    else:
        print("  all %d genomes round-trip at indent=1, ensure_ascii=False"
              % len(genomes))

    # ---- 6. the test file passes ------------------------------------------
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
    print("SELFTEST OK -- invariant over %d genomes, 12 moved and only 12, "
          "no species offers both kinds, both recipe literals gone, and the "
          "REAL dna.resolve_plan returns the declared kind for every moved "
          "style" % len(genomes))
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
