"""Can the export's sidecar step import its models once, holding the building bases for a small
second pass?

The sidecar step imports the package twice: a first pass with Godot's defaults (no sidecars yet),
then -- the sidecars rewritten (embedded images, the pins, since 0.187.0 the bake's marks), what
the first pass extracted deleted and the cache wiped -- a second full pass: about 88 s of cold run
9254's 241 s export. The one-import plan (`import_plan_probe.py`, refuted and corrected in the
README) ran the first pass with the models' final settings as `project.godot` defaults and then
re-imported only what the pins changed: 53.6 s where the passes had taken 121.6 -- and left 105
slab meshes greybox, because the worldskin skins a building's slabs by `load()`ing one of its
floor modules, which a model's FIRST import cannot promise is imported. Only `site_base*.glb`
loads a sibling (`zoo_worldskin.gd`'s two `load()` calls are in its base branch).

So B holds the bases out of the first pass:

  A   the export as it is (Level Factory 0.188.0)
  B   the sidecar step replaced in-process by `sidecars_once`: every `site_base*.glb` renamed to
      `.glb.held` (an extension Godot does not import); `project.godot` given the models' final
      settings as defaults (embedded images, Static Lightmaps when the export bakes); a first
      pass; the bases back; the pins, the bake's marks, and a model whose own second UV set is
      shader data set back to the Static it always shipped with; a second pass on the same cache
      -- the bases' first import with their siblings imported, the pinned textures, the changed
      models; `project.godot` back byte for byte

  C   as B, but the first pass holds EVERY model out (`sidecars_thrice`): B's models, imported
      before the shared textures were, each embedded a copy of them -- 1,463 surfaces in 461
      models (`sidecar_once_probe.draft1.out.txt`, its digests read in full). Three passes over
      three sets: the textures and the rest; every model but the bases; the bases and what the
      bake's marks change

and prints for each the export's wall time, the sidecar step's and each pass's, each light-bake
`--import`'s; the gates from the export's own reports; then digests every model as Godot loads
it from each export's kept cache (`import_digest.gd`, `--full`) and compares the first arm's with
each other's, saying for each differing surface whether its texture alone moved. The workspace's
own package is held aside and put back. It measures and prints.

    python docs/findings/grader_speed/sidecar_once_probe.py <workspace> <mission> [--arms A,C]

Arms F and G call Level Factory 0.189.0's `_filtered_shared_textures`, which 0.190.0 replaced
(compressed everywhere: `_normal_map_shared_textures`); they ran on 0.189.0 and are kept as the
record, and fail on anything after it. Arms A, O and D read nothing it removed.
"""
import collections
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import time
from pathlib import Path

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
sys.path.insert(0, F)
X = os.path.join(F, "_scratch", "sidecar_once")
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
DIGEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_digest.gd")
TIMES = collections.defaultdict(list)


def first_pass_defaults(text, lightmaps):
    """`project.godot`'s text with the models' final settings in `[importer_defaults] scene`."""
    keys = {"gltf/embedded_image_handling": 3}
    if lightmaps:
        keys["meshes/light_baking"] = 2
    lines = ",\n".join('"%s": %s' % (k, v) for k, v in keys.items())
    section, head = "[importer_defaults]\n", "scene={\n"
    if section in text and head in text[text.index(section):]:
        i = text.index(head, text.index(section)) + len(head)
        j = text.index("}", i)
        body = text[i:j].rstrip("\n")
        return text[:i] + (body + ",\n" if body.strip() else "") + lines + "\n" + text[j:]
    if section in text:
        k = text.index(section) + len(section)
        return text[:k] + "\n" + head + lines + "\n}\n" + text[k:]
    return text.rstrip("\n") + "\n\n" + section + "\n" + head + lines + "\n}\n"


