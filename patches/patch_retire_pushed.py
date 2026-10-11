"""tools/factory_retire.py: what a PUSHED record makes regenerable is retired (the walker, 2026-10-11).

"we should have a package clean job so we don't accrue GBs of packages that have already been pushed
and verified as known good to GIT". The retention rule kept every cold-run workspace among the newest
twelve whatever its state, and nothing at all looked at the packages the factory makes: by
2026-10-11 the zips beside the factory came to 770 MB and an install test's unpack to 1.3 GB.

VERIFIED MEANS PUSHED. A run's record (`docs/cold_runs/cold_N/NOTES.md`), an install test's record
(`docs/findings/stranger_install/install_test_N/`) and a release's notes (`docs/releases/<tag>.md`)
are written after the thing is checked; once they are in the branch the root pushes to, the output
they describe can be made again from them. Four rules, every one asking the upstream branch through
git and none of them firing when the root has no upstream:

  workspaces     a cold-run workspace beyond the newest KEEP_PUSHED (4) whose record is pushed --
                 the newest four stay because a price takes the previous run's package as its
                 control; a workspace a record's script names stays, as before
  release zips   `gabagool_factory_package_factory-vX.Y.Z.zip` whose notes are pushed, except the
                 newest release's, which is the handoff
  test zips      `gabagool_factory_package_<YYYYMMDD_HHMM>.zip` that a pushed record names
  test unpacks   an install test's unpack (its script's `DEST`, a `stranger_202_N` folder) whose
                 record is pushed, except the newest

and `--apply` removes a file as well as a folder. Anchored, the file pinned by hash, nothing written
on a miss; the selftest grows a tree with a bare upstream and fails without the rules.

    python patches/patch_retire_pushed.py && python tools/factory_retire.py --selftest
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "factory_retire.py"
SHA = "69bd4e27b3d4ae11"

DOC_OLD = ("                 that still reads one keeps it). Regenerable from\n"
           "                 docs/cold_runs/cold_N/.\n")
DOC_NEW = (DOC_OLD +
           "\n"
           "VERIFIED MEANS PUSHED (2026-10-11, the walker: \"a package clean job so we\n"
           "don't accrue GBs of packages that have already been pushed and verified as\n"
           "known good\"). Once a record is in the branch the root pushes to, what it\n"
           "describes can be made again from it. None of these fires without an upstream:\n"
           "\n"
           "  pushed runs    a cold-run workspace beyond the newest KEEP_PUSHED whose\n"
           "                 docs/cold_runs/cold_N/NOTES.md is pushed (a price takes the\n"
           "                 previous run's package as its control, so four stay).\n"
           "  release zips   ../gabagool_factory_package_factory-vX.Y.Z.zip whose\n"
           "                 docs/releases/factory-vX.Y.Z.md is pushed, but not the newest.\n"
           "  test zips      ../gabagool_factory_package_<stamp>.zip a pushed record names.\n"
           "  test unpacks   an install test's unpack (its script's DEST) whose\n"
           "                 docs/findings/stranger_install/install_test_N/ is pushed, but\n"
           "                 not the newest.\n")
CONST_OLD = "WALK_EXPORT_DAYS = 30\n"
CONST_NEW = ("WALK_EXPORT_DAYS = 30\n"
             "#: Pushed runs' workspaces kept, newest first: a price's control is the run before.\n"
             "KEEP_PUSHED = 4\n"
             "_TAGGED = re.compile(r\"gabagool_factory_package_(factory-v(\\d+)\\.(\\d+)\\.(\\d+))\\.zip\")\n"
             "_STAMPED = re.compile(r\"gabagool_factory_package_\\d{8}_\\d{4}\\.zip\")\n")
HELP_OLD = "def plan(root, keep=KEEP_WORKSPACES):\n"
HELP_NEW = ('def _upstream(root):\n'
            '    """The branch the root pushes to (`origin/main`), or None: then nothing is pushed."""\n'
            '    r = subprocess.run(["git", "-C", root, "rev-parse", "--abbrev-ref",\n'
            '                        "--symbolic-full-name", "@{u}"], capture_output=True, text=True)\n'
            '    return (r.stdout.strip() or None) if r.returncode == 0 else None\n'
            '\n'
            '\n'
            'def _pushed(root, upstream, rel):\n'
            '    """Whether ``rel`` -- a file or a folder -- is in the pushed branch."""\n'
            '    r = subprocess.run(["git", "-C", root, "cat-file", "-e", "%s:%s" % (upstream, rel)],\n'
            '                       capture_output=True)\n'
            '    return r.returncode == 0\n'
            '\n'
            '\n'
            'def _pushed_mentions(root, upstream, needle):\n'
            '    """Whether a pushed file under docs/ names ``needle``."""\n'
            '    r = subprocess.run(["git", "-C", root, "grep", "-l", "-F", needle, upstream, "--", "docs"],\n'
            '                       capture_output=True, text=True)\n'
            '    return r.returncode == 0 and bool(r.stdout.strip())\n'
            '\n'
            '\n'
            'def _stranger_installs(root):\n'
            '    """``[(N, folder)]``: each install test\'s unpack, from its own script\'s DEST."""\n'
            '    out = []\n'
            '    d = os.path.join(root, "docs", "findings", "stranger_install")\n'
            '    if not os.path.isdir(d):\n'
            '        return out\n'
            '    for f in sorted(os.listdir(d)):\n'
            '        m = re.fullmatch(r"install_test_(\\d+)\\.sh", f)\n'
            '        if not m:\n'
            '            continue\n'
            '        text = open(os.path.join(d, f), encoding="utf-8", errors="replace").read()\n'
            '        dm = re.search(r"^DEST=\'([^\']+)\'", text, re.M)\n'
            '        if not dm:\n'
            '            continue\n'
            '        folder = os.path.dirname(dm.group(1).rstrip("\\\\/"))\n'
            '        if re.fullmatch(r"stranger_202_\\d+", os.path.basename(folder)):\n'
            '            out.append((int(m.group(1)), folder))\n'
            '    return out\n'
            '\n'
            '\n'
            'def plan(root, keep=KEEP_WORKSPACES, keep_pushed=KEEP_PUSHED, package_dir=None):\n')
