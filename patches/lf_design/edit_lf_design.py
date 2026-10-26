"""Level Factory 0.245.0 on a clone: a level is a saved design (the factory's roadmap 312 and 313, increment 3 of
`docs/AUTHORING_LOOP.md`). Anchored; refuses on a miss.

    python edit_lf_design.py <clone>

Copies packages/service/design.py and packages/service/templates/restaurant_row.json from beside this script into
the clone, adds four operations to packages/service/operations.py, and writes tests/service/test_design.py. The
dock's form is a separate edit (`edit_lf_design_dock.py`). VERSION and CHANGELOG are the generator's.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent

for rel in ("packages/service/design.py", "packages/service/templates/restaurant_row.json"):
    dst = C / rel
    assert not dst.exists(), rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "src" / rel, dst)
    print("wrote", rel)

p = C / "packages" / "service" / "operations.py"
t = p.read_bytes().decode("utf-8")
assert "\r\n" not in t
old = '''OPERATIONS = {
    "discover_installation": discover_installation,
    "configure_installation": configure_installation,
    "prepare_environment": prepare_environment,
}
'''
new = '''def _design_error(exc) -> RequestError:
    return RequestError(exc.code, str(exc))


def list_templates(arguments: dict, events) -> dict:
    """The templates a level can start from: id, label, description. No arguments."""
    _no_unknown(arguments, set())
    from packages.service import design
    try:
        return {"templates": [{"template_id": k, "label": t["label"], "description": t["description"]}
                              for k, t in design.templates().items()]}
    except design.DesignError as exc:
        raise _design_error(exc) from None


def describe_template(arguments: dict, events) -> dict:
    """A template's controls, for a form: each with its support state (supported / conditional / intent), its
    options or range, and its default. Argument: ``template``."""
    _no_unknown(arguments, {"template"})
    from packages.service import design
    try:
        t = design.template(_text(arguments, "template"))
        return {"template_id": t["template_id"], "label": t["label"], "description": t["description"],
                "controls": design.capabilities(t["template_id"])}
    except design.DesignError as exc:
        raise _design_error(exc) from None


def create_design(arguments: dict, events) -> dict:
    """Start a level: a revision-1 design saved as ``<factory>/levels/<slug>/design.json``.

    Arguments: ``template``, ``name``, and optionally ``choices`` and ``intent`` (objects of control values, each
    checked against the template's catalog). A name already used gets a numbered folder, never an overwrite.
    Returns the design, its path, and the brief the pipeline will read from it."""
    _no_unknown(arguments, {"template", "name", "choices", "intent"})
    from packages.service import design
    from packages.tools import discovery
    root = discovery.factory_root()
    if root is None:
        raise RequestError("no_factory", "no %s at or above this Level Factory" % discovery.MANIFEST)
    for part in ("choices", "intent"):
        if not isinstance(arguments.get(part, {}), dict):
            raise RequestError("bad_argument", "%s must be an object" % part)
    try:
        doc = design.new_design(_text(arguments, "template"), _text(arguments, "name"),
                                arguments.get("choices"), arguments.get("intent"))
        folder = design.free_folder(design.levels_root(root), doc["slug"])
        doc["slug"] = folder.name
        path = design.write_design(folder, doc)
    except design.DesignError as exc:
        raise _design_error(exc) from None
    events.emit("design", "ok", "Saved %s" % path)
    return {"design": doc, "path": str(path), "problems": [], "unknown_fields": [],
            "brief": design.brief_from_design(doc)}


def open_design(arguments: dict, events) -> dict:
    """Read a saved design: argument ``path`` (its folder or its design.json). Returns the design with any problems
    that make it unusable and any fields this factory does not know -- reported, never dropped -- and, when it is
    usable, the brief the pipeline will read from it."""
    _no_unknown(arguments, {"path"})
    from packages.service import design
    try:
        got = design.read_design(Path(_text(arguments, "path")))
    except design.DesignError as exc:
        raise _design_error(exc) from None
    got["brief"] = design.brief_from_design(got["design"]) if not got["problems"] else None
    return got


def list_designs(arguments: dict, events) -> dict:
    """The designs saved under ``<factory>/levels``, newest first: name, template, revision, path. No arguments."""
    _no_unknown(arguments, set())
    from packages.service import design
    from packages.tools import discovery
    root = discovery.factory_root()
    if root is None:
        raise RequestError("no_factory", "no %s at or above this Level Factory" % discovery.MANIFEST)
    rows = []
    for p in sorted(design.levels_root(root).glob("*/" + design.DESIGN_FILE)):
        try:
            got = design.read_design(p)
        except design.DesignError as exc:
            rows.append({"path": str(p), "problem": str(exc)})
            continue
        d = got["design"]
        rows.append({"path": str(p), "name": d.get("name"), "template": d.get("template"),
                     "revision": d.get("revision"), "updated_at": d.get("updated_at"),
                     "problem": "; ".join(got["problems"]) or None})
    rows.sort(key=lambda r: str(r.get("updated_at") or ""), reverse=True)
    return {"designs": rows}


OPERATIONS = {
    "discover_installation": discover_installation,
    "configure_installation": configure_installation,
    "prepare_environment": prepare_environment,
    "list_templates": list_templates,
    "describe_template": describe_template,
    "create_design": create_design,
    "open_design": open_design,
    "list_designs": list_designs,
}
'''
assert t.count(old) == 1
p.write_bytes(t.replace(old, new).encode("utf-8"))
print("edited operations.py")

test = C / "tests" / "service" / "test_design.py"
assert not test.exists()
shutil.copyfile(HERE / "src" / "tests" / "service" / "test_design.py", test)
print("wrote", test.name)
