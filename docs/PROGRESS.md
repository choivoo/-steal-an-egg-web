# 진행 현황 (정직한 상태)
## 완료·검증됨 (TESTED)
- Blender 4.0.2 설치(apt) 및 헤드리스 실행 검증, GLB 내보내기 (python3-numpy 필요)
- Blender Python 생성 스크립트로 GLB 7종: 펫 3, 알 3, 수호자 1 (public/assets/models)
- Workbench 썸네일 렌더 (xvfb 필요) -> renders/
- Three.js 게임 코어 루프: 러닝머신 훈련 → 알 훔치기 → 수호자 추격(FSM) → 안전구역 귀환 → 부화 → 펫 수익 → 러닝머신 업그레이드, localStorage 저장, 오프라인 수익/부화(타임스탬프)
- Vitest 7개 통과, Playwright(swiftshader)로 루프 전체 자동 검증(scripts/e2e.mjs)
## 미완료 (대부분)
- 모델 150펫/150알/25수호자/500에셋 중 7개만 완료. 현재 모델은 1차 수준(프리미티브 조합, 리깅·GLB 애니메이션·베이크 텍스처 없음, 드레이크 날개 품질 낮음)
- 원작 조사 문서(ORIGINAL_GAME_RESEARCH.md 등) 미작성 — 아직 웹 조사 안 함
- 지역 1개(숲)만, 인덱스/인벤토리/돌연변이/낚시/이벤트/퀘스트/기지확장/PWA/IndexedDB/i18n 없음
- 온라인 멀티플레이어·서버·DB·어드민·글로벌이벤트: 전혀 구현되지 않음 (BLOCKED 아님, 단순 미착수)
- 배포 안 됨: 공개 URL 없음. GitHub Actions 워크플로만 작성(미실행)
- 실기기 성능 미측정. 404 2건 원인 미확인(KNOWN_ISSUES)
