## [0.199.0] - The price reports what the package holds in memory

**Factory roadmap 238.** A package's texture memory was 314.6 MiB on cold run 9273 and 65.6 MiB on 9274,
once 0.198.0 sized the reflection atlas to the package. No price said either. The fixed-station harness
reported draws and frame time, and the memory was read by a separate probe on a separate copy (the
factory's `docs/findings/texture_memory/`). Now the price carries it, so a change that grows the package's
memory shows up where its draws and frame time do.

- **`tools/perf_stations.gd`** reads the engine's texture, buffer and video memory into the report's
  `geometry` (`texture_mem_bytes`, `buffer_mem_bytes`, `video_mem_bytes`). It reads them once every
  station has been warmed, so what a station shows is resident, and before the measured passes.
- **`tools/perf_stations_run.py`** prints them in MiB beside the passes. A report from before 0.199.0 says
  it carries none, and one carrying only some of the three prints none of them: a missing field is never
  read as a zero.
- `tests/unit/test_perf_memory.py`: the probe's read and where it stands, and the runner's three cases.
  All four fail on 0.198.0, run against an export of it.

**Measured:** on an imported copy of cold run 9276's package (the factory's `docs/findings/texture_memory/`, "In the price"), the harness reads textures 76.0 MiB, buffers 48.0 and video 123.9 after its warm-up. On the same copy, `texture_split_probe.gd`'s `mission` arm reads textures 65.6 MiB and buffers 48.0, as it read 9274's. That arm reads after the package's own warm-up, with its last view nearly empty (1 draw).

The two read different moments, and the gap is measured. A scratch copy of this probe, printing at three points, read 67.9 MiB of textures with the main scene in and 60 frames on, 67.9 with its camera at the first station, and 76.0 once every station was warm, in both of its runs as built; the harness itself read 76.0 in its own. With the positional shadow atlas at 0 and the directional at 256 (`override.cfg`) it read the same 67.9 and 76.0, so the shadow atlases are not the gap. The window accounts for about 1.3 MiB: this probe draws 1280 x 720, the other 1152 x 648, whose empty window is 5.7 MiB. The rest of the 10.4 grows as a camera stands at the stations, and is not attributed.

Buffers are not steady between runs at one moment: 48.0 MiB in three runs, 56.1 in one, which read 35.8 at load. The price's figure is the level in play: everything a station shows, after a camera has stood at every one

**Suite:** exit 0, 2,373 by the progress tally (2,358 passed, 14 skipped, 1 xfail): 0.198.0's 2,368, the new file's four, and one more case of `test_sibling_locator.py`, which runs once a `.py` file in the repository and so once for the new file. `test_perf_memory.py`'s four fail on 0.198.0, run against an export of it
