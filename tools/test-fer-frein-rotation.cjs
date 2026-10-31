// Freinage manuel : clavier et Rapier réels, pas de sauvegarde personnelle.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const http=require('node:http'),{once}=require('node:events');
const root=path.resolve(__dirname,'..');
const puppeteer=require(process.env.FER_PUPPETEER_MODULE||'puppeteer-core');
let html=fs.readFileSync(path.join(root,'fer-et-flamme.html'),'utf8');
html=html.replace('simuler(FIXED);',`
 const observation=window.__ferTest?.enregistrer ? {debut:__ferTest.etat()} : null;
 simuler(FIXED);
`);
html=html.replace('monde.step(fileEvenements);',`
 if(observation)observation.avant=__ferTest.etat();
 monde.step(fileEvenements);
 if(observation){observation.apres=__ferTest.etat();__ferTest.observations.push(observation);}
`);
html=html.replace('</script>',`
window.__ferTest={
 observations:[],enregistrer:false,
 step(s){for(let i=0;i<Math.round(s*60);i++)boucle((dernier+1/60)*1000);},
 elan(omega){vehicule.body.setAngvel(omega,true);}, // Fixture physique uniquement.
 reglage(pct){reglageCoupleManuel=pct;vehicule.coupleManuel=pct;majCoupleManuel();},
 etat(){const v=vehicule;return {...__fer.etat(),av:v.body.angvel(),inertie:v.body.principalInertia(),
  tau:v.thrusters.reduce((s,t)=>s+(t.rx*t.force.y-t.ry*t.force.x)*t.forceN*v.facteur,0),
  fy:v.thrusters.reduce((s,t)=>s+t.force.y*t.forceN*v.facteur,0),
  moteurs:v.thrusters.map(t=>({force:t.forceN,max:t.def.thrust,inverse:t.def.reverse||0,
   levier:t.rx*t.force.y-t.ry*t.force.x})),
  aide:document.getElementById('aide-deplacement').textContent,mode:ui.assist.textContent};}
};
</script>`);
const build=nom=>JSON.parse(fs.readFileSync(path.join(__dirname,nom),'utf8'));
const plans={actuel:build('fer-build-joueur-actuel.json'),precedent:build('fer-build-joueur.json'),
 // Les deux sens n'ont pas la même autorité (poussée inverse à 50 %).
 asymetrique:[['poste',2,1,0],['coeur',2,2,0],['moteur',1,1,1]]
  .map(([type,col,row,rot])=>({type,col,row,rot}))};
