import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { EGGS, PETS, TREADMILLS, RARITIES, ENVIRONMENT, GUARDIANS, PLAYERS } from './data/defs';
import { NESTS, GUARDS, SAFE_LINE, LANE_HALF, BIOME_LEN, biomeZ0, biomeAt, clampToWorld, LANE_END } from './data/worldConsts';
import { BIOMES } from './data/defs';
import { Net } from './net/client';
import { fmt, worldSpeed, carrySpeed, newSave, addEgg, hatchReady, tickIncome, buyTreadmill, incomePerSec, Save } from './engine/logic';

const $ = (id: string) => document.getElementById(id)!;
const SAVE_KEY = 'sae_save_v1';
let save: Save = (() => { try { const s = JSON.parse(localStorage.getItem(SAVE_KEY) || ''); if (s && s.v === 1) return s; } catch {} return newSave(Date.now()); })();
const offline = tickIncome(save, Date.now());
const wasHatched = hatchReady(save, Date.now());

const renderer = new THREE.WebGLRenderer({ canvas: $('c') as HTMLCanvasElement, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.shadowMap.enabled = true;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x8ecae6); scene.fog = new THREE.Fog(0x8ecae6, 60, 160);
const cam = new THREE.PerspectiveCamera(60, 1, 0.1, 300);
scene.add(new THREE.HemisphereLight(0xffffff, 0x446644, 1.1));
const sun = new THREE.DirectionalLight(0xffffff, 2); sun.position.set(30, 50, 20); sun.castShadow = true;
sun.shadow.camera.left = -40; sun.shadow.camera.right = 40; sun.shadow.camera.top = 40; sun.shadow.camera.bottom = -40; scene.add(sun);

// ===== 기지 광장 + 13개 지역 직선 레인 (원작 참고 영상 구조) =====
const plaza = new THREE.Mesh(new THREE.BoxGeometry(70, 1, 50), new THREE.MeshStandardMaterial({ color: 0x6cc45a })); plaza.position.set(0, -0.5, 8); plaza.receiveShadow = true; scene.add(plaza);
const sea = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.MeshStandardMaterial({ color: 0x3fa7e0 })); sea.rotation.x = -Math.PI / 2; sea.position.y = -6; scene.add(sea);
const safeStrip = new THREE.Mesh(new THREE.BoxGeometry(LANE_HALF * 2, 0.08, 0.8), new THREE.MeshBasicMaterial({ color: 0x66ffcc })); safeStrip.position.set(0, 0.05, SAFE_LINE); scene.add(safeStrip);
const bridge = new THREE.Mesh(new THREE.BoxGeometry(LANE_HALF * 2, 1, 6), new THREE.MeshStandardMaterial({ color: 0xbfae8a })); bridge.position.set(0, -0.5, SAFE_LINE - 3); scene.add(bridge);
const darker = (hex: string, k: number) => new THREE.Color(hex).multiplyScalar(k);
function signTexture(text: string, sub: string) {
  const c = document.createElement('canvas'); c.width = 512; c.height = 160; const x = c.getContext('2d')!;
  x.fillStyle = '#000a'; x.fillRect(0, 0, 512, 160); x.fillStyle = '#fff'; x.font = 'bold 64px sans-serif'; x.textAlign = 'center'; x.fillText(text, 256, 78); x.font = 'bold 34px sans-serif'; x.fillStyle = '#ffd54f'; x.fillText(sub, 256, 130);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
BIOMES.forEach((b, i) => {
  const z0 = biomeZ0(i), zc = z0 - BIOME_LEN / 2;
  const floor = new THREE.Mesh(new THREE.BoxGeometry(LANE_HALF * 2, 1, BIOME_LEN), new THREE.MeshStandardMaterial({ color: new THREE.Color(b.ground) })); floor.position.set(0, -0.5, zc); floor.receiveShadow = true; scene.add(floor);
  for (const sx of [-1, 1]) { const w = new THREE.Mesh(new THREE.BoxGeometry(2.4, 5 + (i % 3), BIOME_LEN), new THREE.MeshStandardMaterial({ color: darker(b.ground, 0.62) })); w.position.set(sx * (LANE_HALF + 1.2), (5 + (i % 3)) / 2 - 0.5, zc); w.castShadow = true; w.receiveShadow = true; scene.add(w); }
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(9, 2.8), new THREE.MeshBasicMaterial({ map: signTexture(b.ko, `권장 속도 ${fmt(b.requiredSpeed)}`), transparent: true })); sign.position.set(0, 8.5, z0 - 0.5); scene.add(sign);
});
// 지역 스트리밍: 플레이어 주변(±1 지역)만 Blender 소품·수호자·알 모델 로드
const biomeProps: THREE.Group[] = BIOMES.map(() => { const g = new THREE.Group(); scene.add(g); return g; });
const biomeLoaded = BIOMES.map(() => false);
function loadBiome(i: number) {
  if (i < 0 || i >= BIOMES.length || biomeLoaded[i]) return; biomeLoaded[i] = true; const b = BIOMES[i]; const env = ENVIRONMENT.filter(e => e.biome === b.id); const grp = biomeProps[i]; const z0 = biomeZ0(i);
  const rnd = (k: number) => { const x = Math.sin(i * 97.1 + k * 13.7) * 43758.5; return x - Math.floor(x); };
  for (let k = 0; k < 16; k++) { const e = env[k % env.length]; const side = k % 2 ? 1 : -1; const g = new THREE.Group(); g.position.set(side * (LANE_HALF - 2.2 - rnd(k) * 2), 0, z0 - 4 - k * (BIOME_LEN - 8) / 16); g.rotation.y = rnd(k + 50) * 6.28; grp.add(g); void modelAbs(e.model, e.kind.includes('tree') ? 1.5 : 1.1).then(m => g.add(m)).catch(() => {}); }
  const portal = new THREE.Group(); portal.position.set(0, 0, z0 - 1); grp.add(portal); void modelAbs(`buildings/build_portal_${b.id}.glb`, 2.6).then(m => portal.add(m)).catch(() => {});
  const gd = guards[i]; if (!gd.loaded) { gd.loaded = true; void model(GUARDS[i].model, 5.5 + i * 0.15).then(m => gd.obj.add(m)); }
  wild.forEach(w => { if (w.biome === i && !w.loaded) { w.loaded = true; const d = EGGS.find(x => x.id === w.eggId)!; void model(d.model, 1.4 + d.weight * 0.08).then(m => w.obj.add(m)); } });
}
function unloadBiome(i: number) { if (!biomeLoaded[i]) return; biomeLoaded[i] = false; const grp = biomeProps[i]; while (grp.children.length) grp.remove(grp.children[0]); }
let curBiome = -2;
function stream() { const bi = biomeAt(player.position.z); if (bi === curBiome) return; curBiome = bi; for (let i = 0; i < BIOMES.length; i++) { if (Math.abs(i - bi) <= 1 || (bi === -1 && i === 0)) loadBiome(i); else if (Math.abs(i - bi) > 2) unloadBiome(i); } }
// 기지 러닝머신 위치(모델은 아래 로더 이후 배치)
const TM = new THREE.Vector3(8, 0, 6);
const belt = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.1, 0.1), new THREE.MeshStandardMaterial({ emissive: 0x2288ff })); belt.visible = false; // 훈련 연출 호환용(숨김)
const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder); const cache = new Map<string, Promise<THREE.Object3D>>();
const BASE = import.meta.env.BASE_URL + 'assets/models/';
function model(path: string, h: number): Promise<THREE.Object3D> {
  if (!cache.has(path)) cache.set(path, loader.loadAsync(BASE + path).then(g => g.scene));
  return cache.get(path)!.then(o => { const c = o.clone(true); c.traverse(m => { (m as THREE.Mesh).castShadow = true; }); const b = new THREE.Box3().setFromObject(c); const s = h / (b.max.y - b.min.y || 1); c.scale.setScalar(s); const b2 = new THREE.Box3().setFromObject(c); c.position.y -= b2.min.y; const w = new THREE.Group(); w.add(c); return w; });
}
/** 실제 크기(블렌더 유닛 × s)로 배치 — 환경·건축용 */
function modelAbs(path: string, s: number): Promise<THREE.Object3D> {
  if (!cache.has(path)) cache.set(path, loader.loadAsync(BASE + path).then(g => g.scene));
  return cache.get(path)!.then(o => { const c = o.clone(true); c.scale.setScalar(s); c.traverse(m => { (m as THREE.Mesh).castShadow = true; (m as THREE.Mesh).receiveShadow = true; }); return c; });
}
function place(path: string, x: number, z: number, s = 1, ry = 0) { const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = ry; scene.add(g); void modelAbs(path, s).then(m => g.add(m)).catch(() => {}); return g; }
// 기지 장식(공용 Blender 에셋)
for (const [k, x, z] of [['tree_oak', -26, -6], ['tree_oak', 26, -4], ['bush', -22, 18], ['flower', 20, 20], ['rock', 28, 14]] as [string, number, number][]) place(`environment/env_forest_${k}.glb`, x, z, 1.4);
place('environment/env_common_street_lamp.glb', -9, -10, 1.2); place('environment/env_common_street_lamp.glb', 9, -10, 1.2); place('environment/env_common_bench.glb', 14, 14, 1.3);
// 기지 건축(Blender 에셋)
place('buildings/build_safe_arch.glb', 0, SAFE_LINE + 0.2, 2.2); place('buildings/build_pet_pen.glb', -6, -4, 1.6); place('buildings/build_fountain.glb', 0, 2, 0.9);
for (let i = 0; i < 4; i++) place('buildings/build_hatch_pedestal.glb', -14 + i * 3.2, 8, 1.1);
place('buildings/build_index_kiosk.glb', 10, -3, 1, -Math.PI / 2); place('buildings/build_shop_stall.glb', -10, 6, 1, Math.PI / 2);
// 러닝머신: 현재 단계 모델
let tmObj: THREE.Group | null = null, tmTier = -1;
function syncTreadmill() { if (save.treadmill === tmTier) return; tmTier = save.treadmill; if (tmObj) scene.remove(tmObj); tmObj = place(TREADMILLS[tmTier].model, TM.x, TM.z, 1.7, Math.PI); }
// player (Blender 캐릭터)
const player = new THREE.Group(); const pb = new THREE.Group(); pb.position.y = 0.95; player.add(pb);
model(PLAYERS[0].model, 2.1).then(m => { m.position.y = -0.95; m.rotation.y = 0; pb.add(m); });
player.position.set(0, 0, 4); scene.add(player);
let carried: { eggId: string; src: number; obj: THREE.Object3D } | null = null;

