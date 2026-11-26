export const FOREST = { x: 0, z: -70 };
export const SAFE_R = 14;
export const STEAL_RANGE = 3.5;
export const MAX_SPEED = 17; // 서버가 허용하는 최대 이동속도(m/s)
export const eggSpawn = (i: number) => ({ x: FOREST.x - 12 + i * 12, z: FOREST.z + 4 });
export const GUARDIAN_HOME = { x: FOREST.x, z: FOREST.z - 6 };
export const EGG_TYPES = ['forest_egg', 'lake_egg', 'volcano_egg'];
