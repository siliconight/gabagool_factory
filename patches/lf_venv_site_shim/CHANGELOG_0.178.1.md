## [0.178.1] - A venv made from Blender's Python starts without an error

**Roadmap 202, install test 4** (`docs/findings/stranger_install/` in the
factory): the released 1.36.0 package unpacked fresh and START_HERE.md's
own commands typed into cmd.exe, `setup --venv` for the first time with
the PyPI download allowed. Setup, make and walk all exited 0 and the
closure was clean. And every tool the environment started printed

    Error in sitecustomize; set PYTHONVERBOSE for traceback:
    FileNotFoundError: [WinError 2] The system cannot find the file specified: 'C:\stranger_202_4\blender.shared'

-- twelve times on the way to one first level. Blender's own
`sitecustomize.py`, which the environment sees because it keeps its base's
packages, adds the DLL directory three folders above `sys.executable`; in
an environment that is its `Scripts` folder, and the folder it names is
not there. Nothing failed. A stranger is told "Error" at every step.

- **`interpreter.blender_site_shim`** writes the environment its own
  `sitecustomize.py` when the base is Blender's Python on Windows
  (recognised the way Blender's file finds its libraries: `blender.shared`
  three folders above the interpreter). It does what Blender's does, from
  the folder Blender's names for Blender's own Python. `make_venv` writes it
  after the environment is made and before pip runs.
- Any other base, and Linux, is left alone: there Blender's file adds no
  DLL directory and raises nothing. Read, not run -- there is no Linux
  machine here.
- An environment made by 0.168.0-0.178.0 keeps printing the error until
  `setup --venv` is run again.

**Tests:** 3 in `tests/unit/test_setup_venv.py`, one on Blender's real
Python with its control (the error without the shim). **Suite:** RESULT_SUITE.
