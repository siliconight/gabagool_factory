"""Roadmap 240: Lot 0.119.1 proven in cold run 9264, and Lot 0.119.2 (the pixel floor written as a float,
found in 9264's package). Replaces the end of 240's status (asserted once, the status still above its
heading) and appends one paragraph to 240's body, before 241's status. The index is NOT touched here:
run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_240_9264.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD = ("budgets are 243's. Left: Lot 0.119.1 in a cold run; the street lights' shadow cost, the walker's "
       "call among the levers; the frames beside the comps for the walker's eye; then the rowhouse front "
       "and the silver roofs.*")
NEW = ("budgets are 243's. Lot 0.119.1 proven in cold run 9264 (0 interventions; the generator's far "
       "wires faint continuous lines where 9263's were dashes, +2.2 draws and p95 -0.02 ms), and 0.119.2 "
       "writes its pixel floor as a float, which 9264's package showed Godot reading as null. Left: the "
       "street lights' shadow cost, the walker's call among the levers; the frames beside the comps for "
       "the walker's eye; then the rowhouse front and the silver roofs.*")

BODY = """

**THE PIXEL FLOOR IN A REAL DRIVE, COLD RUN 9264, 2026-10-12** (`docs/cold_runs/cold_9264/`). 0 interventions; the generator's own 0.119.1 wires shot beside 9263's at the same five stations: within about 30 m the same, past about 60 m faint continuous lines where 9263's broke into dashes; priced in the run's package against the wires hidden, +2.2 draws a heading and p95 -0.02 ms at the median inside the controls' 0.14 -- the transparent pass and the vertex shader cost what the opaque wires did. **Found in it:** Lux's re-save carried `shader_parameter/min_px = null`; Lot had written `= 1`, an integer literal for a float uniform, and Godot 4.7 reads that as no value (`docs/findings/pole_line/min_px_resave.gd`: `1` and `2` load and re-save null, `1.0` and `2.0` keep), so the floor held only because the shader's default is the same 1.0 -- a knob with no effect. **Lot 0.119.2** writes the float; its test sets the floor to 1, 2 and 1.5 and asks each for a decimal point."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE PIXEL FLOOR IN A REAL DRIVE" not in text, "already applied"
    assert text.count(OLD) == 1, "240's status end not found once"
    text = text.replace(OLD, NEW)
    h = text.find("\n\n**240. ")
    assert h > 0 and text.count("\n\n**240. ") == 1
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert s >= 0 and text[s:h].endswith(NEW), "240's status does not sit above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**241. ", nxt) > nxt, "241 does not follow 240"
    text = text[:nxt] + BODY + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 240: status end and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
