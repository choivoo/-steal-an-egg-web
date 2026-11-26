# ASSET QA REPORT (자동 생성: blender/validation/validate_assets.py)

- 전체 581개, 통과 580개, 문제 1개
- 검사: GLB 존재·헤더, 생성 메타, 삼각형 예산, 썸네일. **시각 품질 점수는 자동 판정 불가 → 콘택트 시트(renders/sheet_*.png) 육안 검토로 별도 기록**

| 카테고리 | 개수 | 통과 | 평균 삼각형 | 총 용량(MB, meshopt) |
|---|---|---|---|---|
| pets | 161 | 161 | 6781 | 30.7 |
| guardians | 26 | 26 | 7496 | 5.5 |
| eggs | 150 | 150 | 1655 | 8.2 |
| treadmills | 20 | 20 | 2214 | 1.3 |
| environment | 124 | 124 | 1142 | 4.4 |
| buildings | 35 | 35 | 1188 | 1.4 |
| equipment | 25 | 25 | 755 | 0.7 |
| misc | 35 | 35 | 632 | 0.8 |
| players | 5 | 4 | 5710 | 0.8 |

## 문제
- player_1: 삼각형 초과 6152>6000
