"""Run a GDScript probe inside a generated Godot project without touching it.

WHY A SHARED MODULE. `light_census.py` and `look_shots.py` both need the same
four things: find Godot, get a probe script to run inside a project, run it
headless, and read a machine-readable answer back out. factory_paths.py already
argues the case for not writing that twice -- two copies of a rule drift, and a
drifted second copy is the recurring defect of this toolchain. The same argument
applies here, plus one specific to these two: the mirroring rule below is a
safety property, and a safety property with two implementations has one.

WHY IT MIRRORS RATHER THAN INJECTS IN PLACE. An autoload is the only way to get
a script running alongside a scene without editing the scene, and registering
one means writing `[autoload]` into project.godot. Doing that to the project
under test would make the instrument a modification of the thing it measures --
and it would survive the run, because a crashed probe never gets to clean up.
Every run therefore copies the project to a scratch directory and edits the
copy. The source tree is opened read-only and is byte-identical afterwards.

The cost is a full copy per run, dominated by the .glb files: coldrun_pawn_job
is about 1 MB of geometry, so this is milliseconds. A site heavy enough for that
to hurt wants --scratch pointed at a fast disk rather than a cleverer scheme.

WHY THE ANSWER COMES BACK ON STDOUT. Godot's `user://` path depends on the
project name and the platform, so a report written to a file has to be located
before it can be read, and "the file is not there" and "the probe did not run"
look identical from here -- the failure mode walktest.py was built to avoid.
A fenced JSON block on stdout cannot be confused with a previous run's leftover:
if the fence is absent, the probe did not reach its own last line, and that is
reported as a failure to measure rather than as a measurement.

WHAT IT REFUSES TO DO. It never reports SKIP as success. Godot missing, the
project unopenable, the fence absent -- each raises ProbeFailed. A check that
did not run is not a check that passed, and this module has no mode in which it
pretends otherwise.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

# No factory_paths import here on purpose. This module is handed a project
# directory by its caller and never has to find the factory, so importing
# factory_root "for consistency" would be an unused import -- and an unused
# parameter is somebody's unfinished thought. The callers that DO need the root
# import it themselves.

#: Same list library_walk.py carries, and for the same measured reason: a shell
#: without LOT_GODOT set is how a sweep once "completed" twenty sites in zero
#: seconds each. Kept in sync by hand; if a third caller appears, hoist it.
GODOT_FALLBACKS = (
    r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe",
    r"C:\Godot\Godot_v4.7-stable_win64_console.exe",
)


class ProbeFailed(RuntimeError):
    """The measurement did not happen. Never raised for an unwelcome result."""


def find_godot(explicit=None):
    """--godot, then $LOT_GODOT, $DC_GODOT, the usual installs, then PATH.

    Deliberately the same order as walktest.py and library_walk.py. A tool that
    resolves Godot differently from its neighbours produces results nobody can
    line up against theirs.
    """
    for cand in ([explicit] if explicit else []) + [
            os.environ.get("LOT_GODOT"), os.environ.get("DC_GODOT")] + \
            list(GODOT_FALLBACKS) + ["godot4", "godot"]:
        if not cand:
            continue
        path = cand if os.sep in cand else shutil.which(cand)
        if path and os.path.exists(path):
            return path
    return None


def require_godot(explicit=None):
    godot = find_godot(explicit)
    if godot is None:
        raise ProbeFailed(
            "no Godot 4 binary found (looked at --godot, $LOT_GODOT, $DC_GODOT, "
            "the usual install paths, then PATH).\n"
            "  Nothing was measured. Set LOT_GODOT or pass --godot <path>.")
    return godot


def _display_wrapper():
    """On a Linux box with no X display, prefix with xvfb-run; else nothing.

    Only matters for the shot harness -- a census runs --headless and needs no
    display at all. Returned as a list so callers can just prepend it.
    """
    if os.name == "nt" or os.environ.get("DISPLAY"):
        return []
    xvfb = shutil.which("xvfb-run")
    if xvfb is None:
        return []
    return [xvfb, "-a", "-s", "-screen 0 1600x900x24"]


def mirror_project(project_dir, scratch=None):
    """Copy a Godot project to a scratch directory and return its path.

    The .godot import cache travels with it when present, so a project that has
    already been imported does not pay for it again. When it is absent the
    caller must run the import pass -- run_probe() does.
    """
    project_dir = os.path.abspath(project_dir)
    if not os.path.isfile(os.path.join(project_dir, "project.godot")):
        raise ProbeFailed(
            "no project.godot in " + project_dir + " -- that is not a Godot "
            "project. Nothing measured.")
    base = scratch or tempfile.mkdtemp(prefix="godot_probe_")
    dest = os.path.join(base, os.path.basename(project_dir.rstrip(os.sep)))
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(project_dir, dest)
    return dest


def add_autoload(mirror_dir, script_src, autoload_name, settings=None):
    """Copy a probe .gd into the mirror and register it as an autoload.

    `settings` is written as extra ProjectSettings entries, which is how a probe
    receives arguments: an autoload takes none, and baking values into the
    script would mean rewriting source text to pass a number.
    """
    shutil.copy2(script_src, os.path.join(mirror_dir,
                                          os.path.basename(script_src)))
    pg = os.path.join(mirror_dir, "project.godot")
    with open(pg, encoding="utf-8") as f:
        src = f.read()
    block = ["", "[autoload]", "",
             autoload_name + '="*res://' + os.path.basename(script_src) + '"']
    for section, values in (settings or {}).items():
        block += ["", "[" + section + "]", ""]
        for key, value in values.items():
            block.append(key + "=" + json.dumps(value))
    with open(pg, "w", encoding="utf-8") as f:
        f.write(src.rstrip("\n") + "\n" + "\n".join(block) + "\n")


def _fenced(stdout, begin, end):
    """The JSON between the probe's fences, or None if it never printed them."""
    m = re.search(re.escape(begin) + r"\s*(.*?)\s*" + re.escape(end),
                  stdout, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise ProbeFailed(
            "the probe printed its fences but the payload is not JSON (" +
            str(e) + "). That is a defect in the probe, not a result.")


def run_probe(project_dir, script_src, autoload_name, scene, begin, end,
              godot=None, settings=None, headless=True, extra_args=(),
              timeout=600, scratch=None, keep=False, verbose=False):
    """Mirror, instrument, run, and return (payload, stdout, mirror_dir).

    Raises ProbeFailed for every way the measurement can fail to happen. An
    unwelcome measurement is a return value; only a missing one is an error.
    """
    godot = godot or require_godot()
    mirror = mirror_project(project_dir, scratch)
    add_autoload(mirror, script_src, autoload_name, settings)

    if not os.path.isdir(os.path.join(mirror, ".godot")):
        # First open: import the .glb files. Without this the scene loads with
        # its ExtResources missing and the census counts an empty room.
        subprocess.run([godot, "--headless", "--path", mirror, "--import"],
                       capture_output=True, text=True, timeout=timeout)

    cmd = list(_display_wrapper()) if not headless else []
    cmd += [godot]
    if headless:
        cmd.append("--headless")
    cmd += ["--path", mirror] + list(extra_args) + [scene]
    if verbose:
        print("[probe] " + " ".join(cmd))
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ProbeFailed(
            "Godot did not exit within " + str(timeout) + "s. The probe quits "
            "the tree itself, so a timeout means it never reached that line. "
            "Nothing measured.")
    out = (r.stdout or "") + (r.stderr or "")
    payload = _fenced(out, begin, end)
    if payload is None:
        tail = "\n".join(out.strip().splitlines()[-25:])
        raise ProbeFailed(
            "the probe never printed its result fence, so nothing was "
            "measured. Godot exited " + str(r.returncode) + ".\n"
            "  Last of its output:\n" + tail)
    if not keep:
        shutil.rmtree(os.path.dirname(mirror), ignore_errors=True)
    return payload, out, mirror
