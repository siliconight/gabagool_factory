"""Roadmap 267: arena_a02's crowd barricades made (Zoo 1.118.0 / 1.118.1, Deli Counter 0.242.0, cold runs 9358 to
9360) and re-scoped by the walker to a box office's queue in retractable-belt stanchions (Zoo 1.119.0, Deli Counter
0.243.0, cold run 9361); items 273 to 276, found on the way. Copied from `patch_roadmap_202_1_41_0.py`'s checks:
replaces 267's status block (the paragraph directly above its heading, asserted to be the one this was written
against) with a new one that keeps it after "Earlier status kept:", and appends items 273 to 276 after the last item
(272, whose body ends the file). The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check` after it.

    python patches/patch_roadmap_267_queue.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEADING_267 = "\n\n**267. Furniture the generator places that Zoo builds as a box.**"
STATUS_267_OLD_HEAD = ("*STATUS: NARROWED 2026-10-20 -- THE WALKER ON ARENA_A02'S BARRIER: \"Crowd rails (a new "
                       "model)\"")
STATUS_267_HEAD = (
    "*STATUS: NARROWED 2026-10-21 -- ARENA_A02'S BARRIERS, MADE AND THEN RE-SCOPED BY THE WALKER. Made as asked: Zoo "
    "1.118.0 (7344bed) draws the steel crowd-control barricade, `crowd_barrier`, and 1.118.1 (ea536a5) stands its "
    "feet proud of Deli Counter's 2 cm floor skin; Deli Counter 0.242.0 (3ec97799) routes `barrier` to it in its own "
    "kind (`docs/findings/crowd_barrier_267/`; cold runs 9358, 9359 and 9360, 0 interventions each). Shown them, the "
    "walker: \"what are these crowd barriers for....concerts?\", \"queue lanes to the box office\", \"metal barriers "
    "are for outdoor concerts or riot protection from police\", \"retractable belt stanchion\". So Zoo 1.119.0 "
    "(3f54314) draws `stanchion_run`, one straight run of retractable-belt stanchions (168 / 246 / 558 tris at the "
    "genome's corners, 0 coincident pairs), and Deli Counter 0.243.0 (067df43d) lays a box office's sealed ticket "
    "window and a switchback of runs in front of it as generator logic (`ticket_queue.py`, run by `enrich` before "
    "cover and furniture and over the library), every clearance the body contract's; arena_a02's four barricades are "
    "off its event floor, its box office queued, its event floor refurnished (`docs/findings/ticket_queue_267/`; cold "
    "run 9361, 0 interventions, findings 101 -> 101, its nine moved export lines attributed). `crowd_barrier` stays a "
    "species and `barrier` still routes to it, for the outdoors (item 273). Left: `container` -> `cargo_container` "
    "behind a rule for depth-long species; the stair guards (1,025) once a frame shows how a box reads as a guard; "
    "the runs and the new species the rest want; the share in a cold run's package; and two of the walker's calls -- "
    "whether arena_a02's event floor wants its mid-floor crouching cover back (the four barricades were 1.2 m, under "
    "the contract's 1.3 m cover-break height, so no sightline opened; its cover-like pieces 21 -> 17), and whether "
    "the ticket window wants a species of its own (a counter, a speaking grille, a deal tray) rather than Deli "
    "Counter's plain sealed window. Earlier status kept: "
)

ITEMS = (
    "\n*STATUS: OPEN 2026-10-21 -- filed with the walker's re-scope of item 267; not started.*\n"
    "\n"
    "**273. The steel crowd barricade stands nowhere.** Zoo 1.118.0 and 1.118.1 draw `crowd_barrier`, the "
    "interlocking steel barricade on its flat feet, and Deli Counter 0.242.0 routes the word `barrier` to it, but no "
    "level places one now: the walker, 2026-10-20, took arena_a02's four off its event floor -- \"metal barriers are "
    "for outdoor concerts or riot protection from police\" -- and nothing outdoors asks for one. Lot lays the street "
    "and has no notion of a crowd or a cordon. **What would close it:** a brief or a site that says where a crowd or a "
    "police line stands -- an outdoor venue's gates, a cordon round a scene -- and Lot standing barricade lines "
    "there, each panel's hooks over the next panel's leg, with a frame for the walker.\n"
    "\n"
    "*STATUS: OPEN 2026-10-21 -- found by cold run 9359's frames (`docs/findings/crowd_barrier_267/`); two species "
    "fixed or drawn round it, the rest unmeasured.*\n"
    "\n"
    "**274. A prop's ground detail under 2 cm is buried inside a Deli Counter building.** Deli Counter lays a room's "
    "floor finish as a 2 cm skin over the slab and stands every prop on the slab under it (`floors.SKIN_THICK`). Cold "
    "run 9359 framed Zoo 1.118.0's crowd barricades with no feet -- 9.5 mm flat bar, wholly under the carpet, the "
    "legs planted in it; Zoo 1.118.1 drew the feet 3.8 cm tall, and 1.119.0's stanchion bases were drawn 5 cm tall "
    "for the same reason. Nothing has measured the rest of the zoo: a species whose lowest visible detail -- a foot, a "
    "base plate, a kick plate, a mat -- is thinner than 2 cm loses it in a building. **What would close it:** a census "
    "over every Zoo species at its genome's corners of the triangles within 2 cm of its floor, naming each species "
    "that loses something under the skin, and one rule chosen from what it finds -- Zoo keeps ground detail 3 cm or "
    "taller, as both new species do, or Deli Counter stands props on the skin rather than the slab -- with a frame of "
    "whichever species moved most.\n"
    "\n"
    "*STATUS: OPEN 2026-10-21 -- filed with Deli Counter 0.243.0; not started.*\n"
    "\n"
    "**275. A bank's teller line has no queue.** The walker, 2026-10-20: \"stanchion or stanchions are likley more "
    "common for banks and indoor common areas\". Deli Counter 0.243.0's `ticket_queue` lays a box office's switchback "
    "of stanchion runs in front of its ticket window; a bank's teller line -- the counter "
    "`level_design.enclose_teller_lines` walls the staff side of, in the bank preset and the `bank_branch` and "
    "`bank_job` specs -- is the same shape, a service frontage with a public side, and gets nothing in front of it. "
    "**What would close it:** the queue laid from a teller line's public face as from a ticket window (the frontage a "
    "counter, not a window in a wall), by `enrich` and over the library's banks, refurnished and rebuilt, and a cold "
    "run's frames of a bank lobby.\n"
    "\n"
    "*STATUS: OPEN 2026-10-21 -- a question for the walker before it is a task.*\n"
    "\n"
    "**276. arena_a02's event floor is all but black at night.** Cold runs 9358 to 9361 framed it in the level's own "
    "night light (`docs/findings/crowd_barrier_267/barriers_9358_vs_9359_lit.jpg`, "
    "`docs/findings/ticket_queue_267/queue_9360_vs_9361_lit.jpg`): its fluorescent rows hang under a 5.5 m ceiling "
    "and light it, and little reaches the floor, where the box office's queue now stands. An arena between events may "
    "be meant to be dark; a level the crew fights through may not want it. **What would close it:** the walker's "
    "answer; if it is to be lit, Lux's rows for a tall hall -- a high-bay fixture where a troffer is -- priced as "
    "every look is (draws and frame time at fixed stations, before and after, with a control), and a frame.\n"
)


def main():
    raw = RM.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "ARENA_A02'S BARRIERS, MADE AND THEN RE-SCOPED BY THE WALKER" in text or "\n**273. " in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    # 267's status: the paragraph directly above its heading
    if text.count(HEADING_267) != 1:
        raise SystemExit("REFUSED: 267's heading is not there once; nothing written")
    h = text.find(HEADING_267)
    s = text.rindex("\n\n", 0, h) + 2
    old = text[s:h]
    if not old.startswith(STATUS_267_OLD_HEAD) or not old.endswith("*") or "\n" in old:
        raise SystemExit("REFUSED: 267's status block is not the one this was written against; nothing written")
    if text.count(STATUS_267_OLD_HEAD) != 1:
        raise SystemExit("REFUSED: 267's status head is not there once; nothing written")
    new = STATUS_267_HEAD + old[len("*STATUS: "):]
    text = text[:s] + new + text[h:]
    if text.count(new + HEADING_267) != 1:
        raise SystemExit("REFUSED: 267's status no longer adjoins its heading; nothing written")
    # 273 to 276 after the last item
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\*\*(\d+)\. ", text)]
    if max(heads) != 272 or heads[-1] != 272:
        raise SystemExit("REFUSED: the last item is not 272; nothing written")
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    text = text + ITEMS
    for n in (273, 274, 275, 276):
        if len(re.findall(r"(?m)^\*STATUS: [^\n]*\*\n\n\*\*%d\. " % n, text)) != 1:
            raise SystemExit("REFUSED: item %d's status does not adjoin its heading; nothing written" % n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 267: status replaced, the earlier kept; items 273, 274, 275, 276 appended; "
          "now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
