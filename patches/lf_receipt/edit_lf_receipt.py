"""Level Factory 0.254.0 on a clone: a job's fingerprint receipt records every component its cache digest hashes,
and keeps the previous receipt when the digest moves, so a re-run can be attributed from disk. Anchored; refuses on
a miss.

    python edit_lf_receipt.py <clone>

Copies packages/jobs/receipts.py and tests/unit/test_receipt_names_every_digest_input.py from `src/`; the scheduler
writes ``fingerprint`` (BuildFingerprint.as_dict) into the receipt and moves the last receipt aside first.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("packages/jobs/receipts.py", "tests/unit/test_receipt_names_every_digest_input.py"):
    dst = C / rel
    assert not dst.exists(), rel
    shutil.copyfile(HERE / "src" / rel, dst)
    print("wrote", rel)


def edit(rel, edits):
    p = C / rel
    t = p.read_bytes().decode("utf-8")
    assert "\r\n" not in t
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:80])
        t = t.replace(old, new)
    p.write_bytes(t.encode("utf-8"))
    print("edited", rel, len(edits))


edit("packages/jobs/scheduler.py", [
    ('''        try:
            import datetime as _dt
            import json as _json
            receipt_dir = self.jobs_dir / job.job_id
            receipt_dir.mkdir(parents=True, exist_ok=True)
            (receipt_dir / "fingerprint.last.json").write_text(_json.dumps({''', '''        #
        # THE WHOLE FINGERPRINT (0.254.0): ``fingerprint`` is every component the digest hashes. The receipt used to
        # carry six of the twelve, and a job re-ran on the panel's trial level with all six identical. When the
        # digest moves, the last receipt is kept as ``fingerprint.previous.json`` so `packages.jobs.receipts` can
        # say which component moved.
        try:
            import datetime as _dt
            import json as _json
            from packages.jobs import receipts as _receipts
            receipt_dir = self.jobs_dir / job.job_id
            receipt_dir.mkdir(parents=True, exist_ok=True)
            last = receipt_dir / _receipts.LAST
            before = _receipts.read(last)
            if before is not None and before.get("digest") != job.build_fingerprint:
                last.replace(receipt_dir / _receipts.PREVIOUS)
            last.write_text(_json.dumps({'''),
    ('''                "inputs": raw_inputs,
                "evaluated_utc": _dt.datetime.now(''', '''                "inputs": raw_inputs,
                "fingerprint": fp.as_dict(),
                "evaluated_utc": _dt.datetime.now('''),
])
