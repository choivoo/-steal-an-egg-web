import { GlobalEvents, EventKind } from './events';
export type Role = 'OWNER' | 'SUPER_ADMIN' | 'ADMIN' | 'EVENT_MANAGER' | 'MODERATOR' | 'PLAYER';
const RANK: Record<Role, number> = { OWNER: 5, SUPER_ADMIN: 4, ADMIN: 3, EVENT_MANAGER: 2, MODERATOR: 1, PLAYER: 0 };
/** 역할은 서버 환경변수(ADMIN_ROLES="<sha256키>:OWNER,<키>:ADMIN")로만 부여. 클라이언트 값은 신뢰하지 않음. */
export function parseRoles(env: string | undefined): Map<string, Role> {
  const m = new Map<string, Role>(); for (const part of (env ?? '').split(',')) { const [k, r] = part.trim().split(':'); if (/^[0-9a-f]{64}$/.test(k ?? '') && r in RANK) m.set(k, r as Role); } return m;
}
export interface AdminCtx { role: Role; actor: string; now: number; events: GlobalEvents; announce: (msg: string, level: string) => void; status: () => object; kick: (pid: string, reason: string) => boolean; drain: (code: string) => boolean; audit: (e: object) => void }
export interface CmdResult { ok: boolean; msg: string; data?: unknown }
const need = (ctx: AdminCtx, r: Role) => RANK[ctx.role] >= RANK[r];
const KINDS: EventKind[] = ['treadmill', 'income', 'hatch_speed', 'cosmic_eclipse'];
/** 허용된 게임 명령만 해석(셸/SQL/JS 실행 없음). */
export function runCommand(line: string, ctx: AdminCtx): CmdResult {
  const res = exec(line.trim().slice(0, 300), ctx);
  ctx.audit({ at: new Date(ctx.now).toISOString(), actor: ctx.actor, role: ctx.role, cmd: line.slice(0, 120), ok: res.ok, result: res.msg });
  return res;
}
function exec(line: string, ctx: AdminCtx): CmdResult {
  if (ctx.role === 'PLAYER') return { ok: false, msg: '권한 없음' };
  const a = line.split(/\s+/); const c = a[0];
  if (c === '/server' && a[1] === 'status') return need(ctx, 'MODERATOR') ? { ok: true, msg: 'ok', data: ctx.status() } : { ok: false, msg: '권한 없음' };
  if (c === '/event' && a[1] === 'start') {
    if (!need(ctx, 'EVENT_MANAGER')) return { ok: false, msg: '권한 없음' };
    const kind = a[2] as EventKind, mult = parseFloat((a[3] ?? '').replace(/x$/i, '')), min = parseInt((a[4] ?? '').replace(/m$/i, ''), 10);
    if (!KINDS.includes(kind) || !(mult >= 1 && mult <= 100) || !(min >= 1 && min <= 7 * 24 * 60)) return { ok: false, msg: '형식: /event start <treadmill|income|hatch_speed|cosmic_eclipse> <배율 1~100>x <분>m global' };
    const e = ctx.events.start(kind, mult, min, ctx.now); ctx.announce(`[ADMIN EVENT] ${e.title} 시작! (${min}분)`, 'event'); return { ok: true, msg: `시작됨 ${e.id}`, data: e };
  }
  if (c === '/event' && a[1] === 'stop') { if (!need(ctx, 'EVENT_MANAGER')) return { ok: false, msg: '권한 없음' }; return ctx.events.stop(a[2] ?? '') ? (ctx.announce('[ADMIN EVENT] 이벤트가 종료되었습니다', 'event'), { ok: true, msg: '중단됨' }) : { ok: false, msg: '없는 이벤트 ID' }; }
  if (c === '/event' && a[1] === 'preset') { if (!need(ctx, 'ADMIN')) return { ok: false, msg: '권한 없음' }; if (a[2] !== 'ORIGINAL' && a[2] !== 'CLASSIC_CUSTOM') return { ok: false, msg: 'ORIGINAL | CLASSIC_CUSTOM' }; ctx.events.preset = a[2]; return { ok: true, msg: '프리셋 ' + a[2] }; }
  if (c === '/announce' && a[1] === 'global') { if (!need(ctx, 'MODERATOR')) return { ok: false, msg: '권한 없음' }; const msg = a.slice(2).join(' ').slice(0, 200); if (!msg) return { ok: false, msg: '메시지 필요' }; ctx.announce(msg, 'notice'); return { ok: true, msg: '공지 전송' }; }
  if (c === '/player' && a[1] === 'kick') { if (!need(ctx, 'MODERATOR')) return { ok: false, msg: '권한 없음' }; return ctx.kick(a[2] ?? '', a.slice(3).join(' ')) ? { ok: true, msg: '추방됨' } : { ok: false, msg: '플레이어 없음' }; }
  if (c === '/server' && a[1] === 'drain') { if (!need(ctx, 'ADMIN')) return { ok: false, msg: '권한 없음' }; return ctx.drain((a[2] ?? '').toUpperCase()) ? { ok: true, msg: '신규 입장 중지' } : { ok: false, msg: '서버 없음' }; }
  return { ok: false, msg: '알 수 없는 명령' };
}
