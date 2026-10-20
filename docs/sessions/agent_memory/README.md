# The assistant's project memory, backed up

**What it is.** A copy of the notes the coding assistant keeps for this project between sessions: `MEMORY.md`, the
index loaded into every session, and one note per fact -- the START HERE work queue (`open-work-2026-10-09.md`), the
walker's calls with their reasons, and lessons this repo has paid for once. They live outside git, in Claude Code's
per-project memory folder on one machine, so until 2026-10-20 a new PC would have started without them. The walker,
that day: no progress lost to a new PC -- and, asked where this copy should live, this repo, public.

**What it is not.** Source of truth for anything the repo records itself. `CLAUDE.md`, `docs/FILING.md`,
`docs/COMMANDS.md`, the roadmap and the CHANGELOGs win over a note that disagrees; a note is what was believed when it
was written, and says when.

**The copy is the notes as they stand**, with one change because it is public: the machine's home folder is written
`%USERPROFILE%`.

    python tools/agent_memory.py backup     # refresh this copy from the memory folder (each release does)
    python tools/agent_memory.py check      # what differs, changing nothing
    python tools/agent_memory.py restore    # on a new PC: the copy into its memory folder

The memory folder is `~/.claude/projects/<slug>/memory`, the slug being the factory root's absolute path with every
character outside [A-Za-z0-9] made `-`; clone the factory to the same path and `restore` finds it, or pass
`--memory <folder>`.
