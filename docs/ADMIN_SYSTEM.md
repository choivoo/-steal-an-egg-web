# 어드민 시스템 (IMPLEMENTED, TESTED: 단위+소켓+브라우저)
- 역할: OWNER > SUPER_ADMIN > ADMIN > EVENT_MANAGER > MODERATOR > PLAYER. **서버 환경변수 ADMIN_ROLES** 로만 부여: `<계정키>:OWNER,<계정키>:ADMIN` (계정키 = 게임 토큰의 SHA-256, 64자리 hex). 클라이언트/닉네임/LocalStorage 값으로는 권한 불가.
- OWNER 계정키 얻는 법: 내 브라우저 localStorage `sae_token` 값의 SHA-256. (추후 게임 내 "내 계정키 보기" 버튼 제공 예정)
- 명령(서버가 형식·권한 검증, 셸/SQL/JS 실행 없음): `/event start <treadmill|income|hatch_speed|cosmic_eclipse> <배율>x <분>m global`, `/event stop ID`, `/event preset ORIGINAL|CLASSIC_CUSTOM`, `/announce global 메시지`, `/server status`, `/server drain CODE`, `/player kick PID 사유`
- 감사 로그: 모든 명령 기록(최근 500건, 저장소 meta:audit). 공지는 textContent로 렌더(HTML 실행 없음).
- 미구현: 관리자 웹 대시보드 탭 18종(현재는 명령 콘솔만), 기간 정지, 알/수호자 소환, 서버 재시작 명령, 2단계 확인 UI
