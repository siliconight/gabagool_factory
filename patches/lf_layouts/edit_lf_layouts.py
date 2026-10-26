"""Level Factory 0.246.0 on a clone: generate a level's layouts and choose one from the panel (the factory's roadmap
314, increment 4 of `docs/AUTHORING_LOOP.md`). Anchored; refuses on a miss.

    python edit_lf_layouts.py <clone>

Copies packages/service/layouts.py and tests/service/test_layouts.py from `src/` beside this script, and adds the
operations `generate_layouts` and `choose_layout`. The panel's half is `edit_lf_layouts_panel.py`. VERSION and
CHANGELOG are the generator's.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("packages/service/layouts.py", "tests/service/test_layouts.py"):
    dst = C / rel
    assert not dst.exists(), rel
    shutil.copyfile(HERE / "src" / rel, dst)
    print("wrote", rel)

p = C / "packages" / "service" / "operations.py"
t = p.read_bytes().decode("utf-8")
assert "\r\n" not in t
old = '''OPERATIONS = {
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
new = '''def generate_layouts(arguments: dict, events) -> dict:
    """Generate the layouts of the design at ``path`` (`packages.service.layouts.generate`): the shell legs `make`
    runs, progress from the job index, a stop through the run's ``cancel`` file. Returns every layout with its state
    -- valid, needs attention, failed, not checked -- its evidence, and the automated recommendation, which says so
    when every layout failed."""
    _no_unknown(arguments, {"path"})
    from packages.service import layouts
    try:
        return layouts.generate(_text(arguments, "path"), events, Path(events.path).parent)
    except (layouts.LayoutError, ValueError) as exc:
        raise RequestError(getattr(exc, "code", "design_unusable"), str(exc)) from None


def choose_layout(arguments: dict, events) -> dict:
    """Record the designer's choice: arguments ``path`` (the design) and ``candidate`` (a layout's id). A choice,
    not a review."""
    _no_unknown(arguments, {"path", "candidate"})
    from packages.service import layouts
    try:
        return layouts.choose(_text(arguments, "path"), _text(arguments, "candidate"), events,
                              Path(events.path).parent)
    except (layouts.LayoutError, ValueError) as exc:
        raise RequestError(getattr(exc, "code", "design_unusable"), str(exc)) from None


OPERATIONS = {
    "discover_installation": discover_installation,
    "configure_installation": configure_installation,
    "prepare_environment": prepare_environment,
    "list_templates": list_templates,
    "describe_template": describe_template,
    "create_design": create_design,
    "open_design": open_design,
    "list_designs": list_designs,
    "generate_layouts": generate_layouts,
    "choose_layout": choose_layout,
}
'''
assert t.count(old) == 1
p.write_bytes(t.replace(old, new).encode("utf-8"))
print("edited operations.py")
