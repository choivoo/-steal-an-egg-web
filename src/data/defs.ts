export interface Rarity { id: string; name: string; color: string }
export const RARITIES: Rarity[] = [
  { id: 'common', name: '커먼', color: '#9aa0a6' }, { id: 'uncommon', name: '언커먼', color: '#4caf50' },
  { id: 'rare', name: '레어', color: '#2196f3' }, { id: 'epic', name: '에픽', color: '#9c27b0' },
  { id: 'legendary', name: '레전더리', color: '#ff9800' },
];
export interface EggDef { id: string; name: string; model: string; rarity: string; weight: number; hatchSec: number; pets: { id: string; w: number }[] }
export interface PetDef { id: string; name: string; model: string; rarity: string; income: number; scale: number }
export const PETS: PetDef[] = [
  { id: 'moss_fox', name: '이끼 여우', model: 'pets/moss_fox.glb', rarity: 'common', income: 1, scale: 0.6 },
  { id: 'aqua_slime', name: '아쿠아 슬라임', model: 'pets/aqua_slime.glb', rarity: 'rare', income: 5, scale: 0.6 },
  { id: 'ember_drake', name: '엠버 드레이크', model: 'pets/ember_drake.glb', rarity: 'epic', income: 25, scale: 0.5 },
];
export const EGGS: EggDef[] = [
  { id: 'forest_egg', name: '숲의 알', model: 'eggs/forest_egg.glb', rarity: 'common', weight: 1, hatchSec: 10, pets: [{ id: 'moss_fox', w: 80 }, { id: 'aqua_slime', w: 18 }, { id: 'ember_drake', w: 2 }] },
  { id: 'lake_egg', name: '호수의 알', model: 'eggs/lake_egg.glb', rarity: 'rare', weight: 3, hatchSec: 20, pets: [{ id: 'moss_fox', w: 30 }, { id: 'aqua_slime', w: 60 }, { id: 'ember_drake', w: 10 }] },
  { id: 'volcano_egg', name: '화산의 알', model: 'eggs/volcano_egg.glb', rarity: 'epic', weight: 6, hatchSec: 30, pets: [{ id: 'aqua_slime', w: 30 }, { id: 'ember_drake', w: 70 }] },
];
export const TREADMILLS = [
  { name: '기본 러닝머신', cost: 0, gain: 1 }, { name: '강화 러닝머신', cost: 500, gain: 5 }, { name: '코어 러닝머신', cost: 5000, gain: 25 },
];
