import { createServer, IncomingMessage, ServerResponse } from 'node:http';
import { WebSocketServer, WebSocket } from 'ws';
import { World } from './world';
import { RoomManager, MAX_PLAYERS_PER_ROOM } from './rooms';
import { PgStore } from './pgstore';
import { Profiles, Store, MemoryStore, JsonFileStore, validToken, keyOf } from './profiles';
import { GlobalEvents, Preset } from './events';
import { parseRoles, runCommand, Role } from './admin';

export interface ServerOpts { roles?: string; preset?: Preset; origins?: string }
export function startServer(port: number, mgr = new RoomManager(), store: Store = new MemoryStore(), opts: ServerOpts = {}) {
  const roles = parseRoles(opts.roles); const origins = (opts.origins ?? '').split(',').map(s => s.trim()).filter(Boolean);
  const events = new GlobalEvents(opts.preset ?? 'ORIGINAL');
  const meta = store as unknown as { load(k: string): Promise<any>; set(k: string, v: any): void };
  void meta.load('meta:events').then(v => events.load(v)).catch(() => {});
  let audit: object[] = []; void meta.load('meta:audit').then(v => { if (Array.isArray(v?.list)) audit = v.list; }).catch(() => {});
  const saveMeta = () => { meta.set('meta:events', events.dump()); meta.set('meta:audit', { list: audit.slice(-500) }); };
  const startedAt = Date.now();
  const status = () => ({ ok: true, storage: store.constructor.name === 'PgStore' ? 'postgres' : store.constructor.name === 'JsonFileStore' ? 'file(임시 디스크)' : 'memory', online: mgr.online(), servers: mgr.rooms.size, maxPerServer: MAX_PLAYERS_PER_ROOM, uptimeSec: Math.round((Date.now() - startedAt) / 1000),
    rooms: mgr.list().filter(r => r.state !== 'CLOSED').map(r => ({ id: r.id, code: r.code, players: r.players, max: r.max, state: r.state })), events: events.active(Date.now()).map(e => ({ id: e.id, kind: e.kind, mult: e.mult, end: e.end, title: e.title })) });
  const http = createServer((req: IncomingMessage, res: ServerResponse) => {
    res.setHeader('Access-Control-Allow-Origin', origins.length ? (origins.includes(req.headers.origin ?? '') ? req.headers.origin! : origins[0]) : '*');
    res.setHeader('Content-Type', 'application/json; charset=utf-8'); res.setHeader('Cache-Control', 'no-store');
    if (req.url === '/' || req.url === '/health') { res.end(JSON.stringify({ ok: true })); return; }
    if (req.url === '/status') { res.end(JSON.stringify(status())); return; }
    res.statusCode = 404; res.end('{"ok":false}');
  });
  const wss = new WebSocketServer({ server: http, maxPayload: 4096, verifyClient: (info: { origin: string }) => !origins.length || origins.includes(info.origin) });
  http.listen(port);
  const profiles = new Profiles(store);
  const conns = new Map<string, WebSocket>(); let seq = 0; const worlds = new Map<number, World>(); const authed = new Map<string, Role>();
  const roomOf = (pid: string) => [...mgr.rooms.values()].find(r => r.players.has(pid));
  const worldOf = (pid: string) => { const r = roomOf(pid); if (!r) return undefined; let w = worlds.get(r.id); if (!w) { w = new World(); worlds.set(r.id, w); } return w; };
  const tx = (pid: string, msg: object) => conns.get(pid)?.send(JSON.stringify(msg));
  const all = (msg: object) => { const s = JSON.stringify(msg); for (const pid of authed.keys()) conns.get(pid)?.send(s); };
  const pushEvents = (pid?: string) => { const m = { t: 'events', list: status().events, now: Date.now() }; pid ? tx(pid, m) : all(m); };
  const pushProfile = (pid: string) => { const s = profiles.get(pid); if (s) tx(pid, { t: 'profile', p: { money: s.money, train: s.train, treadmill: s.treadmill, eggs: s.eggs, pets: s.pets, slots: s.slots, uid: s.uid } }); };
  const send = (evs: { to: string; msg: any }[]) => { for (const e of evs) { if (e.msg.t === 'returned') { const ok = profiles.giveEgg(e.to, e.msg.eggId, Date.now(), events.mult('hatch_speed', Date.now())); tx(e.to, { ...e.msg, stored: ok }); pushProfile(e.to); } else tx(e.to, e.msg); } };
  const broadcast = (pid: string, msg: object) => { const r = roomOf(pid); if (!r) return; for (const q of r.players) if (q !== pid) tx(q, msg); };
  const info = (pid: string) => { const r = roomOf(pid)!; return { t: 'joined', you: pid, room: r.id, code: r.code, players: r.players.size, max: MAX_PLAYERS_PER_ROOM, online: mgr.online(), servers: mgr.rooms.size }; };
  const announce = (r: { players: Set<string> } | undefined) => { if (!r) return; const m = { t: 'count', players: r.players.size, online: mgr.online(), servers: mgr.rooms.size }; for (const q of r.players) tx(q, m); };
  let n = 0; let lastEvSig = '';
  const loop = setInterval(() => {
    const now = Date.now(); n++; const mult = { train: events.mult('treadmill', now), income: events.mult('income', now) };
    for (const [id, w] of worlds) { const r = mgr.rooms.get(id); if (!r) { worlds.delete(id); continue; } send(w.tick(0.05, now));
      if (n % 2 === 0) { const m = JSON.stringify(w.snap()); for (const q of r.players) conns.get(q)?.send(m); }
      if (n % 10 === 0) for (const q of r.players) if (profiles.tick(q, now, w.pos.get(q), mult)) pushProfile(q); }
    if (n % 20 === 0) { const sig = events.active(now).map(e => e.id).join(); if (sig !== lastEvSig) { lastEvSig = sig; pushEvents(); } }
    if (n % 200 === 0) { mgr.expire(now); saveMeta(); void profiles.periodic().catch(() => {}); }
  }, 50);
  wss.on('connection', ws => {
    const pid = 'u' + ++seq; conns.set(pid, ws); let rate = 0; const iv = setInterval(() => rate = 0, 1000);
    ws.on('message', async raw => {
      if (++rate > 60) return; let m: any; try { m = JSON.parse(raw.toString()); } catch { return; }
      if (m.t === 'hello') {
        if (authed.has(pid) || !validToken(m.token)) return; const role = roles.get(keyOf(m.token)) ?? 'PLAYER'; authed.set(pid, role);
        let r; try { r = await profiles.login(pid, m.token, Date.now()); } catch { authed.delete(pid); tx(pid, { t: 'error', error: 'DB_UNAVAILABLE' }); return; }
        if (r.kick) { tx(r.kick, { t: 'kicked' }); conns.get(r.kick)?.close(); } tx(pid, { t: 'hello_ok', offline: r.offline, role }); pushProfile(pid); pushEvents(pid); return;
      }
      const role = authed.get(pid); if (!role) return;
      if (m.t === 'match') { mgr.autoMatch(pid); tx(pid, info(pid)); announce(roomOf(pid)); }
      else if (m.t === 'code') { const r = mgr.joinByCode(pid, String(m.code ?? '')); tx(pid, r.ok ? info(pid) : { t: 'error', error: r.error }); if (r.ok) announce(roomOf(pid)); }
      else if (m.t === 'pos' && Number.isFinite(m.x) && Number.isFinite(m.z) && Math.abs(m.x) < 500 && Math.abs(m.z) < 500) { const w = worldOf(pid); w?.report(pid, m.x, m.z, Date.now()); const pp = w?.pos.get(pid); broadcast(pid, { t: 'pos', id: pid, x: pp?.x ?? m.x, z: pp?.z ?? m.z, ry: Number(m.ry) || 0 }); }
      else if (m.t === 'steal' && Number.isInteger(m.i)) { const w = worldOf(pid); if (!w) return; if (!profiles.hasSlot(pid)) return tx(pid, { t: 'steal_fail', reason: 'SLOTS_FULL' }); send(w.steal(pid, m.i, Date.now())); }
      else if (m.t === 'train') { const ok = profiles.setTraining(pid, !!m.on, worldOf(pid)?.pos.get(pid)); tx(pid, { t: 'train_state', on: !!m.on && ok }); }
      else if (m.t === 'buy') { const ok = profiles.buy(pid); tx(pid, { t: 'buy_result', ok }); pushProfile(pid); }
      else if (m.t === 'admin' && typeof m.cmd === 'string') {
        const r = runCommand(m.cmd, { role, actor: keyOf(String(pid)).slice(0, 12) + '/' + pid, now: Date.now(), events, status,
          announce: (text, level) => all({ t: 'announce', text, level }), audit: e => audit.push(e),
          kick: (target, reason) => { const c = conns.get(target); if (!c) return false; tx(target, { t: 'kicked', reason }); c.close(); return true; }, drain: code => mgr.drain(code) });
        tx(pid, { t: 'admin_result', ...r }); if (r.ok) { pushEvents(); saveMeta(); }
      }
    });
    ws.on('close', () => { clearInterval(iv); authed.delete(pid); const rr = roomOf(pid); send(worldOf(pid)?.remove(pid, Date.now()) ?? []); broadcast(pid, { t: 'left', id: pid }); conns.delete(pid); mgr.leave(pid); announce(rr); void profiles.logout(pid).catch(() => {}); });
  });
  const shutdown = async () => { clearInterval(loop); saveMeta(); await profiles.periodic().catch(() => {}); for (const c of wss.clients) c.terminate(); await new Promise<void>(res => { wss.close(() => res()); }); await new Promise<void>(res => http.close(() => res())); };
  return { wss, http, mgr, profiles, events, close: shutdown };
}
if (process.argv[1]?.endsWith('index.ts') || process.argv[1]?.endsWith('index.js')) {
  const s = startServer(Number(process.env.PORT ?? 8080), new RoomManager(), process.env.DATABASE_URL ? new PgStore(process.env.DATABASE_URL) : new JsonFileStore(process.env.DATA_FILE ?? 'data/db.json'),
    { roles: process.env.ADMIN_ROLES, preset: (process.env.EVENT_PRESET as Preset) ?? 'ORIGINAL', origins: process.env.ALLOWED_ORIGINS });
  for (const sig of ['SIGTERM', 'SIGINT']) process.on(sig, () => { void s.close().finally(() => process.exit(0)); }); // 종료 신호 시 저장 후 종료
  console.log('listening', process.env.PORT ?? 8080);
}