// 수호자(지역별 13) — 오프라인 FSM, 온라인은 서버 스냅샷
type GState = 'SLEEP' | 'WAKE_UP' | 'CHASE' | 'ATTACK' | 'RECOVER' | 'RETURN_HOME';
interface Guard { obj: THREE.Group; state: GState; t: number; home: THREE.Vector3; speed: number; loaded: boolean; sx: number; sz: number }
const guards: Guard[] = GUARDS.map(g => { const obj = new THREE.Group(); obj.position.set(g.home.x, 0, g.home.z); scene.add(obj); return { obj, state: 'SLEEP', t: 0, home: new THREE.Vector3(g.home.x, 0, g.home.z), speed: g.speed, loaded: false, sx: g.home.x, sz: g.home.z }; });
let chaser: Guard | null = null;
// 둥지 알(39)
interface Wild { eggId: string; biome: number; pos: THREE.Vector3; obj: THREE.Group; taken: boolean; loaded: boolean }
const wild: Wild[] = NESTS.map(n => { const g = new THREE.Group(); const p = new THREE.Vector3(n.x, 0, n.z); g.position.copy(p); scene.add(g); return { eggId: n.eggId, biome: n.biome, pos: p, obj: g, taken: false, loaded: false }; });
// pets at base
const petObjs = new Map<string, THREE.Object3D>();
function syncPets() {
  save.pets.forEach((p, i) => { if (petObjs.has(p.uid)) return; const d = PETS.find(x => x.id === p.petId)!; const g = new THREE.Group(); const a = i * 0.9; g.position.set(-6 + Math.cos(a) * (3 + Math.floor(i / 7) * 2.5), 0, -4 + Math.sin(a) * (3 + Math.floor(i / 7) * 2.5)); g.userData.ph = Math.random() * 6; scene.add(g); petObjs.set(p.uid, g); model(d.model, d.scale * 1.8).then(m => g.add(m)); });
}
const slotObjs = new Map<string, THREE.Group>();
function syncEggs() {
  save.eggs.forEach((e, i) => { if (slotObjs.has(e.uid)) return; const g = new THREE.Group(); g.position.set(-14 + i * 3.2, 0, 8); scene.add(g); slotObjs.set(e.uid, g); const d = EGGS.find(x => x.id === e.eggId)!; model(d.model, 1.5).then(m => g.add(m)); });
  for (const [uid, g] of slotObjs) if (!save.eggs.find(e => e.uid === uid)) { scene.remove(g); slotObjs.delete(uid); }
}

