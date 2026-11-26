export type NetStatus = 'offline' | 'connecting' | 'online';
export interface NetInfo { room: number; code: string; players: number; max: number; online: number; servers: number }
export class Net {
  status: NetStatus = 'connecting'; info: NetInfo | null = null; you = ''; private ws: WebSocket | null = null; private tries = 0;
  onPos: (id: string, x: number, z: number, ry: number) => void = () => {}; onLeft: (id: string) => void = () => {}; onMsg: (m: any) => void = () => {}; onError: (e: string) => void = () => {};
  private joined = false;
  static token(): string { const gen = () => { const a = new Uint8Array(24); crypto.getRandomValues(a); return [...a].map(x => x.toString(16).padStart(2, '0')).join(''); }; try { let t = localStorage.getItem('sae_token'); if (!t || !/^[0-9a-f]{32,64}$/.test(t)) { t = gen(); localStorage.setItem('sae_token', t); } return t; } catch { return gen(); } }
  constructor(private url: string, private code?: string) { this.connect(); }
  private connect() {
    this.status = 'connecting';
    let ws: WebSocket; try { ws = new WebSocket(this.url); } catch { this.status = 'offline'; return; }
    this.ws = ws;
    ws.onopen = () => { this.tries = 0; this.joined = false; ws.send(JSON.stringify({ t: 'hello', token: Net.token() })); };
    ws.onmessage = e => { let m: any; try { m = JSON.parse(e.data); } catch { return; }
      if (m.t === 'hello_ok') { if (!this.joined) { this.joined = true; ws.send(JSON.stringify(this.code ? { t: 'code', code: this.code } : { t: 'match' })); } this.onMsg(m); } else if (m.t === 'kicked') { this.status = 'offline'; this.tries = 99; this.onMsg(m); }
      else if (m.t === 'joined') { this.status = 'online'; this.you = m.you; this.info = m; } else if (m.t === 'pos') this.onPos(m.id, m.x, m.z, m.ry ?? 0);
      else if (m.t === 'count') { if (this.info) Object.assign(this.info, { players: m.players, online: m.online, servers: m.servers }); } else if (m.t === 'left') this.onLeft(m.id); else if (m.t === 'error') { this.status = 'offline'; this.onError(m.error); } else this.onMsg(m); };
    ws.onclose = () => { this.info = null; if (this.status === 'offline' && this.code) return; this.status = this.tries >= 5 ? 'offline' : 'connecting'; if (this.tries < 5) setTimeout(() => this.connect(), Math.min(8000, 500 * 2 ** this.tries++)); };
    ws.onerror = () => ws.close();
  }
  send(o: object) { if (this.status === 'online' && this.ws?.readyState === 1) this.ws.send(JSON.stringify(o)); }
  sendPos(x: number, z: number, ry: number) { if (this.status === 'online' && this.ws?.readyState === 1) this.ws.send(JSON.stringify({ t: 'pos', x: +x.toFixed(2), z: +z.toFixed(2), ry: +ry.toFixed(2) })); }
}
