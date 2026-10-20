"""Back up, restore and check the assistant's project memory notes against docs/sessions/agent_memory/.

The notes -- the START HERE work queue, the walker's calls and their reasons, lessons paid for once -- live outside
git, in Claude Code's per-project memory folder on one machine. The walker, 2026-10-20: a new PC must not lose any
progress; asked where the copy should live, they chose this repo, public.

    python tools/agent_memory.py backup      this machine's notes -> docs/sessions/agent_memory/ (a mirror)
    python tools/agent_memory.py check       say what differs between the two; change nothing (exit 1 if any)
    python tools/agent_memory.py restore     docs/sessions/agent_memory/ -> this machine's memory folder
    python tools/agent_memory.py restore --force   ... overwriting notes there that differ

The memory folder is `~/.claude/projects/<slug>/memory`, the slug being the factory root's absolute path with every
character outside [A-Za-z0-9] made `-` (C:\\Projects\\gabagool_studios\\gabagool_factory ->
C--Projects-gabagool-studios-gabagool-factory); `--memory DIR` names another. The copy is the notes as they stand,
with one change because it is public: this machine's home folder is written `%USERPROFILE%`. A restore leaves notes
the copy lacks where they are, and without --force refuses to overwrite a note that differs, naming each.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
COPY = ROOT / "docs" / "sessions" / "agent_memory"
KEEP = {"README.md"}            # the copy's own page, never a note


def memory_dir(argv):
    if "--memory" in argv:
        return pathlib.Path(argv[argv.index("--memory") + 1])
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(ROOT))
    return pathlib.Path.home() / ".claude" / "projects" / slug / "memory"


def public(text):
    """The note as the public copy carries it: this machine's home folder, in each spelling a note might use, as
    %USERPROFILE%."""
    home = str(pathlib.Path.home())
    spellings = {home, home.replace("\\", "/")}
    if len(home) > 2 and home[1] == ":":
        spellings.add("/" + home[0].lower() + home[2:].replace("\\", "/"))
    for s in sorted(spellings, key=len, reverse=True):
        text = text.replace(s, "%USERPROFILE%")
    return text


def notes(folder):
    return {p.name: p for p in sorted(folder.glob("*.md")) if p.name not in KEEP} if folder.is_dir() else {}


def compare(mem):
    """(only in memory, only in the copy, differing): note names, the memory side read as the copy would carry it."""
    a, b = notes(mem), notes(COPY)
    differ = [n for n in sorted(set(a) & set(b))
              if public(a[n].read_text(encoding="utf-8")) != b[n].read_text(encoding="utf-8")]
    return sorted(set(a) - set(b)), sorted(set(b) - set(a)), differ


def main(argv):
    if not argv or argv[0] not in ("backup", "check", "restore"):
        print(__doc__)
        return 2
    mem = memory_dir(argv)
    if argv[0] in ("backup", "check") and not notes(mem):
        print("REFUSED: no notes in %s" % mem)
        return 2
    only_mem, only_copy, differ = compare(mem)
    if argv[0] == "check":
        print("memory %s: %d notes; copy %s: %d" % (mem, len(notes(mem)), COPY.relative_to(ROOT), len(notes(COPY))))
        for title, names in (("only in memory", only_mem), ("only in the copy", only_copy), ("differ", differ)):
            print("%s: %d %s" % (title, len(names), " ".join(names[:12]) + (" ..." if len(names) > 12 else "")))
        return 1 if (only_mem or only_copy or differ) else 0
    if argv[0] == "backup":
        COPY.mkdir(parents=True, exist_ok=True)
        for n, p in notes(mem).items():
            (COPY / n).write_bytes(public(p.read_text(encoding="utf-8")).encode("utf-8"))
        for n in only_copy:
            (COPY / n).unlink()
        print("backup: %d notes to %s (%d new, %d changed, %d removed)"
              % (len(notes(mem)), COPY.relative_to(ROOT), len(only_mem), len(differ), len(only_copy)))
        return 0
    # restore
    if differ and "--force" not in argv:
        print("REFUSED: %d notes in %s differ from the copy (--force overwrites them): %s"
              % (len(differ), mem, " ".join(differ)))
        return 1
    mem.mkdir(parents=True, exist_ok=True)
    for n, p in notes(COPY).items():
        (mem / n).write_bytes(p.read_bytes())
    print("restore: %d notes to %s (%d new, %d overwritten; %d only there, left as they were)"
          % (len(notes(COPY)), mem, len(only_copy), len(differ), len(only_mem)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
