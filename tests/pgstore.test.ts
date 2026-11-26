import { it, expect } from 'vitest';
import { PgStore } from '../server/src/pgstore';
import { Profiles, validToken } from '../server/src/profiles';
const URL = process.env.TEST_PG_URL;
it.skipIf(!URL)('Postgres: persist across store instances (simulated server restart)', async () => {
  const T = 'c'.repeat(31) + String(Date.now() % 10); expect(validToken(T)).toBe(true);
  const s1 = new PgStore(URL!); const p1 = new Profiles(s1); await p1.login('a', T, 0); p1.giveEgg('a', 'egg_forest_00', 0); await p1.logout('a'); await s1.end();
  const s2 = new PgStore(URL!); const p2 = new Profiles(s2); const r = await p2.login('b', T, 3600_000); expect(r.save.pets.length).toBe(1); await s2.end();
});
