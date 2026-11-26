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

## 업데이트 4 (TESTED)
- server/src/world.ts: 방별 서버 권위 월드 — 알 소유권(NEST/CARRIED/COOLDOWN), 수호자 FSM(SLEEP/CHASE/ATTACK/RETURN), 안전구역 판정, 이동속도 한계 17m/s로 순간이동 보정, 사거리 검사, 중복 운반 차단, 운반자 접속 종료 시 알 복귀
- 20Hz 틱, 10Hz 스냅샷 브로드캐스트. 온라인 시 클라이언트는 서버 수호자/알 상태를 따름 (오프라인 모드는 로컬 로직 유지)
- 테스트: tests/world.test.ts 6개 + e2e-world.mjs(브라우저 2개: 동일 알 경쟁 1명만 성공, 서버 수호자 추격·잡힘)
- 총 vitest 20개 통과
## 한계(중요)
- 서버 권위인 것: 알 소유권, 수호자, 귀환 판정, 이동 속도 제한. **돈/훈련/부화/펫은 여전히 클라이언트 localStorage** (조작 가능, 서버 DB 없음)
- 서버는 플레이어 실제 이동속도(훈련 능력치)를 모르고 고정 한계 17m/s를 사용 — 수호자 속도도 고정 12
- 귀환 시 알 지급은 클라이언트가 'returned' 메시지를 받아 로컬 저장에 추가(서버가 소유 알을 저장하지 않음)
- e2e 중 일부 상황(성공 귀환 온라인)은 브라우저 e2e로는 아직 미검증(단위 테스트만)

## 업데이트 5 (TESTED) — 서버 권위 경제/저장
- server/src/profiles.ts: 익명 토큰 계정(클라이언트가 랜덤 토큰 생성·localStorage 보관, 서버는 SHA-256 해시만 저장), Store 인터페이스(MemoryStore / JsonFileStore 원자적 쓰기, 손상 파일 백업 후 덮어쓰기 방지)
- 서버 판정: 훈련(트레드밀 반경 검증, 서버 시계 누적), 구매(잔액 검증), 수익·부화(서버 시계, 오프라인 정산), 슬롯 한도, 귀환 시 알 지급(서버 저장), 중복 로그인 시 이전 세션 저장 후 킥
- 클라이언트: 온라인에서는 서버 프로필을 그대로 표시, 로컬 계산/저장 중단. 오프라인 모드는 기존 localStorage 로직 유지
- 테스트: vitest 27개 통과(프로필 6, 소켓 경제 1 포함 — 이 중 소켓 테스트가 중복 로그인 진행도 유실 버그를 발견해 수정), e2e-economy.mjs(로컬 돈 조작→서버가 0으로 복원, 새로고침 후 유지)
## 한계
- 저장소는 로컬 JSON 파일(data/db.json). **Postgres 연결 없음**, 무료 호스팅의 임시 디스크에서는 재배포 시 데이터 소실 가능 → 배포 전 DB 어댑터 필요
- 계정은 익명 토큰(토큰 분실=계정 분실, 로그인/복구 UI 없음). 어드민 권한 체계 없음
- 훈련 위치 검증은 서버가 아는 위치(속도 제한 적용) 기준. 상세 치트 방어(패킷 변조 외 로직 우회)는 미감사
- 크기·돌연변이는 아직 없음

## 업데이트 6 (TESTED/부분)
- 무료 인프라 조사 → docs/FREE_TIER_LIMITS.md, docs/HOSTING_COST_REPORT.md (Render 무료는 15분 무트래픽 스핀다운·임시 디스크 → Postgres 필수)
- server/src/pgstore.ts: Postgres 저장소(배치 UPSERT, 실패 시 재시도 큐). 로컬 Postgres 16으로 영속성 테스트 통과(tests/pgstore.test.ts, TEST_PG_URL 지정 시 실행). **Neon 실제 연결은 미검증**(자격 증명 없음)
- Store 비동기화, 로그인 시 이전 세션 선저장 후 로드(경합 수정). DB 불가 시 DB_UNAVAILABLE 응답
- render.yaml 작성(미적용). **배포하지 않았으므로 공개 URL/온라인 검증 없음**
## 사용자가 해야 하는 일(권한 필요)
- Render 계정 연결 + Neon DB 생성 후 DATABASE_URL 설정, GitHub Pages 활성화(Settings→Pages→GitHub Actions)

## 업데이트 7 (TESTED)
- HTTP 엔드포인트: `/health`(Render 헬스체크), `/status`(실제 접속자·서버 목록·이벤트). 이전 버전은 HTTP 응답 경로가 없어 Render 헬스체크 실패 가능성이 컸음
- 글로벌 이벤트·어드민·감사 로그(docs/ADMIN_SYSTEM.md, docs/GLOBAL_EVENT_SYSTEM.md), SIGTERM 시 저장 후 종료, ALLOWED_ORIGINS로 Origin 검증 옵션
- 클라이언트 로비: 실제 동접자/서버 목록(/status), 자동 매칭, 코드 입장(형식 검증), 가득 찬 서버 숨기기, 서버 콜드스타트 재시도 안내, 오프라인 플레이, HUD 서버 코드 탭→복사, 이벤트 타이머, 공지 배너, 관리자 콘솔(권한자만 표시)
- 테스트: vitest 35 통과(+PG 1 조건부), e2e-lobby.mjs(모바일 390x844, 브라우저 5개) 통과
## 배포 상태
- 기본 서버 주소를 https://steal-an-egg-server.onrender.com 으로 가정(render.yaml 서비스명). 이 컨테이너에서 해당 주소는 응답 없음(타임아웃) — 실제 주소 미확인. 이 환경의 프록시는 WebSocket 업그레이드를 통과시키지 못하므로 여기서 실서버 WS 검증 불가
- GitHub Pages 워크플로는 main 푸시 시 실행. 작업 브랜치→main 병합은 사용자 승인 필요

## 업데이트 8 (TESTED) — 배포 + 레인 월드 + VOXEL 에셋
- **실제 배포 확인**: 프런트 https://choivoo.github.io/-steal-an-egg-web/ (GitHub Pages, main 푸시 시 자동), 서버 https://steal-an-egg-server.onrender.com (Render Blueprint). 배포된 게임 → WSS 접속 → 공개 서버 자동 생성·입장(1/7)을 헤드리스 브라우저로 확인
- 사용자 제공 원작 플레이 영상(프레임 추출 분석) 기반으로 월드를 **기지 → 안전선 → 13개 지역 직선 레인**으로 재구성(클라이언트·서버 공용 worldConsts). 지역당 둥지 3, 지역별 수호자 13(카탈로그 추격 속도), 지역 스트리밍(±1 지역만 모델 로드), 지역별 하늘색·바닥·벽·표지판(권장 속도)·Blender 소품·포털
- 에셋 582개 VOXEL 스타일(레퍼런스 Starlight Kitsune) — docs/ASSET_MANIFEST.md, docs/ASSET_QA_REPORT.md
- `/status`에 저장소 종류 표시(postgres / file(임시 디스크) / memory) — Render에 DATABASE_URL 미설정이면 재시작 시 진행도 소실
- 테스트: vitest 37 통과(+PG 1 조건부), e2e: 오프라인 루프·레인 6지역 스크린샷·지역 수호자 추격·온라인 경쟁·로비
## 남은 큰 작업
- 인벤토리/도감 UI(썸네일 사용), 돌연변이·크기, 낚시, 기지 확장, 퀘스트, 부화 연출, 리깅 애니메이션, 서버 이동 UI, 부하 테스트(50/100), i18n, PWA
