const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const http=require('node:http'),{once}=require('node:events');
const root=path.resolve(__dirname,'..'),puppeteer=require(process.env.FER_PUPPETEER_MODULE||'puppeteer-core');
const source=fs.readFileSync(process.env.FER_HTML||path.join(root,'fer-et-flamme.html'),'utf8');
const html=source.replace('MONDE.sol.profil = lisserProfil(MONDE.sol.controle, 2, 9);','MONDE.sol.profil = [[-10000,0],[10000,0]];')
 .replace('monde.step(fileEvenements);','if(window.__ferTest)__ferTest.effort();monde.step(fileEvenements);').replace('</script>',`
window.__ferTest={
 effort(){const v=vehicule,a=v.body.rotation();this.forceX=v.thrusters.reduce((s,t)=>s+(t.force.x*Math.cos(a)-t.force.y*Math.sin(a))*t.forceN*v.facteur,0);},
 isoler(){detruireRival();detruireEnnemis();detruireTirsEnnemis();detruireProjectiles();tourelles=[];MISSION.etat='inactive';
  monde.forEachRigidBody(b=>{const p=b.translation();if(b.isFixed()&&p.y===8&&(p.x===MONDE.bornes.min||p.x===MONDE.bornes.max))b.setTranslation({x:p.x<0?-10000:10000,y:8},true);});},
 step(s){for(let i=0;i<Math.round(s*60);i++)boucle((dernier+1/60)*1000);},
 etat(){const v=vehicule,a=v.body.rotation(),co=Math.cos(a),si=Math.sin(a);
  const fx=v.thrusters.reduce((s,t)=>s+t.force.x*t.forceN*v.facteur,0);
  const fy=v.thrusters.reduce((s,t)=>s+t.force.y*t.forceN*v.facteur,0);
  return {...__fer.etat(),av:v.body.angvel(),fx,fy,wx:this.forceX??(fx*co-fy*si),wy:fx*si+fy*co,
   tau:v.thrusters.reduce((s,t)=>s+(t.rx*t.force.y-t.ry*t.force.x)*t.forceN*v.facteur,0),
   hud:{vx:ui.vx.textContent,alt:ui.alt.textContent,angle:ui.angle.textContent,mode:ui.assist.textContent}};}
};
</script>`);
const colonne=JSON.parse(fs.readFileSync(path.join(__dirname,'fer-build-joueur-colonne.json'),'utf8'));
const plans={colonne,lateraux:JSON.parse(fs.readFileSync(path.join(__dirname,'fer-build-joueur-actuel.json'),'utf8')),
 compact:[['moteur',1,0],['chassis',2,0],['moteur',3,0],['coeur',1,1],['poste',2,1],['coeur',3,1]]
 .map(([type,col,row])=>({type,col,row,rot:0}))};
async function main(){
 const out=path.join(root,'artifacts','fer-transition');fs.mkdirSync(out,{recursive:true});
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
  for(const[nom,design]of Object.entries(plans)){
   if(process.env.FER_CASE&&!process.env.FER_CASE.split(',').includes(nom))continue;
   await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design})),design);
   for(let recharge=0;recharge<(process.env.FER_DIAGNOSTIC?1:2);recharge++){
    await page.reload();await ready();assert.deepEqual(await page.evaluate(()=>__fer.design()),design);
    await page.evaluate(()=>{__fer.lancer();__ferTest.isoler();});
    for(const depart of ['decollage','stationnaire'])for(const touche of ['d','q']){
     if(depart==='decollage'){
      await page.keyboard.press('x');await page.evaluate(()=>__ferTest.isoler());
      const pose=await state();await page.evaluate(y=>__fer.placer(-20,y),pose.y);
      await page.keyboard.down('z');await step(0.35);await page.keyboard.up('z');
     }else{await page.evaluate(()=>__fer.placer(-20,16));await step(2);}
     const debut=await state(),trace=[];await page.keyboard.down(touche);
     for(let i=0;i<120;i++){await step(1/60);trace.push(await state());}
     await page.keyboard.up(touche);await step(8);const fin=await state();const sens=touche==='d'?1:-1;
     const bilan={nom,recharge,depart,touche,minVx:Math.min(...trace.map(e=>sens*e.vx)),
      minFx:Math.min(...trace.map(e=>sens*e.wx)),angleMax:Math.max(...trace.map(e=>Math.abs(e.angle))),
      oscillation:Math.max(...trace.slice(105).map(e=>e.angle))-Math.min(...trace.slice(105).map(e=>e.angle)),
      fin:{angle:fin.angle,av:fin.av,vx:fin.vx,vy:fin.vy}};
     resultats.push({bilan,debut,trace,fin});
     const fichier=process.env.FER_DIAGNOSTIC?'avant.json':process.env.FER_CASE?`resultats-${process.env.FER_CASE}.json`:'resultats.json';
     fs.writeFileSync(path.join(out,fichier),JSON.stringify(resultats,null,2));
     console.log(JSON.stringify(bilan));
     if(!process.env.FER_DIAGNOSTIC){
      assert.ok(bilan.minVx>=-0.03,'aucun départ dans le sens opposé');
      assert.ok(bilan.minFx>=-1,'pas de poussée latérale opposée à la commande');
      assert.ok(bilan.oscillation<0.06,'assiette sans oscillation persistante');
      assert.ok(trace.every(e=>!e.sol&&!e.hs),'vol intact dans la piste de mesure');
      assert.ok(trace.every(e=>e.coque===debut.coque&&e.nbBlocs===design.length),'pas d’impact extérieur dans la mesure');
      assert.equal(fin.coque,debut.coque,'aucun projectile pendant le contrôle d’arrêt');
      assert.ok(Math.abs(fin.vx)<0.25&&Math.abs(fin.angle)<0.07&&Math.abs(fin.av)<0.05,'arrêt stable');
      assert.equal(fin.hud.mode,'ON');assert.ok(Math.abs(parseFloat(fin.hud.alt)-fin.y)<0.1,'altitude affichée');
     }
    }
    await page.screenshot({path:path.join(out,`${nom}-${recharge}.png`)});
   }
  }
  assert.deepEqual(errors,[]);
 }finally{if(browser)await browser.close();server.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
