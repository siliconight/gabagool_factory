"""Roadmap 214: Zoo's README points at the standard (Zoo 531db42, docs only).

Appended to item 214, anchored on its last line, which must end the file.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

TAIL = ("a knob with no effect, which CLAUDE.md calls a defect. Small; recorded here, not fixed.\n")
ADD = ("\n"
       "**ZOO POINTS AT IT** (531db42, docs only, no version). The README's \"Adding a species\" now opens on "
       "the standard and its mapping, with the authorship guide's brief per prop. It says the standard's numbers "
       "are starting points and that the measured house rules win. \"Low-poly heroes (PS1/N64)\" notes that the "
       "house target has moved to the standard's \"modernized low poly\". One copy of the standard lives at the "
       "factory root; Zoo carries the pointer.\n")


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    if text.count(TAIL) != 1 or not text.endswith(TAIL):
        sys.exit("refusing: item 214's last line is not the end of the file")
    ROADMAP.write_bytes((text + ADD).encode("utf-8"))
    print("roadmap 214: %d -> %d bytes" % (len(data), len((text + ADD).encode("utf-8"))))


if __name__ == "__main__":
    main()
