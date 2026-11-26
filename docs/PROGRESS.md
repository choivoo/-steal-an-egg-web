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

## 업데이트 2 (TESTED)
- docs/ORIGINAL_GAME_RESEARCH.md: 웹검색 2회 기반(2차 자료, 대부분 UNVERIFIED) — 공식 페이지 직접 열람 못함
- server/src/rooms.ts: RoomManager(방당 7명 서버측 강제, 자동매칭, 6자리 코드, 마지막 슬롯 경합, 중복 접속 방지, 빈 방 종료) — 단위테스트
- server/src/index.ts: ws 서버. 실제 소켓 15명 → 7+7+1 검증, 코드 FULL/BAD_CODE, pos 브로드캐스트, 레이트리밋(초당 60)
- 총 테스트 14개 통과
## 여전히 미구현 (온라인)
- 서버 권위 경제/알/수호자 동기화, DB·계정, 서버 목록·코드 입력 UI(현재는 URL 파라미터만), 어드민, 글로벌 이벤트, 호스팅 조사·배포, 부하테스트

## 업데이트 3 (TESTED)
- 클라이언트↔서버 연결(src/net/client.ts): `?ws=ws://host:8080` 로 활성화, `&code=XXXXXX` 코드 접속. 지수 백오프 재접속(최대 5회), 미연결 시 "오프라인 모드" 표시(가짜 접속자 없음)
- 원격 플레이어 3D 표시(보간), 퇴장 처리, 서버 코드/인원/접속자/서버 수 HUD (서버 집계값)
- e2e(scripts/e2e-net.mjs): 실제 브라우저 2개 — 상호 표시, 퇴장 후 제거, 인원 갱신 확인
- 원격 플레이어는 임시 캡슐(캐릭터 모델·애니메이션 동기화 없음). 서버는 위치 릴레이만 — 서버 권위 아님
- 실행: `npm run server` (포트 8080)
