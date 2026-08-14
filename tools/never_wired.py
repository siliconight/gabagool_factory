"""Find what is declared and never wired: keys read but never written, and
functions defined but never called.

WHAT THIS IS FOR. Four times in one day this toolchain turned out to contain a
correct piece that no code path reaches, and each one read as a MISSING FEATURE
until somebody measured:

    LuxLightLoader / LuxFixtureSpawner   documented, never called
    Zoo's LuxEmit_* markers              baked correctly, nothing reads them
    upstream_artifact_hashes             a fingerprint field, never populated
    provenance "inputs"                  a record field, always empty

Each cost hours to find by hand. The pattern is cheap to find by machine, so the
review question this file answers is not "is this designed correctly" -- it
generally is -- but **"is this called?"**

    python tools\\never_wired.py <repo> [<repo> ...] [--min-reads 1]

WHAT IT MEASURES.

  * READ-ONLY KEYS. A string literal used as a dict/mapping key in a LOAD
    position -- `d["k"]`, `d.get("k")`, `d.pop("k", ...)` -- that never appears
    in a STORE position anywhere in the corpus: `d["k"] = ...`, `{"k": ...}`,
    `dict(k=...)`, `d.setdefault("k", ...)`. `upstream_hashes` is exactly this
    shape: one read, zero writes, in the whole repository.

  * UNCALLED DEFINITIONS. A `def` whose name never appears anywhere else as a
    call, attribute, or bare reference.

WHAT IT CANNOT KNOW, and why the output is a list to read rather than a verdict.
A key read here may legitimately be written by a DIFFERENT repo, by a tool
outside this tree, or by hand-authored JSON -- that is normal for a manifest
contract, and this tool cannot see across that boundary. A function may be an
entry point, an override, or called by name through a registry. So every finding
is a QUESTION ("who writes this?"), never a defect. Ranking is by how loud the
question is: a key read in several places and written in none is louder than one
read once.

WHAT A NONZERO EXIT MEANS. Nothing was scanned. Findings never set the exit
code -- this is a lead generator, not a gate, and a gate here would fire on
every legitimate cross-repo contract in the tree.
"""
import argparse
import ast
import os
import re
import sys
from collections import defaultdict

#: Names that are entry points, protocol methods, or otherwise called by
#: machinery rather than by a visible reference. Kept explicit: an exclusion
#: nobody can see is how a scan quietly stops covering things.
_CALLED_BY_MACHINERY = re.compile(
    r"^(main|setup|teardown|test_.*|_.*_|__.*__"
    # ast.NodeVisitor dispatches these by name, Blender calls execute/draw/
    # register/unregister on its operators and panels, and pytest calls
    # conftest hooks. This file flagged its OWN visitors on the first run.
    r"|visit_.*|generic_visit|execute|draw|poll|invoke|modal"
    r"|register|unregister|pytest_.*)$")

#: Adapter/SDK protocol methods -- the scheduler calls these by interface, so a
#: definition with no visible caller is correct, not dead.
_PROTOCOL = {
    "probe", "validate_configuration", "fingerprint_inputs", "plan_commands",
    "collect_outputs", "normalize_validation", "adapter_id", "adapter_version",
    "output_contract_version",
}

_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules",
              "build", "dist", ".godot", "_scratch"}


def py_files(root):
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(dirpath, f)


