"""Deli Counter 0.284.0: a placed piece asks Zoo for a material its species is made of. Run in a Deli Counter clone's
root (on 0.283.0). Every anchor is asserted to occur exactly once; nothing is written on a miss.
"""
import pathlib

HERE = pathlib.Path(__file__).parent
R = pathlib.Path.cwd()


def edit(rel, pairs):
    p = R / rel
    t = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n")
    for a, b in pairs:
        assert t.count(a) == 1, (rel, t.count(a), a[:80])
        t = t.replace(a, b)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print(p, "edited")


MIRROR = "SPECIES_MATERIALS = {\n    'aisle_sign': ('wood', ('wood', 'paper', 'plastic', 'metal_painted')),\n    'atm': ('metal_painted', ('metal_painted', 'plastic')),\n    'back_bar': ('wood_stained', ('wood_stained', 'wood', 'laminate')),\n    'bar_stool': ('metal_bare', ('metal_bare', 'wood')),\n    'booth_seat': ('leather', ('leather', 'canvas', 'plastic')),\n    'cargo_container': ('metal_painted', ('metal_painted', 'plastic')),\n    'carton_stack': ('paper', ('paper',)),\n    'cash_cart': ('metal_bare', ('metal_bare',)),\n    'ceiling_hanger': ('paper', ('paper', 'plastic', 'wood', 'metal_painted')),\n    'chair': ('wood', ('wood', 'metal_painted', 'plastic', 'leather')),\n    'check_desk': ('wood', ('concrete', 'metal', 'wood', 'plaster')),\n    'cigarette_machine': ('metal_painted', ('metal_painted', 'wood_stained')),\n    'club_chair': ('wood', ('wood',)),\n    'club_stage': ('wood', ('wood', 'laminate')),\n    'cocktail_table': ('wood', ('wood', 'laminate')),\n    'coffee_island': ('metal', ('metal',)),\n    'cooler_run': ('metal_painted', ('metal_painted', 'glass')),\n    'counter': ('wood', ('wood', 'laminate', 'metal')),\n    'crowd_barrier': ('metal_bare', ('metal_bare',)),\n    'crt_tv': ('plastic', ('plastic', 'wood', 'metal')),\n    'cubicle_bank': ('cloth', ('cloth', 'canvas', 'velvet')),\n    'dartboard': ('wood_stained', ('wood_stained', 'metal_painted', 'wood')),\n    'deli_case': ('metal_painted', ('metal_painted', 'glass')),\n    'desk': ('laminate', ('laminate', 'wood', 'metal')),\n    'display_case': ('laminate', ('laminate', 'wood', 'wood_panel', 'metal_painted')),\n    'drop_safe': ('metal_painted', ('metal_painted',)),\n    'dust_sheet': ('canvas', ('canvas',)),\n    'filing_cabinet': ('metal_painted', ('metal_painted', 'wood', 'laminate')),\n    'flat_top_grill': ('metal_bare', ('metal_bare',)),\n    'folding_chair': ('plastic', ('plastic', 'metal_painted', 'wood', 'laminate')),\n    'folding_table': ('plastic', ('plastic', 'laminate', 'wood', 'metal_painted')),\n    'furnace': ('metal_painted', ('metal_painted',)),\n    'hanging_banner': ('cloth', ('cloth', 'canvas', 'plastic', 'paper')),\n    'hvac_unit': ('metal', ('metal', 'plastic')),\n    'litter_bin': ('metal_painted', ('metal_painted',)),\n    'milk_crate_stack': ('plastic', ('plastic',)),\n    'neon_sign': ('metal_painted', ('metal_painted', 'wood')),\n    'pack_wall': ('metal_painted', ('metal_painted', 'laminate', 'wood_panel', 'slatwall')),\n    'pallet_stack': ('wood', ('wood',)),\n    'payphone': ('metal_painted', ('metal_painted', 'plastic')),\n    'pennant_row': ('cloth', ('cloth', 'canvas', 'velvet')),\n    'pew': ('wood', ('concrete', 'metal', 'wood', 'plaster')),\n    'planter': ('plaster', ('plaster', 'concrete', 'plastic')),\n    'pool_table': ('wood', ('wood', 'laminate')),\n    'poster': ('metal_bare', ('metal_bare', 'wood', 'plastic')),\n    'poster_wall': ('paper', ('paper',)),\n    'produce_table': ('wood', ('concrete', 'metal', 'wood', 'plaster')),\n    'pump': ('metal_painted', ('metal_painted',)),\n    'queue_stanchion': ('metal_painted', ('metal_painted',)),\n    'roller_grill': ('metal_bare', ('metal_bare', 'glass')),\n    'security_camera': ('plastic', ('plastic', 'metal')),\n    'shelving': ('metal_bare', ('metal_bare', 'wood')),\n    'slush_machine': ('metal_painted', ('metal_painted', 'glass')),\n    'snack_gondola': ('metal_painted', ('metal_painted',)),\n    'stanchion_run': ('metal_painted', ('metal_painted',)),\n    'stoop_railing': ('metal_painted', ('metal_painted',)),\n    'table': ('wood', ('wood', 'laminate', 'metal')),\n    'teller_line': ('metal', ('metal', 'laminate', 'concrete', 'wood')),\n    'vending_machine': ('metal_painted', ('metal_painted', 'plastic')),\n    'video_poker': ('metal_painted', ('metal_painted',)),\n    'video_rack': ('metal_painted', ('metal_painted',)),\n    'wall_clock': ('plastic', ('plastic', 'metal_painted')),\n    'water_barrel': ('plastic', ('plastic',)),\n    'water_tank': ('metal_bare', ('metal_bare', 'plastic')),\n    'window_drape': ('velvet', ('velvet',)),\n}\n"

