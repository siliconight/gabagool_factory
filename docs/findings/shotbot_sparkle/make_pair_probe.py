"""Make shot_bot_pair.gd: the shot bot, saving each station's second frame beside its first.

    python make_pair_probe.py <preview dir>
"""
import pathlib
import sys

d = pathlib.Path(sys.argv[1])
t = (d / "shot_bot.gd").read_text(encoding="utf-8")
old = '\tvar png: String = "%s/%s.png" % [_shots_dir, s["name"]]\n\ta.save_png(png)\n'
new = ('\tvar png: String = "%s/%s.png" % [_shots_dir, s["name"]]\n\ta.save_png(png)\n'
       '\tb.save_png("%s/%s_b.png" % [_shots_dir, s["name"]])\n')
assert t.count(old) == 1
assert "_hold_warmups(site)" in t, "the preview's shot_bot.gd is not 0.171.0's"
(d / "shot_bot_pair.gd").write_text(t.replace(old, new), encoding="utf-8", newline="\n")
print("wrote", d / "shot_bot_pair.gd")
