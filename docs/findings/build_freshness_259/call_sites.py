"""For each Deli Counter module a shell build can reach but build_freshness's GEOMETRY_SOURCES does not list:
every reached module that imports it, and the lines there that use it (its alias included). Static, from the
source text; a use is a line naming the alias followed by a dot, or a name the import brought in. It says WHERE a
module is used on the build path, not what the use bakes into a shell -- that is read off the lines. A probe:
prints and stops (roadmap 259).

    python docs/findings/build_freshness_259/call_sites.py deli_counter [--max 4]
"""
import ast
import os
import re
import sys

dc = os.path.abspath(sys.argv[1])
cap = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 4
sys.path.insert(0, dc)
local = {f[:-3] for f in os.listdir(dc) if f.endswith(".py")}


def parse(mod):
    return ast.parse(open(os.path.join(dc, mod + ".py"), encoding="utf-8").read())


def bindings(tree):
    """{module: set of local names it is reached by} for repo-local imports anywhere in the tree."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                m = a.name.split(".")[0]
                if m in local:
                    out.setdefault(m, set()).add(a.asname or m)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            m = node.module.split(".")[0]
            if m in local:
                for a in node.names:
                    out.setdefault(m, set()).add("=" + (a.asname or a.name))
    return out


seen, todo, graph = set(), ["build", "deli_counter"], {}
while todo:
    m = todo.pop()
    if m in seen:
        continue
    seen.add(m)
    graph[m] = bindings(parse(m))
    todo.extend(graph[m])

import build_freshness  # noqa: E402
listed = {s[:-3] for s in build_freshness.GEOMETRY_SOURCES}
for target in sorted(seen - listed - {"build", "deli_counter"}):
    print("== %s" % target)
    for importer in sorted(graph):
        names = graph[importer].get(target)
        if not names:
            continue
        lines = open(os.path.join(dc, importer + ".py"), encoding="utf-8").read().split("\n")
        pats = []
        for n in names:
            if n.startswith("="):
                pats.append(re.compile(r"\b%s\b" % re.escape(n[1:])))
            else:
                pats.append(re.compile(r"\b%s\." % re.escape(n)))
        hits = [(i + 1, l.strip()) for i, l in enumerate(lines)
                if any(p.search(l) for p in pats) and not l.strip().startswith(("import ", "from ", "#"))]
        tag = "listed" if importer in listed else ("entry" if importer in ("build", "deli_counter") else "unlisted")
        print("   in %s (%s): %d use(s)" % (importer, tag, len(hits)))
        for ln, text in hits[:cap]:
            print("      %d: %s" % (ln, text[:150]))