class Scan(ast.NodeVisitor):
    """One file's key reads, key writes, definitions and name references."""

    def __init__(self, path):
        self.path = path
        self.reads = defaultdict(list)
        self.writes = set()
        self.defs = []
        self.names = set()

    # -- keys -------------------------------------------------------------
    def visit_Subscript(self, node):
        key = _const_str(node.slice)
        if key is not None:
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                self.writes.add(key)
            else:
                self.reads[key].append(node.lineno)
        self.generic_visit(node)

    def visit_Dict(self, node):
        for k in node.keys:
            key = _const_str(k)
            if key is not None:
                self.writes.add(key)
        self.generic_visit(node)

    def visit_Call(self, node):
        fn = node.func
        if isinstance(fn, ast.Attribute):
            self.names.add(fn.attr)
            first = _const_str(node.args[0]) if node.args else None
            if first is not None:
                if fn.attr in ("get", "pop", "getattr"):
                    self.reads[first].append(node.lineno)
                elif fn.attr in ("setdefault", "set", "update_one"):
                    self.writes.add(first)
        elif isinstance(fn, ast.Name):
            self.names.add(fn.id)
        # dict(k=...) and Model(k=...) both WRITE k
        for kw in node.keywords:
            if kw.arg:
                self.writes.add(kw.arg)
        self.generic_visit(node)

    # -- definitions and references ---------------------------------------
    def visit_FunctionDef(self, node):
        self.defs.append((node.name, node.lineno))
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Name(self, node):
        self.names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self.names.add(node.attr)
        self.generic_visit(node)

    # A keyword-only or annotated parameter named `k` is a WRITE of that key
    # from the caller's side -- `def f(*, cap_thick)` means someone passes it.
    def visit_arg(self, node):
        self.writes.add(node.arg)
        self.generic_visit(node)


def _const_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def scan_repo(root):
    reads = defaultdict(list)
    writes = set()
    defs = []
    names = set()
    unreadable = []
    for path in py_files(root):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                tree = ast.parse(fh.read(), filename=path)
        except (OSError, SyntaxError) as exc:
            unreadable.append(f"{path}: {exc}")
            continue
        s = Scan(path)
        s.visit(tree)
        rel = os.path.relpath(path, root)
        for k, lines in s.reads.items():
            reads[k].extend((rel, ln) for ln in lines)
        writes |= s.writes
        names |= s.names
        defs.extend((name, rel, ln) for name, ln in s.defs)
    return reads, writes, defs, names, unreadable


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repos", nargs="+")
    ap.add_argument("--min-reads", type=int, default=1,
                    help="only report keys read at least this many times")
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args(argv)

    any_scanned = False
    for root in args.repos:
        if not os.path.isdir(root):
            sys.stderr.write("not a directory: %s\n" % root)
            continue
        reads, writes, defs, names, unreadable = scan_repo(root)
        if not reads and not defs:
            sys.stderr.write("no python found under %s\n" % root)
            continue
        any_scanned = True
        print("=" * 72)
        print(os.path.basename(os.path.abspath(root)))
        print("=" * 72)

        orphan_keys = {k: v for k, v in reads.items()
                       if k not in writes and len(v) >= args.min_reads
                       and not k.startswith("__")}
        print()
        print("KEYS READ BUT NEVER WRITTEN (%d) -- who writes this?"
              % len(orphan_keys))
        for k, sites in sorted(orphan_keys.items(),
                               key=lambda kv: (-len(kv[1]), kv[0]))[:args.top]:
            where = ", ".join("%s:%d" % s for s in sites[:3])
            more = "" if len(sites) <= 3 else " (+%d more)" % (len(sites) - 3)
            print("  %-34s %2d read(s)  %s%s" % (k, len(sites), where, more))

        seen = defaultdict(int)
        for name, _rel, _ln in defs:
            seen[name] += 1
        uncalled = [(n, r, l) for n, r, l in defs
                    if n not in names
                    and not _CALLED_BY_MACHINERY.match(n)
                    and n not in _PROTOCOL
                    and seen[n] == 1]
        print()
        print("DEFINED BUT NEVER REFERENCED (%d) -- who calls this?"
              % len(uncalled))
        for name, rel, ln in sorted(uncalled)[:args.top]:
            print("  %-34s %s:%d" % (name, rel, ln))

        for u in unreadable:
            sys.stderr.write("unreadable: " + u + "\n")
        print()

    if not any_scanned:
        return 2
    print("Every line above is a QUESTION, not a defect: a key may be written "
          "by another repo\nor by hand-authored JSON, and a function may be an "
          "entry point or called through a\nregistry. This tool cannot see "
          "across those boundaries and does not pretend to.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
