"""에셋 검증: 카탈로그의 모든 항목에 GLB·썸네일·메타가 있고, 삼각형 예산 이내, GLB 헤더 정상인지 확인 → docs/ASSET_QA_REPORT.md"""
import json, os, struct, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
C = json.load(open(os.path.join(ROOT, 'public/assets/manifests/catalog.json')))
BUDGET = {'pets': 16000, 'guardians': 25000, 'eggs': 5000, 'treadmills': 8000, 'environment': 8000, 'buildings': 8000, 'equipment': 3000, 'misc': 3000, 'players': 6000}
rows, problems = [], []; agg = collections.defaultdict(lambda: dict(n=0, tris=0, bytes=0, ok=0))
for cat, budget in BUDGET.items():
    for s in C[cat]:
        p = os.path.join(ROOT, 'public/assets/models', s['model']); mp = os.path.join(ROOT, 'renders/batch', s['id'] + '.json'); tp = os.path.join(ROOT, 'public/assets/thumbnails', s['id'] + '.png')
        issues = []
        if not os.path.exists(p): issues.append('GLB 없음')
        else:
            with open(p, 'rb') as f: magic, ver, ln = struct.unpack('<4sII', f.read(12))
            if magic != b'glTF' or ver != 2 or ln != os.path.getsize(p): issues.append('GLB 헤더 오류')
        meta = json.load(open(mp)) if os.path.exists(mp) else None
        if not meta: issues.append('메타 없음')
        elif meta['tris'] > budget: issues.append(f"삼각형 초과 {meta['tris']}>{budget}")
        if not os.path.exists(tp): issues.append('썸네일 없음')
        a = agg[cat]; a['n'] += 1; a['tris'] += meta['tris'] if meta else 0; a['bytes'] += os.path.getsize(p) if os.path.exists(p) else 0; a['ok'] += not issues
        if issues: problems.append((s['id'], issues))
total = sum(a['n'] for a in agg.values()); ok = sum(a['ok'] for a in agg.values())
L = ['# ASSET QA REPORT (자동 생성: blender/validation/validate_assets.py)', '', f'- 전체 {total}개, 통과 {ok}개, 문제 {len(problems)}개', '- 검사: GLB 존재·헤더, 생성 메타, 삼각형 예산, 썸네일. **시각 품질 점수는 자동 판정 불가 → 콘택트 시트(renders/sheet_*.png) 육안 검토로 별도 기록**', '',
     '| 카테고리 | 개수 | 통과 | 평균 삼각형 | 총 용량(MB, meshopt) |', '|---|---|---|---|---|']
for c, a in agg.items(): L.append(f"| {c} | {a['n']} | {a['ok']} | {a['tris'] // max(1, a['n'])} | {a['bytes'] / 1e6:.1f} |")
if problems: L += ['', '## 문제'] + [f'- {i}: {", ".join(x)}' for i, x in problems]
open(os.path.join(ROOT, 'docs/ASSET_QA_REPORT.md'), 'w').write('\n'.join(L) + '\n'); print(f'VALIDATE total={total} ok={ok} problems={len(problems)}')
