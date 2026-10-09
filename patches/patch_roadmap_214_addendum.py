"""Roadmap 214: the standard's Addendum A (subdivision, sculpt and
retopology, multires), and the priced trials it gives Zoo.

Anchored on 214's status line ("seven gaps") and on the item's last line,
which must end the file; refuses otherwise.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

OLD_STATUS = ("maps it onto Zoo 1.86.0's minting, measured: what Zoo already does, seven gaps, and where a measured "
              "house rule decides. Next: the asset record's missing fields, a budget class per genome, and the "
              "standard's A/B/C review on its three approval assets.*\n")
NEW_STATUS = ("maps it onto Zoo 1.86.0's minting, measured: what Zoo already does, nine gaps, and where a measured "
              "house rule decides. Addendum A, from the walker's notes the same day, adds subdivision modeling, "
              "sculpt and retopology, and multires. Next: the asset record's missing fields, a budget class per "
              "genome, the standard's A/B/C review on its three approval assets, and Addendum A.4's priced trials, "
              "weighted normals and convex-edge wear first.*\n")

TAIL = ("house target has moved to the standard's \"modernized low poly\". One copy of the standard lives at the "
        "factory root; Zoo carries the pointer.\n")
ADD = (
    "\n"
    "**ADDENDUM A (2026-10-08).** The walker: \"I missed some parts in that docx\", namely subdivision modeling "
    "and the topology that goes with it (support edges, edge reduction methods), sculpt and retopology, and the "
    "multires modifier, with a sculpt-and-retopology walkthrough and a retopology tutorial. Written into the "
    "standard as Addendum A, before its references, in this project's terms; the `.docx` is unchanged.\n"
    "- **A.1 Subdivision modeling.** Support loops, creases and pre-subdivision bevels, quads where the surface "
    "curves, poles off the highlights, and edge reduction. It is a bake source or a priced level-1 hero mesh, "
    "never a runtime modifier.\n"
    "- **A.2 Sculpt and retopology.** The eight-step workflow and retopology practice, for human-made "
    "characters, food and damage, which enter through Zoo's ingest.\n"
    "- **A.3 Multires.** Normal maps only here: displacement needs a subdivided render mesh.\n"
    "- **A.4 The priced trials Zoo could run,** cheapest first:\n"
    "  1. weighted normals;\n"
    "  2. convex-edge wear in vertex colour. `wear_colors` darkens concave vertices only. No texture.\n"
    "  3. a procedural bake source: a creased or support-looped second build under a Subdivision Surface "
    "modifier, baked onto the game mesh. One texture per species, no triangles. Zoo bakes nothing today.\n"
    "  4. procedural detail on that bake source.\n"
    "- **A.5 What does not change.** No subdivided mesh at runtime; a normal map is a texture in the part "
    "family's one material; triangles are counted on the game mesh.\n"
)


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    if text.count(OLD_STATUS) != 1:
        sys.exit("refusing: 214's status anchor matches %d times" % text.count(OLD_STATUS))
    if text.count(TAIL) != 1 or not text.endswith(TAIL):
        sys.exit("refusing: item 214's last line is not the end of the file")
    text = text.replace(OLD_STATUS, NEW_STATUS) + ADD
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 214: %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
