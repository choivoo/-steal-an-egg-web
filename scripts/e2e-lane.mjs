import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 844, height: 390 } }); const errs = [];
p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error' && !/favicon/.test(m.location()?.url ?? '')) errs.push(m.text() + ' @ ' + m.location()?.url); });
await p.goto('http://localhost:4173/?offline=1'); await p.waitForTimeout(5000);
const st = () => p.evaluate(() => { const g = window.__game; return { eggs: g.save().eggs.length, pets: g.save().pets.length, carried: !!g.carried, z: +g.player.position.z.toFixed(1), zone: document.getElementById('zone').textContent, chasing: g.guards.filter(x => x.state !== 'SLEEP').length }; });
// 숲 둥지에서 훔쳐 기지로 귀환
await p.evaluate(() => { const g = window.__game, w = g.wild[0]; g.player.position.set(w.pos.x, 0, w.pos.z + 1.5); }); await p.waitForTimeout(1500);
await p.evaluate(() => window.__game.interact()); await p.waitForTimeout(300); console.log('stolen', await st());
await p.evaluate(() => window.__game.player.position.set(0, 0, 0)); await p.waitForTimeout(800); console.log('returned', await st());
// 레인 끝까지 각 지역 스크린샷(스트리밍)
const shots = [0, 3, 5, 8, 10, 12];
for (const i of shots) { await p.evaluate(i => { const g = window.__game; g.player.position.set(0, 0, -20 - i * 70 - 12); }, i); await p.waitForTimeout(3500); await p.screenshot({ path: `renders/lane_${i}.png` }); console.log('biome', i, (await st()).zone); }
// 화산 지역에서 훔치고 정지 → 그 지역 수호자에게 잡힘
await p.evaluate(() => { const g = window.__game, w = g.wild[15]; g.player.position.set(w.pos.x, 0, w.pos.z + 1.5); }); await p.waitForTimeout(2500);
await p.evaluate(() => window.__game.interact()); await p.waitForTimeout(400); console.log('volcano stolen', await st()); await p.waitForTimeout(9000); console.log('after chase', await st());
console.log('errors', errs); await b.close();