edit("prop_species.py", [
('''def species_for_name(name):''',
 '''#: WHAT EACH ROUTED SPECIES IS MADE OF (0.284.0): Zoo's genome `materials`, ``{species: (default, options)}``,
#: mirrored because Deli Counter does not read Zoo; `tests/test_species_materials.py` holds it to Zoo's genomes when
#: Zoo is beside the repo. Zoo builds ANY known kind a slot names, options or not (`dna.resolve_module_plan`), and
#: delco_1997 maps `metal` to `metal_rusted_street`: measured on the bank level's kit, the ATM was built
#: `_mmetal`, rust, and the cash cart, the camera, the clock and the planter `_mwood` -- the slots asked for the
#: name table's row or its `wood` default. Across the library's built slots 2,800 asked for a kind their species
#: does not offer: ATMs, vending machines, litter bins, filing cabinets, furnaces, payphones and queue stanchions
#: in street rust, cartons in wood rather than paper, dust sheets in wood rather than canvas.
''' + MIRROR + '''

def material_for(species, asked):
    """The kind a slot of ``species`` asks Zoo for: ``asked`` when the species is made of it, else the species' own
    default. A box (no species) and a species not mirrored keep ``asked``."""
    row = SPECIES_MATERIALS.get(species)
    if row is None or asked in row[1]:
        return asked
    return row[0]


def species_for_name(name):'''),
])

edit("deli_counter.py", [
('''                    "material": rmat, "species": "stoop_railing", "stock": None, "variant": 0,''',
 '''                    # the rail a species offers (0.284.0): a wood stair's guard is a steel pipe rail
                    "material": prop_species.material_for("stoop_railing", rmat), "species": "stoop_railing",
                    "stock": None, "variant": 0,'''),
('''                    "material": v.material or self.s.default_material,
                    "species": species,''',
 '''                    # a kind the species is made of, else its own (0.284.0, `prop_species.material_for`)
                    "material": prop_species.material_for(species, v.material or self.s.default_material),
                    "species": species,'''),
])

dst = R / "tests" / "test_species_materials.py"
assert not dst.exists(), dst
dst.write_bytes((HERE / "test_species_materials.py").read_bytes())
print(dst, "written")
