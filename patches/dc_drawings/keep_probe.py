"""How a drawing should ship in a Godot package (the factory's roadmap 296): what Godot 4.7 makes of an SVG left to its
default import, and of one beside a hand-written `importer="keep"` .import -- and whether a game can still read the
kept one and draw it.

Builds a throwaway Godot project in a temp dir: `a.svg` and `b.svg`, both deli_a03's exploded axonometric as Deli
Counter renders it (argv[1], a Deli Counter checkout), `b.svg.import` the keep file, and `keep_probe.gd` beside this
file. Runs Godot headless `--import`, then the probe; kills the process tree on a timeout (docs/COMMANDS.md, Godot
probes). Reports what `.godot/imported/` holds and how big, both `.import` files, whether the keep file came back as
written, and the probe's lines. Prints measurements only; writes keep_probe.out.txt beside this file.

    python patches/dc_drawings/keep_probe.py <deli_counter checkout>
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[1]
DC = pathlib.Path(sys.argv[1]).resolve()
GODOT = json.loads((F / "factory.local.json").read_text(encoding="utf-8"))["godot_executable"]
KEEP = '[remap]\n\nimporter="keep"\n'
sys.path.insert(0, str(DC))
import axonometric  # noqa: E402
import spec_loader  # noqa: E402

assert pathlib.Path(axonometric.__file__).resolve().parent == DC
svg = axonometric.render_axonometric(spec_loader.load_spec(str(DC / "specs" / "deli_a03.json")))
P = pathlib.Path(tempfile.mkdtemp(prefix="keep_probe_"))
for name in ("a.svg", "b.svg"):
    (P / name).write_text(svg, encoding="utf-8", newline="\n")
(P / "b.svg.import").write_text(KEEP, encoding="utf-8", newline="\n")
(P / "project.godot").write_text('config_version=5\n\n[application]\n\nconfig/name="keep_probe"\n'
                                 'config/features=PackedStringArray("4.7")\n', encoding="utf-8", newline="\n")
shutil.copy2(HERE / "keep_probe.gd", P / "probe.gd")


def run(args, timeout):
    p = subprocess.Popen([GODOT, "--headless", "--path", str(P)] + args, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        out, _ = p.communicate()
        out += "\nTIMED OUT, tree killed"
    return p.returncode, out


lines = ["# keep_probe.py, Godot %s, deli_a03's axonometric from %s (%d bytes)"
         % (pathlib.Path(GODOT).name, (DC / "VERSION").read_text(encoding="utf-8"), len(svg.encode("utf-8")))]
rc, _out = run(["--import"], 240)
lines.append("import exit %d" % rc)
imp = P / ".godot" / "imported"
for f in sorted(imp.glob("*")) if imp.is_dir() else []:
    lines.append("  .godot/imported/%s  %d bytes" % (f.name, f.stat().st_size))
for name in ("a.svg.import", "b.svg.import"):
    p = P / name
    if not p.exists():
        lines.append("== %s MISSING" % name)
        continue
    text = p.read_text(encoding="utf-8")
    lines.append("== %s%s" % (name, " -- as written" if name == "b.svg.import" and text == KEEP else ""))
    lines += ["    " + ln for ln in text.splitlines()[:8]]
rc, out = run(["--script", "res://probe.gd"], 120)
lines.append("probe exit %d" % rc)
lines += ["  " + ln for ln in out.splitlines() if ln.startswith("KEEP_PROBE") or "ERROR" in ln]
shutil.rmtree(P, ignore_errors=True)
txt = "\n".join(lines) + "\n"
(HERE / "keep_probe.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
