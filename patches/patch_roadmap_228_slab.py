"""Roadmap 228: 9226's "pale slab" was a backdrop warehouse's lit window, not a container's roof (cold run 9240).

Appends one paragraph to 228's body; its status is not touched (the slab is one of the looks its
status lists, and the paragraph corrects it where the item's history is kept). Run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_228_slab.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
HEAD = "\n\n**228. The edge of the plate: E, varied by level.**"
TAIL = ("Two calls for the walker: a minimum distance from an elevated station for the near band, and "
        "the guides' alpha-card method for the lobes (step G) before the forms become species. Not "
        "proven: the parkland by day, the player's eye at the fence, the price on the low-end target.")
ADD = """

**THE PALE SLAB WAS A LIT WINDOW, 2026-10-11** (cold run 9240, `docs/cold_runs/cold_9240/NOTES.md`, `slab_ray.py`). 228's status lists "a container's near-white roof reads as a pale slab over the roofline from an elevated view (9226)" among the looks, and Zoo 1.99.0 darkened the container's roof for it. **Retracted.** `elev_W` is an orthographic camera looking level, so it sees no horizontal face; its rays through the slab meet one backdrop box in front of the eye, the warehouse `backdrop_117` 91 m off, and land in its third high window of six, which Zoo paints lit cool white -- the window's top at 6.20 m is the slab's top edge, its bottom behind the storefront's roofline, and the orthographic projection draws it at its full 1.8 m where a person would see a few pixels through rain. 9240 on 9226's brief shows the slab unchanged, mean (192, 199, 202) in both packages, and 9226's own backdrop-off control had already put it in the backdrop. 1.99.0's roof shade stays as a look (no draw, no triangle) and fixed nothing seen; no camera has yet looked down on the near band's containers, because every elevated station is orthographic. The general lesson is in 9240's notes: a frame is not evidence about an object until something says which object drew it, and the slot manifest plus the shots report are enough to say so."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE PALE SLAB WAS A LIT WINDOW" not in text, "already applied"
    assert text.count(HEAD) == 1, "228's heading not found once"
    h = text.index(HEAD)
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h, "no status after 228"
    body = text[h:nxt]
    assert body.endswith(TAIL), ("228's body does not end where this patch read it", body[-160:])
    text = text[:nxt] + ADD + text[nxt:]
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 228's slab paragraph appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
