// Pleines capacités assistées, vrai Rapier et clavier, après sauvegarde/recharge.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const http=require('node:http'),{once}=require('node:events');
const root=path.resolve(__dirname,'..'),puppeteer=require(process.env.FER_PUPPETEER_MODULE||'puppeteer-core');
let html=fs.readFileSync(process.env.FER_HTML||path.join(root,'fer-et-flamme.html'),'utf8');
html=html.replace('simuler(FIXED);',`
 const debut=window.__ferTest?.enregistrer?__ferTest.etat():null;
 simuler(FIXED);
 if(debut)__ferTest.trace.push({debut,apres:__ferTest.etat()});
`);
html=html.replace('</script>',`
window.__ferTest={
 isoler(){detruireRival();detruireEnnemis();detruireTirsEnnemis();detruireProjectiles();tourelles=[];MISSION.etat='inactive';},
 trace:[],enregistrer:false,
 step(s){for(let i=0;i<Math.round(s*60);i++)boucle((dernier+1/60)*1000);},
 etat(){const v=vehicule;return {...__fer.etat(),av:v.body.angvel(),inertie:v.body.principalInertia(),
  fy:v.thrusters.reduce((s,t)=>s+t.force.y*t.forceN*v.facteur,0),
  tau:v.thrusters.reduce((s,t)=>s+(t.rx*t.force.y-t.ry*t.force.x)*t.forceN*v.facteur,0),
  moteurs:v.thrusters.map(t=>({force:t.forceN,max:t.def.thrust,inverse:t.def.reverse||0,sens:t.force})),
  hud:{mode:ui.assist.textContent,alt:ui.alt.textContent,vx:ui.vx.textContent,angle:ui.angle.textContent}};}
};
</script>`);
const build=nom=>JSON.parse(fs.readFileSync(path.join(__dirname,nom),'utf8'));
const compact=[['moteur',1,0],['chassis',2,0],['moteur',3,0],['coeur',1,1],['poste',2,1],['coeur',3,1]]
 .map(([type,col,row])=>({type,col,row,rot:0}));
