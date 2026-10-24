#!/usr/bin/env bash
# The 0.266.0 clone's censuses against the factory's deli_counter (0.265.0), in one session: only bins changed, bins
# by reason, bins removed, the arrangement census and the route census. Outputs beside this script.
F=/c/Projects/gabagool_studios/gabagool_factory
P=$F/patches/dc_bins_on_walls
C=$F/_scratch/dc_bins_d
cd $F || exit 9
python - > $P/only_bins_moved.out.txt <<'PY'
import glob, json, os
diff = specs = missing = 0
for p in sorted(glob.glob("deli_counter/specs/*.json")):
    n = os.path.basename(p); q = os.path.join("_scratch/dc_bins_d/specs", n)
    if not os.path.exists(q):
        missing += 1; continue
    a, b = open(p, "rb").read(), open(q, "rb").read()
    if a == b:
        continue
    specs += 1
    A, B = json.loads(a), json.loads(b)
    strip = lambda d: json.dumps(dict(d, volumes=[v for v in d.get("volumes", []) if not v["name"].startswith("litter_bin_")]), sort_keys=True)
    if strip(A) != strip(B):
        diff += 1; print("OTHER CHANGE", n)
print("specs changed", specs, "; with a change other than a litter bin:", diff, "; untracked lf_ specs not in the clone:", missing)
PY
for d in deli_counter _scratch/dc_bins_d; do (cd $d && python -c "
import glob,json,os,collections,arrangement as A
c=collections.Counter()
for p in glob.glob('specs/*.json'):
    if os.path.basename(p).startswith('lf_'): continue
    try: s=json.load(open(p,encoding='utf-8'))
    except ValueError: continue
    if not isinstance(s,dict) or not s.get('rooms'): continue
    rooms={r['id']:r for r in s['rooms'] if r.get('bounds')}
    for rid,ps in A.standing(s).items():
        if rid not in rooms: continue
        for v,w in A.reasons(rooms[rid],ps):
            if A.stem(v['name'],rid)=='litter_bin' and A.producer(v,rooms[rid])=='furnish': c[w]+=1
print('$d', dict(c), sum(c.values()))
"); done > $P/bins_library.out.txt
python -c "
import glob,json,os,sys
sys.path.insert(0,'deli_counter'); import level_design as L
for p in sorted(glob.glob('deli_counter/specs/*.json')):
    n=os.path.basename(p); q=os.path.join('_scratch/dc_bins_d/specs',n)
    if not os.path.exists(q): continue
    A=json.load(open(p,encoding='utf-8')); B=json.load(open(q,encoding='utf-8'))
    if not isinstance(A,dict): continue
    a={v['name'] for v in A.get('volumes',[]) if v['name'].startswith('litter_bin_')}; b={v['name'] for v in B.get('volumes',[]) if v['name'].startswith('litter_bin_')}
    tags={L._room_tag(r):r for r in A.get('rooms',[])}
    for x in sorted(a-b):
        r=tags[x.split('_')[2]]; x0,y0,x1,y1=r['bounds']
        print(n[:-5], x, 'room', r['id'], '%.0f m2' % ((x1-x0)*(y1-y0)))
" > $P/bins_removed.out.txt
python patches/dc_table_chairs/rooms_moved.py dump _scratch/dc_bins_d _scratch/bins_after_d.json > /dev/null
python patches/dc_table_chairs/rooms_moved.py compare _scratch/bins_before.json _scratch/bins_after_d.json > $P/rooms_moved.out.txt 2>&1
(cd $C && python arrangement.py) > $P/arrangement_0266.out.txt 2>&1
sed 's#^DC = FACTORY / "deli_counter"#DC = FACTORY / "_scratch" / "dc_bins_d"#' $P/route_cost_0265.py > $P/route_cost_0266.py
python $P/route_cost_0266.py > $P/route_cost_0266.out.txt 2>&1
rm -f $P/route_cost.json $P/route_cost.out.txt
cat $P/only_bins_moved.out.txt $P/bins_library.out.txt $P/bins_removed.out.txt
head -6 $P/arrangement_0266.out.txt
grep -E "> 1.10|closes to the body|closes to the bake|narrows from two abreast" $P/route_cost_0266.out.txt
