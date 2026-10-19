"""Which of Deli Counter's own modules does a shell build import, and which of those does build_freshness's
GEOMETRY_SOURCES not list? Static: AST imports -- top-level and inside functions alike -- followed
transitively through repo-local modules from build.py and deli_counter.py. "Imported by" names the first
importer met, not every one. A module reached is one the build CAN execute; whether its output is baked into
a shell is a separate question this does not answer. A probe: prints and stops (roadmap 259).

    python docs/findings/build_freshness_259/freshness_imports.py deli_counter
"""
import ast
import os
import sys

dc = os.path.abspath(sys.argv[1])
sys.path.insert(0, dc)
local = {f[:-3] for f in os.listdir(dc) if f.endswith(".py")}


def imports(mod):
    src = open(os.path.join(dc, mod + ".py"), encoding="utf-8").read()
    out = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out.add(node.module.split(".")[0])
    return {m for m in out if m in local}


seen, todo, via = set(), ["build", "deli_counter"], {}
while todo:
    m = todo.pop()
    if m in seen:
        continue
    seen.add(m)
    for n in sorted(imports(m)):
        via.setdefault(n, m)
        todo.append(n)

import build_freshness  # noqa: E402
listed = {s[:-3] for s in build_freshness.GEOMETRY_SOURCES}
print("reached from build.py / deli_counter.py:", len(seen))
print("listed in GEOMETRY_SOURCES:", len(listed))
print("listed but not reached:", sorted(listed - seen))
print("reached but NOT listed:")
for m in sorted(seen - listed):
    print("   %-28s (imported by %s)" % (m, via.get(m, "-")))
