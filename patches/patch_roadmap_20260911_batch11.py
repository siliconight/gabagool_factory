"""Roadmap batch 11, 2026-09-11: item 110's close gains the engine-side count.

One exact-once anchor inside the status block written by batch 10; the
sentence is extended, nothing else moves.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD = ("`export_closure_scan` ok with 0 issues, portability PASS with the\n"
       "scene instantiated and 0 parser errors. THREE THINGS FOUND ON THE WAY, ALL\n")
NEW = ("`export_closure_scan` ok with 0 issues, portability PASS with the\n"
       "scene instantiated and 0 parser errors -- and, read off the RUNNING\n"
       "package by the new `tools/dressing_census.py` rather than off the file\n"
       "that asked for it: 4 MultiMeshInstance3D nodes under\n"
       "`/root/Mission/county_hospital_001_dressing`, 1,094 instances, 1,094\n"
       "visible, every mesh resolved, origins on the ground plate at y 0.00\n"
       "spanning x -30.5..30.5 and z -34.5..34.5. THREE THINGS FOUND ON THE WAY, ALL\n")


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    n = text.count(OLD)
    if n != 1:
        print(f"anchor matched {n} times; refusing", file=sys.stderr)
        return 1
    out = text.replace(OLD, NEW).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
