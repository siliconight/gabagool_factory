"""Make shot_bot_near.gd: the 0.171.0 shot bot, its second frame taken by changing the camera's
near plane instead of moving the camera 1 mm.

    python make_near_probe.py <preview dir> <near factor>

A near-plane change leaves every pixel's position and texture sample where it was, so texture
sparkle cannot appear in it; it requantizes depth, which is what two coplanar faces fight over.
"""
import pathlib
import sys

d = pathlib.Path(sys.argv[1])
factor = float(sys.argv[2])
t = (d / "shot_bot.gd").read_text(encoding="utf-8")
assert "_hold_warmups(site)" in t, "the preview's shot_bot.gd is not 0.171.0's"
old = "\tvar b: Image = await _frame(eye + Vector3(JITTER, JITTER, JITTER), look)\n"
new = ("\tvar near_was: float = _cam.near\n"
       "\t_cam.near = near_was * %r\n"
       "\tvar b: Image = await _frame(eye, look)\n"
       "\t_cam.near = near_was\n") % factor
assert t.count(old) == 1
out = t.replace(old, new)
save_old = '\ta.save_png(png)\n'
save_new = '\ta.save_png(png)\n\tb.save_png("%s/%s_b.png" % [_shots_dir, s["name"]])\n'
assert out.count(save_old) == 1
out = out.replace(save_old, save_new)
(d / "shot_bot_near.gd").write_text(out, encoding="utf-8", newline="\n")
print("wrote", d / "shot_bot_near.gd", "near x", factor)
