import pg from 'pg';
import type { Save } from '../../src/engine/logic';
import type { Store } from './profiles';
/** Postgres(Neon 등) 저장소. 쓰기는 큐에 모았다가 flush에서 UPSERT(요청 수·CU 절약). */
export class PgStore implements Store {
  private pool: pg.Pool; private pending = new Map<string, Save>(); ready: Promise<void>;
  constructor(url: string) {
    this.pool = new pg.Pool({ connectionString: url, max: 4, ssl: /localhost|127\.0\.0\.1/.test(url) ? undefined : { rejectUnauthorized: true } });
    this.ready = this.pool.query('CREATE TABLE IF NOT EXISTS profiles (key text PRIMARY KEY, data jsonb NOT NULL, updated_at timestamptz NOT NULL DEFAULT now())').then(() => {});
  }
  async load(k: string) { await this.ready; const p = this.pending.get(k); if (p) return structuredClone(p); const r = await this.pool.query('SELECT data FROM profiles WHERE key=$1', [k]); return r.rows[0]?.data as Save | undefined; }
  set(k: string, v: Save) { this.pending.set(k, structuredClone(v)); }
  async flush() {
    await this.ready; if (!this.pending.size) return; const batch = [...this.pending]; this.pending.clear();
    try { for (const [k, v] of batch) await this.pool.query('INSERT INTO profiles(key,data) VALUES($1,$2) ON CONFLICT (key) DO UPDATE SET data=EXCLUDED.data, updated_at=now()', [k, JSON.stringify(v)]); }
    catch (e) { for (const [k, v] of batch) if (!this.pending.has(k)) this.pending.set(k, v); console.error('pg flush failed, will retry', (e as Error).message); }
  }
  async end() { await this.flush(); await this.pool.end(); }
}
