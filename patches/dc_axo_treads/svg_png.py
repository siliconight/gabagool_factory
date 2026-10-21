"""Rasterize an SVG to PNG with the machine's Edge, headless, at the SVG's own size (argv: svg, png[, scale]).
Reads the local file only; writes the PNG; leaves no browser running (Edge exits after the screenshot)."""
import pathlib
import re
import subprocess
import sys

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
svg, png = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
head = svg.read_text(encoding="utf-8")[:400]
w = float(re.search(r'width="([\d.]+)"', head).group(1))
h = float(re.search(r'height="([\d.]+)"', head).group(1))
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                    "--force-device-scale-factor=%g" % scale, "--window-size=%d,%d" % (w, h),
                    "--screenshot=%s" % png, svg.as_uri()], capture_output=True, text=True, timeout=120)
print("exit", r.returncode, png, png.exists() and png.stat().st_size, "bytes", "(%dx%d)" % (w, h))