def sidecars_once(export_dir, godot_executable, *, bake_spawned=None):
    from packages.exporting import export as E
    from packages.exporting import light_bake as LB
    from packages.exporting.occluders import unimported_models
    if not godot_executable:
        return 0
    export_dir = Path(export_dir)
    log_path = export_dir.parent / (export_dir.name + ".import.log")
    log_path.unlink(missing_ok=True)
    passes = []

    def one_pass():
        t = time.time()
        done = subprocess.run([str(godot_executable), "--headless", "--path", str(export_dir),
                               "--import"], capture_output=True, timeout=1200)
        passes.append(done.returncode)
        with open(log_path, "ab") as fh:
            fh.write(("==== import pass %d: exit %s\n" % (len(passes), done.returncode)).encode())
            fh.write((done.stdout or b"") + (done.stderr or b""))
        TIMES["import pass"].append(round(time.time() - t, 1))

    def verified():
        left = []
        for _ in range(E.IMPORT_PASSES):
            one_pass()
            left = unimported_models(export_dir)
            if not left:
                return
        raise E.ExportImportError("the import left %d model(s) unimported; first %s" % (len(left), left[0]))

    lightmaps = bake_spawned is not None
    held = []
    for p in sorted(export_dir.rglob("site_base*.glb")):
        if ".godot" in p.parts:
            continue
        q = p.with_name(p.name + ".held")
        p.rename(q)
        held.append((q, p))
    print("[once] B: %d base(s) held out of the first pass" % len(held), flush=True)
    proj = export_dir / "project.godot"
    kept = proj.read_bytes()
    eol = "\r\n" if b"\r\n" in kept else "\n"
    proj.write_bytes(first_pass_defaults(kept.decode("utf-8").replace("\r\n", "\n"), lightmaps)
                     .replace("\n", eol).encode("utf-8"))
    try:
        try:
            verified()
        finally:
            for q, p in held:
                q.rename(p)
        E._pin_shared_texture_imports(export_dir)
        E._pin_sign_texture_imports(export_dir)
        if lightmaps:
            marks = LB.mark_imports(export_dir, bake_spawned)
            static = 0
            for rel in marks["dynamic"]:
                side = export_dir / (rel + ".import")
                if not side.is_file():
                    continue
                text = side.read_text(encoding="utf-8")
                new = re.sub(r"^meshes/light_baking=\d+$", "meshes/light_baking=1", text, flags=re.M)
                if new != text:
                    side.write_text(new, encoding="utf-8", newline="\n")
                    static += 1
            print("[once] B: marks %s; %d own-second-UV model(s) set back to Static"
                  % ({k: len(v) for k, v in marks.items()}, static), flush=True)
        verified()
    finally:
        proj.write_bytes(kept)
    return len(list(export_dir.rglob("*.import")))