const near=(a,b,t,label)=>assert.ok(Math.abs(a-b)<=t,`${label}: ${a} != ${b}`);
function capacite(e,sens){return e.moteurs.reduce((s,m)=>s+Math.max(0,sens*m.levier*m.max,-sens*m.levier*m.max*m.inverse),0);}
async function main(){
 const out=path.join(root,'artifacts','fer-frein-rotation');fs.mkdirSync(out,{recursive:true});
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
  const ready=()=>page.waitForFunction('!!window.__ferTest',{timeout:15000,polling:100});
  await page.goto(`http://127.0.0.1:${server.address().port}/fer-et-flamme.html`);await ready();
  const step=s=>page.evaluate(s=>__ferTest.step(s),s),state=()=>page.evaluate(()=>__ferTest.etat());
  async function freiner(label,{omega,touche='q',reglage=100,poussee=false,stockVide=false}={}){
   await page.evaluate(({reglage,stockVide})=>{
    __fer.placer(-40,30);__ferTest.reglage(reglage);
    if(stockVide)__fer.energie(0);
   },{reglage,stockVide});
   if(poussee)await page.keyboard.down('z');
   if(omega===undefined){
    await page.keyboard.down(touche);await step(0.1);const tenue=await state();
    const sens=touche==='q'?1:-1;
    near(tenue.tau,sens*capacite(tenue,sens)*reglage/100*tenue.facteur,0.1,'couple tenu maximal choisi');
    await page.keyboard.up(touche);
   }else await page.evaluate(omega=>__ferTest.elan(omega),omega);
   const depart=await state();
   await page.evaluate(()=>{__ferTest.observations=[];__ferTest.enregistrer=true;});
   await step(0.7);
   const mesures=await page.evaluate(()=>{__ferTest.enregistrer=false;return __ferTest.observations;});
   const fini=await state();
   assert.ok(mesures.length>70,'observations de chaque pas physique');
   for(const {debut:d,avant:a,apres:b}of mesures){
    assert.ok(Math.abs(b.av)<=Math.abs(d.av)+0.00001,'vitesse angulaire décroissante');
    assert.ok(d.av*b.av>=0||Math.abs(b.av)<0.00001,`aucune relance dans le sens inverse (${d.av} → ${b.av})`);
    const sens=-Math.sign(d.av),max=capacite(a,sens);
    near(a.tau,sens*Math.min(max,d.inertie*Math.abs(d.av)*120)*a.facteur,0.1,'contre-couple physique maximal puis impulsion arrêt');
    assert.ok(a.demandePropulsion>=0&&a.puissanceUtilisee>=0,'énergie prise dans le budget commun');
   }
   assert.ok(Math.abs(fini.av)<0.00001,'arrêt de la rotation');
   await step(0.2);const stable=await state();near(stable.angle,fini.angle,0.0001,'angle atteint conservé');
   assert.ok(Math.abs(stable.angle)>0.001||Math.abs(depart.av)<0.01,'aucune remise à plat');
   assert.ok(fini.aide.includes('frein auto')&&fini.mode==='OFF','aide visible en mode manuel');
   if(poussee){assert.ok(fini.fy>1000,'Z reste actif une fois la rotation arrêtée');await page.keyboard.up('z');}
   if(stockVide)assert.ok(mesures.some(m=>m.avant.facteur<0.95),'freinage réellement limité par la puissance');
   resultats.push({label,depart,mesures,fini,stable});
  }
  for(const[nom,design]of Object.entries(plans)){
   await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design,coupleManuel:100})),design);
   for(let recharge=0;recharge<2;recharge++){
    await page.reload();await ready();assert.deepEqual(await page.evaluate(()=>__fer.design()),design);
    await page.evaluate(()=>__fer.lancer());await page.keyboard.press('r');
    await freiner(`${nom}-${recharge}-q`);await freiner(`${nom}-${recharge}-d`,{touche:'d'});
    console.log('OK frein :',nom,'recharge',recharge,'deux sens, couple maximal puis arrêt stable');
   }
  }
  // Reprendre le vrai build pour les commandes combinées et le réglage.
  await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design,coupleManuel:100})),plans.actuel);
  await page.reload();await ready();await page.evaluate(()=>__fer.lancer());await page.keyboard.press('r');
  await freiner('Z-maintenu',{poussee:true});
  await freiner('jauge-30',{reglage:30});await freiner('jauge-0',{reglage:0,omega:3});
  await freiner('stock-vide',{stockVide:true,omega:-3});
  for(const omega of [-0.0003,0.0003])await freiner('faible-vitesse-'+omega,{omega});
  // Une nouvelle commande interrompt immédiatement le frein automatique.
  await page.evaluate(()=>{__fer.placer(-40,30);__ferTest.elan(3);__ferTest.reglage(100);});
  await step(1/60);assert.ok((await state()).tau<0,'frein en cours');
  await page.keyboard.down('q');await step(1/60);const reprise=await state();
  near(reprise.tau,capacite(reprise,1)*reprise.facteur,0.1,'priorité immédiate à Q');await page.keyboard.up('q');
  // Capture de la phase de freinage : propulseurs, jauge et aide après recharge.
  await page.waitForFunction('!document.getElementById("chargement")',{timeout:3000,polling:50});
  await page.evaluate(()=>{__fer.placer(-40,20);__ferTest.reglage(100);__ferTest.elan(10);});
  await step(0.08);await page.screenshot({path:path.join(out,'frein-actuel-recharge.png')});
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'resultats.json'),JSON.stringify({resultats,reprise},null,2));
  console.log('OK frein : Z, jauges 30/0, puissance limitée, faibles vitesses, reprise immédiate, aide après recharge');
 }finally{if(browser)await browser.close();server.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
