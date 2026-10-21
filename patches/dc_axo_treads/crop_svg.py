"""Crop an SVG to the drawn region of the elements carrying an attribute (argv: svg, out svg, attribute regex,
padding px, scale): the bounding box of every point in a matching element's group or polygon, padded, as the new
viewBox, the canvas scaled. For looking at a detail; writes only the out file."""
import re
import sys

src, dst, attr, pad, scale = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
svg = open(src, encoding="utf-8").read()
xs, ys = [], []
for m in re.finditer(r"<g[^>]*%s[^>]*>(.*?)</g>" % attr, svg, re.S):
    for x, y in re.findall(r"([-\d.]+),([-\d.]+)", m.group(1)):
        xs.append(float(x))
        ys.append(float(y))
if not xs:
    raise SystemExit("no element matches %r" % attr)
x0, y0, x1, y1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
w, h = x1 - x0, y1 - y0
head = re.match(r"<svg[^>]*>", svg).group(0)
new = re.sub(r'width="[\d.]+"', 'width="%.0f"' % (w * scale), head, count=1)
new = re.sub(r'height="[\d.]+"', 'height="%.0f"' % (h * scale), new, count=1)
new = re.sub(r'viewBox="[^"]+"', 'viewBox="%.1f %.1f %.1f %.1f"' % (x0, y0, w, h), new, count=1)
open(dst, "w", encoding="utf-8").write(svg.replace(head, new, 1))
print("cropped to", "%.0f x %.0f" % (w * scale, h * scale))