def sidecars_thrice(export_dir, godot_executable, *, bake_spawned=None):
    """Arm C: B's first pass held EVERY model out, because B's models, imported before the shared
    textures were, embedded a copy of each (1,463 surfaces in 461 models, where A's reference the
    shared `_tex/` files). Three passes over three sets: the textures and everything that is not
    a model; then every model but the bases, the textures already imported; then the bases, their
    floor modules imported, with the models the bake's marks change."""
    from packages.exporting import export as E
    from packages.exporting import light_bake as LB
    from packages.exporting.occluders import unimported_models
    if not godot_executable:
        return 0
    export_dir = Path(export_dir)
    log_path = export_dir.parent / (export_dir.name + ".import.log")
    log_path.unlink(missing_ok=True)
    passes = []

    def one_pass():
        t = time.time()
        done = subprocess.run([str(godot_executable), "--headless", "--path", str(export_dir),
                               "--import"], capture_output=True, timeout=1200)
        passes.append(done.returncode)
        with open(log_path, "ab") as fh:
            fh.write(("==== import pass %d: exit %s\n" % (len(passes), done.returncode)).encode())
            fh.write((done.stdout or b"") + (done.stderr or b""))
        TIMES["import pass"].append(round(time.time() - t, 1))
        print("[once] after import pass %d: %s" % (len(passes), pin_census(export_dir)), flush=True)

    def verified():
        left = []
        for _ in range(E.IMPORT_PASSES):
            one_pass()
            left = unimported_models(export_dir)
            if not left:
                return
        raise E.ExportImportError("the import left %d model(s) unimported; first %s" % (len(left), left[0]))

    lightmaps = bake_spawned is not None
    held = {}
    for p in sorted(export_dir.rglob("*.glb")):
        if ".godot" in p.parts:
            continue
        q = p.with_name(p.name + ".held")
        p.rename(q)
        held[p] = q
    bases = [p for p in held if p.name.startswith("site_base")]
    print("[once] C: %d model(s) held out of the first pass, %d of them bases" % (len(held), len(bases)),
          flush=True)
    proj = export_dir / "project.godot"
    kept = proj.read_bytes()
    eol = "\r\n" if b"\r\n" in kept else "\n"
    proj.write_bytes(first_pass_defaults(kept.decode("utf-8").replace("\r\n", "\n"), lightmaps)
                     .replace("\n", eol).encode("utf-8"))
    try:
        try:
            verified()                       # the textures and the rest
            E._pin_shared_texture_imports(export_dir)
            E._pin_sign_texture_imports(export_dir)
            for p, q in held.items():
                if p not in bases:
                    q.rename(p)
            verified()                       # every model but the bases
        finally:
            for p, q in held.items():
                if q.exists():
                    q.rename(p)
        if lightmaps:
            marks = LB.mark_imports(export_dir, bake_spawned)
            static = 0
            for rel in marks["dynamic"]:
                side = export_dir / (rel + ".import")
                if not side.is_file():
                    continue
                text = side.read_text(encoding="utf-8")
                new = re.sub(r"^meshes/light_baking=\d+$", "meshes/light_baking=1", text, flags=re.M)
                if new != text:
                    side.write_text(new, encoding="utf-8", newline="\n")
                    static += 1
            print("[once] C: marks %s; %d own-second-UV model(s) set back to Static"
                  % ({k: len(v) for k, v in marks.items()}, static), flush=True)
        verified()                           # the bases, and what the marks changed
    finally:
        proj.write_bytes(kept)
    return len(list(export_dir.rglob("*.import")))


def pin_census(export_dir):
    """The shared textures' sidecars under `_tex/`: pinned (mipmaps on, alpha border off),
    defaulted (neither), or mixed -- `docs/findings/texture_pins/pin_phase_probe.py`'s count."""
    c = collections.Counter()
    for r, _, fs in os.walk(export_dir):
        if os.path.basename(r) != "_tex" or ".godot" in r.replace("\\", "/").split("/"):
            continue
        for f in fs:
            if f.endswith(".png.import"):
                text = open(os.path.join(r, f), encoding="utf-8", errors="replace").read()
                mip = "mipmaps/generate=true" in text
                fab = "process/fix_alpha_border=false" in text
                c["pinned" if (mip and fab) else "defaulted" if (not mip and not fab) else "mixed"] += 1
    return dict(c)


