"""The walker chose the cruiser's livery, 2026-10-09: "black and white". It is
already Zoo 1.86.0's default (`cruiser_forms.DEFAULT_LIVERY`), so no code
moves; the two places that left the choice open now say it is made.

Anchored; each anchor once, or nothing is written.
"""
import pathlib
import sys

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")

EDITS = {
    ROOT / "docs" / "findings" / "cruiser_build" / "README.md": [
        ("**The light bar is red on the driver's side from every angle.** Which\n"
         "livery is the default is the walker's to choose.\n",
         "**The light bar is red on the driver's side from every angle.** Which\n"
         "livery is the default is the walker's to choose.\n"
         "- *Chosen 2026-10-09:* \"black and white\". It was already the default\n"
         "  (`cruiser_forms.DEFAULT_LIVERY`), so no code moved; `white_blue` stays\n"
         "  a form a slot can ask for.\n"),
    ],
    ROOT / "PIPELINE_ROADMAP.md": [
        ("  - **The livery is the walker's to choose.** Both are shown in the finding's frames.\n",
         "  - **The livery is the walker's to choose.** Both are shown in the finding's frames. *Chosen "
         "2026-10-09: \"black and white\", already the default.*\n"),
    ],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        if b"\r\n" in data:
            sys.exit(f"refusing: {path.name} has CRLF endings")
        text = data.decode("utf-8")
        for old, new in pairs:
            n = text.count(old)
            if n != 1:
                sys.exit(f"refusing: {path.name} anchor matches {n} times")
            text = text.replace(old, new)
        staged[path] = text.encode("utf-8")
    for path, raw in staged.items():
        path.write_bytes(raw)
        print("ok", path.name)


if __name__ == "__main__":
    main()
