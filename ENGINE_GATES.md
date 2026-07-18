# Engine Gates — the Godot leg of Phase 0

## The handoff boundary (read this before extending any gate)

This stack builds **levels for someone else's game**. The consumer takes the
mission-shell handoff — GLB + `.gameplay.json` + markers + evidence reports,
orchestrated end-to-end by
[`level_factory`](https://github.com/siliconight/level_factory) — into their
own Godot project, and THEY are the authority on the network and gameplay
layer: replication, tick model, player controllers, weapons, AI. Our gates
certify the ASSET, never the game:

- `nav_qa_director.gd` is a disposable QA harness bot proving the baked
  navmesh and the collision agree. It is not a player controller and must
  never grow into one — step-up, repath, and reseat exist so the harness
  can't false-fail a good level, not to ship movement mechanics.
- `mp_smoke.gd` is replication-free BY CONTRACT, not by omission: it proves a
  shell survives N peers loading it and physically moving through it at the
  target player count. Authority models, interpolation, netcode design —
  downstream's problem, downstream's freedom.
- If a future gate seems to need gameplay logic, that's the signal it
  belongs in the consumer's test suite, not here.

The four gates the sandbox could not run (no Godot there). All target
**Godot 4.7 stable**, all run headless, all write machine-readable reports
whose results map onto the registry gate fields. Point the runners at your
binary once:

```powershell
$env:DC_GODOT = "C:\path\to\Godot_v4.7-stable_win64.exe"
```

(If you have the `_console.exe` variant, prefer it — stdout streams properly
on Windows.)

| Gate | Runner | Report | Registry field |
|---|---|---|---|
| Godot import / round-trip engine leg | `deli_counter\godot_gate.py` | `build\<name>.godot_import.json` | `godot_import` |
| Navmesh stair proof (existing) | `deli_counter\nav_gate.py` | `build\<name>.navgate.json` | part of `navigation_validation` |
| Automated walktest bot | `lot\walktest.py` | `<site>_navqa.walktest.json` | `runtime_walktest` |
| Multiplayer smoke | `lot\mp_smoke.py` | `<site>.mp_smoke.json` | `multiplayer_smoke_test` |

## The reference run (do this first)

From `gabagool_factory`:

```powershell
# 1. build the reference shells locally (Blender via $BLENDER/PATH as usual)
cd deli_counter
python build.py specs\pvp_station_ref.json
python build.py specs\bank_job.json

# 2. building-level gates
python nav_gate.py build\pvp_station_ref.glb
python godot_gate.py build\pvp_station_ref.glb
python roundtrip.py build\pvp_station_ref.glb      # Blender leg, same tolerances
cd ..

# 3. stage the site's buildings (see lot\specs\ref_pvp\README.md)
copy deli_counter\build\pvp_station_ref.glb            lot\specs\ref_pvp\buildings\
copy deli_counter\build\pvp_station_ref.gameplay.json  lot\specs\ref_pvp\buildings\
copy deli_counter\build\bank_job.glb                   lot\specs\ref_pvp\buildings\
copy deli_counter\build\bank_job.gameplay.json         lot\specs\ref_pvp\buildings\

# 4. assemble into a throwaway Godot project dir
cd lot
python lot.py specs\ref_pvp\ref_pvp_site.json --out-dir ..\_runs\ref_pvp_proj --walkable --navqa
xcopy /E /I /Y specs\ref_pvp\buildings ..\_runs\ref_pvp_proj\buildings

# 5. site-level gates (runners bootstrap project.godot + sync addons)
python walktest.py ..\_runs\ref_pvp_proj --all
python mp_smoke.py ..\_runs\ref_pvp_proj specs\ref_pvp\ref_pvp_site.json --players 4
cd ..
```

Green across all five commands = the engine leg exists and the reference
records in `pipeline\registries` can graduate from `pending_engine_leg` to
`pass`. Paste any failure output back into the Cowork session — these
scripts were authored blind to a live Godot and are expected to need an
iteration or two.

## What each gate actually checks

**`godot_gate.py` → `import_gate.gd`** — loads the built GLB in Godot itself
and compares against the SAME manifest `expected` block the Blender-side
`roundtrip.py` uses (so the two legs cannot drift): GI-SCALE (every node
unit positive scale), GI-BOUNDS (visual AABB vs expectations, Z-up→Y-up
converted, 2 cm), GI-ORIGIN (footprint-center origin, ground plane),
GI-MARKERS (marker empties within 5 cm).

**`walktest.py` → `heist_nav_qa/nav_qa_director.gd`** — the addon Lot's
`--navqa` scene has always referenced now exists. Pass 1 path-proves the
mission spine (crew home → every proxy → consecutive proxies) on the baked
navmesh, failing off-mesh anchors and disjoint islands. Pass 2 spawns
`simulated_players` physical CharacterBody3D walkers driving the spine plus
`bot_count` pressure bots, failing anyone stuck > 4 s. This is the §13
"automated runtime walktest": no teleporting, no debug flight, real
collision.

**`mp_smoke.py` → `mp_smoke.gd`** — one headless host + N−1 headless clients
on localhost, all loading the composed site scene; clients physically walk
spawn→objective and heartbeat cumulative distance to the host. Pass = every
client connected, moved ≥ 5 m through real site collision, no early
disconnects. Deliberately a smoke, not a netcode framework — the shells are
replication-free by design.

## Wiring results into the registries

After a green run, update the reference records (the registrar refuses
`approved` until every gate field reads `pass`):

```powershell
# edit the record json: runtime_walktest/godot_import/multiplayer_smoke_test -> "pass"
python pipeline\registry.py add-config  <updated record>.json --dir pipeline\registries --root .
python pipeline\registry.py add-mission <updated record>.json --dir pipeline\registries --root .
python pipeline\registry.py check --dir pipeline\registries
```

At the next factory re-certification, fold these five commands into the
gate list alongside walkabout / headless_walk / the LF suite.
