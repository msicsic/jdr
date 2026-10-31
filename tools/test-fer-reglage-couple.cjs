// Jauge de couple : clavier, physique, HUD et sauvegarde dans un profil isolé.
// Configuration FER_PUPPETEER_MODULE / FER_RAPIER_MODULE / FER_BROWSER habituelle.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const http=require('node:http'),{once}=require('node:events');
const root=path.resolve(__dirname,'..');
const puppeteer=require(process.env.FER_PUPPETEER_MODULE||'puppeteer-core');
const html=fs.readFileSync(path.join(root,'fer-et-flamme.html'),'utf8').replace('</script>',`
window.__ferTest={
 step(s){for(let i=0;i<Math.round(s*60);i++)boucle((dernier+1/60)*1000);},
 etat(){const v=vehicule;return {...__fer.etat(),av:v.body.angvel(),
  tau:v.thrusters.reduce((s,t)=>s+(t.rx*t.force.y-t.ry*t.force.x)*t.forceN*v.facteur,0),
  fy:v.thrusters.reduce((s,t)=>s+t.force.y*t.forceN*v.facteur,0),
  maximum:v.thrusters.reduce((s,t)=>{const k=t.rx*t.force.y-t.ry*t.force.x;
   return s+Math.max(0,k*t.def.thrust,-k*t.def.thrust*(t.def.reverse||0));},0),
  minimum:v.thrusters.reduce((s,t)=>{const k=t.rx*t.force.y-t.ry*t.force.x;
   return s+Math.min(0,k*t.def.thrust,-k*t.def.thrust*(t.def.reverse||0));},0),
  jauge:{texte:ui.coupleManuel.textContent,largeur:ui.jauges.coupleManuel.style.width,
   aria:ui.metreCoupleManuel.getAttribute('aria-valuenow')},
  sauvegarde:JSON.parse(localStorage.getItem(CLE))};}
};
</script>`);
const near=(a,b,tol,label)=>assert.ok(Math.abs(a-b)<=tol,label+': '+a+' != '+b);
async function main(){
 const out=path.join(root,'artifacts','fer-reglage-couple');fs.mkdirSync(out,{recursive:true});
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);});
 server.listen(0,'127.0.0.1');await once(server,'listening');let browser;
 const resultats=[];
 try{
  browser=await puppeteer.launch({executablePath:process.env.FER_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu']});
  const page=await browser.newPage();await page.setViewport({width:1440,height:900});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.evaluateOnNewDocument(()=>{window.requestAnimationFrame=()=>0;});
  if(process.env.FER_RAPIER_MODULE){
   const body=fs.readFileSync(process.env.FER_RAPIER_MODULE,'utf8');await page.setRequestInterception(true);
   page.on('request',r=>r.url().includes('/rapier.mjs')?r.respond({status:200,contentType:'text/javascript',headers:{'Access-Control-Allow-Origin':'*'},body}):r.continue());
  }
  const ready=async()=>{
   await page.waitForFunction('!!window.__ferTest',{timeout:15000,polling:100});
   await page.waitForFunction('!document.getElementById("chargement")',{timeout:3000,polling:50});
  };
  await page.goto(`http://127.0.0.1:${server.address().port}/fer-et-flamme.html`);await ready();
  const step=s=>page.evaluate(s=>__ferTest.step(s),s),state=()=>page.evaluate(()=>__ferTest.etat());
  const reset=()=>page.evaluate(()=>__fer.placer(-40,20));
  const jauge=async pct=>{
   const e=await state();assert.equal(e.coupleManuel,pct);assert.equal(e.jauge.texte,pct+' %');
   assert.equal(e.jauge.largeur,pct+'%');assert.equal(e.jauge.aria,String(pct));return e;
  };
  const rotation=async(touche,pct)=>{
   await reset();await page.keyboard.down(touche);await step(0.05);const e=await jauge(pct);await page.keyboard.up(touche);
   const attendu=(touche==='q'?e.maximum:e.minimum)*pct/100*e.facteur;
   near(e.tau,attendu,0.1,'couple choisi par le joueur');
   if(pct===0)assert.ok(e.forces.every(f=>f===0),'aucun couple à zéro');
   return e;
  };
  for(const[nom,fichier]of [['actuel','fer-build-joueur-actuel.json'],['precedent','fer-build-joueur.json']]){
   const design=JSON.parse(fs.readFileSync(path.join(__dirname,fichier),'utf8'));
   // Ancienne sauvegarde : absence du réglage doit donner 100 %.
   await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design,selected:'poste',ghostRot:0})),design);
   await page.reload();await ready();await page.evaluate(()=>{__fer.lancer();__fer.placer(-40,20);});await page.keyboard.press('r');
   await jauge(100);const niveaux=[];
   for(let pct=100;pct>=0;pct-=10){
    if(pct<100)await page.keyboard.press('ArrowDown');
    const g=await rotation('q',pct),d=await rotation('d',pct);niveaux.push({pct,gauche:g.tau,droite:d.tau});
    assert.equal((await state()).sauvegarde.coupleManuel,pct);
   }
   await page.keyboard.press('ArrowDown');await jauge(0);
   await reset();await page.keyboard.press('ArrowDown');await step(0.15);
   const flecheSansPoussee=await state();assert.ok(flecheSansPoussee.forces.every(f=>f===0),'flèche bas réservée au réglage');
   await page.keyboard.down('z');await step(0.15);const propulsionZero=await state();await page.keyboard.up('z');
   assert.ok(propulsionZero.fy>1000,'Z reste disponible à 0 % de couple');
   for(let pct=10;pct<=100;pct+=10){await page.keyboard.press('ArrowUp');await jauge(pct);}
   await page.keyboard.press('ArrowUp');await jauge(100);
   await reset();await page.keyboard.press('ArrowUp');await step(0.15);const sansPoussee=await state();
   assert.ok(sansPoussee.forces.every(f=>f===0),'flèche haut ne commande pas une propulsion');
   await page.keyboard.down('z');await step(0.15);const propulsionCent=await state();await page.keyboard.up('z');
   near(propulsionZero.fy,propulsionCent.fy,0.1,'réglage indépendant de la poussée');
   // Réglage en cours de rotation, sans devoir relâcher Q.
   await reset();await page.keyboard.down('q');await step(0.05);const plein=await state();
   for(let i=0;i<5;i++)await page.keyboard.press('ArrowDown');await step(0.1);const moitie=await jauge(50);await page.keyboard.up('q');
   near(moitie.tau,plein.tau/2,0.1,'réglage immédiat pendant la rotation');
   await page.screenshot({path:path.join(out,nom+'-50.png')});
   // Le réglage est manuel uniquement : les flèches ne changent pas l'altitude en ON.
   await reset();await page.keyboard.press('r');await step(0.2);const hover=await state();
   await page.keyboard.press('ArrowDown');await jauge(40);await step(0.3);const hoverApres=await state();
   near(hoverApres.y,hover.y,0.15,'réglage sans poussée verticale en assistance ON');
   assert.ok(Math.abs(hoverApres.angle)<0.02,'assiette assistée conservée');
   // Sauvegarde, changement de mode et remise en piste conservent le choix.
   await page.keyboard.press('r');await page.keyboard.press('x');await jauge(40);
   await page.reload();await ready();assert.deepEqual(await page.evaluate(()=>__fer.design()),design);
   await page.evaluate(()=>{__fer.lancer();__fer.placer(-40,20);});await jauge(40);await page.keyboard.press('r');
   const recharge=await rotation('q',40);near(recharge.tau,recharge.maximum*0.4*recharge.facteur,0.1,'couple après recharge');
   await page.setViewport({width:1024,height:640});
   await page.waitForFunction('document.querySelector("canvas").width === Math.round(innerWidth*Math.min(2,devicePixelRatio))',{polling:50});
   await step(0.15);
   const rect=await page.$eval('#jauge-couple-manuel',e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,droite:r.right,bas:r.bottom};});
   assert.ok(rect.x>=0&&rect.y>=0&&rect.droite<=1024&&rect.bas<=640,'jauge visible à petite résolution');
   const aide=await page.$eval('#aide-jeu',e=>{const r=e.getBoundingClientRect();return {x:r.x,droite:r.right,bas:r.bottom};});
   assert.ok(aide.x>=0&&aide.droite<=1024&&aide.bas<=640,'aide clavier dans la fenêtre');
   await page.screenshot({path:path.join(out,nom+'-recharge-1024.png')});await page.setViewport({width:1440,height:900});
   resultats.push({nom,niveaux,moitie,recharge,rect});
   console.log('OK jauge :',nom,'0 à 100 % par pas de 10, rotation immédiate, poussée indépendante, recharge');
  }
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'resultats.json'),JSON.stringify(resultats,null,2));
 }finally{if(browser)await browser.close();server.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
