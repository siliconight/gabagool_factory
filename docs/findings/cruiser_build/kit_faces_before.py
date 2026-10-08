"""Does `test_no_two_kit_faces_share_a_plane` fail on the kit as it stood
before the census? It must, or it proves nothing.

    python kit_faces_before.py <zoo repo at 1.86.0 or later>

`cruiser_forms_pre_census.py` beside this file is `core/cruiser_forms.py` as
it stood before the first census: rebuilt by reversing the census's edits,
its relative import made absolute so it loads beside the package. Its kit
takes (lay, seat) -- the partition at a guessed y_fs + 0.38, no cabin. This
runs the shipped test's own `_coincident` over that kit at the genome's 27
corners, through the test's own `_lay` and `_seat`. Prints what it measured
and stops.
"""
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def main(zoo):
    zoo = pathlib.Path(zoo).resolve()
    sys.path.insert(0, str(zoo))
    sys.path.insert(0, str(zoo / "tests"))
    spec = importlib.util.spec_from_file_location("cruiser_forms_pre_census",
                                                  HERE / "cruiser_forms_pre_census.py")
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    import test_cruiser as T
    total, worst = 0, 0
    for dims in T.CORNERS:
        lay = T._lay(dims)
        boxes = [b for rows in old.kit(lay, T._seat(lay)).values() for b in rows]
        n = len(T._coincident(boxes))
        now = [b for rows in T._kit(lay).values() for b in rows]
        total += n
        worst = max(worst, n)
        print("%-20s before %3d face pairs, as shipped %d" % (dims, n, len(T._coincident(now))))
    print("before: %d coincident face pairs over %d corners, at most %d a corner" % (total, len(T.CORNERS), worst))


if __name__ == "__main__":
    main(sys.argv[1])
