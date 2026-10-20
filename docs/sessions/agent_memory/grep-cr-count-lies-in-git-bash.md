---
name: grep-cr-count-lies-in-git-bash
description: "`grep -c $'\\r' file` in this machine's Git Bash counts EVERY line, so an LF file reads as all-CRLF; count b'\\r\\n' with Python"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-20T00:05:22.087Z
---

On 2026-10-19 `grep -c $'\r'` reported layout_lint.py as 1668 CRLF lines of 1668 in a fresh Deli Counter clone; Python's `read_bytes().count(b'\r\n')` said 0, and `git ls-files --eol` said `w/lf`. The grep count equals `wc -l` on any file: it is the broken instrument, not the file.

**Why:** a line-ending scare stops a patch (the generators assert LF) and invites a "fix" that would actually introduce CRLF. CLAUDE.md already says compare bytes, not characters; this is the shell-side trap of the same rule.

**How to apply:** check endings with `python -c "b=open(p,'rb').read(); print(b.count(b'\r\n'), b.count(b'\n'))"` or `git ls-files --eol <file>`; never with grep in Git Bash. Related: [[bash-heredoc-large-bodies-fail]], [[bash-cwd-drifts-between-calls]].
