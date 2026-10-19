# Cold run 9322 -- urban_row_001 on Level Factory 0.217.0 (2026-10-19): the vault ledges are skinned, and the themed package carries no greybox

Staged from 9321. The only tool change between them is Level Factory 0.217.0 (31cc75c): `zoo_worldskin.gd` skins a
vault ledge, with the building's drywall wall first, then any wall, then its floor family. It is also the first
cold run whose clean job applied `tools/factory_retire.py --pushed-only` (the root's 884a141).

**Run:** 0 interventions (journal 0, unattributed files 0), drive exit 0. The pick is seed 9104 again, PASS 100,
route completion 1.00, 0 major -- the same pick and grade as 9317, 9318, 9320 and 9321. Findings 109 -> 109
against 9321. The package shipped with the closure verdict clean and its four nav links: two drops, two climbs.

**The census** (`greybox_skin_scan.json`, kept here):

    themed True   greybox surfaces 0   slabs 0   by role: none        (9321 on 0.216.1: gb_floor 3, the vault ledges)

That is the first themed package with no greybox surface at all. Every class roadmap 168 named now has an owner:
ladders a worldskin pass (Level Factory 0.136.0), roof parapets wall slots (Deli Counter 0.177.0), and vault
ledges a worldskin pass (0.217.0). The drop-edge gate still reads 20 at a declared drop and 0 undeclared.

**The clean job** took two workspaces, 2.7 GB, both with pushed records: cold-9314-ws, which records name, and
cold-9318-ws, now beyond the newest four. The drop-edge finding re-reads 9318 from its own
`gate_9318_inputs/`, so nothing that still reads a workspace lost it.

Next: Level Factory 0.218.0 makes the census refuse any greybox surface in a themed package, behind
`ExportProfile.require_no_greybox`. This package is the zero it rests on.
