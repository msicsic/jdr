// Vol manuel dans un navigateur isolé, Rapier réel, appuis clavier réels.
// Configuration identique aux autres tests FER_* ; aucune sauvegarde personnelle.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const http=require('node:http'),{once}=require('node:events');
const root=path.resolve(__dirname,'..');
const puppeteer=require(process.env.FER_PUPPETEER_MODULE||'puppeteer-core');
const html=fs.readFileSync(path.join(root,'fer-et-flamme.html'),'utf8').replace('</script>',`
window.__ferTest={
 step(s){for(let i=0;i<Math.round(s*60);i++)boucle((dernier+1/60)*1000);},
 etat(){const v=vehicule;return {...__fer.etat(),av:v.body.angvel(),
  fx:v.thrusters.reduce((s,t)=>s+t.force.x*t.forceN*v.facteur,0),
  fy:v.thrusters.reduce((s,t)=>s+t.force.y*t.forceN*v.facteur,0),
  tau:v.thrusters.reduce((s,t)=>s+(t.rx*t.force.y-t.ry*t.force.x)*t.forceN*v.facteur,0),
  moteurs:v.thrusters.map(t=>({force:t.forceN,max:t.def.thrust,inverse:t.def.reverse||0,
   direction:t.force,rx:t.rx,ry:t.ry,couple:(t.rx*t.force.y-t.ry*t.force.x)*t.forceN*v.facteur})),
  aide:document.getElementById('aide-deplacement').textContent,
  hud:{mode:ui.assist.textContent,angle:ui.angle.textContent,alt:ui.alt.textContent}};}
};
</script>`);
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'fer-build-joueur.json'),'utf8'));
const actuel=JSON.parse(fs.readFileSync(path.join(__dirname,'fer-build-joueur-actuel.json'),'utf8'));
const near=(a,b,tol,label)=>assert.ok(Math.abs(a-b)<=tol,label+': '+a+' != '+b);
// Oracle direct des extrêmes d'un ensemble de tuyères indépendantes, sans
// utiliser le calcul d'enveloppe ni la répartition du moteur.
function verifierCoupleMaximal(e,sens){
 let disponible=0;
 for(const m of e.moteurs){
  const levier=m.rx*m.direction.y-m.ry*m.direction.x;
  disponible+=Math.max(0,sens*levier*m.max,-sens*levier*m.max*m.inverse);
  if(Math.abs(levier)>1e-6){
   const attendu=sens*levier>0?m.max:-m.max*m.inverse;
   near(m.force,attendu,0.01,'tuyère au maximum utile de sa plage');
  }
 }
 near(e.tau,sens*disponible*e.facteur,0.1,'tout le couple disponible après budget électrique');
 return disponible;
}
async function main(){
 const out=path.join(root,'artifacts','fer-manuel');fs.mkdirSync(out,{recursive:true});
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
  const reset=()=>page.evaluate(()=>__fer.placer(-40,20));
  const action=async(keys,duree=0.2)=>{
   await reset();for(const k of keys)await page.keyboard.down(k);
   await step(duree);const e=await state();for(const k of keys.slice().reverse())await page.keyboard.up(k);
   return e;
  };
  // Le deuxième montage est asymétrique et comporte aussi des tuyères inversées.
  const plans={actuel,joueur:fixture,laterauxHauts:fixture.map(b=>b.type==='moteur'&&(b.rot===1||b.rot===3)
   ? {...b,col:b.rot===1?7:5,row:3}:b),asymetrique:[
   ['moteur',1,0,0],['chassis',2,0,0],['moteur',3,0,0],
   ['coeur',1,1,0],['poste',2,1,0],['coeur',3,1,0],
   ['moteur',1,2,2],['chassis',2,2,0],['moteur',3,2,2],['blindage',0,1,0]
  ].map(([type,col,row,rot])=>({type,col,row,rot}))};
  for(const[nom,design]of Object.entries(plans)){
   await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design,selected:'poste',ghostRot:0})),design);
   for(let recharge=0;recharge<2;recharge++){
    await page.reload();await ready();assert.deepEqual(await page.evaluate(()=>__fer.design()),design);
    await page.evaluate(()=>__fer.lancer());
    await page.keyboard.press('r');await step(0.1);
    const auSol=await state();await page.keyboard.down('z');await step(0.5);
    const decollage=await state();await page.keyboard.up('z');
    assert.ok(decollage.fy>1000&&decollage.y>auSol.y+0.5&&!decollage.sol,'décollage manuel depuis le sol');
    await reset();
    const manuel=await state();assert.equal(manuel.assist,false);assert.equal(manuel.hud.mode,'OFF');
    assert.ok(manuel.aide.includes('Z')&&manuel.aide.includes('Q')&&manuel.aide.includes('rotation'),'aide correspondant au mode');
    const repos=await action([]);assert.ok(repos.moteurs.every(m=>Math.abs(m.force)<1e-6),'aucune poussée automatique');
    assert.ok(repos.vy < -1,'chute sous la gravité sans maintien automatique');
    const haut=await action(['z']);assert.ok(haut.fy>1000&&haut.vy>0,'poussée avant locale');
    near(haut.fx,0,0.1,'pas de translation latérale commandée');near(haut.tau,0,0.1,'poussée sans couple commandé');
    const bas=await action(['s']);assert.ok(bas.fy < -1000&&bas.vy<repos.vy,'poussée arrière locale');
    near(bas.fx,0,0.1,'pas de translation latérale arrière');near(bas.tau,0,0.1,'poussée arrière sans couple');
    const gauche=await action(['q'],0.05);assert.ok(gauche.tau>0&&gauche.av>0.3,'rotation gauche');
    verifierCoupleMaximal(gauche,1);
    const lateraux=gauche.moteurs.filter(m=>Math.abs(m.direction.x)>0.6);
    if(lateraux.length){
      assert.ok(lateraux.some(m=>Math.abs(m.force)>1),'réacteurs latéraux utilisés en rotation');
      assert.ok(lateraux.reduce((s,m)=>s+m.couple,0)>1,'contribution latérale dans le sens de rotation');
      if(lateraux.every(m=>Math.abs(m.ry-lateraux[0].ry)<1e-6)){
        near(lateraux.reduce((s,m)=>s+m.couple,0),-lateraux[0].ry*gauche.fx,0.1,'couple et dérive physiques liés au bras de levier');
      }
    }
    await step(0.3);const inertie=await state();
    assert.ok(Math.abs(inertie.av)<0.001,'rotation freinée automatiquement au relâchement');
    assert.ok(Math.abs(inertie.angle)>0.01,'angle atteint conservé sans remise à plat');
    await page.keyboard.down('d');await step(0.025);const contre=await state();await page.keyboard.up('d');
    assert.ok(contre.av<0&&contre.tau<0,'reprise immédiate de la commande opposée');
    const droite=await action(['d'],0.05);assert.ok(droite.tau<0&&droite.av < -0.3,'rotation droite');
    verifierCoupleMaximal(droite,-1);
    if(lateraux.length)assert.ok(droite.moteurs.filter(m=>Math.abs(m.direction.x)>0.6).reduce((s,m)=>s+m.couple,0)<-1,'latérales utilisées dans les deux sens');
    const combine=await action(['z','q'],0.1);assert.ok(combine.tau>0,'rotation maintenue avec Z');
    verifierCoupleMaximal(combine,1);
    // À couple maximal, la géométrie peut ne laisser aucune poussée axiale.
    // Les moteurs sans bras de levier utilisent alors toute la marge restante.
    const fyMax=combine.moteurs.reduce((s,m)=>{
      const levier=m.rx*m.direction.y-m.ry*m.direction.x;
      const f=Math.abs(levier)>1e-6?(levier>0?m.max:-m.max*m.inverse)
        :(m.direction.y>0?m.max:-m.max*m.inverse);
      return s+m.direction.y*f;
    },0);
    near(combine.fy,fyMax*combine.facteur,0.1,'poussée axiale maximale compatible avec tout le couple');
    if(lateraux.length)assert.ok(combine.moteurs.filter(m=>Math.abs(m.direction.x)>0.6).reduce((s,m)=>s+m.couple,0)>1,'latérales actives avec poussée et rotation combinées');
    assert.ok(combine.demandePropulsion>0&&combine.puissanceUtilisee>0,'forces alimentées par le budget électrique');
    for(const m of combine.moteurs)assert.ok(m.force>=-m.max*m.inverse-1e-4&&m.force<=m.max+1e-4,'bornes réelles de chaque tuyère');
    await page.screenshot({path:path.join(out,`${nom}-${recharge}.png`)});
    const opposees=await action(['z','s','q','d']);
    assert.ok(opposees.moteurs.every(m=>Math.abs(m.force)<1e-6),'flèches opposées annulées');
    const compat=await action(['w','a'],0.1);
    near(compat.fy,combine.fy,0.1,'alias WASD / poussée');near(compat.tau,combine.tau,0.1,'alias WASD / rotation');
    const doubleAlias=await action(['z','w']);near(doubleAlias.fy,haut.fy,0.1,'alias ne double pas la poussée');
    const aliasOpposes=await action(['z','s','q','ArrowRight']);
    assert.ok(aliasOpposes.moteurs.every(m=>Math.abs(m.force)<1e-6),'oppositions entre alias annulées');
    await reset();await page.evaluate(()=>__fer.retourner(Math.PI/2));
    await page.keyboard.down('z');await step(0.2);const incline=await state();await page.keyboard.up('z');
    assert.ok(incline.vx < -0.5,'poussée tourne avec le véhicule');
    near(incline.vy,repos.vy,0.2,'poussée locale à 90 degrés sans composante verticale');
    await reset();await page.evaluate(()=>__fer.retourner(Math.PI));
    await page.keyboard.down('z');await step(0.15);const retourne=await state();await page.keyboard.up('z');
    assert.ok(retourne.vy<repos.vy,'haut pousse vers le sol sur le dos, sans correction monde');
    await page.keyboard.press('x');await step(0.05);const repare=await state();
    assert.ok(!repare.assist&&repare.hud.mode==='OFF'&&repare.aide.includes('Z'),'réparation conserve le mode manuel');
    // Retour en assistance : commandes communes et alias gauche/droite.
    await reset();await page.keyboard.press('r');await step(0.3);const assiste=await state();
    assert.ok(assiste.assist&&assiste.hud.mode==='ON'&&assiste.aide.includes('Z')&&assiste.aide.includes('Q'),'aide assistée restaurée');
    for(const [azerty,fleche] of [['q','ArrowLeft'],['d','ArrowRight']]){
      const a=await action([azerty]),b=await action([fleche]);
      for(const champ of ['fx','fy','tau','vx','vy','angle']) near(a[champ],b[champ],0.1,'commandes ON équivalentes '+azerty+' / '+champ);
    }
    const classique=await action(['z']);assert.ok(classique.vy>0,'poussée Z conservée en assistance');
    resultats.push({nom,recharge,auSol,decollage,repos,haut,bas,gauche,inertie,contre,droite,combine,incline,retourne,repare,assiste});
    fs.writeFileSync(path.join(out,'resultats.json'),JSON.stringify(resultats,null,2));
    console.log('OK manuel :',nom,'recharge',recharge,JSON.stringify({poussee:haut.fy,inverse:bas.fy,couple:combine.tau,rotationLibre:inertie.av}));
   }
  }
  // Des tuyères horizontales décalées peuvent aussi produire un couple pur.
  // Aucun moteur vertical : la flèche haut ne doit pas créer de force fictive.
  const horizontal=[['poste',2,1,0],['coeur',2,2,0],['moteur',1,1,3],['moteur',1,2,1]]
   .map(([type,col,row,rot])=>({type,col,row,rot}));
  await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design})),horizontal);
  await page.reload();await ready();await page.evaluate(()=>{__fer.lancer();__fer.placer(-40,20);});await page.keyboard.press('r');
  const horizontalRotation=await action(['ArrowLeft'],0.05);
  verifierCoupleMaximal(horizontalRotation,1);
  assert.ok(horizontalRotation.tau>0&&horizontalRotation.av>0.3,'couple des tuyères horizontales');
  near(horizontalRotation.fx,0,0.1,'couple horizontal sans translation');near(horizontalRotation.fy,0,0.1,'pas de moteur vertical inventé');
  const sansPoussee=await action(['z']);assert.ok(sansPoussee.moteurs.every(m=>Math.abs(m.force)<1e-6),'axe de propulsion absent respecté');
  resultats.push({nom:'horizontal',horizontalRotation,sansPoussee});
  console.log('OK manuel : rotation par tuyères horizontales, absence de propulsion verticale respectée');
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'resultats.json'),JSON.stringify(resultats,null,2));
 }finally{if(browser)await browser.close();server.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
