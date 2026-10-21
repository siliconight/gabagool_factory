"""Evaluate the guide's clear-width formula against agent_contract.json's numbers.
Reads the contract; prints numbers only."""
import json, math, sys
c = json.load(open(sys.argv[1], encoding="utf-8"))
body_r = c["characters"]["player"]["radius_m"]
bake_r = c["nav_bake"]["agent_radius_m"]
cell = c["nav_bake"]["cell_size_m"]
door = c["clearances"]["min_door_width_m"]
corr = c["clearances"]["min_corridor_width_m"]
speed = c["characters"]["player"]["walk_speed_mps"]
eye = c["sightlines"]["crew_sight_height_m"]; eye_e = c["sightlines"]["enemy_sight_height_m"]
aim = c["characters"]["player"]["chest_height_m"]
print("inputs: body_r", body_r, "bake_r", bake_r, "cell", cell, "door", door, "corridor", corr, "walk", speed)

def clear(n, d, wm, gap):
    return n * d + 2 * wm + (n - 1) * gap

# bake passable floor (contract derivation): 2*ceil(r/cell)*cell + 2*cell
floor_ = 2 * math.ceil(round(bake_r / cell, 9)) * cell + 2 * cell
print("bake passable floor (one agent):", round(floor_, 3))
# door's per-side margin for the body
print("door per-side margin for body:", round((door - 2 * body_r) / 2, 3))
# corridor margin implied: corr = 2*bake_r + 0.3
print("corridor implied margin per side over bake diameter:", round((corr - 2 * bake_r) / 2, 3))

rows = [
    ("A guide inputs: d=2*body_r, wm=0.15, gap=0.20", 2 * body_r, 0.15, 0.20),
    ("B bake diameter: d=2*bake_r, wm=0.15, gap=0.20", 2 * bake_r, 0.15, 0.20),
    ("C door margin: d=2*body_r, wm=(door-2r)/2, gap=0.20", 2 * body_r, (door - 2 * body_r) / 2, 0.20),
    ("D zero margins: d=2*body_r, wm=0, gap=0", 2 * body_r, 0.0, 0.0),
]
for label, d, wm, gap in rows:
    print(label, "| n=1 %.3f  n=2 %.3f  n=4 %.3f" % (clear(1, d, wm, gap), clear(2, d, wm, gap), clear(4, d, wm, gap)))

# what DC's numbers are, in n-bodies under guide inputs (A)
for name, w in (("island_aisle/staff_aisle 1.25", 1.25), ("min_corridor 1.10", corr),
                ("combat_audit WIDE_DOOR 4*r", 4 * body_r), ("_seed_clear volume margin 0.9", 0.9),
                ("H_CARRY_PINCH opening 1.2", 1.2), ("CRAMP_MIN_DIM 2.2", 2.2),
                ("tactical MIN_OPENING_WIDTH 0.8", 0.8), ("door_approach 2r+0.3", 2 * body_r + 0.3)):
    # largest n with clear(n, 0.70, 0.15, 0.20) <= w
    n = 0
    while clear(n + 1, 2 * body_r, 0.15, 0.20) <= w + 1e-9:
        n += 1
    print("%-34s %.3f m -> holds %d side-by-side bodies at guide margins; passes bake floor: %s" % (name, w, n, w >= floor_ - 1e-9))

# cover heights
a, b = eye, eye_e
cross = a - (a - aim) ** 2 / (a + b - 2 * aim)
print("cover_break (crossing):", round(cross, 4), "shelter (taller eye):", max(a, b))
print("crouch_height_m:", c["characters"]["player"].get("crouch_height_m"))
# crossings: exposure time at contract speed vs guide's 4.5
for dist in (3.0, 6.0, 7.0, 15.0, 25.0):
    print("crossing %.1f m: %.2f s at %.1f m/s, %.2f s at 4.5 m/s" % (dist, dist / speed, speed, dist / 4.5))
