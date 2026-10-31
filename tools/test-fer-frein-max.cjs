// Poussée latérale et arrêt avec Rapier réel, hors combat et hors murs.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const http=require('node:http'),{once}=require('node:events');
const root=path.resolve(__dirname,'..'),puppeteer=require(process.env.FER_PUPPETEER_MODULE||'puppeteer-core');
const source=fs.readFileSync(process.env.FER_HTML||path.join(root,'fer-et-flamme.html'),'utf8');
const html=source.replace('</script>',`
window.__ferTest={
 isoler(){detruireRival();detruireEnnemis();detruireTirsEnnemis();tourelles=[];MISSION.etat='inactive';
  monde.forEachRigidBody(b=>{const p=b.translation();if(b.isFixed()&&p.y===8&&(p.x===MONDE.bornes.min||p.x===MONDE.bornes.max))b.setTranslation({x:p.x<0?-10000:10000,y:8},true);});},
 step(s){const t=performance.now();for(let i=0;i<Math.round(s*60);i++)boucle((dernier+1/60)*1000);return performance.now()-t;},
 lancerVitesse(vx){vehicule.body.setLinvel({x:vx,y:0},true);vehicule.latVerrou=false;},
 etat(){const v=vehicule;return {...__fer.etat(),av:v.body.angvel(),
  fy:v.thrusters.reduce((s,t)=>s+t.force.y*t.forceN*v.facteur,0),
  effort:v.thrusters.reduce((s,t)=>s+Math.abs(t.forceN)*v.facteur,0)/v.thrusters.reduce((s,t)=>s+t.def.thrust,0),
  angleMax:v.thetaUtil,verrou:v.latVerrou,
  hud:{vx:ui.vx.textContent,alt:ui.alt.textContent,angle:ui.angle.textContent,mode:ui.assist.textContent}};}
};
</script>`);
const charger=n=>JSON.parse(fs.readFileSync(path.join(__dirname,n),'utf8'));
const plans={colonne:charger('fer-build-joueur-colonne.json'),compact:[['moteur',1,0],['chassis',2,0],['moteur',3,0],['coeur',1,1],['poste',2,1],['coeur',3,1]]
 .map(([type,col,row])=>({type,col,row,rot:0})),lateraux:charger('fer-build-joueur-actuel.json')};
