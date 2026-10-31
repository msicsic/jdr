// Même environnement de test isolé que test-fer-assistance.cjs.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { once } = require('node:events');
const root = path.resolve(__dirname, '..');
const puppeteer = require(process.env.FER_PUPPETEER_MODULE || 'puppeteer-core');
const html = fs.readFileSync(path.join(root,'fer-et-flamme.html'),'utf8');
const instrumente = html.replace('</script>', `
let emissionsLaser = 0;
window.__ferTest = {
  step(s) { for(let i=0;i<Math.round(s*60);i++) {
    const avant = vehicule?.guns[0]?.charge;
    boucle((dernier+1/60)*1000);
    if (vehicule?.guns[0]?.charge < avant) emissionsLaser++;
  } },
  observation() { return {
    tir: souris.tir, orientation: souris.bouclier, dedans: souris.dedans,
    angle: vehicule?.bouclier.angle, obus: vehicule?.obus,
    charge: vehicule?.guns[0]?.charge, faisceaux: faisceaux.length,
    projectiles: listeProjectiles.length, emissionsLaser
  }; }
};
</script>`);
async function main() {
  const server = http.createServer((req,res) => {
    res.setHeader('Content-Type','text/html; charset=utf-8'); res.end(instrumente);
  });
  server.listen(0,'127.0.0.1'); await once(server,'listening');
  let browser;
  const out = path.join(root,'artifacts','fer-souris'); fs.mkdirSync(out,{recursive:true});
  const resultats = [];
  try {
    browser = await puppeteer.launch({ executablePath: process.env.FER_BROWSER || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless:true,args:['--disable-gpu'] });
    const page = await browser.newPage(); await page.setViewport({width:1440,height:900});
    const errors = []; page.on('pageerror',e=>errors.push(e.message));
    await page.evaluateOnNewDocument(() => { window.requestAnimationFrame = () => 0; });
    if (process.env.FER_RAPIER_MODULE) {
      const rapier = fs.readFileSync(process.env.FER_RAPIER_MODULE,'utf8');
      await page.setRequestInterception(true);
      page.on('request',req=>req.url().includes('/rapier.mjs')
        ? req.respond({status:200,contentType:'text/javascript',headers:{'Access-Control-Allow-Origin':'*'},body:rapier})
        : req.continue());
    }
    const url = `http://127.0.0.1:${server.address().port}/fer-et-flamme.html`;
    const ready = () => page.waitForFunction('!!window.__ferTest',{timeout:15000,polling:100});
    await page.goto(url); await ready();
    const step = s=>page.evaluate(s=>__ferTest.step(s),s);
    const state = ()=>page.evaluate(()=>__ferTest.observation());
    const expect = async (tir,orientation,label) => {
      const e = await state();
      assert.equal(e.tir,tir,label+' / tir'); assert.equal(e.orientation,orientation,label+' / orientation');
      return e;
    };
    for (const arme of ['canon','laser']) {
      const design = [ ['moteur',1,0], ['chassis',2,0], ['moteur',3,0],
        ['coeur',1,1], ['poste',2,1], ['bouclier',3,1],
        [arme==='canon'?'soute':'condensateur',1,2], [arme,2,2], ['coeur',3,2]
      ].map(([type,col,row])=>({type,col,row,rot:0}));
      await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design,selected:'poste',ghostRot:0})),design);
      for (let recharge=0;recharge<2;recharge++) {
        await page.reload(); await ready();
        assert.deepEqual(await page.evaluate(()=>__fer.design()),design);
        await page.evaluate(()=>{__fer.lancer();__fer.placer(-40,8);}); await step(0.2);
        for (const ordre of [['left','right'],['right','left']]) {
          await page.mouse.move(1000,220); await step(1);
          const avant = await state();
          await page.mouse.down({button:ordre[0]});
          await expect(ordre[0]==='left',ordre[0]==='right','premier bouton');
          await page.mouse.down({button:ordre[1]});
          await expect(true,true,'deux boutons maintenus');
          await page.mouse.move(1000,260); await step(0.05);
          const ensemble = await expect(true,true,'deux actions simultanées');
          assert.ok(Math.abs(ensemble.angle-avant.angle)>0.01,'orientation réelle du bouclier');
          if(arme==='canon') assert.ok(ensemble.obus<avant.obus,'obus consommé avec les deux boutons');
          else assert.ok(ensemble.charge<avant.charge && ensemble.faisceaux>0,'laser émis avec les deux boutons');
          const hud = await page.$eval('#h-bouclier-note',e=>e.textContent);
          assert.ok(hud.length>0,'bouclier affiché au HUD');
          await page.screenshot({path:path.join(out,`${arme}-${recharge}-${ordre[0]}.png`)});
          // Relâcher le premier bouton doit conserver le second.
          await page.mouse.up({button:ordre[0]});
          await expect(ordre[1]==='left',ordre[1]==='right','relâchement du premier');
          const partiel = await state(); await page.mouse.move(1080,320); await step(1);
          const suite = await state();
          if(ordre[1]==='left') {
            if(arme==='canon') assert.ok(suite.obus<partiel.obus,'tir maintenu après relâchement droit');
            else assert.ok(suite.emissionsLaser>partiel.emissionsLaser,'laser maintenu après relâchement droit');
            assert.equal(suite.angle,partiel.angle,'bouclier ne suit plus sans bouton droit');
          } else {
            assert.ok(Math.abs(suite.angle-partiel.angle)>0.01,'orientation maintenue après relâchement gauche');
            if(arme==='canon') assert.equal(suite.obus,partiel.obus,'tir arrêté sans bouton gauche');
            else {
              assert.equal(suite.emissionsLaser,partiel.emissionsLaser,'laser arrêté sans bouton gauche');
              assert.ok(suite.charge>=partiel.charge,'laser recharge sans bouton gauche');
            }
          }
          await page.mouse.up({button:ordre[1]}); await expect(false,false,'tous relâchés');
          // Répéter en relâchant cette fois le deuxième bouton d'abord.
          await page.mouse.down({button:ordre[0]}); await page.mouse.down({button:ordre[1]});
          await page.mouse.up({button:ordre[1]});
          await expect(ordre[0]==='left',ordre[0]==='right','relâchement du deuxième');
          await page.mouse.up({button:ordre[0]}); await expect(false,false,'fin séquence inverse');
          resultats.push({arme,recharge,ordre,ensemble,suite,hud});
        }
        // La sortie et la perte de focus annulent les commandes sans blocage.
        await page.mouse.down({button:'left'}); await page.mouse.down({button:'right'});
        await page.mouse.move(-10,100); await expect(false,false,'sortie du canvas');
        await page.mouse.up({button:'left'}); await page.mouse.up({button:'right'});
        await page.mouse.move(1000,220); await page.mouse.down({button:'left'}); await page.mouse.down({button:'right'});
        await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
        await expect(false,false,'perte de focus');
        await page.mouse.up({button:'left'}); await page.mouse.up({button:'right'});
        // Les changements de mode ne conservent aucune commande active.
        await page.mouse.down({button:'left'}); await page.mouse.down({button:'right'});
        await page.keyboard.press('Escape'); await expect(false,false,'retour atelier');
        await page.mouse.up({button:'left'}); await page.mouse.up({button:'right'});
        await page.evaluate(()=>__fer.lancer()); await expect(false,false,'nouveau lancement');
        console.log('OK souris :',arme,'recharge',recharge,'deux ordres et deux ordres de relâchement');
      }
    }
    assert.deepEqual(errors,[]);
    fs.writeFileSync(path.join(out,'resultats.json'),JSON.stringify(resultats,null,2));
  } finally {
    if(browser) await browser.close(); server.close();
  }
}
main().catch(e=>{console.error(e);process.exitCode=1;});
