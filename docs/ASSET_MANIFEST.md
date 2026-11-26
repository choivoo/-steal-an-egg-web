# ASSET MANIFEST
- 단일 소스: `public/assets/manifests/catalog.json` (생성: `blender/catalog/build_catalog.py`, 고정 시드)
- 생성: `scripts/build-models.sh` → Blender 4.0.2(apt) 헤드리스, `blender/generators/{kit,creatures,props,generate_batch}.py`, 4병렬, 소스+스펙 해시로 변경분만 재생성
- 스타일: **VOXEL** (사용자 레퍼런스 Starlight Kitsune 기준) — 베벨 박스, 16px 픽셀 텍스처(Closest), 월드 좌표 박스 UV(픽셀 크기 통일), 큰 부위 inverted-hull 검정 외곽선, 발광 재질
- 압축: meshopt(gltf-transform), 썸네일: Workbench 텍스처 모드 256px (`public/assets/thumbnails/<id>.png`)
- 레퍼런스 정밀 재현 모델: `blender/reference/starlight_kitsune.py` (+ .blend, 렌더 비교 renders/kitsune/)

| 카테고리 | 개수 | 비고 |
|---|---|---|
| 펫 | 161 (+키츠네 1 = 162) | 13개 체형 계열 × 부위 조합(뿔6·귀5·꼬리8·등8·날개6·눈4종) 서명 중복 없음, 최고 등급 전용 5종 |
| 알 | 150 | 13지역, 5형태 × 16장식 조합 |
| 수호자/보스 | 13 + 13 | |
| 러닝머신 | 20 | 단계별 장식 누적 |
| 환경 | 124 | 지역별 9종 + 공용 7 |
| 건축 | 35 | 지역 포털 13 포함 |
| 장비 | 25 | 낚싯대 8·찌 4·뜰채 3·가방 5·모자 5 |
| 기타 | 35 | 물고기 12·상자 5 등 |
| 플레이어 | 5 | |
| **합계** | **582** | |

## 정직한 한계
- 크리처 대부분은 **절차적 조합 디자인**이다. 체형·부위 서명은 모두 다르지만, 손으로 하나씩 다듬은 키츠네 수준의 개별 완성도는 아니다(콘택트 시트 renders/sheet_*.png로 확인 가능).
- **리깅/GLB 애니메이션 없음**(키츠네 포함). 게임 내 움직임은 코드상 절차 애니메이션(통통 튀기 등).
- 슬라임/정령 계열은 층 쌓은 형태가 비슷해 보이는 경향이 있음 → 개선 대상.
- 게임에 실제 적용된 것: 숲 환경 9종, 건축 7종, 러닝머신 20단계, 플레이어 1, 숲 수호자 1, 숲 알 3종 + 그 부화 펫(숲 12종). 나머지 지역 에셋은 아직 월드에 배치되지 않음(지역 확장 미구현).
