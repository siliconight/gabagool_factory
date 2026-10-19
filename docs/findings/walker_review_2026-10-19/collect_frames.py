"""Collect the review's frames into one folder as JPEGs with stable names, for the review page to publish. A copier:
it converts each listed PNG, refuses a source that is missing, and prints what it wrote.

    python collect_frames.py <out dir>

Sources are this session's look_shots runs under the factory's _scratch/review/ (fresh, 2026-10-19) and frames the
roadmap items already cite under docs/. Each output is at most 1280 px wide, JPEG quality 84.
"""
import sys
from pathlib import Path

from PIL import Image

F = Path(__file__).resolve().parents[3]
R = F / "_scratch" / "review"
FRAMES = {
    # restaurant_row_001, cold run 9335, evening, clear
    "r_cars_row": R / "shots_9335/cars_row.png",
    "r_cars_lot": R / "shots_9335/cars_lot.png",
    "r_drain_level": R / "shots_9335b/drain_inlet_close.png",
    "r_drain_inspect": R / "shots_9335i/INSPECT_studio_drain_inlet_close.png",
    "r_drain_road_inspect": R / "shots_9335i/INSPECT_studio_drain_road_top.png",
    "r_edge_south": R / "shots_9335/edge_south.png",
    "r_edge_corner": R / "shots_9335/edge_corner.png",
    "r_edge_gap": R / "shots_9335b/edge_gap.png",
    "r_payphone_back_level": R / "shots_9335b/payphone_17_front.png",
    "r_payphone_back_inspect": R / "shots_9335i/INSPECT_studio_payphone_17_front.png",
    "r_payphone_face_inspect": R / "shots_9335p/INSPECT_studio_payphone_17_behind.png",
    "r_payphone_side_level": R / "shots_9335b/payphone_17_side.png",
    "r_room_deli_aisles": R / "shots_9335r/deli_market_aisles.png",
    "r_room_deli_kitchen": R / "shots_9335r/deli_kitchen.png",
    "r_room_deli_stock": R / "shots_9335r/deli_stockroom_loading.png",
    "r_room_rx_counter": R / "shots_9335r/pharmacy_rx_counter.png",
    "r_room_rx_vault": R / "shots_9335r/pharmacy_rx_vault.png",
    "r_room_office_lobby": R / "shots_9335r/office_lobby.png",
    "r_room_office_bullpen": R / "shots_9335r/office_ground_bullpen.png",
    "r_wall_drywall": R / "shots_9335b/in_drywall_delco_1997_3.png",
    "r_wall_concrete": R / "shots_9335/in_concrete_delco_1997.png",
    "r_spawn": R / "shots_9335/spawn.png",
    "r_extraction": R / "shots_9335/extraction.png",
    # urban_row_001, cold run 9336, evening, clear
    "u_street_wall": R / "shots_9336/street_wall.png",
    "u_skyline": R / "shots_9336/skyline.png",
    "u_awning_west": R / "shots_9336/awning_west.png",
    "u_awning_east": R / "shots_9336/awning_east.png",
    "u_street_long": R / "shots_9336/street_long.png",
    "u_pole_line": R / "shots_9336/pole_line.png",
    "u_fire_escape_inspect": R / "shots_9336i/INSPECT_studio_fire_escape.png",
    "u_fire_escape_close_inspect": R / "shots_9336i/INSPECT_studio_fire_escape_close.png",
    "u_street_furniture_inspect": R / "shots_9336i/INSPECT_studio_south_stoops.png",
    "u_awning_inspect": R / "shots_9336i/INSPECT_studio_awning_west.png",
    "u_roofs_inspect": R / "shots_9336i/INSPECT_studio_roofs_raised.png",
    # county_hospital_001, cold run 9334, night, rain
    "h_rain_street": R / "shots_9334/rain_street.png",
    "h_tree_campus": R / "shots_9334/tree_campus.png",
    "h_payphone_face_level": R / "shots_9334/payphone_b.png",
    "h_payphone_face_inspect": R / "shots_9334i/INSPECT_studio_payphone_b.png",
    # frames the roadmap items already cite
    "x_hatch_climber": F / "docs/cold_runs/cold_9316/hatch_frames/hatch_climber_side.png",
    "x_hatch_above": F / "docs/cold_runs/cold_9316/hatch_frames/hatch_from_above.png",
    "x_hatch_hinge": F / "docs/cold_runs/cold_9316/hatch_frames/hatch_hinge_side.png",
    "x_edge_9230": F / "docs/cold_runs/cold_9230/edge_before_after.png",
    "x_atlas_9274": F / "docs/cold_runs/cold_9274/atlas.png",
    "x_shadow_options": F / "docs/findings/pole_line/shadow_options.png",
    "x_corner_9295": F / "docs/findings/urban_street/ab_9295/corner_sheet.png",
    "x_corner_9297": F / "docs/findings/urban_street/ab_9297/corner_sheet.png",
    "x_skyline_9292": F / "docs/findings/urban_street/ab_9292/skyline_sheet.png",
    "x_walkups_9303": F / "docs/findings/fire_escape/walkups_9303_sheet.png",
}
EXTRA = {}
if len(sys.argv) > 2:
    # name=path pairs added at the command line (the clear night's frames, shot after this list was written)
    for a in sys.argv[2:]:
        k, _, v = a.partition("=")
        EXTRA[k] = Path(v)

out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
missing = [k for k, p in {**FRAMES, **EXTRA}.items() if not p.is_file()]
if missing:
    raise SystemExit("MISSING: " + ", ".join(missing))
total = 0
for k, p in {**FRAMES, **EXTRA}.items():
    im = Image.open(p).convert("RGB")
    if im.width > 1280:
        im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
    dst = out / (k + ".jpg")
    im.save(dst, quality=84, optimize=True)
    total += dst.stat().st_size
print("wrote %d frames, %.1f MB" % (len(FRAMES) + len(EXTRA), total / 1e6))