const plans={actuel:build('fer-build-joueur-actuel.json'),precedent:build('fer-build-joueur.json'),compact};
const near=(a,b,t,label)=>assert.ok(Math.abs(a-b)<=t,`${label}: ${a} != ${b}`);
function sain(e){
 assert.ok(!e.hs&&!e.sol&&e.assist,'vol assisté intact');
 for(const m of e.moteurs)assert.ok(m.force>=-m.max*m.inverse-0.01&&m.force<=m.max+0.01,'bornes physiques');
}
async function main(){
 const out=path.join(root,'artifacts','fer-debridage');fs.mkdirSync(out,{recursive:true});
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);});
 server.listen(0,'127.0.0.1');await once(server,'listening');let browser;const resultats=[];
 try{
  browser=await puppeteer.launch({executablePath:process.env.FER_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu']});
  const page=await browser.newPage();await page.setViewport({width:1440,height:900});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));await page.evaluateOnNewDocument(()=>{window.requestAnimationFrame=()=>0;});
  if(process.env.FER_RAPIER_MODULE){
   const body=fs.readFileSync(process.env.FER_RAPIER_MODULE,'utf8');await page.setRequestInterception(true);
   page.on('request',r=>r.url().includes('/rapier.mjs')?r.respond({status:200,contentType:'text/javascript',headers:{'Access-Control-Allow-Origin':'*'},body}):r.continue());
  }
  const ready=()=>page.waitForFunction('!!window.__ferTest',{timeout:15000,polling:100});
  await page.goto(`http://127.0.0.1:${server.address().port}/fer-et-flamme.html`);await ready();
  const step=s=>page.evaluate(s=>__ferTest.step(s),s),state=()=>page.evaluate(()=>__ferTest.etat());
  const reset=()=>page.evaluate(()=>__fer.placer(-60,22));
  for(const[nom,design]of Object.entries(plans)){
   if(process.env.FER_CASE&&!process.env.FER_CASE.split(',').includes(nom))continue;
   await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design})),design);
   for(let recharge=0;recharge<2;recharge++){
    await page.reload();await ready();assert.deepEqual(await page.evaluate(()=>__fer.design()),design);
    await page.evaluate(()=>{__fer.lancer();__ferTest.isoler();});await reset();await step(0.2);
    const verticales=[];
    for(const [touche,sens]of [['z',1],['s',-1]]){
     await reset();await page.keyboard.down(touche);await step(0.1);const e=await state();await page.keyboard.up(touche);sain(e);
     const max=e.moteurs.reduce((s,m)=>s+(Math.abs(m.sens.y)>0.6?m.max*(sens>0?1:m.inverse):0),0);
     near(e.fy,sens*max*e.facteur,0.1,'pleine poussée compatible avec assiette à plat');
     verticales.push(e);
    }
    // Grande erreur d'angle : couple puis freinage physiques, sans plafond fixe.
    const rotations=[];
    for(const angle of [-1.2,1.2,Math.PI]){
     await reset();await page.evaluate(angle=>{__fer.retourner(angle);__ferTest.trace=[];__ferTest.enregistrer=true;},angle);
     // Sans latéraux, le redressement est suivi du freinage de la dérive par
     // inclinaison : laisser le temps à cette boucle de translation de finir.
     await step(8);const fin=await state();sain(fin);
     const trace=await page.evaluate(()=>{__ferTest.enregistrer=false;return __ferTest.trace;});
     const omegaMax=Math.max(...trace.map(e=>Math.abs(e.apres.av)));
     const alphaMax=Math.max(...trace.map(e=>Math.abs((e.apres.av-e.debut.av)*120)));
     assert.ok(Math.abs(fin.angle)<0.04&&Math.abs(fin.av)<0.02,'assiette et rotation stabilisées : '+JSON.stringify(fin));
     assert.ok(trace.every(e=>!e.apres.hs&&!e.apres.sol),'redressement sans impact');
     await step(0.5);near((await state()).angle,fin.angle,0.005,'pas d’oscillation persistante');
     rotations.push({angle,omegaMax,alphaMax,fin,trace});
    }
    if(nom==='compact'){
     assert.ok(rotations.some(e=>e.omegaMax>2.6),'dépasse réellement ancien plafond 2,5 rad/s');
     assert.ok(rotations.some(e=>e.alphaMax>23),'dépasse réellement ancien plafond 22 rad/s²');
    }
    // Déplacement puis arrêt : poussée latérale et portance restent coordonnées.
    const deplacements=[];
    for(const touche of ['q','d']){
     await reset();await step(0.2);await page.keyboard.down(touche);await step(0.5);const a=await state();
     await step(0.5);const b=await state();await page.keyboard.up(touche);sain(a);sain(b);
     const sens=touche==='d'?1:-1;assert.ok(sens*b.vx>sens*a.vx+0.5,'accélération maintenue');
     assert.ok(Math.abs(b.y-22)<0.5,'portance conservée pendant accélération');
     await step(7);const fin=await state();sain(fin);
     assert.ok(Math.abs(fin.vx)<0.25&&Math.abs(fin.angle)<0.07&&Math.abs(fin.y-22)<0.5,'arrêt et altitude stables');
     near(parseFloat(fin.hud.alt),fin.y,0.1,'altitude affichée après recharge');deplacements.push({touche,a,b,fin});
    }
    await page.waitForFunction('!document.getElementById("chargement")',{timeout:3000,polling:50});
    await page.screenshot({path:path.join(out,`${nom}-${recharge}.png`)});
    resultats.push({nom,recharge,verticales,rotations,deplacements});
    const fichier=process.env.FER_CASE?`resultats-${process.env.FER_CASE}.json`:'resultats.json';
    fs.writeFileSync(path.join(out,fichier),JSON.stringify(resultats,null,2));
    console.log('OK capacités :',nom,recharge,JSON.stringify(rotations.map(e=>({angle:e.angle,omega:e.omegaMax,alpha:e.alphaMax}))));
   }
  }
  assert.deepEqual(errors,[]);
 }finally{if(browser)await browser.close();server.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
