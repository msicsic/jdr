// Capacités inverses en ON : vrai clavier, vraie physique, profil isolé.
// FER_HTML permet de rejouer le même contrat sur une copie antérieure du jeu.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const http=require('node:http'),{once}=require('node:events');
const root=path.resolve(__dirname,'..'),puppeteer=require(process.env.FER_PUPPETEER_MODULE||'puppeteer-core');
const source=fs.readFileSync(process.env.FER_HTML||path.join(root,'fer-et-flamme.html'),'utf8');
const html=source.replace('</script>',`
window.__ferTest={
 step(s){for(let i=0;i<Math.round(s*60);i++)boucle((dernier+1/60)*1000);},
 vitesse(vy){vehicule.body.setLinvel({x:0,y:vy},true);vehicule.altVerrou=false;},
 rapprocher(){const t=vehicule.body.worldCom();view.x=t.x;view.h=t.y+5;
  view.zoom=70;view.off=view.h*view.zoom;view.horizon=ch/2-5*view.zoom;dessiner();},
 etat(){const v=vehicule;return {...__fer.etat(),av:v.body.angvel(),
  fy:v.thrusters.reduce((s,t)=>s+t.force.y*t.forceN*v.facteur,0),
  fx:v.thrusters.reduce((s,t)=>s+t.force.x*t.forceN*v.facteur,0),
  couple:v.thrusters.reduce((s,t)=>s+(t.rx*t.force.y-t.ry*t.force.x)*t.forceN*v.facteur,0),
  nette:v.pousseeNette,inclinaison:v.thetaUtil,
  moteurs:v.thrusters.map(t=>({force:t.forceN,sens:t.force,max:t.def.thrust,
   inverse:t.def.reverse||0,power:t.def.power})),
  hud:{mode:ui.assist.textContent,vy:ui.vy.textContent,alt:ui.alt.textContent,poussee:ui.poussee.textContent},
  aide:document.getElementById('aide-deplacement').textContent};}
};
</script>`);
const build=nom=>JSON.parse(fs.readFileSync(path.join(__dirname,nom),'utf8'));
const actuel=build('fer-build-joueur-actuel.json'),precedent=build('fer-build-joueur.json');
const plans={actuel,precedent,
 lateralUnique:actuel.filter(b=>!(b.type==='moteur'&&b.rot===3)),
 verticauxRetournes:actuel.map(b=>b.type==='moteur'&&b.rot===0?{...b,rot:2}:b)};
