import os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch_thread3_close.py")
with open(P, "r", encoding="utf-8") as fh:
    src = fh.read()

OLD = '''    ns = {}
    exec(compile(src, TEST_PATH, "exec"), ns)
'''
NEW = '''    # the test module resolves its own path from __file__, so give it one --
    # an empty globals dict makes it raise NameError before it can be reused
    ns = {"__file__": TEST_PATH, "__name__": "_t3_selftest_probe"}
    exec(compile(src, TEST_PATH, "exec"), ns)
'''

n = src.count(OLD)
if n != 1:
    print("REFUSING -- the block to replace appears %d time(s), expected 1" % n)
    sys.exit(1)

with open(P + ".pre_fix2", "w", encoding="utf-8", newline="") as fh:
    fh.write(src)
out = src.replace(OLD, NEW)
assert out != src
with open(P, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)
print("patched the exec namespace in %s" % os.path.basename(P))
