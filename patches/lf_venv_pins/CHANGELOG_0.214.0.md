## [0.214.0] - What the three pins bring is held too

**The factory's roadmap 256, found by install test 9** (the factory's `docs/findings/stranger_install/README.md`,
"Install test 9"). `setup --venv` ran `pip install pillow==12.3.0 pygltflib==1.16.5 jsonschema==4.26.0` and let
pip resolve the nine packages those three require from whatever the index held that day: install test 8
(2026-10-12) took wrapt 2.5.0 from pip's cache, install test 9 (2026-10-14), the same three pins, downloaded wrapt
2.5.1. Two strangers a week apart installed two environments from one package, and a certified set certified an
environment it did not fix.

- **`interpreter.CONSTRAINED`:** the nine, each at the version install test 9 ran -- dataclasses-json 0.6.7,
  deprecated 3.0.0, jsonschema-specifications 2025.9.1, marshmallow 3.26.2, mypy-extensions 1.1.0, referencing
  0.37.0, rpds-py 2026.9.1, typing-inspect 0.9.0, wrapt 2.5.1.
- **`write_constraints(venv)`:** `<venv>/constraints.txt`, one `==` line for every distribution `setup --venv`
  may install, `PINNED` and `CONSTRAINED`; `make_venv` writes it before pip runs and passes it with `-c`. A
  constraint fixes a version without asking for the package, so what the base already carries (attrs, packaging
  and typing-extensions, from Blender's own Python) stays the base's, and pip resolves nothing afresh.
- **`setup --venv`'s line** says so: "with pillow 12.3.0, pygltflib 1.16.5, jsonschema 4.26.0, and the 9
  packages they bring held at their versions (constraints.txt)".
- **`tests/unit/test_setup_venv.py`:** the pip call carries `-c <venv>/constraints.txt` ahead of the pins (the
  first test, restated); the file holds the twelve, sorted, the two sets disjoint; the nine are the set install
  test 9 installed. The restated test and the first new one fail on 0.213.0.

Not changed: the doctor's `tools_python` row, which asks the interpreter for its imports and not their versions.
The factory's START_HERE.md said `--venv` "downloads the three packages Blender's Python lacks"; it now says the
nine they need come with them, at the versions the factory was certified with. Certified by the next install
test, which is where this is proven: nothing built changes.

**Suite:** RESULT_SUITE