def sidecars_four(export_dir, godot_executable, *, bake_spawned=None):
    """Arm E: C, with the pinned textures re-imported in a pass of their own, every model still
    held, before any model's first import -- C reset 26 shared textures' pins, and the guess is
    that its second pass imported models whose textures had just been re-pinned and not yet
    re-imported, several at once. Prints the pin census after every pass."""
    from packages.exporting import export as E
    from packages.exporting import light_bake as LB
    from packages.exporting.occluders import unimported_models
    if not godot_executable:
        return 0
    export_dir = Path(export_dir)
    log_path = export_dir.parent / (export_dir.name + ".import.log")
    log_path.unlink(missing_ok=True)
    passes = []

    def one_pass(label):
        t = time.time()
        done = subprocess.run([str(godot_executable), "--headless", "--path", str(export_dir),
                               "--import"], capture_output=True, timeout=1200)
        passes.append(done.returncode)
        with open(log_path, "ab") as fh:
            fh.write(("==== import pass %d: exit %s\n" % (len(passes), done.returncode)).encode())
            fh.write((done.stdout or b"") + (done.stderr or b""))
        TIMES["import pass"].append(round(time.time() - t, 1))
        print("[once] E: after %-34s %s" % (label, pin_census(export_dir)), flush=True)

    def verified(label):
        left = []
        for _ in range(E.IMPORT_PASSES):
            one_pass(label)
            left = unimported_models(export_dir)
            if not left:
                return
        raise E.ExportImportError("the import left %d model(s) unimported; first %s" % (len(left), left[0]))

    lightmaps = bake_spawned is not None
    held = {}
    for p in sorted(export_dir.rglob("*.glb")):
        if ".godot" in p.parts:
            continue
        q = p.with_name(p.name + ".held")
        p.rename(q)
        held[p] = q
    bases = [p for p in held if p.name.startswith("site_base")]
    proj = export_dir / "project.godot"
    kept = proj.read_bytes()
    eol = "\r\n" if b"\r\n" in kept else "\n"
    proj.write_bytes(first_pass_defaults(kept.decode("utf-8").replace("\r\n", "\n"), lightmaps)
                     .replace("\n", eol).encode("utf-8"))
    try:
        try:
            verified("the textures and the rest")
            E._pin_shared_texture_imports(export_dir)
            E._pin_sign_texture_imports(export_dir)
            print("[once] E: after %-34s %s" % ("the pins", pin_census(export_dir)), flush=True)
            verified("the pinned textures, models held")
            for p, q in held.items():
                if p not in bases:
                    q.rename(p)
            verified("every model but the bases")
        finally:
            for p, q in held.items():
                if q.exists():
                    q.rename(p)
        if lightmaps:
            marks = LB.mark_imports(export_dir, bake_spawned)
            for rel in marks["dynamic"]:
                side = export_dir / (rel + ".import")
                if not side.is_file():
                    continue
                text = side.read_text(encoding="utf-8")
                new = re.sub(r"^meshes/light_baking=\d+$", "meshes/light_baking=1", text, flags=re.M)
                if new != text:
                    side.write_text(new, encoding="utf-8", newline="\n")
        verified("the bases and the marks")
    finally:
        proj.write_bytes(kept)
    return len(list(export_dir.rglob("*.import")))


def sidecars_three_filtered(export_dir, godot_executable, *, bake_spawned=None):
    """Arm F: C's three passes, the filtered-texture set read BEFORE any model is held. C and E
    re-pinned the same 26 shared textures at the end: `_filtered_shared_textures` reads the
    models' glTF to find the textures every sampler filters (pinned VRAM, 0.128.0), and with
    every model renamed `.glb.held` it found none, so those 26 were pinned lossless until the
    read-back after the last import (0.182.0) put them right. E's census showed no pin lost
    inside the sidecar step, so E's extra pass for the textures alone is not kept."""
    from packages.exporting import export as E
    filtered = E._filtered_shared_textures(Path(export_dir))
    real = E._filtered_shared_textures
    E._filtered_shared_textures = lambda d: filtered
    print("[once] F: %d shared texture(s) filtered by every sampler, read before the models are held"
          % len(filtered), flush=True)
    try:
        return sidecars_thrice(export_dir, godot_executable, bake_spawned=bake_spawned)
    finally:
        E._filtered_shared_textures = real


PARTIAL_SIDECAR = ('[remap]\n\nimporter="scene"\nimporter_version=1\ntype="PackedScene"\n\n'
                   '[params]\n\nmeshes/light_baking=%d\ngltf/embedded_image_handling=3\n')