// input
const keys: Record<string, boolean> = {}; let joy = { x: 0, y: 0 };
addEventListener('keydown', e => { keys[e.code] = true; if (e.code === 'KeyE') interact(); if (e.code === 'KeyU') shopBuy(); });
addEventListener('keyup', e => keys[e.code] = false); addEventListener('blur', () => { for (const k in keys) keys[k] = false; joy = { x: 0, y: 0 }; });
const joyEl = $('joy'), knob = $('knob'); let joyId = -1; let camYaw = 0, camPitch = 0.45, camDist = 11; let camId = -1, lastX = 0, lastY = 0;
joyEl.addEventListener('pointerdown', e => { joyId = e.pointerId; joyEl.setPointerCapture(e.pointerId); mv(e); });
joyEl.addEventListener('pointermove', e => { if (e.pointerId === joyId) mv(e); });
const joyEnd = (e: PointerEvent) => { if (e.pointerId === joyId) { joyId = -1; joy = { x: 0, y: 0 }; knob.style.transform = ''; } };
joyEl.addEventListener('pointerup', joyEnd); joyEl.addEventListener('pointercancel', joyEnd);
function mv(e: PointerEvent) { const r = joyEl.getBoundingClientRect(); let dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2); const l = Math.hypot(dx, dy), m = 55; if (l > m) { dx = dx / l * m; dy = dy / l * m; } joy = { x: dx / m, y: dy / m }; knob.style.transform = `translate(${dx}px,${dy}px)`; }
const cv = $('c'); cv.addEventListener('pointerdown', e => { camId = e.pointerId; lastX = e.clientX; lastY = e.clientY; AudioCtx(); });
cv.addEventListener('pointermove', e => { if (e.pointerId !== camId) return; camYaw -= (e.clientX - lastX) * 0.006; camPitch = Math.min(1.2, Math.max(0.1, camPitch + (e.clientY - lastY) * 0.005)); lastX = e.clientX; lastY = e.clientY; });
cv.addEventListener('pointerup', () => camId = -1); cv.addEventListener('wheel', e => { camDist = Math.min(20, Math.max(5, camDist + e.deltaY * 0.01)); });
$('act').addEventListener('pointerdown', e => { e.stopPropagation(); interact(); }); $('shop').addEventListener('pointerdown', e => { e.stopPropagation(); shopBuy(); });
// audio
let ac: AudioContext | null = null; function AudioCtx() { if (!ac) try { ac = new AudioContext(); } catch {} }
function beep(f: number, d = 0.15, t: OscillatorType = 'sine') { if (!ac) return; const o = ac.createOscillator(), g = ac.createGain(); o.type = t; o.frequency.value = f; g.gain.value = 0.08; o.connect(g); g.connect(ac.destination); o.start(); g.gain.exponentialRampToValueAtTime(0.0001, ac.currentTime + d); o.stop(ac.currentTime + d); }
let msgT = 0; function say(s: string, t = 2.5) { $('msg').textContent = s; msgT = t; }

