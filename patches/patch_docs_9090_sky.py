"""Cold run 9090 into the two docs that own its numbers: the sky priced at
stations (DRAW_CALL_BUDGET.md), and a refuted cost claim in the sky
proposal (SKY_PROVIDER.md).

Anchored; refuses on any miss. Root repo only -- neither file is hashed by
a cold run, and none is in flight.
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
BUDGET = ROOT / "docs" / "DRAW_CALL_BUDGET.md"
SKY = ROOT / "docs" / "proposals" / "SKY_PROVIDER.md"


def edit(path, pairs, label):
    raw = path.read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s has mixed endings" % path)
    eol = "\r\n" if crlf else "\n"
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for i, (old, new) in enumerate(pairs):
        if t.count(old) != 1:
            raise SystemExit("REFUSED: %s anchor %d matched %d times"
                             % (label, i, t.count(old)))
        t = t.replace(old, new, 1)
    out = (t.replace("\n", eol) if eol == "\r\n" else t).encode("utf-8")
    path.write_bytes(out)
    print("[patch] %s: %d blocks, %d -> %d bytes"
          % (path.name, len(pairs), len(raw), len(out)))


BUDGET_ANCHOR = "## Open questions this file does not answer\n"
BUDGET_NEW = '''## The sky, priced — cold run 9090

Cold run 9090 is 9089 again with Lux 0.53.0: SkyMint 1.1 spawned by the
`delco_night` preset (cube-sampled `empty_space` at brightness 8, clouds
off) and nothing else changed. It closed at **zero interventions**, same
seed, same candidate, same 34 and 58 findings, 1,356 files, closure clean.

The harness read every station **higher than 9089 at identical draw
counts** — extraction_10 8.89 → 10.20 ms on 2,300 draws both times,
player_start_28 8.84 → 10.70 on 2,773. Draws are the budget in this file, so
a cost that moves with none of them is a different kind of cost, and it was
priced the way CLAUDE.md asks: the same package, copied, with the preset's
`sky_provider_script` blanked and nothing else touched, run through the same
harness back to back. Worst heading per station, sky on / sky off:

| station | sky ON p95 / gpu | sky OFF p95 / gpu | draws | Δ p95 | Δ gpu |
|---|---:|---:|---:|---:|---:|
| highest_vantage | 13.10 / 7.19 | 11.41 / 5.62 | 2,649 | +1.69 | +1.57 |
| player_start_28 | 10.70 / 5.30 | 10.45 / 3.65 | 2,773 | +0.25 | +1.65 |
| extraction_10 | 10.20 / 4.76 | 10.02 / 3.48 | 2,300 | +0.18 | +1.28 |
| attacker_spawn_16 | 9.82 / 4.34 | 8.56 / 2.73 | 2,167 | +1.26 | +1.61 |
| attacker_spawn_11 | 9.53 / 5.15 | 8.74 / 2.56 | 1,692 | +0.79 | +2.59 |
| longest_sightline | 9.22 / 4.76 | 8.02 / 3.08 | 2,139 | +1.20 | +1.68 |
| camera_socket_1 | 7.99 / 3.25 | 6.94 / 2.08 | 2,024 | +1.05 | +1.17 |
| extraction_3 | 7.40 / 2.66 | 6.81 / 2.05 | 2,027 | +0.59 | +0.61 |
| crew_spawn_2 | 6.88 / 3.04 | 6.65 / 1.64 | 1,953 | +0.23 | +1.40 |
| objective_4 | 3.36 / 1.58 | 2.82 / 1.10 | 1,278 | +0.54 | +0.48 |

(Four stations picked a different worst heading between the two runs and
are left out rather than compared across headings. Reports:
`docs/cold_runs/cold_9090/perf_stations.json` and
`perf_stations_nosky_control.json`.)

**The sky costs about 1.3 ms of GPU and 0.2–1.7 ms of p95 at every
station, on identical draw counts.** It is a per-pixel cost — a fullscreen
shader — so it scales with resolution and not with the level, which is the
one shape of cost this file's draw-call reasoning cannot see. On an RTX 2060
at the walk copy's resolution that is inside the 11 ms budget everywhere
except the vantage, which was over without it (11.41). On the GL
Compatibility target it is unmeasured and will be larger in proportion.

**And it is not the cube.** SkyMint's cloud block — five noise fetches, a
`pow`, and the lighting that follows — runs on every pixel whether or not
there are clouds: `cloud_density = 1.0` zeroes the *mask* after the fetches,
not before them. `docs/proposals/SKY_PROVIDER.md` §Cost claimed the reverse
and is corrected there. The cheap version is one `if` around that block
when density is 1.0, which would change `glow_occlusion` slightly (it reads
cloud `thickness` even with no clouds) and has not been priced. That is the
next measurement, not this one.

**The rest of 9089's 1 ms is the day.** The control run (sky off) still
read ~1.2 ms above 9089 at the same draws — extraction_10 10.02 against 8.89
— on the same machine a day apart, one sample each. The harness still does
not repeat a station, so drift of that size is the noise floor these tables
sit on until it does.

Stations over the 2,000-draw guardrail on 9090: **7 of 14** — the five
anchors 9089 had, plus the vantage and the sightline, both of which were
over on 9089 too and simply had not been stations then.

'''

SKY_OLD = '''Not yet priced properly, and it should be before anything ships. What is
known: with clouds off the sky shader does one equirect lookup plus a disc,
and the per-pixel cloud work (7 texture fetches) is gone. `Sky` is set to
`PROCESS_MODE_INCREMENTAL` at 256 in the prototype rather than SkyMint's
`REALTIME` at 128, which costs a face rebuild per frame rather than all at
once; with a static sky neither should matter and neither has been measured
at stations.
'''
SKY_NEW = '''**PRICED 2026-09-27, cold run 9090, and the paragraph below it was wrong.**
Same package, sky provider on and off, same harness back to back: **about
1.3 ms GPU and 0.2–1.7 ms p95 at every station, on identical draw counts.**
The table is in `docs/DRAW_CALL_BUDGET.md` § "The sky, priced".

RETRACTED: "with clouds off ... the per-pixel cloud work (7 texture fetches)
is gone." It is not. Read the shader rather than the profile: the five noise
fetches, the `pow` and the cloud lighting run on every pixel, and
`cloud_density = 1.0` zeroes the resulting MASK, after the work. Clouds off
is a look, not a saving. The saving is one branch around that block, which
would move `glow_occlusion` slightly (it reads cloud thickness even at zero
coverage) and is unpriced.

What was known before that, kept for the record: `Sky` is set to
`PROCESS_MODE_INCREMENTAL` at 256 in the prototype rather than SkyMint's
`REALTIME` at 128, which costs a face rebuild per frame rather than all at
once; with a static sky neither should matter and neither has been measured
at stations.
'''


def main() -> int:
    edit(BUDGET, [(BUDGET_ANCHOR, BUDGET_NEW + BUDGET_ANCHOR)], "DRAW_CALL_BUDGET.md")
    edit(SKY, [(SKY_OLD, SKY_NEW)], "SKY_PROVIDER.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
