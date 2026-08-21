import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch_thread3_close.py")
with open(P, "r", encoding="utf-8") as fh:
    src = fh.read()

OLD = '''    if PC_NEW not in vtext:
        fails.append("version.py does not carry %s" % PC_NEW)
    if ftext.strip() != PC_NEW:
        fails.append("VERSION says %r, expected %r" % (ftext.strip(), PC_NEW))
    _, ztext, _ = read(os.path.join(ZOO, "VERSION"))
    if ztext.strip() != ZOO_NEW:
        fails.append("zoo VERSION says %r, expected %r" % (ztext.strip(), ZOO_NEW))
'''

NEW = '''    # VERSION files carry a name prefix ("Pixelcoat 0.16.0"), so check for the
    # presence of the new version and the ABSENCE of the old one, rather than
    # asserting an exact form. The first version of this check assumed a bare
    # number and failed against correct files.
    if PC_NEW not in vtext:
        fails.append("version.py does not carry %s" % PC_NEW)
    if PC_OLD in vtext:
        fails.append("version.py still carries %s" % PC_OLD)
    if PC_NEW not in ftext:
        fails.append("pixelcoat VERSION does not carry %s -- it says %r"
                     % (PC_NEW, ftext.strip()))
    if PC_OLD in ftext:
        fails.append("pixelcoat VERSION still carries %s" % PC_OLD)
    _, ztext, _ = read(os.path.join(ZOO, "VERSION"))
    if ZOO_NEW not in ztext:
        fails.append("zoo VERSION does not carry %s -- it says %r"
                     % (ZOO_NEW, ztext.strip()))
    if ZOO_OLD in ztext:
        fails.append("zoo VERSION still carries %s" % ZOO_OLD)
'''

n = src.count(OLD)
if n != 1:
    print("REFUSING -- the block to replace appears %d time(s), expected 1" % n)
    sys.exit(1)

with open(P + ".pre_fix", "w", encoding="utf-8", newline="") as fh:
    fh.write(src)
out = src.replace(OLD, NEW)
assert out != src
with open(P, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)
print("patched the selftest version check in %s" % os.path.basename(P))

# show the VERSION files so the assumption is visible, not inferred again
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "pixelcoat", "VERSION"),
          os.path.join(ROOT, "zoo", "VERSION"),
          os.path.join(ROOT, "pixelcoat", "pixelcoat", "version.py")):
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8") as fh:
            print("  %-34s %r" % (os.path.relpath(p, ROOT).replace("\\", "/"),
                                  fh.read().strip()[:80]))
