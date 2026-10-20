"""docs/DRAW_CALL_BUDGET.md: the 9088 table's second column is primitives across every pass, not triangles (the
factory's roadmap 261).

The table was read off the walk overlay's perf panel, which printed Godot's `RENDER_TOTAL_PRIMITIVES_IN_FRAME` as
"tris" until Level Factory 0.226.0. That monitor counts what each render pass submits -- vertices or indices, the
shadow and depth passes included -- and moved 1.5 to 5.4 times on identical meshes with the Lux tier alone
(`docs/findings/lux_tiers/`). The finding the table supports does not change: frame time follows draws, and this
figure barely moved while it did. What changes is its name, in the table and in the two sentences that read it.
CLAUDE.md's own "1.4M triangles" sentence is the walker's text, and stays theirs to change.

Anchored; the file pinned by hash; nothing written on a miss; a second run is refused.

    python patches/patch_doc_draw_budget_prims.py
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "DRAW_CALL_BUDGET.md"
PIN = "f9dbe4d56fdd4824"
EDITS = [
    ("""**Cold run 9088's walk copy, 2026-09-27**, read off the F4 overlay while the
walker moved through the level. Same package, same machine, one session:

| draws | triangles | frame ms | GPU ms | render-CPU ms |
""", """**Cold run 9088's walk copy, 2026-09-27**, read off the F4 overlay while the
walker moved through the level. Same package, same machine, one session. The
second column is the overlay's primitives figure, which it printed as "tris"
until Level Factory 0.226.0: Godot's `RENDER_TOTAL_PRIMITIVES_IN_FRAME`, what
every pass submits, shadows and depth included -- never a triangle count
(roadmap 261; it moved 1.5-5.4x on identical meshes with the Lux tier alone):

| draws | primitives (all passes) | frame ms | GPU ms | render-CPU ms |
"""),
    ("""**Triangles again did nothing.** Across rows 2–8 the triangle count moves
1.81M → 2.07M, a 15% change, while frame time moves 7.03 → 29.90 ms, a factor
""", """**Geometry again did nothing.** Across rows 2–8 the primitive count moves
1.81M → 2.07M, a 15% change, while frame time moves 7.03 → 29.90 ms, a factor
"""),
    ("""to reopen it narrowly: at 2.07M triangles and CPU-bound submission, LOD's
value here would be in **collapsing distant objects into fewer submissions**
(visibility-range HLOD), not in thinning near geometry. That is the shape
worth a proposal; per-mesh decimation is not.
""", """to reopen it narrowly: at 2.07M primitives across all passes and CPU-bound
submission, LOD's value here would be in **collapsing distant objects into
fewer submissions** (visibility-range HLOD), not in thinning near geometry.
That is the shape worth a proposal; per-mesh decimation is not.
"""),
]


def main():
    raw = DOC.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: docs/DRAW_CALL_BUDGET.md has CRLF lines; nothing written")
    text = raw.decode("utf-8")
    got = hashlib.sha256(raw).hexdigest()[:16]
    if got != PIN:
        raise SystemExit("REFUSED: docs/DRAW_CALL_BUDGET.md is %s, not the %s this patch was written against; "
                         "nothing written" % (got, PIN))
    for old, new in EDITS:
        if text.count(old) != 1:
            raise SystemExit("REFUSED: an anchor is there %d times: %r; nothing written" % (text.count(old), old[:60]))
        text = text.replace(old, new)
    DOC.write_bytes(text.encode("utf-8"))
    print("docs/DRAW_CALL_BUDGET.md: %d edits; the 9088 table reads primitives (all passes)" % len(EDITS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
