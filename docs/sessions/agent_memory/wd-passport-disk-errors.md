---
name: wd-passport-disk-errors
description: "2026-10-09: the walker's external WD My Passport (USB) threw 30,051 disk hardware errors 00:06-15:27 and kept re-attaching; walker told; not tied to cold 9214's import failure (9213 exported fine during them)"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-09T20:12:54.531Z
---

The Windows System log had 30,051 `disk` hardware errors on 2026-10-09,
00:06 to 15:27. The worst stretch was about 750 every ten minutes, from
10:00. Nearly all were at one block, LBA 0x3f00c000, on "Disk 2".
- **Microsoft-Windows-Partition/Diagnostic** names Disk 2 as a WD My
  Passport 2626 on USB, size reported as 0. It re-attached about a dozen
  times between 09:33 and 15:36.
- **C: and the WD hard disk are healthy:** C: is a Samsung 970 EVO NVMe;
  D: and E: are the WD10JPLX SATA disk.

**Why it is here.** It was found while chasing cold run 9214's import pass,
which stopped short at 15:30 (Level Factory 0.163.1). Nothing ties the two
together: cold run 9213 exported cleanly while the errors ran, and they had
stopped three minutes earlier.

**How to apply:**
- If a step fails strangely, look at the System log's `disk` events before
  blaming the code.
- The walker was told to copy anything that matters off that drive. Never
  touch the drive itself.
