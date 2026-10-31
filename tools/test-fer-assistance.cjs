// npm install --no-save puppeteer-core, puis node tools/test-fer-assistance.cjs
// Variables facultatives : FER_PUPPETEER_MODULE, FER_BROWSER, FER_RAPIER_MODULE.
// Navigateur de test isolé : aucune lecture du profil/sauvegarde du joueur.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const vm = require('node:vm');
const { once } = require('node:events');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'fer-et-flamme.html'), 'utf8');
const maths = html.slice(html.indexOf('const borneMin ='), html.indexOf('// Simule un appareil'));
const ctx = vm.createContext({ Math });
vm.runInContext(`const MARGE_PORTANCE=0.85; const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)); const lerp=(a,b,t)=>a+(b-a)*t;
${maths}; this.api={bornesGroupe,repartirGroupe,enveloppeGroupe,proportionRealisable};`, ctx);
const { bornesGroupe, repartirGroupe, enveloppeGroupe, proportionRealisable } = ctx.api;

// Oracle indépendant : sommets de la boîte de poussées coupée par un couple
// fixé (toutes les variables sauf une sur leurs bornes).
function oracle(g, tau) {
  const values = [];
  for (let libre = 0; libre < g.length; libre++) {
    const autres = g.map((_, i) => i).filter(i => i !== libre);
    for (let mask = 0; mask < 2 ** autres.length; mask++) {
      let force = 0, couple = 0;
      autres.forEach((i, bit) => {
        const f = (mask >> bit) & 1 ? g[i].max : g[i].min || 0;
        force += f; couple += g[i].rx * f;
      });
      const a = g[libre];
      if (Math.abs(a.rx) < 1e-9) {
        if (Math.abs(tau - couple) < 1e-6) values.push(force + (a.min || 0), force + a.max);
      } else {
        const f = (tau - couple) / a.rx;
        if (f >= (a.min || 0) - 1e-6 && f <= a.max + 1e-6) values.push(force + f);
      }
    }
  }
  return { possible: !!values.length, lo: Math.min(...values), hi: Math.max(...values) };
}
const near = (a, b, tol = 1e-5) => assert.ok(Math.abs(a - b) <= tol, `${a} != ${b}`);
let seed = 77;
const random = () => ((seed = (1664525 * seed + 1013904223) >>> 0) / 2 ** 32);
for (let cas = 0; cas < 80; cas++) {
  const g = Array.from({ length: 1 + cas % 5 }, () => ({
    rx: random() * 3 - 1.5, min: cas % 2 ? -3400 : 0, max: 1000 + random() * 5800
  }));
  const tau = cas % 4 ? (random() - 0.5) * 20000 : 0;
  const a = bornesGroupe(g, tau), b = oracle(g, tau);
  assert.equal(a.possible, b.possible);
  if (b.possible) { near(a.lo, b.lo); near(a.hi, b.hi); }
  const r = repartirGroupe(g, (random() - 0.35) * 20000, tau, 2500);
  g.forEach(t => assert.ok(t.forceN >= t.min - 1e-6 && t.forceN <= t.max + 1e-6));
  near(r.force, g.reduce((s, t) => s + t.forceN, 0));
  near(r.tau, g.reduce((s, t) => s + t.rx * t.forceN, 0));
  const delta = {force:(random()-0.5)*30000,tau:(random()-0.5)*30000};
  const portion = proportionRealisable(enveloppeGroupe(g),r,delta);
  assert.ok(portion>=0&&portion<=1);
  const atteint = oracle(g,r.tau+portion*delta.tau);
  const force = r.force+portion*delta.force;
  assert.ok(atteint.possible&&force>=atteint.lo-1e-4&&force<=atteint.hi+1e-4,'couple et force compensés réalisables');
  if(portion<0.9999){
    const suite = oracle(g,r.tau+(portion+0.0001)*delta.tau);
    const f = r.force+(portion+0.0001)*delta.force;
    assert.ok(!suite.possible||f<suite.lo-1e-5||f>suite.hi+1e-5,'projection maximale');
  }
}
const asym = [-0.1, 0.5, 1].map(rx => ({ rx, max: 6800 }));
near(bornesGroupe(asym, 0).hi, 8160);
near(repartirGroupe(asym, 6000, 0, 6000).force, 6000);
near(asym.reduce((s, t) => s + t.rx * t.forceN, 0), 0);
const inverse = [-0.5, 0.5].map(rx => ({ rx, min: -3400, max: 6800 }));
const redressement = repartirGroupe(inverse, -3000, -1000, 2500);
near(redressement.force, -3000); near(redressement.tau, -1000);
assert.notEqual(inverse[0].forceN, inverse[1].forceN);
const opposees = [-0.5,0.5].flatMap(rx => [{rx,min:0,max:6800},{rx,min:-6800,max:0}]);
repartirGroupe(opposees,5000,0,5000);
near(opposees.reduce((s,t)=>s+Math.abs(t.forceN),0),5000);
const troisVerticaux=[-0.5,0,0.5].map(rx=>({rx,max:6800}));
near(proportionRealisable(enveloppeGroupe(troisVerticaux),{force:6150,tau:0},{force:0,tau:-4918}),3075/4918);
console.log('OK enveloppe exacte : 80 groupes, oracle indépendant, asymétrie et inversion');
if (process.env.FER_MATH_ONLY) process.exit(0);

