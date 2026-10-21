"""What does the rescue's route check take away? (argv: the 0.252.0 clone, its base commit.) A temp clone at the base
commit (0.251.0's library and modules), the 0.252.0 clone's `level_design.py` copied in once as it stands and once with
the rescue's route check switched off by one anchored edit (`(keep_all or rescue)` -> `keep_all`, so a rescued chair
is asked of a reserved route only on a corner store's floor, as every chair is); each arm refurnished and sheltered by
the base's own migrations, then counted by `seats.py`, and every host it took away listed by `gone_hosts.py` against
the factory's checkout (0.251.0). The first arm must reproduce the clone's tally (`seats.out.txt`), or the second says
nothing. Writes nothing outside its temp dirs, and removes them.

    python patches/dc_table_chairs/no_route_check.py <dc_seats2 clone> 2ebc1359
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
clone, base = pathlib.Path(sys.argv[1]), sys.argv[2]
src = (clone / "level_design.py").read_text(encoding="utf-8")
OLD = "if routes and (keep_all or rescue) and on_protected_route("
assert src.count(OLD) == 1, src.count(OLD)
arms = (("the clone's level_design.py", src),
        ("the rescue's route check off", src.replace(OLD, "if routes and keep_all and on_protected_route(")))
for label, text in arms:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="dc_no_route_check_"))
    try:
        work = tmp / "dc"
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(clone), str(work)], check=True)
        subprocess.run(["git", "-C", str(work), "checkout", "-q", base], check=True)
        (work / "level_design.py").write_bytes(text.encode("utf-8"))
        for step in ("migrate_furnish_recipes.py", "migrate_shelter.py"):
            r = subprocess.run([sys.executable, "-B", step], cwd=str(work), capture_output=True, text=True)
            assert r.returncode == 0, (step, r.stderr[-1500:])
            print("[%s] %s" % (label, r.stdout.strip().splitlines()[-1]))
        r = subprocess.run([sys.executable, "-B", str(HERE / "seats.py"), str(work)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-1500:]
        print("== seats.py,", label)
        print(r.stdout.replace(str(work), "<temp clone at %s>" % base).rstrip())
        r = subprocess.run([sys.executable, "-B", str(HERE / "gone_hosts.py"), str(HERE.parents[1] / "deli_counter"),
                            str(work)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-1500:]
        print("== gone_hosts.py,", label)
        print(r.stdout.rstrip())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
