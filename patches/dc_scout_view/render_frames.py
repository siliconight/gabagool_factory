"""Render the review page's three buildings both ways from a Deli Counter checkout: <repo> <outdir>."""
import pathlib
import subprocess
import sys

repo, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
sys.path.insert(0, str(repo))
import axonometric  # noqa: E402
import spec_loader  # noqa: E402

out.mkdir(parents=True, exist_ok=True)
PNG = r"C:\Projects\gabagool_studios\gabagool_factory\patches\dc_axo_treads\svg_png.py"
for name in ("deli_a03", "office", "pharmacy_a01"):
    spec = spec_loader.load_spec(str(repo / "specs" / (name + ".json")))
    for mode in (False, True):
        svg = axonometric.render_axonometric(spec, scout=mode)
        f = out / ("%s_%s.svg" % (name, "scout" if mode else "full"))
        f.write_text(svg, encoding="utf-8")
        print(f.name, len(svg), "chars", svg.count("<"), "elements")
        subprocess.run([sys.executable, PNG, str(f), str(f.with_suffix(".png"))], check=True)
