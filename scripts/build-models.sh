#!/usr/bin/env bash
# 에셋 파이프라인: 카탈로그 → Blender 생성(4병렬, 해시로 변경분만) → 썸네일(압축 전) → meshopt 압축 → 검증
set -e
cd "$(dirname "$0")/.."
python3 blender/catalog/build_catalog.py
for i in 0 1 2 3; do blender -b --factory-startup --python-exit-code 1 --python blender/generators/generate_batch.py -- all $i 4 > /tmp/gen$i.log 2>&1 & done; wait
grep -h BATCH /tmp/gen*.log
: > /tmp/new.txt
for m in renders/batch/*.json; do f=public/assets/models/$(python3 -c "import json,sys;print(json.load(open('$m'))['model'])"); grep -q EXT_meshopt_compression "$f" || basename "$m" .json >> /tmp/new.txt; done
echo "new/changed: $(wc -l < /tmp/new.txt)"
if [ -s /tmp/new.txt ]; then
  split -n l/4 -d /tmp/new.txt /tmp/part
  for i in 0 1 2 3; do [ -s /tmp/part0$i ] && xvfb-run -a -n $((90+i)) blender -b --factory-startup --python blender/generators/render_thumbnails.py -- /tmp/part0$i 34 256 > /tmp/r$i.log 2>&1 & done; wait
  for f in $(find public/assets/models -name '*.glb'); do grep -q EXT_meshopt_compression "$f" || echo "$f"; done | xargs -r -P 4 -I{} sh -c 'npx gltf-transform meshopt "{}" "{}.tmp.glb" >/dev/null 2>&1 && mv "{}.tmp.glb" "{}"'
fi
python3 blender/validation/validate_assets.py
