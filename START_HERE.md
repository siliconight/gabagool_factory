# Start here: your first level

Gabagool Factory makes playable heist levels for Godot from a short written
brief. It needs **Blender** and **Godot 4.7**. You don't need to install
anything else.

| you need | where it comes from |
|---|---|
| Blender 4.2 or newer | blender.org. On Windows, use the installer. On Linux, use the `.tar.xz` archive, which carries its own Python; a distribution's packaged Blender does not. |
| Godot 4.7 | godotengine.org. It is a zip with no installer: unpack it anywhere and note where. |

## 1. Unpack and open a terminal

Unzip the factory anywhere, for example `C:\gabagool` or `~/gabagool`, and
open a terminal in that folder:
- **Windows:** type `cmd` in Explorer's address bar.
- **Linux:** open any terminal and `cd` there.

## 2. Set up, once

Windows:

```
factory setup --venv --godot C:\Godot\Godot_v4.7-stable_win64.exe
```

Linux:

```
./factory.sh setup --venv --godot ~/Godot/Godot_v4.7-stable_linux.x86_64
```

Point `--godot` at your own Godot. Then:

- **How `factory` runs.** `factory` (`factory.sh` on Linux) finds the Python
  that ships inside Blender, and runs the factory with it.
- **If Blender is not where its installer puts it,** say where it is first:
  - Windows: `set BLENDER=D:\Apps\Blender\blender.exe`
  - Linux: `export BLENDER=~/blender-5.1.1-linux-x64/blender`
- **`--venv` uses the network, once.** It gives the factory a Python
  environment of its own, in `.venv`, and downloads the three packages
  Blender's Python lacks: Pillow, pygltflib and jsonschema. It is the only
  step that touches the network, and it changes nothing in Blender.
- **Setup ends with the doctor.** `worst: PASS` or `worst: WARN` means you are
  ready. Any `FAIL` line says what is missing and how to fix it.
- **In PowerShell** rather than cmd, type `.\factory` wherever this page says
  `factory`: PowerShell does not run commands from the current folder by
  name.

## 3. Make a level

Windows:

```
factory -C levels make docs\first_level\batch.json
```

Linux:

```
./factory.sh -C levels make docs/first_level/batch.json
```

That one command does the following, and says which step it is on as it
goes:
1. makes a workspace called `levels`;
2. builds three candidate layouts and tests each one:
   - a walker crosses it;
   - a bot crew plays the heist through;
3. picks the best candidate;
4. dresses and lights it;
5. exports it as a Godot package.

It took about half an hour on the machine it was written on. If a step
fails, it stops with `STOPPED at <step>` and the reason.

## 4. Walk it

```
factory -C levels walk restaurant_row_001 --play
```

That opens Godot on a first-person preview of what was exported:
- **Move:** WASD, with Shift to sprint.
- **Jump:** Space.
- **Look:** the mouse.
- **Free the mouse:** Esc.

The exported package itself, ready to drop into your own Godot project, is
the folder `make` printed as `the level:`.

## 5. Your own level

The brief is `docs/first_level/briefs/restaurant_row_001.json`. To make your
own:
1. Copy it, and change `mission_id` plus what you want to be different:
   - `archetype`
   - `building_count`
   - `time_of_day` (morning, noon, afternoon, evening or midnight)
   - `weather`
2. Add the new `mission_id` to a `batch.json` like the one beside it.
3. Run `make` on that batch, adding `--mission <mission_id>` if the batch
   lists more than one.

`docs/LEVEL_STANDARD.md`, Appendix A, describes the request a brief comes
from, and which fields the factory reads today.

## When something goes wrong

- **`factory -C levels doctor`** checks every tool and says what it cannot
  reach.
- **`factory -C levels pick restaurant_row_001`** shows why the candidate
  `make` chose was chosen.
- **`USING_THE_FACTORY.md`** is the operators' guide: which tool owns what,
  and what to do when a brief asks for something no tool makes yet.
