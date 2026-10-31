"""Level Factory 0.274.0: a window with a painted pane occludes.

bake_occluders.gd classifies a window_ module carrying Zoo's `_p<state>` pane token as solid.

Proven: tests/unit/test_occluders_painted_panes.py fails on 0.273.0 (fails_on_old.out.txt); the clone's suite
(suite_clone.out.txt); the slice re-walked and priced (slice 22c).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'level_factory'
PINS = {'CHANGELOG.md': 'f0ef4295e6771061', 'VERSION': '6bebce8f0aaa744f', 'assets/godot/bake_occluders.gd': '546eeaa7f2b91e26'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [0.273.0] - the draw distance on the merged meshes, and cover keeps its silhouette\n', '## [0.274.0] - a window with a painted pane occludes\n\n### Fixed\n- **`bake_occluders.gd`**: every `window_` module was porous -- "the opening IS the module" -- and a PAINTED pane is\n  not an opening: Zoo (>= 1.64.0) paints it over the sealed, full-thickness collider Deli Counter cuts every window\n  with, and names it `_p<state>`. So a window carrying one (`PAINTED_PANE_TOKENS`: `_plit`, `_pdark`, `_pboarded`,\n  `_pshop_`) is now solid; a clear window, a glazed one and every doorway stay as they were, and the existing hole\n  check still refuses a module whose mesh leaves its aperture open. Every Empty\'s painted windows had been porous\n  since their panes were painted; what found it was Deli Counter 0.295.0 painting the slice\'s bank\'s 32 new upper\n  windows -- from the camera socket on that storey 259 -> 1,224 draws, the culler open behind every one. On the\n  slice: occluders 1,918 -> 2,177, porous modules 388 -> 129; that view 1,224 -> 624.\n\nOn the slice (slice 22 against slice 21, Level Factory 0.274.0, Deli Counter 0.295.0 and Lux 0.82.0 together; the factory\'s docs/findings/slice_look/, perf_s22c_*): the median heading +0 draws and -0.08 ms p95, the worst street view (longest_sightline yaw 90) 2,312 -> 2,320; the two camera sockets set on building faces at upper-storey height +134 to +365, with the same objects in their frustum (+-16), so what moved there is culling, not submissions added -- not attributed further. Tests: tests/unit/test_occluders_painted_panes.py (a real Godot classify; fails on 0.273.0).\n\n## [0.273.0] - the draw distance on the merged meshes, and cover keeps its silhouette\n')], 'VERSION': [('lines 1-1', '0.273.0', '0.274.0')], 'assets/godot/bake_occluders.gd': [('lines 39-40', '##\n## `wallEnd_` is solid brick and is skipped: it is a corner filler, and the\n', "##\n##   solid   a window_ with a PAINTED pane (0.274.0): Zoo names one `_p<state>`\n##           (`zoo_keeper.core.kit`, 1.64.0) -- an Empty's windows and a storey\n##           nobody reaches (Deli Counter 0.295.0) -- and the pane is painted\n##           over a sealed, full-thickness collider: nothing is seen through\n##           it. Left porous, the slice's bank's 32 painted upper windows\n##           opened the culler: from its camera socket on that storey 259 ->\n##           1,224 draws, everything behind its walls submitted.\n##\n## `wallEnd_` is solid brick and is skipped: it is a corner filler, and the\n"), ('lines 61-62', 'const GLASS_TOKEN := "mglass"\n\n', 'const GLASS_TOKEN := "mglass"\n#: A painted pane\'s state as Zoo names it (`_p<state>`): every state Deli\n#: Counter\'s `empty_panes` draws begins with one of these.\nconst PAINTED_PANE_TOKENS := ["_plit", "_pdark", "_pboarded", "_pshop_"]\n\n'), ('lines 143-144', '\t\tif s.begins_with(p):\n\t\t\treturn "porous"\n', '\t\tif s.begins_with(p):\n\t\t\tif p == "window_":\n\t\t\t\tfor tok in PAINTED_PANE_TOKENS:\n\t\t\t\t\tif s.contains(tok):\n\t\t\t\t\t\treturn "solid"\n\t\t\treturn "porous"\n')]}
WHOLE = {}
NEW_FILES = {'tests/unit/test_occluders_painted_panes.py': '"""A window with a painted pane occludes (0.274.0).\n\n`bake_occluders.gd` left every `window_` module porous: "the opening IS the module". A PAINTED pane is not an opening:\nZoo paints it over the sealed, full-thickness collider Deli Counter cuts every window with, and names it `_p<state>`\n(`zoo_keeper.core.kit`, 1.64.0) -- every Empty\'s windows, and since Deli Counter 0.295.0 a storey nobody reaches. Left\nporous, the slice\'s bank\'s 32 painted upper windows opened the culler: from the camera socket on that storey, 259 ->\n1,224 draws (the factory\'s `docs/findings/slice_look/`, slice 22).\n\nTHE GODOT HALF RUNS HERE FOR REAL: `classify` is called on real module stems from the slice\'s package. Skipped where no\nGodot is installed. FAILS ON 0.273.0: a painted window classifies `porous`.\n\nRun:  python -m pytest tests/unit/test_occluders_painted_panes.py -q\n"""\nfrom __future__ import annotations\n\nimport json\nimport os\nimport shutil\nimport subprocess\nfrom pathlib import Path\n\nimport pytest\n\nSCRIPT = Path(__file__).resolve().parents[2] / "assets" / "godot" / "bake_occluders.gd"\n\n#: real stems from the slice\'s package, and what each must classify as\nSTEMS = {\n    "window_delco_1997_01_w160_plit_blind_cool_o92c863": "solid",        # the bank\'s painted upper window\n    "window_delco_1997_01_w95_mbrick_orange_plit_blind_cool_o173e47": "solid",  # an Empty\'s\n    "window_delco_1997_01_w95_mbrick_orange_pdark_o173e47": "solid",\n    "window_delco_1997_01_w95_mbrick_orange_pboarded_o173e47": "solid",\n    "window_delco_1997_01_w300_pshop_deli_o173e47": "solid",\n    "window_delco_1997_01_w160_o92c863": "porous",                       # a clear window: the opening is the module\n    "window_delco_1997_01_w240_mglass_o92c863": "glass",\n    "doorway_delco_1997_01_w180_plit_o92c863": "porous",                 # only a window\'s pane is painted shut\n    "wall_delco_1997_01_w300": "solid",\n}\n\nPROBE = """extends SceneTree\nfunc _initialize() -> void:\n\tvar b: Object = load("res://bake_occluders.gd").new()\n\tvar out := {}\n\tfor s in %s:\n\t\tout[s] = b.call("classify", s)\n\tprint("RESULT " + JSON.stringify(out))\n\tquit(0)\n"""\n\n\ndef _godot() -> str | None:\n    for env in ("LF_GODOT", "DC_GODOT", "LOT_GODOT"):\n        p = os.environ.get(env)\n        if p and Path(p).is_file():\n            return p\n    usual = Path("C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe")\n    if usual.is_file():\n        return str(usual)\n    return shutil.which("godot")\n\n\n@pytest.mark.skipif(_godot() is None, reason="no Godot binary; this test calls classify")\ndef test_a_painted_window_is_solid_and_a_clear_one_stays_porous(tmp_path):\n    proj = tmp_path / "p"\n    proj.mkdir()\n    (proj / "project.godot").write_text(\'config_version=5\\n[application]\\nconfig/name="occ"\\n\', encoding="utf-8")\n    shutil.copyfile(SCRIPT, proj / "bake_occluders.gd")\n    (proj / "probe.gd").write_text(PROBE % json.dumps(sorted(STEMS)), encoding="utf-8")\n    r = subprocess.run([_godot(), "--headless", "--path", str(proj), "--script", "res://probe.gd"],\n                       capture_output=True, text=True, timeout=180)\n    line = next((ln for ln in r.stdout.splitlines() if ln.startswith("RESULT ")), None)\n    assert line, r.stdout + r.stderr\n    got = json.loads(line[len("RESULT "):])\n    assert got == STEMS\n'}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s/%s has mixed line endings; nothing written" % (REPO.name, name))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %s/%s is %s, not the %s this patch was written against; nothing written"
                         % (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %s/%s: the anchor at %s is there %d times; nothing written"
                                 % (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
