# Third-party software the factory uses, and how a user gets it

Measured 2026-10-26 from each installed package's own metadata (`importlib.metadata`: `License-Expression`, or the
licence classifiers where a package declares no expression), in this machine's `.venv` and Blender 5.1.1's Python.
Re-measure when a pin moves: `level_factory/packages/tools/interpreter.py` holds the pins (`PINNED`, `CONSTRAINED`).

## What a release contains

A factory release (`tools/make_factory_package.ps1`, published to GitHub and the forge by
`tools/publish_release.py`) is `git archive` of the factory's own repos. It **contains no third-party Python package,
no Blender and no Godot.** The user installs Blender and Godot themselves, from their publishers.

## What setup downloads, and from where

`factory setup --venv`, or **Prepare environment** on the Factory panel, runs pip on the user's own machine. pip
downloads each package below from PyPI, at the pinned version, into `<factory>/.venv`. The factory redistributes none
of them. Each user receives each package from its publisher, under that package's licence.

| Package | Version | Licence (declared) | Why |
|---|---|---|---|
| Pillow | 12.3.0 | MIT-CMU | Pixelcoat, Patina: images |
| pygltflib | 1.16.5 | MIT | Patina; Deli Counter's gates and composer: glTF |
| jsonschema | 4.26.0 | MIT | Patina |
| dataclasses-json | 0.6.7 | MIT | needed by pygltflib |
| marshmallow | 3.26.2 | MIT | needed by dataclasses-json |
| typing-inspect | 0.9.0 | MIT | needed by dataclasses-json |
| mypy-extensions | 1.1.0 | MIT | needed by typing-inspect |
| deprecated | 3.0.0 | MIT | needed by pygltflib |
| wrapt | 2.5.1 | BSD-2-Clause | needed by deprecated |
| referencing | 0.37.0 | MIT | needed by jsonschema |
| jsonschema-specifications | 2025.9.1 | MIT | needed by jsonschema |
| rpds-py | 2026.9.1 | MIT | needed by referencing |

## What comes with Blender's Python

The `.venv` is made from Blender's own interpreter and inherits its packages. They arrive with Blender, under
Blender's distribution, not from the factory: attrs 25.3.0 (MIT), packaging 25.0 (Apache-2.0 or BSD), typing-extensions
4.14.1 (PSF-2.0), numpy 2.3.4 (BSD).

## What the factory itself needs no package for

The authoring loop's records are checked against their schemas by a built-in validator
(`level_factory/packages/service/schemas.py`, 0.252.0), so they add no dependency. `jsonschema` is in the list above
only for Patina.

## Decided by the walker, 2026-10-26

- **Bootstrap: download at setup.** Releases keep carrying no third-party package. A user's own setup fetches the
  pinned packages above from PyPI, once, and needs the network for that one step. Two guards follow, both shipped
  in Level Factory 0.255.0 (b6a0b76):
  - setup shows the user this list, licences included, before it downloads: `setup --venv` prints it, and the
    Setup tab shows it beside Prepare environment;
  - a pin is held to the licence recorded for it (`interpreter.LICENSES`): `make_venv` refuses an environment whose
    package is another version or declares another licence. Checked on this machine's `.venv`: none differ.
- **Every factory repo is MIT.** Lot, Pixelcoat and Zoo already were. Level Factory (was "Proprietary", in LICENSE
  and `pyproject.toml`), Patina (was a placeholder), Deli Counter, Laser Tag, Lux, Dispatch, Pipeline and the factory
  root (none) carry MIT from 2026-10-26: `Copyright (c) 2026 Siliconight / GabagoolStudios`.

## Not yet audited

Third-party ASSETS inside the factory's own repos travel in every release. Pixelcoat's fonts (`assets/fonts/*`) each
carry their own LICENSE.txt beside them; nothing yet lists every bundled font, texture or reference image with its
licence the way this file lists packages.