async function browserTests() {
  const puppeteer = require(process.env.FER_PUPPETEER_MODULE || 'puppeteer-core');
  const instrumente = html.replace('</script>', `
window.__ferTest = {
  step(s) { for(let i=0;i<Math.round(s*60);i++) boucle((dernier+1/60)*1000); },
  allocation() { return { com: vehicule.com, physique: vehicule.body.localCom(), av: vehicule.body.angvel(), inertie: vehicule.inertie }; }
};
</script>`);
  const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.end(instrumente);
  });
  server.listen(0, '127.0.0.1'); await once(server, 'listening');
  let browser;
  const out = path.join(root, 'artifacts', 'fer-assistance'); fs.mkdirSync(out, { recursive: true });
  try {
    browser = await puppeteer.launch({
      executablePath: process.env.FER_BROWSER || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
      headless: true, args: ['--disable-gpu']
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900 });
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    await page.evaluateOnNewDocument(() => { window.requestAnimationFrame = () => 0; });
    if (process.env.FER_RAPIER_MODULE) {
      const rapier = fs.readFileSync(process.env.FER_RAPIER_MODULE, 'utf8');
      await page.setRequestInterception(true);
      page.on('request', req => req.url().includes('/rapier.mjs')
        ? req.respond({ status: 200, contentType: 'text/javascript', headers: { 'Access-Control-Allow-Origin': '*' }, body: rapier })
        : req.continue());
    }
    const url = `http://127.0.0.1:${server.address().port}/fer-et-flamme.html`;
    const ready = async () => { await page.waitForFunction('!!window.__ferTest', { timeout: 15000, polling: 100 }); };
    await page.goto(url); await ready();
    const step = s => page.evaluate(s => __ferTest.step(s), s);
    const state = () => page.evaluate(() => __fer.etat());
    const samples = [];
    const plans = {
      symetrique: [ ['moteur',1,0], ['chassis',2,0], ['moteur',3,0], ['coeur',1,1], ['poste',2,1], ['coeur',3,1] ],
      asymetrique: [ ['moteur',0,0], ['moteur',1,0], ['moteur',2,0], ['coeur',0,1], ['poste',1,1], ['chassis',2,1], ['coeur',0,2] ],
      opposees: [ ['moteur',1,0], ['chassis',2,0], ['moteur',3,0], ['coeur',1,1], ['poste',2,1], ['coeur',3,1], ['moteur',1,2,2], ['chassis',2,2], ['moteur',3,2,2] ],
      laterales: [ ['moteur',1,0], ['chassis',2,0], ['moteur',3,0], ['coeur',1,1], ['poste',2,1], ['coeur',3,1], ['moteur',0,1,3], ['moteur',4,1,1] ],
      foudre: null
    };
    for (const [nom, tuples] of Object.entries(plans)) {
      if (process.env.FER_CASE && nom !== process.env.FER_CASE) continue;
      const design = tuples ? tuples.map(([type,col,row,rot=0]) => ({type,col,row,rot})) : null;
      if (design) {
        await page.evaluate(design => localStorage.setItem('fer-et-flamme.design.v2', JSON.stringify({design,selected:'poste',ghostRot:0})), design);
      } else {
        await page.evaluate(() => __fer.chargerPreset('foudre'));
      }
      await page.reload(); await ready();
      const saved = await page.evaluate(() => ({
        design: __fer.design(), bilan: document.getElementById('bilan').textContent
      }));
      if (design) assert.deepEqual(saved.design, design);
      assert.ok(saved.bilan.includes('Inclinaison max'));
      await page.evaluate(() => { __fer.lancer(); __fer.placer(-70, 15); });
      await step(4); let e = await state();
      assert.ok(e.assistOK && !e.sol && !e.hs, nom + ' en vol');
      assert.ok(Math.abs(e.angle) < 0.06 && Math.abs(e.vy) < 0.2 && Math.abs(e.y-15) < 0.5, nom + ' maintien : ' + JSON.stringify(e));
      if (nom === 'opposees') {
        assert.ok(Math.abs(e.forces[2]) < 2 && Math.abs(e.forces[3]) < 2, 'pas de contre-poussée au maintien');
        assert.ok(e.puissanceUtilisee < 110000, 'budget électrique du maintien');
      }
      await page.keyboard.down('d'); await step(1.25); const acceleration1 = await state();
      await step(1.25); const acceleration2 = await state(); await page.keyboard.up('d');
      if(process.env.FER_TRACE) console.log('acceleration',nom,JSON.stringify(acceleration2));
      assert.ok(acceleration1.vx > 0 && acceleration2.vx > acceleration1.vx + 0.5,
        nom + ' accélération maintenue : ' + JSON.stringify([acceleration1.vx,acceleration2.vx]));
      assert.ok(Math.abs(acceleration2.y-15) < 1, nom + ' altitude en accélération : ' + acceleration2.y);
      near(parseFloat(await page.$eval('#h-vx', e=>e.textContent)),acceleration2.vx,0.1);
      // Mesurer l'arrêt sur un appareil intact, avant de prolonger son
      // exposition aux ennemis de la piste ; une perte de bloc invalide l'essai.
      if(process.env.FER_TRACE){
        for(let i=0;i<20;i++){
          await step(0.25); const e=await state();
          console.log('freinage',i/4,JSON.stringify({x:e.x,y:e.y,vx:e.vx,vy:e.vy,angle:e.angle,sol:e.sol,blocs:e.nbBlocs,forces:e.forces}));
        }
      } else await step(5);
      const stopped = await state();
      assert.equal(stopped.nbBlocs,e.nbBlocs,nom+' véhicule intact pendant le contrôle de freinage');
      assert.ok(Math.abs(stopped.vx) < 0.25 && Math.abs(stopped.angle) < 0.07, nom + ' freinage : ' + JSON.stringify(stopped));
      await page.evaluate(() => { __fer.placer(-40, 38); __fer.retourner(Math.PI); });
      for(let i=0;i<16;i++) {
        await step(0.5);
        if (process.env.FER_TRACE) {
          const e=await state(); console.log('redressement', i/2, JSON.stringify({y:e.y,vy:e.vy,angle:e.angle,forces:e.forces,allocation:await page.evaluate(()=>__ferTest.allocation())}));
        }
      }
      const recovered = await state();
      assert.ok(Math.abs(recovered.angle) < 0.12 && !recovered.sol && !recovered.hs,
        nom + ' redressement : ' + JSON.stringify(recovered));
      // Le retour vers l'altitude visée peut encore être en cours à 8 s.
      await step(12); const settled = await state();
      assert.ok(!settled.sol && !settled.hs && Math.abs(settled.vy) < 0.5 && Math.abs(settled.y-38) < 1,
        nom + ' maintien après redressement : ' + JSON.stringify(settled));
      await page.screenshot({ path: path.join(out, nom + '.png') });
      samples.push({ nom, saved, hover:e, acceleration1, acceleration2, stopped, recovered, settled });
      // Le build reste le même après une nouvelle recharge et le même vol est reproductible.
      await page.reload(); await ready();
      assert.deepEqual(await page.evaluate(() => __fer.design()), saved.design);
      await page.evaluate(() => { __fer.lancer(); __fer.placer(-70,15); }); await step(4);
      const reloaded = await state();
      near(reloaded.y,e.y,0.05); near(reloaded.angle,e.angle,0.01);
      assert.equal(await page.$eval('#h-assist', e=>e.textContent), 'ON');
      await page.keyboard.down('d'); await step(2.5); const reloadedDrive = await state(); await page.keyboard.up('d');
      near(reloadedDrive.vx,acceleration2.vx,0.1);
      near(parseFloat(await page.$eval('#h-vx',e=>e.textContent)),reloadedDrive.vx,0.1);
      await step(5); const reloadedStop = await state();
      assert.ok(Math.abs(reloadedStop.vx) < 0.25 && Math.abs(reloadedStop.angle) < 0.07,
        nom + ' freinage après recharge : ' + JSON.stringify(reloadedStop));
      console.log('OK vol et recharge :', nom, JSON.stringify({hover:e.y, vx1:acceleration1.vx, vx2:acceleration2.vx, altitude:acceleration2.y, redresse:recovered.angle}));
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync(path.join(out,'resultats.json'), JSON.stringify(samples,null,2));
  } finally {
    if (browser) await browser.close();
    server.close();
  }
}
browserTests().catch(e => { console.error(e); process.exitCode = 1; });
