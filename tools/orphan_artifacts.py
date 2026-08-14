"""Producers with no consumer, and consumers with no producer.

WHAT THIS IS FOR. Five times now this toolchain has turned out to contain a
correct piece that nothing reaches, and every one read as a MISSING FEATURE
until somebody measured:

    LuxLightLoader / LuxFixtureSpawner   documented, never called
    Zoo's LuxEmit_* markers              baked correctly, nothing reads them
    upstream_artifact_hashes             a fingerprint field, never populated
    provenance "inputs"                  a record field, always empty
    Patina's trim atlas + instances      emitted, and absent from the export

`never_wired.py` finds the first four: they are Python-visible, a name read in
one place and written in none. The fifth is invisible to it, because the seam is
not a function call -- it is a FILE. Patina writes `<stem>.trim.png`, every
build order carries a `uv_region` into it, Zoo writes TEXCOORD_0 on all 2255
cover primitives, and the atlas is in no export: one material, `M_Cover_
concrete`, flat grey, zero textures. Nothing in Python is wrong. The pipeline
just stops.

So this asks the same question one layer out -- **who reads this file?** -- in
both directions:

  A. ON DISK, MENTIONED NOWHERE (or in only one repo). Something produced it.
     If only the producing repo names it, nothing downstream consumes it.

  B. NAMED IN SOURCE, ABSENT FROM DISK -- absent from the workspace AND from
     every repo scanned. Something expects it. If no build ever produced one
     and no repo ships one, the importer is reading a file that is never
     written -- the
     shape of the dispatch importers naming `lux.lighting.json`,
     `lux.volumes.json` and `*.nav_hints.json`. Markdown and test files are
     excluded from this half: a CHANGELOG naming a file from three releases
     ago, and a fixture called `o.glb`, are mentions, not consumers. It is
     restricted to dotted sidecars for the same reason -- a bare `batch.json`
     cannot be told from a variable holding a path.

    python tools\\orphan_artifacts.py --workspace rockay-ws --repos .

WHAT AN ARTIFACT KIND IS. Not a filename -- filenames carry seeds, stems and
mission ids. The KIND is the part a consumer would actually hardcode: the last
two DOTTED components.

    shell.slots.json                 -> .slots.json
    shell.patina.dressing.json       -> .dressing.json
    site.site.lights.json            -> .lights.json
    o.trim.png                       -> .trim.png

DELIBERATELY NARROW, after a wider first draft was mostly noise. That draft also
took a trailing `_word.ext`, which turned `gothic_street_night.tres` into the
"artifact kind" `_night.tres` and `wall_rockay_01_w200.glb` into `_w200.glb` --
filenames, not seams. It buried the real findings under dozens of them. So
`lf_..._5017_dressing.glb` is NOT covered here: undotted names are a naming
convention this tool cannot distinguish from a stem, and a lead generator that a
human reads is worth more precise than complete.

For the same reason `.gd` and `.tres` are not scanned on disk. An export copies
Lux's addon SOURCE into `runtime/lux/`, so every one of those files looks like a
produced artifact nobody reads, and none of them is. Bare extensions (`.json`,
`.glb`) are likewise never flagged: every repo mentions `.json`.

WHAT THIS CANNOT KNOW, and why every line is a QUESTION rather than a verdict.
A consumer may build the name dynamically (`base + "." + kind + ".json"`), in
which case the literal never appears and a live consumer looks dead. A file may
be an intermediate that is SUPPOSED to stop at a stage boundary. A name in
source may be documentation. So this ranks by how loud the question is -- many
files on disk and one repo naming them is louder than one file and two repos --
and never sets the exit code on a finding.

WHAT A NONZERO EXIT MEANS. Nothing was scanned: no workspace, no repos, or no
files under either. An empty result is never reported as "everything is wired".
"""
import argparse
import collections
import os
import re
import sys

#: Extensions worth tracking as pipeline artifacts. Source and build noise
#: (.py, .pyc, .md) is excluded deliberately -- this is about DATA crossing a
#: tool boundary, not about code.
#: `.gd` / `.tres` are excluded: an export copies addon SOURCE into its runtime
#: dir, so they all read as produced-and-unread and none of them is.
_ART_EXT = {".json", ".glb", ".gltf", ".png", ".tscn", ".jpg", ".exr", ".obj",
            ".csv"}

_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules",
              ".godot", ".import", "_scratch", "venv",
              ".venv", "site-packages", "dist", "build"}

_SRC_EXT = {".py", ".gd", ".tscn", ".tres", ".cfg", ".json", ".md", ".toml"}

#: A string that looks like a filename inside source.
_NAME_IN_SRC = re.compile(
    r"[\w*?.\-]+\.(?:json|glb|gltf|png|tscn|jpg|exr|obj|csv)\b")

#: Quoted spans only. Scanned raw, `bpy.ops.export_scene.gltf` reads as a file
#: named `.gltf` -- a Python attribute chain is not a path, and only a string
#: literal can be one.
_QUOTED = re.compile(r"\"([^\"\n]*)\"|'([^'\n]*)'")


def artifact_kind(name):
    """The part of a filename a consumer would hardcode. See module docstring."""
    root, ext = os.path.splitext(name)
    if ext.lower() not in _ART_EXT:
        return None
    parts = name.split(".")
    if len(parts) >= 3:
        return "." + ".".join(parts[-2:])
    return ext


