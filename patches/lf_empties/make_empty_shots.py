"""Write `empty_shots.gd` beside this file: the field frame script aimed at
the Empties across the through road, placed from a site's own drawn spec
(`site.site.drawn.json`: its `blockers` and road 0). Plan (x, y) is Godot
(x, -y).

Every view is shot TWICE: `_fill` with the frame script's 0.6-energy
directional fill (so a night level's shapes read), and `_night` without it
(what a player sees). A frame that says nothing about which it is gets
judged as the game.

    python make_empty_shots.py <site.site.drawn.json>
    godot --path <walk copy> --script empty_shots.gd -- <out dir>
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "lot_fields" / "field_shots.gd"


def g(x, y, h):
    return "Vector3(%.2f, %.2f, %.2f)" % (x, h, -y)


def main():
    s = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    empties = [b for b in s["blockers"] if b.get("empty")]
    assert empties, "no Empties in this drawn spec"
    road = s["roads"][0]
    y_road = (road["a"][1] + road["b"][1]) / 2.0
    half, walk = road["width"] / 2.0, road.get("sidewalk", 0.0)
    near_walk = y_road + half + walk / 2.0          # the playable side
    far_walk = y_road - half - walk / 2.0
    front = max(b["at"][1] + b["size_y"] / 2.0 for b in empties)
    back = min(b["at"][1] - b["size_y"] / 2.0 for b in empties)
    xs = [b["at"][0] for b in empties]
    x0, x1 = min(xs), max(xs)
    mid = min(xs, key=lambda x: abs(x))                # the Empty nearest x = 0
    shots = [
        ("empties_across_the_street", g(mid, near_walk, 1.7), g(mid, front, 4.5)),
        ("empties_down_the_row", g(x0 - 12.0, far_walk, 1.7), g(x0 + 40.0, front - 1.0, 4.0)),
        ("empties_one_front", g(mid, y_road - half + 1.0, 1.7), g(mid, front, 3.0)),
        ("empties_from_above", g(mid, y_road + 25.0, 30.0), g(mid, (front + back) / 2.0, 0.0)),
        ("empties_roofs", g(mid + 15.0, back - 20.0, 22.0), g(mid, front, 8.0)),
    ]
    body = ",\n".join('\t["%s", %s, %s]' % sh for sh in shots)
    src = SRC.read_text(encoding="utf-8")
    new, k = re.subn(r"const SHOTS: Array = \[\n.*?\n\]\n", "const SHOTS: Array = [\n" + body + ",\n]\n",
                     src, flags=re.S)
    assert k == 1, "SHOTS block not found"
    loop_old = '''	for s in SHOTS:
		cam.look_at_from_position(s[1], s[2], Vector3.UP)
		for _i in range(12):
			await process_frame
		var path: String = "%s/lot_%s.png" % [args[0], String(s[0])]
		root.get_viewport().get_texture().get_image().save_png(path)
		print("SHOTS wrote ", path)
'''
    loop_new = '''	for lit in [true, false]:
		fill.visible = lit
		for s in SHOTS:
			cam.look_at_from_position(s[1], s[2], Vector3.UP)
			for _i in range(12):
				await process_frame
			var tag: String = "fill" if lit else "night"
			var path: String = "%s/%s_%s.png" % [args[0], String(s[0]), tag]
			root.get_viewport().get_texture().get_image().save_png(path)
			print("SHOTS wrote ", path)
'''
    assert new.count(loop_old) == 1, "shot loop not found"
    new = new.replace(loop_old, loop_new)
    new = re.sub(r"## Shoots each parking field.*?Written by make_shots\.py\.",
                 "## Shoots the Empties across the through road, each view with the plain\n"
                 "## fill and without it, into the folder after `--`. Written by\n"
                 "## make_empty_shots.py.", new, flags=re.S)
    (HERE / "empty_shots.gd").write_text(new, encoding="utf-8", newline="\n")
    print("%d view(s) x 2 -> empty_shots.gd (Empty nearest x=0 at %.2f; fronts %.2f, %d Empties x %.1f..%.1f)"
          % (len(shots), mid, front, len(empties), x0, x1))


if __name__ == "__main__":
    main()