def sidecars_g(export_dir, godot_executable, *, bake_spawned=None):
    """Arm G: F, with every model imported exactly once. F imported the six models whose own
    second UV set is shader data with the defaults' Static Lightmaps, set them back to Static,
    and imported them again -- and that re-import embedded their shared texture (3 surfaces in
    three trees) and reset 2 textures' pins: a model re-imported after its textures are imported
    is the race 0.182.0 backstops. So the models whose final light baking is not the default
    (Static for a shader second UV set, Dynamic for a spawned one) are held with the bases and
    imported in the third pass, each from a sidecar written beforehand with its final settings."""
    from packages.exporting import export as E
    from packages.exporting import light_bake as LB
    from packages.exporting.occluders import unimported_models
    if not godot_executable:
        return 0
    export_dir = Path(export_dir)
    filtered = E._filtered_shared_textures(export_dir)
    real_filtered = E._filtered_shared_textures
    E._filtered_shared_textures = lambda d: filtered
    log_path = export_dir.parent / (export_dir.name + ".import.log")
    log_path.unlink(missing_ok=True)
    passes = []

    def one_pass():
        t = time.time()
        done = subprocess.run([str(godot_executable), "--headless", "--path", str(export_dir),
                               "--import"], capture_output=True, timeout=1200)
        passes.append(done.returncode)
        with open(log_path, "ab") as fh:
            fh.write(("==== import pass %d: exit %s\n" % (len(passes), done.returncode)).encode())
            fh.write((done.stdout or b"") + (done.stderr or b""))
        TIMES["import pass"].append(round(time.time() - t, 1))
        print("[once] after import pass %d: %s" % (len(passes), pin_census(export_dir)), flush=True)

    def verified():
        left = []
        for _ in range(E.IMPORT_PASSES):
            one_pass()
            left = unimported_models(export_dir)
            if not left:
                return
        raise E.ExportImportError("the import left %d model(s) unimported; first %s" % (len(left), left[0]))

    lightmaps = bake_spawned is not None
    special = {}
    if lightmaps:
        wanted = set(bake_spawned)
        for p in sorted(export_dir.rglob("*.glb")):
            if ".godot" in p.parts:
                continue
            rel = p.relative_to(export_dir).as_posix()
            if rel in wanted:
                special[p] = LB.DYNAMIC
            elif LB.glb_has_uv2(p):
                special[p] = 1
    held = {}
    for p in sorted(export_dir.rglob("*.glb")):
        if ".godot" in p.parts:
            continue
        q = p.with_name(p.name + ".held")
        p.rename(q)
        held[p] = q
    late = [p for p in held if p.name.startswith("site_base") or p in special]
    print("[once] G: %d model(s) held; %d imported last (%d bases, %d with a light baking of their own)"
          % (len(held), len(late), sum(p.name.startswith("site_base") for p in late), len(special)), flush=True)
    proj = export_dir / "project.godot"
    kept = proj.read_bytes()
    eol = "\r\n" if b"\r\n" in kept else "\n"
    proj.write_bytes(first_pass_defaults(kept.decode("utf-8").replace("\r\n", "\n"), lightmaps)
                     .replace("\n", eol).encode("utf-8"))
    try:
        try:
            verified()                       # the textures and the rest
            E._pin_shared_texture_imports(export_dir)
            E._pin_sign_texture_imports(export_dir)
            for p, q in held.items():
                if p not in late:
                    q.rename(p)
            verified()                       # every model imported with the defaults
        finally:
            for p, q in held.items():
                if q.exists():
                    q.rename(p)
        # A sidecar written by hand is not a new import to Godot. Its first run carried two keys
        # and came out without the worldskin (the project's defaults reach only a file with no
        # sidecar); its second added the import script and came out `gltf/texture_map_mode=0`
        # where every new import reads 1 -- a key a sidecar lacks takes the value an import from
        # before the key existed would have had. So the late models' sidecars are whole: every
        # `[params]` line of a model the second pass imported, light baking set to theirs.
        donor = next(p for p in held if p not in late)
        params = Path(str(donor) + ".import").read_text(encoding="utf-8")
        params = params[params.index("[params]"):]
        assert "meshes/light_baking=" in params, donor
        head = '[remap]\n\nimporter="scene"\nimporter_version=1\ntype="PackedScene"\n\n'
        for p, value in special.items():
            body = re.sub(r"^meshes/light_baking=\d+$", "meshes/light_baking=%d" % value, params, flags=re.M)
            Path(str(p) + ".import").write_text(head + body, encoding="utf-8", newline="\n")
        if lightmaps:
            marks = LB.mark_imports(export_dir, bake_spawned)
            print("[once] G: marks %s" % {k: len(v) for k, v in marks.items()}, flush=True)
        verified()                           # the bases, the models with their own light baking
    finally:
        proj.write_bytes(kept)
        E._filtered_shared_textures = real_filtered
    got = collections.Counter()
    for p, value in special.items():
        text = Path(str(p) + ".import").read_text(encoding="utf-8")
        lb = re.search(r"^meshes/light_baking=(\d+)$", text, re.M)
        script = "import_script/path=\"res://" in text
        got["%s wanted %d, sidecar %s, worldskin %s" % (p.name[:24], value, lb.group(1) if lb else "-",
                                                        script)] += 1
    print("[once] G: the late models' sidecars after their import: %s" % dict(got), flush=True)
    return len(list(export_dir.rglob("*.import")))


