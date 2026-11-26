/** 레인 월드(원작 참고 동영상 구조): 기지(z>0) → 안전선 → 13개 지역이 -Z 방향 일직선 복도로 이어짐. 클라이언트·서버 공용. */
import { BIOMES, EGGS, GUARDIANS } from './defs';
export const SAFE_LINE = -14;          // z > SAFE_LINE 이면 기지 안전구역
export const LANE_HALF = 13;           // 복도 반폭(x)
export const BIOME_START = -20;        // 첫 지역 시작 z
export const BIOME_LEN = 70;           // 지역 길이
export const STEAL_RANGE = 3.5;
export const MAX_SPEED = 17;           // 서버가 허용하는 최대 이동속도(m/s)
export const biomeZ0 = (i: number) => BIOME_START - i * BIOME_LEN;
export const biomeCenter = (i: number) => biomeZ0(i) - BIOME_LEN / 2;
export const LANE_END = biomeZ0(BIOMES.length);
export const biomeAt = (z: number) => z > BIOME_START ? -1 : Math.min(BIOMES.length - 1, Math.floor((BIOME_START - z) / BIOME_LEN));
export interface Nest { biome: number; eggId: string; x: number; z: number }
/** 지역당 둥지 3곳: 해당 지역 알 중 낮은·중간·높은 등급 */
export const NESTS: Nest[] = BIOMES.flatMap((b, bi) => {
  const eggs = EGGS.filter(e => e.biome === b.id); const pick = [0, Math.floor(eggs.length * 0.45), eggs.length - 2];
  return pick.map((k, j) => ({ biome: bi, eggId: eggs[Math.max(0, Math.min(k, eggs.length - 1))].id, x: -7 + j * 7, z: biomeCenter(bi) + 8 - j * 9 }));
});
export const GUARDS = BIOMES.map((b, bi) => { const g = GUARDIANS.find(x => x.id === 'guardian_' + b.id)!; return { biome: bi, id: g.id, name: g.ko, model: g.model, speed: g.chaseSpeed, home: { x: 0, z: biomeZ0(bi) - BIOME_LEN + 12 } }; });
export const EGG_TYPES = NESTS.map(n => n.eggId);
export const eggSpawn = (i: number) => ({ x: NESTS[i].x, z: NESTS[i].z });
/** 이동 가능 영역으로 위치 보정(기지 광장 + 복도) */
export function clampToWorld(x: number, z: number): [number, number] {
  if (z > SAFE_LINE + 2) return [Math.max(-32, Math.min(32, x)), Math.min(32, z)];
  return [Math.max(-LANE_HALF + 0.6, Math.min(LANE_HALF - 0.6, x)), Math.max(LANE_END + 2, z)];
}
