"""Is the release zip the package an install test certified? Every member's CRC-32 and size, side by side.

    python docs/findings/stranger_install/zip_same.py <the install test's zip> <the release zip>

Prints how many members are the same bytes (by CRC-32 and size), and lists each that differs or is in one zip only.
It reads the zips' own directories, nothing unpacked; it names differences and stops.
"""
import sys
import zipfile


def members(path):
    with zipfile.ZipFile(path) as z:
        return {i.filename: (i.CRC, i.file_size) for i in z.infolist() if not i.is_dir()}


a, b = members(sys.argv[1]), members(sys.argv[2])
same = sorted(n for n in a if n in b and a[n] == b[n])
differ = sorted(n for n in a if n in b and a[n] != b[n])
only_a, only_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
print("%s: %d files; %s: %d files" % (sys.argv[1], len(a), sys.argv[2], len(b)))
print("the same bytes: %d" % len(same))
for n in differ:
    print("differ: %s  (%d -> %d bytes)" % (n, a[n][1], b[n][1]))
for n in only_a:
    print("only in the first: %s" % n)
for n in only_b:
    print("only in the second: %s" % n)