// state
const online = () => !!net && net.status === 'online';
let training = false; let chased = false; const dist2 = (a: THREE.Vector3, b: THREE.Vector3) => Math.hypot(a.x - b.x, a.z - b.z);
function nearWild(): Wild | null { for (const w of wild) if (!w.taken && dist2(player.position, w.pos) < 3.5) return w; return null; }
function interact() {
  AudioCtx();
  if (training) { training = false; if (online()) net!.send({ t: 'train', on: false }); say('훈련 종료'); return; }
  if (dist2(player.position, TM) < 3.5 && !carried) { training = true; player.position.set(TM.x, 0.4, TM.z); say('훈련 시작! (이동하면 종료)'); beep(440); if (online()) net!.send({ t: 'train', on: true }); return; }
  const w = nearWild();
  if (w && !carried && online()) { net!.send({ t: 'steal', i: wild.indexOf(w) }); return; }
  if (w && !carried && save.eggs.length < save.slots) {
    const d = EGGS.find(e => e.id === w.eggId)!; w.taken = true; const idx = wild.indexOf(w);
    scene.remove(w.obj); const o = new THREE.Group(); carried = { eggId: w.eggId, src: idx, obj: o }; scene.add(o); model(d.model, 1.2).then(m => o.add(m));
    chased = true; chaser = guards[w.biome]; chaser.state = chaser.state === 'SLEEP' ? 'WAKE_UP' : 'CHASE'; chaser.t = 0; beep(120, 0.4, 'sawtooth'); say(`${d.name} 훔침! 안전구역으로 도망!`);
  } else if (w && save.eggs.length >= save.slots) say('부화 슬롯이 가득 찼습니다');
}
function shopBuy() { if (online()) { net!.send({ t: 'buy' }); return; } const n = TREADMILLS[save.treadmill + 1]; if (!n) return say('최고 단계'); if (buyTreadmill(save)) { say(`${n.name} 구매!`); beep(660); persist(); } else say(`돈 부족: ${fmt(n.cost)} 필요`); }
function endChase(success: boolean) {
  chased = false; if (chaser) chaser.state = 'RETURN_HOME'; chaser = null; $('chase').style.display = 'none';
  if (!carried) return; const c = carried; carried = null; scene.remove(c.obj);
  if (success) { addEgg(save, c.eggId, Date.now()); syncEggs(); say('귀환 성공! 알이 부화 슬롯에 놓였습니다'); beep(880, 0.3); persist(); }
  else { const w = wild[c.src]; w.taken = false; scene.add(w.obj); say('잡혔다! 알을 잃었습니다'); beep(90, 0.5, 'square'); player.position.set(0, 0, 4); }
}
function persist() { if (online()) return; save.last = Date.now(); try { localStorage.setItem(SAVE_KEY, JSON.stringify(save)); } catch {} }
setInterval(persist, 5000); document.addEventListener('visibilitychange', () => { if (document.hidden) persist(); });

