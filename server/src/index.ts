import { WebSocketServer, WebSocket } from 'ws';
import { World } from './world';
import { RoomManager, MAX_PLAYERS_PER_ROOM } from './rooms';
import { Profiles, Store, MemoryStore, JsonFileStore, validToken } from './profiles';
export function startServer(port: number, mgr = new RoomManager(), store: Store = new MemoryStore()) {
  const wss = new WebSocketServer({ port, maxPayload: 4096 });
  const profiles = new Profiles(store);
  const conns = new Map<string, WebSocket>(); let seq = 0; const worlds = new Map<number, World>(); const authed = new Set<string>();
  const roomOf = (pid: string) => [...mgr.rooms.values()].find(r => r.players.has(pid));
  const worldOf = (pid: string) => { const r = roomOf(pid); if (!r) return undefined; let w = worlds.get(r.id); if (!w) { w = new World(); worlds.set(r.id, w); } return w; };
  const tx = (pid: string, msg: object) => conns.get(pid)?.send(JSON.stringify(msg));
  const pushProfile = (pid: string) => { const s = profiles.get(pid); if (s) tx(pid, { t: 'profile', p: { money: s.money, train: s.train, treadmill: s.treadmill, eggs: s.eggs, pets: s.pets, slots: s.slots, uid: s.uid } }); };
  const send = (evs: { to: string; msg: any }[]) => { for (const e of evs) { if (e.msg.t === 'returned') { const ok = profiles.giveEgg(e.to, e.msg.eggId, Date.now()); tx(e.to, { ...e.msg, stored: ok }); pushProfile(e.to); } else tx(e.to, e.msg); } };
  const broadcast = (pid: string, msg: object) => { const r = roomOf(pid); if (!r) return; for (const q of r.players) if (q !== pid) tx(q, msg); };
  const info = (pid: string) => { const r = roomOf(pid)!; return { t: 'joined', you: pid, room: r.id, code: r.code, players: r.players.size, max: MAX_PLAYERS_PER_ROOM, online: mgr.online(), servers: mgr.rooms.size }; };
  const announce = (r: { players: Set<string> } | undefined) => { if (!r) return; const m = { t: 'count', players: r.players.size, online: mgr.online(), servers: mgr.rooms.size }; for (const q of r.players) tx(q, m); };
  let n = 0;
  const loop = setInterval(() => {
    const now = Date.now(); n++;
    for (const [id, w] of worlds) { const r = mgr.rooms.get(id); if (!r) { worlds.delete(id); continue; } send(w.tick(0.05, now));
      if (n % 2 === 0) { const m = JSON.stringify(w.snap()); for (const q of r.players) conns.get(q)?.send(m); }
      if (n % 10 === 0) for (const q of r.players) if (profiles.tick(q, now, w.pos.get(q))) pushProfile(q); }
    if (n % 200 === 0) { mgr.expire(now); profiles.periodic(); }
  }, 50);
  wss.on('connection', ws => {
    const pid = 'u' + ++seq; conns.set(pid, ws); let rate = 0; const iv = setInterval(() => rate = 0, 1000);
    ws.on('message', raw => {
      if (++rate > 60) return; let m: any; try { m = JSON.parse(raw.toString()); } catch { return; }
      if (m.t === 'hello') { if (authed.has(pid) || !validToken(m.token)) return; const r = profiles.login(pid, m.token, Date.now()); authed.add(pid);
        if (r.kick) { tx(r.kick, { t: 'kicked' }); conns.get(r.kick)?.close(); } tx(pid, { t: 'hello_ok', offline: r.offline }); pushProfile(pid); return; }
      if (!authed.has(pid)) return;
      if (m.t === 'match') { mgr.autoMatch(pid); tx(pid, info(pid)); announce(roomOf(pid)); }
      else if (m.t === 'code') { const r = mgr.joinByCode(pid, String(m.code ?? '')); tx(pid, r.ok ? info(pid) : { t: 'error', error: r.error }); if (r.ok) announce(roomOf(pid)); }
      else if (m.t === 'pos' && Number.isFinite(m.x) && Number.isFinite(m.z) && Math.abs(m.x) < 500 && Math.abs(m.z) < 500) { const w = worldOf(pid); w?.report(pid, m.x, m.z, Date.now()); const pp = w?.pos.get(pid); broadcast(pid, { t: 'pos', id: pid, x: pp?.x ?? m.x, z: pp?.z ?? m.z, ry: Number(m.ry) || 0 }); }
      else if (m.t === 'steal' && Number.isInteger(m.i)) { const w = worldOf(pid); if (!w) return; if (!profiles.hasSlot(pid)) return tx(pid, { t: 'steal_fail', reason: 'SLOTS_FULL' }); send(w.steal(pid, m.i, Date.now())); }
      else if (m.t === 'train') { const ok = profiles.setTraining(pid, !!m.on, worldOf(pid)?.pos.get(pid)); tx(pid, { t: 'train_state', on: !!m.on && ok }); }
      else if (m.t === 'buy') { const ok = profiles.buy(pid); tx(pid, { t: 'buy_result', ok }); pushProfile(pid); }
    });
    ws.on('close', () => { clearInterval(iv); authed.delete(pid); const rr = roomOf(pid); send(worldOf(pid)?.remove(pid, Date.now()) ?? []); broadcast(pid, { t: 'left', id: pid }); conns.delete(pid); mgr.leave(pid); announce(rr); profiles.logout(pid); });
  });
  return { wss, mgr, profiles, close: () => new Promise<void>(res => { clearInterval(loop); profiles.periodic(); for (const c of wss.clients) c.terminate(); wss.close(() => res()); }) };
}
if (process.argv[1]?.endsWith('index.ts') || process.argv[1]?.endsWith('index.js')) { startServer(Number(process.env.PORT ?? 8080), new RoomManager(), new JsonFileStore(process.env.DATA_FILE ?? 'data/db.json')); console.log('listening'); }