def walk(root, exts):
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1].lower() in exts:
                yield os.path.join(dirpath, f)


def on_disk(workspaces):
    """{kind: [paths]} for every artifact under the workspaces."""
    kinds = collections.defaultdict(list)
    for ws in workspaces:
        for path in walk(ws, _ART_EXT):
            k = artifact_kind(os.path.basename(path))
            if k:
                kinds[k].append(path)
    return kinds


def source_index(repos):
    """(mentions, literals): kind -> {repo}, and every filename literal seen."""
    mentions = collections.defaultdict(set)
    literals = collections.defaultdict(set)
    for repo in repos:
        label = os.path.basename(os.path.abspath(repo)) or repo
        for path in walk(repo, _SRC_EXT):
            low = path.replace("\\", "/").lower()
            # A CHANGELOG naming a file from three releases ago, and a test
            # fixture called `o.glb`, are both mentions. Neither is a consumer.
            doc_or_test = (low.endswith(".md")
                           or "/test" in low or low.rsplit("/", 1)[-1].startswith("test_"))
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            rel = os.path.relpath(path, repo)
            for q in _QUOTED.finditer(text):
              span = q.group(1) if q.group(1) is not None else q.group(2)
              for m in _NAME_IN_SRC.finditer(span or ""):
                name = m.group(0)
                k = artifact_kind(name)
                if k:
                    mentions[k].add(label)
                    if not doc_or_test:
                        literals[name].add("%s/%s" % (label, rel))
    return mentions, literals


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workspace", nargs="+", required=True,
                    help="dirs holding BUILT artifacts (a mission workspace)")
    ap.add_argument("--repos", nargs="+", required=True,
                    help="dirs holding SOURCE (tool repos; '.' for the factory)")
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args(argv)

    ws = [w for w in args.workspace if os.path.isdir(w)]
    rp = [r for r in args.repos if os.path.isdir(r)]
    for bad in set(args.workspace) - set(ws):
        sys.stderr.write("not a directory: %s\n" % bad)
    for bad in set(args.repos) - set(rp):
        sys.stderr.write("not a directory: %s\n" % bad)
    if not ws or not rp:
        sys.stderr.write("need at least one workspace and one repo\n")
        return 2

    disk = on_disk(ws)
    mentions, literals = source_index(rp)
    if not disk and not mentions:
        sys.stderr.write("no artifacts and no source found -- nothing scanned\n")
        return 2

    generic = set(_ART_EXT)

    print("=" * 74)
    print("A. ON DISK, AND NAMED BY AT MOST ONE REPO -- who reads this?")
    print("=" * 74)
    rows = [(k, len(v), sorted(mentions.get(k, ())))
            for k, v in disk.items()
            if k not in generic and len(mentions.get(k, ())) <= 1]
    if not rows:
        print("  (none -- every non-generic artifact kind is named by 2+ repos)")
    for k, n, repos in sorted(rows, key=lambda r: (-r[1], r[0]))[:args.top]:
        print("  %-26s %5d file(s)   named by: %s"
              % (k, n, ", ".join(repos) if repos else "NOBODY"))
        print("      e.g. %s" % os.path.basename(disk[k][0]))

    print()
    print("=" * 74)
    print("B. NAMED IN SOURCE, ABSENT FROM DISK -- who writes this?")
    print("=" * 74)
    # "Absent from disk" has to mean absent EVERYWHERE this run looked, not
    # just absent from the workspace. A first pass compared source literals
    # against built artifacts only, so every schema and spec that lives inside
    # a repo read as missing -- `level.schema.json`, which sits at
    # deli_counter/schema/, came back as the loudest line in the report at 157
    # mentions. The top hit being noise is how a lead generator teaches you to
    # stop reading it.
    have = set()
    for paths in disk.values():
        have.update(os.path.basename(p) for p in paths)
    for repo in rp:
        for path in walk(repo, _ART_EXT):
            have.add(os.path.basename(path))
    missing = []
    for name, sites in literals.items():
        if "*" in name or "?" in name:
            continue
        # Only SIDECARS -- a dotted kind. A bare `batch.json` names a file
        # whose stem is the whole name, and this tool cannot tell a missing
        # one from a variable holding a path.
        if len(name.split(".")) < 3:
            continue
        if any(h == name or h.endswith("." + name) or h.endswith(name)
               for h in have):
            continue
        missing.append((name, sorted(sites)))
    if not missing:
        print("  (none -- every filename literal in source exists on disk)")
    for name, sites in sorted(missing, key=lambda r: (-len(r[1]), r[0]))[:args.top]:
        print("  %-34s named in %d place(s)" % (name, len(sites)))
        for s in sites[:3]:
            print("      %s" % s)
        if len(sites) > 3:
            print("      ... +%d more" % (len(sites) - 3))

    print()
    print("Every line is a QUESTION, not a defect. A consumer that BUILDS the "
          "name at\nruntime (base + '.' + kind + '.json') never shows a "
          "literal, so a live consumer\ncan look dead here; and an "
          "intermediate is SUPPOSED to stop at a stage\nboundary. This tool "
          "cannot see across either and does not pretend to.")
    print()
    print("scanned: %d artifact kind(s) on disk, %d filename literal(s) in "
          "%d repo(s)" % (len(disk), len(literals), len(rp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