BODY_OLD = ("        for d in cold[keep:]:\n"
            "            if d in named or _tracked(root, \"workspaces/\" + d):\n"
            "                continue\n"
            "            p = os.path.join(ws, d)\n"
            "            out.append({\"path\": p, \"why\": \"cold-run workspace beyond the newest %d, unreferenced\" % keep, \"bytes\": _size(p)})\n"
            "    return out\n")
BODY_NEW = ("        for d in cold[keep:]:\n"
            "            if d in named or _tracked(root, \"workspaces/\" + d):\n"
            "                continue\n"
            "            p = os.path.join(ws, d)\n"
            "            out.append({\"path\": p, \"why\": \"cold-run workspace beyond the newest %d, unreferenced\" % keep, \"bytes\": _size(p)})\n"
            "    upstream = _upstream(root)\n"
            "    if not upstream:\n"
            "        return out\n"
            "    already = {o[\"path\"] for o in out}\n"
            "    if os.path.isdir(ws):\n"
            "        for d in cold[keep_pushed:]:\n"
            "            p = os.path.join(ws, d)\n"
            "            if p in already or d in named or _tracked(root, \"workspaces/\" + d):\n"
            "                continue\n"
            "            n = d.split(\"-\")[1]\n"
            "            if _pushed(root, upstream, \"docs/cold_runs/cold_%s/NOTES.md\" % n):\n"
            "                out.append({\"path\": p, \"why\": \"cold-run workspace beyond the newest %d whose record is pushed\" % keep_pushed, \"bytes\": _size(p)})\n"
            "    pdir = package_dir or os.path.dirname(os.path.abspath(root))\n"
            "    if os.path.isdir(pdir):\n"
            "        zips = sorted(f for f in os.listdir(pdir) if f.startswith(\"gabagool_factory_package_\") and f.endswith(\".zip\"))\n"
            "        tagged = sorted((f for f in zips if _TAGGED.fullmatch(f)),\n"
            "                        key=lambda f: tuple(int(x) for x in _TAGGED.fullmatch(f).group(2, 3, 4)))\n"
            "        for f in zips:\n"
            "            p = os.path.join(pdir, f)\n"
            "            m = _TAGGED.fullmatch(f)\n"
            "            if m:\n"
            "                if f != tagged[-1] and _pushed(root, upstream, \"docs/releases/%s.md\" % m.group(1)):\n"
            "                    out.append({\"path\": p, \"why\": \"release package whose notes are pushed, not the newest release\", \"bytes\": os.path.getsize(p)})\n"
            "            elif _STAMPED.fullmatch(f) and _pushed_mentions(root, upstream, f):\n"
            "                out.append({\"path\": p, \"why\": \"install-test package a pushed record names\", \"bytes\": os.path.getsize(p)})\n"
            "    live = [(n, d) for n, d in _stranger_installs(root) if os.path.isdir(d)]\n"
            "    newest = max((n for n, _d in live), default=None)\n"
            "    for n, d in live:\n"
            "        if n != newest and _pushed(root, upstream, \"docs/findings/stranger_install/install_test_%d\" % n):\n"
            "            out.append({\"path\": d, \"why\": \"install-test unpack whose record is pushed, not the newest\", \"bytes\": _size(d)})\n"
            "    return out\n")