async function main(){
 const out=path.join(root,'artifacts','fer-frein-max');fs.mkdirSync(out,{recursive:true});
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);});
 server.listen(0,'127.0.0.1');await once(server,'listening');let browser;const resultats=[];
 try{
  browser=await puppeteer.launch({executablePath:process.env.FER_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu']});
  const page=await browser.newPage();await page.setViewport({width:1440,height:900});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));await page.evaluateOnNewDocument(()=>{window.requestAnimationFrame=()=>0;});
  if(process.env.FER_RAPIER_MODULE){const body=fs.readFileSync(process.env.FER_RAPIER_MODULE,'utf8');await page.setRequestInterception(true);
   page.on('request',r=>r.url().includes('/rapier.mjs')?r.respond({status:200,contentType:'text/javascript',headers:{'Access-Control-Allow-Origin':'*'},body}):r.continue());}
  const ready=()=>page.waitForFunction('!!window.__ferTest',{timeout:15000,polling:100});
  await page.goto(`http://127.0.0.1:${server.address().port}/fer-et-flamme.html`);await ready();
  const step=s=>page.evaluate(s=>__ferTest.step(s),s),state=()=>page.evaluate(()=>__ferTest.etat());
  for(const[nom,design]of Object.entries(plans)){
   if(process.env.FER_CASE&&!process.env.FER_CASE.split(',').includes(nom))continue;
   await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design})),design);
   for(let recharge=0;recharge<(process.env.FER_DIAGNOSTIC?1:2);recharge++){
    await page.reload();await ready();assert.deepEqual(await page.evaluate(()=>__fer.design()),design);
    await page.evaluate(()=>{__fer.lancer();__ferTest.isoler();});
    if(process.env.FER_COMBINEES){
     for(const vertical of ['z','s'])for(const lateral of ['d','q']){
      await page.evaluate(()=>__fer.placer(0,200));await step(0.5);
      await page.keyboard.down(vertical);await page.keyboard.down(lateral);await step(2);
      const e=await state();await page.keyboard.up(vertical);await page.keyboard.up(lateral);
      assert.ok(!e.hs&&!e.sol&&e.nbBlocs===design.length,'vol combiné intact');
      assert.ok((lateral==='d'?1:-1)*e.vx>1,'direction horizontale combinée');
      assert.ok((vertical==='z'?1:-1)*e.vy>1,'direction verticale combinée');
      assert.equal(e.hud.mode,'ON');
      console.log(JSON.stringify({nom,recharge,commandes:vertical+lateral,vx:e.vx,vy:e.vy,angle:e.angle}));
     }
     continue;
    }
    for(const sens of [1,-1])for(const scenario of ['appui','vitesse40']){
     if(process.env.FER_SCENARIO&&process.env.FER_SCENARIO!==scenario)continue;
     if(process.env.FER_SENS&&Number(process.env.FER_SENS)!==sens)continue;
     await page.evaluate(()=>__fer.placer(0,24));await step(0.5);const trace=[];let cpu=0;
     if(process.env.FER_STOCK_VIDE)await page.evaluate(()=>__fer.energie(0));
     if(scenario==='appui'){
      await page.keyboard.down(sens>0?'d':'q');
      for(let i=0;i<40;i++){cpu+=await step(0.05);trace.push({phase:'appui',...await state()});}
      await page.screenshot({path:path.join(out,`${nom}-${recharge}-${sens}-poussee.png`)});
      await page.keyboard.up(sens>0?'d':'q');
     }else await page.evaluate(vx=>__ferTest.lancerVitesse(vx),40*sens);
     const depart=await state();let arret=null;
     for(let i=0;i<200;i++){
      cpu+=await step(0.05);const e={phase:'freinage',...await state()};trace.push(e);
      if(arret===null&&Math.abs(e.vx)<0.15)arret=(i+1)*0.05;
      if(arret!==null&&Math.abs(e.vx)<0.15&&Math.abs(e.angle)<0.02&&Math.abs(e.av)<0.05&&Math.abs(e.vy)<0.1&&Math.abs(e.y-24)<0.15)break;
     }
     const fin=await state(),pousse=trace.filter(e=>e.phase==='appui'),frein=trace.filter(e=>e.phase==='freinage');
     const bilan={nom,recharge,sens,scenario,arret,cpu,angleAppui:Math.max(0,...pousse.map(e=>Math.abs(e.angle)))*180/Math.PI,
      effortAppui:Math.max(0,...pousse.map(e=>e.effort)),angleFrein:Math.max(...frein.map(e=>Math.abs(e.angle)))*180/Math.PI,
      effortFrein:Math.max(...frein.map(e=>e.effort)),altMin:Math.min(...trace.map(e=>e.y)),altMax:Math.max(...trace.map(e=>e.y)),
      vitesseInverse:Math.min(...frein.map(e=>sens*e.vx)),fin:{vx:fin.vx,vy:fin.vy,angle:fin.angle,av:fin.av,y:fin.y}};
     resultats.push({bilan,depart,trace,fin});console.log(JSON.stringify(bilan));
     fs.writeFileSync(path.join(out,process.env.FER_RESULTAT||(process.env.FER_DIAGNOSTIC?'diagnostic.json':'resultats.json')),JSON.stringify(resultats,null,2));
     if(!process.env.FER_DIAGNOSTIC){
      assert.ok(trace.every(e=>!e.hs&&!e.sol&&e.nbBlocs===design.length),'vol intact');
      assert.ok(arret!==null&&Math.abs(fin.angle)<0.02&&Math.abs(fin.vx)<0.15&&Math.abs(fin.y-24)<0.15,'arrêt, retour à plat et altitude retrouvée');
      assert.ok(bilan.vitesseInverse>=-0.03,'pas de départ en sens inverse');
      if(nom!=='lateraux'&&scenario==='appui')assert.ok(bilan.effortAppui>0.9&&bilan.angleAppui>fin.angleMax*180/Math.PI-3,'pleine inclinaison et poussée');
      assert.equal(fin.hud.mode,'ON');
     }
     await page.screenshot({path:path.join(out,`${nom}-${recharge}-${sens}-${scenario}.png`)});
    }
   }
  }
  assert.deepEqual(errors,[]);
 }finally{if(browser)await browser.close();server.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
