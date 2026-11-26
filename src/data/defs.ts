/** 게임 데이터 = Blender 카탈로그(public/assets/manifests/catalog.json)가 단일 소스. 수치는 모두 독자 설정(원작 수치 아님). */
import catalog from '../../public/assets/manifests/catalog.json';
export interface Rarity { id: string; name: string; color: string }
export interface Biome { id: string; ko: string; en: string; ground: string; sky: string; requiredSpeed: number; index: number }
export interface PetDef { id: string; name: string; nameEn: string; biome: string; model: string; rarity: string; income: number; scale: number; arche: string }
export interface EggDef { id: string; name: string; biome: string; model: string; rarity: string; weight: number; hatchSec: number; pets: { id: string; w: number }[] }
export interface TreadmillDef { id: string; name: string; cost: number; gain: number; model: string }
const C = catalog as any;
export const RARITIES: Rarity[] = C.rarities.map((r: any) => ({ id: r.id, name: r.ko, color: r.color }));
const RI = (id: string) => RARITIES.findIndex(r => r.id === id);
export const BIOMES: Biome[] = C.biomes;
export const PETS: PetDef[] = C.pets.map((p: any) => ({ id: p.id, name: p.ko, nameEn: p.en, biome: p.biome, model: p.model, rarity: p.rarity, income: p.income, scale: 0.55 + RI(p.rarity) * 0.04, arche: p.arche }));
export const EGGS: EggDef[] = C.eggs.map((e: any) => ({ id: e.id, name: e.ko, biome: e.biome, model: e.model, rarity: e.rarity, weight: e.weight, hatchSec: e.hatchSec, pets: e.pets }));
export const TREADMILLS: TreadmillDef[] = C.treadmills.map((t: any) => ({ id: t.id, name: t.ko, cost: t.cost, gain: t.gain, model: t.model }));
export const GUARDIANS = C.guardians as { id: string; ko: string; biome: string; kind: string; model: string; chaseSpeed: number }[];
export const ENVIRONMENT = C.environment as { id: string; biome: string; kind: string; model: string }[];
export const BUILDINGS = C.buildings as { id: string; kind: string; biome?: string; model: string }[];
export const PLAYERS = C.players as { id: string; model: string }[];
export const MISC = C.misc as { id: string; kind: string; model: string }[];
export const EQUIPMENT = C.equipment as { id: string; kind: string; tier: number; model: string }[];
