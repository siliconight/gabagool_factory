"""Roadmap 275: a bank's teller line gets a queue (Deli Counter 0.244.0, cold run 9363); items 277 to 279, found on the
way. Copied from `patch_roadmap_267_queue.py`'s checks: replaces 275's status block (the paragraph directly above its
heading, asserted to be the one this was written against) with a CLOSED one that keeps it after "Earlier status
kept:", and appends items 277 to 279 after the last item (276, whose body ends the file). The index is NOT touched
here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_275_teller.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEADING_275 = "\n\n**275. A bank's teller line has no queue.**"
STATUS_275_OLD = "*STATUS: OPEN 2026-10-21 -- filed with Deli Counter 0.243.0; not started.*"
STATUS_275_NEW = (
    "*STATUS: CLOSED 2026-10-21 -- SHIPPED AND PROVEN. Deli Counter 0.244.0 (33e81109): "
    "`ticket_queue.queue_teller_lines` lays a teller line's queue on its public side -- three lanes or two of stanchion "
    "runs parallel to the counter, letting out along it, the floor in front a door's approach and a corridor "
    "(`teller_service_depth`) -- through the one fitting the box office's queue now shares (unchanged: re-planned from "
    "0.242.0's arena_a02 to the millimetre), by `enrich` after the enclosure and before cover and furniture, and over "
    "the library with its furniture set aside and refurnished after. A queue is not furniture: furnish's count leaves "
    "its runs out -- the first cut counted them and each lobby lost four pieces, among them a payphone and two ATMs -- "
    "and a room holding a queue drops the lobby recipe's lone posts. The library: bank_branch_a02, bank_branch_a03, "
    "bank_job and credit_union_a01 queued (three lanes, 5.2 to 5.6 m) and refurnished, bank_branch_a04 left with its "
    "reason (279), the bank preset queued by `enrich`; the suite 1,715 passed, check.py all passed, Zoo plans all 20 "
    "runs as the species (`docs/findings/teller_queue_275/`, `patches/dc_teller_queue/`). Cold run 9363 (bank_block_001, "
    "seed 9281, bank_branch_a02): 0 interventions, the queue's collision in the package as Zoo draws it, frames in both "
    "lights (`bank_queue_9363_inspect.jpg`, `_lit.jpg`); 9362 void (278). Found on the way: 277, 278, 279. Earlier "
    "status kept: OPEN 2026-10-21 -- filed with Deli Counter 0.243.0; not started.*"
)

ITEMS = (
    "\n*STATUS: OPEN 2026-10-21 -- measured (`patches/dc_teller_queue/storey_filter_floats.py`), not changed; fixing "
    "it refurnishes the library's multi-storey specs.*\n"
    "\n"
    "**277. Furnish's storey filter is decided by float rounding.** `level_design._room_volume_count` counts a volume "
    "in a room when `abs(z - (story * sh + h / 2)) < sh`. For a piece standing on the floor below, that quantity IS the "
    "storey height in exact arithmetic, so the strict `<` falls to rounding: under bank_branch_a03's upstairs offices "
    "(3.6 m storeys), seven of the eleven ground-floor pieces read 3.5999999999999996 and count against the offices' "
    "furnish target -- the teller counter, a vending machine, a waiting chair, three lone posts, cartons -- and four "
    "read 3.6 and do not -- the service counter, the payphone, the ATM, a low table "
    "(`patches/dc_teller_queue/storey_filter_floats_0243.out.txt`). Which pieces a room believes it holds is the "
    "floats' to decide, and a change to a ground floor re-draws the room over it: Deli Counter 0.244.0 removed three "
    "of those posts and the offices took five pieces more. CLAUDE.md's \"a threshold asked of two spellings of one "
    "number\" again. **What would close it:** the filter asks a piece's own floor -- its foot within half a storey of "
    "the room's floor -- the library refurnished where that moves anything, every move counted room by room and "
    "attributed, and the furnish fixed-point tests green.\n"
    "\n"
    "*STATUS: OPEN 2026-10-21 -- found by cold run 9362; the cold drive guards it since (`tools/cold_drive/"
    "cold_drive.sh`), Level Factory does not.*\n"
    "\n"
    "**278. Level Factory approves a candidate no job built.** Cold run 9362 named seed 9281 against a batch whose "
    "candidates were 9054, 9155 and 9256; `level_factory approve <mission> candidate_selected --candidate "
    "<mission>.candidate.seed_9281` accepted it, and the next approval refused it as \"THIS LOCK PROTECTS NOTHING ... "
    "the site file contributed NO protected key\" -- true of a candidate that does not exist, and a long way from the "
    "cause (`docs/cold_runs/cold_9362/NOTES.md`). The cold drive now stops before approving when the named seed has no "
    "built candidate, and lists the batch's own. **What would close it:** `approve candidate_selected` refuses a "
    "candidate with no built shell job and names the candidates there are, with a test, so a stranger typing the "
    "page's commands meets the guard the drive has.\n"
    "\n"
    "*STATUS: OPEN 2026-10-21 -- found by Deli Counter 0.244.0's teller-line queue; not started.*\n"
    "\n"
    "**279. bank_branch_a04's teller counter stands against its lobby's wall.** Its `teller_counter` (10.0 x 0.9 x "
    "2.4 m, x -11 to -1 at y 3.5) stands in the `teller_line` room with its public face at y 3.05 -- 0.1 m inside "
    "partition 0, the concrete wall at y 3.0 between it and the grand lobby, which `level_design._public_side` reads "
    "off the street doors as its public side. No body reaches the counter from the lobby but through that wall's doors "
    "at x -12 and 12; `enclose_teller_lines` leaves it open; `ticket_queue` lays no queue (\"partition 0 inside the "
    "queue\"). **What would close it:** the walker's call on which side is public -- the counter facing the grand lobby "
    "through an opening in partition 0, as bank.json's `teller` opening does, or the teller_line room made the public "
    "room -- then the enclosure, the queue, a refurnish, and a frame.\n"
)


def main():
    raw = RM.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\n**277. " in text or STATUS_275_NEW[:60] in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    if text.count(HEADING_275) != 1:
        raise SystemExit("REFUSED: 275's heading is not there once; nothing written")
    h = text.find(HEADING_275)
    s = text.rindex("\n\n", 0, h) + 2
    if text[s:h] != STATUS_275_OLD:
        raise SystemExit("REFUSED: 275's status block is not the one this was written against; nothing written")
    text = text[:s] + STATUS_275_NEW + text[h:]
    if text.count(STATUS_275_NEW + HEADING_275) != 1:
        raise SystemExit("REFUSED: 275's status no longer adjoins its heading; nothing written")
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\*\*(\d+)\. ", text)]
    if max(heads) != 276 or heads[-1] != 276:
        raise SystemExit("REFUSED: the last item is not 276; nothing written")
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    text = text + ITEMS
    for n in (277, 278, 279):
        if len(re.findall(r"(?m)^\*STATUS: [^\n]*\*\n\n\*\*%d\. " % n, text)) != 1:
            raise SystemExit("REFUSED: item %d's status does not adjoin its heading; nothing written" % n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 275: CLOSED, the earlier status kept; items 277, 278, 279 appended; "
          "now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
