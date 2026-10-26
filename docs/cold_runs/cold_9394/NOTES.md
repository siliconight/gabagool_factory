# Cold run 9394 -- 0 interventions, stopped at the shell leg: no brief can anchor a civic building

**What it was for.** Deli Counter 0.270.0 (the civic rooms: pews facing an altar, a judge's bench, a lectern) and Zoo
1.130.0 (the `pew`) in a package. restaurant_row_001's lot draws no civic building, so this run carried the first
brief with a civic archetype: `funeral_row_001`, restaurant_row's brief with `archetype: funeral_home`
(`briefs/funeral_row_001.json`).

**What it measured.** `INTERVENTIONS: 0`. The run stopped at the shell leg with nothing built, and correctly. The
re-run of that leg's own command in the run's workspace after `--end` (diagnosis, not an intervention;
`shell_rerun.out.txt`) printed:

> internal error: brief archetype 'funeral_home' matches no DC preset.

A brief's anchor is GENERATED from a Deli Counter preset (Level Factory's `adapters/deli_counter._preset_for`; 24
presets). The funeral homes, courthouses, museums and landmark halls are authored specs in the library and nothing
else. So no brief can anchor one, and nothing 0.270.0 changed can reach a level through a brief. The refusal is by
design: the adapter's docstring records the lot demo whose `mixed_block` briefs silently built banks. Filed as the
factory's roadmap 309.

**The driver hid it, three ways** (`tools/cold_drive/cold_drive.sh`, the shell leg, fixed tonight):
- its filter kept only `candidates:` and `blockers open`, so the CLI's error line never reached `driver.log`;
- with no candidate job, its loop printed `basename`'s usage;
- `${PIPESTATUS[0]}` was read after the loop, so it reported the loop's 0 while the CLI had exited 5.

The leg now keeps `internal error` and `Error:` lines, skips a glob that matched nothing, and takes the CLI's exit
before the loop. Replayed on this run's workspace, it prints the refusal and `exit 5` and stops the leg.

**The pews are still unproven in a package.** Their proof is in Deli Counter's own build of the twelve specs
(`patches/dc_civic_rooms/`: the suite, the nav gate, the route census, the room plans) and Zoo's Blender tests and
previews (`patches/zoo_pew/`).