def step_of(commit):
    """`_write_import_sidecars` as Level Factory had it at `commit`, read from git and compiled
    as a module of its own -- arm O, the step as it was, beside the applied one."""
    import types
    lf = os.path.join(F, "level_factory")
    src = subprocess.run(["git", "-C", lf, "show", "%s:packages/exporting/export.py" % commit],
                         capture_output=True, text=True, check=True).stdout
    mod = types.ModuleType("export_at_%s" % commit)
    mod.__file__ = os.path.join(lf, "packages", "exporting", "export.py")
    sys.modules[mod.__name__] = mod   # a dataclass looks its module up there
    exec(compile(src, "export_at_%s.py" % commit, "exec"), mod.__dict__)
    return mod._write_import_sidecars


def timed(module, name, label):
    real = getattr(module, name)

    def wrapped(*a, **k):
        t = time.time()
        try:
            return real(*a, **k)
        finally:
            TIMES[label].append(round(time.time() - t, 1))
    setattr(module, name, wrapped)


def reports(pkg):
    def j(n):
        p = os.path.join(pkg, n)
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    g, m, lb, o, c = (j("greybox_skin_scan.json"), j("merge_empties.json"), j("light_bake.json"),
                      j("occluders.json"), j("export_closure_scan.json"))
    out = {}
    if g:
        out["greybox"] = {k: g.get(k) for k in ("greybox_surfaces", "greybox_area_m2", "slab_surfaces", "themed")}
    if m:
        rows = m.get("scenes") or []
        out["merge"] = {"meshes_in": sum(r["meshes_in"] for r in rows), "merged": sum(r["merged"] for r in rows),
                        "colliders": sum(r["colliders"] for r in rows), "ok": m.get("ok")}
    if lb:
        out["bake"] = {"ok": lb.get("ok"), "users": (lb.get("result") or {}).get("users"),
                       "editor_s": lb.get("editor_s"),
                       "imports": {k: len(v) for k, v in (lb.get("imports") or {}).items()}}
    if o:
        out["occluders"] = {"occluders": o.get("occluders"), "ok": o.get("ok")}
    if c:
        out["closure"] = {"ok": c.get("ok"), "missing": c.get("missing_resource_count"),
                          "issues": len(c.get("issues") or [])}
    return out


