"""extraction_15, the station the sky arm reported over its frame budget: each heading's draws, median and p95 ms in
the three arms of `price.py`. Measurements only.

    python docs/findings/sky_life_307/extraction_15.py > docs/findings/sky_life_307/extraction_15.out.txt
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
for arm in ("ctrl", "sky", "ctrl2"):
    d = json.loads((HERE / ("price_%s.json" % arm)).read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if str(r.get("station") or r.get("name") or r.get("anchor")) == "extraction_15"]
    assert len(rows) == 1, (arm, len(rows))
    print(arm, " ".join("yaw %g: %d draws %.2f/%.2f ms" % (h["yaw"], h["draws"], h["ms_median"], h["ms_p95"])
                         for h in rows[0]["headings"]))
