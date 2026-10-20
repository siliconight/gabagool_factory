---
name: bash-heredoc-large-bodies-fail
description: "In this harness a long quoted heredoc fails to parse and nothing runs, and even a short quoted heredoc collapses a double backslash to one; write such scripts with the Write tool and run them from disk."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4bb794c9-c366-4613-95bd-3c61e9a0d0f9
  modified: 2026-10-11T06:06:45.412Z
---

Three times on 2026-09-11 a `python - <<'EOF' ... EOF` body over ~100 lines
failed. They were anchored patch scripts with triple-quoted docstrings and
apostrophes.
- Each came back "unexpected EOF while looking for matching `''".
- NOTHING in the command ran, including unrelated commands before the
  heredoc.
- Short heredocs (under ~60 lines, few quotes) run fine.

**Backslashes, 2026-10-06.** Even inside `<<'EOF'`, which should pass text
untouched, a `\\` reached Python as one `\`.
- A one-line test printed `len("\\r") == 1`, the character 13.
- A heredoc scanner looking for literal-backslash line-ending guards
  therefore looked for real CR/LF instead, and flagged twelve correct
  patches.
- A single escape like `b"\r\n"` still reaches Python as written.

**Why:** both failures are in the harness's shell handling, not the script.
The first silently costs a turn. The second silently changes what a script
checks, which is worse: it produces a confident wrong answer.

**Broken three more times on 2026-10-06, in one session, despite this note:**
- A Windows path `"\\%s\\art"` reached Python as `\a`, a bell character, and
  the file was not found.
- A regex `\\[` in an edit script wrote literal CR/LF into a source file.
- A `newline="\\n"` anchor turned into a real newline and missed.
- **The rule is now absolute: ANY backslash in a heredoc body goes through
  the Write tool. Use forward slashes in Windows paths.**

**Broken five more times by 2026-10-10.** The fifth wrote a real CR byte into
`.gitattributes`: the comment `\\r` in a Python bytes literal reached Python as
`\r`. It was caught only because `tail` showed `/bin/sh` with nothing after it.
After any heredoc edit, count the file's `\r` bytes.

**And again on 2026-10-11, into a findings README.** A section of markdown
carrying Windows paths (`C:\\blender\\5.1\\python\\bin`, `.\\factory`) went
through a heredoc'd Python string: `\b`, `\f` and an octal `\5` landed as
NINE control characters in the committed-to-be file. Python warned
("invalid escape sequence") and that warning was the only tell. Also: a
`python -c "..."` one-liner with a backslash in it fails the same way.
- Prose with a Windows path is a body with a backslash. Write the text to a
  file with the Write tool and swap it in with a script run from disk.
- After any shell-routed write, scan the file for
  `[\x00-\x08\x0b\x0c\x0e-\x1f]` (with a script written by the Write tool).

**How to apply:**
- Write a script to the scratchpad and run it with `python <path>` when:
  - its body is longer than a screen;
  - it contains triple quotes;
  - it contains a backslash of ANY kind (paths, regexes, escapes).
- A roadmap patch goes under the repo's `patches/` instead of the
  scratchpad.
- Keep heredocs for short, quote-light, backslash-free bodies.

Related: [[gabagool-roadmap-edit]] patches already live under `patches/`.
