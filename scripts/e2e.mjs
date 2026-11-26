import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 844, height: 390 } }); const errs = [];
p.on('console', m => { if (m.type() === 'error') errs.push(m.text() + ' @ ' + (m.location()?.url ?? '')); }); p.on('response', r => { if (r.status() >= 400) errs.push(r.status() + ' ' + r.url()); }); p.on('pageerror', e => errs.push(String(e)));
await p.goto('http://localhost:4173/?offline=1'); await p.waitForTimeout(6000);
const g = () => p.evaluate(() => { const x = window.__game; return { money: x.save().money, train: x.save().train, eggs: x.save().eggs.length, pets: x.save().pets.length, carried: !!x.carried, gs: x.G.state }; });
console.log('start', await g());
await p.evaluate(() => { const x = window.__game; x.player.position.set(8, 0, 6); x.interact(); }); await p.waitForTimeout(3000);
console.log('train', await g());
await p.evaluate(() => { const x = window.__game; x.interact(); const w = x.wild[0]; x.player.position.set(w.pos.x, 0, w.pos.z + 2); x.interact(); });
console.log('stolen', await g());
await p.evaluate(() => { window.__game.player.position.set(0, 0, 10); }); await p.waitForTimeout(1500);
console.log('returned', await g());
await p.evaluate(() => { const s = window.__game.save(); s.eggs[0].hatchAt = Date.now() - 1; }); await p.waitForTimeout(1500);
console.log('hatched', await g()); await p.waitForTimeout(3000); console.log('income', await g());
// chase+caught
await p.evaluate(() => { const x = window.__game; const w = x.wild[1]; x.player.position.set(w.pos.x, 0, w.pos.z + 2); x.interact(); x.G.state = 'CHASE'; x.G.state; x.player.position.set(w.pos.x, 0, w.pos.z + 2); }); await p.waitForTimeout(9000);
console.log('after chase', await g());
await p.screenshot({ path: 'renders/game.png' }); console.log('errors', errs); await b.close();
