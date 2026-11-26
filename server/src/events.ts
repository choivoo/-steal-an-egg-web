/** 글로벌 이벤트: 수동 이벤트(관리자) + 시간표 이벤트(시각으로부터 계산 → 재시작해도 자동 복원). 내부 UTC. */
export type EventKind = 'treadmill' | 'income' | 'hatch_speed' | 'cosmic_eclipse';
export interface GEvent { id: string; kind: EventKind; mult: number; start: number; end: number; source: 'admin' | 'schedule'; title: string }
export type Preset = 'ORIGINAL' | 'CLASSIC_CUSTOM';
const KST = 9 * 3600_000;
export function scheduled(now: number, preset: Preset): GEvent[] {
  if (preset !== 'CLASSIC_CUSTOM') return [];
  const out: GEvent[] = [];
  const dayStartKst = Math.floor((now + KST) / 86400_000) * 86400_000 - KST; // 오늘 00:00 KST (UTC ms)
  const s = dayStartKst + 15 * 3600_000, e = dayStartKst + 17 * 3600_000;
  if (now >= s && now < e) out.push({ id: 'sched-admin-' + s, kind: 'treadmill', mult: 8, start: s, end: e, source: 'schedule', title: '어드민 이벤트: 러닝머신 8배' });
  const half = Math.floor(now / 1800_000) * 1800_000; // 매시 정각·30분, 3분간
  if (now < half + 180_000) out.push({ id: 'sched-eclipse-' + half, kind: 'cosmic_eclipse', mult: 1, start: half, end: half + 180_000, source: 'schedule', title: '코스믹 이클립스' });
  return out;
}
export class GlobalEvents {
  manual: GEvent[] = []; private seq = 0;
  constructor(public preset: Preset = 'ORIGINAL') {}
  active(now: number): GEvent[] { this.manual = this.manual.filter(e => e.end > now); return [...this.manual.filter(e => e.start <= now), ...scheduled(now, this.preset)]; }
  mult(kind: EventKind, now: number): number { return this.active(now).filter(e => e.kind === kind).reduce((m, e) => Math.max(m, e.mult), 1); } // 중첩 곱셈 대신 최대값(배율 중복 적용 방지)
  start(kind: EventKind, mult: number, minutes: number, now: number, title?: string): GEvent {
    const e: GEvent = { id: 'ev' + now.toString(36) + (++this.seq), kind, mult, start: now, end: now + minutes * 60_000, source: 'admin', title: title ?? `${kind} ${mult}x` };
    this.manual.push(e); return e;
  }
  stop(id: string): boolean { const n = this.manual.length; this.manual = this.manual.filter(e => e.id !== id); return this.manual.length < n; }
  load(v: { manual?: GEvent[]; preset?: Preset } | undefined) { if (v?.manual) this.manual = v.manual; if (v?.preset) this.preset = v.preset; }
  dump() { return { manual: this.manual, preset: this.preset }; }
}