// online (서버 없으면 오프라인 모드로 표시)
const qs = new URLSearchParams(location.search);
const SERVER = (qs.get('server') || (import.meta.env.VITE_SERVER_URL as string | undefined) || 'https://steal-an-egg-server.onrender.com').replace(/\/$/, '');
const WS = qs.get('ws') || SERVER.replace(/^http/, 'ws');
let net: Net | null = null;
let events: { id: string; kind: string; mult: number; end: number; title: string }[] = [];
let role = 'PLAYER';
let profileReady = false;
const remotes = new Map<string, { o: THREE.Group; tx: number; tz: number; ry: number }>();
function bindNet(net: Net) {
  net.onPos = (id, x, z, ry) => { let r = remotes.get(id); if (!r) { const o = new THREE.Group(); const b = new THREE.Mesh(new THREE.CapsuleGeometry(0.45, 0.9, 4, 12), new THREE.MeshStandardMaterial({ color: 0x66aaff })); b.position.y = 0.95; o.add(b); o.position.set(x, 0, z); scene.add(o); r = { o, tx: x, tz: z, ry }; remotes.set(id, r); } r.tx = x; r.tz = z; r.ry = ry; };
  net.onLeft = id => { const r = remotes.get(id); if (r) { scene.remove(r.o); remotes.delete(id); } };
  net.onError = e => say(e === 'FULL' ? '해당 서버가 가득 찼습니다. 빈자리가 생긴 후 다시 시도해 주세요.' : e === 'NOT_FOUND' ? '존재하지 않거나 종료된 서버입니다.' : '올바른 서버 코드를 입력해 주세요.', 5);
  net.onMsg = m => {
    if (m.t === 'snap') { (m.g as number[][]).forEach((a, i) => { const gd = guards[i]; if (gd) { gd.sx = a[0]; gd.sz = a[1]; gd.state = a[2] === 0 ? 'SLEEP' : a[2] === 2 ? 'RETURN_HOME' : 'CHASE'; } }); m.eggs.forEach((st: number, i: number) => { const w = wild[i]; if (!w) return; const take = st !== 0; if (take && !w.taken) { w.taken = true; scene.remove(w.obj); } else if (!take && w.taken && !(carried && carried.src === i)) { w.taken = false; scene.add(w.obj); } }); }
    else if (m.t === 'steal_ok') { const d = EGGS.find(e => e.id === m.eggId)!; const o = new THREE.Group(); carried = { eggId: m.eggId, src: m.i, obj: o }; wild[m.i].taken = true; scene.remove(wild[m.i].obj); scene.add(o); model(d.model, 1.2).then(x => o.add(x)); beep(120, 0.4, 'sawtooth'); say(`${d.name} 훔침! 안전구역으로 도망!`); }
    else if (m.t === 'steal_fail') say(m.reason === 'SLOTS_FULL' ? '부화 슬롯이 가득 찼습니다' : m.reason === 'TAKEN' ? '다른 플레이어가 먼저 가져갔습니다' : m.reason === 'ALREADY_CARRYING' ? '이미 알을 들고 있습니다' : '알에 더 가까이 가세요');
    else if (m.t === 'returned') { if (carried) { scene.remove(carried.obj); carried = null; } say('귀환 성공! 알이 부화 슬롯에 놓였습니다'); beep(880, 0.3); }
    else if (m.t === 'profile') { const had = save.pets.length; Object.assign(save, m.p); syncEggs(); syncPets(); if (save.pets.length > had && had >= 0 && profileReady) { const p = save.pets[save.pets.length - 1]; const d = PETS.find(x => x.id === p.petId)!; say(`🐣 ${d.name} 부화! (${RARITIES.find(r => r.id === d.rarity)!.name})`, 4); beep(990, 0.4); } profileReady = true; }
    else if (m.t === 'buy_result') { say(m.ok ? '러닝머신 구매!' : '돈이 부족합니다', 2); if (m.ok) beep(660); }
    else if (m.t === 'hello_ok') { role = m.role ?? 'PLAYER'; $('adminBtn').style.display = role !== 'PLAYER' ? 'block' : 'none'; if (m.offline > 1) say(`오프라인 수익 +${fmt(m.offline)}`, 4); }
    else if (m.t === 'kicked') say(m.reason ? '관리자에 의해 연결이 종료되었습니다' : '다른 곳에서 접속하여 연결이 종료되었습니다', 8);
    else if (m.t === 'events') events = m.list;
    else if (m.t === 'announce') { const b = $('banner'); b.textContent = m.text; b.style.display = 'block'; setTimeout(() => b.style.display = 'none', 10000); beep(700, 0.3); }
    else if (m.t === 'admin_result') { $('adminOut').textContent = (m.ok ? '✅ ' : '❌ ') + m.msg + (m.data ? '\n' + JSON.stringify(m.data, null, 1) : ''); }
    else if (m.t === 'caught') { if (carried) { scene.remove(carried.obj); carried = null; } say('잡혔다! 알을 잃었습니다'); beep(90, 0.5, 'square'); player.position.set(0, 0, 4); }
  };
  setInterval(() => net.sendPos(player.position.x, player.position.z, player.rotation.y), 100);
}
function connect(code?: string) { if (net) return; net = new Net(WS, code); bindNet(net); }
// loop
const clock = new THREE.Clock(); const v = new THREE.Vector3(); let lastHatchCheck = 0;
function resize() { const w = innerWidth, h = innerHeight; renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); } addEventListener('resize', resize); resize();
function frame() {
  const dt = Math.min(clock.getDelta(), 0.1); const now = Date.now(); const t = clock.elapsedTime;
  let ix = (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0) + joy.x, iz = (keys.KeyS ? 1 : 0) - (keys.KeyW ? 1 : 0) + joy.y;
  const il = Math.hypot(ix, iz); const moving = il > 0.1;
  if (training && moving) { training = false; if (online()) net!.send({ t: 'train', on: false }); }
  const base = worldSpeed(save.train); const spd = carried ? carrySpeed(base, EGGS.find(e => e.id === carried!.eggId)!.weight) : base;
  if (training) { if (!online()) save.train += TREADMILLS[save.treadmill].gain * dt; player.rotation.y = Math.PI; pb.position.y = 0.95 + Math.abs(Math.sin(t * 12)) * 0.15; belt.material.emissiveIntensity = 1 + Math.sin(t * 20) * 0.5; }
  else if (moving) {
    const l = Math.min(il, 1); ix /= il; iz /= il; const c = Math.cos(camYaw), s = Math.sin(camYaw);
    const wx = ix * c + iz * s, wz = -ix * s + iz * c; player.position.x += wx * spd * l * dt; player.position.z += wz * spd * l * dt;
    player.rotation.y = Math.atan2(wx, wz); pb.position.y = 0.95 + Math.abs(Math.sin(t * 14)) * 0.12;
  } else pb.position.y = 0.95;
  { const [cx, cz] = clampToWorld(player.position.x, player.position.z); player.position.x = cx; player.position.z = cz; }
  const inSafe = player.position.z > SAFE_LINE; stream();
  if (carried) { carried.obj.position.set(player.position.x, 2.4, player.position.z); carried.obj.rotation.y += dt * 2; if (inSafe && !online()) endChase(true); }
  // 수호자: 온라인=서버 위치 보간, 오프라인=로컬 FSM(추격 중인 1마리)
  for (const gd of guards) {
    const gp = gd.obj.position;
    if (online()) { const dx = gd.sx - gp.x, dz = gd.sz - gp.z; gp.x += dx * Math.min(1, dt * 10); gp.z += dz * Math.min(1, dt * 10); if (Math.hypot(dx, dz) > 0.05) gd.obj.rotation.y = Math.atan2(dx, dz); continue; }
    if (gd.state === 'SLEEP') { gd.obj.scale.y = 1 + Math.sin(t * 1.5) * 0.015; continue; }
    if (gd.state === 'WAKE_UP') { gd.t += dt; gd.obj.scale.y = 1 + Math.sin(gd.t * 8) * 0.06; if (gd.t > 1) { gd.state = 'CHASE'; gd.t = 0; gd.obj.scale.y = 1; } }
    else if (gd.state === 'CHASE') {
      if (!chased || !carried || chaser !== gd) gd.state = 'RETURN_HOME'; else {
        v.set(player.position.x - gp.x, 0, player.position.z - gp.z); const d = v.length(); v.normalize(); gp.addScaledVector(v, gd.speed * dt); gd.obj.rotation.y = Math.atan2(v.x, v.z);
        gp.z = Math.min(gp.z, SAFE_LINE - 2); gp.x = Math.max(-LANE_HALF + 1, Math.min(LANE_HALF - 1, gp.x)); // 안전구역·벽 통과 불가
        if (d < 3) { gd.state = 'ATTACK'; gd.t = 0; }
      }
    } else if (gd.state === 'ATTACK') { gd.t += dt; gp.y = Math.sin(Math.min(gd.t * 3, 1) * Math.PI) * 0.8; if (gd.t > 0.5 && carried && dist2(gp, player.position) < 4.5) { gp.y = 0; endChase(false); gd.state = 'RECOVER'; gd.t = 0; } else if (gd.t > 0.7) { gd.state = carried ? 'CHASE' : 'RECOVER'; gd.t = 0; gp.y = 0; } }
    else if (gd.state === 'RECOVER') { gd.t += dt; gp.y = 0; if (gd.t > 1.5) gd.state = 'RETURN_HOME'; }
    else if (gd.state === 'RETURN_HOME') { v.set(gd.home.x - gp.x, 0, gd.home.z - gp.z); const d = v.length(); if (d < 0.5) gd.state = 'SLEEP'; else { v.normalize(); gp.addScaledVector(v, Math.min(d, 9 * dt)); gd.obj.rotation.y = Math.atan2(v.x, v.z); } }
  }
  if (online()) chased = !!carried; $('chase').style.display = chased ? 'block' : 'none';
  // hatching + income
  if (now - lastHatchCheck > 500 && !online()) { lastHatchCheck = now; const g = tickIncome(save, now); const h = hatchReady(save, now); if (h.length) { syncEggs(); syncPets(); h.forEach(p => { const d = PETS.find(x => x.id === p.petId)!; say(`🐣 ${d.name} 부화! (${RARITIES.find(r => r.id === d.rarity)!.name})`, 4); beep(990, 0.4); }); persist(); } void g; }
  for (const [, o] of petObjs) o.position.y = Math.abs(Math.sin(t * 2 + o.userData.ph)) * 0.2;
  for (const e of save.eggs) { const o = slotObjs.get(e.uid); if (o) { const total = EGGS.find(x => x.id === e.eggId)!.hatchSec * 1000; const pr = 1 - Math.max(0, e.hatchAt - now) / total; o.rotation.z = pr > 0.8 ? Math.sin(t * 25) * 0.15 * pr : 0; o.scale.setScalar(0.8 + pr * 0.4); } }
  for (const w of wild) w.obj.rotation.y += dt * 0.5;
  // camera
  const tgt = new THREE.Vector3(player.position.x, 1.8, player.position.z); cam.position.set(tgt.x + Math.sin(camYaw) * Math.cos(camPitch) * camDist, tgt.y + Math.sin(camPitch) * camDist, tgt.z + Math.cos(camYaw) * Math.cos(camPitch) * camDist); cam.lookAt(tgt);
  // HUD
  $('money').textContent = `💰 ${fmt(save.money)}`; $('spd').textContent = `👟 ${fmt(save.train)} (속도 ${spd.toFixed(1)})`; $('inc').textContent = `🐾 +${fmt(incomePerSec(save))}/s`;
  void LANE_END; const nxt = TREADMILLS[save.treadmill + 1]; $('shop').textContent = nxt ? `${nxt.name.slice(0, 2)}\n${fmt(nxt.cost)}` : 'MAX';
  { const bi = biomeAt(player.position.z); const b = BIOMES[bi]; $('zone').textContent = inSafe ? '🟢 기지(안전구역)' : bi < 0 ? '🌉 다리' : `${b.ko} · 권장 ${fmt(b.requiredSpeed)}${save.train < b.requiredSpeed ? ' ⚠️' : ''}`;
    const sky = new THREE.Color(bi < 0 ? '#9fd3ff' : b.sky); (scene.background as THREE.Color).lerp(sky, Math.min(1, dt * 2)); (scene.fog as THREE.Fog).color.copy(scene.background as THREE.Color); }
  $('list').innerHTML = save.eggs.map(e => { const d = EGGS.find(x => x.id === e.eggId)!; const s = Math.max(0, Math.ceil((e.hatchAt - now) / 1000)); return `🥚 ${d.name} — ${s}s`; }).join('<br>') + `<br>펫 ${save.pets.length}마리 · 슬롯 ${save.eggs.length}/${save.slots}`;
  const canAct = training || (dist2(player.position, TM) < 3.5 && !carried) || !!nearWild(); ($('act') as HTMLElement).style.display = canAct ? 'block' : 'none';
  if (msgT > 0) { msgT -= dt; if (msgT <= 0) $('msg').textContent = ''; }
  for (const r of remotes.values()) { r.o.position.x += (r.tx - r.o.position.x) * Math.min(1, dt * 12); r.o.position.z += (r.tz - r.o.position.z) * Math.min(1, dt * 12); r.o.rotation.y = r.ry; }
  $('evt').textContent = events.map(e => `⚡ ${e.title} ${new Date(Math.max(0, e.end - now)).toISOString().slice(11, 19)}`).join('  '); $('evt').style.display = events.length ? 'inline-block' : 'none';
  $('net').textContent = !net ? '⚪ 오프라인 모드' : net.status === 'online' && net.info ? `🟢 서버 ${net.info.code} · ${net.info.players}/${net.info.max} · 접속 ${net.info.online}명 · 서버 ${net.info.servers}개` : net.status === 'connecting' ? '🟡 서버 연결 중…' : '🔴 서버 연결 실패(오프라인 모드)';
  renderer.render(scene, cam); requestAnimationFrame(frame);
}
syncEggs(); syncPets(); syncTreadmill(); setInterval(syncTreadmill, 500);
if (offline > 1) say(`오프라인 수익 +${fmt(offline)}${wasHatched.length ? `, 펫 ${wasHatched.length}마리 부화!` : ''}`, 4);
(window as any).__game = { remotes, get net() { return net; }, save: () => save, player, guards, get carried() { return carried; }, interact, wild };
// 로비
async function loadServers() {
  const box = $('servers'); box.textContent = '서버 목록 확인 중… (서버가 잠들어 있으면 깨어나는 데 최대 1분)';
  for (let i = 0; i < 6; i++) {
    try { const r = await fetch(SERVER + '/status', { cache: 'no-store' }); const st = await r.json();
      $('lobbyOnline').textContent = `● ONLINE ${st.online}명 · 공개 서버 ${st.servers}개`;
      const rooms = (st.rooms as any[]).filter(x => !($('hideFull') as HTMLInputElement).checked || x.players < x.max).sort((a, b) => b.players - a.players);
      box.innerHTML = rooms.length ? '' : '열린 서버 없음 — 자동 매칭하면 새 공개 서버가 생성됩니다';
      for (const x of rooms) { const row = document.createElement('div'); row.className = 'row'; row.textContent = `#${x.id} · ${x.code} · ${x.players}/${x.max} `; const b = document.createElement('button'); b.textContent = x.players >= x.max ? '가득 참' : '접속'; b.disabled = x.players >= x.max || x.state !== 'OPEN'; b.onclick = () => enter(x.code); row.appendChild(b); box.appendChild(row); }
      return; } catch { box.textContent = `서버 시작 중… (${i + 1}/6)`; await new Promise(r => setTimeout(r, 10000)); }
  }
  box.textContent = '서버에 연결할 수 없습니다. 오프라인으로 플레이할 수 있습니다.'; $('lobbyOnline').textContent = '● 서버 응답 없음';
}
function enter(code?: string) { AudioCtx(); $('lobby').style.display = 'none'; connect(code); }
$('btnMatch').onclick = () => enter();
$('btnCode').onclick = () => { const c = ($('codeIn') as HTMLInputElement).value.trim().toUpperCase(); if (!/^[A-Z0-9]{6}$/.test(c)) { $('lobbyMsg').textContent = '올바른 서버 코드를 입력해 주세요.'; return; } enter(c); };
$('btnOffline').onclick = () => { AudioCtx(); $('lobby').style.display = 'none'; };
$('btnRefresh').onclick = () => void loadServers(); ($('hideFull') as HTMLInputElement).onchange = () => void loadServers();
$('net').addEventListener('click', () => { if (net?.info) { void navigator.clipboard?.writeText(net.info.code).then(() => say('서버 코드 복사됨: ' + net!.info!.code)).catch(() => say('서버 코드: ' + net!.info!.code, 5)); } });
$('adminBtn').onclick = () => { const p = $('adminPanel'); p.style.display = p.style.display === 'block' ? 'none' : 'block'; };
$('adminRun').onclick = () => { const v = ($('adminIn') as HTMLInputElement).value; if (v && net) net.send({ t: 'admin', cmd: v }); };
if (qs.get('ws') || qs.get('code')) enter(qs.get('code') || undefined); else if (qs.get('offline') === '1') $('lobby').style.display = 'none'; else void loadServers();
frame();
