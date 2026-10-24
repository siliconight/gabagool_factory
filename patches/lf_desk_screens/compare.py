"""The desk screen overlay's price, read off the three arms' reports (`price.py`): per station and heading, draws and
p95 ms in each arm, the control's spread (shipped against shipped2) beside the overlay's move (overlay against the
mean of the two shipped). Refuses a report whose shape it does not recognise. Writes compare.out.txt here.

    python patches/lf_desk_screens/compare.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def load(arm):
    d = json.loads((HERE / (arm + ".json")).read_text(encoding="utf-8"))
    assert d.get("schema") == "level_factory.perf_stations.v1" and d.get("complete") is True, (arm, d.get("schema"))
    out = {}
    for r in d["rows"]:
        for h in r["headings"]:
            out[(r["station"], float(h["yaw"]))] = (int(h["draws"]), float(h["ms_p95"]))
    assert out, arm
    return out


a, o, b = load("shipped"), load("overlay"), load("shipped2")
assert set(a) == set(o) == set(b), "the arms measured different stations"
lines = ["station                    yaw   draws shipped/overlay/shipped2    p95 ms shipped/overlay/shipped2   "
         "control spread  overlay move"]
dd, dm, spread = [], [], []
for k in sorted(a):
    (da, ma), (do, mo), (db, mb) = a[k], o[k], b[k]
    sp = abs(ma - mb)
    mv = mo - (ma + mb) / 2.0
    spread.append(sp)
    dm.append(mv)
    dd.append(do - (da + db) / 2.0)
    lines.append("%-24s %5.0f   %5d %5d %5d                   %6.2f %6.2f %6.2f              %5.2f          %+5.2f"
                 % (k[0], k[1], da, do, db, ma, mo, mb, sp, mv))
lines.append("")
lines.append("draws added by the overlay, per heading: min %+.1f, max %+.1f; headings where it added any: %d of %d"
             % (min(dd), max(dd), sum(1 for x in dd if x > 0.5), len(dd)))
lines.append("p95 move (overlay - mean shipped): median %+.2f ms, max %+.2f; control spread |shipped - shipped2|: "
             "median %.2f ms, max %.2f" % (sorted(dm)[len(dm) // 2], max(dm), sorted(spread)[len(spread) // 2],
                                           max(spread)))
office = [k for k in a if k[0].startswith("camera_socket") and abs(a[k][0] - o[k][0]) > 0]
lines.append("headings whose draws the overlay moved: %s" % sorted(office))
(HERE / "compare.out.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print("\n".join(lines))