def run_arm(arm, ws, mission, exports):
    from packages.exporting import export, light_bake
    if arm == "B":
        export._write_import_sidecars = sidecars_once
    if arm == "C":
        export._write_import_sidecars = sidecars_thrice
    if arm == "E":
        export._write_import_sidecars = sidecars_four
    if arm == "F":
        export._write_import_sidecars = sidecars_three_filtered
    if arm == "G":
        export._write_import_sidecars = sidecars_g
    if arm == "O":   # the step as Level Factory 0.188.0 had it (commit 157d50e)
        export._write_import_sidecars = step_of("157d50e")
    if arm == "D":
        # the shared textures' 3D detection pinned off: the bake's editor re-encodes every one
        # it finds used in 3D when it opens the scene (its own log), lossless pins included
        export.SHARED_TEX_PINS = dict(export.SHARED_TEX_PINS, **{"detect_3d/compress_to": "0"})
    timed(export, "_write_import_sidecars", "sidecar step")
    timed(light_bake, "_import", "light-bake --import")
    if "--phases" in sys.argv:
        # the pin census before and after each phase that follows the sidecar step
        from packages.exporting import greybox_skin, merge_empties, occluders

        def censused(module, name, label):
            real = getattr(module, name)

            def wrapped(*a, **k):
                d = a[0] if a else k.get("export_dir")
                print("[once] %s: before %-26s %s" % (arm, label, pin_census(d)), flush=True)
                try:
                    return real(*a, **k)
                finally:
                    print("[once] %s: after  %-26s %s" % (arm, label, pin_census(d)), flush=True)
            setattr(module, name, wrapped)
        censused(occluders, "emit", "the occluder bake")
        censused(merge_empties, "merge", "the Empties' merge")
        censused(light_bake, "mark_imports", "the bake's marks")
        censused(light_bake, "_import", "a light-bake --import")
        censused(greybox_skin, "measure", "the greybox census")
    pins = {}
    real_repin = export._repin_after_imports

    def repin(d):
        r = real_repin(d)
        pins.update(r)
        return r
    export._repin_after_imports = repin
    sys.argv = ["level_factory", "-C", ws, "export", mission, "--mode", "portable-godot"]
    t = time.time()
    code = 0
    try:
        runpy.run_module("level_factory", run_name="__main__", alter_sys=True)
    except SystemExit as exc:
        code = exc.code
    wall = time.time() - t
    pkg = os.path.join(exports, "LF_%s.portable-godot" % mission)
    print("[once] %s: exit %s, the export %.1f s; %s" % (arm, code, wall, dict(TIMES)), flush=True)
    print("[once] %s: pins %s" % (arm, {k: v for k, v in pins.items() if not isinstance(v, (list, dict))}),
          flush=True)
    for k, v in reports(pkg).items():
        print("[once] %s: %-9s %s" % (arm, k, v), flush=True)
    log = pkg + ".lightbake.log"
    if os.path.exists(log):
        text = open(log, encoding="utf-8", errors="replace").read()
        opened = re.search(r"BAKE the scene opened after (\d+) ms", text)
        print("[once] %s: the bake's editor opened the scene after %s ms; textures it re-encoded as "
              "used in 3D %d, as normal maps %d"
              % (arm, opened.group(1) if opened else "?", text.count("detected as used in 3D. Enabling"),
                 text.count("detected as used as a normal map")), flush=True)
    dst = os.path.join(X, arm)
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    for n in os.listdir(exports):
        if n.startswith("LF_%s." % mission):
            shutil.move(os.path.join(exports, n), os.path.join(dst, n))


