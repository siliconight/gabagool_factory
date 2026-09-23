"""Set-dressing reference: ladders, rusted outdoors and clean indoors.

The walker's call, 2026-09-23, with two reference photographs, given while cold
run 9071 was in flight -- so this records the decision and the groundwork; the
tool change waits for the run to end.

Anchored on the closing section, which must match exactly once. The line ending
is DERIVED from the file rather than assumed: this document is CRLF (741 CRLF,
0 bare LF, 45,711 bytes) while the roadmap beside it is LF, and the first
version of this patch refused because it assumed otherwise. That refusal is
the guard working.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "docs" / \
    "SET_DRESSING_REFERENCES.md"

ANCHOR = "## What the references do not settle\n"

SECTION = """## Ladders — rusted outside, clean inside

**The walker's call, 2026-09-23, with two references.** Outdoor ladders are
rusted; indoor ladders are clean. It is a two-way split, which is the point: a
single material for "ladder" is wrong in one of the two places it lands, which
is why the slab reveal's one-family choice could not simply be copied here.

**Reference 1 — the outdoor ladder.** A fixed steel ladder bolted flat to a
poured-concrete wall. Rust is the dominant read: orange-brown bleeding down
from every bolt and bracket, the rails streaked with it, the original pale
paint surviving only in patches between. The brackets are separate flat plates
standing proud of the wall, each with its own bloom running onto the concrete
below. The wall behind carries its own staining and form-tie marks, so the
ladder is not the only weathered thing in frame — it sits in a weathered wall.

**Reference 2 — the indoor ladder.** A dark steel ship's ladder at a steep
pitch, clean and recently made: matte near-black rails and stringers, no
corrosion anywhere, and treads of bright galvanised diamond plate that catch
the light against the dark frame. The value contrast between dark frame and
bright tread is what reads at distance, more than any texture on either. It
stands against a wood-plank tiled wall — an interior finish, not a structural
one.

**What the pipeline has, measured 2026-09-23 on cold run 9070's package:**
nothing. A ladder is Deli Counter's greybox boxes and stays that way into a
themed package — `ladder<n>_rail_<story>_<sgn>` and `ladder<n>_rung_<story>_<r>`
(`deli_counter.py:2032`), all on flat `gb_ladder`, 38 surfaces, 22.82 m2. The
`greybox_skin` gate counts them and deliberately does NOT refuse on them:
nothing has ever skinned a ladder, so this is an absent capability rather than
a regression. They are rails and rungs as plain boxes — no brackets, no tread
plate, no stand-off from the wall.

**The fallback is YELLOW, not grey, and it is yellow on purpose.** Recorded
because it was got wrong in the conversation that produced this section.
`GREYBOX_PALETTE` (`deli_counter.py:326`) gives `gb_ladder` (1.00, 0.90, 0.55)
— luminance 0.897, the BRIGHTEST value on the site — beside `gb_stair`'s
(1.00, 0.78, 0.32). Its own comment says why: a ladder "gets the brightest
value on the site because it is the smallest thing that has to be found", and
it is seen against the wall it is bolted to (0.710) and the roof it arrives
at, never against the floor. The slab collar that started this work is a
different case and genuinely IS grey: `gb_floor` is (0.52, 0.52, 0.55).

(Those are LINEAR glTF factors. Godot reports the same materials in sRGB —
0.52 linear reads back as 0.748 — and two instruments disagreeing by exactly
that gamma is the colour space, not a defect.)

**So skinning a ladder SPENDS a legibility signal, and that is a real cost,
not a detail.** The palette is built on value separation for greyscale, low
light and colourblind play; a rusted ladder on a rusted exterior wall is
precisely the "amber and grey reading as one surface" failure the palette's
own comment describes, arriving through the back door. Reference 2 already
carries the answer for indoors — dark frame against bright galvanised tread is
a value contrast, not a hue one — and the outdoor skin needs the equivalent
found deliberately rather than assumed: the brackets and rail edges catching
light against a darker wall, or the rungs held brighter than the rails.
Whatever is chosen, it should be MEASURED against the wall it lands on, the
way the palette's own values were.

**The discriminator already exists and nothing needs inferring.**
`spec_types.Ladder.placement_mode` is `interior` / `exterior_wall` / `platform`
/ `shaft` (`spec_types.py:217`), authored per ladder. Rusted is
`exterior_wall` and `platform`; clean is `interior` and `shaft`. Do NOT reach
for `cut_slabs` as a proxy for indoors — it says whether the ladder passes
through a floor plate, a different question that merely correlates.

**Owners.** Zoo — a `ladder` species with the structure the photographs show,
because the walker's standing preference is species-true structure before
texture tricks: two rails, rungs, and separate wall brackets standing the
rails off the wall, forms `fixed_vertical` and `ship` (the second with
diamond-plate treads and a handrail, per reference 2). Pixelcoat — two skins,
a rusted steel and a clean dark steel with a bright galvanised tread, since
neither exists in any kit module today and `_family_material` can only borrow
what a building's pack already wears. Deli Counter — carry `placement_mode`
into the emitted node name the way `stair<n>col_` and `stair<n>ramp_` already
carry their kind, so the skin can be chosen without adding a second material
to the greybox palette and without guessing from position.

**Not a texture-only job, and saying so before anyone prices it as one.** The
slab collar was fixed by swapping one material on geometry that was already
the right shape. A ladder is not: boxes with a rust texture on them are still
boxes, and the brackets and tread plate in both photographs are structure. The
cheap version exists — skin the existing boxes and take the value contrast —
and is worth doing first if it is wanted sooner, but it should be recorded as
the cheap version rather than sold as the look.

"""

NEW = SECTION + ANCHOR


def _eol(data: bytes) -> str:
    """The file's line ending, DERIVED rather than assumed.

    CLAUDE.md records what assuming costs: a helper asked `CRLF in anchor` of a
    single-line anchor containing no newline at all, answered LF for a CRLF
    document, and wrote 81 bare LF lines into it. A mixed file refuses.
    """
    crlf = data.count(b"\r\n")
    bare = data.count(b"\n") - crlf
    if crlf and bare:
        raise SystemExit(f"REFUSED: mixed endings, {crlf} CRLF and {bare} LF")
    return "\r\n" if crlf else "\n"


def main() -> None:
    data = TARGET.read_bytes()
    eol = _eol(data)
    text = data.decode("utf-8")
    anchor = ANCHOR.replace("\n", eol)
    replacement = NEW.replace("\n", eol)
    hits = text.count(anchor)
    if hits != 1:
        raise SystemExit(f"REFUSED: anchor matched {hits} times")
    before = len(data)
    out = text.replace(anchor, replacement).encode("utf-8")
    if _eol(out) != eol:
        raise SystemExit("REFUSED: would change the file's line endings")
    TARGET.write_bytes(out)
    print(f"SET_DRESSING_REFERENCES.md: {before} -> {len(out)} bytes "
          f"(+{len(out) - before}), endings unchanged ({eol!r})")


if __name__ == "__main__":
    main()