const near=(a,b,t,label)=>assert.ok(Math.abs(a-b)<=t,`${label}: ${a} != ${b}`);
function verifierBornes(e){
 for(const t of e.moteurs)assert.ok(t.force>=-t.max*t.inverse-0.001&&t.force<=t.max+0.001,'plage physique du réacteur');
 const demande=e.moteurs.reduce((s,t)=>s+Math.abs(t.force)*t.power/t.max,0);
 near(e.demandePropulsion,demande,0.1,'consommation de toutes les poussées, inverses comprises');
 assert.equal(e.hud.mode,'ON');assert.ok(!e.hs&&!e.sol,'appareil intact en vol');
}
async function main(){
 const out=path.join(root,'artifacts','fer-inversion-assistee');fs.mkdirSync(out,{recursive:true});
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);});
 server.listen(0,'127.0.0.1');await once(server,'listening');let browser;const resultats=[];
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
  const reset=()=>page.evaluate(()=>__fer.placer(-60,35));
  for(const[nom,design]of Object.entries(plans)){
   if(process.env.FER_CASE&&!process.env.FER_CASE.split(',').includes(nom))continue;
   await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design})),design);
   for(let recharge=0;recharge<2;recharge++){
    await page.reload();await ready();assert.deepEqual(await page.evaluate(()=>__fer.design()),design);
    const bilan=await page.$eval('#bilan',e=>e.textContent);
    await page.evaluate(()=>__fer.lancer());await reset();await step(2);
    const hover=await state();verifierBornes(hover);
    assert.ok(Math.abs(hover.angle)<0.04&&Math.abs(hover.vy)<0.1&&Math.abs(hover.y-35)<0.2,'stationnaire');
    if(nom==='verticauxRetournes'){
     assert.ok(hover.moteurs.filter(t=>Math.abs(t.sens.y)>0.6).every(t=>t.force<0),'sustentation par inversion de moteurs orientés vers le bas');
     assert.ok(hover.nette>hover.masse*9.81&&hover.inclinaison>0,'bilan de portance inclut la poussée inverse');
     near(hover.pousseeVerticale,10200,0.01,'poussée verticale du bilan inclut les inverses');
     assert.ok(bilan.includes('10.2 kN'),'portance inverse visible dans le bilan après recharge');
    }
    await reset();await page.keyboard.down('s');await step(0.15);const descente=await state();await page.keyboard.up('s');
    verifierBornes(descente);assert.ok(descente.fy < -1000&&descente.vy < -1.5,'descente propulsée, au-delà de la chute libre');
    if(nom!=='verticauxRetournes')assert.ok(descente.moteurs.filter(t=>Math.abs(t.sens.y)>0.6).some(t=>t.force < -100),'réacteurs verticaux inversés par S à plat');
    // Freinage d'une montée rapide, sans commande S.
    await reset();await page.evaluate(()=>__ferTest.vitesse(12));await step(0.1);const freinMontee=await state();
    verifierBornes(freinMontee);assert.ok(freinMontee.fy < -1000&&freinMontee.vy<10,'poussée descendante au freinage automatique');
    await step(3);const arretVertical=await state();
    assert.ok(Math.abs(arretVertical.vy)<0.25&&Math.abs(arretVertical.angle)<0.07,'arrêt vertical stable : '+JSON.stringify(arretVertical));
    const lateraux=[];
    for(const touche of ['q','d']){
     await reset();await page.keyboard.down(touche);const trace=[];
     for(let i=0;i<10;i++){await step(0.1);const e=await state();verifierBornes(e);trace.push(e);}
     await page.keyboard.up(touche);const pousse=trace.at(-1),sens=touche==='d'?1:-1;
     assert.ok(sens*pousse.vx>1,'déplacement commandé');
     if(pousse.moteurs.some(t=>Math.abs(t.sens.x)>0.6&&t.sens.x*sens<0)){
      assert.ok(trace.some(e=>e.moteurs.some(t=>Math.abs(t.sens.x)>0.6&&t.sens.x*sens<0&&t.force < -10)),'latéral opposé utilisé en inversion');
     }
     assert.ok(trace.every(e=>Math.abs(e.angle)<=e.inclinaison+0.01&&Math.abs(e.y-35)<1),
      'compensation commune portance/couple : '+JSON.stringify({nom,touche,
       angleMax:Math.max(...trace.map(e=>Math.abs(e.angle))),
       ecartAltitude:Math.max(...trace.map(e=>Math.abs(e.y-35)))}));
     await step(7);const stop=await state();verifierBornes(stop);
     assert.ok(Math.abs(stop.vx)<0.25&&Math.abs(stop.angle)<0.07&&Math.abs(stop.y-35)<1,'arrêt latéral stable');
     near(parseFloat(stop.hud.alt),stop.y,0.1,'altitude visible après recharge');
     lateraux.push({touche,trace,stop});
    }
    // Représentation existante des flammes inverses, en phase de descente.
    await page.waitForFunction('!document.getElementById("chargement")',{timeout:3000,polling:50});
    await reset();await page.keyboard.down('s');await step(0.1);
    await page.evaluate(()=>__ferTest.rapprocher());
    await page.screenshot({path:path.join(out,`${nom}-${recharge}.png`)});await page.keyboard.up('s');
    resultats.push({nom,recharge,bilan,hover,descente,freinMontee,arretVertical,lateraux});
    const fichier=process.env.FER_CASE?`resultats-${process.env.FER_CASE}.json`:'resultats.json';
    fs.writeFileSync(path.join(out,fichier),JSON.stringify(resultats,null,2));
    console.log('OK inversion assistée :',nom,'recharge',recharge,'descente, frein montée, deux sens latéraux, arrêt');
   }
  }
  // Même plage physique sans autorité d'assiette (une seule tuyère verticale).
  const unique=[['poste',2,1,0],['coeur',2,2,0],['moteur',2,0,2]].map(([type,col,row,rot])=>({type,col,row,rot}));
  await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design})),unique);
  await page.reload();await ready();await page.evaluate(()=>__fer.lancer());await reset();
  await page.keyboard.down('z');await step(0.1);const sansAutorite=await state();await page.keyboard.up('z');
  assert.equal(sansAutorite.assistOK,false);near(sansAutorite.moteurs[0].force,-3400,0.01,'inversion sans assiette active');
  assert.deepEqual(errors,[]);console.log('OK inversion sans autorité active : bornes physiques respectées');
 }finally{if(browser)await browser.close();server.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
