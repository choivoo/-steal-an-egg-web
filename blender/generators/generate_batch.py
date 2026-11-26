"""사용: blender -b --factory-startup --python-exit-code 1 --python generate_batch.py -- <카테고리|all> <shard> <nshards> [--only id1,id2]
결과: public/assets/models/<경로>.glb + renders/batch/<id>.json(검증 정보). 해시가 같으면 재생성 생략."""
import sys, os, json, hashlib, time, traceback
sys.path.insert(0, os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
GEN_VERSION = 'v2.0'
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['all', '0', '1']
cat_name, shard, nsh = argv[0], int(argv[1]), int(argv[2]); only = set(argv[argv.index('--only') + 1].split(',')) if '--only' in argv else None
C = json.load(open(os.path.join(ROOT, 'public/assets/manifests/catalog.json')))
import creatures, props
BUILD = {'pets': lambda s: creatures.build_creature(s), 'guardians': lambda s: creatures.build_creature(s, boss=True),
         'eggs': props.build_egg, 'treadmills': props.build_treadmill, 'environment': props.build_env, 'buildings': props.build_building,
         'equipment': props.build_equipment, 'misc': props.build_misc, 'players': props.build_player}
srcs = ''.join(open(os.path.join(os.path.dirname(__file__), f)).read() for f in ('kit.py', 'creatures.py', 'props.py'))
items = [(c, s) for c in (BUILD if cat_name == 'all' else [cat_name]) for s in C[c]]
items = [x for i, x in enumerate(items) if i % nsh == shard and (only is None or x[1]['id'] in only)]
os.makedirs(os.path.join(ROOT, 'renders/batch'), exist_ok=True); ok = fail = skip = 0
for c, s in items:
    out = os.path.join(ROOT, 'public/assets/models', s['model']); meta = os.path.join(ROOT, 'renders/batch', s['id'] + '.json')
    h = hashlib.sha1((GEN_VERSION + json.dumps(s, sort_keys=True) + srcs).encode()).hexdigest()[:16]
    if os.path.exists(out) and os.path.exists(meta) and json.load(open(meta)).get('hash') == h: skip += 1; continue
    try:
        t0 = time.time(); k = BUILD[c](s); os.makedirs(os.path.dirname(out), exist_ok=True); tris, dims = k.export(out)
        json.dump(dict(id=s['id'], cat=c, model=s['model'], tris=tris, dims=dims, bytes=os.path.getsize(out), hash=h, gen=GEN_VERSION, sec=round(time.time() - t0, 2)), open(meta, 'w')); ok += 1
    except Exception as e:
        fail += 1; print('FAIL', s['id'], e); traceback.print_exc()
print(f'BATCH {cat_name} shard {shard}/{nsh}: ok={ok} skip={skip} fail={fail}')