def digests(arm, mission):
    """Every model as Godot loads it from the arm's package with its kept cache as `.godot`."""
    pkg = os.path.join(X, arm, "LF_%s.portable-godot" % mission)
    kept = pkg + ".import_cache"
    if not os.path.isdir(kept):
        print("[once] %s: no kept cache beside the package" % arm, flush=True)
        return {}, {}
    shutil.move(kept, os.path.join(pkg, ".godot"))
    t = time.time()
    p = subprocess.run([GODOT, "--headless", "--path", pkg, "--import"], capture_output=True, timeout=900)
    t_check = time.time() - t
    q = subprocess.run([GODOT, "--headless", "--path", pkg, "-s", DIGEST, "--", "--full"],
                       capture_output=True, text=True, timeout=900)
    out, lines = {}, collections.defaultdict(list)
    for ln in q.stdout.splitlines():
        if ln.startswith("DIGEST "):
            _, path, h = ln.split(" ", 2)
            out[path] = h
        elif ln.startswith("LINE "):
            _, path, rest = ln.split(" ", 2)
            lines[path].append(rest)
    print("[once] %s: its kept cache checked by --import, exit %d, %.1f s; %d models digested, %d unloadable"
          % (arm, p.returncode, t_check, len(out), sum(v == "UNLOADABLE" for v in out.values())), flush=True)
    return out, lines


def compare_digests(a, b, label):
    """How many models load differently, and how: a surface whose texture alone moved (from a
    shared `_tex/` file into the model, or otherwise), or anything else."""
    (da, la), (db, lb) = a, b
    diff = sorted(k for k in set(da) | set(db) if da.get(k) != db.get(k))
    kinds = collections.Counter()
    first_other = None
    for k in diff:
        x, y = la.get(k, []), lb.get(k, [])
        if len(x) != len(y):
            kinds["different node or surface count"] += 1
            first_other = first_other or k
            continue
        for u, v in zip(x, y):
            if u == v:
                continue
            if re.sub(r" tex=.*$", "", u) == re.sub(r" tex=.*$", "", v):
                moved = "/_tex/" in u and v.split(" tex=")[-1].split(" ")[0].endswith(".glb")
                kinds["texture only, shared file -> in the model" if moved else "texture only, other"] += 1
            else:
                kinds["other"] += 1
                first_other = first_other or (k, u, v)
    print("[once] %s: %d and %d models; digests differing %d; differing surfaces or lines %s%s"
          % (label, len(da), len(db), len(diff), dict(kinds),
             "; first other %s" % (first_other,) if first_other else ""), flush=True)


def main():
    ws, mission = os.path.abspath(sys.argv[1]), sys.argv[2]
    exports = os.path.join(ws, ".level_factory", "exports")
    if "--arm" in sys.argv:
        run_arm(sys.argv[sys.argv.index("--arm") + 1], ws, mission, exports)
        return
    held_dir = os.path.join(X, "held")
    os.makedirs(held_dir, exist_ok=True)
    assert not os.listdir(held_dir), "a held package is already waiting in %s" % held_dir
    held = [n for n in os.listdir(exports) if n.startswith("LF_%s." % mission)]
    for n in held:
        shutil.move(os.path.join(exports, n), os.path.join(held_dir, n))
    print("[once] held aside: %s" % held, flush=True)
    arms = (sys.argv[sys.argv.index("--arms") + 1].split(",") if "--arms" in sys.argv else ["A", "B"])
    try:
        passed = [f for f in ("--phases",) if f in sys.argv]   # each arm's process sees the flags
        for arm in arms:
            subprocess.run([sys.executable, "-u", os.path.abspath(__file__), ws, mission, "--arm", arm]
                           + passed, check=False)
        got = {arm: digests(arm, mission) for arm in arms}
        for arm in arms[1:]:
            compare_digests(got[arms[0]], got[arm], "%s against %s" % (arms[0], arm))
    finally:
        for n in os.listdir(exports):
            if n.startswith("LF_%s." % mission):
                p = os.path.join(exports, n)
                shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p)
        for n in held:
            shutil.move(os.path.join(held_dir, n), os.path.join(exports, n))
        print("[once] the run's package restored; A and B kept in %s until read" % X, flush=True)


if __name__ == "__main__":
    main()