APPLY_OLD = ("        for p in items:\n"
             "            shutil.rmtree(p[\"path\"], ignore_errors=False)\n")
APPLY_NEW = ("        for p in items:\n"
             "            if os.path.isdir(p[\"path\"]):\n"
             "                shutil.rmtree(p[\"path\"], ignore_errors=False)\n"
             "            else:\n"
             "                os.remove(p[\"path\"])\n")
TEST_OLD = ("    shutil.rmtree(root, ignore_errors=True)\n"
            "    print(\"selftest ok\")\n")
TEST_NEW = ("    shutil.rmtree(root, ignore_errors=True)\n"
            "    _selftest_pushed()\n"
            "    print(\"selftest ok\")\n"
            "\n"
            "\n"
            "def _selftest_pushed():\n"
            "    \"\"\"The pushed rules, on a tree with a bare upstream (2026-10-11).\"\"\"\n"
            "    import tempfile\n"
            "    base = tempfile.mkdtemp(prefix=\"factory_retire_pushed_\")\n"
            "    up, root, pkgs = (os.path.join(base, x) for x in (\"up.git\", \"factory\", \"pkgs\"))\n"
            "    os.makedirs(pkgs)\n"
            "\n"
            "    def git(*a):\n"
            "        subprocess.run([\"git\", \"-C\", root, \"-c\", \"user.name=t\", \"-c\", \"user.email=t@t\"] + list(a),\n"
            "                       check=True, capture_output=True)\n"
            "\n"
            "    def write(rel, text):\n"
            "        p = os.path.join(root, *rel.split(\"/\"))\n"
            "        os.makedirs(os.path.dirname(p), exist_ok=True)\n"
            "        open(p, \"w\", encoding=\"utf-8\").write(text)\n"
            "    subprocess.run([\"git\", \"init\", \"-q\", \"--bare\", up], check=True, capture_output=True)\n"
            "    os.makedirs(root)\n"
            "    git(\"init\", \"-q\")\n"
            "    git(\"checkout\", \"-q\", \"-b\", \"main\")\n"
            "    write(\"docs/cold_runs/cold_1/NOTES.md\", \"run 1\\n\")\n"
            "    write(\"docs/releases/factory-v1.0.0.md\", \"notes\\n\")\n"
            "    write(\"docs/releases/factory-v1.1.0.md\", \"notes\\n\")\n"
            "    write(\"docs/findings/stranger_install/README.md\", \"made gabagool_factory_package_20260101_0000.zip\\n\")\n"
            "    for n in (1, 2):\n"
            "        os.makedirs(os.path.join(base, \"stranger_202_%d\" % n, \"gabagool\"))\n"
            "        write(\"docs/findings/stranger_install/install_test_%d.sh\" % n,\n"
            "              \"DEST='%s'\\n\" % os.path.join(base, \"stranger_202_%d\" % n, \"gabagool\"))\n"
            "    write(\"docs/findings/stranger_install/install_test_1/steps.txt\", \"ok\\n\")\n"
            "    git(\"add\", \"-A\")\n"
            "    git(\"commit\", \"-q\", \"-m\", \"records\")\n"
            "    git(\"remote\", \"add\", \"origin\", up)\n"
            "    git(\"push\", \"-q\", \"-u\", \"origin\", \"main\")\n"
            "    # committed after the push, so NOT pushed: run 2's record and test 2's\n"
            "    write(\"docs/cold_runs/cold_2/NOTES.md\", \"run 2\\n\")\n"
            "    write(\"docs/findings/stranger_install/install_test_2/steps.txt\", \"ok\\n\")\n"
            "    git(\"add\", \"-A\")\n"
            "    git(\"commit\", \"-q\", \"-m\", \"later\")\n"
            "    for n in range(1, 7):\n"
            "        os.makedirs(os.path.join(root, \"workspaces\", \"cold-%d-ws\" % n))\n"
            "    for f in (\"factory-v1.0.0\", \"factory-v1.1.0\", \"20260101_0000\", \"20260202_0000\"):\n"
            "        open(os.path.join(pkgs, \"gabagool_factory_package_%s.zip\" % f), \"wb\").write(b\"z\")\n"
            "    open(os.path.join(pkgs, \"someone_else.zip\"), \"wb\").write(b\"z\")\n"
            "    got = sorted(os.path.basename(p[\"path\"]) for p in plan(root, keep=12, keep_pushed=2, package_dir=pkgs))\n"
            "    want = [\"cold-1-ws\", \"gabagool_factory_package_20260101_0000.zip\",\n"
            "            \"gabagool_factory_package_factory-v1.0.0.zip\", \"stranger_202_1\"]\n"
            "    assert got == want, got\n"
            "    # with no upstream the pushed rules say nothing\n"
            "    git(\"branch\", \"--unset-upstream\")\n"
            "    assert plan(root, keep=12, keep_pushed=2, package_dir=pkgs) == []\n"
            "    shutil.rmtree(base, ignore_errors=True)\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def main():
    raw = TOOL.read_bytes()
    assert b"\r\n" not in raw, "factory_retire.py is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA, ("factory_retire.py is not the file this patch read", got)
    text = raw.decode("utf-8")
    assert "KEEP_PUSHED" not in text, "already applied"
    text = _once(text, DOC_OLD, DOC_NEW, "the docstring's rules")
    text = _once(text, CONST_OLD, CONST_NEW, "the constants")
    text = _once(text, HELP_OLD, HELP_NEW, "plan's signature and the helpers")
    text = _once(text, BODY_OLD, BODY_NEW, "the workspace rule and plan's return")
    text = _once(text, APPLY_OLD, APPLY_NEW, "--apply")
    text = _once(text, TEST_OLD, TEST_NEW, "the selftest's end")
    TOOL.write_bytes(text.encode("utf-8"))
    print("factory_retire.py: what a pushed record makes regenerable is retired")


if __name__ == "__main__":
    sys.exit(main())
