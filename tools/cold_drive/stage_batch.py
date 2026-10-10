"""Stage cold run N's batch from run PREV's: copy batch.json and briefs/, and
set BOTH the batch id and the description -- 9148 to 9151 were staged by
copying and editing only the description, and all four ran as 'cold_9147'.

    python tools/cold_drive/stage_batch.py <N> <PREV> "<description>"
"""
import json
import pathlib
import shutil
import sys

# the factory is two directories above this file, wherever it was unpacked (roadmap 202)
F = pathlib.Path(__file__).resolve().parents[2] / "docs" / "cold_runs"
n, prev, desc = sys.argv[1], sys.argv[2], sys.argv[3]
src, dst = F / f"cold_{prev}", F / f"cold_{n}"
assert not (dst / "batch.json").exists(), f"{dst} already staged"
dst.mkdir(parents=True, exist_ok=True)
d = json.loads((src / "batch.json").read_text(encoding="utf-8"))
d["batch_id"] = f"cold_{n}"
d["name"] = desc
(dst / "batch.json").write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8", newline="\n")
if (src / "briefs").is_dir():
    shutil.copytree(src / "briefs", dst / "briefs")
check = json.loads((dst / "batch.json").read_text(encoding="utf-8"))
assert check["batch_id"] == f"cold_{n}", check["batch_id"]
print("staged", dst, "batch_id", check["batch_id"])
