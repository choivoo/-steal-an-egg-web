# STEAL AN EGG: WEB EDITION — 세션 재개 가이드
마스터 프롬프트 요약: Three.js + Blender(GLB) 3D 알 훔치기 게임, 온라인 멀티(방당 7명, 공개서버만), 어드민, 무료 인프라. 상세는 docs/PROGRESS.md, docs/NEXT_ACTIONS.md.
명령: `scripts/setup-cloud.sh`(Blender), `npm run models`(GLB 생성), `xvfb-run -a blender -b --python blender/generators/render_thumbnails.py`, `npm test`, `npm run build`, e2e: vite preview 후 `node scripts/e2e.mjs`.
Playwright는 executablePath '/opt/pw-browsers/chromium' 사용.
